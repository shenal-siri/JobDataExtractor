from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse, fields, marshal
from html_processor import JobData

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

# Stand-in data store of 'job' objects to test API (pending database implementation)
jobs = [
    {
        'id': 1,
        'url': "test url",
        'title': "test title",
        'company': "test company",
        'location': "test location",
        'seniority': "test seniority",
        'employment_type': "test employment type",
        'industries': ["test industry 1", "test industry 2"],
        'functions': ["test function 1", "test function 2", "test function 3"],
        'posting_text': "test job posting text, description and information"
    }
]


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

    def post(self):
        # Assign the id and HTML received from the Chrome Extension into a ata object
        args = self.reqparse.parse_args()
        job_args = {
            'id': args['id'],
            'html': args['HTML']
        }
        current_job = JobData(job_posting_data=job_args)
        
        # Have the JobData object extract the relevant data fields from the raw HTML
        current_job.extract_job_data()
        
        # Add the JobData object data to our temporary data store
        jobs.append(current_job.data)
        return {'job': marshal(current_job.data, job_fields)}, 201


class JobAPI(Resource):
    
    # Validation arguments for '/jobs/<id>' endpoint
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('id', type=int, required=True,
                                   help='No job id provided',
                                   location='json')
        self.reqparse.add_argument('HTML', type=str, location='json')
        super(JobAPI, self).__init__()    
        
    def get(self, id):
        job = [job for job in jobs if job['id'] == id]
        if len(job) == 0:
            abort(404)
        return {'job': marshal(job[0], job_fields)}
    

api.add_resource(JobListAPI, '/jobdataextractor/api/v1.0/jobs/', endpoint = 'jobs')
api.add_resource(JobAPI, '/jobdataextractor/api/v1.0/jobs/<int:id>', endpoint = 'job')


if __name__ == '__main__':
    app.run(debug=True)
    