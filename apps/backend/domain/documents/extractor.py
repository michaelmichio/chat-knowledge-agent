import fitz  # PyMuPDF
import docx
import csv

def extract_pdf(path: str) -> str:
    text = []
    with fitz.open(path) as doc:
        for page in doc:
            text.append(page.get_text())
    return "\n".join(text)

def extract_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs)

def extract_csv(path: str) -> str:
    rows = []
    with open(path, newline='', encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            rows.append(", ".join(row))
    return "\n".join(rows)

def extract_text(path: str, mime: str) -> str:
    if mime == "application/pdf":
        return extract_pdf(path)
    elif mime == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
        return extract_docx(path)
    elif mime == "text/csv":
        return extract_csv(path)
    else:
        raise ValueError(f"Tipe file {mime} tidak didukung untuk ekstraksi.")
