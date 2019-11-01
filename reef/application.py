from collections import defaultdict
from datetime import datetime, timedelta
import os
import pandas as pd
import requests
from flask import Flask, abort, render_template, render_template_string, request
from werkzeug.exceptions import BadRequest
from . import settings


app = Flask(__name__)


class InvalidEmailPassword(BadRequest):
    pass


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
        if response.status_code == 401:
            raise InvalidEmailPassword()
        elif response.status_code in (403, 404, 429):
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
        if response.status_code in (401, 403, 404, 429):
            abort(response.status_code)
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
        if response.status_code in (401, 403, 404, 429):
            abort(response.status_code)
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
        if response.status_code in (401, 403, 404, 429):
            abort(response.status_code)
        return [org["id"] for org in response.json().get("users", [])]

    def member_team_reports(self, date):
        start_date = date.strftime("%Y-%m-%d")
        _csv = lambda x: ",".join(map(str, x))
        user_ids = self.organization_user_ids()
        cs_user_ids = _csv(user_ids)
        org_ids = self.organization_ids()
        cs_org_ids = _csv(org_ids)
        proj_ids = []
        for user_id in user_ids:
            pids = self.project_ids(user_id)
            proj_ids.extend(pids)
        cs_proj_ids = _csv(set(proj_ids))
        response = requests.get(
            settings.CUSTOM_BY_MEMBER_TEAM_ENDPOINT,
            params={
                "start_date": start_date,
                "end_date": start_date,
                "organizations": cs_org_ids,
                "projects": cs_proj_ids,
                "users": cs_user_ids,
            },
            headers={"App-Token": settings.APP_TOKEN, "Auth-Token": self.auth_token},
        )
        if response.status_code in (401, 403, 404, 429):
            abort(response.status_code)
        return response.json()


def pivot_table(report):
    pivot_dict = defaultdict(dict)
    for organization in report.get("organizations"):
        for user in organization.get("users"):
            for date in user.get("dates"):
                for project in date.get("projects"):
                    pivot_dict[user["name"]][project["name"]] = (
                        pivot_dict[user["name"]].get(project["name"], 0)
                        + project["duration"]
                    )
    return pivot_dict


@app.route("/reports", methods=["GET"])
def reports():
    user = User()
    date = request.args.get("date", datetime.now() + timedelta(days=-1))
    if isinstance(date, str):
        try:
            date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError as e:
            raise ValueError(
                "<h3>date querystring value is invalid. Please enter a valid parsable querystring in the format: yyyy-mm-dd.</h3>"
            )
    report = user.member_team_reports(date)
    pivot_dict = pivot_table(report)
    data_frame = pd.DataFrame(pivot_dict)
    file_name = datetime.now().strftime("%Y-%m-%d|%H::%M::%S")
    html_data = data_frame.fillna("").to_html()
    path = os.path.join(".", settings.FOLDER_NAME, file_name)
    with open(path, "w") as fd:
        fd.write(html_data)
    return render_template_string(html_data)


@app.errorhandler(401)
def invalid_request(e):
    return e.message, 401


@app.errorhandler(ValueError)
def generic_error(e):
    return e.message, 400


@app.errorhandler(InvalidEmailPassword)
def invalid_email_password(e):
    return "<h3> Invalid email and/or password.</h3>", 401


@app.errorhandler(403)
def api_access_only_for_active_org(e):
    return "<h3>API access is only for organizations on an active plan.</h3>", 403


@app.errorhandler(404)
def page_not_found(e):
    return "<h3>Could not find record you are looking for.</h3>", 404


@app.errorhandler(429)
def rate_limit_exceeded(e):
    return (
        "<h3>Rate limit has been reached. Please wait before making your next request.</h3>",
        429,
    )


if __name__ == "__main__":
    app.run(debug=True)
