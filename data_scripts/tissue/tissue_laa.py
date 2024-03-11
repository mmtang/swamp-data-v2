'''
The code in this script file is used in Step 3 of the tissue data workflow. The main function takes in a dataframe of individual result records and calculates annual averages (average of individuals, average of individuals over 305mm, or the 350mm length-adjusted average) based on certain criteria or groupings (more information below). All of the code in this script is heavily based off the R code provided to us by SFEI in December 2023 with some modifications.

Updated: 02/29/2024 
'''

import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime
from re import sub
from scipy.stats import sem


def get_individual_averages(input_df):
    # ----- 1) Import data and initial prep
    df = input_df.copy()
    df = df[df['TLAvgLength(mm)'].notna()] # Need to ensure that there are no NA values in the length column or the statsmodels package will throw some errors

    # Create new dataframe for calculating residuals, group by specified columns
    # 12/19/23 MT - Added dropna=False
    grouped = df.groupby([
        'StationCode', 
        'StationName', 
        'LocationCodeBOG', 
        'CommonName', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ], dropna=False)


    # ----- 2) Get residuals (within a station, location, species group for the linear model)
    # Define a function to calculate residuals using linear regression
    def calculate_resids(group):
        X = group['TLAvgLength(mm)']
        y = group['ResultAdjusted']
        X1 = sm.add_constant(X)  # Add a constant term for the intercept
        model = sm.OLS(y, X1).fit()
        group['Residuals'] = model.resid # 12/19/23 Renamed 'resids' to 'Residuals' (this doesn't really matter much, just saves an extra step)
        return group
    
    # Apply the function to each group within the grouped DataFrame
    res = grouped.apply(calculate_resids).reset_index(drop=True) 

    # Select the needed columns
    # 12/19/23 MT - Added 'TissueResultRowID'. This column will be used for the merge function below
    res = res[[
        'StationCode', 
        'StationName', 
        'CommonName', 
        'LocationCodeBOG',
        'TissueResultRowID', 
        'Residuals', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ]]

    # Add residuals to original dataframe in a new column called "Residuals"
    # 12/19/23 MT - This way of adding the residuals back to the original df does not work as expected because both dataframes have different sizes. This results in a lot of empty values because only the first # rows get populated. Use the merge/join functiom below
    #df['Residuals'] = res['resids']

    # 12/19/23 MT - Add TissueResultRowID as one of the join columns. Without this column, this merge operation will join all grouping rows to each matching row in the original DF, resulting in a lot of duplicate rows.
    df = pd.merge(df, res, on=[
        'StationCode', 
        'StationName', 
        'CommonName', 
        'LocationCodeBOG', 
        'TissueResultRowID', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ], how = "left")  

    # 12/19/23 MT - Convert object type to float
    df['Residuals'] = df['Residuals'].astype('float') 


    # ----- 3) Get predictions and significance of regression to calculate length adjusted results
    # Get predictions at 350mm and significance of regression for Station, Location, Species grouping.  Calculate the p-value of f-statistic (run on the groupby function)

    def calculate_predictions(group):
        model = sm.OLS(group['ResultAdjusted'], sm.add_constant(group['TLAvgLength(mm)'])).fit()
        predicted_at_350 = model.predict([1, 350])[0]  # Extract the first element of the predicted array
        significance = model.f_pvalue
        return pd.Series({'PredictedAt350': predicted_at_350, 'Significance': significance})

    # 12/19/23 - Added dropna=False
    predictions = df.groupby([
        'StationCode', 
        'StationName', 
        'LocationCodeBOG', 
        'CommonName', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ], dropna=False).apply(calculate_predictions).reset_index() 

    # 12/19/23 - Significance is object type for some reason, convert to float
    predictions['Significance'] = predictions['Significance'].astype('float') 

    # Merge predictions back to the main dataframe
    df = pd.merge(df, predictions, on=[
        'StationCode', 
        'StationName', 
        'LocationCodeBOG', 
        'CommonName', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ], how = "left")

    # Sum the residuals and predicted concentrations to get a length adjusted result
    df['LengthAdjustedResult'] = df['Residuals'] + df['PredictedAt350']


    # ----- 4) Create a new dataframe with averages of the Length Adjusted Results for each station
    # 12/19/23 - Added dropna=False 
    laa = df.groupby([
        'StationCode', 
        'StationName', 
        'CommonName', 
        'LocationCodeBOG', 
        'Significance', 
        'DWC_AnalyteWFraction', 
        'Unit', 
        'SampleYear', 
        'FinalID', 
        'ProgramName', 
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum', 
        'ParentProjectName', 
        'ProjectName', 
        'ProjectCode', 
        'TissueName', 
        'TissuePrep'
    ], dropna=False) 

    # Add additional calculated fields
    laa = pd.DataFrame({
        'LengthAdjustedAverage': laa['LengthAdjustedResult'].mean(),
        'seLengthAdjusted': laa.apply(lambda x: (x['LengthAdjustedResult'].std() / (x['LengthAdjustedResult'].count() ** 0.5))),
        'SampleDateMax': laa['SampleDate'].max(),
        'N': laa['ResultAdjusted'].count(),
        'N_Above305mm': laa.apply(lambda x: x[x['TLAvgLength(mm)'] >= 305]['ResultAdjusted'].count()),
        'N_NonDetects': laa['NonDetectCount'].sum(),
        'SimpleMean': laa['ResultAdjusted'].mean(),
        'SimpleMean_Above305mm': laa.apply(lambda x: x[x['TLAvgLength(mm)'] >= 305]['ResultAdjusted'].mean()),
        'TwoXse': 2 * ((laa['ResultAdjusted'].std()) / (laa['ResultAdjusted'].count() ** 0.5)),
        'TwoXse_Above305mm': laa.apply(lambda x: 2 * (x[x['TLAvgLength(mm)'] >= 305]['ResultAdjusted'].std() / (x[x['TLAvgLength(mm)'] >= 305]['ResultAdjusted'].count() ** 0.5))),
        'TLAvgLength(mm)': laa['TLAvgLength(mm)'].mean()
    })

    laa = laa.reset_index() # Ungroup


    # ----- 5) Filter rows based on conditions
    ## Create a list of bass species and analytes that will use the length adjusted averages
    BassLAASpecies = ["Largemouth Bass", "Smallmouth Bass", "Spotted Bass"]
    LAA_Analytes = ['Mercury, Total']

    # Conditionally populate ResultType in the output based on various criteria
    laa['ResultType'] = laa.apply(lambda row: 'Average of 350 mm Length-Adjusted' if row['Significance'] <= 0.05 and not pd.isna(row['Significance']) and row['N'] >= 7 and row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes else ('Average of Individuals >=305 mm' if row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes and row['DWC_AnalyteWFraction'] in LAA_Analytes and row['N_Above305mm'] > 0 else 'Average of Individuals'), axis=1) 

    # Conditionally populate Result in the output based on various criteria
    laa['Result'] = laa.apply(lambda row: row['LengthAdjustedAverage'] if row['Significance'] <= 0.05 and not pd.isna(row['Significance']) and row['N'] >= 7 and row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes else (row['SimpleMean_Above305mm'] if row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes and row['N_Above305mm'] > 0 else row['SimpleMean']), axis=1)

    # Conditionally populate 'N in Avg' in the output based on various criteria
    laa['N in Avg'] = laa.apply(lambda row: row['N'] if row['Significance'] <= 0.05 and not pd.isna(row['Significance']) and row['N'] >= 7 and row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes else (row['N_Above305mm'] if row['CommonName'] in BassLAASpecies and row['DWC_AnalyteWFraction'] in LAA_Analytes and row['N_Above305mm'] > 0 else row['N']), axis=1)


    # ----- 6) Set up a dataframe that will serve as the ouput, to be combined with the composite averages (NumberInComposite now really indicates number in avg)
    modelAvgs = laa[[
        'ProgramName', 
        'ParentProjectName', 
        'ProjectCode', 
        'ProjectName', 
        'StationCode',
        'StationName',
        'LocationCodeBOG',
        'DWC_AnalyteWFraction',
        'Result',
        'Unit',
        'ResultType',
        'N in Avg',
        'N_NonDetects',
        'CommonName',
        'FinalID',
        'TissueName',
        'TissuePrep',
        'TLAvgLength(mm)',
        'SampleDateMax',
        'SampleYear',
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum'
    ]]

    # Rename the columns               
    modelAvgs.rename(columns = {
        'LocationCodeBOG':'LocationCode',
        'N in Avg': 'N_in_Avg',
        'N_NonDetects':'ND_in_Avg',
        'DWC_AnalyteWFraction': 'Analyte',
        'TLAvgLength(mm)': 'TLAvgLength_mm'
    }, inplace = True) 

    # Rewrite the average length value for the length-adjusted averages. They are all predicted values at 350mm
    modelAvgs.loc[modelAvgs['ResultType'] == 'Average of 350 mm Length-Adjusted', 'TLAvgLength_mm'] = 350


    # ------- 7) Set up another dataframe with Standard error (se) of LAA and Significance of F for model
    laa_output = laa[[
        'ProgramName', 
        'ParentProjectName', 
        'ProjectCode', 
        'ProjectName', 
        'StationCode',
        'StationName',
        'LocationCodeBOG',
        'CommonName',
        'FinalID', 
        'TissueName',
        'TissuePrep',
        'SampleYear',
        'DWC_AnalyteWFraction',
        'Unit',
        'Result',
        'ResultType',
        'LengthAdjustedAverage',
        'seLengthAdjusted',
        'Significance',
        'SimpleMean_Above305mm',
        'TwoXse_Above305mm',
        'SimpleMean',
        'TwoXse',
        'N in Avg',
        'N_NonDetects',
        'TargetLatitude', 
        'TargetLongitude', 
        'Datum'
    ]]

    # Rename the columns               
    laa_output.rename(columns = {
        'seLengthAdjusted':'se (length adj)',
        'SimpleMean_Above305mm':'SimpleMean >=305mm',
        'TwoXse_Above305mm':'2*se >=305mm',
        'TwoXse':'2*se',
        'LocationCodeBOG':'LocationCode',
        'N in Avg': 'N_in_Avg',
        'N_NonDetects':'ND_in_Avg',
        'DWC_AnalyteWFraction': 'Analyte'
    }, inplace = True) 

    # Output both dataframes
    return [laa_output, modelAvgs]
