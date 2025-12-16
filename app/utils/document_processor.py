import io
import pdfplumber
import docx
import pytesseract
from PIL import Image

# ----------- OCR for images -----------

def extract_text_from_image(file_content: bytes) -> str:
    """Extract text from image bytes using Tesseract."""
    try:
        image = Image.open(io.BytesIO(file_content))
        text = pytesseract.image_to_string(image)
        return text.lower()
    except Exception as e:
        print(f"OCR Error: {e}")
        return ""

# ----------- Text extraction for documents -----------

def extract_text_from_document(file_content: bytes, filename: str) -> str:
    """Extract text from PDF or DOCX bytes."""
    content = ""
    file_stream = io.BytesIO(file_content)

    try:
        if filename.lower().endswith(".pdf"):
            with pdfplumber.open(file_stream) as pdf:
                for page in pdf.pages:
                    content += page.extract_text() or ""
        elif filename.lower().endswith(".docx"):
            doc = docx.Document(file_stream)
            for para in doc.paragraphs:
                content += para.text
        return content.lower()
    except Exception as e:
        print(f"Document Extraction Error: {e}")
        return ""

# ----------- KMP implementation -----------

def compute_lps(pattern: str):
    M = len(pattern)
    lps = [0] * M
    length = 0
    i = 1

    while i < M:
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        else:
            if length != 0:
                length = lps[length - 1]
            else:
                lps[i] = 0
                i += 1
    return lps


def kmp_search(text: str, pattern: str) -> bool:
    """Return True if pattern exists in text."""
    N = len(text)
    M = len(pattern)

    if M == 0:
        return False

    lps = compute_lps(pattern)
    i = j = 0

    while i < N:
        if pattern[j] == text[i]:
            i += 1
            j += 1

        if j == M:
            return True
        elif i < N and pattern[j] != text[i]:
            if j != 0:
                j = lps[j - 1]
            else:
                i += 1
    return False
