from django.forms import ColorInput, ModelForm
from .models import ReceiptItemCategory


class ReceiptItemCategoryForm(ModelForm):
    class Meta:
        model = ReceiptItemCategory
        fields = '__all__'
        widgets = {
            'color': ColorInput(),
        }