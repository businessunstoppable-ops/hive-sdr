import re

KEYWORD_MAP = {
    "gym": ["gym", "fitness", "workout", "crossfit", "yoga", "pilates", "fitness center", "health club"],
    "restaurant": ["restaurant", "cafe", "coffee shop", "bakery", "bistro", "diner", "eatery", "pub", "grill"],
    "plumber": ["plumber", "plumbing", "pipe", "drain", "water heater", "plumbing service"],
    "saas": ["software", "saas", "cloud", "platform", "api", "subscription", "app", "web app"],
    "coffee shop": ["coffee", "espresso", "latte", "brew", "cafe", "coffee house"],
    "retail": ["store", "shop", "boutique", "market", "retail", "merchandise", "ecommerce"],
    "healthcare": ["clinic", "doctor", "dentist", "medical", "health", "wellness", "hospital", "dental"],
    "automotive": ["auto", "car", "mechanic", "repair", "tire", "dealership", "automotive", "garage"],
    "beauty": ["salon", "spa", "nail", "hair", "beauty", "barber", "cosmetics", "esthetician"],
    "real estate": ["real estate", "realtor", "property", "home", "condo", "realtor", "realty"],
    "education": ["school", "college", "university", "training", "tutoring", "academy", "learning"],
    "construction": ["construction", "builder", "contractor", "remodel", "roof", "build", "renovation"],
    "legal": ["law", "attorney", "legal", "lawyer", "firm", "counsel", "solicitor"],
    "marketing": ["marketing", "advertising", "seo", "social media", "digital marketing", "agency"],
    "accounting": ["accounting", "bookkeeping", "tax", "cpa", "accountant", "finance"],
    "insurance": ["insurance", "agent", "broker", "insure", "coverage", "life insurance"],
    "dentist": ["dentist", "dental", "teeth", "orthodontist", "dental clinic"],
    "lawyer": ["lawyer", "attorney", "legal", "law firm", "solicitor"],
    "hotel": ["hotel", "inn", "lodge", "accommodation", "resort", "motel"],
    "photography": ["photography", "photographer", "photo", "portrait", "wedding photography"],
}

def detect_industry_from_text(text: str) -> str:
    text_lower = text.lower()
    for industry, keywords in KEYWORD_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                return industry
    return "Unknown"

def detect_industry_from_website(website: str, use_ai: bool = False) -> str:
    if not website:
        return "Unknown"
    # Simple: use the domain name as text
    domain = website.replace("https://", "").replace("http://", "").split("/")[0]
    return detect_industry_from_text(domain)

# Optional: Map Google Places types to industries
PLACES_TYPE_MAP = {
    "gym": ["gym", "fitness_center", "health"],
    "restaurant": ["restaurant", "cafe", "bakery", "bar"],
    "plumber": ["plumber", "general_contractor"],
    "dentist": ["dentist", "dental_clinic"],
    "lawyer": ["lawyer"],
    "hotel": ["lodging", "hotel"],
    "real estate": ["real_estate_agency"],
    "beauty": ["beauty_salon", "hair_care", "spa"],
    "automotive": ["car_dealer", "car_repair", "auto_parts_store"],
    "healthcare": ["doctor", "hospital", "physiotherapist", "medical_center"],
}

def detect_industry_from_place_types(types: list) -> str:
    for industry, place_types in PLACES_TYPE_MAP.items():
        for pt in place_types:
            if pt in types:
                return industry
    return "Unknown"
