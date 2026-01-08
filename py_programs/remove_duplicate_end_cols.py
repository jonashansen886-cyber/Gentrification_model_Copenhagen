
import os
import pandas as pd
import glob

# --- Configuration ---
MASTER_FILES_FOLDER = 'final_lag'
MASTER_FILE_PATTERNS = ["GT_V1_data_finger.csv", "GT_V1_data_cph.csv"]
# --- End Configuration ---

def main():
    """
    Removes redundant '_2020' columns from specified master CSV files.
    """
    print("Starting removal of redundant '_2020' columns...")

    for master_filename in MASTER_FILE_PATTERNS:
        master_filepath = os.path.join(MASTER_FILES_FOLDER, master_filename)
        
        try:
            print(f"\n--- Processing master file: {master_filename} ---")
            df_master = pd.read_csv(master_filepath)
            
            # Identify only the redundant columns named like 'topic_2020'
            # These are typically non-reg/std features, derived from the year '2020' only.
            # We want to keep _reg_2015_2020, _std_2015_2020, _end_value.
            # The redundant ones are those that just end in _2020 from add_final_state_features.py
            cols_to_drop = [col for col in df_master.columns 
                            if col.endswith('_2020') and not ('_reg_' in col or '_std_' in col)]
            
            if cols_to_drop:
                print(f"  - Found {len(cols_to_drop)} columns to remove: {cols_to_drop}")
                df_master.drop(columns=cols_to_drop, inplace=True)
                print(f"  - Remaining columns: {len(df_master.columns)}")
                
                # Save the modified DataFrame, overwriting the original file
                df_master.to_csv(master_filepath, index=False)
                print(f"  -> SUCCESS: Updated {master_filename} with redundant columns removed.")
            else:
                print(f"  - No redundant '_2020' columns found in {master_filename}.")

        except FileNotFoundError:
            print(f"  - Skipping: Master file not found at {master_filepath}")
        except Exception as e:
            print(f"  - Error processing {master_filename}: {e}")

    print("\nCleanup of redundant columns finished.")


if __name__ == '__main__':
    main()
