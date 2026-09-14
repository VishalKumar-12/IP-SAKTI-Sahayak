def should_abstain(results, min_score=0.65):

    if not results:
        return True

    scores = [score for _, score in results]

    best_score = max(scores)

    return best_score < min_score