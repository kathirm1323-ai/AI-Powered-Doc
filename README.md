# DocMind AI 🧠

DocMind AI is a professional-grade, single-page AI document analysis platform. It allows users to upload documents (PDF, DOCX, Images) and instantly receive AI-powered summaries, named entity extraction, and sentiment analysis.

## Features

- **Upload Anything:** Supports PDF, Word documents (DOCX), and images (PNG, JPG, WEBP).
- **Intelligent Analysis:** Powered by Llama 3 and Groq inference for lightning-fast, highly accurate document understanding.
- **Entity Extraction:** Automatically identifies and categorizes persons, organizations, locations, dates, and monetary amounts.
- **Sentiment Analysis:** Determines overall tone (positive, negative, neutral) with context.

## 🚀 Live Demo

You can view the live deployment of DocMind AI here:
👉 **[https://ai-powered-doc-oxm0.onrender.com/](https://ai-powered-doc-oxm0.onrender.com/)**

## 🎨 $100,000 Ultra-Premium UI

The frontend has been completely redesigned from scratch to meet elite Enterprise SaaS aesthetic standards (inspired by Apple, Stripe, and Vercel) relying strictly on **Vanilla HTML, CSS, and JS**:

- **Glassmorphism 2.0:** High-blur frosted glass panels with precise 1px specular lighting borders.
- **Deep Space Palette:** Ultra-dark monochromatic zinc/slate palette `#09090b` for minimal distraction.
- **Aurora Mesh Backgrounds:** Sophisticated slow-moving volumetric light orbs masked behind cinematic film grain noise.
- **Bento Box Grids:** Results are structured into a modern dashboard layout making data extraction instantly readable.

## Tech Stack

- **Backend:** FastAPI (Python)
- **AI Inference:** Groq API (Llama-3.3-70b-versatile)
- **Text Extraction:** PyMuPDF, pdfplumber, python-docx, pytesseract
- **Frontend:** Pure HTML5, Vanilla CSS3, Vanilla JavaScript
- **Dependency Management:** `uv`

## How to Run Locally

### Prerequisites
- Python 3.12+
- `uv` installed (`pip install uv`)
- Groq API Key

### Setup & Run
1. Clone the repository:
   ```bash
   git clone https://github.com/kathirm1323-ai/AI-Powered-Doc.git
   cd AI-Powered-Doc/docmind
   ```
2. Export your Groq API key:
   - Linux/Mac: `export GROQ_API_KEY="your_api_key_here"`
   - Windows (PowerShell): `$env:GROQ_API_KEY="your_api_key_here"`
3. Run the development server:
   ```bash
   uv run uvicorn app.main:app --reload --port 8000
   ```
4. Open the application in your browser at `http://127.0.0.1:8000`.
