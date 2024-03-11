'''
This script downloads SWAMP data from the CEDEN water quality data mart and saves the data locally. 

If running the water quality data scripts separately from the rest of the data types, run the scripts in sequence from 1 to 4:

--- 1_wq_download_data.py
--- 2_wq_data_quality.py
--- 3_wq_process_data.py
--- 4_wq_upload_portal.py

Updated: 03/06/2024 
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '..\\utils\\') 
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    print('--- Downloading data from %s' % p_constants.datamart_tables['water_quality'])

    # Download water quality data (SWAMP) for select analytes on the ceden_wq_analytes list. Do not include SPoT records because they will be pulled separately with no restrictions below
    sql_wq_swamp = "SELECT * FROM " + p_constants.datamart_tables['water_quality'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND ParentProject != 'SWAMP Stream Pollution Trends' AND Analyte in (" + ', '.join(["'{}'".format(value) for value in p_constants.ceden_wq_analytes]) + "))"
    wq_swamp_df = p_utils.download_data(sql_wq_swamp,  p_constants.wq_date_cols)

    # Download water quality data (SPoT), all analytes
    sql_wq_spot = "SELECT * FROM " + p_constants.datamart_tables['water_quality'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND ParentProject = 'SWAMP Stream Pollution Trends')"
    wq_spot_df = p_utils.download_data(sql_wq_spot,  p_constants.wq_date_cols)

    # Combine the two dataframes
    wq_df = pd.concat([wq_swamp_df, wq_spot_df], ignore_index=True)

    # Strip whitespace from StationName. See example station: 205PS0365
    wq_df['StationName'] = wq_df['StationName'].apply(lambda x: x.strip())

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(wq_df, 'ceden_swamp_wq', outdir)

    # Write data file in dated folder in CEDEN archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(wq_df, 'ceden_swamp_wq' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))

    