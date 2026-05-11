# Gentrification_model

Notebook-driven Python ML project for analyzing gentrification patterns in Copenhagen using XGBoost, LSTM, and ensemble methods, with a structured data lifecycle and reproducible workflows.

## Dummy Data

Due to the underlying data being copyrighted, dummy CSV files have been created.
To get correct results, replace them with real data in `data/raw/` using the same filenames referenced in the notebooks.
The ArcGIS toolbox also requires long-format CSV files placed in `data/raw/long_format_csv/`.

## Workspace Structure

```
data/
  raw/                        — original inputs (shapefiles, CSVs, CVR JSON exports)
    cvr_raw/                  — raw CVR business-register data (current + temporal snapshots, industry IDs)
    long_format_csv/          — inputs for the ArcGIS space-time cube toolbox
    neighborhood_shapefile/
    fingerplanen_shapefile/
    ...
  interim/                    — checkpoints and partially-processed files
  processed/                  — cleaned, enriched outputs consumed by later notebooks
    NetCDF_cubes/             — space-time cube NetCDF files (output of notebook 00)
    tsc_reclass/              — reclassified TSC rasters (output of notebook 02)
    cvr/                      — processed CVR datasets (GeoJSON, Parquet, JSON)
    time_series_cluster_py/
    tsc_netcdf_vector/
    ...
results/
  figures/                    — interactive HTML maps
  models/                     — saved model artifacts and prediction CSVs
  metrics/                    — charts, overlay outputs
  reports/                    — written report
py_programs/                  — reusable helper scripts
notebooks/                    — analysis notebooks (run top-to-bottom)
```

## Notebooks

| # | Notebook | Description |
|---|----------|-------------|
| 00 | `00_space_time_cube_processing.ipynb` | Loads neighborhood socio-economic CSVs from `data/raw/long_format_csv`, applies K-NN spatial imputation across three 10-year intervals (1990–2020), and writes NetCDF space-time cubes to `data/processed/NetCDF_cubes`. |
| 01 | `01_timeseries_visualization.ipynb` | Visualizes ArcGIS Time Series Clustering DBF charts and exports HTML charts to `results/metrics/charts_html`. |
| 02 | `02_rasterize_reclassify.ipynb` | Rasterizes TSC clusters and applies Excel-based reclassification rules; outputs to `data/processed/tsc_reclass`. |
| 03 | `03_weighted_overlay_analysis.ipynb` | Computes weighted overlay, runs zonal statistics on clusters, and builds an interactive map; outputs to `results/metrics/overlay_output`. |
| 04 | `04_raster_data_cleaning.ipynb` | Prepares and cleans data including raster-derived features. |
| 05 | `05_XGBoost_model.ipynb` | XGBoost classification with stratified splits, `RandomizedSearchCV` hyperparameter tuning, threshold tuning for class 0, and prediction/probability export (`predictions_cph.csv`, `xgb_proba_cph.csv`). |
| 06 | `06_cvr_adresse_API.ipynb` | Queries `cvrapi.dk` and the DAWA geocoding API to enrich CVR business records with coordinates; saves progress to `data/interim/cvr_pipeline_checkpoint.json` for resumable runs (rate limit: ~100–200 requests/day). |
| 07 | `07_manual_cvr_data_pross_current.ipynb` | Processes current-snapshot CVR JSON exports from `data/raw/cvr_raw/cvr_current/`, filters to Copenhagen (kommunekode 101), and joins address/name/industry tables into a master dataset. |
| 08 | `08_manual_cvr_data_pross_temporal.ipynb` | Mirrors notebook 07 for temporal CVR JSON files (`data/raw/cvr_raw/cvr_temporal/`); uses streaming (`ijson`) to handle large (~10 GB) address files. |
| 09 | `09_proccecing_gentrified_industries.ipynb` | Filters CVR businesses to gentrification-associated industry codes and renders an interactive Folium timeline map of openings/closings (2000–2026). |
| 10 | `10_LSTM_model.ipynb` | Builds a PyTorch LSTM classifier; spatially joins CVR business points to neighborhood clusters, aggregates DB25 industry counts per 5-year window (6 time steps, 1990–2020), trains a sequence model, and saves the model to `results/models/lstm_gentrification.pt` and probabilities to `results/models/lstm_proba_cph.csv`. |
| 11 | `11_ensemble_model.ipynb` | Combines XGBoost (CV macro-F1 ≈ 0.727) and LSTM (CV macro-F1 ≈ 0.523) via hard and soft voting using pre-saved probability CSVs; analyzes error overlap and saves final ensemble predictions to `results/models/ensemble_predictions.csv`. |
| — | `MAPS/xgboost_prediction_maps.ipynb` | Visualizes XGBoost predictions over Copenhagen neighborhoods and the fingerplan shapefile; saves interactive HTML maps to `results/figures/`. |
| — | `MAPS/lstm_prediction_map.ipynb` | Visualizes LSTM predictions over Copenhagen neighborhoods; saves interactive HTML map to `results/figures/`. |
| — | `MAPS/ensemble_prediction_maps.ipynb` | Visualizes ensemble predictions over Copenhagen neighborhoods; saves interactive HTML map to `results/figures/`. |
| — | `MAPS/combined_prediction_map.ipynb` | Interactive choropleth combining all model predictions (XGBoost, LSTM, Hard/Soft Ensemble) across years (2020–2035) with toggle controls; saves `results/figures/ensemble_map_combined.html`. |
| — | `OLD_notebooks/` | Legacy experiments for reference only. |

