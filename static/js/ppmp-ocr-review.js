(() => {
  'use strict';
  const dataNode = document.getElementById('ocrRowsData');
  const dialog = document.getElementById('ocrReviewDialog');
  if (!dataNode || !dialog) return;
  let rows = [];
  try { rows = JSON.parse(dataNode.textContent || '[]'); } catch (_) { return; }
  const fields = Array.from(dialog.querySelectorAll('[id^="ocrField"]'));
  const confidences = Array.from(dialog.querySelectorAll('[id^="ocrConfidence"]'));
  const labels = fields.map(f => f.closest('label')?.querySelector('span')?.textContent?.trim() || '');
  const statusBox = document.getElementById('ocrReviewStatus');
  const mappingInfo = document.getElementById('ocrMappingInfo');
  function levelClass(level) { return String(level || '').toLowerCase().replace(/\s+/g,'-'); }
  function openRow(id) {
    const row = rows.find(r => String(r.temp_id) === String(id));
    if (!row) return;
    document.getElementById('ocrTempId').value = row.temp_id;
    fields.forEach((field, i) => {
      const label = labels[i];
      field.value = row.fields?.[label] || '';
      const info = row.field_confidence?.[label] || {};
      const level = info.level || 'Unmapped';
      confidences[i].textContent = level + (typeof info.score === 'number' ? ` · ${Math.round(info.score*100)}%` : '');
      confidences[i].className = 'field-confidence ' + levelClass(level);
      field.closest('label')?.classList.toggle('needs-attention', ['Medium','Low','Unmapped'].includes(level));
    });
    statusBox.innerHTML = `<strong>${row.temp_id}</strong><span class="badge ${row.status === 'High Confidence' || row.status === 'Reviewed' ? 'ok' : 'warn'}">${row.status || 'Needs Review'}</span>`;
    mappingInfo.innerHTML = labels.map(label => {
      const info = row.field_confidence?.[label] || {};
      const src = info.source_label || 'No reliable source label detected';
      return `<div><b>${escapeHtml(label)}</b><span>${escapeHtml(src)}</span></div>`;
    }).join('');
    dialog.showModal();
    window.resizeEditorFields?.(dialog);
  }
  function escapeHtml(s) { const el=document.createElement('span'); el.textContent=String(s||''); return el.innerHTML; }
  document.addEventListener('click', e => {
    const btn = e.target.closest('[data-ocr-review]');
    if (btn) openRow(btn.dataset.ocrReview);
    if (e.target.closest('[data-ocr-close]')) dialog.close();
  });
  dialog.addEventListener('click', e => {
    if (e.target !== dialog) return;
    const r=dialog.getBoundingClientRect();
    if (e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom) dialog.close();
  });
})();
