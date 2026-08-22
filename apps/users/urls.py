from django.urls import path

from .views import current_user

app_name = "users"


urlpatterns = [
    path(
        "me/",
        current_user,
        name="current-user",
    ),
]