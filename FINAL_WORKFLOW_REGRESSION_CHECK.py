from pathlib import Path
import ast

BASE = Path(__file__).resolve().parent
app = (BASE / 'app.py').read_text(encoding='utf-8')
app_tpl = (BASE / 'templates' / 'app.html').read_text(encoding='utf-8')
ppmp_tpl = (BASE / 'templates' / 'ppmp_home.html').read_text(encoding='utf-8')
review_tpl = (BASE / 'templates' / 'document_review.html').read_text(encoding='utf-8')
preview_js = (BASE / 'static' / 'js' / 'source-preview.js').read_text(encoding='utf-8')
css = (BASE / 'static' / 'css' / 'reference-layout.css').read_text(encoding='utf-8')
schema = (BASE / 'supabase' / 'schema.sql').read_text(encoding='utf-8')

ast.parse(app)
checks = {
    'APP exact-source API canonical route': "@app.route('/api/ppmp/<int:id>/source')" in app,
    'APP exact-source API backward-compatible route': "@app.route('/api/ppmp/<int:id>')" in app,
    'APP template uses exact source endpoint': 'data-source-endpoint="/api/ppmp/{id}/source"' in app_tpl,
    'JS resolves {id} endpoint': "endpoint.includes('{id}')" in preview_js,
    'APP only receives Approved PPMP': "where p.status='Approved' and a.id is null" in app,
    'APP POST validates Approved PPMP': "id=? and status='Approved'" in app,
    'PPMP review route exists': "def ppmp_review(id):" in app,
    'PPMP review completion route exists': "def ppmp_mark_reviewed(id):" in app,
    'PPMP approval route exists': "def ppmp_approve(id):" in app,
    'PPMP review action visible': "url_for('ppmp_review'" in ppmp_tpl,
    'PPMP Reviewed state supported': "status == 'Reviewed'" in review_tpl or "status=='Reviewed'" in review_tpl,
    'PPMP approval metadata schema': all(x in schema for x in ('reviewed_by text','reviewed_at text','approved_by text','approved_at text')),
    'Centered modal CSS': 'transform:translate(-50%,-50%)' in css and 'dialog.ppmp-editor-modal' in css,
    'Login inset green panel': 'margin:20px 0 20px 20px' in css,
    'Login wider/shorter split': '46%' in css and '54%' in css,
}
failed = [name for name, ok in checks.items() if not ok]
for name, ok in checks.items():
    print(('PASS' if ok else 'FAIL') + ': ' + name)
if failed:
    raise SystemExit('Failed checks: ' + ', '.join(failed))
print(f'PASS: {len(checks)} workflow/UI regression checks')
