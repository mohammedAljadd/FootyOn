from django import forms
from .models import Match
from django import forms
from .models import Match

class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        # which model fields we want exposed in the form
        fields = ["date", "time", "location_name", "location_google_maps_url", "location_google_maps_embed_url", "max_players"]

        # Use HTML5 input types so the browser shows proper pickers 
        # (date picker, time picker, etc.) instead of plain text boxes
        # in django admin, we can have date picker without widgets, but
        # because we used custom template we need to use these widgets
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "location_name": forms.TextInput(attrs={"class": "form-control"}),
            "location_google_maps_url": forms.URLInput(attrs={"class": "form-control"}),
            "location_google_maps_embed_url": forms.TextInput(attrs={"class": "form-control"}),
            "max_players": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }


