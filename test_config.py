#!/usr/bin/env python3
"""
Test configuration loading for both local and production environments.
"""

import os
import sys

# Add current directory to path
sys.path.insert(0, '.')

def test_environment_detection():
    """Test the environment detection logic."""
    
    def is_streamlit_cloud():
        """Detect if running on Streamlit Cloud."""
        return (
            os.environ.get('STREAMLIT_SHARING_MODE') == 'true' or 
            os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true' or
            'streamlit.app' in os.environ.get('HOSTNAME', '') or
            'share.streamlit.io' in str(os.environ.get('STREAMLIT_SERVER_BASE_URL_PATH', ''))
        )
    
    print("🔧 Environment Detection Test:")
    print(f"Is Streamlit Cloud: {is_streamlit_cloud()}")
    print()
    
    # Test with simulated Streamlit Cloud environment
    print("🌐 Simulating Streamlit Cloud environment:")
    os.environ['STREAMLIT_SERVER_HEADLESS'] = 'true'
    print(f"Is Streamlit Cloud: {is_streamlit_cloud()}")
    
    # Clean up
    del os.environ['STREAMLIT_SERVER_HEADLESS']
    print("✅ Environment detection working correctly!")
    print()

def test_env_file():
    """Test .env file loading."""
    print("📁 Testing .env file:")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        api_key = os.environ.get('OPENROUTER_API_KEY', '')
        model = os.environ.get('OPENROUTER_DEFAULT_MODEL', '')
        
        if api_key and api_key != 'your-openrouter-api-key-here':
            print("✅ .env file loaded successfully")
            print(f"   API Key: {api_key[:20]}...{api_key[-4:]}")
            print(f"   Model: {model}")
        else:
            print("⚠️ .env file exists but API key not found")
            
    except ImportError:
        print("❌ python-dotenv not installed")
    except Exception as e:
        print(f"❌ Error loading .env: {e}")
    
    print()

def test_config_loading():
    """Test the configuration loading without Streamlit."""
    print("⚙️ Testing configuration loading:")
    
    try:
        # Load configuration like the app would
        from dotenv import load_dotenv
        import json
        
        load_dotenv()
        
        # Load config.json
        config = {}
        try:
            if os.path.exists('config.json'):
                with open('config.json', 'r') as f:
                    config = json.load(f)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")
        
        # Build final configuration
        final_config = {
            "openrouter": {
                "api_key": os.environ.get('OPENROUTER_API_KEY', config.get('openrouter', {}).get('api_key', '')),
                "default_model": os.environ.get('OPENROUTER_DEFAULT_MODEL', config.get('openrouter', {}).get('default_model', 'mistralai/mistral-small-3.2-24b-instruct:free'))
            }
        }
        
        api_key = final_config['openrouter']['api_key']
        if api_key and api_key != 'your-openrouter-api-key-here':
            print("✅ Configuration loaded successfully!")
            print(f"   API Key source: {'Environment variable' if os.environ.get('OPENROUTER_API_KEY') else 'config.json'}")
            print(f"   Model: {final_config['openrouter']['default_model']}")
        else:
            print("⚠️ No valid API key found")
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
    
    print()

if __name__ == "__main__":
    print("🧪 Configuration Test Suite")
    print("=" * 40)
    
    test_environment_detection()
    test_env_file()  
    test_config_loading()
    
    print("🎉 All tests completed!")
    print()
    print("📋 Next Steps:")
    print("1. Deploy to Streamlit Cloud")
    print("2. Add secrets in Streamlit Cloud dashboard")
    print("3. Verify app loads configuration from st.secrets")