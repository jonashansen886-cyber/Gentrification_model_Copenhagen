# -*- coding: utf-8 -*-
"""
Generalized Space-Time Analysis Model Builder
This script processes multiple CSV files and generates space-time cubes,
emerging hotspot analyses, and time series clustering outputs.
"""
import arcpy
import os
import json
from pathlib import Path

class STAAnalysisConfig:
    """Configuration class for STA analysis parameters"""
    def __init__(self, config_file="sta_config.json"):
        """Load configuration from JSON file"""
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        else:
            # Default configuration
            config = self._get_default_config()
        
        # Analysis parameters
        self.clusters_feature = config.get("clusters_feature", "clusters_hovedstad")
        self.csv_folder = config.get("csv_folder", "cph_frb_long")
        self.location_id = config.get("location_id", "cluster_id")
        self.time_field = config.get("time_field", "Timedate")
        self.time_step_interval = config.get("time_step_interval", "1 Years")
        self.cluster_count = config.get("cluster_count", 6)
        self.neighborhood_distance = config.get("neighborhood_distance", "200 Meters")
        self.neighborhood_time_step = config.get("neighborhood_time_step", 1)
        self.number_of_neighbors = config.get("number_of_neighbors", 5)
        
        # Output coordinate system
        self.output_crs = config.get("output_crs", "PROJCS[\"ETRS_1989_UTM_Zone_32N\",GEOGCS[\"GCS_ETRS_1989\",DATUM[\"D_ETRS_1989\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",9.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]")
        
        # Workspace settings
        self.scratch_workspace = config.get("scratch_workspace", None)
        self.workspace = config.get("workspace", None)
    
    @staticmethod
    def _get_default_config():
        """Return default configuration dictionary"""
        return {
            "clusters_feature": "clusters_hovedstad",
            "csv_folder": "cph_frb_long",
            "location_id": "cluster_id",
            "time_field": "Timedate",
            "time_step_interval": "1 Years",
            "cluster_count": 6,
            "neighborhood_distance": "200 Meters",
            "neighborhood_time_step": 1,
            "number_of_neighbors": 5,
            "output_crs": "PROJCS[\"ETRS_1989_UTM_Zone_32N\",GEOGCS[\"GCS_ETRS_1989\",DATUM[\"D_ETRS_1989\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",9.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]"
        }
    
    def save_template(self, output_file="sta_config_template.json"):
        """Save a template configuration file"""
        with open(output_file, 'w') as f:
            json.dump(self._get_default_config(), f, indent=2)


