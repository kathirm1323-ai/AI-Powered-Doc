# DocMind AI 🧠

DocMind AI is a professional-grade, single-page AI document analysis platform. It allows users to upload documents (PDF, DOCX, Images) and instantly receive AI-powered summaries, named entity extraction, and sentiment analysis.

## Features

- **Upload Anything:** Supports PDF, Word documents (DOCX), and images (PNG, JPG, WEBP).
- **Intelligent Analysis:** Powered by Llama 3 and Groq inference for lightning-fast, highly accurate document understanding.
- **Entity Extraction:** Automatically identifies and categorizes persons, organizations, locations, dates, and monetary amounts.
- **Sentiment Analysis:** Determines overall tone (positive, negative, neutral) with context.

## 🎨 Premium Cinematic UI

The frontend has been completely overhauled from scratch without the use of heavy frameworks, relying strictly on **Vanilla HTML, CSS, and JS**:

- **Glassmorphism & Gradients:** A sleek, dark-themed UI featuring floating pill navbars, animated gradient text, and dynamic custom shadow properties.
- **Cinematic Backgrounds:** Animated drifting glow orbs overlaying a glowing grid pattern.
- **Dynamic Micro-Interactions:** Smooth hover states, glowing borders, pulsing status indicators, and spinning neural rings during the analysis phase.
- **Fully Responsive:** Adapts seamlessly to all screen sizes, from mobile to desktop.

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
