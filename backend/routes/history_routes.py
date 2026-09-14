from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import Conversation, Message


history_bp = Blueprint("history", __name__)


# ============================================================
# Get all conversations for the logged-in user
# ============================================================

@history_bp.route("/chat/conversations", methods=["GET"])
@jwt_required()
def list_conversations():

    user_id = get_jwt_identity()

    conversations = (
        Conversation.query
        .filter_by(user_id=user_id)
        .order_by(Conversation.updated_at.desc())
        .all()
    )

    return jsonify({
        "success": True,
        "conversations": [
            conversation.to_dict()
            for conversation in conversations
        ]
    }), 200


# ============================================================
# Get complete messages of one conversation
# ============================================================

@history_bp.route(
    "/chat/conversations/<conversation_id>",
    methods=["GET"]
)
@jwt_required()
def get_conversation(conversation_id):

    user_id = get_jwt_identity()

    conversation = Conversation.query.filter_by(
        id=conversation_id,
        user_id=user_id
    ).first()

    if not conversation:
        return jsonify({
            "success": False,
            "error": "Conversation not found."
        }), 404

    return jsonify({
        "success": True,
        "conversation": conversation.to_dict(
            include_messages=True
        )
    }), 200


# ============================================================
# Delete one conversation
# ============================================================

@history_bp.route(
    "/chat/conversations/<conversation_id>",
    methods=["DELETE"]
)
@jwt_required()
def delete_conversation(conversation_id):

    user_id = get_jwt_identity()

    try:

        # Only allow the logged-in user
        # to delete their own conversation
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

        if not conversation:
            return jsonify({
                "success": False,
                "error": "Conversation not found."
            }), 404

        # Delete all messages belonging
        # to this conversation first
        Message.query.filter_by(
            conversation_id=conversation.id
        ).delete(
            synchronize_session=False
        )

        # Delete the conversation
        db.session.delete(conversation)

        # Save changes
        db.session.commit()

        return jsonify({
            "success": True,
            "message": "Conversation deleted successfully."
        }), 200

    except Exception as error:

        db.session.rollback()

        print("Delete conversation error:", error)

        return jsonify({
            "success": False,
            "error": "Unable to delete conversation."
        }), 500