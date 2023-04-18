'''
This script uses the CEDEN stations dataset to creates a new dataset of all unique SWAMP monitoring stations in CSV format. It adds a new field: 'LastSampleDate'

LastSampleDate = The most recent sample date for the site found by looking through all records from CEDEN
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    #####  Import data  #####
    ceden_stations_df = p_utils.import_csv('../../support_files/ceden_stations.csv') # Import CEDEN station data from local file

    # Fields needed from CEDEN data files to create new stations dataset
    import_fields = ['StationCode', 'StationName', 'SampleDate', 'TargetLatitude', 'TargetLongitude', 'DataQuality']
    date_fields = ['SampleDate']

    # Add Tissue data when we add the Tissue data type
    print('--- Importing data')
    wq_df = p_utils.import_csv('../../support_files/swamp_wq_data_quality.csv', fields=import_fields, date_cols=date_fields) # Chemistry
    phab_df = p_utils.import_csv('../../support_files/swamp_phab_data_quality.csv', fields=import_fields, date_cols=date_fields) # Habitat
    tox_df = p_utils.import_csv('../../support_files/swamp_tox_data_quality.csv', fields=import_fields, date_cols=date_fields) # Toxicity

    # Concatenate all CEDEN dfs
    data_df = pd.concat([wq_df, phab_df, tox_df], ignore_index=True, sort=True)


    #####  Process data  #####
    # Filter for data quality categories
    data_df = data_df.drop(data_df[~(data_df['DataQuality'].isin(p_constants.dq_categories))].index)

    # Drop data quality column
    data_df.drop('DataQuality', axis=1, inplace=True)

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
    stations_df = pd.concat([stations_df, date_col], 1)

    # Change date format to standard format (open data portal). This format is required in order to query date values using the portal API
    stations_df['SampleDate'] = stations_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Rename "SampleDate" column to "LastSampleDate"
    stations_df = stations_df.rename(columns={'SampleDate': 'LastSampleDate'})

    # Strip whitespace from StationName. For an example of why this is needed, see station: 205PS0365
    stations_df['StationName'] = stations_df['StationName'].apply(lambda x: x.strip())


    #####  Write file  #####
    file_name = 'swamp_stations_without_region'
    outdir = '../../support_files'

    print('--- Writing %s.csv' % file_name)
    p_utils.write_csv(stations_df, file_name, outdir)

    print('%s finished running' % os.path.basename(__file__))
