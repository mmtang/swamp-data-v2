'''
Step 3: This script further processes the data exported from Step 2 and calculates annual averages for each station/species/analyte/year combination. Individual and composite records are split and processed/analyzed separately before being joined back together into one dataframe

Updated: 02/29/2024 
'''

import os
import pandas as pd
import sys
import numpy as np
import re

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import p_constants # p_constants.py
import p_utils  # p_utils.py
sys.path.insert(0, './')
import tissue_laa # tissue_laa.py
    

if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))

    print('--- Importing data')
    import_file_path = '../../support_files/swamp_tissue_data_quality.csv'
    tissue_df = pd.read_csv(import_file_path, parse_dates=p_constants.tissue_date_cols, low_memory=False)

    ##### Remove unneeded records or records with missing data elements
    # Filter out records with DataQuality = Metadata or Reject record
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['DataQuality'] == 'MetaData') | (tissue_df['DataQuality'] == 'Reject record')].index)

    # Drop replicate records
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['CollectionReplicate'] != 1)].index)
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['CompositeReplicate'] != 1)].index)
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['ResultsReplicate'] != 1)].index)

    # Drop records that have a null or negative value for Result AND a null or negative MDL. We cannot use a record that does not have a valid value for either field
    tissue_df = tissue_df.drop(tissue_df[((tissue_df['Result'].isna()) | (tissue_df['Result'] < 0)) & ((tissue_df['MDL'].isna()) | (tissue_df['MDL'] < 0))].index)

    # Delete if not needed
    # Drop DNQ/ND records that have a null or negative MDL value
    # tissue_df = tissue_df.drop(tissue_df[((tissue_df['ResultQualCode'] == 'DNQ') | (tissue_df['ResultQualCode'] == 'ND')) & ((tissue_df['MDL'] < 0) | (tissue_df['MDL'].isna()))].index)

    # Added 7/20/22 
    # Drop records with ResultQualCode == '=' and empty Result value
    # These records cause an issue when displaying the station summary data
    tissue_df = tissue_df.drop(tissue_df[((tissue_df['ResultQualCode'] == '=') & (tissue_df['Result'].isna()))].index)

    # Drop records that have a "NR" ResultQualCode value and a null result
    tissue_df = tissue_df.drop(tissue_df[(tissue_df['ResultQualCode'] == 'NR') & (tissue_df['Result'].isna())].index)

    # Added 2/5/24 - Drop data with no sample date
    tissue_df = tissue_df.drop(tissue_df[tissue_df['SampleDate'].isna()].index)

    # Added 2/5/24 - Drop dry weight records. May want to revisit this to include these records in the future
    tissue_df = tissue_df.drop(tissue_df[tissue_df['Unit'] == 'ug/g dw'].index)
    tissue_df = tissue_df.drop(tissue_df[tissue_df['Unit'] == 'NR dw'].index)


    ##### Process data
    # Strip special characters
    tissue_df.replace(r'\t',' ', regex=True, inplace=True) # tab
    tissue_df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    tissue_df.replace(r'\n',' ', regex=True, inplace=True) # newline
    tissue_df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    tissue_df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    tissue_df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    tissue_df.replace(r'\"', ' ', regex=True, inplace=True) # quotes

    # Fill the in NA TissuePrep values as 'None'
    tissue_df['TissuePrep'].fillna('None', inplace=True)

    # Create a SampleYear column based on the SampleDate value
    tissue_df['SampleYear'] = tissue_df['SampleDate'].dt.year

    # Evaluate each record to determine if a substitute value for Result is needed
    nd_values = tissue_df.apply(lambda row: p_utils.get_nd_values(row), axis=1)
    # Copy the output over to new fields in the dataframe
    tissue_df['ResultAdjusted'] = nd_values[0]
    tissue_df['ResultNote'] = nd_values[1]
    tissue_df['NonDetectCount'] = nd_values[2] # If the result is ND, then this value will be 1. This field will be used in the annual average groupings to count how many ND result values were used to calculate an annual average
    tissue_df['NumberOfResults'] = 1 # This field will be used in the annual average groupings to count how many result values (including ND) were used to calculate an annual average

    # Extract Location Code (L1, L2, L3) from the CompositeCompositeID field/value
    pattern = r'(L[1-3]BOG)'
    tissue_df['LocationCodeBOG'] = tissue_df['CompositeCompositeID'].str.extract(pattern, flags=re.IGNORECASE)
    tissue_df['LocationCodeBOG'].fillna('NA', inplace=True) # Fill the values in this column as 'NA' by default
    tissue_df['LocationCodeBOG'] = tissue_df['LocationCodeBOG'].str[:2] # Replace the 'NA' values with the actual location code if there is a valid location code present in the CompositeCompositeid value

    # Create new column designating if the record/result is for an individual sample or composite sample
    tissue_df.loc[tissue_df['NumberFishperComp'] == 1, 'CompositeIndividual'] = 'Individual'
    tissue_df.loc[tissue_df['NumberFishperComp'] > 1, 'CompositeIndividual'] = 'Composite'


    ##### ------ Calculate annual averages for the composite and individual records ----- ######

    # Separate thte individual and composite records into separate dataframes
    composite_records = tissue_df.loc[tissue_df['CompositeIndividual'] == 'Composite']
    individual_records = tissue_df.loc[tissue_df['CompositeIndividual'] == 'Individual']

    # The set of columns used for the first composite grouping
    group_composite_columns = [
        'StationCode', 
        'StationName',
        'CommonName', 
        'FinalID', 
        'TissueName',
        'TissuePrep',
        'CompositeIndividual',
        'NumberFishperComp',
        'DWC_AnalyteWFraction', # Use the 'DWC_AnalyteWFraction' field (instead of the 'Analyte' field) because the values in this field include the fraction and match the analyte values in the other CEDEN datasets
        'Unit',
        #'ResultQualCode',
        'MDL',
        'SampleYear', 
        'ProgramName',
        'ParentProjectName',
        'ProjectCode',
        'ProjectName',
        'TLAvgLength(mm)', # Added 8/18/23, need to group by TLAvgLength(mm) for first grouping because composite records need to be averaged together first before calculating the average for the entire year. See Shadow Cliffs Reservoir, Largemouth Bass, Mercury, 2015, where there are three different composite sets for the year 2015. 
        'TargetLatitude',
        'TargetLongitude',
        'Datum', # Added 9/8/23 to match the current map's data export
        'TissueResultRowID', # Added 8/23/23, use this because there can be multiple composite sets with the same TLAvgLength(mm) value
        'LocationCodeBOG'
    ]

    # The set of columns used for the second composite grouping
    group_composite_columns2 = [
        'StationCode', 
        'StationName',
        'CommonName', 
        'FinalID', 
        'TissueName',
        'TissuePrep',
        'CompositeIndividual',
        #'NumberFishperComp', Removed 8/18/23
        'DWC_AnalyteWFraction',
        'Unit',
        #'ResultQualCode',
        #'MDL', Removed 8/23/23
        'SampleYear', 
        'ProgramName',
        'ParentProjectName',
        'ProjectCode',
        'ProjectName',
        'TargetLatitude',
        'TargetLongitude',
        'Datum', # Added 9/8/23, to match the current map's data export
        #'LocationCodeBOG' # Taken out 2/12/2024 - the current map seems to average location composites
    ]


    # ---- Composite records - calculate annual averages on selected columns using the groupby function
    # This is done twice, each time on a different set of columns
    # To keep the composite sets, do grouping #1 but not grouping #2
    # Even though we are calculating annual averages, LastSampleDate is still needed for the dashboard when displaying the last sample date for each station
    composite_summary_df = composite_records.groupby(group_composite_columns, as_index=False).agg({
        'Result' : 'mean', 
        'ResultAdjusted' : 'mean', 
        'SampleDate' : 'max', 
        'NonDetectCount' : 'sum', 
        'NumberOfResults' : 'sum'
    }).reset_index()

    # Second grouping includes averaging the TLAvgLength(mm)s
    composite_summary2_df = composite_summary_df.groupby(group_composite_columns2, as_index=False).agg({
        'Result' : 'mean', 
        'ResultAdjusted' : 'mean', 
        'TLAvgLength(mm)' : 'mean', 
        'SampleDate' : 'max', 
        'NonDetectCount' : 'sum', 
        'NumberOfResults' : 'sum'
    }).reset_index()

    # Add a ResultType column the same value for all records
    composite_summary2_df['ResultType'] = 'Average of Composites'

    # Drop unneeded columns
    composite_summary2_df = composite_summary2_df.drop(['CompositeIndividual', 'Result'], axis=1)

    # Rename columns
    composite_summary2_df = composite_summary2_df.rename(columns={
        'DWC_AnalyteWFraction': 'Analyte',
        'NonDetectCount': 'ND_in_Avg',
        'NumberOfResults': 'N_in_Avg',
        'ResultAdjusted': 'Result',
        'SampleDate': 'SampleDateMax',
        'LocationCodeBOG': 'LocationCode',
        'TLAvgLength(mm)': 'TLAvgLength_mm'
    })


    # ---- Individual records - calculate annual averages
    # Use the 'get_individual_averages' function from the tissue_laa.py file to process the individual records and calculate the averages. This function will output an array of two dataframes
    individual_summary_df = tissue_laa.get_individual_averages(individual_records)

    laa_output = individual_summary_df[0] # This dataframe is not really needed, but it includes some additional information and statistical output that is useful to have when reviewing the data
    model_avgs_output = individual_summary_df[1] # This is the output we will combine with the composite averages

    # Create a new 'ResultType' field similar to the composite df and include the result type followed by the location code (if present). Example: 'Average of Individuals L1'
    model_avgs_output['ResultType'] = model_avgs_output.apply(lambda row: '{} {}'.format(row['ResultType'], row['LocationCode']) if row['LocationCode'] != 'NA' else row['ResultType'], axis=1)         

    # Write the two output files into the support file folder for reference
    p_utils.write_csv(model_avgs_output, 'model_avgs_output', '../../support_files/')
    p_utils.write_csv(laa_output, 'laa_output', '../../support_files/')  


    # ----- Combine the composite and individual records into one dataframe
    # Put the model_avgs dataframe first to keep the column order
    combined_summary_df = pd.concat([model_avgs_output, composite_summary2_df], ignore_index=True)

    # When concatenating multiple dataframes, if one of the dataframes is missing a column, the values are assigned NaN. The composite df does not keep LocationCode in the second grouping, so these records will be assigned NaN after concatenating the two dfs. Replace the NaN values with 'NA'
    combined_summary_df['LocationCode'].fillna('NA', inplace=True)

    # Rename columns
    combined_summary_df = combined_summary_df.rename(columns={
        'ProgramName' : 'Program',
        'ParentProjectName' : 'ParentProject',
        'ProjectName' : 'Project',
        'SampleDateMax' : 'LastSampleDate', # Rename 'SampleDateMax' field to LastSampleDate 
    })

    # Round the calculated columns to 2 decimal places
    combined_summary_df['Result'] = combined_summary_df['Result'].round(2)
    combined_summary_df['TLAvgLength_mm'] = combined_summary_df['TLAvgLength_mm'].round(2)

    # Change date format to the standard format used by the open data portal. This format is required for querying date values using the open data portal API
    combined_summary_df['LastSampleDate'] = combined_summary_df['LastSampleDate'].dt.strftime('%Y-%m-%dT%H:%M:%S')

    # Create an AnalyteDisplay field, which is a copy of the Analyte field with some changes (if necessary)
    # The AnalyteDisplay field is used by the web application
    combined_summary_df['AnalyteDisplay'] = combined_summary_df['Analyte'].copy()

    # Add AnalyteGroup column
    combined_summary_df['AnalyteGroup1'] = 'Tissue'

    # Add MatrixDisplay field - needed for the dashboard
    combined_summary_df['MatrixDisplay'] = 'tissue'

    # ----- Add Region field
    stations_df = p_utils.import_csv('../../support_files/swamp_stations.csv', date_cols=['LastSampleDate']) # Import station data
    station_cols = stations_df[['StationCode', 'Region']] # Get a subset of the columns
    combined_summary_df = pd.merge(combined_summary_df, station_cols, how='left', on='StationCode') # Join the region values
    # After joining, some records will have a blank region value. Use the first character of StationCode (usually a number in reference to the region) or leave blank
    combined_summary_df['Region'] = combined_summary_df.apply(
        lambda row: row['StationCode'][0] if np.isnan(row['Region']) else row['Region'],
        axis=1
    )
    # Convert Region column to int first (to remove decimal point) and then to string again
    combined_summary_df['Region'] = combined_summary_df['Region'].astype(int)
    combined_summary_df['Region'] = combined_summary_df['Region'].astype(str)

    # ----- Add Program fields
    # Assign False to all programs initially
    combined_summary_df['Bioassessment'] = False
    combined_summary_df['Bioaccumulation'] = False
    combined_summary_df['Fhab'] = False
    combined_summary_df['Spot'] = False

    # Overwrite the False values and assign True values based on if the ParentProject value is on the program lists
    # 2/5/24 - Per Anna's suggestion, give state assignments to all regional projects. Historically, regions have conducted monitoring supporting the statewide program. This might change in the future.
    bioaccumulation_regional_projects = [
        'SWAMP RWB1 Monitoring', 
        'SWAMP RWB2 Monitoring',
        'SWAMP RWB3 CCAMP Harbors Study',
        'SWAMP RWB3 CCAMP Lakes Study',
        'SWAMP RWB3 CCAMP Salinas Rotation',
        'SWAMP RWB3 CCAMP Santa Barbara Rotation',
        'SWAMP RWB3 CCAMP SpecialStudies',
        'SWAMP RWB4 Monitoring',
        'SWAMP RWB6 Monitoring',
        'SWAMP RWB7 Monitoring',
        'SWAMP RWB8 Monitoring',
        'SWAMP RWB9 Monitoring'
    ]
    
    # Bioassessment
    combined_summary_df.loc[combined_summary_df['ParentProject'].isin(p_constants.bioassessment_parent_projects), 'Bioassessment'] = True

    # ----- Bioaccumulation
    # Add the bioaccumulation regional and statewide projects to create one array
    all_bioaccumulation_parprojects = bioaccumulation_regional_projects + p_constants.bioaccumulation_parent_projects
    combined_summary_df.loc[combined_summary_df['ParentProject'].isin(all_bioaccumulation_parprojects), 'Bioaccumulation'] = True

    # FHAB
    combined_summary_df.loc[combined_summary_df['ParentProject'].isin(p_constants.fhab_parent_projects), 'Fhab'] = True

    # SPoT
    combined_summary_df.loc[combined_summary_df['ParentProject'].isin(p_constants.spot_parent_projects), 'Spot'] = True

    # Add Reference Site column
    ref_sites_df = p_utils.import_csv(p_constants.reference_sites_file)
    ref_cols = ref_sites_df[['cedenid', 'StationCategory']] 
    combined_summary_df = pd.merge(combined_summary_df, ref_cols, how='left', left_on=combined_summary_df['StationCode'].str.lower(), right_on=ref_cols['cedenid'].str.lower())
    combined_summary_df = combined_summary_df.drop('cedenid', axis=1)

    # Add Data Quality columns with "Not assessed" for each record. Even though we ran the data through the data quality checker in the 2nd script, this information was lost after the composite groupings and calculating the annual averages for the inidividual records. The data in its current form cannot be run through the data quality checker again
    combined_summary_df['DataQuality'] = 'Not assessed'
    combined_summary_df['DataQualityIndicator'] = None

    # Add Censored column, used by the web application
    combined_summary_df.loc[combined_summary_df['ND_in_Avg'] == 0, 'Censored'] = False
    combined_summary_df.loc[combined_summary_df['ND_in_Avg'] > 0, 'Censored'] = True

    # Add DisplayText column, this value is displayed in the web application
    combined_summary_df['DisplayText'] = combined_summary_df['ND_in_Avg'].apply(lambda x: 'Calculation includes ND results' if x > 0 else None)

    order_columns = [
        'Program',
        'ParentProject',
        'ProjectCode',
        'Project',
        'StationCode',
        'StationName',
        'LocationCode',
        'CommonName',
        'FinalID',
        'TissueName',
        'TissuePrep',
        'Analyte',
        'Result',
        'Unit',
        'ResultType',
        'ND_in_Avg',
        'N_in_Avg',
        'Censored',
        'TLAvgLength_mm',
        'LastSampleDate',
        'SampleYear',
        'TargetLatitude',
        'TargetLongitude',
        'Datum',
        'DataQuality',
        'AnalyteDisplay',
        'AnalyteGroup1',
        'MatrixDisplay',
        'Region',
        'Bioaccumulation',
        'Bioassessment', 
        'Fhab',
        'Spot',
        'StationCategory',
        'DisplayText'
    ]

    # Reorder fields
    combined_summary_df = combined_summary_df[order_columns]


    #----- Write the export files
    # Write the summary df to the support_files folder
    export_file_name = 'swamp_tissue_summary_data'
    outdir = '../../support_files/'
    p_utils.write_csv(combined_summary_df, 'swamp_tissue_summary_data', outdir)

    # Write the summary file (dated) to a dated folder in the export folder
    p_utils.write_csv(combined_summary_df, export_file_name + '_' + p_constants.today, '../../export' + '/' + p_constants.today) 


