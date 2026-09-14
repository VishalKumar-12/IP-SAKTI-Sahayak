from flask import Blueprint, request, jsonify
import time
import json
from urllib.parse import quote

from flask_jwt_extended import jwt_required, get_jwt_identity

from backend.extensions import db
from backend.models import Conversation, Message
from backend.rag.hybrid_search import hybrid_search
from backend.rag.reranker import rerank_documents
from backend.ai.answer_generator import generate_answer
from backend.safety.citation_validator import validate_citations
from backend.ai.confidence import calculate_confidence
from backend.classification.classifier import classify_query


chat_bp = Blueprint("chat", __name__)


def _get_or_create_conversation(
    user_id,
    conversation_id,
    first_message
):
    conversation = None

    if conversation_id:
        conversation = Conversation.query.filter_by(
            id=conversation_id,
            user_id=user_id
        ).first()

    if not conversation:
        title = first_message[:60] + (
            "..." if len(first_message) > 60 else ""
        )

        conversation = Conversation(
            user_id=user_id,
            title=title
        )

        db.session.add(conversation)
        db.session.commit()

    return conversation


def _save_assistant_message(
    conversation_id,
    answer,
    citations=None,
    confidence=None,
    classification=None,
    language=None
):
    conversation = Conversation.query.filter_by(
        id=conversation_id
    ).first()

    if not conversation:
        raise ValueError("Conversation not found")

    assistant_message = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=answer,
        citations=citations or [],
        confidence=confidence,
        classification=json.dumps(
            classification or {}
        ),
        language=language
    )

    db.session.add(assistant_message)

    conversation.updated_at = db.func.now()

    db.session.commit()

    print(
        "ASSISTANT MESSAGE SAVED:",
        assistant_message.id,
        assistant_message.content[:100]
    )


@chat_bp.route("/chat", methods=["POST"])
@jwt_required()
def chat():

    user_id = get_jwt_identity()

    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()
    language = data.get("language", "en")
    conversation_id = data.get("conversation_id")

    if not message:
        return jsonify({
            "success": False,
            "error": "Message is required"
        }), 400

    conversation = _get_or_create_conversation(
        user_id,
        conversation_id,
        message
    )

    # Save user message
    db.session.add(
        Message(
            conversation_id=conversation.id,
            role="user",
            content=message,
            language=language
        )
    )

    conversation.updated_at = db.func.now()

    db.session.commit()

    try:

        start = time.time()

        # 1. CLASSIFICATION
        classification, classification_confidence = classify_query(
            message
        )

        print(
            "Classification:",
            classification
        )

        # 2. HYBRID RETRIEVAL
        results = hybrid_search(
            message,
            k=8,
            min_score=0.65,
            classification=classification
        )

        print(
            "Hybrid Search:",
            round(time.time() - start, 2),
            "sec"
        )

        if not results:

            no_info_answer = (
                "I could not find sufficient information "
                "in the available sources."
            )

            _save_assistant_message(
                conversation.id,
                no_info_answer,
                confidence=0.0,
                classification=classification,
                language=language
            )

            return jsonify({
                "success": True,
                "conversation_id": conversation.id,
                "answer": no_info_answer,
                "citations": [],
                "confidence": 0.0,
                "classification": classification,
                "classification_confidence": (
                    classification_confidence
                ),
                "language": language
            })

        # 3. RERANKING
        reranked_results = rerank_documents(
            message,
            results,
            top_k=2
        )

        print(
            "Reranker:",
            round(time.time() - start, 2),
            "sec"
        )

        if not reranked_results:

            no_info_answer = (
                "I could not find sufficient information "
                "in the available sources."
            )

            _save_assistant_message(
                conversation.id,
                no_info_answer,
                confidence=0.0,
                classification=classification,
                language=language
            )

            return jsonify({
                "success": True,
                "conversation_id": conversation.id,
                "answer": no_info_answer,
                "citations": [],
                "confidence": 0.0,
                "classification": classification,
                "classification_confidence": (
                    classification_confidence
                ),
                "language": language
            })

        # 4. GENERATE ANSWER
        answer, source_citations = generate_answer(
            message,
            reranked_results,
            classification,
            language
        )

        print(
            "LLM:",
            round(time.time() - start, 2),
            "sec"
        )

        # 5. VALIDATE CITATIONS
        documents = [
            document
            for document, score in reranked_results
        ]

        validation = validate_citations(
            answer,
            documents
        )

        # 6. BUILD CITATIONS
        citations = []

        for number in validation["valid_citations"]:

            document = documents[number - 1]

            source = document.metadata.get(
                "source",
                "Unknown source"
            )

            page = document.metadata.get(
                "page",
                "Unknown page"
            )

            citations.append({
                "source": source,
                "page": page,
                "url": (
                    "/api/source?"
                    "file="
                    + quote(str(source))
                    + "&page="
                    + quote(str(page))
                )
            })

        # 7. CONFIDENCE
        confidence = calculate_confidence(
            reranked_results,
            citation_valid=validation["valid"]
        )

        print(
            "TOTAL:",
            round(time.time() - start, 2),
            "sec"
        )

        # 8. SAVE ASSISTANT MESSAGE
        _save_assistant_message(
            conversation.id,
            answer,
            citations=citations,
            confidence=confidence,
            classification=classification,
            language=language
        )

        # 9. RESPONSE
        return jsonify({
            "success": True,
            "conversation_id": conversation.id,
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "classification": classification,
            "classification_confidence": (
                classification_confidence
            ),
            "language": language
        })

    except Exception as error:

        print(
            "Chat Error:",
            error
        )

        db.session.rollback()

        return jsonify({
            "success": False,
            "conversation_id": conversation.id,
            "error": "Unable to process the question."
        }), 500