# This is a settings file

import os

API_ENDPOINT = "https://api.hubstaff.com/v1"
AUTH_ENDPOINT = API_ENDPOINT + "/auth"
ORGS_ENDPOINT = API_ENDPOINT + "/organizations"
USERS_ENDPOINT = API_ENDPOINT + "/users"
PROJECTS_ENDPOINT = API_ENDPOINT + "/users/{id}/projects"
ORG_MEMBERS_ENDPOINT = API_ENDPOINT + "/organizations/{id}/members"
CUSTOM_BY_MEMBER_ENDPOINT = API_ENDPOINT + "/weekly/team"
TIMEZONE = "Europe/Warsaw"
APP_TOKEN = os.environ.get("APP_TOKEN", "TAgq83AeDd6PKGu9hoB86JhTkaAkLqU3_tabEQmi3ws")
FLASK_APP = os.environ.get("FLASK_APP", "application.py")
EMAIL = os.environ.get("EMAIL", "thatiparthysreenivas@gmail.com")
PASSWORD = os.environ.get("PASSWORD", "Hubstaff@1434")
