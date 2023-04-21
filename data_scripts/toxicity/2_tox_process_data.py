'''
This script cleans and processes the SWAMP toxicity data before it is uploaded to the open data portal. It filters out some records that do not have valid values and adds some fields (analyte categories, region, program, etc.) that are used by the web app. This script should be run AFTER script #1
'''

import numpy as np
import os
import pandas as pd
import sys

sys.path.insert(0, '../utils/') # To import module from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    tox_df = p_utils.import_csv('../../support_files/swamp_tox_data_quality.csv', date_cols=p_constants.tox_date_cols)

    #####  Drop records that could cause some issues

    # Drop records with StationCode = 'FIELDQA_SWAMP'
    tox_df = tox_df.drop(tox_df[tox_df['StationCode'] == 'FIELDQA_SWAMP'].index)

    # Drop records with SampleTypeCode = 'FieldBLDup'.
    tox_df = tox_df.drop(tox_df[tox_df['SampleTypeCode'] == 'FieldBLDup'].index)

    # Drops records with -88 for the Mean
    tox_df = tox_df.drop(tox_df[tox_df['Mean'] == -88].index)

    # Filter out matrix with 'blank' (QA)
    tox_df = tox_df.drop(tox_df[tox_df['MatrixName'].str.contains('blank', regex=False)].index)

    # Drop records with null latitude or longitude coordinates
    tox_df = tox_df.drop(tox_df[(tox_df['TargetLatitude'].isna()) | (tox_df['TargetLongitude'].isna())].index)


    #####  Process data
    print('--- Processing data')

    # Strip special characters
    tox_df.replace(r'\t',' ', regex=True, inplace=True) # tab
    tox_df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    tox_df.replace(r'\n',' ', regex=True, inplace=True) # newline
    tox_df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    tox_df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    tox_df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    tox_df.replace(r'\"', ' ', regex=True, inplace=True) # quotes
    tox_df.replace(',', '', regex=True, inplace=True) # commas

    # Strip whitespace from StationName
    tox_df['StationName'] = tox_df['StationName'].apply(lambda x: x.strip())

    # Change date format to standard format (open data portal). This format is required to query date values using the portal API
    tox_df['SampleDate'] = tox_df['SampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Create new MeanDisplay column and copy over values from Mean column
    # For records with ResQualCode == 'NSI' (no surviving individuals), enter column value 0
    # Need to ask Bryn how to handle NSI records
    tox_df['MeanDisplay'] = tox_df['Mean']
    tox_df.loc[tox_df['ResultQualCode'] == 'NSI', 'MeanDisplay'] = 0

    # Remove duplicate records
    # Copied what David did for his open data portal scripts for consistency
    # https://github.com/daltare/CA-Data-Portal-Uploads/blob/main/Toxicity/Toxicity-Summary-Replicate-Data-Pull.R
    all_cols = list(tox_df.columns)
    subtract_cols = ['ToxID', 'LabReplicate', 'Result', 'ResQualCode', 'ToxResultComments', 'OrganismPerRep', 'ToxResultQACode']
    use_cols = [x for x in all_cols if x not in subtract_cols]
    tox_df.drop_duplicates(subset=use_cols, inplace=True)

    # Add analyte fields
    tox_df['Analyte'] = tox_df['Analyte'].replace('\'', '', regex=True) # Strip single quote from analyte name
    tox_df['AnalyteDisplay'] = tox_df['Analyte'] + ' (' + tox_df['OrganismName'] + ')' # Create new AnalyteDisplay field, copy values from Analyte column, and add the organism name in parentheses

    # Add analyte category fields
    analytes_df = p_utils.import_csv('../../assets/joined_analyte_list_3-21-23.csv') # Import reference table
    analyte_cols = analytes_df[['CedenAnalyteName', 'AnalyteGroup1', 'AnalyteGroup2', 'AnalyteGroup3']] # Get a subset of the fields
    tox_df = pd.merge(tox_df, analyte_cols, how='left', left_on='Analyte', right_on='CedenAnalyteName') # Join AnalyteGroup fields to data frame 
    tox_df.drop(['CedenAnalyteName'], axis=1, inplace=True) # Drop unneeded fields

    # Add matrix field
    tox_df['MatrixDisplay'] = tox_df['MatrixName'] # Copy over matrix values to a new column
    tox_df['MatrixDisplay'] = tox_df['MatrixDisplay'].apply(lambda x: p_utils.get_matrix_name(x)) # Standardize the matrix values. App uses the MatrixDisplay field to show the matrix tags

    # Add region field
    stations_df = p_utils.import_csv('../../support_files/swamp_stations.csv', date_cols=['LastSampleDate'])
    station_cols = stations_df[['StationCode', 'Region']] # Get a subset of the columns
    tox_df = pd.merge(tox_df, station_cols, how='left', on='StationCode') # Join region field
    # After joining, some records will have a blank region value. Use the first character of StationCode (usually a number in reference to the region) or leave blank
    tox_df['Region'] = tox_df.apply(
        lambda row: row['StationCode'][0] if np.isnan(row['Region']) else row['Region'],
        axis=1
    )

    # Convert Region column to int first (to remove decimal point) and then to string again
    tox_df['Region'] = tox_df['Region'].astype(int)
    tox_df['Region'] = tox_df['Region'].astype(str)

    # Add program fields
    # Assign False to all programs initially
    tox_df['Bioassessment'] = False
    tox_df['Bioaccumulation'] = False
    tox_df['Fhab'] = False
    tox_df['Spot'] = False
    # Overwrite the False values and assign True values based on if the ParentProject value is on the program lists
    tox_df.loc[tox_df['ParentProject'].isin(p_constants.bioassessment_parent_projects), 'Bioassessment'] = True
    tox_df.loc[tox_df['ParentProject'].isin(p_constants.bioaccumulation_parent_projects), 'Bioaccumulation'] = True
    tox_df.loc[tox_df['ParentProject'].isin(p_constants.fhab_parent_projects), 'Fhab'] = True
    tox_df.loc[tox_df['ParentProject'].isin(p_constants.spot_parent_projects), 'Spot'] = True

    # 4/12/23 - Add DisplayText field. This field used to show text in chart tooltips for additional context. Ex. Non-detect. 
    # Can leave blank if there is no text to show
    tox_df.loc[tox_df['ResultQualCode'] == 'ND', 'DisplayText'] = 'Non-detect' # If value in ResultQualCode is 'ND', populate DisplayComment field with 'Non-detect'
    tox_df.loc[tox_df['ResultQualCode'] == 'DNQ', 'DisplayText'] = 'Detected not quantified'

    # If ResultQualCode includes '<' or '>', copy the value over to the DisplayText field
    tox_df.loc[tox_df['ResultQualCode'].str.contains('<|>'), 'DisplayText'] = tox_df['ResultQualCode']

    # For 15 degree samples
    tox_df.loc[(tox_df['Treatment'] == 'Temperature') & (tox_df['UnitTreatment'] == 'Deg C') & (tox_df['TreatmentConcentration'] == 15), 'DisplayText'] = 'Test conducted at a non-standard temperature of 15°C'

    #####  Write data
    print('--- Exporting data')
    tox_file_name = 'swamp_toxicity_data'

    # Write file in dated folder in export folder
    p_utils.write_csv(tox_df, tox_file_name + '_' + p_constants.today, '../../export' + '/' + p_constants.today) 

    print('%s finished running' % os.path.basename(__file__))
