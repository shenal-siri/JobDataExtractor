FROM python:3.8-slim-buster
WORKDIR /app
COPY requirements.txt .
# RUN apt-get update && \ 
# apt-get install -y libpq-dev gcc && \
RUN pip install --no-cache-dir -r requirements.txt 
COPY . .
EXPOSE 5000
#RUN chmod +x docker-wait-for-pg.sh
RUN chmod +x wait-for-it.sh
#ENTRYPOINT ["python3", "api_gevent_server.py"]