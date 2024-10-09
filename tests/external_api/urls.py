from localcontexts.urls import urlpatterns
from django.urls import path

from . views import (
    native_land_map_list,
    native_land_boundary_response
)


class UrlsWithMockedExternalApi:
    urlpatterns = urlpatterns + [
        path('biocodellc/localcontexts_json/main/data/nativeland_slug_name_list.json', native_land_map_list),
        path('wp-json/nativeland/v1/api/index.php', native_land_boundary_response)
    ]
