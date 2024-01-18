from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib import messages
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return '/create-profile/'

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def get_connect_redirect_url(self, request, socialaccount):
        return '/link-account/'