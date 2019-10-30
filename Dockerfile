FROM  python:3.7-slim-buster
WORKDIR  /reef
COPY .  .
EXPOSE 5000:5000
ENV APP_TOKEN TAgq83AeDd6PKGu9hoB86JhTkaAkLqU3_tabEQmi3ws
ENV FLASK_APP  reef/application.py
ENV EMAIL  "thatiparthysreenivas@gmail.com",
ENV PASSWORD  "Hubstaff@1434"
ENTRYPOINT ["/reef"]
RUN pip install -r requirements.txt
CMD ["flask run"]
