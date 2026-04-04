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
    Analyze an uploaded document or text with universal detection (Form or JSON).
    """
    # Pre-populate required root fields for tester compatibility
    res = {
        "fileName": "unknown",
        "summary": "Processing...",
        "entities": [],
        "sentiment": "Neutral",
        "error": ""
    }

    try:
        content_type = request.headers.get("content-type", "")
        logger.info(f"Incoming Request Content-Type: {content_type}")
        
        actual_file = None
        extracted_text = None
        filename = "document.txt"

        if "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            logger.info(f"Form keys received: {list(form.keys())}")
            for name, value in form.items():
                if not isinstance(value, str):
                    actual_file = value
                    filename = getattr(value, "filename", "unknown") or "unknown"
                    logger.info(f"Detected file in form field: '{name}', type: {type(value)}")
                    break
                elif isinstance(value, str):
                    if not extracted_text or name.lower() in ["text", "content", "document", "file", "data", "url"]:
                        extracted_text = value
                    logger.info(f"Detected raw text in form field: '{name}'")
                    
        elif "application/json" in content_type:
            data = await request.json()
            logger.info(f"JSON keys received: {list(data.keys())}")
            
            # Auto-detect any large string as our content, or specific keys
            for key, val in data.items():
                if key.lower() in ["filename", "file_name", "name"]:
                    filename = str(val)
                elif isinstance(val, str):
                    if not extracted_text or key.lower() in ["text", "content", "data", "document", "file", "url"]:
                        extracted_text = str(val)
                    logger.info(f"Detected content in JSON key: '{key}'")
                    # don't break, keep looking for filename but we have text

        else:
            # Fallback for plain text or unexpected content types
            body_bytes = await request.body()
            if body_bytes:
                text_body = body_bytes.decode('utf-8', errors='ignore').strip()
                if text_body:
                    extracted_text = text_body
                    logger.info("Detected fallback raw body text.")

        # 3. Process the results
        if actual_file:
            file_bytes = await actual_file.read()
            if len(file_bytes) > 0:
                extracted_text = extract_text(filename, file_bytes)
            else:
                res["error"] = "empty_file"
                return JSONResponse(status_code=400, content=res)
        
        if not extracted_text:
            logger.error("No text or file found in request.")
            res["error"] = "missing_input"
            res["summary"] = "Error: Please upload a file or send text as 'content' or 'document'."
            return JSONResponse(status_code=422, content=res)

        res["fileName"] = filename
        
        # AI Analysis
        analysis = analyze_document(extracted_text)
        
        # Merge results into response
        res.update({
            "summary": analysis["summary"],
            "entities": analysis["entities"],
            "sentiment": analysis["sentiment"],
            "document_meta": analysis["document_meta"],
            "keywords": analysis["keywords"],
            "sentiment_explanation": analysis["sentiment_explanation"],
            "word_count": len(extracted_text.split()),
            "char_count": len(extracted_text),
            "file_type": get_file_type_label(filename),
        })

        return JSONResponse(content=res)

    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        res["error"] = "internal_server_error"
        res["summary"] = f"An error occurred: {str(e)}"
        return JSONResponse(status_code=500, content=res)

    return JSONResponse(content=response)
