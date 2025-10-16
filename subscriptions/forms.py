# subscriptions/forms.py
from django import forms
from .models import Subscription
from django.utils import timezone

class SubscriptionForm(forms.ModelForm):
    class Meta:
        model = Subscription
     
        fields = [
            'provider', 'plan', 'start_date', 'end_date',
            'auto_renew', 'currency', 'description'
        ]
        widgets = {
            'start_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'description': forms.Textarea(attrs={'rows':3}),
        }

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get('start_date') or timezone.now()
        end = cleaned.get('end_date')
        if end and start and end <= start:
            raise forms.ValidationError("La fecha de fin debe ser posterior a la fecha de inicio.")
        return cleaned
