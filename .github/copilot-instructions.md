# Copilot Instructions for Gentrification_model

These instructions guide AI coding agents to be productive in this workspace. Focus on the current structure: data folders, notebooks-driven workflows, and Python-based ML experiments.

## Overview & Architecture
- **Workspace structure:**
  - `data/` with `raw/`, `interim/`, `processed/`: store datasets across lifecycle stages. Agents should not hardcode external paths; prefer using files in `data/`.
  - `notebooks/`: primary analysis in Jupyter notebooks. Key notebooks:
    - `01_Raster_data_cleaning.ipynb`: data preparation and cleaning (including raster-derived features).
    - `02_Machine_Learning_Modell.ipynb`: XGBoost classification with stratified splits, hyperparameter tuning, threshold tuning for class 0, and predictions export.
    - `03_visualixe_model_training_data.ipynb`: core model visualization over neighborhoods.
    - `04_visualize_model_fingerplan.ipynb`: fingerplan visualization map using Leafmap.
    - `OLD_*` notebooks: legacy experiments; use for reference, not extension.
  - `py_programs/`: placeholder for reusable Python scripts/functions. Prefer extracting shared logic here.
- **Data flow:** Clean data is produced in `01_...` and consumed by the ML model in `02_...`. Keep inputs/outputs versioned under `data/processed/` to make runs reproducible.
 - **Spatial augmentation:** Use `py_programs/augment_with_geo.py` to merge centroid coordinates from the shapefile into the primary CSV, producing `data/processed/GT_V1_data_cph_geo.csv` for spatial analysis.
  - Reproject to EPSG:25832 before computing centroids to ensure metric distances.
  - Join key: CSV `Cluster_id` ↔ shapefile `munic_clus` (fallbacks handled).

## Environment & Dependencies
- **Python version:** Use Python 3.9+ unless the user specifies otherwise.
- **Core libs:** `pandas`, `numpy`, `matplotlib`, `scikit-learn`, `xgboost`.
- **Install deps:** When adding code, include a minimal `requirements.txt` update if new packages are necessary.
- **Notebook kernels:** Ensure the active kernel has required packages before executing cells.
- **Virtual envs:** Do not commit the local venv. Recreate via `requirements.txt`; add `.venv/` to `.gitignore`.
- **Conda option:** If you prefer Conda, commit an `environment.yml` (alternative to `requirements.txt`, avoid maintaining both).

## Conventions & Patterns
- **Paths:** Use `os.path.join` and workspace-relative paths (e.g., `data/processed/...`). Avoid absolute Windows paths like `C:\Users\...` in committed notebooks or scripts.
- **Splits:** Use `train_test_split(..., stratify=y)` and a fixed `random_state=42` for reproducibility (as seen in `03_Machine_Learning_Modell.ipynb`).
- **Models:** Favor `XGBClassifier` for binary classification. Evaluate with `accuracy_score`, `classification_report`, and `ConfusionMatrixDisplay`.
- **Tuning:** Hyperparameter search via `RandomizedSearchCV` with `cv=10`, `n_iter=100`, `scoring='accuracy'`, `n_jobs=-1`, `random_state=42`.
 - **Threshold tuning (Notebook 3):** Select the class-0 probability via `best_model.classes_`, binarize labels (`y == 0`), sweep thresholds to prioritize recall for class 0 (tie-breaker F1), and use the tuned threshold `best_t` for downstream predictions (predict 0 if `P(class0) >= best_t`, else `argmax`).
- **Feature importance:** Plot using `best_model.feature_importances_` and `matplotlib` after sorting indices.
- **Language:** Some comments are in Danish; preserve meaning when refactoring.
- **Code layout:** Keep reusable logic in `py_programs/` for now. When it grows, consider a `src/` layout (e.g., `src/gentrification_model/`) with minimal packaging to enable consistent imports.
 - **Spatial joins:**
   - CSV join key is `Cluster_id`.
   - Shapefile key typically `munic_clus` (fallback `cluster_id` or heuristic columns containing 'munic'/'cluster').
   - Coordinates come from polygon centroids (`gdf.geometry.centroid`) into `x_coord`/`y_coord`.
 - **Imputation (Notebook 1):**
   - Define `X` excluding `Cluster_id` and optional target `y` (auto-detected; proceed without `y` if absent).
   - Two-stage approach: KDTree on valid metric coordinates; temporal-weighted averaging inside spatial neighborhoods.
   - Rows lacking valid coordinates fall back to global column means.
   - Save step aligns indices and includes `y` only when present and length-matched.
 - **Dimensionality reduction (optional):** If PCA is reintroduced, drop any-NaN columns prior to scaling, and standardize features (exclude `Cluster_id`, `Gen_value`, `x_coord`, `y_coord`).

