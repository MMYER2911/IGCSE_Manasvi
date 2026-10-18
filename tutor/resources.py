from io import BytesIO
from pathlib import Path
from threading import Lock
from pypdf import PdfReader
import pypdfium2 as pdfium


# PDFium calls must be serialised within a process, including across documents.
_pdf_lock = Lock()


def pdf_pages(content):
    """Extract only the visible page rectangle, not adjacent off-page spread text."""
    pages = []
    size = 0
    with _pdf_lock:
        with pdfium.PdfDocument(content) as document:
            for index in range(len(document)):
                page = document[index]
                try:
                    textpage = page.get_textpage()
                    try:
                        text = textpage.get_text_bounded(*page.get_bbox()).replace('\r\n','\n').replace('\r','\n')
                    finally:
                        textpage.close()
                finally:
                    page.close()
                size += len(text)
                if size > 2_000_000:
                    raise ValueError('Extracted text exceeds the 2 million character limit.')
                pages.append(text)
    return pages


def extract(filename, content):
    suffix = Path(filename).suffix.lower()
    if suffix == '.txt':
        pages = [content.decode('utf-8')]
    elif suffix == '.pdf':
        reader = PdfReader(BytesIO(content))
        if reader.is_encrypted:
            raise ValueError('Encrypted PDFs are not supported. Upload an authorised unlocked copy.')
        if len(reader.pages) > 300:
            raise ValueError('Please upload at most 300 pages at a time.')
        pages = pdf_pages(content)
    else:
        raise ValueError('Upload a PDF or UTF-8 text file.')
    if not any(page.strip() for page in pages):
        raise ValueError('No searchable text found. Scanned documents require OCR before upload.')
    if sum(map(len, pages)) > 2_000_000:
        raise ValueError('Extracted text exceeds the 2 million character limit.')
    return [(number, text[offset:offset + 1600])
            for number, text in enumerate(pages, 1)
            for offset in range(0, len(text), 1400) if text[offset:offset + 1600].strip()]
