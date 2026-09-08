from functools import wraps

from django.core.exceptions import PermissionDenied

from .permissions import is_full_operator


def superuser_required(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not is_full_operator(request.user):
            raise PermissionDenied
        return view(request, *args, **kwargs)

    return wrapped