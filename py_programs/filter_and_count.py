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
OUTPUT_DIR = os.environ.get(
    "OUTPUT_DIR", os.path.join(BASE_DIR, "data", "processed", "filtered_csvs")
)

KNOWN_ID_CANDIDATES = ["munic_clus", "cluster_id", "Cluster_id"]


def find_id_column(columns):
    cols = [str(c) for c in columns]
    for cand in KNOWN_ID_CANDIDATES:
        if cand in cols:
            return cand
    # Heuristic fallback
    for c in cols:
        if any(sub in c.lower() for sub in ("munic", "cluster", "clus")):
            return c
    return None


def normalize_ids(series):
    s = series.astype(str).str.strip()
    # Strip leading zeros and spaces for robust join
    s = s.str.lstrip("0")
    # Ensure empty strings become a consistent value
    s = s.replace({"": None})
    return s


def filter_csv_files_and_report():
    """
    Filter CSV files based on IDs from a shapefile and report changes.
    - Uses workspace-relative defaults under data/ for portability.
    - Auto-detects join keys with sensible fallbacks.
    - Normalizes ID values to reduce merge mismatches.
    """
    print("--- Starting Filtering Process ---")

    # --- 1. Create Output Directory ---
    try:
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        print(f"Output directory ensured at: {OUTPUT_DIR}")
    except OSError as e:
        print(f"Error creating directory {OUTPUT_DIR}: {e}")
        return

    # --- 2. Read Shapefile and Get Valid IDs ---
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
            f"Shapefile key: '{shp_id_col}'. Read {len(valid_ids)} unique normalized IDs from the shapefile."
        )
    except Exception as e:
        print(f"Error reading shapefile or extracting IDs: {e}")
        return

    # --- 3. Process Each CSV File ---
    try:
        if not os.path.isdir(CSV_DIR):
            raise NotADirectoryError(f"CSV directory not found: {CSV_DIR}")
        csv_files = [f for f in os.listdir(CSV_DIR) if f.lower().endswith(".csv")]
        if not csv_files:
            print(f"No CSV files found in {CSV_DIR}.")
            return

        print(f"\nFound {len(csv_files)} CSV files to process...")

        for filename in sorted(csv_files):
            file_path = os.path.join(CSV_DIR, filename)

            try:
                df = pd.read_csv(file_path)
                csv_id_col = find_id_column(df.columns)
                if csv_id_col is None:
                    raise KeyError(
                        f"No ID column found in {filename}. Checked candidates: {KNOWN_ID_CANDIDATES}"
                    )
                original_rows = len(df)

                ids_norm = normalize_ids(df[csv_id_col])
                filtered_df = df[ids_norm.isin(valid_ids)].copy()
                filtered_rows = len(filtered_df)

                removed_rows = original_rows - filtered_rows

                # Save the new filtered file
                output_path = os.path.join(OUTPUT_DIR, filename)
                filtered_df.to_csv(output_path, index=False)

                # Report the result for the file
                print(f"\nProcessed: {filename}")
                print(f"  - ID column (CSV): {csv_id_col}")
                print(f"  - Original rows: {original_rows}")
                print(f"  - Rows removed:  {removed_rows}")
                print(f"  - New file saved with {filtered_rows} rows at {output_path}")

            except Exception as e:
                print(f"Could not process file {filename}. Reason: {e}")

    except Exception as e:
        print(f"\nAn error occurred while accessing the CSV directory: {e}")

    print("\n--- Filtering Process Complete ---")


if __name__ == "__main__":
    filter_csv_files_and_report()
