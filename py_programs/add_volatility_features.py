
import os
import glob
import pandas as pd

# --- Configuration ---
MASTER_FILES_FOLDER = 'final_lag'

JOBS = [
    {
        "master_file": "GT_V1_data_finger.csv",
        "source_folder": "fingerplan_source_files",
        "source_pattern": "*.csv"
    },
    {
        "master_file": "GT_V1_data_cph.csv",
        "source_folder": "final_lag",
        "source_pattern": "*_cph_fre.csv"
    }
]

PERIODS = [
    (1990, 1995), (1995, 2000), (2000, 2005),
    (2005, 2010), (2010, 2015), (2015, 2020)
]
# --- End Configuration ---

def main():
    """
    Adds "Volatility" (standard deviation) features to the master datasets.
    """
    if not os.path.exists(MASTER_FILES_FOLDER):
        print(f"Error: Master files folder '{MASTER_FILES_FOLDER}' not found.")
        return

    for job in JOBS:
        master_filepath = os.path.join(MASTER_FILES_FOLDER, job['master_file'])
        
        try:
            print(f"\n--- Processing master file: {job['master_file']} ---")
            df_master = pd.read_csv(master_filepath)
        except FileNotFoundError:
            print(f"  - Skipping: Master file not found at {master_filepath}")
            continue

        source_files = sorted(glob.glob(os.path.join(job['source_folder'], job['source_pattern'])))
        if not source_files:
            print(f"  - Warning: No source files found for this job in '{job['source_folder']}'")
            continue
        
        print(f"  - Found {len(source_files)} source files to extract volatility data from.")

        for source_path in source_files:
            try:
                df_source = pd.read_csv(source_path)
                
                # --- Create a temporary dataframe for the new volatility features ---
                topic = os.path.basename(source_path).replace('.csv', '').replace('_cph_fre', '').replace('cluster_', '')
                df_volatility_features = df_source[['cluster_id']].copy()

                # --- Calculate volatility for each 5-year period ---
                for start_year, end_year in PERIODS:
                    new_col_name = f"{topic}_std_{start_year}_{end_year}"
                    
                    year_cols = [str(y) for y in range(start_year, end_year + 1)]
                    year_cols_exist = [c for c in year_cols if c in df_source.columns]

                    if len(year_cols_exist) < 2:
                        df_volatility_features[new_col_name] = pd.NA
                    else:
                        # Calculate standard deviation across the year columns for each row
                        df_volatility_features[new_col_name] = df_source[year_cols_exist].std(axis=1)
                
                # --- Merge the new volatility features into the master dataframe ---
                if 'Cluster_id' in df_master.columns and 'cluster_id' in df_volatility_features.columns:
                     df_volatility_features.rename(columns={'cluster_id': 'Cluster_id'}, inplace=True)
                     join_key = 'Cluster_id'
                else:
                    join_key = 'cluster_id'

                df_master = pd.merge(df_master, df_volatility_features, on=join_key, how='left')

            except Exception as e:
                print(f"    - Error processing source file {os.path.basename(source_path)}: {e}")

        # Save the updated master file
        df_master.to_csv(master_filepath, index=False)
        print(f"  -> SUCCESS: Updated {job['master_file']} with {len(source_files) * len(PERIODS)} new 'Volatility' features.")

    # Clean up the temporary directory
    try:
        print("\nCleaning up temporary source file directory...")
        temp_dir = 'temp_source_files_for_volatility'
        # Ensure consistent order for cleanup as well
        files_in_temp = sorted(glob.glob(os.path.join(temp_dir, '*.csv')))
        for f in files_in_temp:
            os.remove(f)
        os.rmdir(temp_dir)
        print("  - Cleanup complete.")
    except Exception as e:
        print(f"  - Warning: Could not clean up temporary directory. {e}")


if __name__ == '__main__':
    main()

