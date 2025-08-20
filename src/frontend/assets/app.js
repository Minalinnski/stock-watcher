const API = location.origin.replace(/:\d+$/, ':8888'); // 若前后端同机：后端跑在 8566
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
      <td><b>${item.symbol}</b></td>
      <td>${item.name || ''}</td>
      <td class="price">-</td>
      <td class="chg">-</td>
      <td><canvas class="spark"></canvas></td>
      <td class="ab">加载中…</td>
    `;
    tbody.appendChild(tr);

    // 价格 + 涨跌
    jget(`/api/quote/${item.symbol}`).then(q => {
      tr.querySelector('.price').textContent = q.price ?? '-';
      tr.querySelector('.chg').innerHTML = q.change==null ? '-' : `<span class="${pctClass(q.change)}">${q.change}%</span>`;
    });

    // 迷你曲线
    const canvas = tr.querySelector('.spark');
    const ctx = canvas.getContext('2d');
    jget(`/api/chart/${item.symbol}?period=1d&interval=1m`).then(ch => {
      const labels = ch.points.map(p=>p.t);
      const data = ch.points.map(p=>p.p);
      new Chart(ctx, {
        type:'line',
        data:{ labels, datasets:[{ data, borderWidth:1, pointRadius:0, tension:0.3 }]},
        options:{ responsive:false, plugins:{legend:{display:false}}, scales:{x:{display:false}, y:{display:false}} }
      });
    });

    // AB 信号（含最近两次）
    jget(`/api/ab/${item.symbol}`).then(ab => {
      const two = (ab.last_two_actions||[]).map(x=>`${x.date} ${x.signal}`).join(' / ');
      const sugg = ab.suggestion ? `<span class="badge">${ab.suggestion}</span>` : '';
      tr.querySelector('.ab').innerHTML = `${sugg} ${two || ''}`;
      // 点击整行弹窗
      tr.style.cursor = 'pointer';
      tr.addEventListener('click', () => openModal(item.symbol));
    });
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
