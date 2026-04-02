"""
Text extraction from PDF, DOCX, and image files.
Supports multiple extraction strategies with graceful fallbacks.
"""

import io
import logging
from pathlib import Path

import fitz  # PyMuPDF
import pdfplumber
from docx import Document
from PIL import Image

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {
    "pdf": "PDF Document",
    "docx": "Word Document",
    "doc": "Word Document",
    "png": "Image",
    "jpg": "Image",
    "jpeg": "Image",
    "webp": "Image",
    "bmp": "Image",
    "tiff": "Image",
    "tif": "Image",
}

IMAGE_EXTENSIONS = {"png", "jpg", "jpeg", "webp", "bmp", "tiff", "tif"}


def get_file_extension(filename: str) -> str:
    """Extract and normalize file extension."""
    return Path(filename).suffix.lstrip(".").lower()


def is_supported(filename: str) -> bool:
    """Check if the file extension is supported."""
    return get_file_extension(filename) in SUPPORTED_EXTENSIONS


def get_file_type_label(filename: str) -> str:
    """Get a human-readable file type label."""
    ext = get_file_extension(filename)
    return SUPPORTED_EXTENSIONS.get(ext, "Unknown")


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF using PyMuPDF (primary) with pdfplumber fallback.
    """
    text = ""

    # Strategy 1: PyMuPDF (fast, handles most PDFs well)
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        for page in doc:
            page_text = page.get_text("text")
            if page_text:
                text += page_text + "\n"
        doc.close()
    except Exception as e:
        logger.warning(f"PyMuPDF extraction failed: {e}")

    # Strategy 2: pdfplumber fallback (better for table-heavy PDFs)
    if not text.strip():
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
        except Exception as e:
            logger.warning(f"pdfplumber extraction failed: {e}")

    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file."""
    try:
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [para.text for para in doc.paragraphs if para.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        raise ValueError(f"Failed to extract text from DOCX: {e}")


def extract_text_from_image(file_bytes: bytes) -> str:
    """
    Extract text from an image using OCR (pytesseract).
    Falls back to a descriptive placeholder if Tesseract is not installed.
    """
    try:
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
        return text.strip()
    except ImportError:
        logger.warning("pytesseract not available, using basic image analysis")
        return _basic_image_info(file_bytes)
    except Exception as e:
        logger.warning(f"OCR extraction failed: {e}")
        return _basic_image_info(file_bytes)


def _basic_image_info(file_bytes: bytes) -> str:
    """Provide basic image metadata when OCR is unavailable."""
    try:
        image = Image.open(io.BytesIO(file_bytes))
        w, h = image.size
        mode = image.mode
        fmt = image.format or "Unknown"
        return (
            f"[Image file: {fmt} format, {w}x{h} pixels, {mode} color mode. "
            f"OCR is not available on this server. "
            f"The image contains visual content that cannot be transcribed to text.]"
        )
    except Exception:
        return "[Image file uploaded. Unable to extract text content.]"


def extract_text(filename: str, file_bytes: bytes) -> str:
    """
    Main extraction dispatcher. Routes to the appropriate extractor
    based on file extension.
    """
    ext = get_file_extension(filename)

    if not is_supported(filename):
        raise ValueError(
            f"Unsupported file type: .{ext}. "
            f"Supported types: {', '.join(sorted(SUPPORTED_EXTENSIONS.keys()))}"
        )

    if ext == "pdf":
        text = extract_text_from_pdf(file_bytes)
    elif ext in ("docx", "doc"):
        text = extract_text_from_docx(file_bytes)
    elif ext in IMAGE_EXTENSIONS:
        text = extract_text_from_image(file_bytes)
    else:
        raise ValueError(f"No extractor available for .{ext}")

    if not text.strip():
        raise ValueError(
            "Could not extract any text from the uploaded file. "
            "The file may be empty, corrupted, or contain only images/graphics."
        )

    return text
