
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
# --- End Configuration ---

def main():
    """
    Adds "Starting State" and "Final State" features to the master datasets.
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
        
        print(f"  - Found {len(source_files)} source files to extract start/end data from.")

        for source_path in source_files:
            try:
                df_source = pd.read_csv(source_path)

                # Identify year columns and find the first and last
                year_cols = sorted([col for col in df_source.columns if col.isdigit()])
                if not year_cols:
                    continue # No year columns in this file
                
                first_year = year_cols[0]
                last_year = '2020'
                if last_year not in df_source.columns:
                    last_year = year_cols[-1] # Fallback to the actual last year if 2020 isn't present

                # Extract the cluster_id, start, and end values
                df_new_features = df_source[['cluster_id', first_year, last_year]].copy()

                # Get the topic from the filename for new column names
                topic = os.path.basename(source_path).replace('.csv', '').replace('_cph_fre', '')
                topic = topic.replace('cluster_', '')
                
                start_col_name = f"{topic}_start_value"
                end_col_name = f"{topic}_end_value"
                
                df_new_features.rename(columns={
                    first_year: start_col_name,
                    last_year: end_col_name
                }, inplace=True)

                # Merge the new features into the master dataframe
                df_master = pd.merge(df_master, df_new_features, on='cluster_id', how='left')
            
            except Exception as e:
                print(f"    - Error processing source file {os.path.basename(source_path)}: {e}")

        # Save the updated master file
        df_master.to_csv(master_filepath, index=False)
        print(f"  -> SUCCESS: Updated {job['master_file']} with {len(source_files)*2} new features.")

    # Clean up the temporary directory
    try:
        print("\nCleaning up temporary source file directory...")
        temp_dir = 'temp_source_files_for_final_features'
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

