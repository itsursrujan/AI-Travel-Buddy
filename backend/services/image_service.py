# backend/services/image_service.py
import requests
from typing import Optional
from config import Config
from functools import lru_cache

class ImageService:
    """Service for fetching landmark images from Pexels API"""
    
    PEXELS_API_URL = "https://api.pexels.com/v1/search"
    
    # Cache for landmark images to avoid repeated API calls
    _landmark_cache = {}
    
    @staticmethod
    def _get_fallback_image(query: str, width: int = 400, height: int = 300) -> str:
        """Get a fallback image using Picsum Photos (no API key required)"""
        # Use Picsum Photos as a reliable fallback
        # Create deterministic seed based on query for consistency
        seed = hash(query.replace(" ", "")) % 10000
        return f"https://picsum.photos/seed/{abs(seed)}/{width}/{height}"
    
    @staticmethod
    def get_landmark_image(landmark_name: str, destination: str = None) -> str:
        """
        Fetch image URL for a landmark from Pexels with caching
        
        Args:
            landmark_name (str): Name of the landmark (e.g., "Eiffel Tower")
            destination (str, optional): Destination/city name for more specific search
        
        Returns:
            str: Image URL from Pexels or placeholder if not found
        """
        # Check cache first
        cache_key = f"{landmark_name}_{destination}".lower()
        if cache_key in ImageService._landmark_cache:
            return ImageService._landmark_cache[cache_key]
        
        # If no Pexels API key, use fallback immediately
        if not Config.PEXELS_API_KEY:
            fallback_url = ImageService._get_fallback_image(landmark_name)
            ImageService._landmark_cache[cache_key] = fallback_url
            return fallback_url
        
        try:
            # Clean up the query - remove generic terms
            search_query = landmark_name.strip()
            
            # Remove common generic prefixes and suffixes
            generic_patterns = [
                "Popular attraction in",
                "Culture and heritage in",
                "Scenic view in",
                "Historic architecture in",
                "Shopping and entertainment in",
                "Popular Attraction",
                "famous landmark",
                "cultural center",
                "scenic view",
                "historic monument",
                "shopping district",
            ]
            
            for pattern in generic_patterns:
                search_query = search_query.replace(pattern, "").strip()
            
            # Strategy 1: Try exact landmark name with destination
            if destination:
                final_query = f"{search_query} {destination}".strip()
                print(f"[Pexels] Strategy 1 - Searching for: '{final_query}'")
                image_url = ImageService._search_pexels(final_query)
                if image_url:
                    ImageService._landmark_cache[cache_key] = image_url
                    return image_url
            
            # Strategy 2: Try just the landmark name
            print(f"[Pexels] Strategy 2 - Searching for: '{search_query}'")
            image_url = ImageService._search_pexels(search_query)
            if image_url:
                ImageService._landmark_cache[cache_key] = image_url
                return image_url
            
            # Strategy 3: Try with common landmark keywords
            landmark_keywords = [
                'temple', 'fort', 'palace', 'mosque', 'church', 'monument',
                'museum', 'park', 'garden', 'lake', 'tower', 'bridge'
            ]
            
            for keyword in landmark_keywords:
                if keyword in search_query.lower():
                    # Already has a landmark keyword, don't add more
                    break
            else:
                # No landmark keyword found, try with common ones
                for keyword in landmark_keywords[:3]:  # Try first 3 keywords
                    trial_query = f"{search_query} {keyword}".strip()
                    print(f"[Pexels] Strategy 3 - Trying: '{trial_query}'")
                    image_url = ImageService._search_pexels(trial_query)
                    if image_url:
                        ImageService._landmark_cache[cache_key] = image_url
                        return image_url
            
            # Strategy 4: Try destination only
            if destination:
                print(f"[Pexels] Strategy 4 - Fallback to destination: '{destination}'")
                image_url = ImageService._search_pexels(destination)
                if image_url:
                    ImageService._landmark_cache[cache_key] = image_url
                    return image_url
        
        except Exception as e:
            print(f"[Pexels] Error fetching image for '{landmark_name}': {str(e)}")
        
        # Fallback to Picsum Photos if all strategies fail
        print(f"[Pexels] All strategies failed, using fallback for '{landmark_name}'")
        fallback_url = ImageService._get_fallback_image(landmark_name)
        ImageService._landmark_cache[cache_key] = fallback_url
        return fallback_url
    
    @staticmethod
    def _search_pexels(query: str) -> Optional[str]:
        """
        Internal method to search Pexels API with a given query
        
        Args:
            query (str): Search query
        
        Returns:
            str: Image URL if found, None otherwise
        """
        try:
            headers = {
                "Authorization": Config.PEXELS_API_KEY
            }
            params = {
                "query": query,
                "per_page": 20,  # Get more results to find better matches
                "orientation": "landscape"
            }
            
            response = requests.get(
                ImageService.PEXELS_API_URL,
                headers=headers,
                params=params,
                timeout=8
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get("photos") and len(data["photos"]) > 0:
                    photo = data["photos"][0]
                    image_url = (
                        photo.get("src", {}).get("large2x") or
                        photo.get("src", {}).get("large") or
                        photo.get("src", {}).get("medium") or
                        photo.get("src", {}).get("original")
                    )
                    
                    if image_url:
                        print(f"[Pexels] Found: {image_url}")
                        return image_url
            
            elif response.status_code == 429:
                print(f"[Pexels] Rate limited - too many requests")
                return None
            else:
                print(f"[Pexels] API error {response.status_code}: {response.text}")
                return None
        
        except requests.exceptions.Timeout:
            print(f"[Pexels] Request timeout for query: '{query}'")
            return None
        except Exception as e:
            print(f"[Pexels] Search error for '{query}': {str(e)}")
            return None
    
    @staticmethod
    def get_destination_image(destination: str) -> str:
        """
        Fetch image URL for a destination from Pexels with caching
        
        Args:
            destination (str): Name of the destination (e.g., "Paris")
        
        Returns:
            str: Image URL from Pexels or placeholder if not found
        """
        # Check cache first
        cache_key = f"dest_{destination}".lower()
        if cache_key in ImageService._landmark_cache:
            return ImageService._landmark_cache[cache_key]
        
        # If no Pexels API key, use fallback immediately
        if not Config.PEXELS_API_KEY:
            fallback_url = ImageService._get_fallback_image(destination)
            ImageService._landmark_cache[cache_key] = fallback_url
            return fallback_url
        
        try:
            # Try to fetch from Pexels API for destination
            print(f"[Pexels] Searching destination image for: '{destination}'")
            image_url = ImageService._search_pexels(destination)
            
            if image_url:
                ImageService._landmark_cache[cache_key] = image_url
                return image_url
        
        except Exception as e:
            print(f"[Pexels] Error fetching destination image for '{destination}': {str(e)}")
        
        # Fallback to Picsum Photos if API fails or no results
        print(f"[Pexels] Destination image not found, using fallback for '{destination}'")
        fallback_url = ImageService._get_fallback_image(destination)
        ImageService._landmark_cache[cache_key] = fallback_url
        return fallback_url
