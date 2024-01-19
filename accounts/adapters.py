from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return '/create-profile/'

    def respond_user_inactive(self, request, user):
        messages.error(request, 'Your username or password does not match an account')
        return redirect('login')

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def get_connect_redirect_url(self, request, socialaccount):
        return '/link-account/'