from functools import wraps
from django.shortcuts import redirect
from .models import Researcher
from .utils import checkif_user_researcher


def is_researcher():
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            researcher_pk = kwargs.get('pk')
            researcher = Researcher.objects.get(id=researcher_pk)
            user_can_view = checkif_user_researcher(researcher, request.user)
            if not user_can_view:
                return redirect('public-researcher', researcher_pk)

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
