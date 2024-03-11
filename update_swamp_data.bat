:: This batch file runs the multiple Python scripts used to update the data on the SWAMP Data Dashboard
:: For a full data refresh: Because there are multiple file dependencies across scripts, the scripts should be run in a specific order (as outlined below). The main dependency is the datum data. This dataset is used in the data quality assessor for the water quality and habitat data types.
:: For a partial data refresh: Can run one series independently from the others. Run the scripts for a data type in order. Ex. Tox #1, then Tox #2, then Tox #3. Can run this without updating the datum/station data. 
:: For the upload scripts, I inserted 60 second delays between each data file upload to prevent overloading the open data portal's servers with uploading all files at once

@ECHO OFF
@setlocal

set startTime=%time%

:: Activate conda environment (base). Must switch back and forth between conda environments because the "base" environment does not have geopandas installed. If both pandas and geopandas are installed in the same environment, then one could use a single environment and not have to switch between two. Geopandas has some dependencies that are a bit tricky to resolve, so I have it installed in its own environment
:: @CALL "C:\Anaconda-3.7\Scripts\activate.bat" base
:: @CALL "C:\Users\MTang\Miniconda3\Scripts\activate.bat" base

call "C:\ProgramData\anaconda3\Scripts\activate.bat"

call activate base

:: Run tissue scripts before the other scripts (and before sites)
:: We want to use the summary results data, not the raw data
cd ".\data_scripts\tissue"
python "1_tissue_download_data.py"
python "2_tissue_data_quality.py"
python "3_tissue_process_data.py" 

cd "..\sites"
python "0_get_datum_data.py" 

cd "..\water_quality"
python "1_wq_download_data.py"
python "2_wq_data_quality.py"

cd "..\habitat"
python "1_phab_download_data.py"
python "2_phab_data_quality.py"

cd "..\toxicity"
python "1_tox_download_data.py"

cd "..\sites"
python "1_sites_get_data.py"

:: Need to change env for geopandas
call "C:\ProgramData\anaconda3\Scripts\activate.bat" geo_env

python "2_sites_add_region.py"

:: Change back to base
call "C:\ProgramData\anaconda3\Scripts\activate.bat" base

cd "..\water_quality"
python "3_wq_process_data.py"

cd "..\habitat"
python "3_phab_process_data.py"

cd "..\toxicity"
python "2_tox_process_data.py"

:: Upload files

:: Needed for chunked upload to run
@CALL "C:\ProgramData\anaconda3\Scripts\activate.bat" geo_env

cd "..\sites"
python "3_sites_upload_portal.py"
:: Wait 60 seconds
timeout 60 >nul

cd "..\water_quality"
python "4_wq_upload_portal.py"
:: Wait 60 seconds
timeout 60 >nul

cd "..\habitat"
python "4_phab_upload_portal.py"
:: Wait 60 seconds
timeout 60 >nul

cd "..\toxicity"
python "3_tox_upload_portal.py"
timeout 60 >nul

cd "..\tissue"
python "4_tissue_upload_portal.py"

:: Switch back to base environment
@CALL "C:\ProgramData\anaconda3\Scripts\activate.bat" base

echo Start Time: %startTime%
echo Finish Time: %time%

pause > nul