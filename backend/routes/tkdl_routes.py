from flask import Blueprint, request, jsonify
from urllib.parse import quote

from backend.rag.hybrid_search import hybrid_search
from backend.rag.reranker import rerank_documents
from backend.ai.llm import get_llm
from backend.safety.citation_validator import validate_citations
from backend.ai.confidence import calculate_confidence


tkdl_bp = Blueprint("tkdl", __name__)


@tkdl_bp.route("/tkdl", methods=["POST"])
def tkdl_search():

    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "success": False,
            "error": "Query is required"
        }), 400

    try:

        tkdl_query = f"""
{query}

Traditional Knowledge Digital Library (TKDL)
traditional knowledge
Ayurveda
Siddha
Unani
Yoga
Sowa Rigpa
prior art
patent examination
traditional knowledge protection
misappropriation
"""

        results = hybrid_search(
            tkdl_query,
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
                "sources": [],
                "confidence": 0.0,
                "disclaimer": (
                    "This is informational guidance, not legal advice. "
                    "Restricted TKDL records are not reproduced or exposed."
                )
            })

        reranked_results = rerank_documents(
            tkdl_query,
            results,
            top_k=5
        )

        context_parts = []
        citations = []

        for i, item in enumerate(reranked_results, start=1):

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

        prompt = f"""
You are IP-SAKTI Sahayak, an AI assistant for
Traditional Knowledge Digital Library (TKDL) guidance.

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
8. Explain TKDL as a tool that helps identify relevant
   traditional knowledge as prior-art information.
9. Do NOT say that TKDL directly checks whether a patent
   already exists.
10. Do NOT say that TKDL itself grants, rejects, or approves patents.
11. Do NOT claim that consulting TKDL guarantees patent approval
    or reduces the chance of patent rejection.
12. Do NOT recommend submitting a TKDL search report as a
    mandatory part of a patent application.
13. Do NOT mention NISCAIR unless the provided source specifically
    supports its current role.
14. Do NOT claim that a specific Neem formulation, dosage,
    treatment, or use exists in TKDL unless the provided source
    explicitly supports it.
15. Do NOT reproduce restricted TKDL records or confidential
    database contents.
16. Do NOT invent laws, sections, dates, procedures,
    patent outcomes, or requirements.
17. Clearly distinguish between:
    - an existing patent
    - traditional knowledge
    - prior-art information
18. If the sources are insufficient, say:
"I could not find sufficient information in the available sources."
19. Do not give legal advice.

Answer format:

Simple Answer:
[direct answer]

Key Points:
- [point] [SOURCE X]
- [point] [SOURCE X]
- [point] [SOURCE X]

Note:
TKDL is not a substitute for a complete patent or prior-art search.
This is informational guidance, not legal advice.
"""

        llm = get_llm()

        response = llm.invoke(prompt)

        answer = response.content

        documents = [
            document
            for document, score in reranked_results
        ]

        validation = validate_citations(
            answer,
            documents
        )

        confidence = calculate_confidence(
            reranked_results,
            citation_valid=validation["valid"]
        )

        sources = []

        for citation in citations:

            source = citation.get(
                "source",
                "Unknown source"
            )

            page = citation.get(
                "page",
                None
            )

            sources.append({
                "title": source,
                "page": page,
                "url": (
                    "/api/source"
                    "?file="
                    + quote(source.replace("\\", "/"))
                    + "&page="
                    + quote(str(page))
                )
            })

        return jsonify({
            "success": True,
            "query": query,
            "answer": answer,
            "sources": sources,
            "confidence": confidence,
            "disclaimer": (
                "This is informational guidance, not legal advice. "
                "Restricted TKDL records are not reproduced or exposed."
            )
        })

    except Exception as error:

        print("TKDL Error:", error)

        return jsonify({
            "success": False,
            "error": "TKDL processing failed"
        }), 500