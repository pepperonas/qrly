"""
Google Review QR Code Generator
Simple Place ID to Review URL conversion - No complex URL parsing
"""


def is_valid_place_id(place_id: str) -> bool:
    """
    Validate that a string is a proper Google Place ID

    Args:
        place_id: String to validate

    Returns:
        True if valid Place ID format (ChIJ... or EI...)

    Examples:
        >>> is_valid_place_id("ChIJp4JiUCNP0xQR1JaSjpW_Hms")
        True
        >>> is_valid_place_id("https://google.com/maps/...")
        False
    """
    if not place_id or not isinstance(place_id, str):
        return False

    place_id = place_id.strip()

    # Valid Place IDs start with ChIJ or EI
    if not (place_id.startswith('ChIJ') or place_id.startswith('EI')):
        return False

    # Should be alphanumeric with dashes and underscores
    # Typical length: 20-30 characters
    if len(place_id) < 10 or len(place_id) > 50:
        return False

    return True


def generate_review_url(place_id: str) -> str:
    """
    Generate Google Review URL from Place ID

    Args:
        place_id: Valid Google Place ID (ChIJ... or EI...)

    Returns:
        Direct review URL

    Raises:
        ValueError: If Place ID is invalid

    Examples:
        >>> generate_review_url("ChIJp4JiUCNP0xQR1JaSjpW_Hms")
        'https://search.google.com/local/writereview?placeid=ChIJp4JiUCNP0xQR1JaSjpW_Hms'
    """
    if not is_valid_place_id(place_id):
        raise ValueError(f"Invalid Place ID: {place_id}. Must start with 'ChIJ' or 'EI'")

    return f"https://search.google.com/local/writereview?placeid={place_id.strip()}"


# CLI Helper
def create_review_qr(place_id: str, text: str = None) -> dict:
    """
    Create Google Review QR code metadata

    Args:
        place_id: Valid Google Place ID
        text: Optional text for QR code (max 20 characters)

    Returns:
        Dict with QR code generation parameters

    Example:
        >>> create_review_qr("ChIJp4JiUCNP0xQR1JaSjpW_Hms", "RESTAURANT")
        {'url': 'https://search.google.com/local/writereview?placeid=...', ...}
    """
    if not is_valid_place_id(place_id):
        raise ValueError(
            f"Invalid Place ID: {place_id}\n\n"
            f"How to get a Place ID:\n"
            f"1. Visit: https://developers.google.com/maps/documentation/places/web-service/place-id\n"
            f"2. Scroll to 'Place ID Finder' widget\n"
            f"3. Search for your business\n"
            f"4. Copy the Place ID (starts with ChIJ)\n"
        )

    review_url = generate_review_url(place_id)

    return {
        'url': review_url,
        'place_id': place_id,
        'text': text,
        'is_review_link': True
    }


if __name__ == "__main__":
    # Demo
    test_place_id = "ChIJp4JiUCNP0xQR1JaSjpW_Hms"

    print("=" * 70)
    print("Google Review QR Generator - Simple Place ID Workflow")
    print("=" * 70)
    print()
    print(f"Place ID: {test_place_id}")
    print(f"Valid: {is_valid_place_id(test_place_id)}")
    print()

    if is_valid_place_id(test_place_id):
        review_url = generate_review_url(test_place_id)
        print(f"Review URL: {review_url}")
        print()
        print("✅ Test this URL in your browser - should open review form!")

    print("=" * 70)
