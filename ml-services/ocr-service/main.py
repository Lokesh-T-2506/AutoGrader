import os
os.environ["PADDLE_PDX_DISABLE_MODEL_SOURCE_CHECK"] = "True"
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict
import uvicorn
print("DEBUG: OCR SERVICE STARTING — VERSION 2026-03-30-v4")
import logging
import re
import cv2
import hashlib
import numpy as np
import time
import json
import base64
import io
from PIL import Image
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"))

from gemini_rest import gemini_text_from_images, gemini_json_from_images

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

log_file = r"c:\Users\tallu\OneDrive\Desktop\AutoGrader\ml-services\ocr-service\ocr_service.log"
fh = logging.FileHandler(log_file, mode='a', encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
logger.addHandler(fh)
logging.getLogger().addHandler(fh)
logging.getLogger().setLevel(logging.INFO)

# ── Template OCR Cache ────────────────────────────────────────────────────────
# Key: SHA256(template_bytes)  →  {"zone_ids": [...], "text_map": {...}}
# Eliminates re-running Gemini (75-85s) for every student when template is same.
_template_cache: Dict[str, dict] = {}

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="AutoGrader OCR Service",
    description="Gemini Vision (handwritten) + PaddleOCR (printed)",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Response models ───────────────────────────────────────────────────────────

class OCRResponse(BaseModel):
    text: str
    confidence: float
    model_used: str
    processing_time: float

class ZoneCropResponse(BaseModel):
    crops: Dict[str, str]  # zone_id -> base64_image
    cache_hit: bool
    alignment_confidence: float
    total_processing_time: float


# ── Model manager (PaddleOCR lazy-load) ───────────────────────────────────────

class ModelManager:
    def __init__(self, device: str):
        self.device = device
        self._paddle = None

    def unload_all(self):
        if self._paddle is not None:
            del self._paddle
            self._paddle = None
            gc.collect()

    def get_paddle(self):
        if self._paddle is None:
            logger.info("Initialising PaddleOCR (lazy load)…")
            from paddleocr import PaddleOCR
            self._paddle = PaddleOCR(use_angle_cls=False, lang='en', enable_mkldnn=False)
            logger.info("PaddleOCR ready.")
        return self._paddle


device = "cpu"
model_manager = ModelManager(device)


# ── Helpers ───────────────────────────────────────────────────────────────────

def np_to_pil(image_np: np.ndarray) -> Image.Image:
    return Image.fromarray(cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB))


    logger.info("Gemini layout OK: %s", {k: v[:60] for k, v in text_map.items()})
    return text_map


# ── Segmenter (PaddleOCR path for printed text) ───────────────────────────────

