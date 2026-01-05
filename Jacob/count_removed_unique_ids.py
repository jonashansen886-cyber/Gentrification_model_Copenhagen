
import pandas as pd
import geopandas as gpd
import os

# --- Configuration ---
SHAPEFILE_PATH = r"C:\P7_pyt\GIS_lag\clusters_hovedstad_clean.shp"
CSV_DIR = r"C:\P7_pyt\cph_frb_long"
ID_COLUMN = 'cluster_id'

def count_unique_removed_ids():
    """
    Calculates the number of unique cluster_ids that were removed during the filtering process.
    """
    print("--- Analyzing Unique Cluster IDs ---")

    # --- 1. Get the set of valid IDs from the shapefile ---
    try:
        gdf = gpd.read_file(SHAPEFILE_PATH)
        valid_ids = set(gdf[ID_COLUMN])
        print(f"Found {len(valid_ids)} unique 'cluster_id's in the shapefile.")
    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return

    # --- 2. Get the set of all original IDs from the CSV files ---
    try:
        csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
        if not csv_files:
            print(f"No CSV files found in {CSV_DIR}.")
            return
            
        original_csv_ids = set()
        print(f"Processing {len(csv_files)} original CSV files to find all unique IDs...")
        
        for filename in csv_files:
            file_path = os.path.join(CSV_DIR, filename)
            try:
                df = pd.read_csv(file_path)
                # Add the unique IDs from this file to our master set
                original_csv_ids.update(df[ID_COLUMN].unique())
            except Exception as e:
                print(f"Could not process file {filename}. Reason: {e}")
        
        print(f"Found {len(original_csv_ids)} unique 'cluster_id's across all original CSV files.")

    except Exception as e:
        print(f"An error occurred while accessing the CSV directory: {e}")
        return

    # --- 3. Calculate the difference ---
    # These are the IDs that were in the CSVs but NOT in the shapefile
    removed_ids = original_csv_ids - valid_ids
    
    number_of_removed_ids = len(removed_ids)

    print("\n--- Result ---")
    print(f"Number of unique cluster_ids removed: {number_of_removed_ids}")
    print("--- Complete ---")


if __name__ == "__main__":
    count_unique_removed_ids()
