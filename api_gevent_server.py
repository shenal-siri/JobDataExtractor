from api_linkedin_extractor import app
from gevent.pywsgi import WSGIServer

http_server = WSGIServer(('0.0.0.0', 5000), app)
http_server.serve_forever()