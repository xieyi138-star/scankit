<p align="center">
  <img src="https://img.shields.io/github/license/xieyi138-star/scankit?color=orange" alt="MIT">
  <img src="https://img.shields.io/github/stars/xieyi138-star/scankit?style=social" alt="GitHub stars">
  <img src="https://img.shields.io/badge/Python-3.11+-3670A0?logo=python" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/Docker-Ready-blue?logo=docker" alt="Docker Ready">
</p>

<h1 align="center">ScanKit</h1>

<p align="center">
  <strong>One API call. Barcodes + QR codes + OCR. At the same time.</strong><br>
  Upload an image. Get back every barcode, every QR code, and all the text.<br>
  No SDK. No setup. Just HTTP.
</p>

<p align="center">
  <a href="https://scankit.vercel.app/"><strong>🌐 Website</strong></a> ·
  <a href="https://scankit.vercel.app/"><strong>🚀 Get API Key</strong></a>
</p>

---

## 😤 The Problem

Reading a barcode from an image shouldn't require:

- A $2,000/year Dynamsoft SDK license
- Installing ZXing (Java) + pytesseract (C++) + three Python wrappers
- Two completely separate pipelines for barcodes vs OCR
- 200 lines of boilerplate to decode, rotate, sharpen, and extract

**And nobody** combines barcode reading + OCR text extraction into a single API call. Even though the most common use case — "read the tracking number AND the shipping address from this photo of a label" — needs both.

---

## 💡 ScanKit: One Call, Everything

```bash
curl -X POST https://api.scankit.dev/v1/decode \
  -H "Authorization: Bearer sk_live_xxx" \
  -F "image=@shipping_label.jpg"
```

```json
{
  "barcodes": [
    { "type": "CODE128", "value": "1Z999AA10123456784", "position": { "x": 120, "y": 45 } }
  ],
  "qr_codes": [],
  "text": "SHIP TO:\nJohn Doe\n123 Main St, Springfield, IL 62701\nORDER #88471",
  "barcode_count": 1,
  "qr_count": 0
}
```

### Generate, too

```bash
curl -X POST "https://api.scankit.dev/v1/generate?value=HELLO&format=qr&size=300" > qr.png
```

---

## 🆚 Why Not Just Use...

| Tool | The Problem |
|------|-------------|
| **ZXing (pyzbar)** | Misses ~1 in 6 damaged/badly-printed barcodes. No OCR. Library, not a service. |
| **Dynamsoft** | $2,000+/year. Great software. Absurd pricing for indie devs. |
| **Google Vision API** | $1.50 per 1,000 images. Adds up fast. Google dependency. |
| **pytesseract alone** | OCR only. No barcodes. Requires separate ZXing pipeline. |
| **Cloudmersive** | Only cloud option with combined barcode+OCR. No self-host. Per-call pricing. |

**ScanKit: free self-hosted, or $9/month cloud. Combined barcode + QR + OCR. One endpoint.**

---

## 🚀 Quick Start

### Option A: Docker

```bash
docker run -d -p 8080:8080 ghcr.io/xieyi138-star/scankit:latest
```

### Option B: Python

```bash
pip install -r requirements.txt
python main.py
# API at http://localhost:8080
# Docs at http://localhost:8080/docs
```

### Option C: Hosted API

[Sign up for early access →](https://scankit.vercel.app/)

---

## 📋 Supported Formats

### Barcode Reading
- Code 128, Code 39, Code 93
- EAN-8, EAN-13
- UPC-A, UPC-E
- ITF (Interleaved 2 of 5)
- PDF417
- Data Matrix
- QR Code

### Barcode Generation
- QR Code
- Code 128
- EAN-13, EAN-8
- UPC-A
- Code 39
- ISBN-13, ISBN-10, ISSN
- PZN, ITF

### Image Preprocessing
- Auto-contrast enhancement
- Sharpening
- Grayscale conversion
- Works on phone photos at angles

---

## 🏗️ Tech Stack

| Layer | Choice |
|------|------|
| **Framework** | FastAPI (Python 3.11+) |
| **Barcode reading** | pyzbar (libzbar wrapper) |
| **Barcode generation** | python-barcode + qrcode |
| **OCR** | Tesseract (via pytesseract) |
| **Image processing** | Pillow |
| **Deployment** | Docker / uvicorn |

---

## 📍 Roadmap

- [x] `/v1/decode` — combined barcode + QR + OCR
- [x] `/v1/generate` — barcode & QR generation
- [x] Image preprocessing (contrast, sharpen)
- [x] Swagger docs (`/docs`)
- [ ] API key authentication
- [ ] Usage tracking & rate limiting
- [ ] PDF page support (multi-page)
- [ ] EAN product lookup integration
- [ ] Managed cloud hosting ($9/month)
- [ ] Self-hosted Docker image

---

## 📄 License

MIT — use it, fork it, self-host it, embed it. No strings.

---

<p align="center">
  <a href="https://scankit.vercel.app/"><strong>🌐 Website</strong></a> ·
  <a href="https://github.com/xieyi138-star/scankit/issues"><strong>💡 Request a Feature</strong></a>
</p>

<hr>

<p align="center">
  <sub>Built by <a href="https://github.com/xieyi138-star">@xieyi138-star</a> · Also check out <a href="https://github.com/xieyi138-star/uptix">Uptix</a> — self-hosted status pages</sub>
</p>
