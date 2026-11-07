from pathlib import Path
import logging
import re
import uuid

import fitz  # PyMuPDF
from PIL import Image, UnidentifiedImageError
from flask import Blueprint, current_app, jsonify, request
from flask_jwt_extended import jwt_required
from werkzeug.utils import secure_filename

document_bp = Blueprint("document", __name__)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
ALLOWED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg"}
MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MiB


def _allowed_extension(filename):
    return Path(filename).suffix.lower() in ALLOWED_EXTENSIONS


def _extract_pdf_text(filepath):
    """Extract embedded PDF text. Scanned/image-only PDFs require OCR and are unsupported."""
    chunks = []
    with fitz.open(filepath) as doc:
        for page in doc:
            chunks.append(page.get_text("text"))
    return "\n".join(chunks)


def extract_text(filepath):
    """
    Extract text from a text-based PDF.
    Images are not OCR'd here; reject them rather than treating pixel bytes as text.
    Returns (text, confidence). Confidence is None because no OCR confidence is computed.
    """
    try:
        suffix = Path(filepath).suffix.lower()
        if suffix == ".pdf":
            return _extract_pdf_text(filepath), None

        if suffix in {".png", ".jpg", ".jpeg"}:
            # Validate that the file is a decodable image; actual OCR is not implemented.
            with Image.open(filepath) as image:
                image.verify()
            return "", None

        return "", None
    except (fitz.FileDataError, UnidentifiedImageError, OSError, ValueError):
        logger.warning("Unable to extract text from uploaded report", exc_info=True)
        return "", None


def clean_text(text):
    return " ".join(text.split())


def extract_medical_values(text):
    patterns = {
        "glucose": r"(glucose|fbs|fasting blood sugar)\s*[:\-]?\s*(\d+)",
        "hba1c": r"hba1c\s*[:\-]?\s*(\d+\.?\d*)",
        "cholesterol": r"cholesterol.*?(\d+)",
        "triglycerides": r"triglycerides?\s*[:\-]?\s*(\d+)",
        "hdl": r"\bhdl\b.*?(\d+)",
        "ldl": r"\bldl\b.*?(\d+)",
        "vldl": r"\bvldl\b.*?(\d+\.?\d*)",
        "chol_hdl_ratio": r"total.*hdl.*?(\d+\.?\d*)",
        "ldl_hdl_ratio": r"ldl\/hdl.*?(\d+\.?\d*)",
        "creatinine": r"creatinine\s*[:\-]?\s*(\d+\.?\d*)",
        "urea": r"urea\s*[:\-]?\s*(\d+\.?\d*)",
        "hemoglobin": r"hemoglobin\s*[:\-]?\s*(\d+\.?\d*)",
        "platelets": r"platelet.*?(\d+)",
        "wbc": r"wbc.*?(\d+)",
        "rbc": r"rbc.*?(\d+\.?\d*)",
    }

    data = {}
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            data[key] = match.group(match.lastindex)

    bp_keywords = ["bp", "blood pressure", "b.p"]
    if any(keyword in text.lower() for keyword in bp_keywords):
        bp = re.search(r"(\d{2,3})\s*\/\s*(\d{2,3})", text)
        if bp:
            data["bp"] = f"{bp.group(1)}/{bp.group(2)}"

    return data


def generate_summary(text):
    values = extract_medical_values(text)
    summary = []

    labels = {
        "glucose": ("Fasting blood glucose recorded at ", " mg/dL."),
        "hba1c": ("HbA1c recorded at ", "%."),
        "cholesterol": ("Total cholesterol measured at ", " mg/dL."),
        "triglycerides": ("Triglycerides recorded at ", " mg/dL."),
        "hdl": ("HDL level recorded at ", " mg/dL."),
        "ldl": ("LDL cholesterol recorded at ", " mg/dL."),
        "vldl": ("VLDL measured at ", " mg/dL."),
        "chol_hdl_ratio": ("Total cholesterol to HDL ratio recorded at ", "."),
        "ldl_hdl_ratio": ("LDL to HDL ratio recorded at ", "."),
        "bp": ("Blood pressure recorded at ", "."),
        "creatinine": ("Creatinine level recorded at ", "."),
        "urea": ("Urea level recorded at ", "."),
        "hemoglobin": ("Hemoglobin recorded at ", "."),
        "platelets": ("Platelet count recorded at ", "."),
        "wbc": ("WBC count recorded at ", "."),
        "rbc": ("RBC count recorded at ", "."),
    }

    for key, (prefix, suffix) in labels.items():
        if key in values:
            summary.append(f"{prefix}{values[key]}{suffix}")

    if not summary:
        return ". ".join(text.split(".")[:2]).strip()
    return " ".join(summary)


@document_bp.route("/upload-report", methods=["POST"])
@jwt_required()
def upload_and_summarize():
    # Enforce a request-size limit (also configure MAX_CONTENT_LENGTH globally if desired).
    if request.content_length is not None and request.content_length > MAX_UPLOAD_BYTES:
        return jsonify({"error": "File exceeds the 10 MB upload limit"}), 413

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    uploaded_file = request.files["file"]
    original_name = uploaded_file.filename or ""

    if not original_name.strip():
        return jsonify({"error": "Empty filename"}), 400
    if not _allowed_extension(original_name):
        return jsonify({"error": "Unsupported file type. Upload PDF, PNG, JPG, or JPEG."}), 415

    safe_name = secure_filename(original_name)
    if not safe_name:
        return jsonify({"error": "Invalid filename"}), 400

    UPLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid.uuid4().hex}_{safe_name}"
    filepath = UPLOAD_FOLDER / stored_name

    try:
        uploaded_file.save(filepath)

        # Validate content, not only the extension.
        extension = Path(stored_name).suffix.lower()
        if extension == ".pdf":
            with fitz.open(filepath) as pdf:
                if pdf.is_encrypted:
                    return jsonify({"error": "Password-protected PDFs are not supported"}), 422
        else:
            with Image.open(filepath) as image:
                image.verify()

        raw_text, confidence = extract_text(str(filepath))
        cleaned = clean_text(raw_text)

        if not cleaned:
            if extension != ".pdf":
                return jsonify({
                    "error": "Image upload is accepted, but OCR is not implemented yet. Please upload a text-based PDF."
                }), 422
            return jsonify({
                "error": "No embedded text found. Scanned/image-only PDFs require OCR and are not supported yet."
            }), 422

        values = extract_medical_values(cleaned)
        summary = generate_summary(cleaned)

        # Preserve existing response keys; confidence is null because no OCR confidence is calculated.
        return jsonify({
            "file_id": stored_name,
            "confidence": confidence,
            "summary": summary,
            "raw_preview": cleaned[:500],
            "extracted_values": values
        }), 200

    except (fitz.FileDataError, UnidentifiedImageError, OSError, ValueError):
        logger.info("Rejected invalid report upload", exc_info=True)
        return jsonify({"error": "The uploaded file is invalid or could not be read"}), 422
    except Exception:
        logger.exception("Unexpected error while processing report upload")
        return jsonify({"error": "Report processing failed. Please try again."}), 500
    finally:
        # This endpoint only returns extracted text; don't retain uploaded medical files.
        try:
            filepath.unlink(missing_ok=True)
        except OSError:
            logger.warning("Could not remove temporary report upload: %s", filepath)
