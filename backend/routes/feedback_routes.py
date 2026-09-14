from flask import Blueprint, request, jsonify

feedback_bp = Blueprint("feedback", __name__)


@feedback_bp.route("/feedback", methods=["POST"])
def submit_feedback():
    data = request.get_json(silent=True) or {}

    feedback = data.get("feedback", "").strip()

    if not feedback:
        return jsonify({
            "error": "Feedback is required"
        }), 400

    return jsonify({
        "success": True,
        "message": "Thank you for your feedback."
    })