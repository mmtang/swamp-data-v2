'''
Shared variables used across multiple (or all) scripts
'''

from datetime import datetime
import os


# Environment variables for accessing CEDEN Data marts
SERVER1 = os.environ.get('SERVER1')
UID = os.environ.get('UID')
PWD = os.environ.get('PWD')

# Environment variables for the open data portal
HOST = os.environ.get('CK_host')
KEY = os.environ.get('CK_key') 

allowed_nans = ['', '#N/A', '#N/A N/A', '#NA', '-1.#IND', '-1.#QNAN',
                '-NaN', '-nan', '1.#IND', '1.#QNAN', '<NA>', 'N/A', 'NA',
                'NULL', 'NaN', 'nan', 'null']

# Relative location of analyte list file used for assigning analyte categories
analyte_list_file = '../../assets/joined_analyte_list_3-21-23.csv'

# ParentProject values identifying what data records belong to which statewide programs
bioassessment_parent_projects = [
    'SWAMP California Monitoring and Assessment Program',
    'SWAMP Perennial Stream Surveys',
    'SWAMP Reference Condition Management Plan',
    'Statewide Field Repeat Sampling Study',
    'Statewide Low Gradient Methods Comparison',
    'SWAMP Repeat Sampling Field Methods Comparison',
    'Statewide Sediment TMDL Study'
]

bioaccumulation_parent_projects = [
    'SWAMP Bioaccumulation Monitoring Program',
    'SWAMP Historic Bioaccumulation Data',
    'SWAMP Sportfish Coastal Zones',
    'SWAMP Sportfish Contamination in Lakes and Resrv',
    'SWAMP Sportfish Rivers and Streams',
    'SWAMP Wildlife Contamination in Lakes and Resrv'
]

# To include CSCI and IPI scores from the following SWAMP and SWAMP adjacent 
habitat_programs = [
    'EPA National Rivers and Streams Assessment',
    'Southern CA Stormwater Monitoring Coalition',
    'Surface Water Ambient Monitoring Program',
    'SW Mon Coalition Regional Watershed Monitoring',
    'USFS Management Indicator Species'
]

spot_parent_projects = ['SWAMP Stream Pollution Trends']
fhab_parent_projects = ['SWAMP Freshwater Harmful Algal Blooms(HAB) Program']

# List of CEDEN fields that should be imported as dates
wq_date_cols = [
    'SampleDate', 
    'CalibrationDate', 
    'PrepPreservationDate', 
    'DigestExtractDate',
    'AnalysisDate'
]

ceden_phab_analytes = [
    'CSCI',
    'IPI'
]

# List of analytes that will be queried from the CEDEN WQ data mart. Add or remove as needed
ceden_wq_analytes = [
    'Alkalinity as CaCO3, Total',
    'Aluminum, Total',
    'Ammonia as N, Total',
    'Arsenic, Total',
    'Barium, Total',
    'Beryllium, Total',
    'Boron, Dissolved',
    'Cadmium, Total',
    'Chromium, Total',
    'Chloride, Dissolved',
    'Chlorophyll a, Particulate', # Bioaccumulation
    'Copper, Total',
    'Dissolved Organic Carbon, Dissolved', # Bioaccumulation
    'E. coli',
    'Fluoride, Dissolved',
    'Hardness as CaCO3, Total',
    'Lead, Total',
    'Manganese, Total',
    'Mercury, Methyl, Total', # Bioaccumulation
    'Mercury, Total', # Bioaccumulation
    'Moisture, Total', # Bioaccumulation
    'Nickel, Total',
    'Nitrogen, Total, Total',
    'Nitrogen, Total Kjeldahl, Total',
    'Oxygen, Dissolved, Total', # Bioaccumulation
    'Oxygen, Saturation, Total', # Bioaccumulation
    'pH',
    'Phosphorus as P, Total',
    'Selenium, Total',
    'Silver, Total',
    'SpecificConductivity, Total',
    'Sulfate, Dissolved', # Bioaccumulation
    'Temperature', # Bioaccumulation
    'Total Dissolved Solids, Total',
    'Total Organic Carbon, Total',
    'Turbidity, Total',
    'Zinc, Total'
]

# Not currently in use, keep here for when we have time to work on this again
data_uses = ['Ambient', 'Health', 'Investigation', 'Regulatory']

# The data mart tables associated with each CEDEN data type
datamart_tables = {
    'habitat': 'HabitatDMart_MV',
    'stations': 'DM_WQX_Stations_MV',
    'tissue': 'TissueDMart_MV',
    'toxicity': 'ToxDMart_MV',
    'water_quality': 'WQDMart_MV'
}

# The data categories that will be included in any analysis/summary (data processing only). The same changes must also be made in the app code.
# Categories excluded: "MetaData", "Reject record"
dq_categories = [
    'Passed', 
    'Some review needed', 
    'Spatial accuracy unknown',
    'Unknown data quality',
    'Extensive review needed',
    'Not assessed'
]

# Date fields in the phab dataset that should be imported as the date data type
phab_date_cols = ['SampleDate']

portal_resource_ids = {
    'habitat': '6d9a828a-d539-457e-922c-3cb54a6d4f9b',
    'stations': 'df69fdd7-1475-4e57-9385-bb1514f0291e',
    'tissue': '6f848c25-c1cf-44d0-80a0-5f63b9939a41',
    'toxicity': 'a6dafb52-3671-46fa-8d42-13ddfa36fd49',
    'water_quality': '2bfd92aa-7256-4fd9-bfe4-a6eff7a8019e'
}

# Relative location of RB boundaries layer used for assigning RB value to stations
rb_boundaries_file = '../../assets/rb_boundaries.geojson'

reference_sites_file = '../../assets/reference_sites_1-27-23.csv'

# Date fields in the tissue dataset that should be imported as the date data type
tissue_date_cols = ['EarliestDateSampled', 'DigestExtractDate', 'AnalysisDate', 'LatestDateSampled', 'SampleDate', 'CompositeSampleDate', 'HomogonizedDate']

# Today's date in string 'YYYY-MM-DD' format
today = str(datetime.today()).split(' ')[0]

# Date fields in the tox dataset that should be imported as the date data type
tox_date_cols = ['SampleDate', 'ToxBatchStartDate']

# Relative paths of data files in the export folder
upload_file_paths = {
    'habitat': '../../export/swamp_habitat_data.csv',
    'stations': '../../export/swamp_stations.csv',
    'toxicity': '../../export/swamp_toxicity_data.csv',
    'tissue': '../../export/swamp_tissue_summary_data.csv',
    'water_quality': '../../export/swamp_water_quality_data.csv'
}
