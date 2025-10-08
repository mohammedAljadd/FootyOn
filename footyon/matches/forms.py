# matches/forms.py
from django import forms
from .models import Match
from django.utils.translation import gettext_lazy as _


class MatchForm(forms.ModelForm):
    class Meta:
        model = Match
        fields = ["date", "time", "location_name", "max_players", "location_google_maps_short_url"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "location_name": forms.TextInput(attrs={"class": "form-control"}),
            "max_players": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
            "location_google_maps_short_url": forms.URLInput(attrs={
                "class": "form-control",
                "placeholder": "https://maps.app.goo.gl/..."
            })
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['location_name'].help_text = _("Name of the stadium or location")
        self.fields['location_google_maps_short_url'].label = _("Google Maps Link")
        self.fields['location_google_maps_short_url'].help_text = _("Paste the short Google Maps link (e.g., https://maps.app.goo.gl/...)")
        self.fields['location_google_maps_short_url'].required = False

    def clean_location_google_maps_short_url(self):
        """Validate the Google Maps short URL"""
        short_url = self.cleaned_data.get('location_google_maps_short_url')
        
        if not short_url:
            return None
        
        # Validate that it's a Google Maps URL
        if not ('maps.app.goo.gl' in short_url or 'google.com/maps' in short_url):
            raise forms.ValidationError(
                _("Please enter a valid Google Maps URL (maps.app.goo.gl or google.com/maps)")
            )
        
        return short_url

    def clean_max_players(self):
        """Ensures the admin cannot reduce max_players below the number of joined participants."""
        max_players = self.cleaned_data.get('max_players')
        if self.instance.pk:
            joined_count = self.instance.participation_set.filter(
                status='joined', 
                removed=False, 
                is_no_show=False
            ).count()
            if max_players < joined_count:
                raise forms.ValidationError(
                    _("Cannot set max players below current joined count (%(count)d).") 
                    % {'count': joined_count}
                )
        return max_players