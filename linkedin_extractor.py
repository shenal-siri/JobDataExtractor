# Utility 
import os
import shutil
import sys
from collections import defaultdict
# BeautifulSoup
from bs4 import BeautifulSoup
from bs4 import Comment
# Psycopg2
import psycopg2
from psycopg2 import Error
from psycopg2 import sql
# Custom modules
from text_preprocessor import process_text
from postgres_handler import PGHandler

##### USER MUST SET THESE PARAMS BEFORE RUNNING SCRIPT #####

# Location where HTML files + resources are stored:
HTML_DIR = 'html_files'
# Do you want these files to be deleted by the script after successful extraction to database?
DELETE_HTML_FILES = False

############################################################


# Initialize connection to Postgres database
# NOTE: Connection parameters must be specified in the 'database.ini' file
PGHandler.init_connection()

# Initialize dict for storing extracted data from each job posting
# NOTE: 'rejected' boolean field is not extracted and defaults to 'false' when committing
# a job to the db (see DDL_job_data.sql)
DATA_FIELDS = ['id', 'url', 'title', 'company', 'location', 'seniority', 
               'industries', 'employment_type', 'functions', 'posting_text']
data_extracted = dict.fromkeys(DATA_FIELDS)

# Initialize dicts to store successful / unsuccessful job db commits 
commit_success = {}
commit_fail = {}

# Get list of Linkedin job postings (excluding subfolders) from the directory they have been downloaded to
HTML_DIR = 'html_files'
if not os.path.exists(HTML_DIR):
    print("'{}' directory does not exist. Please create directory and try again.".format(HTML_DIR))
    sys.exit(1)
html_files = [f for f in os.listdir(HTML_DIR) if os.path.isfile(os.path.join(HTML_DIR, f))]


# Main loop for parsing, extraction, commit and deletion of downloaded job postings
for current_file in html_files:
    
    # Open and process html using BS4
    current_file_path = os.path.join(HTML_DIR, current_file)
    with open(current_file_path, 'r') as rf:
        txt = rf.read()

    # Create BS4 object    
    soup = BeautifulSoup(txt, 'html.parser')

    # Extract all comment tags from the main soup object
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))

    # Get the first comment and extract the url and 10-digit id information from it
    data_extracted['url'] = comments[0][22:].strip()
    data_extracted['id'] = comments[0][-12:-2].strip()

    # Extract all tags inside the main article tag
    article_tags = soup.find('article').find_all('div')

    """Reference for data extracted from div tags inside article tag:
    div tag  1: Main article text
    div tag -4: "Seniority Level"
    div tag -3: "Industries"
    div tag -2: "Employment Type"
    div tag -1: "Job Functions"
    """
    # Preprocess and extract relevant data from the respective tags
    data_extracted['posting_text'] = process_text(article_tags[1].get_text(separator=' '), 
                                                    return_as_string=True)
    data_extracted['seniority'] = process_text(article_tags[-4].get_text(separator=' '), 
                                                    ignore_first=True, return_as_string=True)
    data_extracted['industries'] = process_text(article_tags[-3].get_text(separator=' '), 
                                            ignore_first=True)
    data_extracted['employment_type'] = process_text(article_tags[-2].get_text(separator=' '), 
                                                    ignore_first=True, return_as_string=True)
    data_extracted['functions'] = process_text(article_tags[-1].get_text(separator=' '), 
                                                ignore_first=True)

    # Extract all div tags from the main soup object
    tags_all = soup.find_all('div')

    # Search for the tag which contains the job name, company name, and job location text
    # Tag attributes are {'class': ['mt6', 'ml5', 'flex-grow-1']}
    for t in tags_all:
        if 'class' in t.attrs:
            if all(x in ['mt6', 'ml5', 'flex-grow-1'] for x in t.attrs['class']):
                tag_target = t
                break

    # Extract the relevant information from the found tag            
    data_extracted['title'] = process_text(tag_target.find('h1').text, return_as_string=True)

    # Tag locations for other items are not consisten - so we have to parse and process the raw text directly
    company_location_list = process_text(tag_target.find('h3').text)
    data_extracted['company'] = company_location_list[1]
    data_extracted['location'] = company_location_list[3]

    # # Print data
    # print("\n'Extracted job details:'") 
    # print(data_extracted)
    
    
    # Commit extracted data to the Postgres database and store to appropriate dict based on status
    if PGHandler.insert_job(data_extracted):
        commit_success[data_extracted['id']] = [data_extracted['title'], data_extracted['company']]
    else:
        commit_fail[data_extracted['id']] = [data_extracted['title'], data_extracted['company']]
    
    # Delete html file and its corresponding resources folder  
    if DELETE_HTML_FILES:
        current_folder_path = os.path.join(HTML_DIR, current_file[:-5] + '_files')
        shutil.rmtree(current_folder_path)
        os.remove(current_file_path)


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



# Test - update status of a job
status = PGHandler.update_rejected('Software Engineer - Order Generation', 'Wealthsimple')
print(status)


# Close connection to database
PGHandler.connection.close()
