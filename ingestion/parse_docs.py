from pathlib import Path
from pypdf import PdfReader
import re, json

RAW_DIR = Path("data/raw")
OUT_DIR = Path("data/processed")
OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_pdf(pdf_path: Path):
    reader = PdfReader(str(pdf_path))
    sections = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        # normalize whitespace
        text = re.sub(r"\s+", " ", text)
        sections.append({"doc": pdf_path.name, "page": i + 1, "text": text.strip()})
    return sections


if __name__ == "__main__":
    all_docs = []
    for pdf in RAW_DIR.glob("*.pdf"):
        all_docs.extend(parse_pdf(pdf))

    with open(OUT_DIR / "docs.jsonl", "w") as f:
        for row in all_docs:
            f.write(json.dumps(row) + "\n")
