from django.urls import path
from . import views

urlpatterns = [
    # Creating/Joining Accounts and adding Boundaries
    path('preparation-step/', views.preparation_step, name="prep-community"),
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('community-boundary/', views.community_boundary, name="community-boundary"),
    path('add-community-boundary/', views.add_community_boundary, name="add-community-boundary"),
    path('upload-boundary-file/', views.upload_boundary_file, name="upload-boundary-file"),
    path('registration-boundary', views.registration_boundary, name="registration-boundary"),

    # Public view
    path('view/<str:pk>/', views.public_community_view, name="public-community"),

    # Settings
    path('update/<str:pk>/', views.update_community, name="update-community"),
    path('preferences/<str:pk>/', views.account_preferences, name="preferences-community"),
    path('reset-community-boundary/<str:pk>/', views.reset_community_boundary, name="reset-community-boundary"),
    path('update-community-boundary/<str:pk>/', views.update_community_boundary, name="update-community-boundary"),
    path('update-community-boundary-data/<str:pk>/',
         views.update_community_boundary_data,
         name="update-community-boundary-data"
         ),
    path('api-key/<str:pk>/', views.api_keys, name="community-api-key"),
    path('connect-service-provider/<str:pk>/', views.connect_service_provider, name="community-connect-service-provider"),

    # Labels: View
    path('labels/select/<str:pk>/', views.select_label, name="select-label"),
    path('labels/view/<str:pk>/<uuid:label_uuid>/', views.view_label, name="view-label"),

    # Labels: Customize
    path('labels/customize/<str:pk>/<str:label_code>/', views.customize_label, name="customize-label"),
    path('labels/<str:pk>/<str:label_id>/', views.approve_label, name="approve-label"),
    path('labels/edit/<str:pk>/<str:label_id>/', views.edit_label, name="edit-label"),

    # Labels: Apply
    path('labels/apply-labels/<str:pk>/<uuid:project_uuid>/', views.apply_labels, name="apply-labels"),

    #Labels: Export
    path('labels-pdf/<str:pk>/', views.labels_pdf, name="labels-pdf"),
    path('labels-download/<str:pk>/', views.download_labels, name="download-labels"),

    # Members
    path('members/<str:pk>/', views.community_members, name="members"),
    path('members/requests/<str:pk>/', views.member_requests, name="member-requests"),
    path('members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-member"),
    path('members/join-request/delete/<str:pk>/<str:join_id>/', views.delete_join_request, name="delete-join-request"),

    # Projects: View
    path('projects/<str:pk>/', views.projects, name="community-projects"),

    # Projects: Create
    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/<str:related>', views.create_project, name="community-create-project"),
    path('projects/create-project/<str:pk>/<uuid:source_proj_uuid>/', views.create_project, name="community-create-project"),
    path('projects/create-project/<str:pk>/', views.create_project, name="community-create-project"),

    # Projects: Edit
    path('projects/edit-project/<str:pk>/<uuid:project_uuid>/', views.edit_project, name="edit-project"),
    path('projects/actions/<str:pk>/<uuid:project_uuid>/', views.project_actions, name="community-project-actions"),
    path('projects/delete-project/<str:pk>/<uuid:project_uuid>', views.delete_project, name="community-delete-project"),
    path('projects/archive-project/<str:pk>/<uuid:project_uuid>', views.archive_project, name="community-archive-project"),
    path('projects/unlink/<str:pk>/<uuid:target_proj_uuid>/<uuid:proj_to_remove_uuid>', views.unlink_project, name="community-unlink-project"),

    # Connections
    path('connections/<str:pk>/', views.connections, name="community-connections"),
]