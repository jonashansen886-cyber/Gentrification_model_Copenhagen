import pandas as pd
import geopandas as gpd
import os

# --- Configuration ---
SHAPEFILE_PATH = r"C:\P7_pyt\GIS_lag\clusters_hovedstad_clean.shp"
CSV_DIR = r"C:\P7_pyt\cph_frb_long"
OUTPUT_DIR = r"C:\P7_pyt\cph_frb_long_filtered"
ID_COLUMN = 'cluster_id' # As identified by the inspection script

def filter_csv_files_and_report():
    """
    Filters CSV files based on IDs from a shapefile and reports the changes.
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
        gdf = gpd.read_file(SHAPEFILE_PATH)
        # Convert to a set for efficient lookup
        valid_ids = set(gdf[ID_COLUMN])
        print(f"Successfully read {len(valid_ids)} unique cluster IDs from the shapefile.")
    except Exception as e:
        print(f"Error reading shapefile or extracting IDs: {e}")
        return

    # --- 3. Process Each CSV File ---
    try:
        csv_files = [f for f in os.listdir(CSV_DIR) if f.endswith('.csv')]
        if not csv_files:
            print(f"No CSV files found in {CSV_DIR}.")
            return
        
        print(f"\nFound {len(csv_files)} CSV files to process...")

        for filename in csv_files:
            file_path = os.path.join(CSV_DIR, filename)
            
            try:
                df = pd.read_csv(file_path)
                original_rows = len(df)

                # Filter the dataframe
                filtered_df = df[df[ID_COLUMN].isin(valid_ids)]
                filtered_rows = len(filtered_df)
                
                removed_rows = original_rows - filtered_rows

                # Save the new filtered file
                output_path = os.path.join(OUTPUT_DIR, filename)
                filtered_df.to_csv(output_path, index=False)

                # Report the result for the file
                print(f"\nProcessed: {filename}")
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
