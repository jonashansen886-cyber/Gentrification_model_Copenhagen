
import os
import glob

# --- Configuration ---
folder_path = 'final_lag'
# --- End Configuration ---

def main():
    """
    Cleans up the specified folder by removing original and doubly-processed CSV files,
    leaving only the correctly filtered '_cph_fre.csv' files.
    """
    try:
        print(f"Cleaning up duplicate files in '{folder_path}'...")
        all_csvs = glob.glob(os.path.join(folder_path, "*.csv"))
        
        files_to_delete = []
        files_to_keep_count = 0

        # Identify which files to delete and which to keep
        for file_path in all_csvs:
            filename = os.path.basename(file_path)
            # Mark doubly-processed files for deletion
            if '_cph_fre_cph_fre.csv' in filename:
                files_to_delete.append(file_path)
            # Mark original files (which don't have the suffix) for deletion
            elif '_cph_fre.csv' not in filename:
                files_to_delete.append(file_path)
            else:
                # This is a file we want to keep
                files_to_keep_count += 1
        
        if not files_to_delete:
            print("No duplicate files found to delete.")
            return

        # Delete the identified files
        print(f"Found {len(files_to_delete)} files to delete...")
        deleted_count = 0
        for file_path in files_to_delete:
            try:
                os.remove(file_path)
                print(f"  - Deleted: {os.path.basename(file_path)}")
                deleted_count += 1
            except Exception as e:
                print(f"  - Error deleting {os.path.basename(file_path)}: {e}")
        
        print(f"\nCleanup complete. Deleted {deleted_count} files.")
        print(f"{files_to_keep_count} correctly filtered files remain.")

    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main()
