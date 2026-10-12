"""One-time online installer for the local PPMP semantic mapping model."""
from pathlib import Path
import shutil
import sys

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
DEST = Path(__file__).resolve().parent / "models" / "ocr_mapper" / "all-MiniLM-L6-v2"


def main():
    try:
        from sentence_transformers import SentenceTransformer
    except Exception as exc:
        print("sentence-transformers is not installed. Run: python -m pip install -r requirements.txt")
        print(exc)
        return 1
    DEST.parent.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {MODEL_NAME} for one-time offline installation...")
    model = SentenceTransformer(MODEL_NAME)
    if DEST.exists():
        shutil.rmtree(DEST)
    model.save(str(DEST))
    print(f"Saved local semantic model to: {DEST}")
    print("Verifying strict local-only load...")
    try:
        SentenceTransformer(str(DEST), local_files_only=True)
    except TypeError:
        SentenceTransformer(str(DEST))
    print("Offline semantic model verification passed.")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
