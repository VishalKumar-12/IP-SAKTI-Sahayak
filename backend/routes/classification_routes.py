from flask import Blueprint, request, jsonify

classification_bp = Blueprint("classification", __name__)


def classify_query(query):
    text = query.lower()

    # IP type
    if any(word in text for word in ["patent", "patentable", "invention", "prior art"]):
        ip_type = "patent"
    elif any(word in text for word in ["trademark", "brand", "logo"]):
        ip_type = "trademark"
    elif any(word in text for word in ["copyright", "literary", "artistic work"]):
        ip_type = "copyright"
    elif any(word in text for word in ["geographical indication", "gi tag", "gi"]):
        ip_type = "geographical_indication"
    elif any(word in text for word in ["design", "industrial design"]):
        ip_type = "design"
    elif any(word in text for word in ["plant variety", "plant variety protection"]):
        ip_type = "plant_variety"
    elif any(word in text for word in ["biodiversity", "abs", "access and benefit sharing"]):
        ip_type = "biodiversity_abs"
    elif any(word in text for word in ["traditional knowledge", "tkdl"]):
        ip_type = "traditional_knowledge"
    else:
        ip_type = "unknown"

    # Product type
    if any(word in text for word in [
        "ayurvedic formulation", "formulation", "medicine",
        "drug", "ayurvedic drug"
    ]):
        product_type = "ayurvedic_formulation"
    elif any(word in text for word in [
        "ashwagandha", "neem", "turmeric", "plant", "herb",
        "medicinal plant"
    ]):
        product_type = "medicinal_plant"
    elif any(word in text for word in ["food", "nutraceutical"]):
        product_type = "food"
    elif "cosmetic" in text:
        product_type = "cosmetic"
    else:
        product_type = "unknown"

    # Intent
    if any(word in text for word in [
        "can i patent", "patent", "patentable", "how to patent",
        "patent process", "patent application"
    ]):
        intent = "patent_guidance"
    elif any(word in text for word in [
        "register trademark", "trademark registration", "trademark"
    ]):
        intent = "trademark_guidance"
    elif any(word in text for word in [
        "copyright", "copyright registration"
    ]):
        intent = "copyright_guidance"
    elif any(word in text for word in [
        "abs", "biodiversity", "benefit sharing"
    ]):
        intent = "biodiversity_abs_guidance"
    elif any(word in text for word in [
        "tkdl", "traditional knowledge"
    ]):
        intent = "traditional_knowledge_guidance"
    elif any(word in text for word in [
        "gi tag", "geographical indication"
    ]):
        intent = "gi_guidance"
    else:
        intent = "general_ip_guidance"

    # Jurisdiction
    if any(word in text for word in [
        "india", "indian", "indian law", "ip india"
    ]):
        jurisdiction = "India"
    elif any(word in text for word in [
        "international", "wipo", "pct", "madrid", "trips"
    ]):
        jurisdiction = "International"
    else:
        jurisdiction = "India"

    # Confidence
    detected = sum([
        ip_type != "unknown",
        product_type != "unknown",
        intent != "general_ip_guidance",
        jurisdiction == "India" and any(
            word in text for word in ["india", "indian", "ip india"]
        )
    ])

    confidence = round(0.70 + (detected * 0.07), 2)
    confidence = min(confidence, 0.98)

    return {
        "intent": intent,
        "ip_type": ip_type,
        "product_type": product_type,
        "jurisdiction": jurisdiction
    }, confidence


@classification_bp.route("/classify", methods=["POST"])
def classify():
    data = request.get_json(silent=True) or {}

    query = data.get("query", "").strip()

    if not query:
        return jsonify({
            "error": "Query is required"
        }), 400

    classification, confidence = classify_query(query)

    return jsonify({
        "success": True,
        "query": query,
        "classification": classification,
        "confidence": confidence
    })