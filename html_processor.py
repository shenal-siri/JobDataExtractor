import os
# BeautifulSoup
from bs4 import BeautifulSoup
from bs4 import Comment


class JobData:
    """
    JobData objects handle the extraction and storage of relevant job data from the LinkedIn HTML file
    currently being parsed.
    Builds on top of BeautifulSoup objects and methods.
    """
    # Initialize dict for storing extracted data from each job posting
    # NOTE: 'rejected' boolean field is not extracted and defaults to 'false' when committing
    # a job to the db (see DDL_job_data.sql)
    DATA_FIELDS = ['id', 'url', 'title', 'company', 'location', 'seniority', 
                       'industries', 'employment_type', 'functions', 'posting_text']
    
    def __init__(self, fields=DATA_FIELDS):
        self.data = dict.fromkeys(fields)
        self.filepath = None
    
    
    def process_text(self, text, ignore_first=False, return_as_string=False):
        """ Utility function used in extract_job_data()
        Input:  Raw text extracted from a BS4 tag object (i.e: tag.text)
        Output: Either:
                - (Default) A list of strings, itemized by newlines
                - A single string of text, concatenated with ". "
        """
        text_list = [x.strip() for x in text.splitlines()]
        text_list = list(filter(bool, text_list))
        
        if ignore_first:
            text_list = text_list[1:]
        
        if return_as_string:
            return ". ".join(text_list)
        else:
            return text_list
    
    
    def extract_job_data(self, filename, foldername):
        """
        Input:  Filepath to a LinkedIn HTML job posting
        Output: self.data dict populated with relevant job data
        """
        # Read in the target HTML file
        with open(self.filepath, 'r', encoding='utf-8') as rf:
            html_corpus = rf.read()

        # Create BS4 soup object    
        soup = BeautifulSoup(html_corpus, 'html.parser')

        # Extract all comment tags from the main soup object
        comments = soup.find_all(string=lambda text: isinstance(text, Comment))

        # Get the first comment and extract the url and 10-digit id information from it
        self.data['url'] = comments[0][22:].strip()
        self.data['id'] = comments[0][-12:-2].strip()

        # Find the div tag inside the main article tag which contatins the job posting text
        posting_text_tag = soup.find('article').find_all('div', {'id': 'job-details'})
        
        # Extract job posting text from the tag
        self.data['posting_text']  = self.process_text(posting_text_tag[0].get_text(separator=' '), 
                                                       return_as_string=True)
        
        
        # Find the div tags inside the main article tag which contatins additional job details
        detail_tags = soup.find('article').find_all("div", {"class": "jobs-box__group"})
        
        # Parse through each tag and store data in an auxiliary dict
        detail_dict = dict.fromkeys(['Seniority Level', 'Industry', 'Employment Type', 'Job Functions'])
        
        for tag in detail_tags:
            detail_list = self.process_text(tag.get_text(separator=' '), return_as_string=False)
            # Determine if extracted header corresponds to one of the detail categories we care about
            if detail_list[0] in detail_dict.keys():
                detail_dict[detail_list[0]] = detail_list[1:]

        # Preprocess and extract relevant data from their respective tags
        self.data['industries'] = detail_dict['Industry']
        self.data['functions'] = detail_dict['Job Functions']
        
        # Try/Except block needed to handle None if no Seniority or Employment Type in job description
        try:
            self.data['seniority'] = detail_dict['Seniority Level'][0]        # pylint: disable=unsubscriptable-object
        except TypeError:
            self.data['seniority'] = None
        
        try:
            self.data['employment_type'] = detail_dict['Employment Type'][0]  # pylint: disable=unsubscriptable-object
        except TypeError:
            self.data['employment_type'] = None
        
        
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
        self.data['title'] = self.process_text(tag_target.find('h1').text, return_as_string=True)

        # Tag locations for other items are not consistent - so we have to parse and process the raw text directly
        company_location_list = self.process_text(tag_target.find('h3').text)
        self.data['company'] = company_location_list[1]
        self.data['location'] = company_location_list[3]
        
        
    def reset_job_data(self, fields=DATA_FIELDS):
        """
        Resets all values in self.data back to default (None)
        """
        self.data = dict.fromkeys(fields)
    
        
### TODO

