from django.urls import path, re_path
from drf_spectacular.views import (
    SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
)
from .views import *

multisearch = MultiProjectListDetail.as_view({
    'get':'multisearch'
})
date_modified = MultiProjectListDetail.as_view({
    'get':'multisearch_date'
})


urlpatterns = [
    re_path(r'^$', APIOverview.as_view(), name="api-overview"),
    path(
        'notices/open_to_collaborate/', OpenToCollaborateNotice.as_view(),
        name="api-open-to-collaborate"
    ),

    path('get-user/', GetUserAPIView.as_view(), name='get-user'),
    path('projects/', ProjectList.as_view(), name="api-projects"),
    path('subscription', SubscriptionAPI.as_view(), name="subscription"),
    path('projects/<uuid:unique_id>/', ProjectDetail.as_view(), name="api-project-detail"),

    path('projects/multi/<unique_id>/', multisearch, name="api-projects-multi"),
    path(
        'projects/multi/date_modified/<unique_id>/', date_modified,
        name="api-projects-date-modified"
    ),

    # For Developers: Reminder to add the local server to the servers list below for testing.
    path('schema/', SpectacularAPIView.as_view(
            api_version='v2',
            custom_settings= {
                'VERSION': '2.0.0',
                'SERVERS': [
                    {
                        'url': 'https://localcontextshub.org/api/v2/',
                        'description': 'Live instance of the Local Contexts Hub.'
                    },
                    {
                        'url': 'https://sandbox.localcontextshub.org/api/v2/',
                        'description': 'Sandbox/Testing site for the Local Contexts Hub API.'
                    }
                ],
            }
        ), name='schema'
    ),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')

]