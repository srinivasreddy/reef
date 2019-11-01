FROM  python:3.7-slim-buster
LABEL maintainer="Srinivas Reddy Thatiparthy<thatiparthysreenivas@gmail.com>"
WORKDIR  /reef
COPY Pipfile.lock   /reef/Pipfile.lock
COPY . .
EXPOSE 5000:5000
ENV FLASK_APP  reef/application.py
RUN pip install pipenv virtualenv
RUN virtualenv -p python3 flask && pipenv sync
ENV PATH=/root/.virtualenvs/bin:$PATH
ENTRYPOINT ["python"]
CMD ["reef/application.py"]
