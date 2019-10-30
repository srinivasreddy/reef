from flask import Flask, escape, request
import requests
import pytz
import functools

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
        return"{}({}, {}, {})".format(self.__class__.__name__, self.url, self.status_code, self.reason)

def retrieve_auth_token():
    params = {"email": EMAIL, "password": PASSWORD}
    response = requests.post(
        AUTH_ENDPOINT, params=params, headers={"App-Token": APP_TOKEN}
    )
    if response.status_code == 401:
        raise HttpStatusException(AUTH_ENDPOINT, 401, "Invalid email and/or password")
    elif response.status_code == 403:
        raise HttpStatusException(AUTH_ENDPOINT, 403, "API access is only for organizations on an active plan")
    elif response.status_code == 404:
        raise HttpStatusException(AUTH_ENDPOINT, 404, "Could not find record")
    elif response.status_code == 429:
        raise HttpStatusException(AUTH_ENDPOINT, 429, "Rate limit has been reached. Please wait before making your next request.")
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
    print(response.json())
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


def custom_by_member_date_report(
    auth_token, start_date, end_date, organizations, users, project_ids
):
    response = requests.get(
        CUSTOM_BY_MEMBER_ENDPOINT,
        params={
            "start_date": start_date,
            "end_date": end_date,
            "organizations": organizations,
            "projects": project_ids,
            "users": users,
        },
        headers={"App-Token": APP_TOKEN, "Auth-Token": auth_token},
    )
    print(response.json())
    return [org["id"] for org in response.json().get("organizations")]


@app.route("/reports", methods=["GET"])
def reports():
    auth_token = retrieve_auth_token()
    org_ids = retrieve_org_ids(auth_token)
    users = set()
    for org_id in org_ids:
        users.update(set(retrieve_organization_members(auth_token, org_id)))
    users = list(users)
    project_ids = set()
    for user in users:
        project_ids.update(set(retrieve_user_project_ids(auth_token, user)))
    project_ids = list(project_ids)
    start_date = (datetime.now() + timedelta(days=-200)).strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=-10)).strftime("%Y-%m-%d")
    result = custom_by_member_date_report(auth_token, start_date, end_date, org_ids, users, project_ids)
    import pdb; pdb.set_trace()


if __name__ == "__main__":
    app.run()
