const API = location.origin; // 前后端一体化，同一端口
const tbody = document.getElementById('tbody');
const modal = document.getElementById('modal');
const closeBtn = document.getElementById('modal-close');
const bigChartCanvas = document.getElementById('big-chart');

let bigChart;

async function jget(path)  { const r = await fetch(`${API}${path}`); return r.json(); }
async function jpost(path, data) {
  const r = await fetch(`${API}${path}`, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  return r.json();
}
async function jdel(path)  { const r = await fetch(`${API}${path}`, {method:'DELETE'}); return r.json(); }

function pctClass(v){ if(v == null) return ''; return v>=0 ? 'up' : 'down'; }

async function loadWatch() {
  const list = await jget('/api/watchlist');
  tbody.innerHTML = '';
  for (const item of list) {
    const tr = document.createElement('tr');
    tr.innerHTML = `
      <td class="symbol-cell">
        <div class="symbol-info">
          <b>${item.symbol}</b>
          <small>${item.name || ''}</small>
        </div>
      </td>
      <td class="price">-</td>
      <td class="chg">-</td>
      <td class="volume">-</td>
      <td><canvas class="spark"></canvas></td>
      <td class="ab">
        <div class="ab-content">
          <span class="suggestion">加载中…</span>
          <div class="signals-history"></div>
        </div>
      </td>
      <td class="actions">
        <button class="btn-remove" onclick="removeStock('${item.symbol}')" title="删除">×</button>
      </td>
    `;
    tbody.appendChild(tr);

    // 价格 + 涨跌 + 成交量
    jget(`/api/quote/${item.symbol}`).then(q => {
      tr.querySelector('.price').textContent = q.price ? `$${q.price}` : '-';
      const changeCell = tr.querySelector('.chg');
      if (q.change !== null) {
        changeCell.innerHTML = `<span class="${pctClass(q.change)}">${q.change > 0 ? '+' : ''}${q.change}%</span>`;
      } else {
        changeCell.textContent = '-';
      }
      tr.querySelector('.volume').textContent = q.volume ? formatVolume(q.volume) : '-';
    }).catch(() => {
      tr.querySelector('.price').textContent = '错误';
    });

    // 迷你曲线
    const canvas = tr.querySelector('.spark');
    const ctx = canvas.getContext('2d');
    jget(`/api/chart/${item.symbol}?period=1d&interval=5m`).then(ch => {
      if (ch.points && ch.points.length > 0) {
        const labels = ch.points.map(p=>p.t);
        const data = ch.points.map(p=>p.p);
        new Chart(ctx, {
          type:'line',
          data:{ labels, datasets:[{ data, borderColor:'#4CAF50', borderWidth:1, pointRadius:0, tension:0.3, fill:false }]},
          options:{ responsive:false, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{display:false}} }
        });
      }
    }).catch(() => {
      // 图表加载失败，显示占位符
      ctx.fillStyle = '#ddd';
      ctx.fillRect(0, 0, canvas.width, canvas.height);
    });

    // AB 信号
    jget(`/api/ab/${item.symbol}`).then(ab => {
      const suggestionSpan = tr.querySelector('.suggestion');
      const historyDiv = tr.querySelector('.signals-history');
      
      // 显示当前建议
      if (ab.suggestion) {
        suggestionSpan.innerHTML = `<span class="badge ${getBadgeClass(ab.suggestion)}">${ab.suggestion}</span>`;
      } else {
        suggestionSpan.textContent = '无信号';
      }
      
      // 显示历史信号
      if (ab.signal_history && ab.signal_history.length > 0) {
        const historyHtml = ab.signal_history.slice(0, 3).map(sig => 
          `<small class="signal-item">${sig.date} ${sig.signal}</small>`
        ).join('');
        historyDiv.innerHTML = historyHtml;
      } else if (ab.last_two_actions && ab.last_two_actions.length > 0) {
        const historyHtml = ab.last_two_actions.map(sig => 
          `<small class="signal-item">${sig.date} ${sig.signal}</small>`
        ).join('');
        historyDiv.innerHTML = historyHtml;
      }
      
      // 点击行打开详情
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', (e) => {
        if (!e.target.classList.contains('btn-remove')) {
          openModal(item.symbol);
        }
      });
    }).catch(() => {
      tr.querySelector('.suggestion').textContent = '加载失败';
    });
  }
}

function formatVolume(volume) {
  if (volume >= 1e9) return (volume / 1e9).toFixed(1) + 'B';
  if (volume >= 1e6) return (volume / 1e6).toFixed(1) + 'M';
  if (volume >= 1e3) return (volume / 1e3).toFixed(1) + 'K';
  return volume.toString();
}

function getBadgeClass(suggestion) {
  switch(suggestion) {
    case 'BUY': return 'badge-buy';
    case 'SELL': return 'badge-sell';
    case 'SHORT': return 'badge-short';
    case 'STAY LONG': return 'badge-long';
    default: return 'badge-neutral';
  }
}

async function removeStock(symbol) {
  if (confirm(`确定要从监控列表中删除 ${symbol} 吗？`)) {
    try {
      await jdel(`/api/watchlist/${symbol}`);
      loadWatch(); // 重新加载列表
    } catch (error) {
      alert('删除失败，请稍后重试');
    }
  }
}

async function openModal(symbol){
  const [q, ab, ch] = await Promise.all([
    jget(`/api/quote/${symbol}`),
    jget(`/api/ab/${symbol}`),
    jget(`/api/chart/${symbol}?period=5d&interval=15m`)
  ]);
  document.getElementById('m-title').textContent = symbol;
  document.getElementById('m-quote').innerHTML = `Price: <b>${q.price ?? '-'}</b> <span class="${pctClass(q.change)}">${q.change ?? '-'}%</span>`;
  document.getElementById('m-sugg').textContent = ab.suggestion || '-';
  const two = (ab.last_two_actions||[]).map(x=>`${x.date} ${x.signal}`).join(' / ');
  document.getElementById('m-two').textContent = two || '-';
  document.getElementById('m-summary').textContent = ab.summary || '';

  const labels = ch.points.map(p=>p.t);
  const data = ch.points.map(p=>p.p);
  if (bigChart) bigChart.destroy();
  bigChart = new Chart(bigChartCanvas.getContext('2d'), {
    type:'line',
    data:{ labels, datasets:[{ data, borderWidth:1, pointRadius:0, tension:0.3 }]},
    options:{ plugins:{legend:{display:false}}, scales:{x:{display:false}} }
  });

  modal.classList.remove('hidden');
}

closeBtn.addEventListener('click', ()=> modal.classList.add('hidden'));
modal.addEventListener('click', (e)=>{ if (e.target === modal) modal.classList.add('hidden'); });

document.getElementById('add-form').addEventListener('submit', async (e)=>{
  e.preventDefault();
  const val = document.getElementById('add-symbol').value.trim();
  if (!val) return;
  await jpost('/api/watchlist', {symbol: val});
  document.getElementById('add-symbol').value = '';
  loadWatch();
});

// 初次 & 轮询（价格/图每 60s 刷新；AB 由后端定时跑）
loadWatch();
setInterval(loadWatch, 60_000);
