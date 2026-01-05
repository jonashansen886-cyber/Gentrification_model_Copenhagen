@echo off
REM Run STA Model Builder through ArcGIS Pro Python

REM Adjust this path to your ArcGIS Pro installation
set ARCGIS_PYTHON="C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3\python.exe"

REM Run the script
%ARCGIS_PYTHON% "%~dp0STA_modelbuilder.py"

pause
