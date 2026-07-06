"""
ScanKit API — One endpoint for barcodes, QR codes, and OCR.
"""
import io
import logging
from typing import Optional

from fastapi import FastAPI, File, UploadFile, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image, ImageFilter, ImageOps
from pyzbar import pyzbar
import qrcode
import barcode
from barcode.writer import ImageWriter, SVGWriter

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("scankit")

app = FastAPI(
    title="ScanKit",
    description="One API for barcodes, QR codes, and OCR. Upload an image, get everything back.",
    version="0.1.0",
)


# ── OCR (optional, graceful degradation if tesseract not installed) ──

def extract_text(image: Image.Image) -> str:
    """Extract text from image using OCR. Returns empty string if tesseract not available."""
    try:
        import pytesseract
        text = pytesseract.image_to_string(image)
        return text.strip()
    except ImportError:
        logger.warning("pytesseract not installed — OCR disabled")
        return ""
    except Exception as e:
        logger.warning(f"OCR failed: {e}")
        return ""


# ── Image preprocessing for tough barcodes ──

def preprocess_for_barcode(image: Image.Image) -> Image.Image:
    """Apply preprocessing to improve barcode detection on difficult images."""
    # Convert to grayscale
    gray = image.convert("L")
    # Increase contrast
    gray = ImageOps.autocontrast(gray, cutoff=5)
    # Sharpen
    gray = gray.filter(ImageFilter.SHARPEN)
    return gray


# ── Decode endpoint ──

@app.post("/v1/decode")
async def decode_image(
    image: UploadFile = File(..., description="Image file (JPG, PNG) to scan for barcodes, QR codes, and text"),
    preprocess: bool = Query(True, description="Apply preprocessing to improve detection on difficult images"),
):
    """
    Upload an image. Get back all barcodes, all QR codes, and all OCR text.
    One call. Everything.
    """
    # Validate file type
    if image.content_type and image.content_type not in (
        "image/jpeg", "image/png", "image/webp", "image/tiff", "image/bmp",
    ):
        raise HTTPException(400, detail=f"Unsupported image type: {image.content_type}. Use JPG or PNG.")

    try:
        contents = await image.read()
        pil_image = Image.open(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(400, detail=f"Cannot read image: {e}")

    # Ensure RGB
    if pil_image.mode not in ("RGB", "L"):
        pil_image = pil_image.convert("RGB")

    # Decode barcodes and QR codes
    barcodes = []
    qr_codes = []

    # Try original image first
    decoded = pyzbar.decode(pil_image)

    # If nothing found and preprocessing enabled, try preprocessed version
    if not decoded and preprocess:
        processed = preprocess_for_barcode(pil_image)
        decoded = pyzbar.decode(processed)

    for d in decoded:
        item = {
            "type": d.type,
            "value": d.data.decode("utf-8", errors="replace"),
            "position": {
                "x": d.rect.left,
                "y": d.rect.top,
                "width": d.rect.width,
                "height": d.rect.height,
            },
        }
        if d.type == "QRCODE":
            qr_codes.append(item)
        else:
            barcodes.append(item)

    # OCR
    ocr_text = extract_text(pil_image)

    return {
        "barcodes": barcodes,
        "qr_codes": qr_codes,
        "text": ocr_text,
        "barcode_count": len(barcodes),
        "qr_count": len(qr_codes),
        "image_size": {"width": pil_image.width, "height": pil_image.height},
    }


# ── Generate endpoint ──

SUPPORTED_FORMATS = {
    "qr": "QR Code",
    "code128": "Code 128",
    "ean13": "EAN-13",
    "ean8": "EAN-8",
    "upca": "UPC-A",
    "isbn13": "ISBN-13",
    "isbn10": "ISBN-10",
    "issn": "ISSN",
    "code39": "Code 39",
    "pzn": "PZN",
    "itf": "ITF",
}


@app.post("/v1/generate")
async def generate_barcode(
    value: str = Query(..., description="The value to encode into the barcode/QR code"),
    format: str = Query("qr", description=f"Barcode format. Supported: {', '.join(SUPPORTED_FORMATS.keys())}"),
    output: str = Query("png", description="Output format: png or svg"),
    size: int = Query(300, ge=100, le=2000, description="Image size in pixels"),
):
    """
    Generate a barcode or QR code. Returns PNG image or SVG.
    One endpoint. All formats.
    """
    if format not in SUPPORTED_FORMATS:
        raise HTTPException(400, detail=f"Unsupported format '{format}'. Supported: {', '.join(SUPPORTED_FORMATS.keys())}")

    # QR code uses a different library
    if format == "qr":
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(value)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        img = img.resize((size, size), Image.LANCZOS)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return StreamingResponse(buf, media_type="image/png")

    # 1D barcodes use python-barcode
    try:
        if output == "svg":
            writer = SVGWriter()
            media_type = "image/svg+xml"
            buf = io.BytesIO()
            bc = barcode.get(format, value, writer=writer)
            bc.write(buf)
            buf.seek(0)
            return StreamingResponse(buf, media_type=media_type)
        else:
            writer = ImageWriter()
            buf = io.BytesIO()
            # python-barcode writes to file, so we use a temp approach
            bc = barcode.get(format, value, writer=writer)
            # Render to PIL image
            options = {"module_width": 0.3, "module_height": 15.0, "quiet_zone": 6.5, "font_size": 10}
            bc_io = io.BytesIO()
            bc.write(bc_io, options=options)
            bc_io.seek(0)
            return StreamingResponse(bc_io, media_type="image/png")

    except Exception as e:
        raise HTTPException(400, detail=f"Failed to generate {format} barcode: {e}")


# ── Health & root ──

@app.get("/")
def root():
    return {
        "service": "ScanKit",
        "version": "0.1.0",
        "endpoints": {
            "decode": "POST /v1/decode",
            "generate": "POST /v1/generate",
        },
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
