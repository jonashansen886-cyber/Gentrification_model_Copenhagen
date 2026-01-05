# Space-Time Analysis Model Builder

A generalized Python script for ArcGIS Pro that processes multiple CSV files and generates space-time cubes, emerging hotspot analyses, and time series clustering outputs.

## Features

- **Batch Processing**: Automatically processes all CSV files in a specified folder
- **Organized Output**: Creates separate folders for each analysis type:
  - `space_time_cube/` - NetCDF space-time cube files (.nc)
  - `emerging_hotspot/` - Emerging hotspot analysis results
  - `time_series_cluster/` - Time series clustering outputs (.shp and .dbf)
- **Configurable**: Uses a JSON configuration file for easy customization
- **Error Handling**: Graceful error handling with detailed logging

## Setup

### 1. Configuration File

Edit `sta_config.json` with your parameters:

```json
{
  "clusters_feature": "clusters_hovedstad",      // Vector feature name
  "csv_folder": "cph_frb_long",                   // Folder containing CSV files
  "location_id": "cluster_id",                    // ID field to join on
  "time_field": "Timedate",                       // Time field name in CSV
  "time_step_interval": "1 Years",                // Time aggregation interval
  "cluster_count": 6,                             // Number of clusters for TSC
  "neighborhood_distance": "200 Meters",          // Spatial neighborhood
  "neighborhood_time_step": 1,                    // Temporal neighborhood steps
  "number_of_neighbors": 5,                       // Number of neighbors for EHA
  "output_crs": "PROJCS[...]",                    // Output coordinate system
  "scratch_workspace": null,                      // Optional GDB path
  "workspace": null                               // Optional GDB path
}
```

### 2. CSV Folder Structure

Place all your CSV files in the folder specified in `csv_folder`. The script expects:
- Files to be named: `cluster_<variable>_long.csv`
- Each CSV should have columns:
  - `cluster_id` (or your specified location_id)
  - `Timedate` (or your specified time_field)
  - `Value` (the measured variable)

Example files:
- `cluster_unemp_long.csv`
- `cluster_emp_long.csv`
- `cluster_age_18_25_long.csv`

## Usage

### Run the script:

```python
python STA_modelbuilder.py
```

The script will:
1. Create output directories if they don't exist
2. Scan the CSV folder for all .csv files
3. Process each CSV file through:
   - **Step 1**: Create Space-Time Cube
   - **Step 2**: Emerging Hotspot Analysis
   - **Step 3**: Time Series Clustering
4. Display progress and results summary

### Output Structure

```
P7_pyt/
├── space_time_cube/
│   ├── SpaceTC_unemp.nc
│   ├── SpaceTC_emp.nc
│   └── SpaceTC_age_18_25.nc
├── emerging_hotspot/
│   ├── EHA_unemp/
│   ├── EHA_emp/
│   └── EHA_age_18_25/
└── time_series_cluster/
    ├── TSC_unemp.shp
    ├── TSC_unemp.dbf
    ├── TSC_emp.shp
    ├── TSC_emp.dbf
    └── ...
```

## Class Reference

### STAAnalysisConfig

Configuration loader that reads from `sta_config.json` and provides default values.

**Methods:**
- `__init__(config_file)` - Initialize with config file
- `save_template(output_file)` - Generate template configuration

### STAModelBuilder

Main class that orchestrates the analysis pipeline.

**Methods:**
- `__init__(config)` - Initialize with configuration
- `create_output_directories(base_path)` - Create folder structure
- `get_csv_files(csv_folder)` - List all CSV files
- `extract_variable_name(csv_filename)` - Extract variable name from filename
- `process_csv_file(csv_file, output_dirs)` - Process single CSV through all steps
- `run(base_output_path)` - Execute analysis for all CSV files

## Customization

### Modify File Naming Convention

Edit the `extract_variable_name()` method to match your naming convention:

```python
def extract_variable_name(self, csv_filename):
    """Extract variable name from CSV filename"""
    # Current: removes 'cluster_' prefix and '_long.csv' suffix
    name = csv_filename.replace('cluster_', '').replace('_long.csv', '')
    return name
```

### Add Custom Analysis Parameters

Extend the configuration by adding new parameters to `sta_config.json` and the `STAAnalysisConfig` class.

### Change Output Directory Structure

Modify `create_output_directories()` to customize folder layout.

## Troubleshooting

### No CSV files found
- Check that the `csv_folder` path in config is correct
- Verify CSV files are named with `.csv` extension
- Ensure folder exists and contains CSV files

### Analysis fails on specific variable
- Check the CSV file format (ensure `cluster_id`, `Timedate`, and `Value` columns exist)
- Verify the vector feature exists and has the correct field name
- Check coordinate system compatibility

### Missing output files
- Ensure ArcGIS Pro has sufficient permissions to write to output directories
- Verify disk space availability
- Check that workspace settings (if configured) are valid

## Requirements

- ArcGIS Pro with Space-Time Pattern Mining extension
- Python 3.x
- arcpy library (included with ArcGIS Pro)

## Notes

- The script will NOT overwrite existing outputs (set `overwriteOutput = True` if needed)
- Each CSV file is processed independently, so errors in one won't stop others
- Processing time depends on:
  - Number of CSV files
  - Size of vector dataset
  - Temporal resolution and spatial extent
  - Number of clusters for time series clustering
