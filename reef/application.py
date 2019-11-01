from collections import defaultdict
from datetime import datetime, timedelta

import pandas as pd
import requests
from flask import Flask, abort, render_template, render_template_string

from . import settings


app = Flask(__name__)


class User:
    def __init__(
        self,
        email=settings.EMAIL,
        password=settings.PASSWORD,
        app_token=settings.APP_TOKEN,
    ):
        self.email = email
        self.password = password
        self.app_token = app_token
        self.auth_token = self.authentication_token()

    def authentication_token(self):
        """
        Returns the authentication token for a user given email, password, and app token.
        Raises an exception if the auth token process fails.
        :return: Authentication Token
        """
        params = {"email": self.email, "password": self.password}
        response = requests.post(
            settings.AUTH_ENDPOINT, params=params, headers={"App-Token": self.app_token}
        )
        if response.status_code in (401, 403, 404, 429):
            abort(response.status_code)
        return response.json()["user"]["auth_token"]

    def organization_ids(self):
        """
        Retrieves organization ids for the authenticated user.

        Caveat: Though the user can belong to multiple organizations,
        we assume in this task that logged in user has only one organization.
        :return: List of organization ids.
        """
        response = requests.get(
            settings.ORGS_ENDPOINT,
            headers={"App-Token": settings.APP_TOKEN, "Auth-Token": self.auth_token},
        )
        return [org["id"] for org in response.json().get("organizations")]

    def project_ids(self, user_id):
        """
        Retrieves the project ids for the user id.
        :return: List of project ids
        """
        response = requests.get(
            settings.PROJECTS_ENDPOINT.format(id=user_id),
            headers={"App-Token": settings.APP_TOKEN, "Auth-Token": self.auth_token},
        )
        return [org["id"] for org in response.json().get("projects")]

    def organization_user_ids(self):
        """
        Retrieves the member/employee ids of an organization.
        :param auth_token: Authentication token
        :param org_id: organization id
        :return: List of employee ids
        """
        org_id = self.organization_ids()[0]
        response = requests.get(
            settings.ORG_MEMBERS_ENDPOINT.format(id=org_id),
            params={"include_removed": False},
            headers={"App-Token": settings.APP_TOKEN, "Auth-Token": self.auth_token},
        )
        return [org["id"] for org in response.json().get("users", [])]

    def member_team_reports(self, date=None):
        date = date or (datetime.now() + timedelta(days=-4))
        start_date = date.strftime("%Y-%m-%d")
        end_date = (date + timedelta(days=2)).strftime("%Y-%m-%d")
        _csv = lambda x: ",".join(map(str, x))
        user_ids = self.organization_user_ids()
        cs_user_ids = _csv(user_ids)
        org_ids = self.organization_ids()
        cs_org_ids = _csv(org_ids)
        proj_ids = []
        for user_id in user_ids:
            import pdb

            pdb.set_trace()
            pids = self.project_ids(user_id)
            proj_ids.extend(pids)
        cs_proj_ids = _csv(set(proj_ids))
        response = requests.get(
            settings.CUSTOM_BY_MEMBER_TEAM_ENDPOINT,
            params={
                "start_date": start_date,
                "end_date": end_date,
                "organizations": cs_org_ids,
                "projects": cs_proj_ids,
                "users": cs_user_ids,
            },
            headers={"App-Token": settings.APP_TOKEN, "Auth-Token": self.auth_token},
        )
        print("the member team reports status code: {}".format(response.status_code))
        return response.json()


@app.route("/reports", methods=["GET"])
def reports():
    user = User()
    report = user.member_team_reports()
    pivot_dict = defaultdict(dict)
    for users in report.get("organizations", {}).get("users", []):
        for user in users:
            for project in user.get("dates")[0].get("projects"):
                pivot_dict[user["name"]][project["name"]] = project["duration"]
    print(pivot_dict)
    # pivot_dict = {"Srini" : {"A":12, "B": 32}, "reddy": {"D":12, "A": 34}}
    data_frame = pd.DataFrame(pivot_dict)
    return render_template_string(data_frame.fillna("").to_html())


@app.errorhandler(401)
def invalid_email_password(e):
    return render_template("401.html"), 401


@app.errorhandler(403)
def api_access_only_for_active_org(e):
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return render_template("429.html"), 429


if __name__ == "__main__":
    app.run(debug=True)
