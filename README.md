# JobDataExtractor

## What is this?
This is a simple Python tool I wrote which parses, extracts, and stores data from LinkedIn job postings (from locally downloaded HTML files). This database can then be queried / analyzed as desired.

## What was your motivation?
- I was manually storing a url to each job posting I applied to in  an Excel sheet, as a means of tracking my job applications. Automating this seemed like a natural next step.

- I wanted to apply the PostgreSQL techniques I had learnt to a practical, useful project. 

- Every data science enthusiast has to have at least *one* web-scraping project!

## Downloading HTML files still seems like a pretty manual process to me...
I agree, it unfortunately is. I didn't want to automate the entire web scraping process (using something like Selenium) and run the risk of having my LinkedIn account banned. LinkedIn's free API is too restrictive for job scraping, and LinkedIn has a track record of cracking down on web scrapers (see [LinkedIn ToS 8.2.b.](https://www.linkedin.com/legal/user-agreement#dos)).

This implementation is a satisfactory step-up for me from storing urls on an Excel sheet.

## How do I set this up?
Since `linkedin_extractor.py` stores data in a PostgreSQL database, the initial setup steps involved include:
1) Cloning / Downloading this repo.
2) Creating a PostgreSQL database and setting up its schema.
3) Setting database connection parameters.

#### 1. Cloning / Downloading this Repo
Self-explanatory, just click here:

![GitHub - Clone / Download Repo](/resources/git_clone.PNG "GitHub - Clone / Download Repo")

Don't forget to set up your Python env using `requirements.txt`!

#### 2. Creating a PostgreSQL database and setting up its schema
I recommend [pgAdmin 4](https://www.pgadmin.org/download/) for hassle-free, GUI-based Postgres database creation and management. Once you've created a database for the tool, you can use pgAdmin's 'Query Tool' to open and run `DDL_job_data.sql`, which will create the requisite tables / relationships / functions.

![pgAdmin 4 - Query Tool](/resources/pgAdmin_1.PNG "pgAdmin 4 - Query Tool")

![pgAdmin 4 - Loading DDL file](/resources/pgAdmin_2.PNG "pgAdmin 4 - Loading DDL file")

![pgAdmin 4 - Building Schema](/resources/pgAdmin_3.PNG "pgAdmin 4 - Building Schema")

The database schema / ERD is summarized below:

![Database ERD](/resources/ERD_job_data.png "Database ERD")

#### 3. Setting database connection parameters.
Copy the `database.ini` file found in the `resources` folder to the top level directory. Edit the `password` and `database` fields to those of the database you have created.

## Done! Now how do I use this tool?

#### 1. Manually download HTML for LinkedIn job postings you wish to store.
Create a folder in the top level directory (default name is `html_files`). 

When you find a LinkedIn job posting you wish to parse, right-click anywhere on the webpage and click "Save as.."

![Saving a LinkedIn job posting](/resources/LinkedIn_save_1.PNG "Saving a LinkedIn job posting")

Save the HTML to the `html_files` directory. Be sure to select "Webpage, Complete".

![Saving a LinkedIn job posting](/resources/LinkedIn_save_2.PNG "Saving a LinkedIn job posting")

#### 2. Run `linkedin_extractor.py`

This will extract the job posting data from all HTML files currently in the `html_files` directory, and commit it to the PostgreSQL database (if it is not already in the database). The script can also be configured to delete the local files after parsing.

## Caveats
- *This tool isn't meant to be a bulk job posting scraper*. The idea was to create a rudimentary pipeline to store data on jobs I would be manually applying to anyways.

- *This tool is a work-in-progress*. As such, it might not be properly refactored or fully bug-tested, but I will try to keep the `main` branch as clean as possible.



## Future Work
- Scraping data's no fun unless you use it! We can load our data into a `pandas` dataframe and go to town on extracting some valuable insights (For example: Which skills are most commonly requested in job postings?) **- Priority: High**

- Some sort of rudimentary GUI to handle running the tool / marking jobs as 'rejected' / deleting jobs would be nice. **- Priority: Medium**

- This just stores data on jobs I apply to. Can this be expanded to a suite of different tools which make the overall job application process easier? (Eg: Auto-filling applications on company web portals? Setting up notifications for companies I actively wish to apply to?) **- Priority: Medium**

- LinkedIn is just one of many job posting aggregators, how about other common options (Indeed, Glassdoor, Monster etc)? **- Priority: Low**

