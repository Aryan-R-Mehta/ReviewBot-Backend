from django.conf import settings
from django.contrib.auth import get_user_model, login
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import redirect
from django.views import View

from .models import GitHubAccount
from .services.github import GitHubOAuthService

User = get_user_model()


class GitHubLoginView(View):

    def get(self, request):
        import secrets

        state = secrets.token_urlsafe(32)
        request.session["github_oauth_state"] = state

        authorization_url = GitHubOAuthService.get_authorization_url(state)

        return redirect(authorization_url)


class GitHubCallbackView(View):

    @transaction.atomic
    def get(self, request):
        code = request.GET.get("code")
        state = request.GET.get("state")

        if not code:
            return HttpResponseBadRequest(
                "GitHub authorization code is missing."
            )

        stored_state = request.session.pop(
            "github_oauth_state",
            None,
        )

        if not stored_state or state != stored_state:
            return HttpResponseBadRequest(
                "Invalid OAuth state."
            )

        # Exchange GitHub code for access token.
        token_data = GitHubOAuthService.exchange_code(code)

        access_token = token_data["access_token"]

        # Get GitHub profile.
        github_user = GitHubOAuthService.get_user(
            access_token
        )

        # Get verified email.
        github_emails = GitHubOAuthService.get_emails(
            access_token
        )

        email = GitHubOAuthService.get_primary_email(
            github_emails
        )

        github_id = github_user["id"]

        # ---------------------------------------------------------
        # 1. Check whether this GitHub account already exists.
        # ---------------------------------------------------------

        github_account = (
            GitHubAccount.objects
            .select_related("user")
            .filter(github_id=github_id)
            .first()
        )

        if github_account:
            user = github_account.user

        else:
            # -----------------------------------------------------
            # 2. Try to connect GitHub to an existing user by email.
            # -----------------------------------------------------

            user = None

            if email:
                user = (
                    User.objects
                    .filter(email__iexact=email)
                    .first()
                )

            # -----------------------------------------------------
            # 3. If no existing user, create one.
            # -----------------------------------------------------

            if user is None:
                username = self.get_unique_username(
                    github_user["login"]
                )

                user = User.objects.create_user(
                    username=username,
                    email=email,
                    first_name=github_user.get("name") or "",
                )

            # -----------------------------------------------------
            # 4. Create GitHub account connection.
            # -----------------------------------------------------

            github_account = GitHubAccount(
                user=user,
                github_id=github_id,
            )

        # ---------------------------------------------------------
        # 5. Update GitHub account information.
        # ---------------------------------------------------------

        github_account.username = github_user["login"]
        github_account.name = github_user.get("name") or ""
        github_account.email = email
        github_account.profile_url = github_user["html_url"]
        github_account.avatar_url = github_user.get("avatar_url") or ""
        github_account.access_token = access_token
        github_account.is_active = True

        github_account.save()

        # ---------------------------------------------------------
        # 6. Create Django session.
        # ---------------------------------------------------------

        login(request, user)

        return redirect(
            f"{settings.FRONTEND_URL}/dashboard"
        )

    @staticmethod
    def get_unique_username(github_username):
        username = github_username

        if not User.objects.filter(username=username).exists():
            return username

        counter = 1

        while User.objects.filter(
            username=f"{username}_{counter}"
        ).exists():
            counter += 1

        return f"{username}_{counter}"