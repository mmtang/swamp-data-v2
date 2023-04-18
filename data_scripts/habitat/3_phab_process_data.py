'''
This script cleans and processes the SWAMP habitat data before it is uploaded to the open data portal. It filters out some records that do not have valid values and adds some fields (censored data, analyte categories, region, program, etc.) that are used by the web app.  
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
    phab_df = p_utils.import_csv('../../support_files/swamp_phab_data_quality.csv', date_cols=p_constants.phab_date_cols)

    #####  Drop records that could cause some issues

    # Drop records with StationCode = FIELDQA_SWAMP
    phab_df = phab_df.drop(phab_df[(phab_df['StationCode'] == 'FIELDQA')].index)
    phab_df = phab_df.drop(phab_df[(phab_df['StationCode'] == 'FIELDQA_SWAMP')].index)

    # Drop records that have a null result value AND a null ResultQualCode value
    phab_df = phab_df.drop(phab_df[(phab_df['Result'].isna()) & (phab_df['ResultQualCode'].isna())].index)

    # Drop records that have a "NR" ResultQualCode value AND a null result
    phab_df = phab_df.drop(phab_df[(phab_df['ResultQualCode'] == 'NR') & (phab_df['Result'].isna())].index)

    # Drop records with negative values
    phab_df = phab_df.drop(phab_df[phab_df['Result'] < 0].index)

    # Drop records with BRK QA Code
    # BRK = 'Sample not analyzed, sample container broken" - not accounted for in data quality script
    phab_df = phab_df.drop(phab_df[phab_df['QACode'] == 'BRK'].index)

    # Added 7/20/22 
    # Drop records with ResultQualCode == '=' and empty Result value
    # These records cause an issue when displaying the station summary data
    phab_df = phab_df.drop(phab_df[((phab_df['ResultQualCode'] == '=') & (phab_df['Result'].isna()))].index)

    # Drop matrix values with 'blank' (QA)
    phab_df = phab_df.drop(phab_df[phab_df['MatrixName'].str.contains('blank', regex=False)].index)


    #####  Process data
    print('--- Processing data')

    # Strip whitespace from StationName. See example station: 205PS0365
    phab_df['StationName'] = phab_df['StationName'].apply(lambda x: x.strip())

    phab_df['SampleDate'] = pd.to_datetime(phab_df['SampleDate']) # Convert values to date type
    phab_df['SampleDate'] = phab_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S') # Change date format to standard format (open data portal). This format is required to query date values using the portal API

    # Add fields for censored data. There is no censored data in the PHAB format (for now), so we can use a default False value and copy over the values from Result. Have to keep these two columns in the data structure because they are used by the web app
    phab_df['Censored'] = False
    phab_df['ResultDisplay'] = phab_df['Result'] 

    # Add AnalyteDisplay field
    # The values in the Analyte column are not "clean", but we still want to keep them for reference. The app uses the AnalyteDisplay field instead of the Analyte field.
    phab_df['Analyte'] = phab_df['Analyte'].replace('\'', '', regex=True) # Strip single quote
    phab_df['AnalyteDisplay'] = phab_df['Analyte']

    # Add analyte categories
    analytes_df = p_utils.import_csv('../../assets/joined_analyte_list_3-21-23.csv') # Import reference table
    analyte_cols = analytes_df[['CedenAnalyteName', 'AnalyteGroup1', 'AnalyteGroup2', 'AnalyteGroup3']] # Get a subset of the fields
    phab_df = pd.merge(phab_df, analyte_cols, how='left', left_on='Analyte', right_on='CedenAnalyteName') # Join AnalyteGroup fields to data frame
    phab_df.drop(['CedenAnalyteName'], axis=1, inplace=True) # Drop unneeded fields

    # Add MatrixDisplay field
    phab_df['MatrixDisplay'] = phab_df['MatrixName'] # Copy over matrix values to a new column
    phab_df['MatrixDisplay'] = phab_df['MatrixDisplay'].apply(lambda x: p_utils.get_matrix_name(x)) # Standardize the matrix values. App uses the MatrixDisplay field to show the matrix tags

    # Add Region field
    stations_df = p_utils.import_csv('../../support_files/swamp_stations.csv', date_cols=['LastSampleDate']) # Import station data
    station_cols = stations_df[['StationCode', 'Region']] # Get a subset of the columns
    phab_df = pd.merge(phab_df, station_cols, how='left', on='StationCode') # Join region values
    # After joining, some records will have a blank region value. Use the first character of StationCode (usually a number in reference to the region) or leave blank
    phab_df['Region'] = phab_df.apply(
        lambda row: row['StationCode'][0] if np.isnan(row['Region']) else row['Region'],
        axis=1
    )

    # Convert Region column to int first (to remove decimal point) and then to string again
    phab_df['Region'] = phab_df['Region'].astype(int)
    phab_df['Region'] = phab_df['Region'].astype(str)

    # Add Program fields
    # Assign False to all programs initially
    phab_df['Bioassessment'] = False
    phab_df['Bioaccumulation'] = False
    phab_df['Fhab'] = False
    phab_df['Spot'] = False
    # Overwrite the False values and assign True values based on if the ParentProject value is on the program lists
    phab_df.loc[phab_df['ParentProject'].isin(p_constants.bioassessment_parent_projects), 'Bioassessment'] = True
    phab_df.loc[phab_df['ParentProject'].isin(p_constants.bioaccumulation_parent_projects), 'Bioaccumulation'] = True
    phab_df.loc[phab_df['ParentProject'].isin(p_constants.fhab_parent_projects), 'Fhab'] = True
    phab_df.loc[phab_df['ParentProject'].isin(p_constants.spot_parent_projects), 'Spot'] = True

    # Change units for indices
    # CEDEN value for CSCI is null
    phab_df.loc[phab_df['Analyte'] == 'CSCI', 'Unit'] = 'score' 
    phab_df.loc[phab_df['Analyte'] == 'IPI', 'Unit'] = 'score'

    # 4/12/23 - Add DisplayText field. This field used to show text in chart tooltips for additional context. Ex. Non-detect. 
    # Can leave blank if there is no text to show
    phab_df.loc[phab_df['ResultQualCode'] == 'ND', 'DisplayText'] = 'Non-detect' # If value in ResultQualCode is 'ND', populate DisplayComment field with 'Non-detect'
    phab_df.loc[phab_df['ResultQualCode'] == 'DNQ', 'DisplayText'] = 'Detected not quantified'

    # If ResultQualCode includes '<' or '>', copy the value over to the DisplayText field
    phab_df.loc[phab_df['ResultQualCode'].str.contains('<|>'), 'DisplayText'] = phab_df['ResultQualCode']


    #####  Write data
    phab_file_name = 'swamp_habitat_data'
    p_utils.write_csv(phab_df, phab_file_name + '_' + p_constants.today, '../../export' + '/' + p_constants.today) # Write file in dated folder in the export folder

    print('%s finished running' % os.path.basename(__file__))