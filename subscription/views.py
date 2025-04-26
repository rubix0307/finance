from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .services import SubscriptionManager



def test_subscription(request):
    mgr = SubscriptionManager(request.user)
    if not mgr.can('photo_analyze'):
        return JsonResponse({'status': 'Error'})
    mgr.register('message_analyze')
    return JsonResponse({'status': 'OK'})