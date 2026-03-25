from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import re

from PIL import Image
import pytesseract
from pdf2image import convert_from_path


# Set Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

document_bp = Blueprint("document", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# 🔥 Load summarizer ONCE
try:
    summarizer = pipeline("summarization", model="facebook/bart-large-cnn", device=-1)
except Exception as e:
    print("MODEL LOAD ERROR:", e)
    summarizer = None


# ================= OCR FUNCTION =================
def extract_text(filepath):
    text = ""

    try:
        if filepath.lower().endswith(".pdf"):
            images = convert_from_path(
                filepath,
                poppler_path=r"C:\poppler\poppler-25.12.0\Library\bin"
            )

            for img in images:
                text += pytesseract.image_to_string(img)

        else:
            img = Image.open(filepath)
            text = pytesseract.image_to_string(img)

        return text, 1.0

    except Exception as e:
        print("OCR ERROR:", e)
        return "", 0.0


# ================= CLEAN TEXT =================
def clean_text(text):
    return " ".join(text.split())


# ================= EXTRACT VALUES =================
def extract_medical_values(text):
    data = {}

    g = re.search(r'glucose\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if g:
        data["glucose"] = int(g.group(1))

    bp = re.search(r'(\d{2,3})\/(\d{2,3})', text)
    if bp:
        data["bp"] = f"{bp.group(1)}/{bp.group(2)}"

    chol = re.search(r'cholesterol\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if chol:
        data["cholesterol"] = int(chol.group(1))

    return data


# ================= SUMMARIZE =================
def generate_summary(text):
    if not text:
        return "No content found"

    sentences = text.split(".")
    summary = ". ".join(sentences[:3])

    return summary.strip()


# ================= ROUTE =================
@document_bp.route("/upload-report", methods=["POST"])
def upload_and_summarize():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        # 🔥 Save file
        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)

        file.save(filepath)

        # 🔥 OCR
        raw_text, confidence = extract_text(filepath)

        if not raw_text.strip():
            return jsonify({"error": "No text extracted"}), 422

        # 🔥 Clean
        cleaned = clean_text(raw_text)

        # 🔥 Summary
        summary = generate_summary(cleaned)

        # 🔥 Extract values
        values = extract_medical_values(cleaned)

        return jsonify({
            "file_id": unique_name,
            "confidence": confidence,
            "summary": summary,
            "raw_preview": cleaned[:500],
            "extracted_values": values
        })

    except Exception as e:
        print("ERROR:", e)
        return jsonify({"error": str(e)}), 500
