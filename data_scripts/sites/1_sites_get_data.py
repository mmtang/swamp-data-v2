'''
Step 1: This script uses the CEDEN stations dataset to create a new dataset of all unique SWAMP monitoring stations in CSV format. It adds a new field: 'LastSampleDate'

LastSampleDate = The most recent sample date for the site based on all queried records from CEDEN

Important: Running this script draws upon the most recent data files saved for water quality, habitat, toxicity, and tissue data. To ensure that the output reflects the most recent data available, run all of the scripts to produce the exported file outputs named in lines 37-41 *before* running this script.

Updated: 03/14/2024 
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '..\\utils\\')
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    #####  Import data  #####
    # Import data from previous script
    ceden_stations_df = p_utils.import_csv('../../support_files/ceden_stations.csv') 

    # Select the fields needed from the CEDEN data files to create new stations dataset
    import_fields = ['StationCode', 'StationName', 'SampleDate', 'TargetLatitude', 'TargetLongitude', 'DataQuality']
    import_fields_tissue = ['StationCode', 'StationName', 'LastSampleDate', 'TargetLatitude', 'TargetLongitude']
    date_fields = ['SampleDate']
    tissue_date_fields = ['LastSampleDate']

    # Import all of the other data types
    # Important: Add Tissue data when we add the Tissue data type
    print('--- Importing data')
    wq_df = p_utils.import_csv('../../support_files/swamp_wq_data_quality.csv', fields=import_fields, date_cols=date_fields) # Chemistry
    phab_df = p_utils.import_csv('../../support_files/swamp_phab_data_quality.csv', fields=import_fields, date_cols=date_fields) # Habitat
    tox_df = p_utils.import_csv('../../support_files/swamp_tox_data_quality.csv', fields=import_fields, date_cols=date_fields) # Toxicity
    ##### Add this for tissue
    #tissue_df = p_utils.import_csv('../../support_files/swamp_tissue_summary_data.csv', fields=import_fields_tissue, date_cols=tissue_date_fields) # Tissue

    ##### Add this for tissue
    # Rename tissue date field to match other CEDEN df
    #tissue_df = tissue_df.rename(columns={'LastSampleDate' : 'SampleDate'})

    # Concatenate all CEDEN dfs except Tissue
    data_df = pd.concat([wq_df, phab_df, tox_df], ignore_index=True, sort=True)


    #####  Process data 
    # Filter for data quality categories
    data_df = data_df.drop(data_df[~(data_df['DataQuality'].isin(p_constants.dq_categories))].index)

    # Drop data quality column
    data_df.drop('DataQuality', axis=1, inplace=True)

    ##### Add this for tissue
    # Add in the tissue dataset
    #data_df = pd.concat([data_df, tissue_df], ignore_index=True, sort=True)

    # Drop FieldQA station code
    data_df = data_df.drop(data_df[data_df['StationCode'] == 'FIELDQA_SWAMP'].index)

    # Drop stations with null latitude or longitude coordinates
    data_df = data_df.drop(data_df[(data_df['TargetLatitude'].isna()) | (data_df['TargetLongitude'].isna())].index)

    # Sort by sample date descending. We want the most recent date for each station. These values will populate the Last Sample Date field
    data_df.sort_values('SampleDate', ascending=False, inplace=True)

    # Remove duplicate records using Station Code. The keep option will keep the first duplicate record found (the one with the most recent sample date) and drop the others
    stations_df = data_df.drop_duplicates(subset=['StationCode'], keep='first')

    # Move the date column to the end so that it appears last
    date_col = stations_df.pop('SampleDate')
    stations_df = pd.concat([stations_df, date_col], axis=1)

    # Change date format to the standard format for the open data portal. This format is required in order to query date values using the portal API
    stations_df['SampleDate'] = stations_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Rename "SampleDate" column to "LastSampleDate"
    stations_df = stations_df.rename(columns={'SampleDate': 'LastSampleDate'})

    # Strip whitespace from StationName. For an example of why this is needed, see station: 205PS0365
    stations_df['StationName'] = stations_df['StationName'].apply(lambda x: x.strip())

    
    #####  Write file
    file_name = 'swamp_stations_without_region'
    outdir = '../../support_files'

    print('--- Writing %s.csv' % file_name)
    p_utils.write_csv(stations_df, file_name, outdir)

    print('%s finished running' % os.path.basename(__file__))
    
