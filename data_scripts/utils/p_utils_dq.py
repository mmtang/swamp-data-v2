import re

# DICTIONARIES
# The following dictionaries refer to codes and their corresponding data quality value as determined by
# Melissa Morris of SWRCB, Office of Information Management and Analysis. 
# 0: QC record, 1: Passed QC, 2: Needs some review, 3: Spatial Accuracy Unknown, 4: Needs extensive review, 5: unknown data quality, 6: reject data record
# (as of 1/22/18)

# These codes not included in this dictionary and currently skipped over later in the script: VFIRL, ROQ, H6, BRK
# Need to check with David, Melissa, Andrew?
QA_Code_list = {"AWM": 1, "AY": 2, "BB": 2, "BBM": 2, "BCQ": 1, "BE": 2, "BH": 1, "BLM": 4, "BRKA": 2, "BS": 2,
                    "BT": 6, "BV": 2, "BX": 4, "BY": 4, "BZ": 4, "BZ15": 2, "C": 1, "CE": 4, "CIN": 2, "CJ": 2, "CNP": 2,
                    "CQA": 1, "CS": 2, "CSG": 2, "CT": 2, "CVH": 1, "CVHB": 4, "CVL": 1, "CVLB": 4, "CZM": 2, "D": 1,
                    "DB": 2, "DBLOD": 2, "DBM": 2, "DF": 2, "DG": 1, "DO": 1, "DRM": 2, "DS": 1, "DT": 1, "ERV": 4, "EUM": 4,
                    "EX": 4, "F": 2, "FCL": 2, "FDC": 2, "FDI": 2, "FDO": 6, "FDP": 2, "FDR": 1, "FDS": 1, "FEU": 6, "FIA": 6,
                    "FIB": 4, "FIF": 6, "FIO": 4, "FIP": 4, "FIT": 2, "FIV": 6, "FLV": 2, "FNM": 6, "FO": 2, "FS": 6, "FTD": 6,
                    "FTT": 6, "FUD": 6, "FX": 4, "GB": 2, "GBC": 4, "GC": 1, "GCA": 1, "GD": 1, "GN": 4, "GR": 4, "H": 2, "H22": 4,
                    "H24": 4, "H8": 2, "HB": 2, "HD": 4, "HH": 2, "HNO2": 2, "HR": 1, "HS": 4, "HT": 1, "IE": 2, "IF": 2, "IL": 4,
                    "ILM": 2, "ILN": 2, "ILO": 2, "IM": 2, "IP": 4, "IP5": 4, "IPMDL2": 4, "IPMDL3": 4, "IPRL": 4, "IS": 4,
                    "IU": 4, "IZM": 2, "J": 2, "JA": 2, "JDL": 2, "LB": 2, "LC": 4, "LRGN": 6, "LRIL": 6, "LRIP": 6, "LRIU": 6,
                    "LRJ": 6, "LRJA": 6, "LRM": 6, "LRQ": 6, "LST": 6, "M": 2, "MAL": 1, "MN": 4, "N": 2, "NAS": 2, "NBC": 2,
                    "NC": 1, "NG": 1, "NMDL": 1, "None": 1, "NR": 5, "NRL": 1, "NTR": 1, "OA": 2, "OV": 2, "P": 4, "PG": 4,
                    "PI": 4, "PJ": 1, "PJM": 1, "PJN": 1, "PP": 4, "PRM": 4, "Q": 4, "QAX": 1, "QG": 4, "R": 6, "RE": 1, "REL": 1,
                    "RIP": 6, "RIU": 6, "RJ": 6, "RLST": 6, "RPV": 4, "RQ": 2, "RU": 4, "RY": 4, "SC": 1, "SCR": 2, "SLM": 1, "TA": 4,
                    "TAC": 1, "TC": 4, "TCI": 4, "TCT": 4, "TD": 4, "TH": 4, "THS": 4, "TK": 4, "TL": 2, "TNC": 2, "TNS": 1, "TOQ": 4,
                    "TP": 4, "TR": 6, "TS": 4, "TW": 2, "UF": 2, "UJ": 2, "UKM": 4, "ULM": 4, "UOL": 2, "VCQ": 2, "VQN": 2, "VC": 2,
                    "VBB": 2, "VBS": 2, "VBY": 4, "VBZ": 4, "VBZ15": 2, "VCJ": 2, "VCO": 2, "VCR": 2, "VD": 1, "VDO": 1, "VDS": 1,
                    "VELB": 1, "VEUM": 4, "VFDP": 2, "VFIF": 6, "VFNM": 6, "VFO": 2, "VGB": 2, "VGBC": 4, "VGN": 4, "VH": 2, "VH24": 4,
                    "VH8": 2, "VHB": 2, "VIE": 2, "VIL": 4, "VILN": 4, "VILO": 2, "VIP": 4, "VIP5": 4, "VIPMDL2": 4, "VIPMDL3": 4,
                    "VIPRL": 4, "VIS": 4, "VIU": 4, "VJ": 2, "VJA": 2, "VLB": 2, "VLMQO": 2, "VM": 2, "VNBC": 2, "VNC": 1, "VNMDL": 1,
                    "VNTR": 1, "VPJM": 1, "VPMQO": 2, "VQAX": 1, "VQCA": 4, "VQCP": 4, "VR": 6, "VRBS": 6, "VRBZ": 6, "VRDO": 6,
                    "VRE": 1, "VREL": 1, "VRGN": 6, "VRIL": 6, "VRIP": 6, "VRIU": 6, "VRJ": 6, "VRLB": 6, "VRLST": 6, "VRQ": 2,
                    "VRVQ": 6, "VS": 2, "VSC": 1, "VSCR": 2, "VSD3": 1, "VTAC": 1, "VTCI": 4, "VTCT": 4, "VTNC": 2, "VTOQ": 4, "VTR": 6,
                    "VTW": 4, "VVQ": 6, "WOQ": 4,  }
