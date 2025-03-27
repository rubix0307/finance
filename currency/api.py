from ninja import Router
from .models import Currency
from .schemas import CurrencySchema

router = Router()

@router.get("/", response=list[CurrencySchema])
def list_currencies(request):
    return Currency.objects.all()
