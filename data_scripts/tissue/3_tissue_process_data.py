'''

'''

import os
import pandas as pd
import sys
import numpy as np

sys.path.insert(0, '../utils/') # To import module from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py


# This function checks whether or not the row qualifies as a non-detect, and returns 2 values in an array
# 1. The result value (adjusted if ND, the original value if not ND)
# 2. Accompanying text to be displayed next to the result value
def get_nd_result_value(row):
    # For records that are marked non-detect (ND or DNQ) and the result is greater than or equal to the MDL, use 1/2 * MDL
    if ((row['Result'] >= row['MDL']) and ((row['ResultQualCode'] == 'ND') or (row['ResultQualCode'] == 'DNQ'))):
        return pd.Series([0.5 * row['MDL'] , ''])
    # For records that are marked non-detect (ND or DNQ) and the result is less than the MDL or null, use the MDL
    elif (((row['Result'] < row['MDL']) or (pd.isnull(row['Result']))) and ((row['ResultQualCode'] == 'ND') or (row['ResultQualCode'] == 'DNQ'))):
        return pd.Series([row['MDL'], 'Note: a conservative estimate']) # This is filler text. Check in with Jennifer
    else:
        return pd.Series([row['Result'], ''])
    

if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    tissue_df = pd.read_csv('../../support_files/swamp_tissue_data_quality.csv', parse_dates=p_constants.tissue_date_cols, low_memory=False)

    #print(tissue_df.columns.values)

    tissue_df = tissue_df.drop(tissue_df[(tissue_df['CollectionReplicate'] != 1)].index)
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['CompositeReplicate'] != 1)].index)
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['ResultsReplicate'] != 1)].index)

    # Remove problematic records

    # Drop records that have null or negative value for Result AND a null or negative MDL
    tissue_df = tissue_df.drop(tissue_df[((tissue_df['Result'].isna()) | (tissue_df['Result'] < 0)) & ((tissue_df['MDL'].isna()) | (tissue_df['MDL'] < 0))].index)

    # Drop DNQ/ND records that have a null or negative MDL value
    tissue_df = tissue_df.drop(tissue_df[((tissue_df['ResultQualCode'] == 'DNQ') | (tissue_df['ResultQualCode'] == 'ND')) & ((tissue_df['MDL'] < 0) | (tissue_df['MDL'].isna()))].index)

    # Added 7/20/22 
    # Drop records with ResultQualCode == '=' and empty Result value
    # These records cause an issue when displaying the station summary data
    tissue_df = tissue_df.drop(tissue_df[((tissue_df['ResultQualCode'] == '=') & (tissue_df['Result'].isna()))].index)

    # Drop records that have a "NR" ResultQualCode value and a null result
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['ResultQualCode'] == 'NR') & (tissue_df['Result'].isna())].index)

    # Drop records that have a null result value and a null ResultQualCode value
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['Result'].isna()) & (tissue_df['ResultQualCode'].isna())].index)

    # Strip special characters
    tissue_df.replace(r'\t',' ', regex=True, inplace=True) # tab
    tissue_df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    tissue_df.replace(r'\n',' ', regex=True, inplace=True) # newline
    tissue_df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    tissue_df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    tissue_df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    tissue_df.replace(r'\"', ' ', regex=True, inplace=True) # quotes
    tissue_df.replace(',', '', regex=True, inplace=True) # commas

    # Change date format to standard format (open data portal). This format is required to query date values using the portal API
    # tissue_df['SampleDate'] = tissue_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Create new column with just the sample year
    tissue_df['SampleYear'] = tissue_df['SampleDate'].dt.year

    # Add fields for censored data (non detects, etc)
    nd_values = tissue_df.apply(lambda row: get_nd_result_value(row), axis=1)
    tissue_df['ResultAdjusted'] = nd_values[0]
    tissue_df['ResultNote'] = nd_values[1]

    # Filter out data quality records = metadata, reject record
    tissue_filtered_df = tissue_df.drop(tissue_df[(tissue_df['DataQuality'] == 'MetaData') | (tissue_df['DataQuality'] == 'Reject record')].index)

    # Create new column indicating if record/result is from an individual or composite
    tissue_filtered_df.loc[tissue_filtered_df['NumberFishperComp'] == 1, 'CompositeIndividual'] = 'Individual'
    tissue_filtered_df.loc[tissue_filtered_df['NumberFishperComp'] > 1, 'CompositeIndividual'] = 'Composite'

    # print(tissue_filtered_df.head())
    print(tissue_filtered_df['CompositeIndividual'].unique())

    # Calculate annual averages for each station/analyte/organism combination and save to new dataframe
    group_columns = [
        'StationCode', 
        'StationName',
        'CommonName', 
        'FinalID', 
        'TissueName',
        'PrepPreservationName',
        'CompositeIndividual',
        'NumberFishperComp',
        'Analyte',
        'Unit',
        'ResultQualCode',
        'MDL',
        'SampleYear', 
        'ProgramName',
        'ParentProjectName',
        'ProjectCode',
        'ProjectName',
        'TLAvgLength(mm)',
        'TargetLatitude',
        'TargetLongitude'
    ]
    tissue_summary_df = tissue_filtered_df.groupby(group_columns, as_index=False)['ResultAdjusted'].mean().reset_index()
    print(tissue_summary_df.tail(n=10))

    outdir = '../../support_files/'
    p_utils.write_csv(tissue_summary_df, 'swamp_tissue_summary', outdir)