BatchVerification_list = {"NA": 5, "NR": 5, "VAC": 1, "VAC,VCN": 6, "VAC,VMD": 2, "VAC,VMD,VQI": 4,
                                  "VAC,VQI": 4, "VAC,VR": 6, "VAF": 1, "VAF,VMD": 2, "VAF,VQI": 4, "VAP": 1,
                                  "VAP,VI": 4, "VAP,VQI": 4, "VCN": 6, "VLC": 1, "VLC,VMD": 2, "VLC,VMD,VQI": 4,
                                  "VLC,VQI": 4, "VLF": 1, "VMD": 2, "VQI": 4, "VQI,VTC": 4, "VQN": 5, "VR": 6, "VTC": 2}
ResultQualCode_list = {"/oC": 4, "<": 1, "<=": 1, "=": 1, ">": 1, ">=": 1, "A": 1, "CG": 4, "COL": 1, "DNQ": 2,
                           "JF": 1, "NA": 6, "ND": 1, "NR": 6, "NRS": 6, "NRT": 6, "NSI": 1, "P": 1, "PA": 1, "w/C": 4,
                           "": 1, "Systematic Contamination": 4, }
Latitude_list = {"-88": 0, "": 6, '0.0': 6, -88: 0 }
Result_list = {"": 1, }
StationCode_list = {"LABQA": 0, "LABQA_SWAMP": 0, "000NONPJ": 0, "FIELDQA": 0, "Non Project QA Sample": 0,
                    "Laboratory QA Sample": 0, "Field QA sample": 0, "FIELDQA SWAMP": 0, "000NONSW": 0, "FIELDQA_SWAMP": 0}
SampleTypeCode_list = {"LabBlank": 0, "CompBLDup": 0, "LCS": 0, "CRM": 0, "FieldBLDup_Grab": 0, "FieldBLDup_Int": 0,
                        "FieldBLDup": 0, "FieldBlank": 0, "TravelBlank": 0, "EquipBlank": 0, "DLBlank": 0,
                        "FilterBlank": 0, "MS1": 0, "MS2": 0, "MS3": 0, "MSBLDup": 0, }
SampleDate_list = {"Jan  1 1950 12:00AM": 0, }
MatrixName_list = {"blankwater": 0, "Blankwater": 0, "labwater": 0, "blankmatrix": 0, }
CollectionReplicate_list = {"0": 1, "1": 1, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, }
ResultsReplicate_list = {"0": 1, "1": 1, "2": 0, "3": 0, "4": 0, "5": 0, "6": 0, "7": 0, "8": 0, }
Datum_list = {"NR": 3, }
DQ_Codes = {0: "MetaData", 1: "Passed", 2: "Some review needed", 3: "Spatial accuracy unknown",
            4: "Extensive review needed", 5: "Unknown data quality", 6: "Reject record", 7: 'Error in data'}

# dictionary of dictionaries
CodeColumns = {
    "QACode": QA_Code_list,
    "BatchVerification": BatchVerification_list,
    "ResultQualCode": ResultQualCode_list,
    "TargetLatitude": Latitude_list,
    "Result": Result_list,
    "StationCode": StationCode_list,
    "SampleTypeCode": SampleTypeCode_list,
    "SampleDate": SampleDate_list,
    "MatrixName": MatrixName_list,
    "CollectionReplicate": CollectionReplicate_list,
    "ResultsReplicate": ResultsReplicate_list,
    "Datum": Datum_list
}

def check_latitude(val):
    try:
        lat = float(val)
        return lat
    except ValueError:
        # a missing latitude value (and non-numeric values) should throw an error
        # missing values should be encoded as 'NaN' to define data type as numeric on open data portal
        return 'NaN'

