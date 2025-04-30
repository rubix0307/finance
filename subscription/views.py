from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from .services import SubscriptionManager



def test_subscription(request):
    mgr = request.user.subscription_manager
    if not mgr.can('photo_analyze'):
        return JsonResponse({'status': 'Error'})
    mgr.register('message_analyze')
    return JsonResponse({'status': 'OK'})