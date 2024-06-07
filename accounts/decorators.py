from django.shortcuts import redirect
from django.contrib import messages
from researchers.utils import is_user_researcher


def unauthenticated_user(view_func):

    def wrapper_func(request, *args, **kwargs):
        # If user is authenticated, takes the user to dashboard,
        # otherwise shows desired view.
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def zero_account_user(view_func):

    def wrapper_func(request, *args, **kwargs):
        user = request.user
        affiliations = (
            user.user_affiliations.prefetch_related(
                "institutions",
            )
            .all()
        )
        has_institutions = any(
            affiliation.institutions.exists()
            for affiliation in affiliations
        )
        if has_institutions or is_user_researcher(user):
            messages.add_message(
                request,
                messages.INFO,
                "Try creating account from Create an account button.")
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func
