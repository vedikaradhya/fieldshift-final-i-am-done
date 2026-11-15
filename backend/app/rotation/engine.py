from pydantic import BaseModel, Field

class RotationRequest(BaseModel):
    season: str = "kharif"
    irrigation_available: bool = False
    soil_type: str | None = None
    previous_crop: str | None = None
    weights: dict[str, float] = Field(default_factory=lambda: {"climate": .30, "soil": .20, "water": .20, "diversity": .15, "nutrient": .15})

CATALOG = [
    {"crop": "Pearl millet", "season": "kharif", "water": "low", "soil": ["sandy", "loamy"], "family": "grass", "nitrogen": .25},
    {"crop": "Pigeon pea", "season": "kharif", "water": "low", "soil": ["loamy", "black"], "family": "legume", "nitrogen": .95},
    {"crop": "Rice", "season": "kharif", "water": "high", "soil": ["clay", "loamy"], "family": "grass", "nitrogen": .20},
    {"crop": "Chickpea", "season": "rabi", "water": "low", "soil": ["loamy", "black"], "family": "legume", "nitrogen": .90},
    {"crop": "Mustard", "season": "rabi", "water": "medium", "soil": ["loamy", "sandy"], "family": "brassica", "nitrogen": .30},
]

def recommend(request: RotationRequest) -> dict:
    weights = request.weights.copy(); total = sum(max(0, v) for v in weights.values())
    if not total: raise ValueError("At least one rotation weight must be positive")
    weights = {k: max(0, v)/total for k, v in weights.items()}
    choices = []
    for item in CATALOG:
        if item["season"] != request.season: continue
        if item["water"] == "high" and not request.irrigation_available: continue
        components = {"climate": .82, "soil": .9 if request.soil_type and request.soil_type.lower() in item["soil"] else .65, "water": .9 if item["water"] == "low" or request.irrigation_available else .55, "diversity": .9 if request.previous_crop and request.previous_crop.lower() not in item["crop"].lower() else .6, "nutrient": item["nitrogen"]}
        score = 100 * sum(weights.get(name, 0) * components.get(name, 0) for name in weights)
        choices.append({"crop": item["crop"], "score": round(score, 1), "components": {k: round(v, 2) for k,v in components.items()}, "limitations": "Planning guidance only; validate locally with an agronomist and current field observations."})
    return {"season": request.season, "weights": weights, "recommendations": sorted(choices, key=lambda c: c["score"], reverse=True), "simulated": True, "data_sources": ["Configurable agronomic rule catalog", "AgriSpace demo environmental context"]}
