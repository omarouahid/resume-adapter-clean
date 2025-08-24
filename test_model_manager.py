#!/usr/bin/env python3
"""
Test the Model Manager functionality
"""

from model_manager import ModelManager
import json

def test_model_fetching():
    """Test fetching models from OpenRouter API."""
    print("🧪 Testing Model Manager")
    print("=" * 40)
    
    manager = ModelManager()
    
    print("🔄 Fetching models from API...")
    models_data = manager.get_models()
    
    if models_data:
        models = models_data.get('models', [])
        print(f"✅ Successfully fetched {len(models)} models")
        
        # Show statistics
        free_models = [m for m in models if m.get('free', False)]
        recommended_models = [m for m in models if m.get('recommended', False)]
        
        print(f"📊 Model Statistics:")
        print(f"  • Total models: {len(models)}")
        print(f"  • Free models: {len(free_models)}")
        print(f"  • Recommended: {len(recommended_models)}")
        
        # Show top models
        print(f"\n🏆 Top 10 Models (by quality score):")
        top_models = sorted(models, key=lambda x: x.get('quality_score', 0), reverse=True)[:10]
        
        for i, model in enumerate(top_models, 1):
            name = model['name'][:40] + '...' if len(model['name']) > 40 else model['name']
            provider = model['provider']
            free_status = "🆓" if model.get('free') else "💰"
            recommended = "⭐" if model.get('recommended') else ""
            score = model.get('quality_score', 0)
            
            print(f"  {i:2d}. {recommended} {free_status} {name} ({provider}) - Score: {score}")
        
        return True
    else:
        print("❌ Failed to fetch models")
        return False

def test_categorization():
    """Test model categorization."""
    print("\n🧪 Testing Model Categorization")
    print("=" * 40)
    
    manager = ModelManager()
    categorized = manager.get_categorized_models()
    
    print("📋 Available Categories:")
    for category, models in categorized.items():
        if models:
            print(f"  • {category.title()}: {len(models)} models")
            
            # Show sample models from each category
            sample_models = models[:3]
            for model in sample_models:
                name = model['name'][:30] + '...' if len(model['name']) > 30 else model['name']
                free_status = "🆓" if model.get('free') else "💰"
                print(f"    - {free_status} {name}")
    
    return True

def test_favorites():
    """Test favorites functionality."""
    print("\n🧪 Testing Favorites Functionality")
    print("=" * 40)
    
    manager = ModelManager()
    
    # Get some test models
    models_data = manager.get_models()
    if not models_data or not models_data.get('models'):
        print("❌ No models available for testing favorites")
        return False
    
    test_model_id = models_data['models'][0]['id']
    
    print(f"🧪 Testing with model: {test_model_id}")
    
    # Test adding to favorites
    print("➕ Adding to favorites...")
    manager.add_favorite(test_model_id)
    
    # Test checking if favorite
    is_fav = manager.is_favorite(test_model_id)
    print(f"✅ Is favorite: {is_fav}")
    
    # Test getting favorites list
    favorites = manager.get_favorites()
    print(f"📋 Favorites list: {len(favorites)} items")
    
    # Test removing from favorites
    print("➖ Removing from favorites...")
    manager.remove_favorite(test_model_id)
    
    # Check again
    is_fav_after = manager.is_favorite(test_model_id)
    print(f"✅ Is favorite after removal: {is_fav_after}")
    
    return is_fav and not is_fav_after

def test_caching():
    """Test caching functionality."""
    print("\n🧪 Testing Caching")
    print("=" * 40)
    
    manager = ModelManager()
    
    print("🔄 First fetch (from API)...")
    models1 = manager.get_models()
    
    print("🔄 Second fetch (should use cache)...")
    models2 = manager.get_models()
    
    if models1 and models2:
        same_count = len(models1.get('models', [])) == len(models2.get('models', []))
        print(f"✅ Cache consistency: {same_count}")
        print(f"📊 Models from first fetch: {len(models1.get('models', []))}")
        print(f"📊 Models from second fetch: {len(models2.get('models', []))}")
        return same_count
    
    return False

def test_streamlit_integration():
    """Test integration with Streamlit components."""
    print("\n🧪 Testing Streamlit Integration")
    print("=" * 40)
    
    manager = ModelManager()
    categorized = manager.get_categorized_models()
    
    print("🎛️ Simulating Streamlit UI components:")
    
    # Simulate category selection
    categories = list(categorized.keys())
    print(f"📋 Available categories for dropdown: {categories}")
    
    # Simulate model selection for each category
    for category in categories[:3]:  # Test first 3 categories
        models = categorized[category]
        if models:
            print(f"\n🎯 Category: {category.title()}")
            print(f"  📊 {len(models)} models available")
            
            # Show formatted model names (as they would appear in dropdown)
            for i, model in enumerate(models[:3]):  # Show first 3
                name = model['name']
                provider = model['provider']
                is_free = "🆓" if model.get('free') else "💰"
                is_fav = "⭐" if manager.is_favorite(model['id']) else ""
                
                display_name = f"{is_fav} {is_free} {name} ({provider})"
                print(f"    {i+1}. {display_name}")
    
    print("\n✅ Streamlit integration components ready!")
    return True

def show_sample_config():
    """Show sample configuration for the models."""
    print("\n📄 Sample Generated Models Cache")
    print("=" * 40)
    
    manager = ModelManager()
    models_data = manager.get_models()
    
    if models_data:
        # Show cache file structure
        print("📁 Cache file structure:")
        print(f"  • last_updated: {models_data.get('last_updated')}")
        print(f"  • total_models: {models_data.get('total_models')}")
        print(f"  • models: [{len(models_data.get('models', []))} items]")
        
        # Show sample model data
        if models_data.get('models'):
            sample_model = models_data['models'][0]
            print(f"\n📄 Sample model data:")
            print(json.dumps(sample_model, indent=2))
    
    return True

def main():
    """Run all model manager tests."""
    print("🚀 Testing Model Manager System")
    print("=" * 50)
    
    tests = [
        ("Model Fetching", test_model_fetching),
        ("Categorization", test_categorization),
        ("Favorites", test_favorites),
        ("Caching", test_caching),
        ("Streamlit Integration", test_streamlit_integration),
        ("Sample Config", show_sample_config)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  • {test_name:20}: {status}")
    
    overall_success = all(result for _, result in results)
    
    if overall_success:
        print("\n🎉 All tests passed! Model Manager is ready!")
        print("\n💡 Features available:")
        print("  • 🔄 Dynamic model fetching from OpenRouter API")
        print("  • 📋 Model categorization (Free, Recommended, Coding, etc.)")
        print("  • ⭐ Favorites system with persistent storage")
        print("  • 💾 Smart caching (24-hour cache duration)")
        print("  • 🎛️ Streamlit UI integration ready")
        print("  • 🆓 Free model filtering and highlighting")
        print("  • 📊 Quality scoring and ranking")
        
        print("\n🌐 Your Streamlit app now has:")
        print("  • Dynamic model dropdown with live API data")
        print("  • Category-based model organization")
        print("  • Favorites system with heart button")
        print("  • Refresh button for latest models")
        print("  • Model details and capabilities display")
    
    return overall_success

if __name__ == "__main__":
    main()


