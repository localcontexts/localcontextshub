from allauth.account.adapter import DefaultAccountAdapter

class CustomAccountAdapter(DefaultAccountAdapter):

    def get_signup_redirect_url(self, request):
        return '/create-profile/'