'''
This script downloads SWAMP data from the CEDEN water quality data mart and saves the data locally. 
'''

import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    print('--- Downloading data from %s' % p_constants.datamart_tables['water_quality'])

    # Download water quality data (SWAMP) for select analytes
    sql_wq_swamp = "SELECT * FROM " + p_constants.datamart_tables['water_quality'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND ParentProject != 'SWAMP Stream Pollution Trends' AND Analyte in (" + ', '.join(["'{}'".format(value) for value in p_constants.ceden_wq_analytes]) + "))"
    wq_swamp_df = p_utils.download_data(sql_wq_swamp,  p_constants.wq_date_cols)

    # Download chemistry data (SPoT), all analytes
    sql_wq_spot = "SELECT * FROM " + p_constants.datamart_tables['water_quality'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND ParentProject = 'SWAMP Stream Pollution Trends')"
    wq_spot_df = p_utils.download_data(sql_wq_spot,  p_constants.wq_date_cols)

    # Combine dataframes
    wq_df = pd.concat([wq_swamp_df, wq_spot_df], ignore_index=True)

    # Strip whitespace from StationName. See example station: 205PS0365
    wq_df['StationName'] = wq_df['StationName'].apply(lambda x: x.strip())

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(wq_df, 'ceden_swamp_wq', outdir)

    # Write data file in dated folder in archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(wq_df, 'ceden_swamp_wq' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))

    