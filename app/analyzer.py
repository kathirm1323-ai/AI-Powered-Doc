"""
AI-powered document analysis using Groq (Llama 3).
Extracts summary, entities, and sentiment from document text.
"""

import json
import logging
import os
import re

from groq import Groq

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
MODEL = "llama-3.3-70b-versatile"

ANALYSIS_PROMPT = """You are a professional document analyst. Analyze the following document text and return a JSON response with exactly this structure:

{{
  "summary": {{
    "brief": "A 2-3 sentence TL;DR version of the summary.",
    "detailed": "A comprehensive full paragraph summary of the document's main content.",
    "bullets": ["Key point 1", "Key point 2", "Key point 3", "Key point 4", "Key point 5"]
  }},
  "document_meta": {{
    "topic": "The primary topic (e.g. Finance, Technology, Recipe)",
    "reading_time": "Estimated reading time (e.g. ~2 min)",
    "complexity": "Basic | Intermediate | Advanced",
    "language": "Language of the document (e.g. English)"
  }},
  "keywords": ["top", "8", "most", "important", "keywords", "or", "key", "phrases"],
  "entities": {{
    "persons": ["list of person names mentioned"],
    "organizations": ["list of organization/company names mentioned"],
    "locations": ["list of geographic locations, cities, countries mentioned"],
    "dates": ["list of dates, years, time periods mentioned"],
    "monetary_amounts": ["list of monetary values, prices, costs mentioned"]
  }},
  "sentiment": "positive | negative | neutral",
  "sentiment_explanation": "A 1-2 sentence explanation of why the document has this sentiment."
}}

Rules:
- Return ONLY valid JSON, no markdown, no code fences, no extra text.
- If a category has no entities, use an empty array [].
- Be thorough in entity extraction — capture ALL mentioned entities.
- For sentiment, analyze the overall tone, word choice, and subject matter.
- The summary should be informative and capture the document's essence.

DOCUMENT TEXT:
---
{text}
---

Return the JSON analysis now:"""


def _clean_json_response(response_text: str) -> str:
    """Clean up LLM response to extract valid JSON."""
    text = response_text.strip()

    # Remove markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (with optional language tag)
        text = re.sub(r"^```(?:json)?\s*\n?", "", text)
        # Remove closing fence
        text = re.sub(r"\n?```\s*$", "", text)

    # Try to find JSON object in the response
    brace_start = text.find("{")
    brace_end = text.rfind("}")
    if brace_start != -1 and brace_end != -1:
        text = text[brace_start : brace_end + 1]

    return text.strip()


def _validate_analysis(data: dict) -> dict:
    """Validate and normalize the analysis response structure."""
    
    # Handle summary object
    raw_summary = data.get("summary", {})
    if isinstance(raw_summary, str):
        summary_obj = {"brief": raw_summary, "detailed": raw_summary, "bullets": [raw_summary]}
    else:
        summary_obj = {
            "brief": str(raw_summary.get("brief", "No brief summary available.")),
            "detailed": str(raw_summary.get("detailed", "No detailed summary available.")),
            "bullets": raw_summary.get("bullets", []) if isinstance(raw_summary.get("bullets"), list) else []
        }
    
    # Handle document_meta
    raw_meta = data.get("document_meta", {})
    meta_obj = {
        "topic": str(raw_meta.get("topic", "Unknown")),
        "reading_time": str(raw_meta.get("reading_time", "~1 min")),
        "complexity": str(raw_meta.get("complexity", "Basic")),
        "language": str(raw_meta.get("language", "Unknown"))
    }
    
    # Handle keywords
    keywords = data.get("keywords", [])
    keywords_list = [str(k) for k in keywords] if isinstance(keywords, list) else []

    result = {
        "summary": summary_obj,
        "document_meta": meta_obj,
        "keywords": keywords_list,
        "entities": {},
        "sentiment": "neutral",
        "sentiment_explanation": str(
            data.get("sentiment_explanation", "No sentiment analysis available.")
        ),
    }

    # Validate entities
    entities = data.get("entities", {})
    entity_keys = ["persons", "organizations", "locations", "dates", "monetary_amounts"]
    for key in entity_keys:
        val = entities.get(key, [])
        if isinstance(val, list):
            result["entities"][key] = [str(v) for v in val if v]
        else:
            result["entities"][key] = []

    # Validate sentiment
    sentiment = str(data.get("sentiment", "neutral")).lower().strip()
    if sentiment in ("positive", "negative", "neutral"):
        result["sentiment"] = sentiment
    else:
        result["sentiment"] = "neutral"

    return result


def analyze_document(text: str) -> dict:
    """
    Send document text to Groq LLM for analysis.
    Returns structured analysis with summary, entities, and sentiment.
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY environment variable is not set. "
            "Please set it to your Groq API key."
        )

    # Truncate very long documents to stay within context limits
    max_chars = 28000
    truncated = False
    if len(text) > max_chars:
        text = text[:max_chars]
        truncated = True
        logger.info(f"Document truncated to {max_chars} characters for analysis")

    prompt = ANALYSIS_PROMPT.format(text=text)
    if truncated:
        prompt += "\n\nNote: This document was truncated due to length. Analyze what is available."

    try:
        client = Groq(api_key=GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a document analysis AI. You always respond with valid JSON only.",
                },
                {"role": "user", "content": prompt},
            ],
            model=MODEL,
            temperature=0.3,
            max_tokens=2048,
            top_p=0.9,
        )

        response_text = chat_completion.choices[0].message.content
        logger.info(f"Raw LLM response length: {len(response_text)} chars")

        # Parse and validate
        cleaned = _clean_json_response(response_text)
        data = json.loads(cleaned)
        return _validate_analysis(data)

    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM JSON response: {e}")
        logger.error(f"Raw response: {response_text[:500]}")
        raise ValueError(
            "The AI returned an invalid response. Please try again."
        )
    except Exception as e:
        logger.error(f"Groq API error: {e}")
        raise ValueError(f"AI analysis failed: {str(e)}")
