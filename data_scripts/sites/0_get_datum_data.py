'''
This script downloads data from the CEDEN Stations data mart and saves the data locally. 
By saving the data locally, we won't have to query the data mart multiple times (for each data type).
This dataset has the 'Datum' field, which is a required field for the data quality assessor.
'''

import os
import pandas as pd
import pyodbc
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py

def get_station_data():
    try:
        sql = "SELECT StationCode, Datum FROM %s ;" % p_constants.datamart_tables['stations']
        cnxn = pyodbc.connect(Driver='SQL Server', Server=p_constants.SERVER1, uid=p_constants.UID, pwd=p_constants.PWD)
        df = pd.read_sql(sql, cnxn)
        return df
    except:
        print("Couldn't connect to %s." % p_constants.SERVER1)


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Downloading data from %s' % p_constants.datamart_tables['stations'])
    ceden_stations_df = get_station_data()

    print('--- Writing ceden_stations.csv')

    # Write data in support files folder
    file_name = 'ceden_stations'
    outdir = '../../support_files'
    p_utils.write_csv(ceden_stations_df, file_name, outdir) # Write file

    # Write data file in archive folder
    outdir_archive = '../../ceden_files/'
    p_utils.write_csv(ceden_stations_df, file_name + '_' + p_constants.today, outdir_archive + '/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))
