from django.urls import path

from .views import current_user, user_repos, repo_pulls

app_name = "users"


urlpatterns = [
    path("me/", current_user, name="current-user"),
    path("repos/", user_repos, name="user-repos"),
    path("repos/<str:owner>/<str:repo>/pulls/", repo_pulls, name="repo-pulls"),
]