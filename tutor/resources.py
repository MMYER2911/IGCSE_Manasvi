from io import BytesIO
from pathlib import Path
from pypdf import PdfReader


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
        pages = [page.extract_text() or '' for page in reader.pages]
    else:
        raise ValueError('Upload a PDF or UTF-8 text file.')
    if not any(page.strip() for page in pages):
        raise ValueError('No searchable text found. Scanned documents require OCR before upload.')
    if sum(map(len, pages)) > 2_000_000:
        raise ValueError('Extracted text exceeds the 2 million character limit.')
    return [(number, text[offset:offset + 1600])
            for number, text in enumerate(pages, 1)
            for offset in range(0, len(text), 1400) if text[offset:offset + 1600].strip()]
