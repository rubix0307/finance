from django.forms import ColorInput, ModelForm
from parler.forms import TranslatableModelForm

from .models import ReceiptItemCategory


class ReceiptItemCategoryForm(TranslatableModelForm):
    class Meta:
        model = ReceiptItemCategory
        fields = '__all__'
        widgets = {
            'color': ColorInput(),
        }