from django.urls import path
from . import views

urlpatterns = [
    path('connect-community/', views.connect_community, name="connect-community"),
    path('create-community/', views.create_community, name="create-community"),
    path('confirm-community/<str:community_id>/', views.confirm_community, name="confirm-community"),

    path('community/update/<str:pk>/', views.update_community, name="update-community"),

    path('community/members/<str:pk>/', views.community_members, name="members"),
    path('community/members/remove/<str:pk>/<str:member_id>', views.remove_member, name="remove-member"),
    
    path('community/labels/select/<str:pk>/', views.select_label, name="select-label"),

    path('community/labels/customize/<str:pk>/<str:label_type>', views.customize_label, name="customize-label"),
    path('community/labels/<str:pk>/<str:label_id>/', views.approve_label, name="approve-label"),
    path('community/labels/edit/<str:pk>/<str:label_id>/', views.edit_label, name="edit-label"),

    path('community/labels/apply-labels/<str:pk>/<str:project_uuid>', views.apply_labels, name="apply-labels"),

    path('community/projects/<str:pk>/', views.projects, name="community-projects"),
    path('community/projects/create-project/<str:pk>/', views.create_project, name="create-project"),
    path('community/projects/edit-project/<str:community_id>/<str:project_uuid>', views.edit_project, name="edit-project"),

    path('community/connections/<str:pk>/', views.connections, name="community-connections"),

    path('community/restricted/<str:pk>/', views.restricted_view, name="restricted"),
    
    path('community/labels-pdf/<str:pk>/', views.labels_pdf, name="labels-pdf"),
    path('community/labels-download/<str:pk>/', views.download_labels, name="download-labels"),

]