import json
from app.ml.training.readiness import assess_yield_dataset

def test_training_gate_rejects_simulated_and_insufficient_dataset(tmp_path):
    dataset = tmp_path / "demo.csv"
    dataset.write_text("farm_id,observed_at,crop,yield_value,yield_unit,data_source,quality_flag\n1,2026-01-01,rice,2,t/ha,simulated,good\n")
    provenance = tmp_path / "provenance.json"
    provenance.write_text(json.dumps({"dataset_version":"v1","license":"CC-BY","collection_method":"demo","spatial_holdout":"district","temporal_holdout":"year","approved_by":"reviewer","contains_simulated_data":True}))
    result = assess_yield_dataset(dataset, provenance)
    assert result.approved is False
    assert result.records == 1
    assert any("Simulated" in error for error in result.errors)

def test_training_gate_requires_provenance(tmp_path):
    result = assess_yield_dataset(tmp_path / "missing.csv", tmp_path / "missing.json")
    assert result.approved is False
    assert result.errors == ["Dataset file is missing."]
