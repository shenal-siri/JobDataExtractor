# Utility 
import os
import shutil
import sys
from collections import defaultdict
# Custom modules
from html_processor import JobData
from postgres_handler import PGHandler

##### USER MUST SET THESE PARAMS BEFORE RUNNING SCRIPT #####

# Location where HTML files + resources are stored:
HTML_DIR = 'html_files'
#HTML_DIR = os.path.join('html_files', '_test') # For test / debug
# Do you want these files to be deleted by the script after successful extraction to database?
DELETE_HTML_FILES = False

############################################################


# Initialize connection to Postgres database
# NOTE: Connection parameters must be specified in the 'database.ini' file
PGHandler.init_connection()

# Initialize dicts to store successful / unsuccessful commits to database 
commit_success = {}
commit_fail = {}

# Get list of LinkedIn job postings (excluding subfolders) from the directory they have been downloaded to
#HTML_DIR = os.path.join('html_files', '_test')
if not os.path.exists(HTML_DIR):
    print("'{}' directory does not exist. Please create directory and try again.".format(HTML_DIR))
    sys.exit(1)
html_files = [f for f in os.listdir(HTML_DIR) if os.path.isfile(os.path.join(HTML_DIR, f))]

# Create JobData object to parse / extract data from LinkedIn job posting
current_job = JobData()

# Main loop for parsing, extraction, commit and deletion of downloaded job postings
for current_file in html_files:
    
    # Set filepath and extract data into JobData object
    current_job.filepath = os.path.join(HTML_DIR, current_file)
    current_job.extract_job_data(current_file, HTML_DIR)
    
    # Commit extracted data to the Postgres database and store to appropriate dict based on status
    if PGHandler.insert_job(current_job.data):
        commit_success[current_job.data['id']] = [current_job.data['title'], current_job.data['company']]
    else:
        commit_fail[current_job.data['id']] = [current_job.data['title'], current_job.data['company']]
    
    # Delete html file and its corresponding resources folder  
    if DELETE_HTML_FILES:
        current_folder_path = os.path.join(HTML_DIR, current_file[:-5] + '_files')
        shutil.rmtree(current_folder_path)
        os.remove(current_job.filepath)
    
    # Reset the current_job.data dict for reuse
    current_job.reset_job_data()


# Show summary of successful / failed commits
num_success = len(commit_success)
num_fail = len(commit_fail)
if num_success > 0:
    print("\n{} Jobs successfully added to database:".format(num_success))
    for job_id, job_info in commit_success.items():
        print("{} --> {}  :  {}".format(job_id, job_info[0], job_info[1]))

if num_fail > 0:
    print("\n{} Jobs unable to be added to database:".format(num_fail))
    for job_id, job_info in commit_fail.items():
        print("{} --> {}  :  {}".format(job_id, job_info[0], job_info[1]))


# # Test - update status of a job
# status = PGHandler.update_rejected('Software Engineer - Order Generation', 'Wealthsimple')
# print(status)


# Close connection to database
PGHandler.connection.close()
