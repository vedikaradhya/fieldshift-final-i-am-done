# ML training governance

AgriSpace currently has **no trained ML model**. No validated labelled yield or crop-suitability dataset was supplied, and training with the included demo observations would be scientifically misleading.

The training gate at `backend/app/ml/training/readiness.py` rejects a dataset unless it has at least 200 labelled records, required outcome/provenance fields, a documented licence and collection method, spatial and temporal holdout plans, approval, consistent yield units, and no simulated sources. This is intentionally a gate, not a model trainer.

## To train a model legitimately

1. Provide a licensed CSV of real field-level outcomes with `farm_id`, `observed_at`, `crop`, `yield_value`, `yield_unit`, `data_source`, and `quality_flag`.
2. Supply a JSON provenance manifest that declares dataset version, licence, collection method, whether data are simulated, spatial/temporal holdout designs, and approver.
3. Pass the readiness gate; retain its output with the training run.
4. Fit on training folds only, tune without touching the spatial/temporal holdouts, then record appropriate metrics and calibration/uncertainty coverage.
5. Have a qualified domain reviewer approve the model before any farmer-facing prediction is enabled.

The project must never call an estimate a field observation, a model score a yield guarantee, or a demo output a validated recommendation.
