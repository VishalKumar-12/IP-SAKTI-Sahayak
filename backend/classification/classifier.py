def classify_query(query):
    query_lower = query.lower()

    classification = {
        "intent": "general_ip_guidance",
        "ip_type": "unknown",
        "jurisdiction": "India",
        "product_type": "unknown",
        "checks": {
            "product_classification": False,
            "patent": False,
            "prior_art": False,
            "tkdl": False,
            "abs": False,
            "regulatory": False,
            "trademark": False,
            "design": False,
            "trade_secret": False,
            "international": False
        }
    }

    # ---------------------------------------------------------
    # PRODUCT / AYURVEDA
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "ayurvedic",
        "ayurveda",
        "ashwagandha",
        "shatavari",
        "herbal",
        "formulation",
        "ayush",
        "medicine",
        "drug",
        "product"
    ]):
        classification["product_type"] = "ayurvedic_formulation"

        classification["checks"]["product_classification"] = True
        classification["checks"]["regulatory"] = True

    # ---------------------------------------------------------
    # PATENT
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "patent",
        "patentable",
        "patentability",
        "invention",
        "inventive step",
        "novel",
        "novelty",
        "developed",
        "new formulation",
        "new invention",
        "new product"
    ]):
        classification["intent"] = "patent_guidance"
        classification["ip_type"] = "patent"

        classification["checks"]["patent"] = True
        classification["checks"]["prior_art"] = True

    # ---------------------------------------------------------
    # PRIOR ART / TRADITIONAL KNOWLEDGE
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "prior art",
        "prior-art",
        "traditional knowledge",
        "traditional",
        "classical text",
        "classical formulation",
        "known formulation",
        "existing formulation"
    ]):
        classification["checks"]["prior_art"] = True
        classification["checks"]["tkdl"] = True

    # ---------------------------------------------------------
    # TKDL
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "tkdl",
        "traditional knowledge digital library"
    ]):
        classification["intent"] = "tkdl_guidance"
        classification["ip_type"] = "traditional_knowledge"

        classification["checks"]["tkdl"] = True
        classification["checks"]["prior_art"] = True

    # ---------------------------------------------------------
    # ABS / BIODIVERSITY
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "abs",
        "access and benefit sharing",
        "access-and-benefit-sharing",
        "benefit sharing",
        "biological resource",
        "biological resources",
        "biodiversity",
        "biodiversity act",
        "nba"
    ]):
        classification["intent"] = "abs_guidance"
        classification["ip_type"] = "biodiversity"

        classification["checks"]["abs"] = True

    # ---------------------------------------------------------
    # REGULATORY
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "manufacture",
        "manufacturing",
        "sell",
        "selling",
        "market",
        "marketing",
        "license",
        "licence",
        "approval",
        "regulation",
        "regulatory",
        "compliance",
        "drug",
        "food",
        "cosmetic",
        "ayurveda-aahar"
    ]):
        classification["checks"]["regulatory"] = True

    # ---------------------------------------------------------
    # TRADEMARK
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "trademark",
        "trade mark",
        "brand name",
        "brand",
        "logo"
    ]):
        classification["intent"] = "trademark_guidance"
        classification["ip_type"] = "trademark"

        classification["checks"]["trademark"] = True

    # ---------------------------------------------------------
    # DESIGN
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "design",
        "packaging design",
        "product appearance"
    ]):
        classification["checks"]["design"] = True

    # ---------------------------------------------------------
    # TRADE SECRET
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "trade secret",
        "confidential",
        "secret formula",
        "secret process"
    ]):
        classification["checks"]["trade_secret"] = True

    # ---------------------------------------------------------
    # INTERNATIONAL
    # ---------------------------------------------------------
    if any(word in query_lower for word in [
        "international",
        "wipo",
        "pct",
        "trips",
        "madrid",
        "hague",
        "budapest",
        "foreign",
        "outside india",
        "export",
        "usa",
        "europe",
        "uk"
    ]):
        classification["jurisdiction"] = "International"
        classification["checks"]["international"] = True

    # ---------------------------------------------------------
    # AYURVEDIC FORMULATION DEFAULT ROUTING
    # ---------------------------------------------------------
    if classification["product_type"] == "ayurvedic_formulation":

        classification["checks"]["product_classification"] = True
        classification["checks"]["prior_art"] = True
        classification["checks"]["tkdl"] = True

    # ---------------------------------------------------------
    # CONFIDENCE
    # ---------------------------------------------------------
    active_checks = sum(
        classification["checks"].values()
    )

    if active_checks >= 4:
        confidence = 0.90
    elif active_checks >= 2:
        confidence = 0.85
    elif active_checks >= 1:
        confidence = 0.80
    else:
        confidence = 0.70

    return classification, confidence