def check_longitude(val):
    try:
        long = float(val)
        if 0. < long < 10000.0:
            val = -long
        return val
    except ValueError:
        # a missing longitude value (and non-numeric values) should throw an error
        # missing values should be encoded as 'NaN' to define data type as numeric on open data portal
        return 'NaN'

def clean_data(df):
    # Clean null values. We have to make a distinction between None, 'None', and ''
    # 'None' and '' are used specifically in the datasets, but None gets translated to 'None' unless we replace it with '' explicitly
    # df.fillna('')

    # Strip special characters
    df.replace(r'\t',' ', regex=True, inplace=True) # tab
    df.replace(r'\r',' ', regex=True, inplace=True) # carriage return
    df.replace(r'\n',' ', regex=True, inplace=True) # newline
    df.replace(r'\f',' ', regex=True, inplace=True) # formfeed
    df.replace(r'\v',' ', regex=True, inplace=True) # vertical tab
    df.replace(r'\|', ' ', regex=True, inplace=True) # pipe
    df.replace(r'\"', ' ', regex=True, inplace=True) # quotes

    # Process the data to make sure the fields are compatible with the portal’s data type definition. 
    # For numeric, make sure that all values can be recognized as a number. Missing values have to be encoded as "NaN". 
    # For dates, the data has to be formatted as YYYY-MM-DD (you can also add a time to that - YYYY-MM-DD HH:MM:SS), and missing values have to be encoded as an empty text string ("").

    # Check numeric columns
    numeric_cols = ['CollectionDepth', 'CollectionReplicate', 'ResultsReplicate', 'Result']
    for col in numeric_cols:
        try:
            df[col].fillna('NaN')
        except:
            print('%s field does not exist for dataframe' % col)

    # Check latitude and longitude values (numeric)
    # sometimes the Longitude gets entered as 119 instead of -119...
    # make sure Longitude value is negative and less than 10000 (could be projected)
    # check for missing and non-numeric values, replace with 'NaN'
    df['TargetLatitude'] = df['TargetLatitude'].map(check_latitude).fillna('NaN')
    df['TargetLongitude'] = df['TargetLongitude'].map(check_longitude).fillna('NaN')

    df.fillna('')
    
    return df

