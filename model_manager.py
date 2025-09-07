"""
Model Manager for OpenRouter API - Fetches, caches, and manages AI models
"""

import json
import os
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ModelManager:
    """Manages OpenRouter models with caching and favorites."""
    
    def __init__(self, cache_file: str = "models_cache.json", favorites_file: str = "favorite_models.json"):
        self.cache_file = cache_file
        self.favorites_file = favorites_file
        self.cache_duration = timedelta(hours=24)  # Cache for 24 hours
        
    def get_models(self, force_refresh: bool = False) -> Dict:
        """Get models with caching logic."""
        
        # Check if we should use cache
        if not force_refresh and self._is_cache_valid():
            logger.info("Using cached models")
            return self._load_from_cache()
        
        # Fetch fresh models from API
        models_data = self.fetch_models_from_api()
        
        if models_data:
            self._save_to_cache(models_data)
            return models_data
        else:
            # Fallback to cache if available
            if os.path.exists(self.cache_file):
                logger.warning("API fetch failed, using cached models")
                return self._load_from_cache()
            else:
                # Ultimate fallback to hardcoded models
                logger.warning("No cache available, using fallback models")
                return self._get_fallback_models()
    
    def fetch_models_from_api(self) -> Optional[Dict]:
        """Fetch latest models from OpenRouter API"""
        try:
            print("🔄 Fetching latest models from OpenRouter API...")
            
            # API endpoint for models
            url = "https://openrouter.ai/api/v1/models"
            headers = {
                "HTTP-Referer": "https://github.com/resume-adapter/resume-latex-generator",
                "X-Title": "Resume LaTeX Generator"
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status()
            
            data = response.json()
            models_list = data.get('data', [])
            
            if not models_list:
                print("⚠️ No models found in API response")
                return None
            
            # Convert API format to our format
            models_data = {
                "models": [],
                "last_updated": datetime.now().isoformat(),
                "total_models": len(models_list)
            }
            
            for model in models_list:
                model_id = model.get('id', '')
                name = model.get('name', model_id)
                context_length = model.get('context_length', 0)
                pricing = model.get('pricing', {})
                
                # Determine if model is free (0 cost for both prompt and completion)
                prompt_cost = float(pricing.get('prompt', '0'))
                completion_cost = float(pricing.get('completion', '0'))
                is_free = (prompt_cost == 0 and completion_cost == 0)
                
                # Include all models but mark pricing info
                # We'll let the UI handle filtering rather than excluding here
                # This ensures all available models are shown to the user
                
                # Determine model type (vision vs text)
                model_type = "text"
                name_lower = name.lower()
                id_lower = model_id.lower()
                if any(keyword in name_lower or keyword in id_lower for keyword in ['vision', 'vl', 'multimodal', 'visual']):
                    model_type = "vision"
                
                # Extract provider from model ID
                provider = "Unknown"
                if '/' in model_id:
                    provider = model_id.split('/')[0].title()
                
                # Mark recommended models
                is_recommended = self._is_recommended_model(model_id, name, is_free)
                
                # Calculate quality score
                quality_score = self._calculate_quality_score(model_id, name, context_length, is_free)
                
                model_data = {
                    "id": model_id,
                    "name": name,
                    "provider": provider,
                    "type": model_type,
                    "free": is_free,
                    "recommended": is_recommended,
                    "context": context_length,
                    "pricing": pricing,
                    "quality_score": quality_score,
                    "description": model.get('description', ''),
                    "capabilities": self._extract_capabilities(model)
                }
                
                models_data["models"].append(model_data)
            
            # Sort models by quality score and recommendation
            models_data["models"].sort(key=lambda x: (x["recommended"], x["quality_score"], x["free"]), reverse=True)
            
            print(f"✅ Fetched {len(models_data['models'])} suitable models from API")
            return models_data
            
        except Exception as e:
            print(f"❌ Failed to fetch models from API: {e}")
            logger.error(f"Model fetch error: {e}")
            return None
    
    def _is_recommended_model(self, model_id: str, name: str, is_free: bool) -> bool:
        """Determine if a model should be recommended."""
        name_lower = name.lower()
        id_lower = model_id.lower()
        
        # Recommended criteria
        recommended_patterns = [
            'gpt-4', 'gpt-3.5', 'claude', 'gemini', 'qwen', 'deepseek',
            'mistral', 'llama', 'phi', 'codestral', 'command'
        ]
        
        for pattern in recommended_patterns:
            if pattern in name_lower or pattern in id_lower:
                return True
        
        return False
    
    def _calculate_quality_score(self, model_id: str, name: str, context_length: int, is_free: bool) -> float:
        """Calculate a quality score for model ranking."""
        score = 0.0
        
        # Base score for free models
        if is_free:
            score += 10.0
        
        # Context length bonus
        if context_length >= 32000:
            score += 5.0
        elif context_length >= 16000:
            score += 3.0
        elif context_length >= 8000:
            score += 1.0
        
        # Provider reputation bonus
        name_lower = name.lower()
        id_lower = model_id.lower()
        
        if any(provider in id_lower for provider in ['openai', 'anthropic', 'google']):
            score += 8.0
        elif any(provider in id_lower for provider in ['mistralai', 'meta-llama']):
            score += 6.0
        elif any(provider in id_lower for provider in ['qwen', 'deepseek']):
            score += 4.0
        
        # Model generation bonus
        if any(gen in name_lower for gen in ['gpt-4', 'claude-3', 'gemini-1.5']):
            score += 7.0
        elif any(gen in name_lower for gen in ['gpt-3.5', 'claude-2', 'gemini-1']):
            score += 5.0
        
        return score
    
    def _extract_capabilities(self, model: Dict) -> List[str]:
        """Extract model capabilities from API data."""
        capabilities = []
        
        name = model.get('name', '').lower()
        description = model.get('description', '').lower()
        model_id = model.get('id', '').lower()
        
        # Check for various capabilities
        if any(keyword in name or keyword in description for keyword in ['code', 'programming', 'codestral']):
            capabilities.append('coding')
        
        if any(keyword in name or keyword in description for keyword in ['vision', 'visual', 'multimodal']):
            capabilities.append('vision')
        
        if any(keyword in name or keyword in description for keyword in ['chat', 'instruct', 'assistant']):
            capabilities.append('chat')
        
        if any(keyword in name or keyword in description for keyword in ['reasoning', 'analysis', 'math']):
            capabilities.append('reasoning')
        
        # Browsing/Internet support (best-effort; some providers like Perplexity do this server-side)
        if any(keyword in name or keyword in description or keyword in model_id for keyword in ['perplexity', 'sonar', 'online', 'browse', 'browsing', 'internet', 'web']):
            capabilities.append('internet')
        
        if model.get('context_length', 0) >= 32000:
            capabilities.append('long-context')
        
        return capabilities
    
    def _is_cache_valid(self) -> bool:
        """Check if the cache is still valid."""
        if not os.path.exists(self.cache_file):
            return False
        
        try:
            with open(self.cache_file, 'r') as f:
                cache_data = json.load(f)
            
            last_updated = datetime.fromisoformat(cache_data.get('last_updated', '1970-01-01'))
            return datetime.now() - last_updated < self.cache_duration
            
        except Exception as e:
            logger.error(f"Cache validation error: {e}")
            return False
    
    def _load_from_cache(self) -> Dict:
        """Load models from cache file."""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Cache loading error: {e}")
            return self._get_fallback_models()
    
    def _save_to_cache(self, models_data: Dict):
        """Save models to cache file."""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(models_data, f, indent=2)
            logger.info(f"Models cached to {self.cache_file}")
        except Exception as e:
            logger.error(f"Cache saving error: {e}")
    
    def _get_fallback_models(self) -> Dict:
        """Fallback models if API fails and no cache."""
        return {
            "models": [
                {
                    "id": "mistralai/mistral-small-3.2-24b-instruct:free",
                    "name": "Mistral Small 3.2 24B Instruct (Free)",
                    "provider": "Mistralai",
                    "type": "text",
                    "free": True,
                    "recommended": True,
                    "context": 32000,
                    "pricing": {"prompt": "0", "completion": "0"},
                    "quality_score": 15.0,
                    "description": "Fast and capable model for general tasks",
                    "capabilities": ["chat", "reasoning"]
                },
                {
                    "id": "openai/gpt-3.5-turbo",
                    "name": "GPT-3.5 Turbo",
                    "provider": "OpenAI",
                    "type": "text",
                    "free": False,
                    "recommended": True,
                    "context": 16384,
                    "pricing": {"prompt": "0.0005", "completion": "0.0015"},
                    "quality_score": 12.0,
                    "description": "Popular and reliable model",
                    "capabilities": ["chat", "coding", "reasoning"]
                }
            ],
            "last_updated": datetime.now().isoformat(),
            "total_models": 2
        }
    
    # Favorites Management
    def get_favorites(self) -> List[str]:
        """Get list of favorite model IDs."""
        try:
            if os.path.exists(self.favorites_file):
                with open(self.favorites_file, 'r') as f:
                    data = json.load(f)
                return data.get('favorites', [])
        except Exception as e:
            logger.error(f"Error loading favorites: {e}")
        return []
    
    def add_favorite(self, model_id: str):
        """Add a model to favorites."""
        favorites = self.get_favorites()
        if model_id not in favorites:
            favorites.append(model_id)
            self._save_favorites(favorites)
    
    def remove_favorite(self, model_id: str):
        """Remove a model from favorites."""
        favorites = self.get_favorites()
        if model_id in favorites:
            favorites.remove(model_id)
            self._save_favorites(favorites)
    
    def is_favorite(self, model_id: str) -> bool:
        """Check if a model is in favorites."""
        return model_id in self.get_favorites()
    
    def _save_favorites(self, favorites: List[str]):
        """Save favorites to file."""
        try:
            data = {
                'favorites': favorites,
                'last_updated': datetime.now().isoformat()
            }
            with open(self.favorites_file, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving favorites: {e}")
    
    def get_categorized_models(self) -> Dict[str, List[Dict]]:
        """Get models organized by categories."""
        models_data = self.get_models()
        models = models_data.get('models', [])
        favorites = self.get_favorites()
        
        categorized = {
            'favorites': [],
            'recommended': [],
            'free': [],
            'coding': [],
            'vision': [],
            'other': []
        }
        
        for model in models:
            # Add to favorites if applicable
            if model['id'] in favorites:
                categorized['favorites'].append(model)
            
            # Add to recommended
            if model.get('recommended', False):
                categorized['recommended'].append(model)
            
            # Add to free
            if model.get('free', False):
                categorized['free'].append(model)
            
            # Add to capability categories
            capabilities = model.get('capabilities', [])
            if 'coding' in capabilities:
                categorized['coding'].append(model)
            if 'vision' in capabilities:
                categorized['vision'].append(model)
            
            # Add to other if not in any special category
            if not (model.get('recommended') or model.get('free') or capabilities):
                categorized['other'].append(model)
        
        # Keep all categories even if empty, but mark them
        # This prevents sections from disappearing unexpectedly
        result = {}
        for k, v in categorized.items():
            result[k] = v
        return result
    
    def refresh_models(self) -> Dict:
        """Force refresh models from API."""
        return self.get_models(force_refresh=True)


