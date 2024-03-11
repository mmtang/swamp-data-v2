'''
Step 2: This script adds the DataQuality and DataQualityIndicator fields to the SWAMP tissue dataset.

Updated: 02/29/2024 
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py
import p_utils_dq # p_utils_dq.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    # Added "na_values" and "keep_default_na" parameters to deal with "AttributeError: 'float' object has no attribute 'split'" error in DQ functions
    tissue_df = pd.read_csv('../../support_files/ceden_swamp_tissue.csv', parse_dates=p_constants.tissue_date_cols, na_values=p_constants.allowed_nans, keep_default_na=False)

    # 10/24/23 - Some dates are not being converted to datetime in the read_csv function for some reason. Force the conversion here
    tissue_df[p_constants.tissue_date_cols] = tissue_df[p_constants.tissue_date_cols].apply(pd.to_datetime, errors='coerce')

    # The datum field (from the CEDEN stations table in the CEDEN data mart) is needed to run the data quality estimator. Import the saved dataset and join the values to the dataset here
    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum']) 
    tissue_df = p_utils.join_datum(tissue_df, station_df) 

    # Rename columns to match the column names used in the data quality functions. Some of these column names are different even compared to the column names of the other CEDEN tables
    tissue_df = tissue_df.rename(columns={
        'ResQualCode': 'ResultQualCode',
        'Matrix': 'MatrixName',
        'ResultReplicate': 'ResultsReplicate'
    })

    print('--- Cleaning data')
    tissue_df = p_utils_dq.clean_data(tissue_df)

    print('--- Adding data quality fields')
    tissue_dq_df = p_utils_dq.add_data_quality(tissue_df)
    
    #####  Export data
    print('--- Exporting data')
    outdir = '../../support_files'
    p_utils.write_csv(tissue_dq_df, 'swamp_tissue_data_quality', outdir)

    print('%s finished running' % os.path.basename(__file__))