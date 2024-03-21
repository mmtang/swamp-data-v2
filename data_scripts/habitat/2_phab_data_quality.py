'''
Step 2: This script adds the DataQuality and DataQualityIndicator fields to the SWAMP habitat data.

---DataQuality: Describes the overall quality of the record by taking the QACode, ResultQACode, ComplicanceCode, BatchVerificationCode, and special circumstances into account to assign it to one of the following categories: . The assignments and categories are provisional. A working explanation of the data quality ranking can be found at the following link: https://docs.google.com/spreadsheets/d/1q-tGulvO9jyT2dR9GGROdy89z3W6xulYaci5-ezWAe0/edit?usp=sharing

---DataQualityIndicator: Explains the reason for the DataQuality value by indicating which quality assurance check the data did not pass (e.g. BatchVerificationCode, ResultQACode, etc.).

Important: Running this script requires having the "ceden_stations.csv" file saved in the support_files folder. To get this file, run the 0_get_datum_data.py script under the "sites" folder.

Updated: 03/14/2024 
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '..\\utils\\') 
import p_constants # p_constants.py
import p_utils  # p_utils.py
import p_utils_dq # p_utils_dq.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    #####  Import data from previous script
    phab_df = pd.read_csv('../../support_files/ceden_swamp_phab.csv', parse_dates=p_constants.phab_date_cols, na_values=p_constants.allowed_nans, keep_default_na=False)

    # 10/15/23 - Dates are not being converted to datetime in the read_csv function, for some reason, so force the conversion here
    phab_df[p_constants.phab_date_cols] = phab_df[p_constants.phab_date_cols].apply(pd.to_datetime, errors='coerce')

    #####  Process data
    # Import station data with a subset of the fields
    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum']) 
    # Join datum field to the df
    phab_df = p_utils.join_datum(phab_df, station_df) 

    print('--- Cleaning data')
    phab_df = p_utils_dq.clean_data(phab_df)

    print('--- Adding data quality fields')
    # Add the DataQuality and DataQualityIndicator fields
    phab_dq_df = p_utils_dq.add_data_quality(phab_df)
    
    #####  Export data
    print('--- Exporting data')
    outdir = '../../support_files'
    p_utils.write_csv(phab_dq_df, 'swamp_phab_data_quality', outdir)

    print('%s finished running' % os.path.basename(__file__))