from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing, name='landing'),

    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),

    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('verify/', views.verify, name='verify'),

    path('invite/', views.invite_user, name='invite'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('onboarding/on', views.onboarding_on, name='onboarding-on'),
    path('create-profile/', views.create_profile, name='create-profile'),

    path('update-profile/', views.update_profile, name='update-profile'),
    path('manage/', views.manage_organizations, name='manage-orgs'),
    path('change-password/', views.change_password, name='change-password'),
    path('deactivate/', views.deactivate_user, name='deactivate-user'),

    path('select-account/', views.registration_reason, name='select-account'),
    
    path('registry/', views.organization_registry, name='organization-registry'),
    path('counter/', views.hub_counter, name='hub-counter'),


    path('reset-password/', auth_views.PasswordResetView.as_view(template_name="accounts/password-reset.html"), name="reset_password"),
    path('reset-password-sent/', auth_views.PasswordResetDoneView.as_view(template_name="accounts/password-reset-sent.html"), name="password_reset_done"),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password-reset-confirm.html"), name="password_reset_confirm"),
    path('reset-password-complete/', auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password-reset-done.html"), name="password_reset_complete"),

]