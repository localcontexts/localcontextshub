from django.urls import path
from . import views

urlpatterns = [
    path('download/open-to-collaborate-notice/researcher/<int:perm>/<int:researcher_id>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice-researcher"),
    path('download/open-to-collaborate-notice/institution/<int:perm>/<int:institution_id>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice-institution"),
    path('download/open-to-collaborate-notice/service-provider/<int:perm>/<int:service_provider_id>/', views.download_open_collaborate_notice, name="download-open-to-collaborate-notice-service-provider"),
    path('download/collections-care-notices/<str:institution_id>/<int:perm>/', views.download_collections_care_notices, name="download-collections-care-notices"),
    path('invite/delete/<str:pk>/', views.delete_member_invite, name="delete-member-invite"),
    path('download/community/support-letter/', views.download_community_support_letter, name="download-community-support-letter"),
    path('community-boundary-view/<int:community_id>', views.community_boundary_view, name="community-boundary-view"),
    path('project-boundary-view/<int:project_id>', views.project_boundary_view, name="project-boundary-view"),
    path('boundary-preview/', views.boundary_preview, name="boundary-preview"),
    path('nld-data/', views.native_land_data, name="nld-data"),
]
