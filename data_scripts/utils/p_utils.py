'''
Shared functions used across multiple (or all) scripts
'''

import os
import pandas as pd
import p_constants # p_constants.py


# Function for downloading data as a Pandas dataframe
def download_data(sql, date_cols):
    import pyodbc
    try:
        cnxn = pyodbc.connect(Driver='SQL Server', Server=p_constants.SERVER1, uid=p_constants.UID, pwd=p_constants.PWD)
        df = pd.read_sql(sql, cnxn, parse_dates=date_cols)
        return df
    except:
        print("Couldn't connect to %s." % p_constants.SERVER1)

# This function checks whether or not the row qualifies as censored data and returns 2 values in an array
# 1. A value calculated as half the MDL
# 2. Boolean value (T/F) if the record is censored or not
def get_censored_result(row):
    if ((row['ResultQualCode'] == 'ND') or (row['ResultQualCode'] == 'DNQ')):
        if (row['MDL'] >= 0):
            return pd.Series([row['MDL'] / 2, True])
    # For ResuiltQualCode values of '<' or '<=', we will show the Result value (and add the '<' in the app)
    elif ((row['ResultQualCode'] == '<') or (row['ResultQualCode'] == '<=')):
        return pd.Series([row['Result'], True])
    else:
        return pd.Series([row['Result'], False])

# Function used for standardizing the matrix name
# Ex. some values have 'samplewater' in them but have extra letters or words. Need all of them to say 'samplewater'. Only concerned about 'samplewater' and 'sediment' for now but may need to add more later
def get_matrix_name(matrix):
    if 'samplewater' in matrix:
        return 'samplewater'
    elif 'sediment' in matrix:
        return 'sediment'
    else:
        return matrix
    
# Function for importing a local CSV file as a Pandas DF
def import_csv(path, fields=None, date_cols=None):
    if (fields):
        df = pd.read_csv(path, usecols=fields, parse_dates=date_cols)
        return df
    else:
        df = pd.read_csv(path, parse_dates=date_cols)
        return df

# Function for joining datum to the CEDEN data structure
def join_datum(data, sites):
    df = pd.merge(data, sites, on='StationCode', how='left') # Left join on StationCode
    df = df.fillna(value={'Datum': 'NR'}) # Fill empty datum values with 'NR'
    return df

# Function for printing a space and line between messages in console (for better readability)
def print_spacer():
    print('')
    print(u'\u2500' * 15) # Print horizontal line
    
# Function for exporting a PD dataframe as a CSV file
def write_csv(df, file_name, outdir):
    # Create folder if it does not already exist
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    file_path = outdir + '/' + file_name + '.csv'
    df.to_csv(file_path, index=False, encoding='utf-8-sig')
