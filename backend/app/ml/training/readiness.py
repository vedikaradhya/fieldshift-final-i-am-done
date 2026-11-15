"""Dataset gate used before a scientifically meaningful training run can begin."""
from dataclasses import dataclass
from pathlib import Path
import csv
import json

REQUIRED_COLUMNS = {"farm_id", "observed_at", "crop", "yield_value", "yield_unit", "data_source", "quality_flag"}
ACCEPTED_UNITS = {"kg/ha", "t/ha"}

@dataclass(frozen=True)
class TrainingReadiness:
    approved: bool
    records: int
    errors: list[str]
    provenance: dict | None

def assess_yield_dataset(dataset_path: str | Path, provenance_path: str | Path) -> TrainingReadiness:
    """Reject unlabeled, demo, or inadequately documented data before model fitting.

    This does not train a model. It makes absence of fit-for-purpose data an
    explicit and auditable stop condition instead of generating false accuracy.
    """
    errors: list[str] = []
    path, provenance_file = Path(dataset_path), Path(provenance_path)
    if not path.is_file(): return TrainingReadiness(False, 0, ["Dataset file is missing."], None)
    if not provenance_file.is_file(): return TrainingReadiness(False, 0, ["Dataset provenance manifest is missing."], None)
    try: provenance = json.loads(provenance_file.read_text())
    except (OSError, json.JSONDecodeError): return TrainingReadiness(False, 0, ["Provenance manifest is not valid JSON."], None)
    for key in ("dataset_version", "license", "collection_method", "spatial_holdout", "temporal_holdout", "approved_by"):
        if not provenance.get(key): errors.append(f"Provenance field '{key}' is required.")
    if provenance.get("contains_simulated_data") is True: errors.append("Simulated data cannot be used for validated model training.")
    try:
        with path.open(newline="") as source:
            rows = list(csv.DictReader(source))
            columns = set(rows[0]) if rows else set()
    except OSError:
        return TrainingReadiness(False, 0, ["Dataset could not be read."], provenance)
    missing = REQUIRED_COLUMNS - columns
    if missing: errors.append("Missing required columns: " + ", ".join(sorted(missing)))
    if len(rows) < 200: errors.append("At least 200 labelled observations are required before an experimental fit.")
    if any(row.get("data_source", "").lower() in {"demo", "simulated", "synthetic"} for row in rows): errors.append("Dataset contains a non-observational source.")
    if any(row.get("yield_unit") not in ACCEPTED_UNITS for row in rows): errors.append("Yield unit must be kg/ha or t/ha for every record.")
    return TrainingReadiness(not errors, len(rows), errors, provenance)
