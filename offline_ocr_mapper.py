"""Offline, schema-driven PPMP OCR/document mapper.

The mapper never calls a cloud API.  It combines a local sentence-transformer
(when installed), fuzzy similarity, value-shape validation and source context.
The destination PPMP schema is fixed; source wording/layout is not.
"""
from __future__ import annotations

import math
import os
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from rapidfuzz.fuzz import ratio as fuzzy_ratio
except Exception:  # optional until setup is completed
    fuzzy_ratio = None

BASE_DIR = Path(__file__).resolve().parent
DEFAULT_MODEL_DIR = BASE_DIR / "models" / "ocr_mapper" / "all-MiniLM-L6-v2"
MODEL_DIR = Path(os.environ.get("OCR_SEMANTIC_MODEL_PATH", str(DEFAULT_MODEL_DIR)))

PPMP_FIELDS: Dict[str, Dict[str, Any]] = {
    "description": {
        "label": "General Description and Objective of the Project to be Procured",
        "meaning": "general description, objective, particulars or requirement of the procurement project, goods, works or services",
        "type": "text",
        "aliases": ["description", "project description", "procurement description", "particulars", "project particulars", "requirement", "project requirement", "item description", "objective"],
    },
    "project_type": {
        "label": "Type of the Project to be Procured",
        "meaning": "classification, category or type of the procurement project, goods, services, infrastructure or equipment",
        "type": "category",
        "aliases": ["project type", "type of project", "classification", "category", "procurement type", "project classification"],
    },
    "quantity_size": {
        "label": "Quantity and Size of the Project to be Procured",
        "meaning": "quantity, number of units, size, dimensions, technical specifications or item specification",
        "type": "quantity_spec",
        "aliases": ["quantity", "qty", "units", "required units", "units needed", "size", "specification", "specifications", "technical specification", "technical specs", "technical requirement"],
    },
    "procurement_mode": {
        "label": "Recommended Mode of Procurement",
        "meaning": "method or mode used to procure goods equipment works or services including bidding shopping or negotiated procurement",
        "type": "procurement_mode",
        "aliases": ["mode of procurement", "procurement method", "method of procurement", "bidding method", "procurement mode", "planned acquisition", "acquisition method"],
    },
    "pre_procurement": {
        "label": "Pre-Procurement Conference Applicable (Yes/No)",
        "meaning": "whether a pre procurement, pre-bid or procurement conference is applicable or required",
        "type": "boolean",
        "aliases": ["pre procurement conference", "pre-bid conference", "prebid conference", "conference applicable", "pre-bid requirement", "pre bid requirement", "conference", "pre procurement requirement"],
    },
    "start_date": {
        "label": "Start of Procurement Activity",
        "meaning": "date or period when procurement activity begins or starts",
        "type": "date",
        "aliases": ["start date", "procurement start", "date started", "start of procurement", "target start", "planned start"],
    },
    "end_date": {
        "label": "End of Procurement Activity",
        "meaning": "date or period when procurement activity ends, closes or is completed",
        "type": "date",
        "aliases": ["end date", "procurement end", "completion date", "end of procurement", "completion target", "target finish", "planned completion"],
    },
    "delivery_period": {
        "label": "Expected Delivery/Implementation Period",
        "meaning": "expected delivery schedule, implementation period, delivery date or implementation schedule",
        "type": "date_or_period",
        "aliases": ["expected delivery", "delivery period", "implementation period", "delivery schedule", "expected implementation", "implementation", "need by"],
    },
    "fund_source": {
        "label": "Source of Funds",
        "meaning": "source, account or origin of funding or budget for the procurement",
        "type": "fund_source",
        "aliases": ["source of funds", "fund source", "funding source", "budget source", "fund", "funding"],
    },
    "budget": {
        "label": "Estimated Budget Allocation (Php)",
        "meaning": "estimated or approved monetary budget, allocation, project cost, total cost or approved budget for procurement",
        "type": "currency",
        "aliases": ["budget", "estimated budget", "approved budget", "approved budget for the contract", "abc", "allocation", "total allocation", "project cost", "cost estimate", "budget ceiling", "financial requirement", "total cost", "amount"],
    },
    "supporting_documents": {
        "label": "Attached Supporting Documents",
        "meaning": "supporting documents, attachments, requirements or documentary evidence for procurement",
        "type": "text",
        "aliases": ["supporting documents", "supporting files", "attachments", "attached documents", "requirements", "documents attached"],
    },
    "remarks": {
        "label": "Remarks",
        "meaning": "additional comments, notes, remarks or other information about the procurement item",
        "type": "text",
        "aliases": ["remarks", "notes", "additional notes", "comments", "additional information"],
    },
}