class Segmenter:
    def __init__(self, manager: ModelManager):
        self.manager = manager
        self.default_major = re.compile(r'^([0-9IVX]+)[.,)\s]?')
        self.default_sub   = re.compile(r'^([A-Ga-g])[.,)\s]?')

    def get_anchors(self, paddle_results, major_pattern=None, sub_pattern=None, width=None):
        p_major = re.compile(major_pattern) if major_pattern else self.default_major
        p_sub   = re.compile(sub_pattern)   if sub_pattern   else self.default_sub
        anchors = []
        if not paddle_results or len(paddle_results) == 0:
            return anchors

        page_res      = paddle_results[0]
        boxes         = page_res['rec_polys']
        texts         = page_res['rec_texts']
        left_boundary = (width * 0.25) if width else 500

        for i in range(len(boxes)):
            box       = boxes[i]
            orig_text = texts[i].strip()
            x_left    = min(p[0] for p in box)
            y_top     = min(p[1] for p in box)

            if x_left > left_boundary:
                continue

            major_match = p_major.match(orig_text)
            if major_match:
                anchors.append({
                    "id": str(major_match.group(1)).strip('.').strip(')'),
                    "type": "major", "box": box, "x": x_left, "y": y_top,
                })
                continue

            sub_match = p_sub.match(orig_text)
            if sub_match:
                anchors.append({
                    "id": str(sub_match.group(1)).upper().strip('.').strip(')'),
                    "type": "sub", "box": box, "x": x_left, "y": y_top,
                })

        anchors.sort(key=lambda a: a["y"])
        return anchors

    def detect_diagram_regions(self, image_np):
        try:
            height, width = image_np.shape[:2]
            gray   = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
            edges  = cv2.Canny(gray, 50, 150)
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
            dilated = cv2.dilate(edges, kernel, iterations=2)
            contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            diagrams = []
            for cnt in contours:
                x, y, w, h = cv2.boundingRect(cnt)
                area_pct  = (w * h) / (width * height)
                roi_edges = edges[y:y+h, x:x+w]
                density   = np.sum(roi_edges > 0) / (w * h) if (w * h) > 0 else 0
                aspect    = w / h if h > 0 else 0
                if area_pct > 0.01 and density > 0.12 and 0.5 < aspect < 2.0:
                    diagrams.append([x, y, w, h])
            return diagrams
        except Exception as e:
            logger.error("detect_diagram_regions: %s", e)
            return []

    def build_hierarchy(self, anchors, diagrams=None, width=1000):
        diagrams  = diagrams or []
        hierarchy = []
        current_major = None
        for i, anchor in enumerate(anchors):
            if anchor["type"] == "major":
                current_major = anchor["id"]
                full_id = current_major
            else:
                full_id = (current_major + "." + anchor["id"]) if current_major else anchor["id"]

            y_anchor = anchor["y"]
            next_y   = anchors[i + 1]["y"] if i + 1 < len(anchors) else 1_000_000

            relevant = [
                [dx, dy, dw, dh] for dx, dy, dw, dh in diagrams
                if not (dy + dh < y_anchor or dy > next_y - 5)
            ]

            hierarchy.append({
                "id":           full_id,
                "y_start":      y_anchor,
                "y_end":        next_y - 5,
                "x_start":      anchor["x"] + 30,
                "diagram_mask": relevant,
            })
        return hierarchy

    def get_hierarchy_from_image(self, image_np, major_pattern=None, sub_pattern=None):
        height, width = image_np.shape[:2]
        logger.info("Building hierarchy for %dx%d image…", width, height)
        paddle         = self.manager.get_paddle()
        paddle_results = paddle.ocr(image_np)
        diagrams       = self.detect_diagram_regions(image_np)
        anchors        = self.get_anchors(paddle_results, major_pattern, sub_pattern, width=width)
        hierarchy      = self.build_hierarchy(anchors, diagrams, width=width)
        return paddle_results, hierarchy, width, height

    def extract_and_ocr(self, paddle_results, hierarchy, width):
        text_map = {zone["id"]: "" for zone in hierarchy}
        if not paddle_results or len(paddle_results) == 0:
            return text_map
        page_res = paddle_results[0]
        boxes    = page_res.get('rec_polys', [])
        texts    = page_res.get('rec_texts', [])
        for zone in hierarchy:
            y_start     = zone["y_start"]
            y_end       = zone["y_end"] if zone["y_end"] is not None else 1_000_000
            zone_texts  = []
            for i in range(len(boxes)):
                y_center = sum(p[1] for p in boxes[i]) / 4.0
                if (y_start - 10) <= y_center <= (y_end + 5):
                    zone_texts.append((y_center, texts[i]))
            zone_texts.sort(key=lambda x: x[0])
            text_map[zone["id"]] = " ".join(t[1] for t in zone_texts).strip()
        return text_map

    def extract_printed_from_aligned(self, aligned_img, hierarchy):
        if aligned_img is None or aligned_img.size == 0:
            return {zone["id"]: "" for zone in hierarchy}
        if len(aligned_img.shape) == 3:
            red = aligned_img[:, :, 2]
            _, thresh   = cv2.threshold(red, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
            processed   = cv2.cvtColor(cv2.bitwise_not(thresh), cv2.COLOR_GRAY2BGR)
        else:
            processed = aligned_img
        paddle  = self.manager.get_paddle()
        results = paddle.ocr(processed)
        return self.extract_and_ocr(results, hierarchy, width=aligned_img.shape[1])

    def align_images(self, template_img, target_img):
        logger.info("Aligning images via ORB…")
        t_h, t_w = template_img.shape[:2]
        gray_t = cv2.equalizeHist(cv2.cvtColor(template_img, cv2.COLOR_BGR2GRAY))
        gray_s = cv2.equalizeHist(cv2.cvtColor(target_img,   cv2.COLOR_BGR2GRAY))
        orb    = cv2.ORB_create(nfeatures=8000)
        kp1, des1 = orb.detectAndCompute(gray_t, None)
        kp2, des2 = orb.detectAndCompute(gray_s, None)
        aligned = None
        confidence = 0.0
        if des1 is not None and des2 is not None and len(des1) >= 10 and len(des2) >= 10:
            matcher = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
            matches = sorted(matcher.match(des1, des2), key=lambda m: m.distance)
            num_good = max(10, int(len(matches) * 0.30))
            good = matches[:num_good]
            if len(good) >= 10:
                pts1 = np.float32([kp1[m.queryIdx].pt for m in good])
                pts2 = np.float32([kp2[m.trainIdx].pt for m in good])
                H, mask = cv2.findHomography(pts2, pts1, cv2.RANSAC, 5.0)
                if H is not None and mask is not None:
                    aligned = cv2.warpPerspective(target_img, H, (t_w, t_h))
                    confidence = float(np.sum(mask) / len(mask))
                    logger.info("ORB alignment OK (%d matches, %.2f confidence)", len(good), confidence)
        if aligned is None:
            logger.warning("ORB failed — using resize fallback.")
            aligned = cv2.resize(target_img, (t_w, t_h), interpolation=cv2.INTER_AREA)
            confidence = 0.0
        return aligned, confidence


segmenter = Segmenter(model_manager)


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "service":            "AutoGrader OCR Service",
        "status":             "running",
        "version":            "3.0.0",
        "handwriting_engine": "Gemini 2.5 Flash Vision",
        "printed_engine":     "PaddleOCR",
        "template_cache":     f"{len(_template_cache)} entries",
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.get("/cache/clear")
async def clear_cache():
    """Evict all cached template OCR results."""
    n = len(_template_cache)
    _template_cache.clear()
    logger.info("Template cache cleared (%d entries removed).", n)
    return {"cleared": n}


@app.post("/api/ocr/crop-zones", response_model=ZoneCropResponse)
async def crop_zones(
    template_file: UploadFile = File(...),
    target_file:   UploadFile = File(...),
    major_pattern: Optional[str] = Form(None),
    sub_pattern:   Optional[str] = Form(None),
):
    """
    Final Year Project Orchestrator:
    1. Align student image to template.
    2. Slice into zones (A, B, C...).
    3. Return Base64 crops for the Grading Engine.
    """
    try:
        start = time.time()
        
        template_bytes = await template_file.read()
        template_hash  = _sha256(template_bytes)
        
        # 1. Get Hierarchy (Zone Coordinates)
        if template_hash in _template_cache:
            hierarchy = _template_cache[template_hash]["hierarchy"]
            cache_hit = True
        else:
            template_np = cv2.imdecode(np.frombuffer(template_bytes, np.uint8), cv2.IMREAD_COLOR)
            _, hierarchy, _, _ = segmenter.get_hierarchy_from_image(template_np, major_pattern, sub_pattern)
            _template_cache[template_hash] = {"hierarchy": hierarchy}
            cache_hit = False

        if not hierarchy:
            raise HTTPException(400, "No zone anchors found in template")

        # 2. Align Target (Student Paper)
        target_bytes = await target_file.read()
        target_np    = cv2.imdecode(np.frombuffer(target_bytes, np.uint8), cv2.IMREAD_COLOR)
        
        # We need the template_np again for alignment
        template_np = cv2.imdecode(np.frombuffer(template_bytes, np.uint8), cv2.IMREAD_COLOR)
        aligned, confidence = segmenter.align_images(template_np, target_np)

        # 3. Slice and Encode
        crops_b64 = {}
        h, w = aligned.shape[:2]
        for zone in hierarchy:
            # Increased padding significantly to handle low-alignment papers (Demo Robustness)
            y_start = int(max(0, zone["y_start"] - 80))
            y_end   = int(min(h, zone["y_end"] + 80))
            x_start = int(max(0, zone["x_start"] - 30))
            
            crop = aligned[y_start:y_end, x_start:w]
            
            if crop.size > 0:
                # Optimized for Gemini Vision (lower quality = faster upload, still excellent OCR)
                _, buffer = cv2.imencode(".jpg", crop, [int(cv2.IMWRITE_JPEG_QUALITY), 60])
                b64 = base64.b64encode(buffer).decode("utf-8")
                crops_b64[zone["id"]] = b64

        return ZoneCropResponse(
            crops=crops_b64,
            cache_hit=cache_hit,
            alignment_confidence=confidence,
            total_processing_time=time.time() - start
        )

    except Exception as e:
        logger.error(f"Error in crop_zones: {e}")
        raise HTTPException(500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
