from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
import os
import uuid
import re

from PIL import Image
import fitz  # PyMuPDF

document_bp = Blueprint("document", __name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================= OCR FUNCTION =================
def extract_text(filepath):
    text = ""

    try:
        # PDF extraction (cloud friendly)
        if filepath.lower().endswith(".pdf"):
            doc = fitz.open(filepath)

            for page in doc:
                text += page.get_text()

        # Image extraction
        else:
            img = Image.open(filepath)

            # fallback simple extraction
            text = img.convert("L").tobytes().decode("latin-1", errors="ignore")

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

    summary_parts = []

    # Extract Glucose
    g = re.search(r'glucose\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if g:
        summary_parts.append(f"Glucose level is {g.group(1)} mg/dL.")

    # Extract BP
    bp = re.search(r'(\d{2,3})\/(\d{2,3})', text)
    if bp:
        summary_parts.append(
            f"Blood pressure recorded as {bp.group(1)}/{bp.group(2)}."
        )

    # Extract Cholesterol
    chol = re.search(r'cholesterol\s*[:\-]?\s*(\d+)', text, re.IGNORECASE)
    if chol:
        summary_parts.append(
            f"Cholesterol level is {chol.group(1)} mg/dL."
        )

    if summary_parts:
        return " ".join(summary_parts)

    # fallback
    sentences = text.split(".")
    return ". ".join(sentences[:2]).strip()

# ================= ROUTE =================
@document_bp.route("/upload-report", methods=["POST"])
def upload_and_summarize():
    try:
        if "file" not in request.files:
            return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        if file.filename == "":
            return jsonify({"error": "Empty filename"}), 400

        filename = secure_filename(file.filename)
        unique_name = f"{uuid.uuid4().hex}_{filename}"
        filepath = os.path.join(UPLOAD_FOLDER, unique_name)

        file.save(filepath)

        raw_text, confidence = extract_text(filepath)

        if not raw_text.strip():
            return jsonify({"error": "No text extracted"}), 422

        cleaned = clean_text(raw_text)

        summary = generate_summary(cleaned)

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