LABEL_TO_KEY = {v["label"]: k for k, v in PPMP_FIELDS.items()}
KEY_TO_LABEL = {k: v["label"] for k, v in PPMP_FIELDS.items()}

_MODEL = None
_MODEL_ERROR = None
_SCHEMA_EMBEDDINGS = None


def _clean(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\u00a0", " ")).strip(" \t\r\n:|-;")


def _norm(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", " ", _clean(value).lower()).strip()


def _cosine(a, b) -> float:
    try:
        import numpy as np
        a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
        den = float(np.linalg.norm(a) * np.linalg.norm(b))
        return float(np.dot(a, b) / den) if den else 0.0
    except Exception:
        return 0.0


def load_local_model():
    """Load only from disk. Never triggers a runtime network download."""
    global _MODEL, _MODEL_ERROR, _SCHEMA_EMBEDDINGS
    if _MODEL is not None:
        return _MODEL
    if not MODEL_DIR.exists():
        _MODEL_ERROR = f"Local OCR semantic model not found at {MODEL_DIR}"
        return None
    try:
        from sentence_transformers import SentenceTransformer
        try:
            model = SentenceTransformer(str(MODEL_DIR), local_files_only=True)
        except TypeError:  # older compatible versions
            os.environ.setdefault("HF_HUB_OFFLINE", "1")
            model = SentenceTransformer(str(MODEL_DIR))
        _MODEL = model
        meanings = [PPMP_FIELDS[k]["meaning"] for k in PPMP_FIELDS]
        _SCHEMA_EMBEDDINGS = model.encode(meanings, normalize_embeddings=True)
        _MODEL_ERROR = None
        return model
    except Exception as exc:
        _MODEL_ERROR = str(exc)
        return None


def model_status() -> Dict[str, Any]:
    model = load_local_model()
    return {
        "active": bool(model),
        "path": str(MODEL_DIR),
        "message": "Local semantic mapper active." if model else (_MODEL_ERROR or "Local semantic mapper unavailable."),
        "rapidfuzz": bool(fuzzy_ratio),
    }


def _semantic_scores(label: str) -> Dict[str, float]:
    model = load_local_model()
    if not model or _SCHEMA_EMBEDDINGS is None or not _clean(label):
        return {k: 0.0 for k in PPMP_FIELDS}
    vec = model.encode([_clean(label)], normalize_embeddings=True)[0]
    return {k: max(0.0, min(1.0, _cosine(vec, emb))) for k, emb in zip(PPMP_FIELDS.keys(), _SCHEMA_EMBEDDINGS)}


def _fuzzy_score(label: str, key: str) -> float:
    if not fuzzy_ratio or not _clean(label):
        return 0.0
    choices = [PPMP_FIELDS[key]["label"], PPMP_FIELDS[key]["meaning"], *PPMP_FIELDS[key]["aliases"]]
    return max(fuzzy_ratio(_norm(label), _norm(c)) / 100.0 for c in choices if _norm(c))


MONTHS = r"jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|sep(?:tember)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?"
DATE_RE = re.compile(rf"\b(?:{MONTHS})\s+\d{{1,2}}(?:,\s*\d{{4}})?\b|\b(?:{MONTHS})\s+\d{{4}}\b|\b\d{{1,4}}[-/]\d{{1,2}}[-/]\d{{1,4}}\b", re.I)
CURRENCY_RE = re.compile(r"(?:₱|PHP|Php|php|P\s*)?\s*\d{1,3}(?:,\d{3})+(?:\.\d{1,2})?|(?:₱|PHP|Php|php)\s*\d+(?:\.\d{1,2})?", re.I)
QTY_RE = re.compile(r"\b\d+(?:\.\d+)?\s*(?:unit|units|pc|pcs|piece|pieces|box|boxes|bottle|bottles|roll|rolls|lot|lots|set|sets|ream|reams|pack|packs)\b", re.I)


def _value_type_score(value: str, key: str) -> float:
    v = _clean(value)
    if not v:
        return 0.0
    typ = PPMP_FIELDS[key]["type"]
    low = v.lower()
    if typ == "currency":
        if CURRENCY_RE.search(v): return 1.0
        if re.fullmatch(r"\d+(?:[,.]\d+)*", v): return 0.70
        return 0.05
    if typ == "quantity_spec":
        if QTY_RE.search(v): return 1.0
        if re.search(r"\b\d+(?:\.\d+)?\b", v) and len(v) > 4: return 0.65
        return 0.25 if len(v) > 10 else 0.05
    if typ in ("date", "date_or_period"):
        if DATE_RE.search(v): return 1.0
        if re.search(r"\b\d+\s*(?:day|days|week|weeks|month|months)\b", low): return 0.85
        return 0.05
    if typ == "boolean":
        return 1.0 if low in {"yes", "no", "applicable", "not applicable", "n/a", "na"} else 0.1
    if typ == "procurement_mode":
        terms = ["bidding", "shopping", "procurement", "negotiated", "contracting", "quotation", "small value"]
        return 0.95 if any(t in low for t in terms) else 0.15
    if typ == "fund_source":
        terms = ["fund", "gf", "sef", "trust", "general fund", "special education"]
        return 0.9 if any(t in low for t in terms) else 0.2
    if typ == "category":
        terms = ["goods", "service", "services", "equipment", "works", "infrastructure", "consulting"]
        return 0.9 if any(t in low for t in terms) else 0.35
    return 0.65 if len(v) >= 2 else 0.1


def _context_score(label: str, value: str, key: str, neighbors: str = "") -> float:
    text = _norm(" ".join([label, value, neighbors]))
    if not text:
        return 0.0
    # This is intentionally generic: compare words from the schema meaning rather than file-specific phrases.
    schema_words = {w for w in _norm(PPMP_FIELDS[key]["meaning"]).split() if len(w) > 3}
    words = set(text.split())
    overlap = len(schema_words & words) / max(1, min(6, len(schema_words)))
    return min(1.0, overlap * 1.8)


def classify_field(label: str, value: str, neighbors: str = "") -> Tuple[str, float, Dict[str, float]]:
    semantic = _semantic_scores(label or neighbors)
    best_key, best_score, best_parts = "", -1.0, {}
    for key in PPMP_FIELDS:
        sem = semantic.get(key, 0.0)
        fuzzy = _fuzzy_score(label or neighbors, key)
        vtype = _value_type_score(value, key)
        context = _context_score(label, value, key, neighbors)
        # When the semantic model is missing, redistribute semantic weight to the other local signals.
        if load_local_model():
            score = sem * 0.45 + vtype * 0.25 + context * 0.20 + fuzzy * 0.10
        else:
            score = vtype * 0.40 + context * 0.30 + fuzzy * 0.30
        if score > best_score:
            best_key, best_score = key, score
            best_parts = {"semantic": sem, "value_type": vtype, "context": context, "fuzzy": fuzzy}
    return best_key, max(0.0, min(1.0, best_score)), best_parts


def confidence_label(score: float) -> str:
    if score >= 0.85: return "High"
    if score >= 0.65: return "Medium"
    if score >= 0.45: return "Low"
    return "Unmapped"


def _split_lines(text: str) -> List[str]:
    """Return readable OCR lines while preserving label punctuation such as ':'."""
    out = []
    for raw in str(text or "").replace("\r", "\n").split("\n"):
        line = re.sub(r"\s+", " ", raw.replace("\u00a0", " ")).strip()
        if line:
            out.append(line)
    return out


def _label_text(value: str) -> str:
    return re.sub(r"\s*[:=\-]+\s*$", "", str(value or "")).strip()


def _lexical_label_score(label: str, key: str) -> float:
    """Schema-driven lexical similarity for a potential source label.

    This does not depend on a particular uploaded document.  It compares the
    candidate against the destination label, semantic description and aliases.
    """
    src = _norm(_label_text(label))
    if not src:
        return 0.0
    field = PPMP_FIELDS[key]
    candidates = [field["label"], field["meaning"], *field.get("aliases", [])]
    best = 0.0
    src_tokens = set(src.split())
    for cand in candidates:
        cn = _norm(cand)
        if not cn:
            continue
        if src == cn:
            return 1.0
        # Exact phrase containment is strong, but require a meaningful phrase.
        if len(cn) >= 5 and (cn in src or src in cn):
            best = max(best, 0.93 if len(cn.split()) >= 2 else 0.82)
        ct = set(cn.split())
        overlap = len(src_tokens & ct) / max(1, min(len(src_tokens), len(ct)))
        best = max(best, min(0.90, overlap * 0.90))
    if fuzzy_ratio:
        best = max(best, _fuzzy_score(src, key))
    return max(0.0, min(1.0, best))


def _best_label_key(label: str) -> Tuple[str, float, Dict[str, float]]:
    """Classify a *label*, not a label/value pair.

    Separating label recognition from value recognition prevents values such as
    'Procurement of ICT Equipment' from being mistaken for the next field name.
    """
    semantic = _semantic_scores(_label_text(label))
    best_key, best_score, best_parts = "", 0.0, {}
    for key in PPMP_FIELDS:
        lexical = _lexical_label_score(label, key)
        sem = semantic.get(key, 0.0)
        if load_local_model():
            score = lexical * 0.65 + sem * 0.35
        else:
            score = lexical
        if score > best_score:
            best_key, best_score = key, score
            best_parts = {"label_lexical": lexical, "label_semantic": sem}
    return best_key, max(0.0, min(1.0, best_score)), best_parts


def _looks_like_value(line: str) -> bool:
    clean = _clean(line)
    low = clean.lower()
    if not clean:
        return False
    if CURRENCY_RE.fullmatch(clean) or QTY_RE.search(clean) or DATE_RE.fullmatch(clean):
        return True
    if low in {"yes", "no", "applicable", "not applicable", "n/a", "na", "gf", "sef"}:
        return True
    # Long descriptive/specification text is much more likely a value than a label.
    if len(clean) > 100:
        return True
    return False


def _label_value_candidates(lines: List[str]) -> List[Tuple[str, str, str, str, float]]:
    """Extract conservative label/value pairs from OCR text.

    Returns (label, value, neighbors, key, label_confidence).  Explicit colon/
    equals labels are strongly preferred.  Crucially, we do NOT pair every line
    with the next line; that behavior caused values to be misread as labels.
    """
    out: List[Tuple[str, str, str, str, float]] = []
    consumed_value_indexes = set()

    for i, original in enumerate(lines):
        if i in consumed_value_indexes:
            continue
        line = original.strip()
        neighbors = " ".join(lines[max(0, i-1):min(len(lines), i+3)])

        # 1) Strongest form: explicit 'Label: value' / 'Label = value'.
        m = re.match(r"^(.{2,140}?)[\s]*[:=][\s]*(.*)$", line)
        if m:
            label = _label_text(m.group(1))
            inline_value = _clean(m.group(2))
            key, lscore, _ = _best_label_key(label)
            if key and lscore >= 0.42:
                value = inline_value
                if not value:
                    # Find the next non-label line as the value.
                    for j in range(i + 1, min(len(lines), i + 4)):
                        nxt = lines[j].strip()
                        if not nxt:
                            continue
                        nkey, nscore, _ = _best_label_key(_label_text(nxt))
                        is_explicit_next_label = bool(re.match(r"^.{2,140}?\s*[:=]\s*.*$", nxt)) and nscore >= 0.50
                        if is_explicit_next_label:
                            break
                        value = _clean(nxt)
                        consumed_value_indexes.add(j)
                        break
                if value:
                    out.append((label, value, neighbors, key, lscore))
            continue

        # 2) Label on its own line without punctuation. Be conservative.
        if _looks_like_value(line):
            continue
        key, lscore, _ = _best_label_key(line)
        if not key or lscore < 0.68:
            continue
        for j in range(i + 1, min(len(lines), i + 3)):
            nxt = lines[j].strip()
            if not nxt:
                continue
            nkey, nscore, _ = _best_label_key(_label_text(nxt))
            if nscore >= 0.72 and not _looks_like_value(nxt):
                break
            out.append((_label_text(line), _clean(nxt), neighbors, key, lscore))
            consumed_value_indexes.add(j)
            break
    return out

def _empty_record(temp_id: str) -> Dict[str, Any]:
    return {
        "temp_id": temp_id,
        "fields": {v["label"]: "" for v in PPMP_FIELDS.values()},
        "field_confidence": {v["label"]: {"score": 0.0, "level": "Unmapped", "source_label": ""} for v in PPMP_FIELDS.values()},
        "average_confidence": 0.0,
        "status": "Needs Review",
    }


def _finalize(record: Dict[str, Any]) -> Dict[str, Any]:
    scores = [x["score"] for label, x in record["field_confidence"].items() if record["fields"].get(label)]
    avg = sum(scores) / len(scores) if scores else 0.0
    record["average_confidence"] = round(avg, 4)
    populated = sum(1 for x in record["fields"].values() if _clean(x))
    lows = any(x["level"] in {"Low", "Unmapped"} for label, x in record["field_confidence"].items() if record["fields"].get(label))
    record["status"] = "High Confidence" if avg >= 0.85 and populated >= 4 and not lows else "Needs Review"
    return record


def _apply_candidate(
    record: Dict[str, Any],
    label: str,
    value: str,
    neighbors: str = "",
    *,
    forced_key: Optional[str] = None,
    source_priority: int = 1,
    label_score: Optional[float] = None,
) -> None:
    """Apply a candidate without allowing weak heuristics to overwrite explicit fields."""
    if not _clean(value):
        return

    if forced_key:
        key = forced_key
        lexical = _lexical_label_score(label, key) if label_score is None else label_score
        sem = _semantic_scores(label).get(key, 0.0) if _clean(label) else 0.0
        vtype = _value_type_score(value, key)
        context = _context_score(label, value, key, neighbors)
        # Explicit labels should be trusted primarily for *mapping* while the
        # value-shape/context signals still influence confidence.
        score = lexical * 0.60 + vtype * 0.25 + max(context, sem) * 0.15
        parts = {"label": lexical, "semantic": sem, "value_type": vtype, "context": context}
    else:
        key, score, parts = classify_field(label, value, neighbors)

    if not key or score < 0.45:
        return
    target = KEY_TO_LABEL[key]
    current_meta = record["field_confidence"].get(target, {})
    existing = float(current_meta.get("score", 0.0) or 0.0)
    existing_priority = int(current_meta.get("source_priority", 0) or 0)

    # Explicit schema labels outrank contextual/free-text guesses, even if a
    # heuristic gets a slightly higher numerical score.
    should_replace = (
        not record["fields"].get(target)
        or source_priority > existing_priority
        or (source_priority == existing_priority and score > existing + 0.015)
    )
    if should_replace:
        record["fields"][target] = _clean(value)
        record["field_confidence"][target] = {
            "score": round(score, 4),
            "level": confidence_label(score),
            "source_label": _clean(label),
            "source_priority": source_priority,
            "signals": parts,
        }

def _key_value_table_rows(table: Dict[str, Any], start_index: int) -> List[Dict[str, Any]]:
    """Recognize two/few-column form tables where each row is Label -> Value.

    DOCX/XLSX/PDF procurement forms are often represented as a vertical table rather
    than paragraphs. Treating each table row as a separate procurement item loses the
    document structure, so detect several distinct PPMP labels before accepting this
    interpretation.
    """
    raw_rows = table.get("rows") or []
    rows = [[_clean(c) for c in row] for row in raw_rows if isinstance(row, (list, tuple)) and any(_clean(c) for c in row)]
    if len(rows) < 3:
        return []
    pairs = []
    keys_seen = set()
    for row in rows:
        nonempty = [(i, cell) for i, cell in enumerate(row) if _clean(cell)]
        if len(nonempty) < 2:
            continue
        label = nonempty[0][1]
        value = " | ".join(cell for _, cell in nonempty[1:] if _clean(cell))
        key, score, _ = _best_label_key(label)
        lexical = _lexical_label_score(label, key) if key else 0.0
        if key and lexical >= 0.65 and value:
            pairs.append((label, value, key, max(score, lexical), " | ".join(row)))
            keys_seen.add(key)
    # A vertical form should expose several *different* schema labels down its
    # first populated column. Ordinary item tables normally have only one header
    # label followed by item names, so they fail this test.
    if len(pairs) < 3 or len(keys_seen) < 3 or (len(pairs) / max(1, len(rows))) < 0.45:
        return []
    rec = _empty_record(f"OCR-TEMP-{start_index:03d}")
    for label, value, key, score, neighbors in pairs:
        _apply_candidate(rec, label, value, neighbors, forced_key=key, source_priority=4, label_score=score)
    return [_finalize(rec)]


def _detect_table_header(rows: List[List[str]]) -> Tuple[int, List[str], Dict[int, Tuple[str, float]]]:
    """Find the row that most plausibly contains PPMP-related column headings."""
    best_index = -1
    best_headers: List[str] = []
    best_map: Dict[int, Tuple[str, float]] = {}
    best_score = -1.0
    for idx, row in enumerate(rows[:15]):
        mapped: Dict[int, Tuple[str, float]] = {}
        distinct = set()
        strength = 0.0
        for col, cell in enumerate(row):
            key, score, _ = _best_label_key(cell)
            if key and score >= 0.40:
                mapped[col] = (key, score)
                distinct.add(key)
                strength += score
        # Require multiple semantic columns for a real item table. This avoids
        # treating title lines and ordinary data rows as headers.
        score_total = len(distinct) * 10.0 + strength
        if len(distinct) >= 2 and score_total > best_score:
            best_index, best_headers, best_map, best_score = idx, row, mapped, score_total
    return best_index, best_headers, best_map


def _rows_from_table(table: Dict[str, Any], start_index: int) -> List[Dict[str, Any]]:
    rows = table.get("rows") or []
    rows = [[_clean(c) for c in row] for row in rows if isinstance(row, (list, tuple)) and any(_clean(c) for c in row)]
    if len(rows) < 2:
        return []

    # First handle a form represented as a vertical key/value table.
    kv = _key_value_table_rows({"rows": rows}, start_index)
    if kv:
        return kv

    header_index, headers, header_map = _detect_table_header(rows)
    if header_index < 0:
        # Conservative fallback: only use the first row as a header when it is
        # mostly textual. Otherwise leave the data for the free-text reviewer.
        header = rows[0]
        textual = sum(1 for c in header if c and not CURRENCY_RE.search(c) and not re.fullmatch(r"[\d,.]+", c))
        if textual < max(1, len(header) // 2):
            return []
        header_index, headers = 0, header
        header_map = {}
        for col, label in enumerate(headers):
            key, score, _ = _best_label_key(label)
            if key and score >= 0.40:
                header_map[col] = (key, score)

    body = rows[header_index + 1:]
    result = []
    for row in body:
        rec = _empty_record(f"OCR-TEMP-{start_index + len(result):03d}")
        for i, value in enumerate(row):
            if not _clean(value):
                continue
            label = headers[i] if i < len(headers) else f"Column {i+1}"
            if i in header_map:
                key, label_score = header_map[i]
                target_label = KEY_TO_LABEL[key]
                # Tables commonly split Qty and Technical Specification into two
                # columns even though PPMP stores them in one Quantity/Size field.
                # Preserve both values instead of letting the stronger one overwrite.
                if key == "quantity_size" and _clean(rec["fields"].get(target_label)):
                    existing = _clean(rec["fields"][target_label])
                    incoming = _clean(value)
                    if incoming and incoming.lower() not in existing.lower():
                        rec["fields"][target_label] = f"{existing}; {incoming}"
                    continue
                _apply_candidate(rec, label, value, " | ".join(row), forced_key=key, source_priority=2, label_score=label_score)
            else:
                _apply_candidate(rec, label, value, " | ".join(row), source_priority=1)
        populated = [k for k, v in rec["fields"].items() if _clean(v)]
        # A real multi-item line should contribute more than one mapped field.
        # This filters table notes/totals from becoming fake procurement rows.
        if len(populated) >= 2:
            result.append(_finalize(rec))
    return result

def map_document(document: Dict[str, Any]) -> Dict[str, Any]:
    """Map extract_document() output to temporary PPMP rows.

    Structured tables are processed first. Explicit form labels from surrounding
    text are then used as shared metadata for table items without overwriting
    row-specific values.
    """
    raw_text = str(document.get("raw_text") or "")
    mapped_rows: List[Dict[str, Any]] = []
    next_index = 1

    for table in document.get("tables") or []:
        table_rows = _rows_from_table(table, next_index)
        mapped_rows.extend(table_rows)
        next_index += len(table_rows)

    lines = _split_lines(raw_text)
    pairs = _label_value_candidates(lines)
    form_record = _empty_record(f"OCR-TEMP-{next_index:03d}")
    for label, value, neighbors, key, label_score in pairs:
        _apply_candidate(
            form_record, label, value, neighbors,
            forced_key=key, source_priority=3, label_score=label_score
        )

    # Contextual value-shape patterns help documents that have weak/implicit labels.
    # They remain lower priority and therefore cannot replace explicit mappings.
    for i, line in enumerate(lines):
        neighbors = " ".join(lines[max(0, i-1):min(len(lines), i+2)])
        if CURRENCY_RE.search(line):
            _apply_candidate(form_record, neighbors, line, neighbors, source_priority=1)
        if QTY_RE.search(line):
            _apply_candidate(form_record, neighbors, line, neighbors, source_priority=1)
        if DATE_RE.search(line):
            _apply_candidate(form_record, neighbors, line, neighbors, source_priority=1)

    form_record = _finalize(form_record)

    # Explicit labels outside a multi-item table (for example Funding: GF or
    # Procurement Method: Shopping) are shared metadata. Inherit them into every
    # table item only when that row does not already have a value for the field.
    if mapped_rows:
        for target_row in mapped_rows:
            for field_label, value in form_record["fields"].items():
                meta = form_record["field_confidence"].get(field_label, {})
                if not _clean(value) or int(meta.get("source_priority", 0) or 0) < 3:
                    continue
                if not _clean(target_row["fields"].get(field_label)):
                    target_row["fields"][field_label] = value
                    copied_meta = dict(meta)
                    copied_meta["inherited_shared_context"] = True
                    target_row["field_confidence"][field_label] = copied_meta
            _finalize(target_row)

    form_populated = sum(1 for v in form_record["fields"].values() if _clean(v))
    if form_populated >= 2:
        desc_label = PPMP_FIELDS["description"]["label"]
        desc = _norm(form_record["fields"].get(desc_label))
        duplicate = bool(desc) and any(_norm(r["fields"].get(desc_label)) == desc for r in mapped_rows)
        # Do not append a second form row when the table itself was a key/value form.
        if not mapped_rows or (not duplicate and any(
            int(m.get("source_priority", 0) or 0) >= 3
            for label, m in form_record["field_confidence"].items()
            if _clean(form_record["fields"].get(label))
        )):
            # If table rows already exist and the form record contains only shared
            # metadata (no distinct description), it is not a separate item.
            if not mapped_rows or desc:
                mapped_rows.append(form_record)

    if not mapped_rows and lines:
        rec = _empty_record("OCR-TEMP-001")
        rec["fields"][PPMP_FIELDS["description"]["label"]] = lines[0][:5000]
        rec["field_confidence"][PPMP_FIELDS["description"]["label"]] = {
            "score": 0.35, "level": "Unmapped", "source_label": "Free text", "signals": {}
        }
        mapped_rows = [_finalize(rec)]

    # Renumber display temp IDs deterministically. Database persistence later assigns
    # durable OCR-TEMP-000001 style identifiers.
    for idx, row in enumerate(mapped_rows, start=1):
        row["temp_id"] = f"OCR-TEMP-{idx:03d}"

    return {
        "rows": mapped_rows,
        "model": model_status(),
        "parser": "offline-schema-semantic-v2",
        "raw_text": raw_text,
        "warnings": list(document.get("warnings") or []),
    }

def validate_record(fields: Dict[str, Any]) -> List[str]:
    errors = []
    description = _clean(fields.get(PPMP_FIELDS["description"]["label"]))
    if not description:
        errors.append("General Description is required.")
    budget = _clean(fields.get(PPMP_FIELDS["budget"]["label"]))
    if budget and not re.search(r"\d", budget):
        errors.append("Estimated Budget must contain a numeric amount.")
    return errors
