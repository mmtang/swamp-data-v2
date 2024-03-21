# SWAMP Data

## About

A collection of Python scripts used to process and analyze data for the SWAMP Data Dashboard (https://github.com/mmtang/swamp-data-dashboard). 

## Data Sources

All SWAMP data used in these scripts and displayed on the SWAMP Data Dashboard are sourced from the California Environmental Data Exchange Network (CEDEN) (https://ceden.org/). The data types include Water Quality, Habitat, Toxicity, and Tissue.

## Usage

Run the update_swamp_data.bat file to update all datasets. The batch script runs all scripts in a specific order because of different file dependencies needed for certain operations. For more information, please review the notes at the top of each individual script file.

These scripts query data from an internal data mart and therefore might not run on your computer if you do not have access to this data mart or if you do not change the connection variables to access the platform using your own account (see *p_constants.py*).

If you wish to update one data type (e.g., water quality, toxicity, tissue) at a time, then run the scripts in the folder in ascending order (ex. 1, 2, 3, 4). You may need to run the first script in the sites folder, 0_get_datum_data.py, before running these scripts. Please review the notes at the top of each individual script file.

## Requirements

The following Python packages are required:

- pandas
- pyodbc - Used for querying CEDEN data from the internal data mart
- statsmodels - Used for calculating length-adjusted averages for tissue data

The following packages are optional and used for uploading the datasets to the California Open Data Portal (https://data.ca.gov/).

- requests (optional)
- requests-toolbox (optional)
- ckanapi (optional)
