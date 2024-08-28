from django.urls import path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from .views import *

multisearch = MultiProjectListDetail.as_view({
    'get':'multisearch'
})
date_modified = MultiProjectListDetail.as_view({
    'get':'multisearch_date'
})

urlpatterns = [
    re_path(r'^$', APIOverview.as_view(), name="api-overview"),
    path('notices/open_to_collaborate/', OpenToCollaborateNotice.as_view(), name="api-open-to-collaborate"),

    path('get-user/', GetUserAPIView.as_view(), name='get-user'),
    path('projects/', ProjectList.as_view(), name="api-projects"),
    path('subscription', SubscriptionAPI.as_view(), name="subscription"),
    path('projects/<uuid:unique_id>/', ProjectDetail.as_view(), name="api-project-detail"),

    path('projects/multi/<unique_id>/', multisearch, name="api-projects-multi"),
    path('projects/date_modified/<unique_id>/', date_modified, name="api-projects-date-modified"),

    path('schema/', SpectacularAPIView.as_view(api_version='v2'), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc')

]