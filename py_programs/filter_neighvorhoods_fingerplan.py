
import pandas as pd
import geopandas as gpd
import os
import glob

# --- Configuration ---
shapefile_path = r'C:\Users\jonas\Desktop\7_semester\Projekt\Data\GIS_lag\clusters_fingerplan.shp'
input_folder = 'CSV_filer'
output_folder = 'final_lag' # New folder specified by user
# --- End Configuration ---

def main():
    """
    Filters all CSV files in input_folder based on cluster IDs from a shapefile,
    saves them to output_folder, and reports on unique IDs removed.
    """
    try:
        # 1. Read the shapefile and get the set of valid cluster IDs
        print(f"Reading shapefile: {os.path.basename(shapefile_path)}")
        shapefile = gpd.read_file(shapefile_path)
        
        # Use 'munic_clus' as identified from inspection
        valid_cluster_ids = set(shapefile['munic_clus'])
        print(f"Found {len(valid_cluster_ids)} unique cluster IDs in the shapefile.")

    except Exception as e:
        print(f"Error reading shapefile: {e}")
        return

    os.makedirs(output_folder, exist_ok=True)
    print("-" * 30)

    # 2. Get all CSV files in the input folder
    csv_files = glob.glob(os.path.join(input_folder, "*.csv"))

    if not csv_files:
        print(f"No CSV files found in '{input_folder}' to process.")
        return

    # 3. Process each CSV file
    for file_path in csv_files:
        filename = os.path.basename(file_path)
        
        try:
            print(f"Processing file: {filename}")
            df = pd.read_csv(file_path)

            # Get unique cluster IDs before filtering
            initial_ids = set(df['cluster_id'])
            
            # Filter the DataFrame
            df_filtered = df[df['cluster_id'].isin(valid_cluster_ids)]

            # Get unique cluster IDs after filtering
            final_ids = set(df_filtered['cluster_id'])
            
            # --- 4. Report on removed IDs and remaining IDs ---
            removed_ids_count = len(initial_ids - final_ids)
            remaining_ids_count = len(final_ids) # Or len(df_filtered['cluster_id'].unique())
            
            print(f"  -> Unique cluster_ids removed: {removed_ids_count}")
            print(f"  -> Unique cluster_ids remaining: {remaining_ids_count}")

            # --- 5. Save the new file ---
            output_path = os.path.join(output_folder, filename) # Keep original filename
            
            df_filtered.to_csv(output_path, index=False)
            print(f"  -> Saved filtered file to: {output_path}")
            print("-" * 30)

        except FileNotFoundError:
            print(f"  - Error: File not found at {file_path}")
        except KeyError as ke:
            print(f"  - Error: Missing expected column in {filename}. Details: {ke}")
        except Exception as e:
            print(f"  - An unexpected error occurred while processing {filename}: {e}")

if __name__ == '__main__':
    main()
