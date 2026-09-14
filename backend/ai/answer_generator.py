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


def generate_answer(query, documents, classification=None, language="en"):
    """
    Generate a source-grounded answer using retrieved documents.
    """

    if not documents:
        return (
            "I could not find sufficient information in the available sources.",
            []
        )

    # ---------------------------------------------------------
    # Classification / routing
    # ---------------------------------------------------------
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

    # ---------------------------------------------------------
    # Resolve target response language
    # ---------------------------------------------------------
    language_name = LANGUAGE_NAMES.get(language, "English")

    # ---------------------------------------------------------
    # Prepare limited context
    # ---------------------------------------------------------
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

        # Limit document content to reduce LLM tokens
        if len(content) > MAX_DOCUMENT_CHARS:
            content = content[:MAX_DOCUMENT_CHARS] + "..."

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

    # ---------------------------------------------------------
    # Shorter prompt
    # ---------------------------------------------------------
    prompt = f"""
You are IP-SAKTI Sahayak.

Answer the user's question using ONLY the provided sources.

Relevant case checks:
{relevant_checks_text}

Respond entirely in {language_name}. Translate all headings, labels, and
content into {language_name} as well — do not answer in English unless
{language_name} is English.

IMPORTANT:
- Routing checks are NOT legal conclusions.
- Do not assume a new formulation is a new drug.
- Do not assume a product is a phytopharmaceutical.
- Do not invent laws, sections, authorities, procedures, fees,
  clinical requirements, or eligibility conditions.
- Every factual claim must be supported by the sources.
- Use [SOURCE X] immediately after supported statements.
- If information is insufficient, say:
  "I could not find sufficient information in the available sources."
- Do not turn a possible requirement into a confirmed requirement.
- TKDL should be described only from the provided sources.
- ABS applicability should be presented as something to check,
  unless the sources establish that it applies.

For a business/product case use:

### Case Analysis

### Relevant Checks

### What You Should Check

### Recommended Next Steps

Keep the answer concise, practical and professional.

User question:
{query}

Available sources:
{context}

Provide the final answer.
"""

    # ---------------------------------------------------------
    # Generate answer
    # ---------------------------------------------------------
    llm = get_llm()

    response = llm.invoke(prompt)

    return response.content.strip(), citations



















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