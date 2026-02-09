
import os
import glob
import pandas as pd
import numpy as np

# --- Configuration ---
INPUT_FOLDER = 'final_lag'
OUTPUT_FOLDER = 'final_lag'

# Define the 5-year periods
PERIODS = [
    (1990, 1995), (1995, 2000), (2000, 2005),
    (2005, 2010), (2010, 2015), (2015, 2020)
]
# --- End Configuration ---

def process_and_combine(file_list, output_filename):
    """
    Processes a list of CSV files to calculate 5-year percentage changes,
    then combines them into a single master CSV file.
    """
    if not file_list:
        print(f"No files to process for output: {output_filename}")
        return

    print(f"\n--- Processing group for: {output_filename} ---")
    dataframes_to_merge = []

    for file_path in file_list:
        filename = os.path.basename(file_path)
        print(f"  - Calculating features for: {filename}")
        
        try:
            df = pd.read_csv(file_path)
            
            # --- 1. Calculate 5-year change features ---
            for start_year, end_year in PERIODS:
                col_name = f'reg_{start_year}_{end_year}'
                
                start_val_series = df.get(str(start_year))
                end_val_series = df.get(str(end_year))
                
                # Calculate percentage change, handling NaNs and division by zero
                # Start with NaNs
                percent_change = pd.Series([np.nan] * len(df))
                
                if start_val_series is not None and end_val_series is not None:
                    # Create masks for valid calculation
                    valid_mask = start_val_series.notna() & end_val_series.notna() & (start_val_series != 0)
                    # Calculate where possible
                    percent_change.loc[valid_mask] = ((end_val_series.loc[valid_mask] - start_val_series.loc[valid_mask]) / start_val_series.loc[valid_mask]) * 100
                
                df[col_name] = percent_change

            # --- 2. Prepare for merge ---
            # Keep only the ID and the new feature columns
            feature_cols = [col for col in df.columns if col.startswith('reg_')]
            df_features = df[['cluster_id'] + feature_cols]
            
            # Get the topic name from filename
            topic = filename.replace('.csv', '').replace('_cph_fre', '')
            if 'cluster_' in topic:
                topic = topic.replace('cluster_', '')

            # Rename feature columns with the topic
            rename_dict = {col: f"{topic}_{col}" for col in feature_cols}
            df_features.rename(columns=rename_dict, inplace=True)
            
            dataframes_to_merge.append(df_features)

        except Exception as e:
            print(f"    - Failed to process {filename}. Error: {e}")

    # --- 3. Merge all processed dataframes for the group ---
    if not dataframes_to_merge:
        print("No dataframes were successfully processed. Aborting merge.")
        return

    print(f"  - Merging {len(dataframes_to_merge)} processed files...")
    # Start with the first dataframe as the base
    merged_df = dataframes_to_merge[0]

    # Iteratively merge the rest
    for df_to_merge in dataframes_to_merge[1:]:
        merged_df = pd.merge(merged_df, df_to_merge, on='cluster_id', how='outer')

    # --- 4. Save the final combined file ---
    output_path = os.path.join(OUTPUT_FOLDER, output_filename)
    try:
        merged_df.to_csv(output_path, index=False)
        print(f"  -> SUCCESS: Created combined file: {output_filename}")
        print(f"     ({len(merged_df)} rows, {len(merged_df.columns)} columns)")
    except Exception as e:
        print(f"  -> FAILED to save merged file. Error: {e}")


def main():
    """
    Main function to orchestrate the entire process for Step 3.
    """
    all_csvs = sorted(glob.glob(os.path.join(INPUT_FOLDER, "*.csv")))

    # Exclude any previous final outputs from being processed
    all_csvs = [f for f in all_csvs if not os.path.basename(f).startswith('GT_V1_') and not os.path.basename(f).startswith('GT_V2_')]

    # Group files based on their suffix (from the now sorted list)
    fingerplan_files = sorted([f for f in all_csvs if not f.endswith('_cph_fre.csv')])
    cph_files = sorted([f for f in all_csvs if f.endswith('_cph_fre.csv')])

    # Process the first group
    process_and_combine(fingerplan_files, 'GT_V1_data_finger.csv')

    # Process the second group
    process_and_combine(cph_files, 'GT_V1_data_cph.csv')

    print("\nStep 3 finished.")


if __name__ == '__main__':
    main()
