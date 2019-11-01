# This is a settings file

import os


API_ENDPOINT = "https://api.hubstaff.com/v1"
AUTH_ENDPOINT = API_ENDPOINT + "/auth"
ORGS_ENDPOINT = API_ENDPOINT + "/organizations"
USERS_ENDPOINT = API_ENDPOINT + "/users"
PROJECTS_ENDPOINT = API_ENDPOINT + "/users/{id}/projects"
ORG_MEMBERS_ENDPOINT = API_ENDPOINT + "/organizations/{id}/members"
CUSTOM_BY_MEMBER_TEAM_ENDPOINT = API_ENDPOINT + "/custom/by_member/team"


TIMEZONE = "Europe/Warsaw"
APP_TOKEN = os.environ.get(
    "HS_APP_TOKEN", "TAgq83AeDd6PKGu9hoB86JhTkaAkLqU3_tabEQmi3ws"
)
EMAIL = os.environ.get("HS_EMAIL", "thatiparthysreenivas@gmail.com")
PASSWORD = os.environ.get("HS_PASSWORD", "qqHubstaff@1434")
