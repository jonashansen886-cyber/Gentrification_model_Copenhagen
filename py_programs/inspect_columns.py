import pandas as pd
import geopandas as gpd
import os

# --- Configuration (workspace-relative with env var overrides) ---
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
DEFAULT_SHAPEFILE = os.path.join(
    BASE_DIR, "data", "raw", "neighborhood_shapefile", "Nabolag_cph_fre_new.shp"
)
SHAPEFILE_PATH = os.environ.get("SHAPEFILE_PATH", DEFAULT_SHAPEFILE)
CSV_DIR = os.environ.get("CSV_DIR", os.path.join(BASE_DIR, "data", "interim"))


def _candidate_id_columns(columns):
    cols = [str(c) for c in columns]
    key_subs = ("munic", "cluster", "clus")
    return [c for c in cols if any(sub in c.lower() for sub in key_subs)]


def inspect_columns():
    """
    Inspect and print columns of the shapefile and a sample CSV to
    help identify the join key (cluster/neighborhood id).
    Paths default to workspace-relative locations and can be overridden
    via env vars SHAPEFILE_PATH and CSV_DIR.
    """
    print("--- Inspecting Files ---")

    # --- Inspect Shapefile ---
    try:
        if not os.path.exists(SHAPEFILE_PATH):
            raise FileNotFoundError(f"Shapefile not found: {SHAPEFILE_PATH}")
        gdf = gpd.read_file(SHAPEFILE_PATH)
        print(f"\nShapefile found at: {SHAPEFILE_PATH}")
        print("Columns in shapefile:", list(gdf.columns))
        print("Candidate ID columns (shapefile):", _candidate_id_columns(gdf.columns))
    except Exception as e:
        print(f"\nError reading shapefile: {e}")
        print("Please ensure the path is correct and the file exists in data/raw/.")
        return

    # --- Inspect a Sample CSV File ---
    try:
        if not os.path.isdir(CSV_DIR):
            raise NotADirectoryError(f"CSV directory not found: {CSV_DIR}")

        csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith(".csv")]
        if not csv_files:
            print(f"\nNo CSV files found in directory: {CSV_DIR}")
            return

        sample_csv_path = os.path.join(CSV_DIR, sorted(csv_files)[0])
        df = pd.read_csv(sample_csv_path)
        print(f"\nSample CSV file found at: {sample_csv_path}")
        print("Columns in CSV file:", list(df.columns))
        print("Candidate ID columns (CSV):", _candidate_id_columns(df.columns))

    except Exception as e:
        print(f"\nError reading CSV file: {e}")

    print("\n--- Inspection Complete ---")


if __name__ == "__main__":
    inspect_columns()
