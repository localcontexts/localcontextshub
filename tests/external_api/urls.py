from localcontexts.urls import urlpatterns
from django.urls import path

from . views import placeholder_view


class UrlsWithMockedExternalApi:
    urlpatterns = urlpatterns + [
        path('placeholder-url/', placeholder_view)
    ]
