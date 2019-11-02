FROM  python:3.7-slim-buster
LABEL maintainer="Srinivas Reddy Thatiparthy<thatiparthysreenivas@gmail.com>"
COPY requirements.txt  /reef/requirements.txt
WORKDIR /reef
RUN mkdir /reef/html_reports
RUN pip install -r requirements.txt
COPY . /reef
EXPOSE 5000:5000
ENV FLASK_APP  reef/application.py
CMD ["python3", "-m", "flask", "run", "--host=0.0.0.0"]