# Gentrification_model

Notebook-driven Python ML project for analyzing gentrification patterns using XGBoost, with a structured data lifecycle and reproducible workflows.

## Workspace Structure
- `data/`
  - `raw/`, `interim/`, `processed/`: datasets across lifecycle stages. Prefer using files in `data/` and avoid hardcoded absolute paths.
- `notebooks/`
  - `01_Raster_data_cleaning.ipynb`: prepare and clean data (including raster-derived features).
  - `02_Machine_Learning_Modell.ipynb`: XGBoost classification; stratified splits, hyperparameter tuning, threshold tuning for class 0, and predictions export.
  - `03_visualixe_model_training_data.ipynb`: visualize core model predictions over neighborhoods (training/holdout context).
  - `04_visualize_model_fingerplan.ipynb`: visualize fingerplan predictions over the fingerplan shapefile.
  - `OLD_*`: legacy notebooks for reference.
- `py_programs/`: placeholder for reusable functions/scripts (extract later when workflows stabilize).
- `.github/copilot-instructions.md`: guidance for AI coding agents.
- `results/`: outputs from analyses
  - `figures/`: plots and interactive maps (e.g., `prediction_map.html`, `fingerplan_predict_map.html`).
  - `models/`: predictions CSVs (e.g., `predictions_cph.csv`, `finger_predictions.csv`) and model artifacts.
  - `reports/`: narrative summaries or run notes.
  - `metrics/`: CSV/JSON metrics (accuracy, confusion matrix counts).

## Data Flow
1. Clean data in `01_Raster_data_cleaning.ipynb` → save to `data/processed/`.
  - Spatial-first, temporal-weighted imputation using KDTree on `x_coord`,`y_coord` (EPSG:25832) and numeric temporal features.
  - Rows without valid coordinates fall back to global column means.
  - Save step aligns indices; includes target `y` only if present and length matches.
2. Augment with spatial centroids using `py_programs/augment_with_geo.py`:
  - Reads `data/raw/GT_V1_data_cph.csv` and shapefile `data/raw/neighborhood_shapefile/Nabolag_cph_fre_new.shp`.
  - Detects shapefile key (prefers `munic_clus`, then `cluster_id`) and merges centroids onto CSV by `Cluster_id`.
  - Reprojects to EPSG:25832; computes polygon centroids.
  - Outputs `data/processed/GT_V1_data_cph_geo.csv` for spatially-aware analysis.
## Typical Run Order
1) Spatial augmentation: `py_programs/augment_with_geo.py` → `data/processed/GT_V1_data_cph_geo.csv`
2) Cleaning & imputation: `notebooks/01_Raster_data_cleaning.ipynb` → `data/processed/` cleaned dataset
3) Modeling: `notebooks/02_Machine_Learning_Modell.ipynb` (stratified splits, XGB, tuning, threshold selection for class 0, evaluation, predictions export)

Train/evaluate XGBoost in `03_Machine_Learning_Modell.ipynb` using processed inputs (prefer `GT_V1_data_cph_geo.csv` where spatial features are needed).

## Conventions
- Use workspace-relative paths: `os.path.join('data', 'processed', ...)`.
- Reproducibility:
  - Train/test split: `train_test_split(..., stratify=y, random_state=42)`.
  - Seed any randomness with `random_state=42`.
- Modeling:
  - Prefer `XGBClassifier` for binary classification.
  - Metrics: `accuracy_score`, `classification_report`, `ConfusionMatrixDisplay`.
  - Threshold tuning: sweep the class-0 probability threshold to prioritize recall for class 0; use the tuned threshold for downstream predictions.
- Hyperparameter tuning:
  - `RandomizedSearchCV` with `cv=10`, `n_iter=100`, `scoring='accuracy'`, `n_jobs=-1`, `random_state=42`.
- Feature importance plotting:
  ```python
  fi = best_model.feature_importances_
  names = X.columns
  idx = np.argsort(fi)[::-1]
  plt.figure(figsize=(10, 6))
  plt.bar(range(len(fi)), fi[idx], align='center')
  plt.xticks(range(len(fi)), np.array(names)[idx], rotation=90)
  plt.xlabel('Feature Importance')
  plt.title('XGBoost Feature Importances')
  plt.show()
  ```
 - Spatial augmentation:
   - Join keys: CSV uses `Cluster_id`; shapefile typically uses `munic_clus` (fallbacks: `cluster_id`, heuristic matches on 'munic'/'cluster').
   - Coordinates: centroids computed via `gdf.geometry.centroid` into `x_coord` and `y_coord`.

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

-## Environment & Layout
- Virtual environment: use Python venv with `python -m venv .venv`. Do not commit `.venv/`; recreate environments from `requirements.txt`.
 - Prefer using the venv’s interpreter for installs to avoid path confusion:
   - `& .\.venv\Scripts\python.exe -m pip install <package>`
- `src/` layout: keep reusable code in `py_programs/` for now. When it grows, promote to `src/gentrification_model/` with minimal packaging so imports are consistent across notebooks and scripts.

## Typical Workflow
- Run notebooks top-to-bottom, saving intermediate and final artifacts into `data/processed/`.
- Keep notebooks clean and deterministic; avoid absolute machine-specific paths.
- When logic stabilizes (data loading, preprocessing, training), extract it into `py_programs/` and import from notebooks.
 - If you reintroduce dimensionality reduction, drop NaN-containing columns before scaling to ensure valid input.

### Interactive Maps (Leafmap → HTML)
- Core model map (Notebook 3):
  - Save slim predictions from `02_Machine_Learning_Modell.ipynb` to `results/models/predictions_cph.csv` with columns: `cluster_id`, `prediction`.
  - Use `notebooks/03_visualixe_model_training_data.ipynb` to merge predictions with the neighborhood shapefile by `Cluster_id`/`cluster_id`, reproject to EPSG:4326, and build a Leafmap.
  - Save to `results/figures/prediction_map.html`; open in a browser (inline display disabled).
  - Status colors: Correct `#2ca02c`, Incorrect `#d62728`, NoPrediction `#7f7f7f`.

- Fingerplan map (Notebook 4):
  - Load `results/models/finger_predictions.csv` (columns: `cluster_id`, `prediction`).
  - Load shapefile `data/raw/fingerplanen_shapefile/GTD_clus_fingerplan_lessthan_50.shp`; prefer join key `munic_clus` (fallback heuristics on `cluster_id`/`munic`/`clus`).
  - Align dtypes for merge, reproject to EPSG:4326.
  - Build Leafmap using `leafmap.Map.add_geojson(..., style_function=...)` with colors: Class 0 `#2ca02c`, Class 1 `#1f77b4`, Class 2 `#ff7f0e`, NoPrediction `#7f7f7f`.
  - Save to `results/figures/fingerplan_predict_map.html`.

#### Open saved maps (Windows PowerShell)
```powershell
Start-Process .\results\figures\prediction_map.html
Start-Process .\results\figures\fingerplan_predict_map.html
```

## Notes
- If external CSVs are needed temporarily, define a configurable variable at the top of the notebook and plan to migrate into `data/processed/`.

## test 123

