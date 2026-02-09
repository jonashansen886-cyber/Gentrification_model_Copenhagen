
import os
import pandas as pd
import numpy as np

# --- Configuration ---
FOLDER_PATH = 'final_lag'
FILES_TO_REPLICATE = [
    "GT_V1_data_finger.csv",
    "GT_V1_data_cph.csv",
    "GT_V2_data_finger.csv",
    "GT_V2_data_cph.csv"
]
# --- End Configuration ---

def main():
    """
    Creates dummy versions of specified CSV files, replacing data with random 0s and 1s.
    """
    print("Starting creation of dummy datasets...")

    for filename in FILES_TO_REPLICATE:
        input_path = os.path.join(FOLDER_PATH, filename)
        
        base_name, ext = os.path.splitext(filename)
        output_filename = f"{base_name}_dummy{ext}"
        output_path = os.path.join(FOLDER_PATH, output_filename)

        try:
            print(f"\n--- Processing: {filename} ---")
            df_original = pd.read_csv(input_path)
            df_dummy = df_original.copy()

            # Identify the ID column (handling potential case differences)
            id_col = None
            if 'cluster_id' in df_dummy.columns:
                id_col = 'cluster_id'
            elif 'Cluster_id' in df_dummy.columns:
                id_col = 'Cluster_id'
            
            if id_col is None:
                print("  - Warning: No 'cluster_id' or 'Cluster_id' column found. Skipping.")
                continue

            # Identify all columns to be replaced with dummy data
            cols_to_replace = [col for col in df_dummy.columns if col != id_col]
            
            # Replace data in each column with random 0s and 1s
            for col in cols_to_replace:
                df_dummy[col] = np.random.randint(0, 2, size=len(df_dummy))
            
            # Save the dummy file
            df_dummy.to_csv(output_path, index=False)
            print(f"  -> SUCCESS: Created dummy file: {output_filename}")

        except FileNotFoundError:
            print(f"  - Error: Source file not found at {input_path}")
        except Exception as e:
            print(f"  - An unexpected error occurred: {e}")

    print("\nDummy dataset creation finished.")


if __name__ == '__main__':
    main()
