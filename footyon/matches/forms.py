# matches/forms.py
from django import forms
from .models import Match
from django.utils.translation import gettext_lazy as _
import re
import requests


class MatchForm(forms.ModelForm):
    # Add a field for the short Google Maps URL (user-friendly input)
    location_google_maps_short_url = forms.URLField(
        required=False,
        label=_("Google Maps Link"),
        help_text=_("Paste the short Google Maps link (e.g., https://maps.app.goo.gl/...)"),
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "https://maps.app.goo.gl/..."
        })
    )
    
    class Meta:
        model = Match
        # Which model fields we want exposed in the form
        fields = ["date", "time", "location_name", "max_players"]

        # Use HTML5 input types so the browser shows proper pickers 
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "time": forms.TimeInput(attrs={"type": "time", "class": "form-control"}),
            "location_name": forms.TextInput(attrs={"class": "form-control"}),
            "max_players": forms.NumberInput(attrs={"class": "form-control", "min": 1}),
        }

    def __init__(self, *args, **kwargs):
        """
        Override __init__ to pre-populate the short URL field when editing.
        Note: We can't reverse-engineer the short URL from embed URL,
        so this field will be empty when editing. User can paste a new one if needed.
        """
        super().__init__(*args, **kwargs)
        
        # Add help text for location name
        self.fields['location_name'].help_text = _("Name of the stadium or location")

    def clean_location_google_maps_short_url(self):
        """
        Validate and convert the short Google Maps URL to an embed URL.
        This runs when the form is submitted.
        """
        short_url = self.cleaned_data.get('location_google_maps_short_url')
        
        # If no URL provided, that's okay (field is optional)
        if not short_url:
            return None
        
        # Validate that it's a Google Maps URL
        if not ('maps.app.goo.gl' in short_url or 'google.com/maps' in short_url):
            raise forms.ValidationError(
                _("Please enter a valid Google Maps URL (maps.app.goo.gl or google.com/maps)")
            )
        
        # Convert short URL to embed URL
        try:
            embed_url = self._convert_to_embed_url(short_url)
            if not embed_url:
                raise forms.ValidationError(
                    _("Could not convert the Google Maps URL. Please try copying the URL again.")
                )
            return embed_url
        except Exception as e:
            raise forms.ValidationError(
                _("Error processing Google Maps URL: %(error)s") % {'error': str(e)}
            )

    def _convert_to_embed_url(self, short_url):
        """
        Convert a Google Maps short URL to an embeddable iframe URL.
        This is the core conversion logic.
        """
        try:
            # Step 1: Follow the redirect to get the full URL
            response = requests.get(short_url, allow_redirects=True, timeout=10)
            full_url = response.url
            
            # Step 2: Extract the place_id and coordinates
            place_id_match = re.search(r'(0x[0-9a-f]+:0x[0-9a-f]+)', full_url)
            
            if place_id_match:
                place_id = place_id_match.group(1)
                
                # Extract coordinates
                coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', full_url)
                
                if coords_match:
                    lat = coords_match.group(1)
                    lon = coords_match.group(2)
                    
                    # Calculate viewport distance (fixed at 6000 for good stadium view)
                    d_value = 6000
                    
                    # Extract place name
                    from urllib.parse import unquote
                    place_name_match = re.search(r'/place/([^/]+)', full_url)
                    place_name = ""
                    if place_name_match:
                        place_name = unquote(place_name_match.group(1)).replace('+', ' ')
                        # URL encode special characters
                        place_name = place_name.replace('é', '%C3%A9').replace('è', '%C3%A8')
                        place_name = place_name.replace('à', '%C3%A0').replace('ô', '%C3%B4')
                        place_name = f"!2s{place_name}"
                    
                    # Build the embed URL
                    embed_url = (
                        f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d{d_value}!"
                        f"2d{lon}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!"
                        f"3m3!1m2!1s{place_id}{place_name}!5e0!3m2!1sen!2sfr"
                    )

                    iframe_html = (
                        f'<iframe src="{embed_url}" '
                        f'width="600" height="450" '
                        f'style="border:0;" '
                        f'allowfullscreen="" '
                        f'loading="lazy" '
                        f'referrerpolicy="no-referrer-when-downgrade">'
                        f'</iframe>'
                    )
                    
                    return iframe_html
            
            return None
            
        except Exception as e:
            print(f"Error converting Google Maps URL: {e}")
            return None

    def save(self, commit=True):
        """
        Override save to store the converted embed URL in the model.
        """
        match = super().save(commit=False)
        
        # Get the converted embed URL from cleaned data
        embed_url = self.cleaned_data.get('location_google_maps_short_url')
        
        # If we have an embed URL, save it to the model
        if embed_url:
            match.location_google_maps_embed_url = embed_url
        
        if commit:
            match.save()
        
        return match

    def clean_max_players(self):
        """
        Ensures the admin cannot reduce max_players below the number of joined participants.
        """
        max_players = self.cleaned_data.get('max_players')
        if self.instance.pk:  # editing existing match
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