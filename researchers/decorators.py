from functools import wraps
from django.shortcuts import redirect
from .models import Researcher
from .utils import checkif_user_researcher


def is_researcher(pk_arg_name='pk'):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            researcher = Researcher.objects.get(id=kwargs.get('pk'))
            user_can_view = checkif_user_researcher(researcher, request.user)
            if not user_can_view:
                return redirect('restricted')

            # update view function args
            kwargs['pk'] = researcher.id
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
