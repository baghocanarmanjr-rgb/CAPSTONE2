# OCR Mapping Bug Fix

## Problem fixed
The OCR engine itself extracted the supplied PPMP test image correctly. The error was in the structured PPMP mapper: it removed trailing `:` markers too early and then treated almost every OCR line as a potential label for the following line. As a result, values such as `Procurement of ICT Equipment` could be mistaken for labels and overwrite correctly mapped fields. This also caused legitimate fields such as `Yes`, `May 2026`, `GF`, supporting documents, and remarks to disappear.

## Fix
- Preserve label punctuation during structural parsing.
- Prefer explicit `Label:` / `Label = value` structures.
- Separate label recognition from value classification.
- Do not pair every line with the next line.
- Give explicit labels higher source priority than heuristic/free-text guesses.
- Prevent lower-priority pattern inference from overwriting explicit mapped fields.
- Keep semantic, fuzzy, pattern, and context mapping for less structured documents.
- Added regression coverage for all 12 PPMP fields from the deployment test document.

## Verified expected mapping
The supplied PPMP test content now maps all 12 fields correctly, including:
- General Description: Procurement of ICT Equipment
- Type: Goods
- Quantity/Size: 2 units Laptop Computer, Intel i5, at least 8GB RAM, 512GB SSD, 15.6-inch display
- Mode: Public Bidding
- Pre-Procurement: Yes
- Start: March 2026
- End: May 2026
- Delivery: June 2026
- Source of Funds: GF
- Budget: 140000.00
- Supporting Documents: Technical Specifications; Approved PPMP
- Remarks: Deployment baseline OCR test - NON-DBM laptop procurement
