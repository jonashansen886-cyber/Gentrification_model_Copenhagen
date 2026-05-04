
import os
import glob
import pandas as pd

# Configuration
INPUT_FOLDER = 'data/raw/long_format_csv'
OUTPUT_FOLDER = 'data/raw/long_format_csv'

def melt_csv(file_path):
    filename = os.path.basename(file_path)
    if filename.endswith('_long.csv'):
        return

    print(f"Processing: {filename}")
    try:
        df = pd.read_csv(file_path)
        
        # Identification column is 'cluster_id'
        if 'cluster_id' not in df.columns:
            print(f"  - Warning: 'cluster_id' not found in {filename}. Skipping.")
            return
            
        # The years are columns. Let's melt them.
        # id_vars='cluster_id', value_vars = all other columns
        value_vars = [col for col in df.columns if col != 'cluster_id']
        
        df_long = pd.melt(df, id_vars=['cluster_id'], value_vars=value_vars, 
                          var_name='Timedate', value_name='Value')
        
        # Convert Timedate from 'YYYY' to 'YYYY-01-01'
        df_long['Timedate'] = df_long['Timedate'].apply(lambda x: f"{x}-01-01")
        
        # Sort by Timedate (as string is fine since it's YYYY-MM-DD) and then cluster_id
        # Actually, let's ensure cluster_id is sorted nicely too.
        df_long = df_long.sort_values(by=['Timedate', 'cluster_id'])
        
        # Save output
        base_name = filename.replace('.csv', '')
        output_filename = f"{base_name}_long.csv"
        output_path = os.path.join(OUTPUT_FOLDER, output_filename)
        
        df_long.to_csv(output_path, index=False)
        print(f"  -> SUCCESS: Saved {output_filename}")
        
    except Exception as e:
        print(f"  - Error processing {filename}: {e}")

def main():
    print("Starting CSV melting process...")
    all_csvs = glob.glob(os.path.join(INPUT_FOLDER, "*.csv"))
    
    # Filter out already melted files
    to_process = [f for f in all_csvs if not f.endswith('_long.csv')]
    
    for file_path in to_process:
        melt_csv(file_path)
        
    print("\nCSV melting finished.")

if __name__ == '__main__':
    main()
