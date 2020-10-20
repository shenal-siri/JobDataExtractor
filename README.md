# JobDataExtractor

## What is this?
This is a custom Chrome extension I wrote which can extract, store, and retrieve data from LinkedIn job postings. This data is stored in a local Postgres database, which can then be queried / analyzed / visualized as the user desires. The app has also been Dockerized - so you can use it with minimal set up!

## What was your motivation?
- When tracking my job applications, I was manually storing a url to each job posting I applied to in an Excel sheet. Automating this seemed like a natural next step, which then snowballed into this app.

- I wanted to apply the PostgreSQL techniques I had learnt to a practical, useful project. 

- Every data science enthusiast has to have at least *one* web-scraping project!


## What does the stack for this app look like?

- Backend: Python (Flask) API, served using Gevent.

- Database: PostgreSQL, accessed using Psycopg2. I opted out of using an ORM (e.g. SQLAlchemy) to gain a better under-the-hood understanding of querying / interacting with the database (would have saved me a lot of time, in hindsight...)

- Frontend: Chrome extension written in barebones Javascript.

As mentioned, the app is Dockerized for compatibility, with separate containers for the Flask API and Postgres db respectively.

The database itself is stored as a volume on the local machine, so the db persists even if the containers are restarted / removed (the volume is mounted via the 'data_postgres' folder created in your local repo after running `docker-compose` for the first time).

![Dockerized App Schema](/resources/Docker_Architecture.png "Dockerized App Schema")

The database schema / ERD is summarized below:

![Database ERD](/resources/ERD_job_data.png "Database ERD")

## Why not just crawl job postings automatically?
In short, I didn't want to run afoul of the [LinkedIn ToS](https://www.linkedin.com/legal/user-agreement#dos). Exploring an automation tool like Selenium would have been fun, but ultimately I chose not to run the risk of having my LinkedIn account banned. LinkedIn's free API is too restrictive for scraping job data, and LinkedIn has a track record of cracking down on web scrapers.

This implementation is a satisfactory step-up for me from storing urls on an Excel sheet.

## How do I set this up?
All you need is [Google Chrome](https://www.google.com/intl/en_us/chrome/) and [Docker](https://www.docker.com/get-started) installed on your machine. Specifically: 
1) Clone / Download this repo.
2) Install the Chrome Extension.
3) Build and run the containers using `docker-compose.yml`.

#### 1. Clone / Download this Repo
Pretty self-explanatory, see the image below.

![GitHub - Clone / Download Repo](/resources/git_clone.PNG "GitHub - Clone / Download Repo")


#### 2. Install the Chrome Extension
- On a Chrome tab, navigate to *chrome://extensions/*

![Chrome - Extensions Page](/resources/readme_setup_2_01.PNG "Chrome - Extensions Page")

- Enable 'Developer mode'.

![Chrome - Developer Mode](/resources/readme_setup_2_02.PNG "Chrome - Developer Mode")

- Select 'Load unpacked' and select the 'chrome_extension' folder from your local repo.

![Chrome - Load Unpacked](/resources/readme_setup_2_03.PNG "Chrome - Load Unpacked")

![Chrome - Select Folder](/resources/readme_setup_2_04.PNG "Chrome - Select Folder")

- The extension should now be installed and ready to use. You can pin it to your extensions toolbar for ease of use.

![Chrome - Installed Extension](/resources/readme_setup_2_05.PNG "Chrome - Installed Extension")

#### 3. Build and Run the Docker Containers

