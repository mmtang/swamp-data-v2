'''
This script uses the SWAMP stations dataset and adds a new field: 'Region'. The values in this new field are numeric (1-9) and they refer to the Regional Water Quality Control Board that the station is located in. Geopandas GIS functions are used to find where the point is located relative to the RB boundaries.

Updated: 03/06/2024 
'''

import geopandas as gpd
import os
import pandas as pd
import sys

sys.path.insert(0, '..\\utils\\') 
import p_constants # p_constants.py
import p_utils  # p_utils.py

# Function used for finding the nearest RB polygon to a site. Used for those sites that do not fall directly within a RB polygon
def get_nearest_region(point):
    # Calculate the point's distance to all of the regions. Sort ascending by distance, and then pick the first object in the array (the nearest feature)
    polygon_index = rb_gdf.distance(point).sort_values().index[0]
    nearest = rb_gdf.loc[polygon_index]
    return nearest['rb'] # Return the 'rb' attribute of the feature


# Change anaconda environment to geo_env before running
if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    

    #####  Import data  #####
    print('--- Importing data')
    # Import data from the previous script
    stations_df = p_utils.import_csv('../../support_files/swamp_stations_without_region.csv') 

    # Convert station coordinates to gdf. Use standard WGS 84 for importing the data, will convert to a projected system later (https://spatialreference.org/ref/epsg/4326/)
    stations_gdf = gpd.GeoDataFrame(stations_df, geometry=gpd.points_from_xy(stations_df.TargetLongitude, stations_df.TargetLatitude), crs='EPSG:4326')

    # Define coordinate system of the gdf and convert to projected
    # CRS 3310: NAD 83 CA Teale Albers (https://spatialreference.org/ref/epsg/3310/)
    # 10/16/23 - For some reason, trying to convert this dataframe to a projected system (3310 or 4269) results in "inf" values in the geometry column. Not sure why.
    # 03/06/24 - Seems to be working now
    stations_gdf = stations_gdf.to_crs('EPSG:3310')
    
    # Load geojson of regional board boundaries (comes in as EPSG: 4326) and convert to same projection
    rb_gdf = gpd.read_file(p_constants.rb_boundaries_file)
    rb_gdf.crs = "EPSG:4326"

    # 10/16/23 - Cannot convert the station layer to EPSG 3310 or 4269. Not sure why. So keep the region layer in WGS 84. Will have to perform the spatial join and nearest region function on non-projected geometries (not ideal), but this is the only option until I find out what's wrong. The results seem to be ok at least.
    # 03/06/24 - Seems to be working now
    rb_gdf = rb_gdf.to_crs('EPSG:3310')


    #####  Process data  
    # Overlay points on rb boundaries and do a left spatial join
    stations_with_rb = gpd.sjoin(stations_gdf, rb_gdf, how='left', predicate='within')

    # After the join, a subset of points will not have a joined rb number due to these points being located slightly outside the border of the rb. Select these points
    missing_rb = stations_with_rb[stations_with_rb['rb'].isna()].copy()

    # Apply the get_nearest_region function to all points with missing RB values
    missing_rb['rb'] = missing_rb.apply(lambda x: get_nearest_region(x.geometry), axis=1)

    # Join these missing rb values back to the df from the spatial join
    # Chose to iterate rather than do an actual merge/join because I didn't want the join to append new columns to the df. It can be done either way
    for i, row in missing_rb.iterrows():
        stations_with_rb.loc[stations_with_rb['StationCode'] == row['StationCode'], 'rb'] = row['rb']

    # Join back to original stations df (before spatial join)
    stations_with_rb = stations_with_rb[['StationCode', 'rb']] # select the two fields we want/need
    stations_df = pd.merge(stations_df, stations_with_rb, how='left', on='StationCode') # left join on StationCode
    
    # Rename "rb" field to "Region"
    stations_df.rename(columns={'rb': 'Region'}, inplace=True)

    # Convert Region column to int (to remove decimal point) and then to string
    stations_df['Region'] = stations_df['Region'].astype(int)
    stations_df['Region'] = stations_df['Region'].astype(str)

    # Manually change the values for some stations, either because geopandas did not get the correct value or there is a special case
    # Place this after the .astype lines
    stations_df.loc[stations_df['StationCode'] == '633RLS01', 'Region'] = 6 # Geopandas puts this site in R5
    stations_df.loc[stations_df['StationCode'] == '526T00016', 'Region'] = 5 # Geopandas puts this site in R6
    stations_df.loc[stations_df['StationCode'] == '902MPLTN1', 'Region'] = 9 # Geopandas puts this site in R8
    stations_df.loc[stations_df['StationCode'] == '540PKC272', 'Region'] = 5 # Geopandas puts this site in R6
    stations_df.loc[stations_df['StationCode'] == '633RLS01', 'Region'] = 5 # Geopandas puts this site in R5

    # Add Reference Site column
    ref_sites_df = p_utils.import_csv(p_constants.reference_sites_file)
    ref_cols = ref_sites_df[['cedenid', 'StationCategory']] # Get a subset of the columns needed for join
    stations_df = pd.merge(stations_df, ref_cols, how='left', left_on=stations_df['StationCode'].str.lower(), right_on=ref_cols['cedenid'].str.lower())
    stations_df = stations_df.drop(['key_0', 'cedenid'], axis=1)


    #####  Write file
    file_name = 'swamp_stations'
    print('--- Writing %s.csv' % file_name)

    # Write file in support files folder
    p_utils.write_csv(stations_df, file_name, '../../support_files')

    # Write file in a dated folder, inside the export folder
    p_utils.write_csv(stations_df, file_name + '_' + p_constants.today, '../../export/' + p_constants.today)

    print('%s finished running' % os.path.basename(__file__))