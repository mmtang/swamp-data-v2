'''
This script adds the DataQuality and DataQualityIndicator fields to the SWAMP water quality data.
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants
import p_utils  # p_utils.py
import p_utils_dq # p_utils_dq.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    # Import SWAMP WQ data
    wq_df = pd.read_csv('../../support_files/ceden_swamp_wq.csv', parse_dates=p_constants.wq_date_cols, low_memory=False)

    # Import SWAMP station data
    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum'])
    wq_df = p_utils.join_datum(wq_df, station_df) # Add datum and region

    print('--- Cleaning data')
    wq_df = p_utils_dq.clean_data(wq_df)

    print('--- Adding data quality fields...')
    wq_dq_df = p_utils_dq.add_data_quality(wq_df)

    print('--- Exporting data')
    outdir = '../../support_files'
    p_utils.write_csv(wq_dq_df, 'swamp_wq_data_quality', outdir)
  
    print('%s finished running' % os.path.basename(__file__))