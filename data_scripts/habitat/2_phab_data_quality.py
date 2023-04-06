'''
This script adds the DataQuality and DataQualityIndicator fields to the SWAMP habitat data.
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
    phab_df = pd.read_csv('../../support_files/ceden_swamp_phab.csv', parse_dates=p_constants.phab_date_cols)

    #####  Process data
    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum']) # Import station data with a subset of the fields
    phab_df = p_utils.join_datum(phab_df, station_df) # Join datum and region fields to the phab df

    print('--- Cleaning data')
    phab_df = p_utils_dq.clean_data(phab_df)

    print('--- Adding data quality fields')
    phab_dq_df = p_utils_dq.add_data_quality(phab_df)
    
    #####  Export data
    print('--- Exporting data')
    outdir = '../../support_files'
    p_utils.write_csv(phab_dq_df, 'swamp_phab_data_quality', outdir)

    print('%s finished running' % os.path.basename(__file__))