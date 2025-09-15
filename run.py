#!/usr/bin/env python3
"""
Launch script for Resume Adapter Pro
"""

import subprocess
import sys
import os
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed."""
    try:
        import streamlit
        import cv2
        import numpy
        import fitz
        import docx
        import PIL
        print("Core dependencies found")
        return True
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Please run: pip install -r requirements.txt")
        return False

def check_optional_dependencies():
    """Check optional dependencies and warn if missing."""
    optional_deps = {
        'easyocr': 'OCR functionality will be limited',
        'transformers': 'TrOCR functionality will be unavailable'
    }
    
    for dep, warning in optional_deps.items():
        try:
            __import__(dep)
            print(f"{dep} found")
        except ImportError:
            print(f"WARNING: {dep} not found - {warning}")

def main():
    """Main function to launch the Streamlit app."""
    print("Starting Resume Adapter Pro...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not Path("app.py").exists():
        print("ERROR: app.py not found. Please run this script from the project directory.")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    check_optional_dependencies()
    
    print("=" * 50)
    print("Launching Streamlit application...")
    print("The app will open in your default browser")
    print("Remember to add your OpenRouter API key in the sidebar")
    print("=" * 50)
    
    # Launch Streamlit
    try:
        # Ensure UTF-8 output to avoid Windows charmap errors with Unicode
        env = os.environ.copy()
        env.setdefault("PYTHONUTF8", "1")
        env.setdefault("PYTHONIOENCODING", "utf-8")

        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.headless", "false",
            "--server.port", "8501",
            "--server.enableCORS", "false"
        ], env=env)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except Exception as e:
        print(f"ERROR: Error launching application: {e}")

if __name__ == "__main__":
    main()


