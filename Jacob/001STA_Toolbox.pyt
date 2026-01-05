# -*- coding: utf-8 -*-
"""
Space-Time Analysis Model Builder Toolbox
ArcGIS Pro Toolbox for batch processing multiple CSV files
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
            config = self._get_default_config()
        
        self.clusters_feature = config.get("clusters_feature", "clusters_hovedstad_clean")
        self.csv_folder = config.get("csv_folder", "cph_frb_long")
        self.location_id = config.get("location_id", "cluster_id")
        self.time_field = config.get("time_field", "Timedate")
        self.time_step_interval = config.get("time_step_interval", "1 Years")
        self.cluster_count = config.get("cluster_count", 6)
        self.neighborhood_distance = config.get("neighborhood_distance", "200 Meters")
        self.neighborhood_time_step = config.get("neighborhood_time_step", 1)
        self.number_of_neighbors = config.get("number_of_neighbors", 5)
        self.output_crs = config.get("output_crs", "PROJCS[\"ETRS_1989_UTM_Zone_32N\",GEOGCS[\"GCS_ETRS_1989\",DATUM[\"D_ETRS_1989\",SPHEROID[\"GRS_1980\",6378137.0,298.257222101]],PRIMEM[\"Greenwich\",0.0],UNIT[\"Degree\",0.0174532925199433]],PROJECTION[\"Transverse_Mercator\"],PARAMETER[\"False_Easting\",500000.0],PARAMETER[\"False_Northing\",0.0],PARAMETER[\"Central_Meridian\",9.0],PARAMETER[\"Scale_Factor\",0.9996],PARAMETER[\"Latitude_Of_Origin\",0.0],UNIT[\"Meter\",1.0]]")
        self.scratch_workspace = config.get("scratch_workspace", None)
        self.workspace = config.get("workspace", None)
    
    @staticmethod
    def _get_default_config():
        """Return default configuration dictionary"""
        return {
            "clusters_feature": "clusters_hovedstad_clean",
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


class STAModelBuilder:
    """Generalized Space-Time Analysis Model Builder"""
    
    def __init__(self, config):
        """Initialize with configuration"""
        self.config = config
        arcpy.env.overwriteOutput = False
        
        if config.scratch_workspace and config.workspace:
            self.env_manager = arcpy.EnvManager(
                scratchWorkspace=config.scratch_workspace,
                workspace=config.workspace
            )
        else:
            self.env_manager = None
    
    def create_output_directories(self, base_path="."):
        """Create organized folder structure for outputs"""
        # Convert to absolute path
        if base_path == ".":
            # Use the directory where this script is located (the workspace)
            script_dir = os.path.dirname(os.path.abspath(__file__))
            base_path = script_dir
        else:
            base_path = os.path.abspath(base_path)
        
        folders = {
            "space_time_cube": os.path.join(base_path, "space_time_cube"),
            "emerging_hotspot": os.path.join(base_path, "emerging_hotspot"),
            "time_series_cluster": os.path.join(base_path, "time_series_cluster"),
            "temp_tables": os.path.join(base_path, "temp_tables")
        }
        
        for folder_path in folders.values():
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
                arcpy.AddMessage(f"Created folder: {folder_path}")
        
        # Create temporary geodatabase for tables
        temp_gdb = os.path.join(folders["temp_tables"], "temp_tables.gdb")
        if not os.path.exists(temp_gdb):
            arcpy.management.CreateFileGDB(folders["temp_tables"], "temp_tables.gdb")
            arcpy.AddMessage(f"Created geodatabase: {temp_gdb}")
        
        folders["temp_gdb"] = temp_gdb
        return folders
    
    def get_csv_files(self, csv_folder):
        """Get list of CSV files from folder"""
        # Convert relative path to absolute if needed
        if not os.path.isabs(csv_folder):
            script_dir = os.path.dirname(os.path.abspath(__file__))
            csv_folder = os.path.join(script_dir, csv_folder)
        
        csv_files = []
        if os.path.isdir(csv_folder):
            csv_files = [f for f in os.listdir(csv_folder) if f.endswith('.csv')]
            arcpy.AddMessage(f"Found {len(csv_files)} CSV files in {csv_folder}")
        else:
            arcpy.AddWarning(f"CSV folder not found: {csv_folder}")
        
        return sorted(csv_files)
    
    def extract_variable_name(self, csv_filename):
        """Extract variable name from CSV filename"""
        name = csv_filename.replace('cluster_', '').replace('_long.csv', '')
        return name
    
    def process_csv_file(self, csv_file, output_dirs):
        """Process a single CSV file through the analysis pipeline"""
        
        variable_name = self.extract_variable_name(csv_file)
        arcpy.AddMessage(f"\n{'='*60}")
        arcpy.AddMessage(f"Processing: {variable_name}")
        arcpy.AddMessage(f"{'='*60}")
        
        try:
            csv_path = os.path.join(self.config.csv_folder, csv_file)
            
            # Convert relative path to absolute if needed
            if not os.path.isabs(csv_path):
                script_dir = os.path.dirname(os.path.abspath(__file__))
                csv_path = os.path.join(script_dir, csv_path)
            
            # Convert CSV to table in geodatabase (adds ObjectID automatically)
            arcpy.AddMessage(f"Converting CSV to table...")
            csv_table = os.path.join(
                output_dirs["temp_gdb"],
                f"Table_{variable_name}"
            )
            
            # Use TableToTable with geodatabase path
            arcpy.conversion.TableToTable(csv_path, output_dirs["temp_gdb"], f"Table_{variable_name}")
            arcpy.AddMessage(f"✓ Table created: {csv_table}")
            
            space_time_cube = os.path.join(
                output_dirs["space_time_cube"],
                f"SpaceTC_{variable_name}.nc"
            )
            hotspot_output = os.path.join(
                output_dirs["emerging_hotspot"],
                f"EHA_{variable_name}"
            )
            # Use different names for shapefile and DBF to avoid conflict
            tsc_shp = os.path.join(
                output_dirs["time_series_cluster"],
                f"TSC_{variable_name}"
            )
            tsc_dbf = os.path.join(
                output_dirs["time_series_cluster"],
                f"TSC_{variable_name}_chart"
            )
            
            # Step 1: Create Space-Time Cube
            arcpy.AddMessage(f"Creating space-time cube...")
            arcpy.stpm.CreateSpaceTimeCubeDefinedLocations(
                in_features=self.config.clusters_feature,
                output_cube=space_time_cube,
                location_id=self.config.location_id,
                temporal_aggregation="NO_TEMPORAL_AGGREGATION",
                time_field=self.config.time_field,
                time_step_interval=self.config.time_step_interval,
                variables=[["Value", "SPACE_TIME_NEIGHBORS"]],
                in_related_table=csv_table,
                related_location_id=self.config.location_id
            )
            arcpy.AddMessage(f"✓ Space-time cube created: {space_time_cube}")
            
            # Step 2: Emerging Hot Spot Analysis
            arcpy.AddMessage(f"Running emerging hotspot analysis...")
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
            arcpy.AddMessage(f"✓ Hotspot analysis completed: {hotspot_output}")
            
            # Step 3: Time Series Clustering
            arcpy.AddMessage(f"Running time series clustering...")
            arcpy.stpm.TimeSeriesClustering(
                in_cube=space_time_cube,
                analysis_variable="VALUE_NONE_SPACE_TIME_NEIGHBORS",
                output_features=tsc_shp,
                characteristic_of_interest="VALUE",
                cluster_count=self.config.cluster_count,
                output_table_for_charts=tsc_dbf
            )
            arcpy.AddMessage(f"✓ Time series clustering completed:")
            arcpy.AddMessage(f"  - Shapefile: {tsc_shp}")
            arcpy.AddMessage(f"  - DBF table: {tsc_dbf}")
            
            return True
            
        except Exception as e:
            arcpy.AddError(f"Error processing {variable_name}: {str(e)}")
            return False
    
    def run(self, base_output_path="."):
        """Run the analysis for all CSV files"""
        
        arcpy.AddMessage("\nInitializing Space-Time Analysis...")
        
        output_dirs = self.create_output_directories(base_output_path)
        csv_files = self.get_csv_files(self.config.csv_folder)
        
        if not csv_files:
            arcpy.AddError("No CSV files found. Exiting.")
            return
        
        results = {}
        for csv_file in csv_files:
            variable_name = self.extract_variable_name(csv_file)
            success = self.process_csv_file(csv_file, output_dirs)
            results[variable_name] = success
        
        arcpy.AddMessage(f"\n{'='*60}")
        arcpy.AddMessage("SUMMARY")
        arcpy.AddMessage(f"{'='*60}")
        successful = sum(1 for v in results.values() if v)
        total = len(results)
        arcpy.AddMessage(f"Completed: {successful}/{total} analyses")
        
        for var_name, success in results.items():
            status = "✓" if success else "✗"
            arcpy.AddMessage(f"  {status} {var_name}")


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        self.label = "Space-Time Analysis Tools"
        self.alias = "statools"
        self.tools = [STABatchAnalysisTool]


class STABatchAnalysisTool(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Batch Space-Time Analysis"
        self.description = "Process multiple CSV files through space-time cube, hotspot, and clustering analyses"
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        params = []
        
        # Parameter 0: Output workspace
        param0 = arcpy.Parameter(
            displayName="Output Workspace",
            name="output_workspace",
            datatype="DEFolder",
            parameterType="Required",
            direction="Input"
        )
        param0.value = "."
        params.append(param0)
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been altered."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        output_workspace = parameters[0].valueAsText
        
        # Load configuration
        config = STAAnalysisConfig("sta_config.json")
        
        # Create and run the analysis
        sta_builder = STAModelBuilder(config)
        
        if sta_builder.env_manager:
            with sta_builder.env_manager:
                sta_builder.run(output_workspace)
        else:
            sta_builder.run(output_workspace)
        
        return
