def calculate_confidence(
    results,
    citation_valid=True
):
    if not results:
        return 0.0

    result_count = len(results)

    # More relevant documents = higher evidence strength
    evidence_score = min(
        result_count / 5,
        1.0
    )

    # Rank strength
    rank_weights = []

    for index in range(result_count):
        weight = 1 / (index + 1)
        rank_weights.append(weight)

    rank_score = (
        sum(rank_weights) /
        len(rank_weights)
    )

    # Reranker score
    top_score = float(results[0][1])

    # CrossEncoder scores are not probabilities.
    # Convert the top score into a bounded strength value.
    if top_score >= 4:
        top_strength = 1.0
    elif top_score >= 2:
        top_strength = 0.85
    elif top_score >= 0:
        top_strength = 0.65
    elif top_score >= -2:
        top_strength = 0.40
    else:
        top_strength = 0.20

    # Citation validation
    citation_score = (
        1.0 if citation_valid else 0.0
    )

    confidence = (
        (top_strength * 0.40)
        + (rank_score * 0.20)
        + (evidence_score * 0.20)
        + (citation_score * 0.20)
    )

    confidence = max(
        0.0,
        min(1.0, confidence)
    )

    return round(
        confidence,
        2
    )