from flask import Flask, escape, request
import requests
from datetime import datetime, timedelta

app = Flask(__name__)
from .config import *


class HttpStatusException(Exception):
    def __init__(self, url, status_code, reason, *args, **kwargs):
        self.url = url
        self.status_code = status_code
        self.reason = reason
        super().__init__(*args, **kwargs)

    def __str__(self):
        return "{}({}, {}, {})".format(
            self.__class__.__name__, self.url, self.status_code, self.reason
        )


class User:
    def __init__(self, email=EMAIL, password=PASSWORD, app_token=APP_TOKEN):
        self.email = email
        self.password = password
        self.app_token = app_token
        # self.org_ids = self.organization_ids()

    @property
    def auth_token(self):
        params = {"email": self.email, "password": self.password}
        response = requests.post(
            AUTH_ENDPOINT, params=params, headers={"App-Token": self.app_token}
        )
        # TODO: Error handling
        return response.json()["user"]["auth_token"]()

    def organization_ids(self):
        """
        Retrieves organization ids for the authenticated user.
        :param auth_token:
        :return: List of organization ids.
        """
        response = requests.get(
            ORGS_ENDPOINT,
            headers={"App-Token": APP_TOKEN, "Auth-Token": self.auth_token},
        )
        return [org["id"] for org in response.json().get("organizations")]

    def project_ids(self):
        org_id = self.organization_ids()[0]
        return retrieve_user_project_ids(self.auth_token, org_id)

    def organization_user_ids(self):
        org_id = self.organization_ids()[0]
        return retrieve_organization_members(self.auth_token, org_id)

    def reports(self, date=None):
        date = date or (datetime.now() + timedelta(days=-1)).strftime("%Y-%m-%d")
        csv = lambda x: ",".join(map(str, list(x)))
        return custom_by_member_report(
            self.auth_token,
            csv(self.organization_user_ids()),
            csv(self.organization_ids()),
            csv(self.project_ids()),
            date,
        )


"""
[{'id': 720879, 'name': 'Srinivas Reddy Thatiparthy', 'duration': 16626, 'dates': [{'date': '2019-10-28', 'duration': 3600, 'projects': [{'id': 811570, 'name': 'ProjectB', 'duration': 3600}]}, {'date': '2019-10-29', 'duration': 7200, 'projects': [{'id': 811568, 'name': 'hubstaff bot50', 'duration': 3600}, {'id': 811569, 'name': 'ProjectA', 'duration': 3600}]}, {'date': '2019-10-30', 'duration': 5826, 'projects': [{'id': 811568, 'name': 'hubstaff bot50', 'duration': 4811}, {'id': 811569, 'name': 'ProjectA', 'duration': 946}, {'id': 811570, 'name': 'ProjectB', 'duration': 69}]}]}]
"""


def retrieve_auth_token():
    params = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(
        AUTH_ENDPOINT, params=params, headers={"App-Token": APP_TOKEN}
    )
    if response.status_code == 401:
        raise HttpStatusException(AUTH_ENDPOINT, 401, "Invalid email and/or password")
    elif response.status_code == 403:
        raise HttpStatusException(
            AUTH_ENDPOINT, 403, "API access is only for organizations on an active plan"
        )
    elif response.status_code == 404:
        raise HttpStatusException(AUTH_ENDPOINT, 404, "Could not find record")
    elif response.status_code == 429:
        raise HttpStatusException(
            AUTH_ENDPOINT,
            429,
            "Rate limit has been reached. Please wait before making your next request.",
        )
    return response.json()["user"]["auth_token"]


def retrieve_org_ids(auth_token):
    """
    Retrieves organization ids for the authenticated user.
    :param auth_token:
    :return: List of organization ids.
    """
    response = requests.get(
        ORGS_ENDPOINT, headers={"App-Token": APP_TOKEN, "Auth-Token": auth_token}
    )
    return [org["id"] for org in response.json().get("organizations")]


def retrieve_user_project_ids(auth_token, id):
    """
    Retrieves the project ids for the authenticated user.
    :param auth_token: Authentication token
    :return: List of project ids
    """
    response = requests.get(
        PROJECTS_ENDPOINT.format(id=id),
        headers={"App-Token": APP_TOKEN, "Auth-Token": auth_token},
    )
    print(response.json())
    return [org["id"] for org in response.json().get("projects")]


def retrieve_organization_members(auth_token, org_id):
    """
    Retrieves the members/employees of an organization.
    :param auth_token: Authentication token
    :param org_id: organization id
    :return: List of employees
    """
    response = requests.get(
        ORG_MEMBERS_ENDPOINT.format(id=org_id),
        params={"include_removed": False},
        headers={"App-Token": APP_TOKEN, "Auth-Token": auth_token},
    )
    print(response.json())
    return [org["id"] for org in response.json().get("users")]


def custom_by_member_report(
    auth_token,
    users,
    organizations,
    project_ids,
    date=(datetime.now() + timedelta(days=-4)).strftime("%Y-%m-%d"),
):
    response = requests.get(
        CUSTOM_BY_MEMBER_TEAM_ENDPOINT,
        params={
            "start_date": date,
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "organizations": organizations,
            "projects": project_ids,
            "users": users,
        },
        headers={"App-Token": APP_TOKEN, "Auth-Token": auth_token},
    )
    return response.json()


@app.route("/reports", methods=["GET"])
def reports():
    user = User()
    auth_token = user.auth_token
    org_ids = retrieve_org_ids(auth_token)
    users = set()
    for org_id in org_ids:
        users.update(set(retrieve_organization_members(auth_token, org_id)))
    project_ids = set()
    for user in users:
        project_ids.update(set(retrieve_user_project_ids(auth_token, user)))
    cs_project_ids = ",".join(map(str, list(project_ids)))
    cs_org_ids = ",".join(map(str, list(org_ids)))
    cs_users = ",".join(map(str, list(users)))
    report = custom_by_member_report(auth_token, cs_users, cs_org_ids, cs_project_ids)
    pt_raw_data = []
    for org in report.get("organizations"):
        if org["id"] in org_ids:
            pt_raw_data = org["users"]
    import pdb

    pdb.set_trace()


if __name__ == "__main__":
    app.run(debug=True)