def add_data_quality(df):
    # Function for adding QACode data quality codes and scores to DQ dictionary
    def add_QACode(row):
        col = 'QACode'
        values = row[col].split(',')
        for i in values:
            try:
                DQ.append({'col': col, 'code': i, 'score': QA_Code_list[i]})
            except:
                print(i + ' not a valid key in  QA_Code_list')

    # Function for adding StationCode data quality codes and scores to DQ dictionary
    def add_StationCode(row):
        col = 'StationCode'
        val = row[col]
        if bool(re.search('000NONPJ', val)):
            # if a record has 000NONPJ or any variant in the StationCode value, add 0 to DQ
            DQ.append({'col': col, 'code': '000NONPJ', 'score': 0})
        elif val in StationCode_list:
            DQ.append({'col': col, 'code': val, 'score': StationCode_list[val]})

    # Function for adding Analyte data quality codes and scores to DQ dictionary
    def add_Analyte(row):
        col = 'Analyte'
        value = row[col]
        # If the analyte name contains 'surrogate', mark DQ with a 0
        if bool(re.search('[Ss]urrogate', row[col])):
            DQ.append({'col': col, 'code': row[col], 'score': 0})

    # Function for adding ResultQualCode data quality codes and scores to DQ dictionary
    def add_ResultQualCode(row):
        col = 'ResultQualCode'
        val = row[col]
        # special cases for ResQualCode
        year = row['SampleDate'].year
        if val == 'DNQ' and year < 2008:
            DQ.append({'col': col, 'code': val, 'score': ResultQualCode_list[val]})
        elif val == 'ND':
            # the Benthic dataset can have an ND value as long as the result
            # is not positive. Record is a pass if less than or equal to zero
            # reject if result is positive
            try:
                result = row['Result']
                if isinstance(result, (int, float)) and result > 0:
                    DQ.append({'col': col, 'code': val, 'score': 6})
                else:
                    DQ.append({'col': col, 'code': val, 'score': 1})
            except KeyError:
                DQ.append({'col': col, 'code': val, 'score': 1})
        # End of Special Rules for ResultQualCode
        # check each value in the code dictionary and add numerical value to DQ
        elif val in ResultQualCode_list:
            DQ.append({'col': col, 'code': val, 'score': ResultQualCode_list[val]})

    # Function for adding Result data quality codes and scores to DQ dictionary
    def add_Result(row):
        col = 'Result'
        val = row[col]
        # Results can be empty if ResultQualCode == 'ND'
        if val == '' and row['ResultQualCode'] == 'ND':
            DQ.append({'col': col, 'code': val, 'score': 1})
        else:
            # All other values, look up in code dictionary
            if val in Result_list:
                DQ.append({'col': col, 'code': val, 'score': Result_list[val]})

    def add_BatchVerification(row):
        try:
            col = 'BatchVerification'
            val = row[col]
            if val in BatchVerification_list:
                DQ.append({'col': col, 'code': val, 'score': BatchVerification_list[val]})
        except:
            pass

    def add_Latitude(row):
        col = 'TargetLatitude'
        val = row[col]
        if val in Latitude_list:
            DQ.append({'col': col, 'code': val, 'score': Latitude_list[val]})

    def add_SampleTypeCode(row):
        col = 'SampleTypeCode'
        val = row[col]
        if val in SampleTypeCode_list:
            DQ.append({'col': col, 'code': val, 'score': SampleTypeCode_list[val]})

    def add_SampleDate(row):
        col = 'SampleDate'
        year = row[col].year
        if year == 1950:
            DQ.append({'col': col, 'code': row[col], 'score': 0})

    def add_MatrixName(row):
        col = 'MatrixName'
        val = row[col]
        if val in MatrixName_list:
            DQ.append({'col': col, 'code': val, 'score': MatrixName_list[val]})

    def add_CollectionReplicate(row):
        col = 'CollectionReplicate'
        val = row[col]
        if val in CollectionReplicate_list:
            DQ.append({'col': col, 'code': val, 'score': CollectionReplicate_list[val]})

    def add_ResultsReplicate(row):
        try:
            col = 'ResultsReplicate'
            val = row[col]
            if val in ResultsReplicate_list:
                DQ.append({'col': col, 'code': val, 'score': ResultsReplicate_list[val]})
        except:
            pass

    def add_Datum(row):
        col = 'Datum'
        val = row[col]
        if val in ResultsReplicate_list:
            DQ.append({'col': col, 'code': val, 'score': Datum_list[val]})
        
    for index, row in df.iterrows():
        # Initialize a list of dictionaries
        # ex. [{col: ###, code: ###, score: #}}, ...]
        DQ = []

        # Go through each column and append DQ dictionaries to DQ
        add_QACode(row)
        add_StationCode(row)
        add_Analyte(row)
        add_ResultQualCode(row)
        add_Result(row)
        add_BatchVerification(row)
        add_Latitude(row)
        add_SampleTypeCode(row)
        add_SampleDate(row)
        add_MatrixName(row)
        add_CollectionReplicate(row)
        add_ResultsReplicate(row)
        add_Datum(row)

        # A word about that DQ variable:
        # DQ might host a long list of numbers but if there is ever a zero, that whole
        # record should be classified as a QC record. If there isnt a zero and the
        # maximum value is a 1, then that record passed our data quality estimate
        # unblemished. If there isn't a zero and the max DQ values is greater than 1,
        # then ... we get the max value and store the corresponding value (from the
        # DQ_Codes dictionary, defined above). If the Max DQ is 6 (which is a reject
        # record) and QInd is empty, then this is a special rule case and we label it as
        # such. Otherwise, we throw all of the QInd information into the Quality
        # indicator column. QInd might look like:
        #   ['ResQualCode:npr,kqed', 'BatchVerificationCode:lol,btw,omg', ]
        # and the this gets converted and stored into the records new column called Data
        # Quality indicator a:
        # 'ResQualCode:npr,kqed; BatchVerificationCode:lol,btw,omg'

        # Find the min and max DQ scores
        min_DQ = min(i['score'] for i in DQ)
        max_DQ = max(i['score'] for i in DQ)

        # Determine the DQ variable for the data record
        if min_DQ == 0:
            df.at[index, 'DataQuality'] = DQ_Codes[0]
            df.at[index, 'DataQualityIndicator'] = ''
        elif max_DQ == 1:
            df.at[index, 'DataQuality'] = DQ_Codes[1]
            df.at[index, 'DataQualityIndicator'] = ''
        else:
            # Data quality score
            df.at[index, 'DataQuality'] = DQ_Codes[max_DQ]

            # Data quality indicator:
            # iterate through all the code matches again and append all where score = max DQ to new list. This is in case there are mulitple codes sharing the same max DQ.
            equal_max_DQ = []
            for i in DQ:
                if i['score'] == max_DQ:
                    equal_max_DQ.append(i)

            # join array items to form the DQ indicator column value
            DQ_indicator = '; '.join(map(str, [i['col'] + ':' + i['code'] for i in equal_max_DQ]))
            
            # write to record dictionary
            if max_DQ == 6 and DQ_indicator == '':
                df.at[index, 'DataQualityIndicator'] = 'ResultQualCode Special Rules'
            else:
                df.at[index, 'DataQualityIndicator'] = DQ_indicator

    # Return the dataframe with the added DQ columns
    return df
