from django.core.exceptions import PermissionDenied


class UnconfirmedAccountException(Exception):
    pass


class UnsubscribedAccountException(PermissionDenied):
    pass
