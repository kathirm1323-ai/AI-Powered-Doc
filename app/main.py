"""
DocMind AI — FastAPI backend.
Provides the /analyze endpoint for document analysis
and serves the frontend SPA.
"""

import logging
import mimetypes
import os
from pathlib import Path

# Fix for MIME type issues in Docker/Render
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('application/javascript', '.js')

from fastapi import FastAPI, File, Header, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from .analyzer import analyze_document
from .extractor import extract_text, get_file_type_label, is_supported

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

# Paths
STATIC_DIR = Path(__file__).parent / "static"

# FastAPI app
app = FastAPI(
    title="DocMind AI",
    description="AI-powered document analysis API using Groq + Llama 3",
    version="0.1.0",
)

# CORS — allow all origins for development; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (CSS, JS)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Max file size: 10 MB
MAX_FILE_SIZE = 10 * 1024 * 1024


@app.get("/")
async def root_get():
    """Serve the frontend SPA."""
    return FileResponse(str(STATIC_DIR / "index.html"))


@app.post("/")
async def root_post(
    file: UploadFile = File(None),
    document: UploadFile = File(None),
    image: UploadFile = File(None),
    x_api_key: str = Header(None)
):
    """Alias for /analyze to support some API testers that POST to root."""
    return await analyze(file, document, image, x_api_key)


@app.get("/health")
async def health():
    """Health check endpoint."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    return {
        "status": "healthy",
        "groq_configured": bool(groq_key),
    }


@app.post("/analyze")
async def analyze(
    file: UploadFile = File(None),
    document: UploadFile = File(None),
    image: UploadFile = File(None),
    x_api_key: str = Header(None)
):
    """
    Analyze an uploaded document.
    """
    # Identify which field was used
    actual_file = file or document or image
    
    if not actual_file:
        logger.error("No file found in common fields (file, document, image)")
        raise HTTPException(
            status_code=422,
            detail={
                "error": "missing_file",
                "message": "No file detected. Please send your document in a field named 'file', 'document', or 'image'.",
                "fileName": "unknown",
                "summary": "",
                "entities": [],
                "sentiment": ""
            }
        )

    if x_api_key:
        logger.info(f"API Key provided in header: {x_api_key[:10]}...")

    filename = actual_file.filename or "unknown"
    logger.info(f"Received file: {filename} ({actual_file.content_type})")

    # Validate file type
    if not is_supported(filename):
        raise HTTPException(
            status_code=400,
            detail={
                "error": "unsupported_file_type",
                "message": f"File type not supported. Please upload a PDF, DOCX, or image file.",
                "fileName": filename,
                "summary": "Error: Unsupported type",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    # Read file bytes
    try:
        file_bytes = await actual_file.read()
    except Exception as e:
        logger.error(f"Failed to read file: {e}")
        raise HTTPException(
            status_code=400,
            detail={
                "error": "file_read_error",
                "message": "Could not read the uploaded file.",
                "fileName": filename,
                "summary": "Error: Read failure",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    # Validate file size
    if len(file_bytes) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail={
                "error": "file_too_large",
                "message": f"File exceeds the 10 MB limit ({len(file_bytes) / 1024 / 1024:.1f} MB).",
                "fileName": filename,
                "summary": "Error: Large file",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    if len(file_bytes) == 0:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "empty_file",
                "message": "The uploaded file is empty.",
                "fileName": filename,
                "summary": "Error: Empty file",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    # Extract text
    try:
        text = extract_text(filename, file_bytes)
    except ValueError as e:
        raise HTTPException(
            status_code=422,
            detail={
                "error": "extraction_failed",
                "message": str(e),
                "fileName": filename,
                "summary": "Error: Extraction failed",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    # Run AI analysis
    try:
        analysis = analyze_document(text)
    except ValueError as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "analysis_failed",
                "message": str(e),
                "fileName": filename,
                "summary": "Error: AI analysis failed",
                "entities": [],
                "sentiment": "N/A"
            },
        )

    # Calculate word count
    word_count = len(text.split())
    char_count = len(text)

    # Build response
    response = {
        "summary": analysis["summary"],
        "document_meta": analysis["document_meta"],
        "keywords": analysis["keywords"],
        "entities": analysis["entities"],
        "sentiment": analysis["sentiment"],
        "sentiment_explanation": analysis["sentiment_explanation"],
        "fileName": filename,
        "word_count": word_count,
        "char_count": char_count,
        "file_type": get_file_type_label(filename),
    }

    return JSONResponse(content=response)

    return JSONResponse(content=response)
