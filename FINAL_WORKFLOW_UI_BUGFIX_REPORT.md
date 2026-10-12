# Final PPMP → APP / Workflow / UI Bug Fix Report

## Fixed issues

### 1. APP “Unable to load the selected PPMP”
Root cause: the APP template/JavaScript treated `/api/ppmp/` as a simple prefix and requested `/api/ppmp/<id>`, while the server route was `/api/ppmp/<id>/source`. The request returned a non-matching response/404, so the preview showed the red error.

Fixes:
- APP now uses `/api/ppmp/{id}/source` explicitly.
- The preview JavaScript supports `{id}` endpoints and a backward-compatible `/api/ppmp/<id>` route is also registered.
- Generate APP stays disabled until the selected Source PPMP loads successfully.
- The server revalidates the selected PPMP by database primary key and Approved status before generation.

### 2. PPMP had no real Review → Reviewed → Approved lifecycle
Root cause: PPMP records were created as Draft and could immediately proceed to APP. The only PPMP action called “Review items” was actually an edit modal, not a document review/approval workflow. Downstream APP/PR code also reused `ppmp.status` for unrelated milestones such as `For APP` and `PR Approved`.

Fixes:
- Added a read-only PPMP Review page.
- Draft PPMP must be explicitly marked Reviewed after checking all stored items.
- Reviewed PPMP can then be explicitly Approved.
- Only Approved PPMP records are available in APP.
- PPMP keeps its own Approved status; APP/PR no longer overwrite the PPMP status.
- Historical PPMP records that already have downstream APP records are normalized to Approved during initialization.
- Added reviewed/approved user/time metadata fields.
- Editing an unconsumed PPMP resets its review/approval status to Draft because the reviewed content changed.
- PPMPs that already have a downstream APP are locked against editing.

### 3. PPMP editor/OCR modal positioning
Fixes:
- Native dialogs are explicitly fixed to the center of the viewport.
- Added system-matching green accent, stronger backdrop, rounded corners, controlled max-height, centered responsive behavior, and scrollable content.

### 4. Login green panel balance
The green panel previously stretched the entire viewport vertically, producing large empty green areas above/below the useful text.

Fixes:
- The green promotional area is now an inset rounded panel with top/bottom breathing room.
- Its width was increased while its visual height was shortened, moving visual weight from excessive top/bottom green into the sides.
- Content is vertically balanced inside the panel.
- The sign-in form remains centered in the white workspace.
- Tablet/mobile behavior remains responsive; the promo panel hides on small screens.

## New PPMP workflow

Draft → Review page → Mark Reviewed → Approve PPMP → available in APP

APP generation no longer accepts Draft or Reviewed-only PPMP records.

## Database upgrade

Migration: `supabase/migrations/202610040004_ppmp_review_approval.sql`

Adds:
- `reviewed_by`
- `reviewed_at`
- `approved_by`
- `approved_at`

The main `supabase/schema.sql` also contains the idempotent `ALTER TABLE ... IF NOT EXISTS` statements, so normal startup applies the upgrade to an existing local Supabase database.

## Validation performed in this build environment

- Python syntax compile: PASS
- JavaScript syntax checks: PASS
- Jinja parse: PASS (27 templates)
- Offline OCR mapper regression tests: PASS
- Final workflow/UI static regression checks: PASS

A live browser/PostgreSQL transaction test must still be performed on the user's Windows Supabase installation because this build environment does not have the user's running local database.