## Workflows
- **Run notebooks:** Execute cells top-to-bottom. If adding cells, document inputs/outputs and write derived datasets to `data/processed/`.
- **Reproducibility:** Seed random operations (`random_state=42`). Save intermediate artifacts (cleaned CSVs, models, predictions) to `data/interim/` or `data/processed/`.
- **Refactor to scripts:** When logic stabilizes (e.g., data loading, preprocessing, model training), extract functions to `py_programs/` and import them in notebooks to reduce duplication.
 - **Spatial augmentation run:**
  ```powershell
  # From repo root
  & .\.venv\Scripts\python.exe py_programs\augment_with_geo.py
  ```
  Produces `data/processed/GT_V1_data_cph_geo.csv`.

### Interactive mapping workflow
- Core predictions output (Notebook 2): Save slim CSV to `results/models/predictions_cph.csv` with columns: `cluster_id`, `prediction`.
- Neighborhood visualization (Notebook 3): Load `predictions_cph.csv` and the neighborhood shapefile, normalize join keys (`Cluster_id`/`cluster_id`), reproject to EPSG:4326, and build a Leafmap. Save `results/figures/prediction_map.html`.
- Fingerplan predictions (Notebook 2): Save slim CSV to `results/models/finger_predictions.csv` with columns: `cluster_id`, `prediction`.
- Fingerplan visualization (Notebook 4):
  - Load `finger_predictions.csv` and shapefile `data/raw/fingerplanen_shapefile/GTD_clus_fingerplan_lessthan_50.shp`.
  - Prefer shapefile join key `munic_clus` (fallbacks: `cluster_id`, heuristic on columns containing 'munic'/'clus'/'cluster'). Align dtypes and strip leading zeros to avoid mismatches.
  - Reproject to EPSG:4326. Convert GeoDataFrame to GeoJSON using `gdf_merged.to_json()` (then `json.loads(...)`).
  - Use `leafmap.Map.add_geojson(..., style_function=...)` and cast `prediction` to int inside `style_function` for color mapping.
  - Colors: Class 0 `#2ca02c`, Class 1 `#1f77b4`, Class 2 `#ff7f0e`, NoPrediction `#7f7f7f`. Save `results/figures/fingerplan_predict_map.html`.

## External Data & Integration
- **CSV inputs:** Prefer reading from `data/processed/` rather than external folders. If an external path is necessary, make it configurable via a variable at the top of the notebook/script.
- **Visualization:** Use `matplotlib` for plots; keep figure sizes and label rotations readable (see feature importance example).
 - **Leafmap maps:** Save to HTML and open in a browser. Reproject GeoDataFrames to EPSG:4326 before exporting. Prefer `GeoDataFrame.to_json()` → `json.loads(...)` to produce GeoJSON for `add_geojson`.

## Examples from the Codebase
- **Train/validation/test split:**
  ```python
  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
  X_train, X_val, y_train, y_val = train_test_split(X_train, y_train, test_size=0.25, random_state=42, stratify=y_train)
  ```
- **Randomized search for XGBoost:**
  ```python
  param_grid = {
      'n_estimators': [100, 200, 300, 500],
      'learning_rate': [0.01, 0.1, 0.2],
      'max_depth': [3, 6, 9],
      'min_child_weight': [1, 3, 5],
      'subsample': [0.7, 0.85, 1.0],
      'colsample_bytree': [0.7, 0.85, 1.0],
      'reg_alpha': [0, 0.01, 0.1, 1, 10, 100],
      'reg_lambda': [0.5, 0.7, 1, 1.3]
  }
  search = RandomizedSearchCV(XGBClassifier(random_state=42), param_grid, cv=10, scoring='accuracy', n_iter=100, n_jobs=-1, verbose=2, random_state=42)
  search.fit(X_train, y_train)
  best_model = search.best_estimator_
  ```
- **Feature importance plot:**
  ```python
  import numpy as np
  import matplotlib.pyplot as plt
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

## Setup Commands (Windows PowerShell)
```powershell
# Create venv and activate
python -m venv .venv; .\.venv\Scripts\Activate.ps1

# Install core dependencies
pip install pandas numpy matplotlib scikit-learn xgboost ipykernel geopandas seaborn leafmap

# Register ipykernel (optional)
& .\.venv\Scripts\python.exe -m ipykernel install --user --name gentrification-model

# Launch Jupyter
jupyter notebook
```

### Windows venv tips
- Prefer using the venv interpreter for installs: `& .\.venv\Scripts\python.exe -m pip install <package>`.
- Avoid committing `.venv/`; recreate environments from `requirements.txt`.

## What Agents Should Do Next
- Prefer relative, configurable data paths; migrate hardcoded external paths into `data/`.
- Extract reusable preprocessing/model code into `py_programs/`.
- Keep notebooks clean: minimal side effects, clear cell order, and saved outputs in `data/processed/`.
 - When saving predictions for mapping, use slim CSVs with columns: `cluster_id`, `prediction` under `results/models/`.

If any of the above is unclear or incomplete (e.g., exact data file names, PCA output location), reply with questions and I’ll refine these instructions. 