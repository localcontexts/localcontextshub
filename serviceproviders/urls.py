from django.urls import path
from . import views

urlpatterns = [
    # Account Creation
    path('preparation-step/', views.preparation_step, name="prep-service-provider"),
    path('create-service-provider/', views.create_service_provider, name="create-service-provider"),
    path('confirm-subscription-service-provider/<str:service_provider_id>/', views.confirm_subscription_service_provider, name="confirm-subscription-service-provider"),

    # Public view
    path('view/<str:pk>/', views.public_service_provider_view, name="public-service-provider"),

    # OTC Notice
    path('notices/<str:pk>/', views.service_provider_notices, name="service-provider-notices"),
    path('notices/otc/delete/<str:pk>/<str:notice_id>/', views.delete_otc_notice, name="service-provider-delete-otc"),
    # path('embed/<str:pk>/', views.embed_otc_notice, name="embed-notice-service-provider"),
    
    # Connections
    path('connections/<str:pk>/', views.connections, name="service-provider-connections"),

    # Members
    path('members/<str:pk>/', views.service_provider_members, name="service-provider-members"),
    path('members/invites/<str:pk>/', views.service_provider_member_invites, name="service-provider-member-intives"),
    path('members/remove/<str:pk>/<str:member_id>', views.service_provider_remove_member, name="service-provider-remove-member"),

    # Settings
    path('update/<str:pk>/', views.update_service_provider, name="update-service-provider"),
    path('api-key/<str:pk>/', views.api_keys, name="service-provider-api-key"),
]