- Open up the terminal of your choice and navigate to the repo's top-level directory. 
- Run the following command (or any variant)
`docker-compose up --build --force-recreate -d`
- Wait for the containers to spin up completely. If this is the first time running, Docker will have to build the app image from the ground-up, so expect this to take some time.
    - Docker Desktop has a dashboard which allows you to view logs and container status.
    - You can also use the `/checkconnection` and `/tryconnection` API endpoints to determine connection status (see [API Reference](#api-reference) below).

## Done! Now how do I use this tool?

1. Navigate to any LinkedIn job posting page (i.e. url begins with `https://www.linkedin.com/jobs/view/`)

2. Click the pinned extension and select 'Extract Job Posting'

![Extension - Extract Posting](/resources/readme_usage_2_01.PNG "Extension - Extract Posting")

3. You should receive a Chrome alert if your job posting was successfuly extracted and stored in the database.

![Extension - Success Alert](/resources/readme_usage_3_01.PNG "Extension - Success Alert")

4. You can retrieve a job posting by its id ('Retrieve Job Posting') or download a JSON file of all the job posting data currently in the database ('Download ALL Job Postings').

![Extension - Success Alert](/resources/readme_usage_4_01.PNG "Extension - Success Alert")


5. Feel free to stop / remove the containers when not using the app. Simply restart them using a `docker-compose up` command and you should be good to go. 

## Caveats

- *This tool isn't meant to be a bulk job posting scraper*. The idea was to create a rudimentary pipeline to store data on jobs I would be manually applying to anyways.

- *This tool is a work-in-progress*. As such, it might not be properly refactored or fully bug-tested, but I will try to keep the `master` branch as clean as possible.



## Potential / Future Work

- [x] Wrapping this up into a rudimentary web app (or even custom Chrome Extension) would be an interesting foray into basic web development tools and technologies **- Implemented**

- [ ] Scraping data's no fun unless you use it! We can load our data into a `pandas` dataframe and go to town with some EDA to extract insights (For example: Which skills are most commonly requested in job postings?) **- Priority: High - In Progress**

- [ ] Adding additional usability features for querying / modifying job postings in the database (flagging jobs as 'rejected', querying using fields other than through job id, etc.) **- Priority: High**

- [ ] Explore the creation of an interactive dashboard à la Tableau or Power BI (Plotly Dash might be promising, if it can connect to a database for live visualizations) **- Priority: Medium**.


- [ ] LinkedIn is just one of many job posting aggregators, how about other common options (Indeed, Glassdoor, Monster etc)? **- Priority: Low**

- [ ] This tool only stores data on jobs I apply to. Can this be expanded to a suite of different tools which make the overall job application process easier? (Eg: Auto-filling applications on company web portals? Setting up notifications for companies I actively wish to apply to?) **- Priority: Low**


## File Index

| Filename / Directory | Description |
| -------- | ----------- |
| `/chrome_extension` | Contains the requisite files for the Job Data Extractor Chrome Extension. |
| `/data_postgres` | (Local-only) Directory created on the local machine which stores the database volume. |
| `/resources` | Contains misc resources for documentation. |
| `.env` | Contains pre-defined environment variables for initializing the Postgres database. |
| `api_gevent_server.py` | Python script which serves the Flask API via a Gevent server. Is run by the app container after `wait-for-it.sh` executes. |
| `api_linkedin_extractor.py` | Flask API for the app. Contains endpoints, methods and objects (see API documentation below). |
| `DDL_job_data.sql` | Defines the tables and functions required for the `job_data` Postgres database. Is run once by the database container on `docker-compose up`, if no existing docker volume is found. |
| `docker-compose.yml` | Docker Compose file containing instructions for spinning up the `app` and `db` containers, `data_postgres` volume and the default network between them. Used during `docker-compose up` command. |
| `Dockerfile` | Dockerfile containing the instructions needed to build the app image. Used during `docker build` command. |
| `html_processor.py` | Custom module for processing text data from a LinkedIn job posting's HTML. Leverages the [Beautifulsoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) library.
| `postgres_handler.py` | Defines the custom PGHandler class - used by the API to manage extracted job data and execute queries on the Postgres database. |
| `requirements.txt` | Lists all required packages. Used during `docker build` command. |
| `wait-for-it.sh` | Bash script run during `docker-compose up` to ensure app container waits for database container's ports are opened befre starting. Documentation found [here](https://github.com/vishnubob/wait-for-it) |
| `linkedin_extractor.py` | Deprecated |
| `postgres_config.py` | Deprecated |

<br>

## API Reference

| HTTP Method | URI | Action | Status |
| :---------: | :-: | :----: | :----: |
| POST   | http://http://localhost:5000/jobdataextractor/api/v1.0/jobs/ | Add a new job posting to the database. | Implemented |
| PUT    | http://localhost:5000/jobdataextractor/api/v1.0/jobs/[job_id] | Update a job's status to 'rejected'. | Not Implemented |
| DELETE | http://localhost:5000/jobdataextractor/api/v1.0/jobs/[job_id] | Delete a job from the database. | Not Implemented |
| GET    | http://localhost:5000/jobdataextractor/api/v1.0/jobs/[job_id] | Get the details of a specific job | Implemented |
| GET    | http://localhost:5000/jobdataextractor/api/v1.0/jobs/ | Get the details of all jobs in the database | Implemented |
| GET    | http://localhost:5000/jobdataextractor/api/v1.0/checkconnection/ | For debugging. Returns current connection status to Postgres database.  | Implemented |
| GET    | http://localhost:5000/jobdataextractor/api/v1.0/tryconnection/ | For debugging. Attempts connection to Postgres database and returns current connection status. | Implemented |

