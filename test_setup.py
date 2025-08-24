#!/usr/bin/env python3
"""
Test script to verify the setup is working correctly.
"""

import sys
import importlib
from pathlib import Path

def test_imports():
    """Test that all required modules can be imported."""
    print("🔍 Testing imports...")
    
    # Core modules
    core_modules = [
        'streamlit',
        'cv2',
        'numpy', 
        'fitz',
        'docx',
        'PIL',
        'requests'
    ]
    
    for module in core_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module}")
        except ImportError:
            print(f"❌ {module} - REQUIRED")
            return False
    
    # Optional modules
    optional_modules = [
        'easyocr',
        'transformers'
    ]
    
    for module in optional_modules:
        try:
            importlib.import_module(module)
            print(f"✅ {module} (optional)")
        except ImportError:
            print(f"⚠️  {module} (optional) - Enhanced features unavailable")
    
    return True

def test_project_files():
    """Test that all project files are present."""
    print("\n📁 Testing project files...")
    
    required_files = [
        'app.py',
        'resume_analyzer.py', 
        'openrouter_client.py',
        'config.py',
        'requirements.txt',
        'README.md'
    ]
    
    for file in required_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            return False
    
    return True

def test_local_imports():
    """Test that our local modules can be imported."""
    print("\n🔧 Testing local modules...")
    
    try:
        from resume_analyzer import ResumeAnalyzer
        print("✅ ResumeAnalyzer")
    except ImportError as e:
        print(f"❌ ResumeAnalyzer - {e}")
        return False
    
    try:
        from openrouter_client import OpenRouterClient
        print("✅ OpenRouterClient")
    except ImportError as e:
        print(f"❌ OpenRouterClient - {e}")
        return False
    
    try:
        import config
        print("✅ config")
    except ImportError as e:
        print(f"❌ config - {e}")
        return False
    
    return True

def test_functionality():
    """Test basic functionality."""
    print("\n🧪 Testing basic functionality...")
    
    try:
        from resume_analyzer import ResumeAnalyzer
        analyzer = ResumeAnalyzer()
        print("✅ ResumeAnalyzer instantiation")
    except Exception as e:
        print(f"❌ ResumeAnalyzer instantiation - {e}")
        return False
    
    try:
        from openrouter_client import OpenRouterClient
        # Don't actually make API call without key
        print("✅ OpenRouterClient class available")
    except Exception as e:
        print(f"❌ OpenRouterClient - {e}")
        return False
    
    return True

def main():
    """Run all tests."""
    print("🧪 Resume to LaTeX Generator - Setup Test")
    print("=" * 50)
    
    all_passed = True
    
    # Run tests
    all_passed &= test_imports()
    all_passed &= test_project_files()
    all_passed &= test_local_imports()
    all_passed &= test_functionality()
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("🎉 All tests passed! You can run the application with:")
        print("   python run.py")
        print("   or")
        print("   streamlit run app.py")
        print("\n💡 Don't forget to get your OpenRouter API key from:")
        print("   https://openrouter.ai")
    else:
        print("❌ Some tests failed. Please check the requirements.")
        print("💡 Try running: pip install -r requirements.txt")
        sys.exit(1)

if __name__ == "__main__":
    main()


