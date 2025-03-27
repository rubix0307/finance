from ninja import Router
from ninja.security import django_auth

from .schemas import UserSchema

router = Router()

@router.get("/me/", auth=django_auth, response=UserSchema)
def list_currencies(request):
    return request.user
