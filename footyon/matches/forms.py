# matches/forms.py
from django import forms
from .models import Match, Stadium
from django.utils.translation import gettext_lazy as _
import re
import requests
from urllib.parse import unquote

class MatchForm(forms.ModelForm):
    # Dropdown to select existing stadiums
    stadium = forms.ModelChoiceField(
        queryset=Stadium.objects.all(),
        label=_("Stadium"),
        required=True,
        empty_label=_("Select a stadium"),
        widget=forms.Select(attrs={"class": "form-select"})
    )
 
    class Meta:
        model = Match
        fields = ["date", "time", "stadium", "max_players"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "max_players": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def clean_max_players(self):
        max_players = self.cleaned_data.get("max_players")
        if self.instance.pk:  # editing existing match
            joined_count = self.instance.participation_set.filter(
                status="joined", removed=False, is_no_show=False
            ).count()
            if max_players < joined_count:
                raise forms.ValidationError(
                    _("Cannot set max players below current joined count (%(count)d).") % {"count": joined_count}
                )
        return max_players

class StadiumForm(forms.ModelForm):
    google_maps_short_url = forms.URLField(
        required=False,
        label=_("Google Maps Link"),
        help_text=_("Paste the short Google Maps link (e.g., https://maps.app.goo.gl/...)"),
        widget=forms.URLInput(attrs={"class": "form-control", "placeholder": "https://maps.app.goo.gl/..."})
    )

    class Meta:
        model = Stadium
        fields = ["name", "google_maps_short_url"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "google_maps_short_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://maps.app.goo.gl/..."
            }),
        }
