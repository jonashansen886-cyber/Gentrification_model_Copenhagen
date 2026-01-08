# Gentrification_model

Notebook-driven Python ML project for analyzing gentrification patterns using XGBoost, with a structured data lifecycle and reproducible workflows.

# Dummy data

Due to our data being copyrighted dummy csv files have been created. 
To get the correct result these dummy files needs to be replaced and placed in `data/raw` and have the same names as in Notebook 05.
Furthermore the ArcGIS tool box need the long_format csv files to be placed in the folder `data/raw/long_format_csv`.

## Workspace Structure
- `data/`
  - `raw/`, `interim/`, `processed/`: datasets across lifecycle stages. Prefer using files in `data/` and avoid hardcoded absolute paths.
- `notebooks/`
  - `01_visualize_timeseries_clustering.ipynb`: visualize ArcGIS Time Series Clustering DBF charts and export HTML charts to `results/metrics/charts_html`.
  - `02_TSC_rasterize_reclassify.ipynb`: rasterize TSC clusters and apply Excel-based reclassification rules; outputs reclassified rasters to `data/processed/tsc_reclass`.
  - `03_weighted_overlay_analysis.ipynb`: compute weighted overlay, run zonal statistics on clusters, and build an interactive map; outputs to `results/metrics/overlay_output`.
  - `04_raster_data_cleaning.ipynb`: prepare and clean data (including raster-derived features).
  - `05_machine_learning_Model.ipynb`: XGBoost classification; stratified splits, hyperparameter tuning, threshold tuning for class 0, and predictions export.
  - `06_visualixe_model_training_data.ipynb`: visualize core model predictions over neighborhoods (training/holdout context).
  - `07_visualize_model_fingerplan.ipynb`: visualize fingerplan predictions over the fingerplan shapefile.
  - `OLD_*`: legacy notebooks for reference.
- `py_programs/`: folder for reusable functions/scripts.
- `.github/copilot-instructions.md`: guidance for AI coding agents.
- `results/`: outputs from analyses
  - `figures/`: plots and interactive maps (e.g., `prediction_map.html`, `fingerplan_predict_map.html`).
  - `models/`: predictions CSVs (e.g., `predictions_cph.csv`, `finger_predictions.csv`) and model artifacts.
  - `reports/`: the full written report.
  - `metrics/`: charts and overlay outputs.


## Conventions
- Use workspace-relative paths: `os.path.join('data', 'processed', ...)`.
- Reproducibility:
  - Train/test split: `train_test_split(..., stratify=y, random_state=42)`.
  - Seed any randomness with `random_state=42`.
- Modeling:
  - Prefer `XGBClassifier` for classification.
  - Metrics: `accuracy_score`, `classification_report`, `ConfusionMatrixDisplay`.
  - Threshold tuning: sweep the class-0 probability threshold to prioritize recall for class 0; use the tuned threshold for downstream predictions.
- Hyperparameter tuning:
  - `RandomizedSearchCV` with `cv=10`, `n_iter=100`, `scoring='accuracy'`, `n_jobs=-1`, `random_state=42`.

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

Tips (macOS):
- If you hit build issues with `geopandas`/`fiona`/`pyproj` on Apple Silicon, consider using Conda (alternative) or install prebuilt wheels. Conda example:
  - `conda create -n gentrification-model python=3.10`
  - `conda activate gentrification-model`
  - `pip install -r requirements.txt`

## Environment & Layout
- Virtual environment: use Python venv with `python -m venv .venv`. Do not commit `.venv/`; recreate environments from `requirements.txt`.
  - Prefer using the venv’s interpreter for installs to avoid path confusion:
    - Windows: `& .\.venv\Scripts\python.exe -m pip install <package>`
    - macOS/Linux: `python -m pip install <package>` (with venv activated)
- `src/` layout: keep reusable code in `py_programs/` for now. When it grows, promote to `src/gentrification_model/` with minimal packaging so imports are consistent across notebooks and scripts.

## Typical Workflow
- Run notebooks top-to-bottom, saving intermediate and final artifacts into `data/processed/`.
- Keep notebooks clean and deterministic; avoid absolute machine-specific paths.


#### Open saved maps (Windows PowerShell)
```powershell
Start-Process .\results\figures\prediction_map.html
Start-Process .\results\figures\fingerplan_predict_map.html
```

## Space-Time Analysis (ArcGIS Pro)
Use the ArcGIS Python Toolbox for a GUI-driven workflow to create Space-Time Cubes, run Time Series Clustering, and optionally Emerging Hotspot Analysis.

- Toolbox path: [ArcGIS_Toolbox/001STA_Toolbox.pyt](ArcGIS_Toolbox)
- Requirements: ArcGIS Pro with Space-Time Pattern Mining tools (`arcpy` comes with ArcGIS Pro; not installed via pip).

### Add the Toolbox in ArcGIS Pro
1. Open ArcGIS Pro and your project.
2. In the Catalog pane, right-click Toolboxes → Add Toolbox.
3. Browse to [ArcGIS_Toolbox/001STA_Toolbox.pyt](ArcGIS_Toolbox/001STA_Toolbox.pyt)t.
4. Run the toolbox and the files should be created.

### Inputs and Conventions
- Long-format CSVs (e.g., `cluster_<variable>_long.csv`) should be placed under `data/raw/long_format_csv` .

### Outputs and Downstream Use
- Space-Time Cubes: [data/processed/space_time_cube](data/processed/space_time_cube)
- Time Series Clustering: [data/processed/time_series_cluster](data/processed/time_series_cluster)
- Emerging Hotspot Analysis: [data/processed/emerging_hotspot](data/processed/emerging_hotspot)
  - Visualize `_chart` DBFs via [notebooks/01_visualize_timeseries_clustering.ipynb](notebooks/01_visualize_timeseries_clustering.ipynb)
  - Continue weighted overlay and zonal stats in [notebooks/03_weighted_overlay_analysis.ipynb](notebooks/03_weighted_overlay_analysis.ipynb).

### Notes & Troubleshooting
- Ensure CSVs include required columns and that `location_id` types match between features and CSVs.
- Keep output paths inside the repository (e.g., `data/processed/`) to stay reproducible.
- `arcpy` is available only within the ArcGIS Pro environment; use ArcGIS Pro to run the toolbox tools.




