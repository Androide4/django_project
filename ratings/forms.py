from django import forms
from .models import Rating

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['name', 'comment', 'score']
        widgets = {
            'comment': forms.Textarea(attrs={'rows':3}),
            'score': forms.NumberInput(attrs={'min':1,'max':10}),
        }
