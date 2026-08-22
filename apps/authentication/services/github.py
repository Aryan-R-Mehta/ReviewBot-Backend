import requests

from django.conf import settings


GITHUB_AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
GITHUB_ACCESS_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_API_URL = "https://api.github.com"


class GitHubOAuthService:

    @staticmethod
    def get_authorization_url(state):
        params = {
            "client_id": settings.GITHUB_CLIENT_ID,
            "redirect_uri": settings.GITHUB_CALLBACK_URL,
            "state": state,
            "allow_signup": "true",
        }

        response = requests.Request(
            "GET",
            GITHUB_AUTHORIZE_URL,
            params=params,
        ).prepare()

        return response.url

    @staticmethod
    def exchange_code(code):
        response = requests.post(
            GITHUB_ACCESS_TOKEN_URL,
            data={
                "client_id": settings.GITHUB_CLIENT_ID,
                "client_secret": settings.GITHUB_CLIENT_SECRET,
                "code": code,
                "redirect_uri": settings.GITHUB_CALLBACK_URL,
            },
            headers={
                "Accept": "application/json",
            },
            timeout=10,
        )

        response.raise_for_status()

        data = response.json()

        if "error" in data:
            raise ValueError(data.get("error_description", "GitHub OAuth failed"))

        return data

    @staticmethod
    def get_user(access_token):
        response = requests.get(
            f"{GITHUB_API_URL}/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_emails(access_token):
        response = requests.get(
            f"{GITHUB_API_URL}/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github+json",
            },
            timeout=10,
        )

        response.raise_for_status()

        return response.json()

    @staticmethod
    def get_primary_email(emails):
        for email in emails:
            if email.get("primary") and email.get("verified"):
                return email["email"]

        return ""
