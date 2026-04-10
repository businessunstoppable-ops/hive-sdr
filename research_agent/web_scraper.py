# research_agent/web_scraper.py
from typing import Dict, List
import re

class WebScraper:
    """Extracts information from business websites (mock mode)"""
    
    def scrape_website(self, url: str) -> Dict:
        """Mock scrape that returns sample data"""
        
        # Handle None or empty URL
        if not url:
            return {
                'url': None,
                'title': 'No website available',
                'meta_description': 'This business does not have a website.',
                'headings': {},
                'contact_info': {},
                'services': [],
                'has_blog': False,
                'social_links': [],
                'error': 'No website URL provided'
            }
        
        print(f"🔍 MOCK: Scraping {url}")
        
        # Extract business name from URL for variety
        try:
            business_name = url.replace("https://", "").replace("http://", "").split(".")[0]
        except:
            business_name = "business"
        
        return {
            'url': url,
            'title': f"{business_name.title()} - Official Website",
            'meta_description': f"Leading provider of services in the area. Contact us today.",
            'headings': {
                'h1': [f"Welcome to {business_name.title()}"],
                'h2': ["Our Services", "About Us", "Contact"],
                'h3': ["Why Choose Us", "Testimonials"]
            },
            'contact_info': {
                'emails': [f"info@{business_name}.com", f"hello@{business_name}.com"]
            },
            'services': [
                "Consulting Services",
                "Customer Support",
                "Product Development"
            ],
            'has_blog': True,
            'social_links': [
                f"https://facebook.com/{business_name}",
                f"https://twitter.com/{business_name}"
            ]
        }
    
    def extract_pain_points(self, website_data: Dict) -> List[str]:
        """Identify potential pain points from website data"""
        if website_data.get('error'):
            return ["No website available - this is a red flag", "May be difficult to reach"]
        
        pain_points = [
            "May be struggling with customer acquisition",
            "Potential inefficiency in operations",
            "Could benefit from modern technology solutions"
        ]
        return pain_points
    
    def find_opportunities(self, website_data: Dict) -> List[str]:
        """Identify potential opportunities"""
        if website_data.get('error'):
            return ["First step: help them establish an online presence"]
        
        opportunities = [
            "Expand digital presence",
            "Automate customer follow-ups",
            "Implement AI-powered lead generation"
        ]
        return opportunities
