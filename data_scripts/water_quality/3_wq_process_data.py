'''
This script cleans and processes the SWAMP water quality data before it is uploaded to the open data portal. It filters out some records that do not have valid values and adds some fields (censored data, analyte categories, region, program, etc.) that are used by the web app.  
'''

import numpy as np
import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    wq_df = pd.read_csv('../../support_files/swamp_wq_data_quality.csv', parse_dates=p_constants.wq_date_cols, low_memory=False)

    #####  Drop records that could cause issues

    # Drop records with StationCode = FIELDQA_SWAMP
    wq_df = wq_df.drop(wq_df[(wq_df['StationCode'] == 'FIELDQA')].index)
    wq_df = wq_df.drop(wq_df[(wq_df['StationCode'] == 'FIELDQA_SWAMP')].index)

    # Drop records with a matrix value that we can't show
    wq_df = wq_df.drop(wq_df[~(wq_df['MatrixName'].str.contains("samplewater|sediment", case=False))].index)

    # Drop records that have null or negative value for Result AND a null or negative MDL
    wq_df = wq_df.drop(wq_df[((wq_df['Result'].isna()) | (wq_df['Result'] < 0)) & ((wq_df['MDL'].isna()) | (wq_df['MDL'] < 0))].index)

    # Drop DNQ/ND records that have a null or negative MDL value
    wq_df = wq_df.drop(wq_df[((wq_df['ResultQualCode'] == 'DNQ') | (wq_df['ResultQualCode'] == 'ND')) & ((wq_df['MDL'] < 0) | (wq_df['MDL'].isna()))].index)

    # Drop records with a BRK QA Code
    # BRK = 'Sample not analyzed, sample container broken" - not accounted for in the data quality script
    wq_df = wq_df.drop(wq_df[wq_df['QACode'] == 'BRK'].index)

    # Added 7/20/22 
    # Drop records with ResultQualCode == '=' and empty Result value
    # These records cause an issue when displaying the station summary data
    wq_df = wq_df.drop(wq_df[((wq_df['ResultQualCode'] == '=') & (wq_df['Result'].isna()))].index)

    # Drop records that have a "NR" ResultQualCode value and a null result
    wq_df = wq_df.drop(wq_df[(wq_df['ResultQualCode'] == 'NR') & (wq_df['Result'].isna())].index)

    # Drop records that have a null result value and a null ResultQualCode value
    wq_df = wq_df.drop(wq_df[(wq_df['Result'].isna()) & (wq_df['ResultQualCode'].isna())].index)

    # Drop matrix values with 'blank' (QA)
    wq_df = wq_df.drop(wq_df[wq_df['MatrixName'].str.contains('blank', regex=False)].index)


    #####  Process data
    print('--- Processing data')

    # Strip special characters
    wq_df.replace(r'\t',' ', regex=True, inplace=True) # tab
    wq_df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    wq_df.replace(r'\n',' ', regex=True, inplace=True) # newline
    wq_df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    wq_df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    wq_df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    wq_df.replace(r'\"', ' ', regex=True, inplace=True) # quotes
    wq_df.replace(',', '', regex=True, inplace=True) # commas

    # Change date format to standard format (open data portal). This format is required to query date values using the portal API
    wq_df['SampleDate'] = wq_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Add fields for censored data (non detects, etc)
    wq_censored = wq_df.apply(lambda row: p_utils.get_censored_result(row), axis=1)
    wq_df['Result_Half_MDL'] = wq_censored[0]
    wq_df['Censored'] = wq_censored[1]

    # Add AnalyteDisplay field
    # The values in the Analyte column are not "clean", but we still want to keep them for reference. The app uses the AnalyteDisplay field instead of the Analyte field.
    wq_df['Analyte'] = wq_df['Analyte'].replace('\'', '', regex=True) # Strip single quote
    wq_df['AnalyteDisplay'] = wq_df['Analyte']

    # Add analyte categories
    analytes_df = pd.read_csv(p_constants.analyte_list_file, dtype='unicode') # Import reference table
    analyte_cols = analytes_df[['CedenAnalyteName', 'AnalyteGroup1', 'AnalyteGroup2', 'AnalyteGroup3']] # Get a subset of the fields
    wq_df = pd.merge(wq_df, analyte_cols, how='left', left_on='Analyte', right_on='CedenAnalyteName') # Join AnalyteGroup fields to data frame
    wq_df.drop(['CedenAnalyteName'], axis=1, inplace=True) # Drop unneeded fields

    # Add MatrixDisplay field
    wq_df['MatrixDisplay'] = wq_df['MatrixName'] # Copy over matrix values to a new column
    wq_df['MatrixDisplay'] = wq_df['MatrixDisplay'].apply(lambda x: p_utils.get_matrix_name(x)) # Standardize the matrix values. App uses the MatrixDisplay field to show the matrix tags

    # Add Region field
    stations_df = p_utils.import_csv('../../support_files/swamp_stations.csv', date_cols=['LastSampleDate']) # Import station data
    station_cols = stations_df[['StationCode', 'Region']] # Get a subset of the fields
    wq_df = pd.merge(wq_df, station_cols, how='left', on='StationCode') # Join region values
    # After joining, some records will have a blank region value. Use the first character of StationCode (usually a number in reference to the region) or leave blank
    wq_df['Region'] = wq_df.apply(
        lambda row: row['StationCode'][0] if np.isnan(row['Region']) else row['Region'],
        axis=1
    )

    # Convert Region column to int first (to remove decimal point) and then to string again
    wq_df['Region'] = wq_df['Region'].astype(int)
    wq_df['Region'] = wq_df['Region'].astype(str)

    ## Add Program fields
    # Assign False to all programs initially
    wq_df['Bioassessment'] = False
    wq_df['Bioaccumulation'] = False
    wq_df['Fhab'] = False
    wq_df['Spot'] = False
    # Overwrite the False values and assign True values based on if the ParentProject value is on the program lists
    wq_df.loc[wq_df['ParentProject'].isin(p_constants.bioassessment_parent_projects), 'Bioassessment'] = True
    wq_df.loc[wq_df['ParentProject'].isin(p_constants.bioaccumulation_parent_projects), 'Bioaccumulation'] = True
    wq_df.loc[wq_df['ParentProject'].isin(p_constants.fhab_parent_projects), 'Fhab'] = True
    wq_df.loc[wq_df['ParentProject'].isin(p_constants.spot_parent_projects), 'Spot'] = True

     # 4/12/23 - Add DisplayText field. This field used to show text in chart tooltips for additional context. Ex. Non-detect. 
    # Can leave blank if there is no text to show
    wq_df.loc[wq_df['ResultQualCode'] == 'ND', 'DisplayText'] = 'Non-detect' # If value in ResultQualCode is 'ND', populate DisplayComment field with 'Non-detect'
    wq_df.loc[wq_df['ResultQualCode'] == 'DNQ', 'DisplayText'] = 'Detected not quantified'

    # If ResultQualCode includes '<' or '>', copy the value over to the DisplayText field
    wq_df.loc[wq_df['ResultQualCode'].str.contains('<|>'), 'DisplayText'] = wq_df['ResultQualCode']

    # Rename censored result field to 'ResultDisplay'. This is the field that the app will use to show Result values
    wq_df = wq_df.rename(columns={'Result_Half_MDL': 'ResultDisplay'})


    #####  Write data
    wq_file_name = 'swamp_water_quality_data'
    # Write file in dated folder in export folder
    p_utils.write_csv(wq_df, wq_file_name + '_' + p_constants.today, '../../export' + '/' + p_constants.today) 

    print('%s finished running' % os.path.basename(__file__))