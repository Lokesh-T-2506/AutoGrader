"""
gemini_rest.py - Shared Gemini REST API helper.
Uses httpx (sync) with retry/backoff for 429 rate limits.
No deprecated google-generativeai SDK.
"""
import os, base64, json, re, logging, time
import httpx
from PIL import Image
import io

logger = logging.getLogger(__name__)

GEMINI_MODEL = "gemini-2.5-flash"
_RETRY_DELAYS = [15, 30, 60]   # seconds to wait on 429, per attempt


def _api_key() -> str:
    return os.environ.get("GEMINI_API_KEY", "")


def _img_to_b64(pil_img: Image.Image) -> str:
    buf = io.BytesIO()
    pil_img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def gemini_text_from_images(prompt: str, *pil_images,
                             model: str = GEMINI_MODEL, timeout: int = 90) -> str:
    """
    Call Gemini generateContent with text prompt + optional PIL images.
    Retries up to 3 times on 429 with exponential backoff.
    Returns the raw text, or empty string on failure.
    """
    key = _api_key()
    if not key:
        logger.error("GEMINI_API_KEY not set")
        return ""

    parts = [{"text": prompt}]
    for img in pil_images:
        parts.append({
            "inline_data": {
                "mime_type": "image/png",
                "data": _img_to_b64(img)
            }
        })

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/"
        f"models/{model}:generateContent?key={key}"
    )
    payload = {
        "contents": [{"parts": parts}],
        "generationConfig": {"temperature": 0.1}
    }

    for attempt, delay in enumerate([0] + _RETRY_DELAYS):
        if delay > 0:
            logger.warning("Rate limited (429). Waiting %ds before retry %d...", delay, attempt)
            time.sleep(delay)
        try:
            resp = httpx.post(url, json=payload, timeout=timeout)

            if resp.status_code == 429:
                # Will retry on next loop iteration
                logger.warning("429 received on attempt %d", attempt + 1)
                continue

            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            if not candidates:
                logger.error("Gemini returned no candidates. data=%s", str(data)[:300])
                return ""
            raw_text = candidates[0]["content"]["parts"][0]["text"]
            logger.info("Gemini RAW response (first 400 chars): %s", raw_text[:400])
            return raw_text

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 429:
                logger.warning("429 HTTPStatusError on attempt %d", attempt + 1)
                continue
            logger.error("Gemini HTTP error: %s", e)
            return ""
        except Exception as e:
            logger.error("Gemini REST error: %s", e)
            return ""

    logger.error("Gemini call failed after %d attempts (all rate-limited)", len(_RETRY_DELAYS) + 1)
    return ""


def gemini_json_from_images(prompt: str, *pil_images,
                             model: str = GEMINI_MODEL, timeout: int = 90):
    """
    Like gemini_text_from_images but parses and returns a JSON dict.
    Returns None on parse failure or empty response.
    """
    raw = gemini_text_from_images(prompt, *pil_images, model=model, timeout=timeout)
    if not raw:
        return None
    # Strip markdown fences if present
    cleaned = raw.strip()
    cleaned = re.sub(r"^```[a-z]*\n?", "", cleaned).rstrip("` \n")
    try:
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict):
            logger.info("Gemini JSON parsed OK: keys=%s", list(parsed.keys())[:10])
        else:
            logger.info("Gemini JSON parsed OK (list): len=%d", len(parsed) if isinstance(parsed, list) else 0)
        return parsed
    except json.JSONDecodeError as e:
        logger.error("JSON parse error: %s | raw=%s", e, raw[:400])
        return None
