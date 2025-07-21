from unittest.mock import DEFAULT
import requests
import json
import os
from urllib.parse import urlencode
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv

load_dotenv()

DEFAULT_CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID")
DEFAULT_CLIENT_SECRET = os.getenv("DIGIKEY_CLIENT_SECRET")
class DigikeyImageFinder:
    def __init__(self, client_id=DEFAULT_CLIENT_ID, client_secret=DEFAULT_CLIENT_SECRET, sandbox=False):
        """
        Initialize the Digikey API client
        
        Args:
            client_id: Your Digikey API client ID
            client_secret: Your Digikey API client secret
            sandbox: Use sandbox environment (True) or production (False)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.sandbox = sandbox
        
        # API endpoints
        if sandbox:
            self.base_url = "https://sandbox-api.digikey.com"
            self.auth_url = "https://sandbox-api.digikey.com/v1/oauth2/token"
        else:
            self.base_url = "https://api.digikey.com"
            self.auth_url = "https://api.digikey.com/v1/oauth2/token"
        
        self.access_token = None
        self.token_expires_at = None
        
    def get_access_token(self):
        """
        Get OAuth2 access token using client credentials flow
        """
        # Check if we have a valid token
        if self.access_token and self.token_expires_at:
            if datetime.now() < self.token_expires_at:
                print("Using cached access token")
                return self.access_token
        
        # Request new token
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'grant_type': 'client_credentials',
            'client_id': self.client_id,
            'client_secret': self.client_secret
        }
        
        try:
            response = requests.post(self.auth_url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            self.access_token = token_data['access_token']
            
            # Set expiration time (subtract 5 minutes for safety)
            expires_in = token_data.get('expires_in', 3600)
            self.token_expires_at = datetime.now() + timedelta(seconds=expires_in - 300)
            print(self.access_token)
            print(expires_in)
            return self.access_token
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting access token: {e}")
            return None
    
    def get_part_details(self, part_number):
        """
        Get detailed part information using ProductDetails API
        
        Args:
            part_number: The manufacturer part number to get details for
            
        Returns:
            Part details dictionary or None if not found
        """
        token = self.get_access_token()
        if not token:
            return None
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json',
            'X-DIGIKEY-Client-Id': self.client_id
        }
        
        # ProductDetails endpoint
        # api.digikey.com/products/v4/search/{productNumber}/productdetails
        # sandbox-api.digikey.com/products/v4/search/{productNumber}/productdetails
        details_url = f"{self.base_url}/products/v4/search/{part_number}/productdetails"
       # details_url = f"https://sandbox-api.digikey.com/products/v4/search/{part_number}/productdetails"
        
        try:
            response = requests.get(details_url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"Error getting details for part {part_number}: {e}")
            if hasattr(e, 'response') and e.response is not None:
                print(f"Response status: {e.response.status_code}")
                print(f"Response: {e.response.text}")
            return None
    
    def get_part_image(self, part_number):
        """
        Get the primary image URL for a given part number using ProductDetails API
        
        Args:
            part_number: The manufacturer part number
            
        Returns:
            Dictionary with image info or None if not found
        """
        part_details = self.get_part_details(part_number)
        
        if not part_details:
            return None
        
        # Extract image information from product details
        image_info = {
            'part_number': part_details.get('ManufacturerProductNumber'),
            'digikey_part_number': part_details.get('DigiKeyPartNumber'),
            'manufacturer': part_details.get('Manufacturer', {}).get('Name'),
            'description': part_details.get('Product').get('Description').get('DetailedDescription') if part_details.get('Product') else None,
            'detailed_description': part_details.get('DetailedDescription'),
            'package': part_details.get('Package', {}).get('Name') if part_details.get('Package') else None,
            'image_url': part_details.get('Product').get('PhotoUrl'),
            'datasheet_url': None,
            'product_url': part_details.get('ProductUrl'),
            'status': part_details.get('ProductStatus', {}).get('Name'),
            'images': []
        }
        
        # Get primary image
        return image_info
    
    def download_image(self, image_url, filename=None):
        """
        Download image from URL
        
        Args:
            image_url: URL of the image to download
            filename: Local filename to save as (optional)
            
        Returns:
            Path to downloaded file or None if failed
        """
        if not image_url:
            return None
        
        try:
            headers = {
                'User-Agent': 'My User Agent 1.0',
                'From': 'youremail@domain.example'  # This is another valid field
            }
            response = requests.get(image_url,headers=headers)
            response.raise_for_status()
            
            if not filename:
                # Extract filename from URL or use generic name
                filename = image_url.split('/')[-1]
                if '.' not in filename:
                    filename = f"component_image_{int(time.time())}.jpg"
            
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            return filename
            
        except requests.exceptions.RequestException as e:
            print(f"Error downloading image: {e}")
            return None



def main():
    """
    Example usage
    """
    # You need to get these from Digikey's API portal
    # Sign up at https://developer.digikey.com/
    CLIENT_ID = "ALqBLDyRIky0AiZZ5Tgzro9V7uqFBD35mClaixS5aI1rVApG"
    CLIENT_SECRET = "EweBmcan1zW2oHsVtFvNgxr0UAwq0IHzGGlMG2zfmHXwzOVBgX1jrGekMCqGkR97"
    
    # Initialize the finder
    finder = DigikeyImageFinder(CLIENT_ID, CLIENT_SECRET, sandbox=False)
    
    # Example part numbers to try
    test_parts = [
        "STM32H750VBT6",
       # "ATMEGA328P-PU",
       # "LM555CN"
    ]
    
    for part_number in test_parts:
        print(f"\nSearching for: {part_number}")
        print("-" * 50)
        
        image_info = finder.get_part_image(part_number)
        print(image_info)
        if image_info:
            print(f"Found: {image_info['part_number']}")
            print(f"Manufacturer: {image_info['manufacturer']}")
            print(f"Description: {image_info['description']}")
            print(f"Package: {image_info['package']}")
            print(f"Image URL: {image_info['image_url']}")
            print(f"Datasheet: {image_info['datasheet_url']}")
            
            # Download the image
            if image_info['image_url']:
                filename = f"{part_number}.jpg"
                downloaded = finder.download_image(image_info['image_url'], filename)
                if downloaded:
                    print(f"Image downloaded as: {downloaded}")
                else:
                    print("Failed to download image")
            else:
                print("No image available for this part")
        else:
            print(f"Part {part_number} not found")


if __name__ == "__main__":
    main()