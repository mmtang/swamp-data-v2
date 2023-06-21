'''
This script adds the DataQuality and DataQualityIndicator fields to the SWAMP tissue dataset.
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # To import module from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py
import p_utils_dq # p_utils_dq.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    tissue_df = pd.read_csv('../../support_files/ceden_swamp_tissue.csv', parse_dates=p_constants.tissue_date_cols)

    #####  Process data
    # The datum field (from the CEDEN stations dataset) is needed to run the data quality estimator
    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum']) # Import station data with a subset of the fields
    tissue_df = p_utils.join_datum(tissue_df, station_df) # Join datum and region fields to the df

    # Rename columns to match the column names used in the data quality functions
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

     ##### EXPORT TEST FILE FOR MERCURY #####
    mercury_df = tissue_dq_df.loc[tissue_df['Analyte'] == 'Mercury']
    p_utils.write_csv(mercury_df, 'test_tissue_mercury_data', outdir)

    print('%s finished running' % os.path.basename(__file__))