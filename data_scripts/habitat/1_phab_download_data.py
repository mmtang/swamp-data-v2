'''
This script downloads SWAMP data from the CEDEN habitat data mart and saves the data locally. 
'''

import os
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Downloading data from %s' % p_constants.datamart_tables['habitat'])
    sql_phab = "SELECT * FROM " + p_constants.datamart_tables['habitat'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND Analyte in (" + ', '.join(["'{}'".format(value) for value in p_constants.ceden_phab_analytes]) + "))"
    phab_df = p_utils.download_data(sql_phab, p_constants.phab_date_cols)

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(phab_df, 'ceden_swamp_phab', outdir)

    # Write data file in archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(phab_df, 'ceden_swamp_phab' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))

    