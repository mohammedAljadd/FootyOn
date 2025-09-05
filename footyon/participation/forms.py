from django import forms
from .models import Participation

class NoShowForm(forms.ModelForm):
    class Meta:
        model = Participation
        fields = ['no_show_reason']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['no_show_reason'].choices = [
            (key, label) for key, label in Participation.NO_SHOW_REASON_CHOICES
        ]
        self.fields['no_show_reason'].required = True
