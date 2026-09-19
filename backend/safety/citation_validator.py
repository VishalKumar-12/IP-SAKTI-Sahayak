import re


def validate_citations(answer, documents):

    valid_sources = set(
        range(1, len(documents) + 1)
    )

    pattern = r"\[\s*SOURCE\s+(\d+)\s*\]"

    cited_sources = re.findall(
        pattern,
        answer,
        re.IGNORECASE
    )

    valid_citations = []
    invalid_citations = []

    for source_number in cited_sources:

        number = int(source_number)

        if number in valid_sources:
            valid_citations.append(number)
        else:
            invalid_citations.append(number)

    # Citation exists only when at least
    # one valid source is cited.
    has_valid_citation = len(
        valid_citations
    ) > 0

    return {
        "valid": (
            has_valid_citation
            and len(invalid_citations) == 0
        ),
        "valid_citations": sorted(
            set(valid_citations)
        ),
        "invalid_citations": sorted(
            set(invalid_citations)
        )
    }