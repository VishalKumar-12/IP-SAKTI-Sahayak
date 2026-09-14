from flask import Blueprint, request, send_file, jsonify
from pathlib import Path

source_bp = Blueprint("source", __name__)

DATA_FOLDER = Path("data").resolve()


@source_bp.route("/source", methods=["GET"])
def source():

    filename = request.args.get("file", "").strip()

    if not filename:
        return jsonify({
            "success": False,
            "error": "File is required"
        }), 400

    # Get only the PDF filename
    filename = Path(filename.replace("\\", "/")).name

    if not filename.lower().endswith(".pdf"):
        return jsonify({
            "success": False,
            "error": "Only PDF files are allowed"
        }), 400

    # Search inside data/ and all subfolders
    matches = list(DATA_FOLDER.rglob(filename))

    if not matches:
        return jsonify({
            "success": False,
            "error": "PDF not found"
        }), 404

    pdf_path = matches[0].resolve()

    # Security check
    try:
        pdf_path.relative_to(DATA_FOLDER)
    except ValueError:
        return jsonify({
            "success": False,
            "error": "Invalid file path"
        }), 403

    return send_file(
        pdf_path,
        mimetype="application/pdf",
        as_attachment=False
    )