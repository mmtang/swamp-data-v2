'''
This script gets the current dated SWAMP toxicity data file (from the archive folder) and uploads it to the open data portal
'''

import os
import re
import sys

sys.path.insert(0, '../utils/') # Must include this line to import modules from another folder
import chunked_upload as cu # chunked_upload.py
import p_constants # p_constants.py
import p_utils  # p_utils.py


if __name__ == '__main__':
    p_utils.print_spacer()
    print('Running %s' % os.path.basename(__file__))
    print('--- Uploading toxicity data file')

    # Get file name
    directory = '../../export/%s' % p_constants.today # Locate folder inside the archive folder with today's date 
    files = os.listdir(directory) # Get list of files inside folder
    substring = 'swamp_toxicity_data'
    matched_file = [x for x in files if re.search(substring, x)] # Get the name of the file that matches substring

    # Construct file path
    file_path = directory + '/' + matched_file[0]

    # Upload file
    # Need to test this line again
    cu.upload_chunked_data(p_constants.portal_resource_ids['toxicity'], file_path, (1024 * 1024 * 64)) # 64MB chunk 

    print('%s finished running' % os.path.basename(__file__))