class STAModelBuilder:
    """Generalized Space-Time Analysis Model Builder"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        arcpy.env.overwriteOutput = False
        
        # Set workspace environments if provided
        if config.scratch_workspace and config.workspace:
            self.env_manager = arcpy.EnvManager(
                scratchWorkspace=config.scratch_workspace,
                workspace=config.workspace
            )
        else:
            self.env_manager = None
    
    def create_output_directories(self, base_path="."):
        """Create organized folder structure for outputs"""
        folders = {
            "space_time_cube": os.path.join(base_path, "space_time_cube"),
            "emerging_hotspot": os.path.join(base_path, "emerging_hotspot"),
            "time_series_cluster": os.path.join(base_path, "time_series_cluster")
        }
        
        for folder_path in folders.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                print(f"Created folder: {folder_path}")
        
        return folders
    
    def get_csv_files(self, csv_folder):
        """Get list of CSV files from folder"""
        csv_files = []
        if os.path.isdir(csv_folder):
            csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
            print(f"Found {len(csv_files)} CSV files in {csv_folder}")
        else:
            print(f"Warning: CSV folder not found: {csv_folder}")
        
        return sorted(csv_files)
    
    def extract_variable_name(self, csv_filename):
        """Extract variable name from CSV filename"""
        # Remove 'cluster_' prefix and '_long.csv' suffix
        name = csv_filename.replace('cluster_', '').replace('_long.csv', '')
        return name
    
    def process_csv_file(self, csv_file, output_dirs):
        """Process a single CSV file through the analysis pipeline"""
        
        variable_name = self.extract_variable_name(csv_file)
        print(f"\n{'='*60}")
        print(f"Processing: {variable_name}")
        print(f"{'='*60}")
        
        try:
            # Construct file paths
            csv_path = os.path.join(self.config.csv_folder, csv_file)
            space_time_cube = os.path.join(
                output_dirs["space_time_cube"],
                f"SpaceTC_{variable_name}.nc"
            )
            hotspot_output = os.path.join(
                output_dirs["emerging_hotspot"],
                f"EHA_{variable_name}"
            )
            tsc_shp = os.path.join(
                output_dirs["time_series_cluster"],
                f"TSC_{variable_name}.shp"
            )
            tsc_dbf = os.path.join(
                output_dirs["time_series_cluster"],
                f"TSC_{variable_name}.dbf"
            )
            
            # Step 1: Create Space-Time Cube
            print(f"Creating space-time cube...")
            arcpy.stpm.CreateSpaceTimeCubeDefinedLocations(
                in_features=self.config.clusters_feature,
                output_cube=space_time_cube,
                location_id=self.config.location_id,
                temporal_aggregation="NO_TEMPORAL_AGGREGATION",
                time_field=self.config.time_field,
                time_step_interval=self.config.time_step_interval,
                variables=[["Value", "SPACE_TIME_NEIGHBORS"]],
                in_related_table=csv_path,
                related_location_id=self.config.location_id
            )
            print(f"✓ Space-time cube created: {space_time_cube}")
            
            # Step 2: Emerging Hot Spot Analysis
            print(f"Running emerging hotspot analysis...")
            with arcpy.EnvManager(outputCoordinateSystem=self.config.output_crs):
                arcpy.stpm.EmergingHotSpotAnalysis(
                    in_cube=space_time_cube,
                    analysis_variable="VALUE_NONE_SPACE_TIME_NEIGHBORS",
                    output_features=hotspot_output,
                    neighborhood_distance=self.config.neighborhood_distance,
                    neighborhood_time_step=self.config.neighborhood_time_step,
                    conceptualization_of_spatial_relationships="FIXED_DISTANCE",
                    number_of_neighbors=self.config.number_of_neighbors,
                    define_global_window="ENTIRE_CUBE"
                )
            print(f"✓ Hotspot analysis completed: {hotspot_output}")
            
            # Step 3: Time Series Clustering
            print(f"Running time series clustering...")
            arcpy.stpm.TimeSeriesClustering(
                in_cube=space_time_cube,
                analysis_variable="VALUE_NONE_SPACE_TIME_NEIGHBORS",
                output_features=tsc_shp,
                characteristic_of_interest="VALUE",
                cluster_count=self.config.cluster_count,
                output_table_for_charts=tsc_dbf
            )
            print(f"✓ Time series clustering completed:")
            print(f"  - Shapefile: {tsc_shp}")
            print(f"  - DBF table: {tsc_dbf}")
            
            return True
            
        except Exception as e:
            print(f"✗ Error processing {variable_name}: {str(e)}")
            return False
    
    def run(self, base_output_path="."):
        """Run the analysis for all CSV files"""
        
        print("\nInitializing Space-Time Analysis...")
        
        # Create output directories
        output_dirs = self.create_output_directories(base_output_path)
        
        # Get CSV files
        csv_files = self.get_csv_files(self.config.csv_folder)
        
        if not csv_files:
            print("No CSV files found. Exiting.")
            return
        
        # Process each CSV file
        results = {}
        for csv_file in csv_files:
            variable_name = self.extract_variable_name(csv_file)
            success = self.process_csv_file(csv_file, output_dirs)
            results[variable_name] = success
        
        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY")
        print(f"{'='*60}")
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        print(f"Completed: {successful}/{total} analyses")
        
        for var_name, success in results.items():
            status = "✓" if success else "✗"
            print(f"  {status} {var_name}")


def main():
    """Main entry point"""
    
    # Load configuration
    config = STAAnalysisConfig("sta_config.json")
    
    # Create and run the analysis
    sta_builder = STAModelBuilder(config)
    
    # Use environment manager if workspace settings are configured
    if sta_builder.env_manager:
        with sta_builder.env_manager:
            sta_builder.run()
    else:
        sta_builder.run()


if __name__ == '__main__':
    main()
