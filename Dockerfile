FROM  python:3.7-slim-buster
LABEL maintainer="Srinivas Reddy Thatiparthy<thatiparthysreenivas@gmail.com>"
# COPY Pipfile   /reef/Pipfile
# COPY Pipfile.lock   /reef/Pipfile.lock
COPY requirements.txt  /reef/requirements.txt
WORKDIR /reef
RUN pip install -r requirements.txt
COPY . /reef
EXPOSE 5000:5000
ENV FLASK_APP  reef/application.py
ENTRYPOINT ["flask"]
CMD ["run"]