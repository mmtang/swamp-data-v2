'''
This script gets the current dated SWAMP habitat data file (from the export folder) and uploads it to the open data portal. If there is no directory in the export folder with the current date, then the script will not be able to locate the correct file and the script will not run.

Updated: 03/06/2024 
'''

import os
import re
import sys

sys.path.insert(0, '../utils/') 
import chunked_upload as cu # chunked_upload.py
import p_constants # p_constants.py
import p_utils  # p_utils.py
# import ckanapi


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    print('--- Uploading habitat data file')

    # Get file name
    directory = '../../export/%s' % p_constants.today # Locate folder inside the archive folder with today's date 
    files = os.listdir(directory) # Get list of files inside folder
    substring = 'swamp_habitat_data'
    matched_file = [x for x in files if re.search(substring, x)] # Get the name of the file that matches substring

    # Construct file path
    file_path = directory + '/' + matched_file[0]

    # Upload file
    cu.upload_chunked_data(p_constants.portal_resource_ids['habitat'], file_path, (1024 * 1024 * 64)) # 64MB chunk 

    # 10/9/23 - Chunked upload was not working, so I used the ckanapi code below. Chunked upload is working now, but keep the code below for reference
    #ckan = ckanapi.RemoteCKAN(p_constants.HOST, apikey=p_constants.KEY)
    #resource_info = ckan.action.resource_show(id=p_constants.portal_resource_ids['habitat'])
    #ckan.action.resource_update(id=resource_info['id'], upload=open(file_path, 'rb'), format=resource_info['format'])

    print('%s finished running' % os.path.basename(__file__))