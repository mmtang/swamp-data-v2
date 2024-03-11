'''
This script gets the current dated SWAMP tissue data file (from the export folder) and uploads it to the open data portal. If there is no directory with the current date, then the script will not be able to locate the correct file and the script will not run.

Updated: 03/06/2024 
'''

import os
import re
import sys

sys.path.insert(0, '../utils/') # Must include this to import modules from another folder
import chunked_upload as cu # chunked_upload.py
import p_constants # p_constants.py
import p_utils  # p_utils.py
# import ckanapi


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    print('--- Uploading tissue data file')

    # Get the folder name (with today's date) where the file is saved. This will not work if there is no export folder with today's date
    directory = '../../export/%s' % p_constants.today 
    files = os.listdir(directory) # Get list of files inside the folder
    substring = 'swamp_tissue_summary_data'
    matched_file = [x for x in files if re.search(substring, x)] # Get the name of the file that matches substring

    # Construct file path
    file_path = directory + '/' + matched_file[0]

    # Upload file
    cu.upload_chunked_data(p_constants.portal_resource_ids['tissue'], file_path, (1024 * 1024 * 64)) # 64MB chunk 

    # Old upload code using the ckanapi, keep for reference
    #ckan = ckanapi.RemoteCKAN(p_constants.HOST, apikey=p_constants.KEY)
    #resource_info = ckan.action.resource_show(id=p_constants.portal_resource_ids['habitat'])
    #ckan.action.resource_update(id=resource_info['id'], upload=open(file_path, 'rb'), format=resource_info['format'])

    print('%s finished running' % os.path.basename(__file__))