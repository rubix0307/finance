from django import forms
from parler.forms import TranslatableModelForm
from django.forms import ColorInput, ModelForm, DateField, DateInput, inlineformset_factory, BaseInlineFormSet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from .models import Receipt, ReceiptItem, Shop, ReceiptItemCategory



class ReceiptItemCategoryForm(TranslatableModelForm):
    class Meta:
        model = ReceiptItemCategory
        fields = '__all__'
        widgets = {
            'color': ColorInput(),
        }


class ReceiptForm(ModelForm):
    date_only = DateField(
        label=_('Date'),
        widget=DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        input_formats=['%Y-%m-%d'],
    )

    class Meta:
        model = Receipt
        fields = ['section', 'shop', 'currency']
        labels = {
            'section': _('Section'),
            'shop': _('Shop'),
            'currency': _('Currency'),
        }

    def __init__(self, *args, user=None, **kwargs):
        instance: Receipt = kwargs.get('instance', None)
        super().__init__(*args, **kwargs)

        self.fields['section'].queryset = user.sections.all()

        if instance and instance.section:
            qs = Shop.objects.filter(receipt__section=instance.section).distinct()
        else:
            qs = Shop.objects.none()
        self.fields['shop'].queryset = qs
        self.fields['shop'].initial = instance.shop

        self.fields['currency'].initial = instance.currency

        if instance and instance.date:
            dt = instance.date
            self.fields['date_only'].initial = dt.date().isoformat()

        today = timezone.localdate()
        self.fields['date_only'].widget.attrs['max'] = today.isoformat()

    def clean(self):
        cleaned = super().clean()
        date = cleaned.get('date_only')
        if date is None:
            raise forms.ValidationError(_('The Date field is required'))
        # не в будущем
        today = timezone.localdate()
        if date > today:
            raise forms.ValidationError(_('The date cannot be in the future'))

        cleaned['date'] = date
        return cleaned

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.date = self.cleaned_data['date']
        if commit:
            instance.save()
        return instance


class BaseReceiptItemFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()
        remaining = 0
        for form in self.forms:
            if self.can_delete and self._should_delete_form(form):
                continue
            if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                remaining += 1
        if remaining < 1:
            raise forms.ValidationError(_('The receipt must contain at least one item'))


ReceiptItemFormSet = inlineformset_factory(
    Receipt,
    ReceiptItem,
    fields=('name', 'price', 'category'),
    formset=BaseReceiptItemFormSet,
    extra=0,
    can_delete=True,
)
