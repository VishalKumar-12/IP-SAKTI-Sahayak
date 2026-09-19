import os
import time

from backend.rag.bm25_index import (
    load_bm25_index,
    tokenize
)

from backend.rag.retriever import retrieve_with_scores


VECTOR_WEIGHT = 0.70
KEYWORD_WEIGHT = 0.30

VECTOR_K = 8
KEYWORD_K = 8

RRF_K = 60


# ============================================================
# BM25 Configuration
# ============================================================

bm25 = None
all_documents = []

ENABLE_BM25 = (
    os.getenv("ENABLE_BM25", "true").lower() == "true"
)


def get_document_key(document):

    source = document.metadata.get("source", "")
    page = document.metadata.get("page", "")

    content = " ".join(
        document.page_content.split()
    ).lower()

    return (
        source,
        page,
        content[:500]
    )


def keyword_search(
    query,
    bm25,
    documents,
    k=KEYWORD_K
):

    query_tokens = tokenize(query)

    scores = bm25.get_scores(
        query_tokens
    )

    results = []

    for document, score in zip(
        documents,
        scores
    ):

        results.append(
            (document, float(score))
        )

    results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    return results[:k]


def rrf_score(rank, weight):

    return weight / (RRF_K + rank)


def diversify_results(
    results,
    k=8,
    max_per_source=2
):

    selected = []
    source_counts = {}

    for document, score in results:

        source = document.metadata.get(
            "source",
            "unknown"
        )

        count = source_counts.get(
            source,
            0
        )

        if count >= max_per_source:
            continue

        selected.append(
            (document, score)
        )

        source_counts[source] = count + 1

        if len(selected) >= k:
            break

    return selected


def hybrid_search(
    query,
    k=8,
    min_score=0.65,
    classification=None,
    jurisdiction="india"
):

    global bm25, all_documents

    start = time.time()

    # ---------------------------------------------------------
    # Add classifier routing terms
    # ---------------------------------------------------------

    search_query = query

    if classification:

        checks = classification.get(
            "checks",
            {}
        )

        routing_terms = []

        # Product classification
        if checks.get("product_classification"):
            routing_terms.append(
                "Ayurveda Ayurvedic formulation "
                "product classification AYUSH"
            )

        # Patent
        if checks.get("patent"):
            routing_terms.append(
                "patent patentability "
                "Patents Act 1970 "
                "novelty "
                "inventive step "
                "industrial applicability "
                "patent application "
                "Section 3 "
                "Section 4"
            )

        # Prior art
        if checks.get("prior_art"):
            routing_terms.append(
                "prior art "
                "novelty "
                "existing formulation "
                "known formulation "
                "traditional knowledge"
            )

        # TKDL
        if checks.get("tkdl"):
            routing_terms.append(
                "TKDL "
                "Traditional Knowledge Digital Library "
                "traditional knowledge "
                "Ayurvedic classical text "
                "prior art"
            )

        # ABS
        if checks.get("abs"):
            routing_terms.append(
                "biodiversity "
                "access and benefit sharing "
                "ABS "
                "biological resources"
            )

        # Regulatory
        if checks.get("regulatory"):
            routing_terms.append(
                "Ayurvedic regulatory requirements "
                "AYUSH "
                "Drugs and Cosmetics Act "
                "Drugs and Cosmetics Rules "
                "manufacturing "
                "quality standards"
            )

        # Trademark
        if checks.get("trademark"):
            routing_terms.append(
                "trademark "
                "Trade Marks Act "
                "brand name"
            )

        # Design
        if checks.get("design"):
            routing_terms.append(
                "design protection "
                "Designs Act "
                "industrial design"
            )

        # Trade secret
        if checks.get("trade_secret"):
            routing_terms.append(
                "trade secret "
                "confidential information "
                "confidential formula"
            )

        # International
        if checks.get("international"):
            routing_terms.append(
                "international IP "
                "WIPO "
                "PCT "
                "TRIPS "
                "Madrid"
            )

        # Jurisdiction
        jurisdiction = (
            jurisdiction
            .lower()
            .strip()
        )

        if jurisdiction == "india":

            routing_terms.append(
                "India "
                "Indian law "
                "IP India "
                "Indian Patents Act "
                "AYUSH"
            )

        elif jurisdiction == "international":

            routing_terms.append(
                "international "
                "WIPO "
                "PCT "
                "TRIPS "
                "Madrid"
            )

        # Final search query
        if routing_terms:

            search_query = (
                query
                + " "
                + " ".join(routing_terms)
            )

    print(
        "Search Query:",
        search_query
    )

    # ---------------------------------------------------------
    # Vector Search
    # ---------------------------------------------------------

    vector_results = retrieve_with_scores(
        search_query,
        k=VECTOR_K,
        min_score=min_score
    )

    print(
        "Vector Search:",
        round(time.time() - start, 2),
        "sec"
    )

    # ---------------------------------------------------------
    # BM25 Search
    # ---------------------------------------------------------

    if ENABLE_BM25:

        # Load BM25 only when first needed
        if bm25 is None:

            print("Loading BM25 index...")

            bm25, all_documents = (
                load_bm25_index()
            )

            print(
                f"BM25 loaded: {len(all_documents)} documents"
            )

        keyword_start = time.time()

        keyword_results = keyword_search(
            search_query,
            bm25,
            all_documents,
            k=KEYWORD_K
        )

        print(
            "BM25 Search:",
            round(
                time.time() - keyword_start,
                2
            ),
            "sec"
        )

    else:

        print(
            "BM25 DISABLED - USING VECTOR SEARCH ONLY"
        )

        keyword_results = []

    # ---------------------------------------------------------
    # No results
    # ---------------------------------------------------------

    if not vector_results and not keyword_results:
        return []

    # ---------------------------------------------------------
    # Vector ranks
    # ---------------------------------------------------------

    vector_ranks = {}

    for rank, (
        document,
        score
    ) in enumerate(
        vector_results,
        start=1
    ):

        key = get_document_key(
            document
        )

        vector_ranks[key] = (
            document,
            rank,
            score
        )

    # ---------------------------------------------------------
    # Keyword ranks
    # ---------------------------------------------------------

    keyword_ranks = {}

    for rank, (
        document,
        score
    ) in enumerate(
        keyword_results,
        start=1
    ):

        key = get_document_key(
            document
        )

        keyword_ranks[key] = (
            document,
            rank,
            score
        )

    # ---------------------------------------------------------
    # Combine using RRF
    # ---------------------------------------------------------

    all_keys = (
        set(vector_ranks.keys())
        .union(
            keyword_ranks.keys()
        )
    )

    final_results = []

    for key in all_keys:

        document = None
        hybrid_score = 0.0

        if key in vector_ranks:

            document = vector_ranks[key][0]
            rank = vector_ranks[key][1]

            hybrid_score += rrf_score(
                rank,
                VECTOR_WEIGHT
            )

        if key in keyword_ranks:

            document = keyword_ranks[key][0]
            rank = keyword_ranks[key][1]

            hybrid_score += rrf_score(
                rank,
                KEYWORD_WEIGHT
            )

        final_results.append(
            (
                document,
                hybrid_score
            )
        )

    # ---------------------------------------------------------
    # Sort
    # ---------------------------------------------------------

    final_results.sort(
        key=lambda item: item[1],
        reverse=True
    )

    # ---------------------------------------------------------
    # Diversify sources
    # ---------------------------------------------------------

    result = diversify_results(
        final_results,
        k=k,
        max_per_source=2
    )

    print(
        "Hybrid Search:",
        round(
            time.time() - start,
            2
        ),
        "sec"
    )

    return result