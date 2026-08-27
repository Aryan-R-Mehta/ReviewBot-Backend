from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from requests.exceptions import HTTPError, RequestException

from apps.authentication.services.github import GitHubOAuthService


@login_required
def current_user(request):
    user = request.user
    github_account = user.github_account

    return JsonResponse({
        "id": user.id,
        "email": user.email,
        "name": github_account.name,
        "github": {
            "id": github_account.github_id,
            "username": github_account.username,
            "avatar_url": github_account.avatar_url,
            "profile_url": github_account.profile_url,
        },
    })

@login_required
def user_repos(request):
    github_account = request.user.github_account

    try:
        repos = GitHubOAuthService.get_repos(github_account.access_token)
    except HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        return JsonResponse(
            {"error": "Failed to fetch GitHub repositories."},
            status=status if status < 500 else 502,
        )
    except RequestException:
        return JsonResponse(
            {"error": "Failed to reach GitHub."},
            status=502,
        )

    return JsonResponse({
        "repos": [
            {
                "id": repo["id"],
                "name": repo["name"],
                "full_name": repo["full_name"],
                "html_url": repo["html_url"],
                "private": repo["private"],
                "description": repo.get("description") or "",
            }
            for repo in repos
        ],
        "has_more": len(repos) == 10,
    })

@login_required
def repo_pulls(request, owner, repo):
    github_account = request.user.github_account
    try:
        pulls = GitHubOAuthService.get_pulls(
            github_account.access_token,
            owner,
            repo,
        )
    except HTTPError as exc:
        status = exc.response.status_code if exc.response is not None else 502
        return JsonResponse(
            {"error": "Failed to fetch pull requests."},
            status=status if status < 500 else 502,
        )
    except RequestException:
        return JsonResponse(
            {"error": "Failed to reach GitHub."},
            status=502,
        )
    return JsonResponse({
        "pull_requests": [
            {
                "id": pull["id"],
                "number": pull["number"],
                "title": pull["title"],
                "state": pull["state"],
                "draft": pull.get("draft") or False,
                "html_url": pull["html_url"],
                "created_at": pull["created_at"],
                "updated_at": pull["updated_at"],
                "user": {
                    "login": pull["user"]["login"],
                    "avatar_url": pull["user"]["avatar_url"],
                },
            }
            for pull in pulls
        ],
    })
