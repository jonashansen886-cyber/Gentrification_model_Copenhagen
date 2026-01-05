
import pandas as pd
import geopandas as gpd
import os

# --- Configuration ---
SHAPEFILE_PATH = r"C:\P7_pyt\GIS_lag\clusters_hovedstad_clean.shp"
CSV_DIR = r"C:\P7_pyt\cph_frb_long"

def inspect_columns():
    """
    This function inspects and prints the columns of the shapefile
    and a sample CSV file to identify the cluster ID columns.
    """
    print("--- Inspecting Files ---")

    # --- Inspect Shapefile ---
    try:
        gdf = gpd.read_file(SHAPEFILE_PATH)
        print(f"\nShapefile found at: {SHAPEFILE_PATH}")
        print("Columns in shapefile:", list(gdf.columns))
    except Exception as e:
        print(f"\nError reading shapefile: {e}")
        print("Please ensure the path is correct and the file is not corrupted.")
        return

    # --- Inspect a Sample CSV File ---
    try:
        # Find the first CSV file in the directory
        csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
        if not csv_files:
            print(f"\nNo CSV files found in directory: {CSV_DIR}")
            return

        sample_csv_path = os.path.join(CSV_DIR, csv_files[0])
        df = pd.read_csv(sample_csv_path)
        print(f"\nSample CSV file found at: {sample_csv_path}")
        print("Columns in CSV file:", list(df.columns))

    except Exception as e:
        print(f"\nError reading CSV file: {e}")

    print("\n--- Inspection Complete ---")

if __name__ == "__main__":
    inspect_columns()
