"""
Configuration settings for Resume Adapter Pro - AI-Powered Resume Enhancement Platform.
"""

import os
from typing import Dict, List

# Application settings
APP_TITLE = "Resume Adapter Pro"
APP_ICON = "🚀"
MAX_FILE_SIZE_MB = 10

# Supported file formats
SUPPORTED_FORMATS = {
    'pdf': 'PDF Documents',
    'png': 'PNG Images', 
    'jpg': 'JPEG Images',
    'jpeg': 'JPEG Images',
    'docx': 'Word Documents'
}

# OCR settings
OCR_CONFIDENCE_THRESHOLD = 0.5
TEXT_REGION_MIN_WIDTH = 20
TEXT_REGION_MIN_HEIGHT = 8

# LaTeX settings
DEFAULT_LATEX_PACKAGES = [
    'geometry',
    'hyperref', 
    'enumitem',
    'xcolor',
    'array',
    'ifthen'
]

# OpenRouter settings
DEFAULT_MODEL = "openai/gpt-4o"
AVAILABLE_MODELS = [
    "openai/gpt-4o",
    "openai/gpt-4-turbo", 
    "anthropic/claude-3.5-sonnet",
    "google/gemini-pro-1.5",
    "meta-llama/llama-3.1-70b-instruct"
]

# Section classification keywords
SECTION_KEYWORDS = {
    'experience': ['experience', 'employment', 'work', 'career', 'professional'],
    'education': ['education', 'academic', 'degree', 'university', 'college', 'school'],
    'skills': ['skills', 'technical', 'programming', 'languages', 'technologies'],
    'projects': ['projects', 'portfolio', 'work samples'],
    'contact': ['contact', 'phone', 'email', 'address', 'linkedin']
}

# UI Color scheme
COLORS = {
    'primary': '#2c3e50',
    'secondary': '#3498db', 
    'success': '#27ae60',
    'warning': '#f39c12',
    'error': '#e74c3c',
    'light': '#ecf0f1',
    'dark': '#34495e'
}

def get_temp_dir() -> str:
    """Get temporary directory for file processing."""
    return os.environ.get('TEMP_DIR', '/tmp')

def get_openrouter_api_key() -> str:
    """Get OpenRouter API key from environment."""
    return os.environ.get('OPENROUTER_API_KEY', '')

def is_debug_mode() -> bool:
    """Check if debug mode is enabled."""
    return os.environ.get('DEBUG', 'False').lower() == 'true'


