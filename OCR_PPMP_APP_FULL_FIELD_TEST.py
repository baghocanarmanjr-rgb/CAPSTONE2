"""Regression checks for the reviewed OCR -> PPMP -> APP source payload contract.
Run from the capstone folder after normal dependencies are installed:
    python OCR_PPMP_APP_FULL_FIELD_TEST.py
This test does not write to PostgreSQL; the manual checklist covers the live DB flow.
"""
import json
import app

EXPECTED = {
    'General Description and Objective of the Project to be Procured': 'Acquisition of Network Infrastructure Equipment',
    'Type of the Project to be Procured': 'Goods',
    'Quantity and Size of the Project to be Procured': '4 units Managed Gigabit Switch, 24-port, rack-mountable, VLAN support',
    'Recommended Mode of Procurement': 'Small Value Procurement',
    'Pre-Procurement Conference Applicable (Yes/No)': 'Not Applicable',
    'Start of Procurement Activity': 'April 2026',
    'End of Procurement Activity': 'May 2026',
    'Expected Delivery/Implementation Period': 'Within 30 calendar days after notice to proceed',
    'Source of Funds': 'General Fund',
    'Estimated Budget Allocation (Php)': 'PHP 80,000.00',
    'Attached Supporting Documents': 'Technical Specifications; Market Survey',
    'Remarks': 'For municipal network upgrade and redundancy',
}


def test_currency():
    for raw in ['80,000', '80,000.00', '₱80,000', '₱80,000.00', 'PHP 80,000', 'PHP80,000', 'Php 80,000.00', '80000', '80000.00']:
        parsed = app.parse_currency_decimal(raw)
        assert parsed is not None and float(parsed) == 80000.0, (raw, parsed)
    assert app.parse_currency_decimal('not an amount') is None
    print('PASS: currency parser preserves valid values and rejects invalid text')


def test_all_fields():
    official_item = app.validated_ppmp_item_from_review(EXPECTED, 'DBM')
    canonical = app.canonical_ppmp_fields(official_item)
    for field, expected in EXPECTED.items():
        actual = canonical[field]
        if field == 'Estimated Budget Allocation (Php)':
            assert actual == 80000.0, (field, actual)
        else:
            assert actual == expected, (field, actual, expected)

    ppmp_row = {
        'id': 3,
        'no': 'PPMP-DBM-2026-0003',
        'type': 'DBM',
        'office': 'General Services Office',
        'year': 2026,
        'status': 'Draft',
        'source_type': 'OCR',
        'items': json.dumps([official_item], ensure_ascii=False),
        # Simulates a record made by the older bugged build.
        'total': 0,
    }
    payload = app.ppmp_source_payload(ppmp_row)
    assert payload['id'] == 3
    assert payload['total'] == 80000.0, payload
    assert len(payload['items']) == 1
    source_fields = payload['items'][0]['fields']
    for field, actual in canonical.items():
        assert source_fields[field] == actual, (field, source_fields[field], actual)
    print('PASS: all 12 reviewed fields survive official PPMP normalization and APP source serialization')


if __name__ == '__main__':
    test_currency()
    test_all_fields()
    print('PASS: OCR -> PPMP -> APP full-field regression complete')
