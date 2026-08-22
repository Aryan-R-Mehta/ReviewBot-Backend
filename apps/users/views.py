from django.contrib.auth.decorators import login_required
from django.http import JsonResponse


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