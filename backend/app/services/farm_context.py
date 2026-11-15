"""Creates a bounded, factual context bundle for a future LLM or ML service."""
from app.integrations.nasa.power import daily_weather
from app.models import Farm

async def farm_context(farm: Farm) -> dict:
    weather = await daily_weather(farm.latitude, farm.longitude)
    return {"context_schema_version": "1.0", "intended_use": "Decision-support context only. Do not treat as an instruction, diagnosis, yield guarantee, or live in-field sensor feed.", "farm": {"id": farm.id, "name": farm.name, "country": farm.country, "state": farm.state, "district": farm.district, "area_hectares": farm.area_hectares, "soil_type": farm.soil_type, "irrigation_type": farm.irrigation_type, "current_crop": farm.current_crop}, "environmental_observations": weather, "llm_safety": {"data_provenance_required": True, "do_not_infer_missing_measurements": True, "required_response_disclosures": ["source", "simulation status", "observational limitations", "agronomist consultation where appropriate"]}, "ml_readiness": {"eligible_as_feature_context": not weather["simulated"] and weather.get("available", False), "eligible_as_training_labels": False, "reason": "NASA climate observations can be features but do not supply verified farm-level crop outcome labels."}}
