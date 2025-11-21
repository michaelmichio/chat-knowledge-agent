import os
import fitz  # PyMuPDF
import docx
import csv

# List MIME yang dianggap valid
PDF_MIMES = [
    "application/pdf",
    "application/x-pdf",
    "application/octet-stream",
]

DOCX_MIMES = [
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/octet-stream",
    "application/zip",
]

CSV_MIMES = [
    "text/csv",
    "application/vnd.ms-excel",
    "application/octet-stream",
]

# ----------------------------
# CLEAN TEXT
# ----------------------------

def clean_text(text: str) -> str:
    return (
        text.replace("\r", " ")
            .replace("  ", " ")
            .replace("\n\n", "\n")
            .strip()
    )

# ----------------------------
# PDF
# ----------------------------

def extract_pdf(path: str) -> str:
    try:
        text = []
        with fitz.open(path) as doc:
            for page in doc:
                content = page.get_text()
                if content:
                    text.append(content)
        return clean_text("\n".join(text))
    except Exception as e:
        raise ValueError(f"Gagal ekstrak PDF: {e}")

# ----------------------------
# DOCX
# ----------------------------

def extract_docx(path: str) -> str:
    try:
        doc = docx.Document(path)
        text = "\n".join(p.text for p in doc.paragraphs)
        return clean_text(text)
    except Exception as e:
        raise ValueError(f"Gagal ekstrak DOCX: {e}")

# ----------------------------
# CSV
# ----------------------------

def extract_csv(path: str) -> str:
    text = []
    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                text.append(", ".join(row))
    except UnicodeDecodeError:
        # fallback encoding lain
        with open(path, newline="", encoding="latin1") as f:
            reader = csv.reader(f)
            for row in reader:
                text.append(", ".join(row))
    except Exception as e:
        raise ValueError(f"Gagal ekstrak CSV: {e}")

    return clean_text("\n".join(text))

# ----------------------------
# MASTER EXTRACTOR
# ----------------------------

def extract_text(path: str, mime: str = None) -> str:
    ext = os.path.splitext(path)[1].lower()

    # auto detect mime jika None
    if mime is None:
        if ext == ".pdf": mime = "application/pdf"
        elif ext == ".docx": mime = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        elif ext == ".csv": mime = "text/csv"
        else:
            raise ValueError(f"Tipe file tidak terdeteksi: path={path}")

    # PDF
    if mime in PDF_MIMES or ext == ".pdf":
        return extract_pdf(path)

    # DOCX
    if mime in DOCX_MIMES or ext == ".docx":
        return extract_docx(path)

    # CSV
    if mime in CSV_MIMES or ext == ".csv":
        return extract_csv(path)

    raise ValueError(f"Tipe file tidak didukung: mime={mime}, ext={ext}")
