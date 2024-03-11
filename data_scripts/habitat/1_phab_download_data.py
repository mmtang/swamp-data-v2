'''
Step 1: This script downloads SWAMP data from the CEDEN habitat data mart and saves the data locally. 
If running the habitat data scripts separately from the rest of the data types, run the scripts in sequence from 1 to 4:

--- 1_phab_download_data.py
--- 2_phab_data_quality.py
--- 3_phab_process_data.py
--- 4_phab_upload_portal.py

Updated: 03/05/2024 
'''

import os
import sys

sys.path.insert(0, '..\\utils\\') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    # Download data from the internal CEDEN data mart, limited to the defined analytes in ceden_phab_analytes
    print('--- Downloading data from %s' % p_constants.datamart_tables['habitat'])
    sql_phab = "SELECT * FROM " + p_constants.datamart_tables['habitat'] + " WHERE Program in (" + ', '.join(["'{}'".format(value) for value in p_constants.habitat_programs]) + ") AND Analyte in (" + ', '.join(["'{}'".format(value) for value in p_constants.ceden_phab_analytes]) + ")"
    phab_df = p_utils.download_data(sql_phab, p_constants.phab_date_cols)

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(phab_df, 'ceden_swamp_phab', outdir)

    # Write unprocessed data to the archive folder for reference
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(phab_df, 'ceden_swamp_phab' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))

    