let currentTrace = null;
const statusEl = document.getElementById('status');
const resultEl = document.getElementById('result');

function render(data) {
  currentTrace = data.trace_id;
  document.getElementById('vcts').textContent = data.vcts ? data.vcts.score.toFixed(1) : 'N/A';
  document.getElementById('initial').textContent = data.initial_action;
  document.getElementById('final').textContent = data.final_action;
  document.getElementById('opencv').textContent = data.opencv_version + (data.opencv5_compliant ? ' ✓' : ' (dev)');
  const trace = document.getElementById('trace');
  trace.innerHTML = '';
  for (const step of data.trace || []) {
    const li = document.createElement('li');
    li.innerHTML = `<b>${step.stage}</b> — ${step.message}<pre>${JSON.stringify(step.data, null, 2)}</pre>`;
    trace.appendChild(li);
  }
  document.getElementById('raw').textContent = JSON.stringify(data, null, 2);
  document.getElementById('review').classList.toggle('hidden', !data.requires_human_approval || !!data.human_decision);
  resultEl.classList.remove('hidden');
}

document.getElementById('run').addEventListener('click', async () => {
  const input = document.getElementById('video');
  if (!input.files.length) { statusEl.textContent = 'Choose a video first.'; return; }
  const form = new FormData();
  form.append('file', input.files[0]);
  statusEl.textContent = 'Analyzing…';
  resultEl.classList.add('hidden');
  try {
    const r = await fetch('/api/analyze', { method: 'POST', body: form });
    const data = await r.json();
    if (!r.ok) throw new Error(data.detail || 'Analysis failed');
    statusEl.textContent = 'Analysis complete.';
    render(data);
  } catch (e) {
    statusEl.textContent = e.message;
  }
});

for (const button of document.querySelectorAll('#review button')) {
  button.addEventListener('click', async () => {
    if (!currentTrace) return;
    const decision = button.dataset.decision;
    const r = await fetch(`/api/review/${currentTrace}`, {
      method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({decision})
    });
    const data = await r.json();
    if (r.ok) render(data); else statusEl.textContent = data.detail || 'Review failed';
  });
}
