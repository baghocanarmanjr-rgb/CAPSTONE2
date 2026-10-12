from offline_ocr_mapper import map_document, PPMP_FIELDS

def test_form():
    doc = {"raw_text": """Project requirement: Procurement of ICT Equipment\nRequired Units: 2 units Laptop Computer, Intel i5, 8GB RAM\nProposed Project Cost: PHP 140,000.00\nProcurement Method: Public Bidding\nFunding Source: General Fund\n""", "tables": [], "warnings": []}
    out = map_document(doc)
    assert out["rows"], out
    row = out["rows"][0]["fields"]
    assert row.get(PPMP_FIELDS["budget"]["label"]), row
    print("PASS: free-form semantic/pattern mapping produced a reviewable PPMP row")

def test_table():
    doc = {"raw_text": "", "tables": [{"rows": [["Item Particulars","Required Units","Financial Requirement"],["Laptop Computer","2 units","PHP 140,000.00"],["Printer","3 units","PHP 45,000.00"]]}], "warnings": []}
    out = map_document(doc)
    assert len(out["rows"]) >= 2, out
    print("PASS: multi-item table produced", len(out["rows"]), "temporary OCR rows")

if __name__ == '__main__':
    test_form(); test_table()

def test_labeled_ppmp_form_complete():
    doc = {"raw_text": """MUNICIPALITY OF ASUNCION
PROJECT PROCUREMENT MANAGEMENT PLAN (PPMP) - TEST DOCUMENT
Category:
NON-DBM
General Description and Objective:
Procurement of ICT Equipment
Type of Project:
Goods
Quantity and Size:
2 units Laptop Computer, Intel i5, at least 8GB RAM, 512GB SSD, 15.6-inch display
Recommended Mode of Procurement:
Public Bidding
Pre-Procurement Conference Applicable:
Yes
Start of Procurement Activity:
March 2026
End of Procurement Activity:
May 2026
Expected Delivery / Implementation Period:
June 2026
Source of Funds:
GF
Estimated Budget Allocation (Php):
140000.00
Attached Supporting Documents:
Technical Specifications; Approved PPMP
Remarks:
Deployment baseline OCR test - NON-DBM laptop procurement
""", "tables": [], "warnings": []}
    out = map_document(doc)
    assert out["rows"], out
    row = out["rows"][0]["fields"]
    expected = {
        PPMP_FIELDS["description"]["label"]: "Procurement of ICT Equipment",
        PPMP_FIELDS["project_type"]["label"]: "Goods",
        PPMP_FIELDS["quantity_size"]["label"]: "2 units Laptop Computer, Intel i5, at least 8GB RAM, 512GB SSD, 15.6-inch display",
        PPMP_FIELDS["procurement_mode"]["label"]: "Public Bidding",
        PPMP_FIELDS["pre_procurement"]["label"]: "Yes",
        PPMP_FIELDS["start_date"]["label"]: "March 2026",
        PPMP_FIELDS["end_date"]["label"]: "May 2026",
        PPMP_FIELDS["delivery_period"]["label"]: "June 2026",
        PPMP_FIELDS["fund_source"]["label"]: "GF",
        PPMP_FIELDS["budget"]["label"]: "140000.00",
        PPMP_FIELDS["supporting_documents"]["label"]: "Technical Specifications; Approved PPMP",
        PPMP_FIELDS["remarks"]["label"]: "Deployment baseline OCR test - NON-DBM laptop procurement",
    }
    for field, value in expected.items():
        assert row.get(field) == value, (field, row.get(field), value)
    print("PASS: complete labeled PPMP form mapped all 12 fields correctly")

if __name__ == '__main__':
    test_labeled_ppmp_form_complete()

def test_key_value_table_and_shared_multi_item_context():
    kv = {
        "raw_text": "",
        "tables": [{"rows": [
            ["Project Particulars", "Acquisition of Network Infrastructure Equipment"],
            ["Classification", "Goods"],
            ["Required Units", "4 units managed switch"],
            ["Procurement Method", "Shopping"],
            ["Funding Source", "GF"],
            ["Project Cost", "80,000"],
            ["Notes", "Network upgrade"],
        ]}],
        "warnings": [],
    }
    out = map_document(kv)
    assert len(out["rows"]) == 1, out
    fields = out["rows"][0]["fields"]
    assert fields[PPMP_FIELDS["description"]["label"]] == "Acquisition of Network Infrastructure Equipment"
    assert fields[PPMP_FIELDS["budget"]["label"]] == "80,000"

    multi = {
        "raw_text": "Funding: GF\nProcurement Method: Shopping",
        "tables": [{"rows": [
            ["Item Particulars", "Qty", "Technical Requirement", "Budget Ceiling", "Need By"],
            ["Desktop Computer", "3 units", "Intel i5, 16GB RAM", "135,000", "Jun 2026"],
            ["UPS", "5 units", "1000VA", "27,500", "Jun 2026"],
        ]}],
        "warnings": [],
    }
    out = map_document(multi)
    assert len(out["rows"]) == 2, out
    first = out["rows"][0]["fields"]
    assert "3 units" in first[PPMP_FIELDS["quantity_size"]["label"]]
    assert "Intel i5" in first[PPMP_FIELDS["quantity_size"]["label"]]
    assert first[PPMP_FIELDS["fund_source"]["label"]] == "GF"
    assert first[PPMP_FIELDS["procurement_mode"]["label"]] == "Shopping"
    print("PASS: key/value forms and multi-item tables with shared metadata mapped correctly")

if __name__ == '__main__':
    test_key_value_table_and_shared_multi_item_context()
