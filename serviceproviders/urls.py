from django.urls import path
from . import views

urlpatterns = [
    path('preparation-step/', views.preparation_step, name="prep-service_provider"),
    # path('create-service-provider/', views.create_service_provider, name="create-service-provider"),
    # path('confirm-subscription-service-provider/<str:service_provider_id>/', views.confirm_subscription_service_provider, name="confirm-subscription-service-provider"),

    # Public view
    # path('view/<str:pk>/', views.public_service_provider_view, name="public-service-provider"),
    # path('embed/<str:pk>/', views.embed_otc_notice, name="embed-notice-service-provider"),

    # path('update/<str:pk>/', views.update_service_provider, name="update-service-provider"),

    # path('notices/<str:pk>/', views.service_provider_notices, name="service-provider-notices"),
    # path('notices/otc/delete/<str:pk>/<str:notice_id>/', views.delete_otc_notice, name="service-provider-delete-otc"),

    # path('connections/<str:pk>/', views.connections, name="service-provider-connections"),

    # path('api-key/<str:pk>/', views.api_keys, name="service-provider-api-key"),
]