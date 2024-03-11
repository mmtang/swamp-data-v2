'''
Step 1: This script downloads SWAMP data from the CEDEN tissue data mart and saves the data locally.
If running the tissue data scripts separately from the rest of the data types, run the scripts in sequence from 1 to 4:

--- 1_tissue_download_data.py
--- 2_tissue_data_quality.py
--- 3_tissue_process_data.py
--- 4_tissue_upload_portal.py

Updated: 02/29/2024 
'''

import os
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    # Download SWAMP data from the internal CEDEN data mart
    print('--- Downloading data from %s' % p_constants.datamart_tables['tissue'])
    sql_tissue = "SELECT * FROM " + p_constants.datamart_tables['tissue'] + " WHERE (ProgramName = 'Surface Water Ambient Monitoring Program')"
    tissue_df = p_utils.download_data(sql_tissue, p_constants.tissue_date_cols)

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(tissue_df, 'ceden_swamp_tissue', outdir)

    # Write data file in archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(tissue_df, 'ceden_swamp_tissue' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))

    