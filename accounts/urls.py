from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path('', views.landing, name='landing'),
    path('login/', views.login, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout, name='logout'),
    path('social/signup/', views.CustomSocialSignupView.as_view(), name='social_signup'),
    path(
        'social/connections/<str:provider>/',
        views.CustomSocialConnectionsView.as_view(),
        name='socialaccount_connections'
    ),
    path(
        "subscription-inquiry/",
        views.subscription_inquiry,
        name="subscription-inquiry",
    ),
    path('activate/<uidb64>/<token>', views.ActivateAccountView.as_view(), name='activate'),
    path('verify/', views.verify, name='verify'),
    path('invite/', views.invite_user, name='invite'),
    path('invitations/', views.member_invitations, name='member-invitations'),
    path(
        'invitations/delete/<str:pk>/',
        views.delete_member_invitation,
        name='delete-member-invitation'
    ),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('onboarding/on', views.onboarding_on, name='onboarding-on'),
    path('create-profile/', views.create_profile, name='create-profile'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('confirm-email/<uidb64>/<token>/', views.confirm_email, name='confirm_email'),
    path('manage/', views.manage_organizations, name='manage-orgs'),
    path(
        'leave-account/<str:account_type>/<int:account_id>',
        views.leave_account,
        name='leave-account'
        ),
    path('link-account/', views.link_account, name='link-account'),
    path('change-password/', views.change_password, name='change-password'),
    path('deactivate/', views.deactivate_user, name='deactivate-user'),
    path('select-account/', views.select_account, name='select-account'),
    path('registry/', views.registry, name='registry'),
    path('registry/<str:filtertype>/', views.registry, name='registry'),
    path('projects-board/', views.projects_board, name='projects-board'),
    path('projects-board/<str:filtertype>/', views.projects_board, name='projects-board'),
    path('counter/', views.hub_counter, name='hub-counter'),
    path('newsletter/subscribe/', views.newsletter_subscription, name='newsletter-subscription'),
    path(
        'newsletter/preferences/<emailb64>/',
        views.newsletter_unsubscription,
        name='newsletter-unsubscription'
    ),
    path('reset-password/', views.CustomPasswordResetView.as_view(), name="reset_password"),
    path(
        'reset-password-sent/',
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password-reset-sent.html"
        ),
        name="password_reset_done"
    ),
    path(
        'reset/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password-reset-confirm.html"
        ),
        name="password_reset_confirm"
    ),
    path(
        'reset-password-complete/',
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password-reset-done.html"
        ),
        name="password_reset_complete"
    ),
    path(
        "subscription/<str:pk>/<str:account_type>/",
        views.subscription,
        name="subscription"
    ),
]
