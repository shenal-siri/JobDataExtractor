from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse, fields, marshal

app = Flask(__name__)
api = Api(app)

# Define the fields to be yielded during GET requests
job_fields = {
    'id': fields.Integer,
    'HTML': fields.String,
    'uri': fields.Url('job')
}

# Stand-in list of 'job' objects to test API (pending database implementation)
jobs = [
    {
        'id': 1,
        'HTML': 'THIS IS THE HTML FOR JOB WITH ID 1'
    },
    {
        'id': 2,
        'HTML': 'JOB #2 IS REALLY COOL, APPLY NOW!!!'
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
        # Assign the id and HTML received from the Chrome Extension into a bundled 'current_job'
        args = self.reqparse.parse_args()
        current_job = {
            'id': args['id'],
            'HTML': args['HTML']
        }
        jobs.append(current_job)
        return {'job': marshal(current_job, job_fields)}, 201


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
    