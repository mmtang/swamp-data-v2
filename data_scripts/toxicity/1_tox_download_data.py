'''
This script downloads SWAMP data from the CEDEN toxicity data mart (replicate data) and saves the data locally. For toxicity data, use the tox replicate data mart and not the tox summary data mart. The summary data mart has some missing data.
'''

import os
import sys

sys.path.insert(0, '../utils/') # To import module from another folder
import p_constants # p_constants.py
import p_utils # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Downloading data from %s' % p_constants.datamart_tables['toxicity'])
    sql_tox = "SELECT * FROM " + p_constants.datamart_tables['toxicity'] + " WHERE (Program = 'Surface Water Ambient Monitoring Program' AND Mean IS NOT NULL AND CollectionReplicate = 1 AND LabReplicate = 1)"
    tox_df = p_utils.download_data(sql_tox, p_constants.tox_date_cols)

    station_df = p_utils.import_csv('../../support_files/ceden_stations.csv', fields=['StationCode', 'Datum']) # Import station data with select fields
    tox_data = p_utils.join_datum(tox_df, station_df) # Join datum field to the tox data df

    #####  Write two sets of data, one set without the data quality columns and one set with the columns
    #####  1. Without the data quality fields

    # Support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(tox_data, 'ceden_swamp_tox', outdir)

    # Write data file in archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(tox_data, 'ceden_swamp_tox' + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    #####  2. With the data quality fields

    # Add DataQuality and DataQualityIndicator columns with placeholder values. Must include these columns (needed for the app). The data quality assessor does not work on tox data. Update it in the future?
    tox_data['DataQuality'] = 'Not assessed'
    tox_data['DataQualityIndicator'] = None

    # Write data file in support files folder
    outdir = '../../support_files/'
    p_utils.write_csv(tox_data, 'swamp_tox_data_quality', outdir)

    print('%s finished running' % os.path.basename(__file__))