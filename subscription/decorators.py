from django.http import HttpResponseForbidden
from .services import SubscriptionManager

def feature_required(code: str):
    def deco(view):
        def wrapper(request, *args, **kwargs):
            mgr = SubscriptionManager(request.user)
            if not mgr.can(code):
                return HttpResponseForbidden("Нет квоты")
            mgr.register(code)
            return view(request, *args, **kwargs)
        return wrapper
    return deco