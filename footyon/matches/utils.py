import re
import requests
from urllib.parse import unquote

def convert_to_embed_url(short_url):
    """
    Convert a Google Maps short URL to an embeddable iframe URL.
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