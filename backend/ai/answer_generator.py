from backend.ai.llm import get_llm


MAX_DOCUMENT_CHARS = 1800

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "as": "Assamese",
    "bn": "Bengali",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ks": "Kashmiri",
    "kok": "Konkani",
    "mai": "Maithili",
    "ml": "Malayalam",
    "mr": "Marathi",
    "ne": "Nepali",
    "or": "Odia",
    "pa": "Punjabi",
    "sa": "Sanskrit",
    "sd": "Sindhi",
    "ta": "Tamil",
    "te": "Telugu",
    "ur": "Urdu",
    "bodo": "Bodo",
    "doi": "Dogri",
    "mni": "Manipuri",
    "bho": "Bhojpuri",
    "mag": "Magahi"
}


def generate_answer(
    query,
    documents,
    classification=None,
    language="en",
    jurisdiction="india"
):
    """
    Generate a source-grounded answer using retrieved documents.
    """

    if not documents:
        return (
            "I could not find sufficient information in the available sources.",
            []
        )

    # ------------------------------------------------------------------
    # Classification / routing
    # ------------------------------------------------------------------

    checks = {}

    if classification:
        checks = classification.get("checks", {})

    check_names = {
        "product_classification": "Product Classification",
        "patent": "Patentability",
        "prior_art": "Prior Art",
        "tkdl": "TKDL / Traditional Knowledge",
        "abs": "ABS / Biodiversity",
        "regulatory": "Regulatory Requirements",
        "trademark": "Trademark",
        "design": "Design Protection",
        "trade_secret": "Trade Secret",
        "international": "International IPR"
    }

    relevant_checks = [
        name
        for key, name in check_names.items()
        if checks.get(key, False)
    ]

    relevant_checks_text = ", ".join(relevant_checks)

    # ------------------------------------------------------------------
    # Response language
    # ------------------------------------------------------------------

    language_name = LANGUAGE_NAMES.get(
        language,
        "English"
    )

    # ------------------------------------------------------------------
    # Prepare retrieved context
    # ------------------------------------------------------------------

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

        content = document.page_content.strip()

        if len(content) > MAX_DOCUMENT_CHARS:
            content = (
                content[:MAX_DOCUMENT_CHARS]
                + "..."
            )

        context_parts.append(
            f"""[SOURCE {i}]
Source: {source}
Page: {page}
Content:
{content}"""
        )

        citations.append({
            "source": source,
            "page": page
        })

    context = "\n\n".join(context_parts)

    # ------------------------------------------------------------------
    # Prompt
    # ------------------------------------------------------------------

    prompt = f"""
You are IP-SAKTI Sahayak.

You are a source-grounded AI assistant for Intellectual Property,
Ayurveda, traditional knowledge, biodiversity and regulatory guidance.

Answer the user's question using ONLY the provided sources.

Jurisdiction:
{jurisdiction}

Relevant case checks:
{relevant_checks_text}

Response language:
{language_name}

IMPORTANT SOURCE-GROUNDING RULES:

1. Every factual legal or regulatory claim MUST be supported by the
   provided sources.

2. Use [SOURCE X] immediately after the statement supported by that
   source.

3. Do NOT invent:
   - laws
   - sections
   - rules
   - authorities
   - procedures
   - fees
   - eligibility requirements
   - patent criteria
   - regulatory requirements
   - filing requirements

4. Do NOT use general knowledge to fill missing information.

5. If the provided sources do not contain enough information to answer
   an important part of the question, clearly say:

   "I could not find sufficient information in the available sources."

6. Do NOT convert a manufacturing, quality-control, pharmacopoeial or
   regulatory requirement into a patentability requirement unless the
   provided source explicitly makes that connection.

7. If the user asks about PATENTABILITY, keep these concepts separate:

   A. Patentability requirements
   B. Prior-art / traditional-knowledge checks
   C. Regulatory or manufacturing requirements

8. If the retrieved sources discuss only manufacturing or regulatory
   requirements but do not establish the patentability requirements,
   explicitly state that the retrieved sources are insufficient for the
   patentability part of the question.

9. Do NOT claim that a formulation is patentable or not patentable
   unless the provided sources support that conclusion.

10. Do NOT assume that:
    - a new formulation is a new drug
    - a product is a phytopharmaceutical
    - traditional knowledge automatically makes an invention
      unpatentable
    - ABS automatically applies

11. TKDL and traditional knowledge must only be described using the
    provided sources.

12. ABS applicability must be presented as something to check unless
    the provided sources explicitly establish applicability.

13. Do not mix Indian and international law unless the question or
    provided sources explicitly require comparison.

14. Jurisdiction is:
    {jurisdiction}

15. Do not treat routing checks as legal conclusions.

PATENT-SPECIFIC RULE:

If the user's question is about patent requirements, patentability,
novelty, inventive step, industrial applicability, prior art, or
traditional knowledge:

- Answer only what the retrieved patent-related sources establish.
- Clearly distinguish patentability from regulatory compliance.
- If patent-law evidence is missing, say so instead of using unrelated
  Ayurveda manufacturing information as a substitute.
- Do not present pharmacopoeial standards, manufacturing records,
  microbial testing, or quality-control requirements as patentability
  criteria unless the source explicitly connects them to patentability.

RESPONSE STRUCTURE:

For a business or product case, use:

### Case Analysis

### Patentability Requirements

### Relevant Checks

### Regulatory / Compliance Considerations

### Recommended Next Steps

For a simple factual question, use a shorter structure.

LANGUAGE RULE:

Respond entirely in {language_name}.

Translate headings, labels and content into {language_name}.

Do not answer in English unless {language_name} is English.

CITATION RULE:

Use citations exactly like:

[ SOURCE 1 ]

Do not create fake source numbers.

Do not cite a source for information that is not present in that source.

USER QUESTION:

{query}

AVAILABLE SOURCES:

{context}

Now provide a concise, practical and source-grounded answer.
"""

    # ------------------------------------------------------------------
    # Generate answer
    # ------------------------------------------------------------------

    llm = get_llm()

    response = llm.invoke(prompt)

    answer = response.content.strip()

    return answer, citations











# from backend.ai.llm import get_llm


# def generate_answer(query, documents):
#     if not documents:
#         return (
#             "I could not find sufficient information in the available sources.",
#             []
#         )

#     context_parts = []
#     citations = []

#     for i, item in enumerate(documents, start=1):
#         document = item[0]

#         source = document.metadata.get("source", "Unknown source")
#         page = document.metadata.get("page", "Unknown page")

#         context_parts.append(
#             f"[SOURCE {i}]\n"
#             f"Source: {source}\n"
#             f"Page: {page}\n"
#             f"Content:\n{document.page_content}"
#         )

#         citations.append({
#             "source": source,
#             "page": page
#         })

#     context = "\n\n".join(context_parts)

#     prompt = f"""
# You are IP-SAKTI Sahayak, an AI assistant for
# Ayurveda Intellectual Property and regulatory guidance.

# Answer ONLY using the provided sources.

# Rules:
# 1. Do not invent laws, sections, rules, dates, or facts.
# 2. If the sources do not contain enough information, say:
# "I could not find sufficient information in the available sources."
# 3. When making a factual statement, mention the source number like [SOURCE 1].
# 4. Do not create fake citations.
# 5. Keep the answer clear and concise.

# Question:
# {query}

# Available Sources:
# {context}

# Answer:
# """

#     llm = get_llm()
#     response = llm.invoke(prompt)

#     return response.content, citations