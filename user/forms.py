from django import forms
from .models import Feedback, User


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5}),
        }

class UserLanguageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['language_code']
        widgets = {
            'language_code': forms.Select(attrs={
                'onchange': 'this.form.submit()'
            }),
        }
