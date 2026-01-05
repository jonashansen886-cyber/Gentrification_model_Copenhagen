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

KNOWN_ID_CANDIDATES = ["munic_clus", "cluster_id", "Cluster_id"]


def find_id_column(columns):
    cols = [str(c) for c in columns]
    for cand in KNOWN_ID_CANDIDATES:
        if cand in cols:
            return cand
    for c in cols:
        if any(sub in c.lower() for sub in ("munic", "cluster", "clus")):
            return c
    return None


def normalize_ids(series):
    s = series.astype(str).str.strip()
    s = s.str.lstrip("0")
    s = s.replace({"": None})
    return s


def count_unique_removed_ids():
    """
    Calculate the number of unique IDs present in CSVs but not in the shapefile.
    Uses auto-detected join keys and normalized IDs for robust comparison.
    """
    print("--- Analyzing Unique Cluster IDs ---")

    # --- 1. Get the set of valid IDs from the shapefile ---
    try:
        if not os.path.exists(SHAPEFILE_PATH):
            raise FileNotFoundError(f"Shapefile not found: {SHAPEFILE_PATH}")
        gdf = gpd.read_file(SHAPEFILE_PATH)
        shp_id_col = find_id_column(gdf.columns)
        if shp_id_col is None:
            raise KeyError(
                f"Could not find an ID column in shapefile. Checked candidates: {KNOWN_ID_CANDIDATES}"
            )
        valid_ids = set(normalize_ids(gdf[shp_id_col]).dropna().unique())
        print(
            f"Found {len(valid_ids)} unique normalized IDs in the shapefile (key: {shp_id_col})."
        )
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return

    # --- 2. Get the set of all original IDs from the CSV files ---
    try:
        if not os.path.isdir(CSV_DIR):
            raise NotADirectoryError(f"CSV directory not found: {CSV_DIR}")
        csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith(".csv")]
        if not csv_files:
            print(f"No CSV files found in {CSV_DIR}.")
            return

        original_csv_ids = set()
        print(
            f"Processing {len(csv_files)} original CSV files to find all unique IDs..."
        )

        for filename in sorted(csv_files):
            file_path = os.path.join(CSV_DIR, filename)
            try:
                df = pd.read_csv(file_path)
                csv_id_col = find_id_column(df.columns)
                if csv_id_col is None:
                    print(f"  - Skipping {filename}: No ID column found.")
                    continue
                original_csv_ids.update(normalize_ids(df[csv_id_col]).dropna().unique())
            except Exception as e:
                print(f"Could not process file {filename}. Reason: {e}")

        print(
            f"Found {len(original_csv_ids)} unique normalized IDs across all original CSV files."
        )

    except Exception as e:
        print(f"An error occurred while accessing the CSV directory: {e}")
        return

    # --- 3. Calculate the difference ---
    removed_ids = original_csv_ids - valid_ids
    number_of_removed_ids = len(removed_ids)

    print("\n--- Result ---")
    print(
        f"Number of unique IDs present in CSVs but missing in shapefile: {number_of_removed_ids}"
    )
    print("--- Complete ---")


if __name__ == "__main__":
    count_unique_removed_ids()
