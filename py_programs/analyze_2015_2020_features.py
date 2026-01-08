import pandas as pd
import os

# --- Configuration ---
INPUT_FILE = r'final_lag/GT_V1_data_cph.csv'
# --- End Configuration ---

def main():
    """
    Analyzes GT_V1_data_cph.csv for presence and NaN counts of 2015-2020 features.
    """
    print(f"Analyzing {os.path.basename(INPUT_FILE)}...")
    try:
        df = pd.read_csv(INPUT_FILE)
        print(f"   - Loaded {len(df)} rows and {len(df.columns)} columns.")
        print("\n   => All Columns in the file:")
        print(df.columns.tolist())

        # Identify all columns related to the 2015-2020 period
        reg_col_pattern = "_reg_2015_2020"
        std_col_pattern = "_std_2015_2020"
        
        # Collect all columns that should represent the 2015-2020 period
        relevant_cols = [col for col in df.columns if reg_col_pattern in col or std_col_pattern in col]

        if not relevant_cols:
            print(f"\n   => No columns containing '{reg_col_pattern}' or '{std_col_pattern}' found.")
        else:
            print(f"\n   => Found {len(relevant_cols)} columns matching 'reg_2015_2020' or 'std_2015_2020':")
            for col in relevant_cols:
                nan_count = df[col].isnull().sum()
                if nan_count == len(df):
                    print(f"      - Column '{col}': ALL NaN ({nan_count} NaNs)")
                elif nan_count > 0:
                    print(f"      - Column '{col}': {nan_count} NaNs")
                else:
                    print(f"      - Column '{col}': No NaNs")
        
        # Also check for _end_value and _start_value columns
        end_value_cols = [col for col in df.columns if col.endswith('_end_value')]
        start_value_cols = [col for col in df.columns if col.endswith('_start_value')]

        if end_value_cols:
            print(f"\n   => Found {len(end_value_cols)} columns ending with '_end_value':")
            for col in end_value_cols:
                nan_count = df[col].isnull().sum()
                if nan_count == len(df):
                    print(f"      - Column '{col}': ALL NaN ({nan_count} NaNs)")
                elif nan_count > 0:
                    print(f"      - Column '{col}': {nan_count} NaNs")
                else:
                    print(f"      - Column '{col}': No NaNs")
        if start_value_cols:
            print(f"\n   => Found {len(start_value_cols)} columns ending with '_start_value':")
            for col in start_value_cols:
                nan_count = df[col].isnull().sum()
                if nan_count == len(df):
                    print(f"      - Column '{col}': ALL NaN ({nan_count} NaNs)")
                elif nan_count > 0:
                    print(f"      - Column '{col}': {nan_count} NaNs")
                else:
                    print(f"      - Column '{col}': No NaNs")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{INPUT_FILE}'")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
