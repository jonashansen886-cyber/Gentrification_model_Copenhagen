
import os
import glob
import pandas as pd

# --- Configuration ---
# This script will update the two master files in the 'final_lag' folder.
MASTER_FILES_FOLDER = 'final_lag'

# Define the two "jobs" to run
JOBS = [
    {
        "master_file": "GT_V1_data_finger.csv",
        # Source files for this job are in the temporary folder we just created
        "source_folder": "temp_source_files_for_step3",
        "source_pattern": "*.csv"
    },
    {
        "master_file": "GT_V1_data_cph.csv",
        # Source files for this job are the '_cph_fre' files in the final_lag folder
        "source_folder": "final_lag",
        "source_pattern": "*_cph_fre.csv"
    }
]
# --- End Configuration ---

def main():
    """
    Adds "Final State" (year 2020) features to the master datasets.
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

        source_files = glob.glob(os.path.join(job['source_folder'], job['source_pattern']))
        if not source_files:
            print(f"  - Warning: No source files found for this job in '{job['source_folder']}'")
            continue
        
        print(f"  - Found {len(source_files)} source files to extract 2020 data from.")

        for source_path in source_files:
            try:
                df_source = pd.read_csv(source_path)

                # Check if the '2020' column exists
                if '2020' not in df_source.columns:
                    print(f"    - Skipping {os.path.basename(source_path)}: '2020' column not found.")
                    continue

                # Extract the cluster_id and 2020 value
                df_final_state = df_source[['cluster_id', '2020']].copy()

                # Get the topic from the filename to create a unique new column name
                topic = os.path.basename(source_path).replace('.csv', '').replace('_cph_fre', '')
                if 'cluster_' in topic:
                    topic = topic.replace('cluster_', '')
                
                new_col_name = f"{topic}_2020"
                df_final_state.rename(columns={'2020': new_col_name}, inplace=True)

                # Merge the new feature into the master dataframe
                # Ensure the join key has the same name in both dataframes
                if 'Cluster_id' in df_master.columns and 'cluster_id' in df_final_state.columns:
                    df_final_state.rename(columns={'cluster_id': 'Cluster_id'}, inplace=True)
                    join_key = 'Cluster_id'
                else:
                    join_key = 'cluster_id'

                df_master = pd.merge(df_master, df_final_state, on=join_key, how='left')
            
            except Exception as e:
                print(f"    - Error processing source file {os.path.basename(source_path)}: {e}")

        # Save the updated master file
        df_master.to_csv(master_filepath, index=False)
        print(f"  -> SUCCESS: Updated {job['master_file']} with {len(source_files)} new 'Final State' features.")

    # Clean up the temporary directory
    try:
        print("\nCleaning up temporary source file directory...")
        for f in glob.glob(os.path.join('temp_source_files_for_step3', '*.csv')):
            os.remove(f)
        os.rmdir('temp_source_files_for_step3')
        print("  - Cleanup complete.")
    except Exception as e:
        print(f"  - Warning: Could not clean up temporary directory. {e}")


if __name__ == '__main__':
    main()
