from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account import signals
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import redirect

class CustomAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return '/create-profile/'

    def respond_user_inactive(self, request, user):
        messages.error(request, 'Your username or password does not match an account')
        return redirect('login')
    
    def post_login(
        self,
        request,
        user,
        *,
        email_verification,
        signal_kwargs,
        email,
        signup,
        redirect_url
    ):
        from allauth.account.utils import get_login_redirect_url

        response = HttpResponseRedirect(
            get_login_redirect_url(request, redirect_url, signup=signup)
        )
        
        if signal_kwargs is None:
            signal_kwargs = {}
        signals.user_logged_in.send(
            sender=user.__class__,
            request=request,
            response=response,
            user=user,
            **signal_kwargs,
        )
        return response

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    
    def get_connect_redirect_url(self, request, socialaccount):
        return '/link-account/'