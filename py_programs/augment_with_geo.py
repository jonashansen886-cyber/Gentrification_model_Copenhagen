import os
import pandas as pd
import geopandas as gpd


def main():
    # Define workspace-relative paths
    base_dir = os.path.dirname(os.path.dirname(__file__))
    data_raw_dir = os.path.join(base_dir, "data", "raw")
    shapefile_path = os.path.join(
        data_raw_dir, "neighborhood_shapefile", "Nabolag_cph_fre_new.shp"
    )
    csv_path = os.path.join(data_raw_dir, "GT_V1_data_cph.csv")

    # Output path
    processed_dir = os.path.join(base_dir, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    output_path = os.path.join(processed_dir, "GT_V1_data_cph_geo.csv")

    # 1. Load the Data
    print(f"Reading shapefile from: {shapefile_path}")
    print(f"Reading CSV from: {csv_path}")
    gdf = gpd.read_file(shapefile_path)
    df = pd.read_csv(csv_path)
    print(f"Shapefile rows: {len(gdf)}, CSV rows: {len(df)}")
    print(f"Shapefile columns: {list(gdf.columns)}")
    print(f"CSV columns: {list(df.columns)}")

    # Optional: report CRS for awareness (no reprojection applied here)
    try:
        print(f"Original Shapefile CRS: {gdf.crs}")
    except Exception:
        print("Original Shapefile CRS: unavailable")

    # Reproject to metric CRS for Denmark (EPSG:25832) before centroid
    try:
        gdf = gdf.to_crs("EPSG:25832")
        print(f"Reprojected Shapefile CRS: {gdf.crs}")
    except Exception as e:
        raise RuntimeError(f"Failed to reproject shapefile to EPSG:25832: {e}")

    # 2. Extract Coordinates from the Shapefile (centroids)
    # Ensure geometry is set and valid; compute centroid
    if gdf.geometry is None:
        raise ValueError("Shapefile does not contain a geometry column.")

    centroids = gdf.geometry.centroid
    gdf["x_coord"] = centroids.x
    gdf["y_coord"] = centroids.y
    # Record CRS used for coordinates (metadata only; not persisted to CSV)
    coords_crs_meta = str(gdf.crs)
    print("Computed centroids and coordinate columns.")
    print(f"Coordinate CRS (metadata): {coords_crs_meta}")

    # 3. Prepare a Smaller DataFrame for Merging
    # Detect shapefile key column. Prefer explicit 'munic_clus' or 'cluster_id'.
    key_col = None
    if "munic_clus" in gdf.columns:
        key_col = "munic_clus"
    elif "cluster_id" in gdf.columns:
        key_col = "cluster_id"
    else:
        # Case-insensitive exact match for either
        exact_ci = [c for c in gdf.columns if c.lower() in ("munic_clus", "cluster_id")]
        if len(exact_ci) > 0:
            key_col = exact_ci[0]
        else:
            # Heuristic: any column containing 'munic' or 'cluster'
            heuristic = [
                c
                for c in gdf.columns
                if ("munic" in c.lower()) or ("cluster" in c.lower())
            ]
            if len(heuristic) > 0:
                key_col = heuristic[0]
                print(
                    f"INFO: Using shapefile key column by heuristic match: '{key_col}'"
                )
            else:
                raise KeyError(
                    "Could not find a join key in shapefile. Expected 'munic_clus' or 'cluster_id' (or a column containing 'munic'/'cluster'). "
                    f"Available columns: {list(gdf.columns)}"
                )

    # Do not include CRS column in merge output; keep as runtime metadata
    coords_df = gdf[[key_col, "x_coord", "y_coord"]].copy()
    print(f"Using shapefile key column: {key_col}")

    # 4. Standardize the Join Column
    coords_df.rename(columns={key_col: "Cluster_id"}, inplace=True)

    # Also standardize the primary CSV join column case-insensitively
    if "Cluster_id" not in df.columns:
        df_key_matches = [c for c in df.columns if c.lower() == "cluster_id"]
        if df_key_matches:
            df.rename(columns={df_key_matches[0]: "Cluster_id"}, inplace=True)
            print(f"Renamed CSV key column from '{df_key_matches[0]}' to 'Cluster_id'.")
        else:
            raise KeyError(
                "Expected 'Cluster_id' column in primary CSV (case-insensitive match allowed)."
            )

    # 5. Merge the Coordinates into the Primary Dataset (left join)
    df_merged = df.merge(coords_df, on="Cluster_id", how="left")
    print(
        f"Merged rows: {len(df_merged)}. Coordinates joined for {df_merged['x_coord'].notna().sum()} rows."
    )

    # 6. Save the Final Result
    df_merged.to_csv(output_path, index=False)

    # 7. Final Verification
    print(df_merged.head())
    print(f"Saved merged dataset to: {output_path}")


if __name__ == "__main__":
    main()
