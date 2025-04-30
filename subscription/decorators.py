from django.http import HttpResponseForbidden
from .services import SubscriptionManager

def feature_required(code: str):
    def deco(view):
        def wrapper(request, *args, **kwargs):
            mgr = request.user.subscription_manager
            if not mgr.can(code):
                return HttpResponseForbidden()
            return view(request, *args, **kwargs)
        return wrapper
    return deco