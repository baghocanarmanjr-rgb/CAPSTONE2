"""Non-destructive regression checks for OCR mapping and downstream PPMP item shape.
Run after dependencies are installed. Database integration is covered by the manual checklist.
"""
import json
from offline_ocr_mapper import map_document, PPMP_FIELDS

sample = {
    'raw_text': '''Project Particulars:\nAcquisition of Network Infrastructure Equipment\nClassification:\nGoods\nRequired Units / Technical Specs:\n4 units Managed Gigabit Switch, 24-port, rack-mountable, VLAN support\nProcurement Method:\nSmall Value Procurement\nFunding Source:\nGeneral Fund\nApproved Budget for the Contract:\nPHP 96,000.00''',
    'tables': [], 'warnings': []
}
result = map_document(sample)
assert result['rows'], 'No OCR row was mapped'
fields = result['rows'][0]['fields']
assert fields[PPMP_FIELDS['description']['label']], 'Description missing'
assert fields[PPMP_FIELDS['quantity_size']['label']], 'Quantity/specification missing'
assert fields[PPMP_FIELDS['budget']['label']], 'Budget missing'
print('PASS: flexible OCR mapping created a reviewable PPMP record')
print(json.dumps(fields, indent=2, ensure_ascii=False))
