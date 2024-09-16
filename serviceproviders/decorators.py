from functools import wraps
from django.shortcuts import redirect
from helpers.utils import check_member_role
from .utils import get_service_provider


def member_required(roles=[]):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            service_provider = get_service_provider(kwargs.get('pk'))
            member_role = check_member_role(request.user, service_provider)
            if member_role not in roles:
                return redirect('restricted')
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
