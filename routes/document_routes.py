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
    patterns = {
        "glucose": r"(glucose|fbs|fasting blood sugar)\s*[:\-]?\s*(\d+)",
        "cholesterol": r"cholesterol\s*[:\-]?\s*(\d+)",
        "triglycerides": r"triglycerides?\s*[:\-]?\s*(\d+)",
        "hdl": r"hdl\s*[:\-]?\s*(\d+)",
        "ldl": r"ldl\s*[:\-]?\s*(\d+)",
        "vldl": r"vldl\s*[:\-]?\s*(\d+)",
        "hba1c": r"hba1c\s*[:\-]?\s*(\d+\.?\d*)",
        "creatinine": r"creatinine\s*[:\-]?\s*(\d+\.?\d*)",
        "urea": r"urea\s*[:\-]?\s*(\d+\.?\d*)",
    }

    data = {}

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(match.lastindex)

    # Blood Pressure
    bp = re.search(r'(\d{2,3})\/(\d{2,3})', text)
    if bp:
        data["bp"] = f"{bp.group(1)}/{bp.group(2)}"

    return data


# ================= SUMMARIZE =================
def generate_summary(text):
    values = extract_medical_values(text)

    if not values:
        sentences = text.split(".")
        return ". ".join(sentences[:2]).strip()

    summary = []

    if "glucose" in values:
        summary.append(f"Glucose level is {values['glucose']} mg/dL.")

    if "hba1c" in values:
        summary.append(f"HbA1c recorded at {values['hba1c']}%.")

    if "cholesterol" in values:
        summary.append(
            f"Total cholesterol is {values['cholesterol']} mg/dL."
        )

    if "triglycerides" in values:
        summary.append(
            f"Triglycerides level is {values['triglycerides']} mg/dL."
        )

    if "hdl" in values:
        summary.append(f"HDL is {values['hdl']} mg/dL.")

    if "ldl" in values:
        summary.append(f"LDL is {values['ldl']} mg/dL.")

    if "vldl" in values:
        summary.append(f"VLDL is {values['vldl']} mg/dL.")

    if "bp" in values:
        summary.append(
            f"Blood pressure recorded as {values['bp']}."
        )

    return " ".join(summary)

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
