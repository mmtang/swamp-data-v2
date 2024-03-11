'''
Step 3: This script cleans and processes the SWAMP habitat data before it is uploaded to the open data portal. It filters out some records that do not have valid values and adds some fields (censored data, analyte categories, region, program, etc.) that are used by the web app.  

Updated: 03/05/2024 
'''

import numpy as np
import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') 
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    #####  Import data from previous script
    phab_df = p_utils.import_csv('../../support_files/swamp_phab_data_quality.csv', date_cols=p_constants.phab_date_cols)


    ##### Remove unneeded records or records with missing data elements
    # Drop records with StationCode = FIELDQA_SWAMP
    phab_df = phab_df.drop(phab_df[(phab_df['StationCode'] == 'FIELDQA')].index)
    phab_df = phab_df.drop(phab_df[(phab_df['StationCode'] == 'FIELDQA_SWAMP')].index)

    # Drop records that have a null result value AND a null ResultQualCode value
    phab_df = phab_df.drop(phab_df[(phab_df['Result'].isna()) & (phab_df['ResultQualCode'].isna())].index)

    # Drop records that have a "NR" ResultQualCode value AND a null result
    phab_df = phab_df.drop(phab_df[(phab_df['ResultQualCode'] == 'NR') & (phab_df['Result'].isna())].index)

    # Drop records with BRK QA Code
    # BRK = 'Sample not analyzed, sample container broken" - not accounted for in data quality script
    phab_df = phab_df.drop(phab_df[phab_df['QACode'] == 'BRK'].index)

    # Added 7/20/22 
    # Drop records with ResultQualCode value '=' and empty Result value
    # These records cause an issue when displaying the station summary data
    phab_df = phab_df.drop(phab_df[((phab_df['ResultQualCode'] == '=') & (phab_df['Result'].isna()))].index)

    # Drop matrix values with 'blank' (QA)
    phab_df = phab_df.drop(phab_df[phab_df['MatrixName'].str.contains('blank', regex=False)].index)

    # Added 2/5/24 - Drop data with no sample date
    phab_df = phab_df.drop(phab_df[phab_df['SampleDate'].isna()].index)

    # Added 2/12/24 - Drop CollectionReplicate records
    phab_df = phab_df.drop(phab_df[phab_df['CollectionReplicate'] != 1].index)


    #####  Process data
    print('--- Processing data')

    # Strip special characters
    phab_df.replace(r'\t',' ', regex=True, inplace=True) # tab
    phab_df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    phab_df.replace(r'\n',' ', regex=True, inplace=True) # newline
    phab_df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    phab_df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    phab_df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    phab_df.replace(r'\"', ' ', regex=True, inplace=True) # quotes

    # Strip whitespace from StationName. See example station: 205PS0365
    phab_df['StationName'] = phab_df['StationName'].apply(lambda x: x.strip())

    # Convert values to date type
    phab_df['SampleDate'] = pd.to_datetime(phab_df['SampleDate']) 
    # Change date format to standard format for the open data portal. This format is required to query date values using the portal API
    phab_df['SampleDate'] = phab_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S') 

    # Add fields for censored data. There is no censored data in the PHAB format (for now), so we can use a default False value and copy over the values from Result. Have to keep these two columns in the data structure because they are used by the web app
    phab_df['Censored'] = False
    phab_df['ResultDisplay'] = phab_df['Result'] 

    # Add AnalyteDisplay field
    # The values in the Analyte column are not "clean" and in some cases are not what we want to have shown in the dashboard, but we still want to keep them there for reference. The app uses the AnalyteDisplay field instead of the Analyte field.
    phab_df['AnalyteDisplay'] = phab_df['Analyte']

    # Change analyte names for CSCI and IPI to show the full unabbreviated name
    phab_df['AnalyteDisplay'] = phab_df['AnalyteDisplay'].replace('CSCI', 'California Stream Condition Index (CSCI)')
    phab_df['AnalyteDisplay'] = phab_df['AnalyteDisplay'].replace('IPI', 'Index of Physical Habitat Integrity (IPI)')

    # Add analyte categories
    analytes_df = p_utils.import_csv('../../assets/joined_analyte_list_3-21-23.csv') 
    analyte_cols = analytes_df[['CedenAnalyteName', 'AnalyteGroup1', 'AnalyteGroup2', 'AnalyteGroup3']] 
    phab_df = pd.merge(phab_df, analyte_cols, how='left', left_on='Analyte', right_on='CedenAnalyteName') 
    phab_df.drop(['CedenAnalyteName'], axis=1, inplace=True) # Drop unneeded fields

    # Add MatrixDisplay field
    # Similar to AnalyteDisplay, we may want to have a different matrix name displayed on the dashboard compared to the CEDEN values. Keep the original field for reference
    # Copy over matrix values to a new column
    phab_df['MatrixDisplay'] = phab_df['MatrixName'] 
    # Standardize the matrix values. App uses the MatrixDisplay field to show the matrix tags
    phab_df['MatrixDisplay'] = phab_df['MatrixDisplay'].apply(lambda x: p_utils.get_matrix_name(x)) 

    # Add Region field
    # Import station data
    stations_df = p_utils.import_csv('../../support_files/swamp_stations.csv', date_cols=['LastSampleDate']) 
    station_cols = stations_df[['StationCode', 'Region']] 
    # Join region values
    phab_df = pd.merge(phab_df, station_cols, how='left', on='StationCode') 
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

    # Add StationCategory column for reference sites
    ref_sites_df = p_utils.import_csv(p_constants.reference_sites_file)
    ref_cols = ref_sites_df[['cedenid', 'StationCategory']] 
    # Left join on StationCode
    phab_df = pd.merge(phab_df, ref_cols, how='left', left_on=phab_df['StationCode'].str.lower(), right_on=ref_cols['cedenid'].str.lower())
    # Drop unneeded fields
    phab_df = phab_df.drop(['key_0', 'cedenid'], axis=1)

    # Change units for indices
    # CEDEN value for CSCI is null
    phab_df.loc[phab_df['Analyte'] == 'CSCI', 'Unit'] = 'score' 
    phab_df.loc[phab_df['Analyte'] == 'IPI', 'Unit'] = 'score'

    # Add DisplayText column. This field is used in the dashboard and standardized across the different data types. Populate with empty values for now until needed
    phab_df['DisplayText'] = np.nan


    #####  Write data
    # Write file in a dated folder in the export folder
    phab_file_name = 'swamp_habitat_data'
    p_utils.write_csv(phab_df, phab_file_name + '_' + p_constants.today, '../../export' + '/' + p_constants.today) 

    print('%s finished running' % os.path.basename(__file__))