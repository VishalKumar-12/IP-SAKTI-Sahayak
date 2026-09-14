from flask import Blueprint, request, jsonify

from backend.rag.hybrid_search import hybrid_search
from backend.rag.reranker import rerank_documents
from backend.ai.llm import get_llm
from backend.safety.citation_validator import validate_citations
from backend.ai.confidence import calculate_confidence


abs_bp = Blueprint("abs", __name__)


@abs_bp.route("/abs", methods=["POST"])
def check_abs():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "error": "Query is required"
        }), 400

    try:

        abs_query = f"""
{query}

Access and Benefit Sharing (ABS)
biodiversity
biological resources
National Biodiversity Authority (NBA)
benefit sharing
Biological Diversity Act
access to biological resources
traditional knowledge
medicinal plants
"""

        results = hybrid_search(
            abs_query,
            k=8,
            min_score=0.60
        )

        if not results:
            return jsonify({
                "success": True,
                "query": query,
                "answer": (
                    "I could not find sufficient information "
                    "in the available sources."
                ),
                "citations": [],
                "confidence": 0.0,
                "disclaimer": (
                    "This is informational guidance, not legal advice."
                )
            })

        documents = rerank_documents(
            abs_query,
            results,
            top_k=5
        )

        # ==============================
        # BUILD SOURCE CONTEXT
        # ==============================

        context_parts = []
        citations = []

        for i, item in enumerate(documents, start=1):

            document = item[0]

            source = document.metadata.get(
                "source",
                "Unknown source"
            )

            page = document.metadata.get(
                "page",
                "Unknown page"
            )

            context_parts.append(
                f"[SOURCE {i}]\n"
                f"Source: {source}\n"
                f"Page: {page}\n"
                f"Content:\n{document.page_content}"
            )

            citations.append({
                "source": source,
                "page": page
            })

        context = "\n\n".join(context_parts)

        # ==============================
        # ABS-SPECIFIC LLM PROMPT
        # ==============================

        prompt = f"""
You are IP-SAKTI Sahayak, an AI assistant for
Access and Benefit Sharing (ABS) guidance.

Question:
{query}

Available Sources:
{context}

Rules:

1. Answer ONLY using the provided sources.
2. Use simple and clear English.
3. Start with "Simple Answer:".
4. Then provide "Key Points:".
5. Give 3-4 short bullet points.
6. Every factual statement must include [SOURCE X].
7. Use only valid source numbers.
8. Explain ABS in simple language when relevant.
9. Explain the role of the National Biodiversity Authority (NBA)
   only when supported by the sources.
10. Do NOT automatically say that approval or permission is required
    unless the provided sources specifically support it.
11. Do NOT claim that every use of a medicinal plant requires ABS
    approval.
12. Do NOT invent benefit-sharing percentages, fees, forms,
    permissions, procedures, deadlines, or legal requirements.
13. Do NOT invent laws, sections, dates, authorities, or penalties.
14. Clearly distinguish between:
    - biological resources
    - traditional knowledge
    - access
    - benefit sharing
15. If the sources do not provide enough information for a
    specific ABS decision, say:
"I could not find sufficient information in the available sources."
16. Do not give legal advice.

Answer format:

Simple Answer:
[direct answer]

Key Points:
- [point] [SOURCE X]
- [point] [SOURCE X]
- [point] [SOURCE X]

Note:
This is informational guidance, not legal advice.
"""

        llm = get_llm()

        response = llm.invoke(prompt)

        answer = response.content

        # ==============================
        # CITATION VALIDATION
        # ==============================

        validation = validate_citations(
            answer,
            [document for document, _ in documents]
        )

        # ==============================
        # CONFIDENCE
        # ==============================

        confidence = calculate_confidence(
            documents,
            citation_valid=validation["valid"]
        )

        # ==============================
        # RESPONSE
        # ==============================

        return jsonify({
            "success": True,
            "query": query,
            "answer": answer,
            "citations": citations,
            "confidence": confidence,
            "disclaimer": (
                "This is informational guidance, not legal advice."
            )
        })

    except Exception as error:

        print("ABS Error:", error)

        return jsonify({
            "success": False,
            "error": "ABS processing failed"
        }), 500