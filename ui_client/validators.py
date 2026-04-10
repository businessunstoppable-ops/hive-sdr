"""Input validation for campaign data"""

from typing import Tuple, Optional

def validate_campaign_input(industry: str, city: str, max_leads: int) -> Tuple[bool, Optional[str]]:
    """
    Validate campaign input parameters.
    Returns (is_valid, error_message)
    """
    
    # Check industry
    if not industry or len(industry.strip()) < 2:
        return False, "Industry must be at least 2 characters"
    
    if len(industry) > 50:
        return False, "Industry name is too long (max 50 characters)"
    
    # Check city
    if not city or len(city.strip()) < 2:
        return False, "City must be at least 2 characters"
    
    if len(city) > 100:
        return False, "City name is too long (max 100 characters)"
    
    # Check max_leads
    if max_leads < 1:
        return False, "Maximum leads must be at least 1"
    
    if max_leads > 50:
        return False, "Maximum leads cannot exceed 50"
    
    # Optional: Check for dangerous characters
    dangerous_chars = ['<', '>', '&', ';', '|', '$', '`']
    for char in dangerous_chars:
        if char in industry or char in city:
            return False, f"Invalid character: {char}"
    
    return True, None

def sanitize_text(text: str) -> str:
    """Sanitize user input to prevent injection"""
    if not text:
        return ""
    # Remove dangerous characters
    dangerous = ['<', '>', '&', ';', '|', '$', '`', '(', ')']
    for char in dangerous:
        text = text.replace(char, '')
    return text.strip()[:200]  # Limit length
