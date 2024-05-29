from django.urls import path, re_path
from .views import *

projects_by_user = ProjectsByIdViewSet.as_view({
    'get':'projects_by_user'
})
projects_by_institution = ProjectsByIdViewSet.as_view({
    'get':'projects_by_institution'
})
projects_by_researcher = ProjectsByIdViewSet.as_view({
    'get':'projects_by_researcher'
})
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

    path('projects/users/<str:pk>/', projects_by_user, name="api-projects-user"),
    path('projects/institutions/<str:institution_id>/', projects_by_institution, name="api-projects-institution"),
    path('projects/institutions/<str:institution_id>/<str:providers_id>', projects_by_institution, name="api-projects-institution"),
    path('projects/researchers/<str:researcher_id>/', projects_by_researcher, name="api-projects-researcher"),

    path('projects/multi/<unique_id>/', multisearch, name="api-projects-multi"),
    path('projects/date_modified/<unique_id>/', date_modified, name="api-projects-date-modified")
]