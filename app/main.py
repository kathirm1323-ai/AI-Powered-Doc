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

from fastapi import FastAPI, File, Header, HTTPException, UploadFile, Request
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
async def root_post(request: Request, x_api_key: str = Header(None)):
    """Universal entry point for API testers."""
    return await analyze(request, x_api_key)


@app.get("/health")
async def health():
    """Health check endpoint."""
    groq_key = os.getenv("GROQ_API_KEY", "")
    return {
        "status": "healthy",
        "groq_configured": bool(groq_key),
    }


@app.post("/analyze")
async def analyze(request: Request, x_api_key: str = Header(None)):
    """
    Analyze an uploaded document with universal field detection.
    """
    error_response = {
        "fileName": "unknown",
        "summary": "N/A",
        "entities": [],
        "sentiment": "N/A",
        "error": ""
    }

    try:
        # Detect any file field in the incoming form data
        form = await request.form()
        actual_file = None
        for name, value in form.items():
            if isinstance(value, UploadFile):
                actual_file = value
                logger.info(f"Detected file in field: '{name}'")
                break
        
        if not actual_file:
            logger.error("No UploadFile found in any form field.")
            error_response["error"] = "missing_file"
            return JSONResponse(status_code=422, content=error_response)

        if x_api_key:
            logger.info(f"API Key provided: {x_api_key[:10]}...")

        filename = actual_file.filename or "unknown"
        error_response["fileName"] = filename
        logger.info(f"Processing: {filename} ({actual_file.content_type})")

        # Validate file type
        if not is_supported(filename):
            error_response["error"] = "unsupported_file_type"
            error_response["summary"] = "Error: This file type is not supported."
            return JSONResponse(status_code=400, content=error_response)

        # Read file bytes
        file_bytes = await actual_file.read()
        if len(file_bytes) > MAX_FILE_SIZE:
            error_response["error"] = "file_too_large"
            error_response["summary"] = "Error: File exceeds 10MB limit."
            return JSONResponse(status_code=413, content=error_response)

        if len(file_bytes) == 0:
            error_response["error"] = "empty_file"
            error_response["summary"] = "Error: The uploaded file is empty."
            return JSONResponse(status_code=400, content=error_response)

        # Extract & Analyze
        text = extract_text(filename, file_bytes)
        analysis = analyze_document(text)

        # Build Success Response (Root keys for tester compatibility)
        return JSONResponse(content={
            "fileName": filename,
            "summary": analysis["summary"],
            "entities": analysis["entities"],
            "sentiment": analysis["sentiment"],
            "document_meta": analysis["document_meta"],
            "keywords": analysis["keywords"],
            "sentiment_explanation": analysis["sentiment_explanation"],
            "word_count": len(text.split()),
            "char_count": len(text),
            "file_type": get_file_type_label(filename),
        })

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        error_response["error"] = "internal_server_error"
        error_response["summary"] = f"Error: {str(e)}"
        return JSONResponse(status_code=500, content=error_response)

    return JSONResponse(content=response)
