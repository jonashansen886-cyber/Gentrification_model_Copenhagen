
import os
import glob
import pandas as pd
import numpy as np

# --- Configuration ---
INPUT_FOLDER = 'data/raw/long_format_csv'
OUTPUT_FILE = 'data/raw/GT_V4_data.csv'

# Define the 10-year periods
PERIODS = [
    (1990, 2000), (2000, 2010), (2010, 2020)
]

START_YEAR = 1990
END_YEAR = 2020
# --- End Configuration ---

def process_file(file_path):
    """
    Processes a single long-format CSV file to extract features.
    """
    filename = os.path.basename(file_path)
    topic = filename.replace('cluster_', '').replace('_long.csv', '')
    
    print(f"  - Processing topic: {topic}")
    
    try:
        df_long = pd.read_csv(file_path)
        
        # Ensure Timedate is just the year for easier pivoting
        df_long['year'] = df_long['Timedate'].str[:4].astype(int)
        
        # Pivot to wide format: cluster_id as rows, years as columns
        df_wide = df_long.pivot(index='cluster_id', columns='year', values='Value')
        
        features = pd.DataFrame(index=df_wide.index)
        
        # --- 1. Calculate 10-year percentage change features ---
        for start, end in PERIODS:
            col_name = f'{topic}_reg_{start}_{end}'
            
            if start in df_wide.columns and end in df_wide.columns:
                start_vals = df_wide[start]
                end_vals = df_wide[end]
                
                # Calculate percentage change, handling zeros
                percent_change = pd.Series(index=df_wide.index, dtype=float)
                valid_mask = start_vals.notna() & end_vals.notna() & (start_vals != 0)
                percent_change[valid_mask] = ((end_vals[valid_mask] - start_vals[valid_mask]) / start_vals[valid_mask]) * 100
                features[col_name] = percent_change
            else:
                features[col_name] = np.nan

        # --- 2. Add Start and End Values ---
        start_col = f'{topic}_start_value'
        end_col = f'{topic}_end_value'
        
        features[start_col] = df_wide[START_YEAR] if START_YEAR in df_wide.columns else np.nan
        features[end_col] = df_wide[END_YEAR] if END_YEAR in df_wide.columns else np.nan
        
        # --- 3. Calculate 10-year Volatility (std deviation) ---
        for start, end in PERIODS:
            col_name = f'{topic}_std_{start}_{end}'
            
            # Identify columns within the period
            period_cols = [c for c in df_wide.columns if start <= c <= end]
            
            if len(period_cols) >= 2:
                features[col_name] = df_wide[period_cols].std(axis=1)
            else:
                features[col_name] = np.nan
                
        return features

    except Exception as e:
        print(f"    - Failed to process {filename}. Error: {e}")
        return None

def main():
    print(f"Starting creation of {OUTPUT_FILE}...")
    
    all_csvs = glob.glob(os.path.join(INPUT_FOLDER, "cluster_*_long.csv"))
    if not all_csvs:
        print(f"No input files found in {INPUT_FOLDER}")
        return

    all_features = []
    
    for file_path in sorted(all_csvs):
        features = process_file(file_path)
        if features is not None:
            all_features.append(features)
            
    if not all_features:
        print("No features were extracted. Aborting.")
        return
        
    print("\nMerging all features...")
    # Start with the first one
    final_df = all_features[0]
    
    # Merge the rest
    for next_df in all_features[1:]:
        final_df = final_df.merge(next_df, left_index=True, right_index=True, how='outer')
        
    # Reset index to have cluster_id as a column
    final_df.reset_index(inplace=True)
    
    # Save the result
    final_df.to_csv(OUTPUT_FILE, index=False)
    print(f"\nSUCCESS: Created {OUTPUT_FILE}")
    print(f"Final shape: {final_df.shape}")

if __name__ == '__main__':
    main()
