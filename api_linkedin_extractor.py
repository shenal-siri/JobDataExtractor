# Flask
from flask import Flask, request, abort, make_response, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal
# Utility 
import os
import shutil
import sys
from collections import defaultdict
# Custom modules
from html_processor import JobData
from postgres_handler import PGHandler


app = Flask(__name__)
api = Api(app)

# Define the fields to be yielded during GET requests
job_fields = {
    'id': fields.Integer,
    'url': fields.String,
    'title': fields.String,
    'company': fields.String,
    'location': fields.String,
    'seniority': fields.String,
    'employment_type': fields.String,
    'industries': fields.List(fields.String),
    'functions': fields.List(fields.String),
    'posting_text': fields.String,
    'uri': fields.Url('job')
}


class JobListAPI(Resource):
    
    # Validation arguments for '/jobs' endpoint
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No job id provided',
                                   location='json')
        self.reqparse.add_argument('HTML', type=str, required=True,
                                   help='No HTML provided',
                                   location='json')
        super(JobListAPI, self).__init__()
        
        
    def get(self):
        # Initialize connection to Postgres database
        # NOTE: Connection parameters must be specified in the 'database.ini' file
        PGHandler.init_connection()
        
        # Select data for all jobs (no id passed) from the Postgres database and store to appropriate dict
        job_list = PGHandler.select_job()
        
        if job_list == "Connection Failed":
            abort(504)
        elif job_list is None:
            abort(404)
        else:
            return {'job_list': [marshal(job, job_fields) for job in job_list]}, 200
        
        
        # Close connection to database
        PGHandler.connection.close()
    

    def post(self):
        # Assign the id and HTML received from the Chrome Extension into a JobData object
        args = self.reqparse.parse_args()
        job_args = {
            'id': args['id'],
            'html': args['HTML']
        }
        current_job = JobData(job_input_data=job_args)
        
        # Have the JobData object extract the relevant data fields from the raw HTML
        current_job.extract_job_data()
        
        # Initialize connection to Postgres database
        # NOTE: Connection parameters must be specified in the 'database.ini' file
        PGHandler.init_connection()
        
        # Commit extracted data to the Postgres database and return HTML code
        if PGHandler.insert_job(current_job.data):
            return {'job': marshal(current_job.data, job_fields)}, 201
        else:
            abort(409)
        
        
        # Close connection to database
        PGHandler.connection.close()


class JobAPI(Resource):
    
    # Validation arguments for '/jobs/<id>' endpoint
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No job id provided',
                                   location='json')
        #self.reqparse.add_argument('HTML', type=str, location='json')
        super(JobAPI, self).__init__()    
        
        
    def get(self, id):
        # Initialize connection to Postgres database
        # NOTE: Connection parameters must be specified in the 'database.ini' file
        PGHandler.init_connection()
        
        # Select data for the specific job id from the Postgres database and store to appropriate dict
        selected_job = PGHandler.select_job(id)
        
        if selected_job == "Connection Failed":
            abort(504)
        elif selected_job is None:
            abort(404)
        else:
            return {'job': marshal(selected_job, job_fields)}, 200
        
        
        # Close connection to database
        PGHandler.connection.close()
        

api.add_resource(JobListAPI, '/jobdataextractor/api/v1.0/jobs/', endpoint = 'jobs')
api.add_resource(JobAPI, '/jobdataextractor/api/v1.0/jobs/<int:id>', endpoint = 'job')


if __name__ == '__main__':
    app.run(debug=True)

# TODO:
# Implement connection pooling
# Implement GET functionality for all jobs (downloadable csv?)
# Figure out how to package app using docker
# Update documentation and release