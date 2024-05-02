from django.shortcuts import redirect
from functools import wraps
from django.shortcuts import get_object_or_404
from django.contrib import messages


def unauthenticated_user(view_func):

    def wrapper_func(request, *args, **kwargs):
        # If user is authenticated, takes the user to dashboard,
        # otherwise shows desired view.
        if request.user.is_authenticated:
            return redirect('dashboard')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def subscription_submission_required(Subscriber):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            subscriber = get_object_or_404(Subscriber, id=kwargs.get('pk'))
            if not subscriber.is_submitted:
                messages.add_message(
                    request,
                    messages.INFO,
                    (
                        "Please fill out the subscription form to unlock"
                        " more activities in your account."
                    ),
                )
                return redirect('dashboard')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
