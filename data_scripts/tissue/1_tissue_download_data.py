'''
This script downloads SWAMP data from the CEDEN tissue data mart and saves the data locally. 
'''

import os
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

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

    