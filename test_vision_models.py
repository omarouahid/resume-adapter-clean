#!/usr/bin/env python3
"""
Test script to debug vision model fetching from OpenRouter API
"""

import os
from openrouter_client import OpenRouterClient

def test_vision_models():
    """Test vision model fetching and filtering"""
    
    # You'll need to set your API key here
    api_key = os.getenv('OPENROUTER_API_KEY')
    if not api_key:
        print("❌ Please set OPENROUTER_API_KEY environment variable")
        return
    
    print("🔍 Testing OpenRouter vision model fetching...")
    
    # Create client
    client = OpenRouterClient(api_key, "anthropic/claude-3-haiku:beta")
    
    try:
        # Test 1: Get all available models
        print("\n📋 Step 1: Fetching all available models...")
        all_models = client.get_available_models()
        print(f"✅ Retrieved {len(all_models)} total models")
        
        # Test 2: Get vision models
        print("\n👁️ Step 2: Fetching vision models...")
        vision_models = client.get_available_vision_models()
        print(f"✅ Retrieved {len(vision_models)} vision models")
        
        if not vision_models:
            print("❌ No vision models found!")
            return
        
        # Test 3: Show all vision models
        print("\n📊 Step 3: Vision models found:")
        for model_id, info in vision_models.items():
            name = info.get('name', model_id)
            provider = info.get('provider', 'Unknown')
            is_free = info.get('is_free', False)
            cost = info.get('cost_per_1k_tokens', 0)
            recommended = info.get('recommended', False)
            print(f"  {model_id}: {name} ({provider}) - {'🆓' if is_free else f'💰{cost}'} {'⭐' if recommended else ''}")
        
        # Test 4: Filter for free models
        print("\n🆓 Step 4: Testing free model filtering...")
        free_models = {k: v for k, v in vision_models.items() if v.get('is_free', False)}
        print(f"✅ Found {len(free_models)} free vision models:")
        for model_id, info in free_models.items():
            name = info.get('name', model_id)
            print(f"  {model_id}: {name}")
        
        # Test 5: Test recommended model selection
        print("\n⭐ Step 5: Testing recommended model selection...")
        recommended_model = client.get_recommended_vision_model(prefer_free=True)
        print(f"✅ Recommended free model: {recommended_model}")
        
        # Test 6: Simulate the filtering logic from app.py
        print("\n🔄 Step 6: Simulating app.py filtering logic...")
        
        # Free models only = True
        show_free_vision_only = True
        if show_free_vision_only:
            filtered_vision_models = {k: v for k, v in vision_models.items() if v.get('is_free', False)}
            print(f"  Free filter enabled: {len(filtered_vision_models)} models")
            if not filtered_vision_models:
                print("  ⚠️ No free models found, would use all models as fallback")
                filtered_vision_models = vision_models
        else:
            filtered_vision_models = vision_models.copy()
            print(f"  Free filter disabled: {len(filtered_vision_models)} models")
        
        # Sorting
        if filtered_vision_models:
            sorted_vision_models = sorted(
                filtered_vision_models.items(), 
                key=lambda x: (
                    not x[1].get('recommended', False), 
                    x[1].get('cost_per_1k_tokens', 0) if not x[1].get('is_free', False) else -1,
                    x[1].get('name', '')
                )
            )
            print(f"  Sorted: {len(sorted_vision_models)} models")
            
            # Show top 3 models
            print("  Top 3 models after sorting:")
            for i, (model_id, info) in enumerate(sorted_vision_models[:3]):
                name = info.get('name', model_id)
                print(f"    {i+1}. {model_id}: {name}")
        else:
            print("  ❌ No models after filtering - this would cause the disappearing issue!")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_vision_models()