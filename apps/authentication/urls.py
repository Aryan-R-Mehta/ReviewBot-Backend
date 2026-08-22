from django.urls import path

from .views import GitHubCallbackView, GitHubLoginView

app_name = "authentication"


urlpatterns = [
    path(
        "github/",
        GitHubLoginView.as_view(),
        name="github-login",
    ),
    path(
        "github/callback/",
        GitHubCallbackView.as_view(),
        name="github-callback",
    ),
]