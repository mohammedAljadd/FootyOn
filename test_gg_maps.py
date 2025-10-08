import requests
import re

def maps_url_to_embed(short_url, width=600, height=450, lang="en", zoom=15):
    """
    Convert a Google Maps short URL into an embeddable <iframe> HTML snippet.
    No API key required.
    """
    # Step 1: Expand short URL
    resp = requests.get(short_url, allow_redirects=True)
    long_url = resp.url

    # Step 2: Extract coordinates (works with most Maps URLs)
    lat, lon = None, None
    match = re.search(r'@([0-9\.\-]+),([0-9\.\-]+)', long_url)
    if match:
        lat, lon = match.groups()
    else:
        # Try alternative pattern (!3dLAT!4dLON)
        match = re.search(r'!3d([0-9\.\-]+)!4d([0-9\.\-]+)', long_url)
        if match:
            lat, lon = match.groups()

    if not lat or not lon:
        raise ValueError("Could not extract coordinates from URL")

    # Step 3: Build <iframe> HTML
    iframe = f"""
    <iframe
        width="{width}"
        height="{height}"
        style="border:0;"
        loading="lazy"
        allowfullscreen
        src="https://maps.google.com/maps?q={lat},{lon}&hl={lang}&z={zoom}&output=embed">
    </iframe>
    """
    return iframe.strip()


# Example usage:
short_url = "https://maps.app.goo.gl/gRvAUQeymQWQHCtT6"
print(maps_url_to_embed(short_url, lang="fr", zoom=14))
