from localcontexts.urls import urlpatterns
from django.urls import path

from . views import native_land_map_list


class UrlsWithMockedExternalApi:
    urlpatterns = urlpatterns + [
        path('wp-json/nativeland/v1/map-list/', native_land_map_list)
    ]
