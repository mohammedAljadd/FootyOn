import requests
import re
from urllib.parse import unquote

def get_embed_url_from_short_link(short_url):
    """
    Convert a Google Maps short URL (maps.app.goo.gl) to an embeddable iframe URL.
    
    Args:
        short_url (str): Short Google Maps URL (e.g., https://maps.app.goo.gl/jVd6iw9EFnNssm8p6)
    
    Returns:
        str: Embeddable Google Maps URL or None if conversion fails
    """
    try:
        # Step 1: Follow the redirect to get the full URL
        print(f"Following redirect from: {short_url}")
        response = requests.get(short_url, allow_redirects=True, timeout=10)
        full_url = response.url
        print(f"Full URL: {full_url}\n")
        
        # Step 2: Extract the place_id from the URL
        # Google Maps place URLs contain a place_id in format like:
        # 0x12cdd10c3345b9bd:0x8a5dc01882b070a3
        
        # Pattern 1: Look for place_id in the URL (most accurate)
        place_id_match = re.search(r'(0x[0-9a-f]+:0x[0-9a-f]+)', full_url)
        
        if place_id_match:
            place_id = place_id_match.group(1)
            print(f"Found Place ID: {place_id}")
            
            # Also extract coordinates for better positioning
            coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', full_url)
            
            if coords_match:
                lat = coords_match.group(1)
                lon = coords_match.group(2)
                print(f"Found Coordinates: {lat}, {lon}")
                
                # Extract zoom level if available (format: ,15z or similar)
                zoom_match = re.search(r',(\d+(?:\.\d+)?)z', full_url)
                zoom = zoom_match.group(1) if zoom_match else "15"
                
                # Calculate the 'd' parameter (distance/zoom related)
                # The 'd' value represents the viewport size in meters
                # Lower value = more zoomed in, higher value = more zoomed out
                # Good default values: 1000-5000 for city view, 500-1000 for street view
                zoom_float = float(zoom)
                
                # Better zoom calculation - matches Google Maps embed behavior
                # Typical good value is around 2000-5000 for stadium view
                d_value = 6000
                
                # Clamp between reasonable bounds
                d_value = max(1000, min(d_value, 10000))
                
                print(f"Zoom level: {zoom}")
                print(f"Calculated 'd' parameter: {d_value}\n")
                
                # Build accurate embed URL with place_id
                # Format breakdown:
                # !1m18 = place map (18 parameters)
                # !1m12!1m3!1d{d_value}!2d{lon}!3d{lat} = viewport/zoom settings
                # !2m3!1f0!2f0!3f0 = pitch, heading, tilt (all 0 for default view)
                # !3m2!1i1024!2i768 = map size
                # !4f13.1 = zoom level
                # !3m3!1m2!1s{place_id} = place identifier (THE IMPORTANT PART!)
                # Place name will be extracted from the URL
                
                # Try to extract place name from URL
                place_name_match = re.search(r'/place/([^/]+)', full_url)
                place_name = ""
                if place_name_match:
                    place_name = unquote(place_name_match.group(1)).replace('+', ' ')
                    # URL encode special characters but keep the structure
                    place_name = place_name.replace('é', '%C3%A9').replace('è', '%C3%A8')
                    place_name = place_name.replace('à', '%C3%A0').replace('ô', '%C3%B4')
                    place_name = f"!2s{place_name}"
                
                embed_url = (
                    f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d{d_value}!"
                    f"2d{lon}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!"
                    f"3m3!1m2!1s{place_id}{place_name}!5e0!3m2!1sen!2sfr"
                )
                
                return embed_url
        
        # Pattern 2: If no place_id found, try to extract location name
        # This is less accurate but still works
        name_match = re.search(r'/place/([^/]+)', full_url)
        if name_match:
            location_name = unquote(name_match.group(1))
            print(f"Found location name: {location_name}")
            
            coords_match = re.search(r'@(-?\d+\.\d+),(-?\d+\.\d+)', full_url)
            if coords_match:
                lat = coords_match.group(1)
                lon = coords_match.group(2)
                
                # Use coordinates-based embed (less accurate, no marker)
                embed_url = (
                    f"https://www.google.com/maps/embed?pb=!1m14!1m12!1m3!1d10000!"
                    f"2d{lon}!3d{lat}!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!"
                    f"5e0!3m2!1sen!2sfr"
                )
                return embed_url
        
        print("❌ Could not extract place_id or coordinates from URL")
        return None
        
    except Exception as e:
        print(f"❌ Error converting URL: {e}")
        return None


def generate_iframe_html(embed_url, width=600, height=450):
    """
    Generate complete iframe HTML code for embedding Google Maps.
    
    Args:
        embed_url (str): Google Maps embed URL
        width (int): iframe width in pixels (default: 600)
        height (int): iframe height in pixels (default: 450)
    
    Returns:
        str: Complete iframe HTML code
    """
    if not embed_url:
        return None
    
    iframe_html = f'''<iframe 
    src="{embed_url}" 
    width="{width}" 
    height="{height}" 
    style="border:0;" 
    allowfullscreen="" 
    loading="lazy" 
    referrerpolicy="no-referrer-when-downgrade">
</iframe>'''
    
    return iframe_html


def extract_place_id_from_url(url):
    """
    Helper function to extract just the place_id from a Google Maps URL.
    Useful for debugging.
    
    Args:
        url (str): Google Maps URL
    
    Returns:
        str: Place ID or None
    """
    place_id_match = re.search(r'(0x[0-9a-f]+:0x[0-9a-f]+)', url)
    return place_id_match.group(1) if place_id_match else None


# ===== EXAMPLE USAGE =====
if __name__ == "__main__":
    # Example: Convert a short URL
    short_url = "https://maps.app.goo.gl/jVd6iw9EFnNssm8p6"
    
    print("="*60)
    print("GOOGLE MAPS SHORT URL TO EMBED CONVERTER")
    print("="*60 + "\n")
    
    embed_url = get_embed_url_from_short_link(short_url)
    
    if embed_url:
        print("="*60)
        print("✅ CONVERSION SUCCESSFUL!")
        print("="*60 + "\n")
        
        print("Embed URL:")
        print(embed_url)
        print("\n")
        
        # Generate iframe HTML
        iframe_html = generate_iframe_html(embed_url, width=600, height=450)
        print("="*60)
        print("IFRAME HTML CODE:")
        print("="*60)
        print(iframe_html)
        
        print("\n" + "="*60)
        print("Copy the iframe code above to use in your HTML!")
        print("="*60)
    else:
        print("="*60)
        print("❌ CONVERSION FAILED")
        print("="*60)
        print("\nTip: Try getting the embed code directly from Google Maps:")
        print("1. Open the location in Google Maps")
        print("2. Click 'Share' button")
        print("3. Select 'Embed a map' tab")
        print("4. Copy the iframe code")