## `py_programs/` Scripts

| Script | Purpose |
|--------|---------|
| `augment_with_geo.py` | Merges centroid coordinates from shapefile into the primary CSV; produces `data/processed/GT_V1_data_cph_geo.csv`. |
| `add_final_state_features.py` | Adds final-state features to the dataset. |
| `add_start_and_end_features.py` | Adds start/end period features. |
| `add_volatility_features.py` | Computes volatility features across time windows. |
| `analyze_2015_2020_features.py` | Analyzes features for the 2015–2020 period. |
| `cleanup_final_lag.py` | Cleans up lagged feature columns. |
| `create_dummy_datasets.py` | Generates dummy CSV files for testing without real data. |
| `filter_neighborhoods_cph_fre.py` | Filters neighborhoods to Copenhagen/Frederiksberg. |
| `filter_neighvorhoods_fingerplan.py` | Filters neighborhoods to the fingerplan area. |
| `melt_csv_to_long.py` | Reshapes wide-format CSV to long format for the space-time cube. |
| `process_5y_reg.py` | Processes 5-year regression statistics. |
| `reclassify_charts.py` | Applies reclassification rules to TSC chart DBFs. |

## Key Results Artifacts

| File | Description |
|------|-------------|
| `results/models/predictions_cph.csv` | XGBoost neighborhood predictions (`cluster_id`, `prediction`). |
| `results/models/xgb_proba_cph.csv` | XGBoost class probabilities for ensemble input. |
| `results/models/finger_predictions.csv` | XGBoost fingerplan area predictions. |
| `results/models/lstm_gentrification.pt` | Saved PyTorch LSTM model weights. |
| `results/models/lstm_predictions.csv` | LSTM neighborhood predictions. |
| `results/models/lstm_proba_cph.csv` | LSTM class probabilities for ensemble input. |
| `results/models/ensemble_predictions.csv` | Final ensemble (XGBoost + LSTM) predictions. |
| `results/figures/prediction_map.html` | Interactive XGBoost neighborhood prediction map. |
| `results/figures/fingerplan_predict_map.html` | Interactive fingerplan prediction map. |

## Conventions

- **Paths:** Use workspace-relative paths: `os.path.join('data', 'processed', ...)`. Never hardcode absolute paths.
- **Reproducibility:** Fix `random_state=42` on all splits and model training. Train/test split uses `stratify=y`.
- **XGBoost modeling:**
  - `XGBClassifier` for classification; evaluate with `accuracy_score`, `classification_report`, `ConfusionMatrixDisplay`.
  - Hyperparameter search: `RandomizedSearchCV` with `cv=10`, `n_iter=100`, `scoring='accuracy'`, `n_jobs=-1`, `random_state=42`.
  - Threshold tuning: sweep class-0 probability to prioritize recall for class 0; use the tuned threshold for downstream predictions.
- **LSTM modeling:**
  - PyTorch sequence model trained on 6 time-step CVR industry count sequences per neighborhood cluster.
  - Save model weights to `results/models/lstm_gentrification.pt` and probabilities to `results/models/lstm_proba_cph.csv`.
- **Ensemble:**
  - Combine XGBoost and LSTM via hard/soft voting from pre-saved probability CSVs.
  - Save final predictions to `results/models/ensemble_predictions.csv`.
- **Spatial joins:**
  - CSV join key: `Cluster_id`; shapefile key: `munic_clus` (fallbacks: `cluster_id`, heuristic on 'munic'/'cluster').
  - Reproject to EPSG:25832 for metric distances; export maps in EPSG:4326.
  - Centroids: `gdf.geometry.centroid` → `x_coord`/`y_coord`.
- **CVR data:**
  - Raw JSON exports from datafordeler.dk go in `data/raw/cvr_raw/cvr_current/` and `data/raw/cvr_raw/cvr_temporal/`.
  - Processed outputs land in `data/processed/cvr/` (GeoJSON, Parquet, JSON).

## Setup (Windows PowerShell)

```powershell
# Create and activate virtual environment
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# (Optional) Register ipykernel
& .\.venv\Scripts\python.exe -m ipykernel install --user --name gentrification-model

# Launch Jupyter
jupyter notebook
```

## Setup (macOS/Linux Bash)

```bash
# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Register ipykernel
python -m ipykernel install --user --name gentrification-model

# Launch Jupyter
jupyter notebook
```

> **macOS tip:** If you hit build issues with `geopandas`/`fiona`/`pyproj` on Apple Silicon, use Conda:
> ```bash
> conda create -n gentrification-model python=3.10
> conda activate gentrification-model
> pip install -r requirements.txt
> ```

## Environment & Layout

- Do not commit `.venv/`; recreate from `requirements.txt`.
- Prefer the venv interpreter for installs:
  - Windows: `& .\.venv\Scripts\python.exe -m pip install <package>`
  - macOS/Linux: `python -m pip install <package>` (with venv activated)
- Keep reusable code in `py_programs/`. When it grows, promote to `src/gentrification_model/`.

## Typical Workflow

1. Run notebooks in order (00 → 14), saving intermediate artifacts to `data/processed/`.
2. Keep notebooks clean and deterministic; avoid absolute machine-specific paths.
3. For the CVR pipeline (notebooks 08–12), the public `cvrapi.dk` API is rate-limited; use checkpoint files in `data/interim/` to resume across sessions.

## Open Saved Maps (Windows PowerShell)

```powershell
Start-Process .\results\figures\prediction_map.html
Start-Process .\results\figures\fingerplan_predict_map.html
```

