#!/usr/bin/env python3
"""
Quick script to restart the Streamlit app with the improved section detection.
"""

import subprocess
import sys
import time
import requests

def check_app_running():
    """Check if the app is already running."""
    try:
        response = requests.get("http://localhost:8501", timeout=2)
        return response.status_code == 200
    except:
        return False

def main():
    print("🔄 Checking Streamlit app status...")
    
    if check_app_running():
        print("✅ Streamlit app is already running at http://localhost:8501")
        print("🔄 The improved section detection is now active!")
        print("\n💡 To test the improvements:")
        print("  1. Go to http://localhost:8501")
        print("  2. Upload your resume (tests/data engineer eng.pdf)")
        print("  3. You should now see 6 sections instead of 1!")
        print("  4. Use 'Improve LaTeX Code' for even better results")
    else:
        print("🚀 Starting Streamlit app with improved section detection...")
        
        try:
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", "app.py",
                "--server.headless", "false",
                "--server.port", "8501"
            ])
        except KeyboardInterrupt:
            print("\n👋 App stopped")

if __name__ == "__main__":
    main()


