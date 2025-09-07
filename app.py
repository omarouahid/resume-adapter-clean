"""
Resume to LaTeX Generator - Streamlit Application
A beautiful platform for converting resumes to LaTeX with AI assistance.
"""

import streamlit as st
import tempfile
import os
import zipfile
import json
import re
from pathlib import Path
from typing import Dict, Tuple, Optional, Any
import logging

# Configure page
st.set_page_config(
    page_title="Resume to LaTeX Generator",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import our custom modules
from resume_analyzer import ResumeAnalyzer
from openrouter_client import OpenRouterClient
from pdf_compiler import PreviewService
from job_adaptation_service import JobAdaptationService, ResumeImprovementService
from enhanced_latex_generator import EnhancedLaTeXGenerator
from model_manager import ModelManager
from resume_critique_service import ResumeCritiqueService
from advanced_resume_parser import AdvancedResumeParser
from smart_latex_generator import SmartLaTeXGenerator
from resume_enhancement_comparison import ResumeEnhancementComparison, display_enhancement_comparison_page
from rate_limiter import IPRateLimiter, RateLimitExceeded
from html_resume_generator import HTMLResumeGenerator
from html_preview_component import HTMLResumePreview, html_preview
from ats_analyzer import ATSAnalyzer, display_ats_score_dashboard
from real_time_editor import RealTimeEditor, real_time_editor
from template_matcher import TemplateMatchingSystem
from image_converter import image_converter
from professional_templates import professional_templates
from freelancer_templates import freelancer_templates
from engineering_templates import engineering_templates
from cover_letter_service import CoverLetterService
from web_research import CompanyResearchService

# Configure logging with file output
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = "logs"
if not os.path.exists(logs_dir):
    os.makedirs(logs_dir)

# Setup logging configuration
log_filename = os.path.join(logs_dir, f"resume_adapter_{datetime.now().strftime('%Y%m%d')}.log")

# Clear any existing handlers to avoid conflicts
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename, encoding='utf-8', mode='a'),
        logging.StreamHandler()  # Still show critical errors in console
    ]
)

# Set specific loggers to different levels
logging.getLogger('streamlit').setLevel(logging.WARNING)
logging.getLogger('urllib3').setLevel(logging.WARNING)
logging.getLogger('requests').setLevel(logging.WARNING)

logger = logging.getLogger(__name__)
logger.info(f"🚀 Resume Adapter started - Logging to: {log_filename}")
logger.info(f"📅 App initialized at {datetime.now()}")
logger.debug("🔧 Logging system configured and operational")

def sanitize_data(data):
    """
    Clean up data that has excessive escaping or corruption from multiple updates.
    
    Args:
        data: Can be string, list, dict, or any nested structure
        
    Returns:
        Cleaned data with proper formatting
    """
    if isinstance(data, str):
        # Fix excessive escaping in strings
        cleaned = data
        # Remove excessive backslashes
        while '\\\\' in cleaned:
            cleaned = cleaned.replace('\\\\', '\\')
        # Remove excessive quotes
        while '\\"' in cleaned:
            cleaned = cleaned.replace('\\"', '"')
        # Remove broken array markers
        cleaned = re.sub(r'\[+\'+\[+', '[', cleaned)
        cleaned = re.sub(r'\]+\'+\]+', ']', cleaned)
        # Remove excessive brackets and quotes at start/end
        cleaned = re.sub(r'^[\["\\\s]+', '', cleaned)
        cleaned = re.sub(r'[\]"\\\s]+$', '', cleaned)
        return cleaned
        
    elif isinstance(data, list):
        cleaned_list = []
        for item in data:
            cleaned_item = sanitize_data(item)
            # Skip empty or corrupted items
            if cleaned_item and str(cleaned_item).strip():
                cleaned_list.append(cleaned_item)
        return cleaned_list
        
    elif isinstance(data, dict):
        cleaned_dict = {}
        for key, value in data.items():
            cleaned_key = sanitize_data(key) if isinstance(key, str) else key
            cleaned_value = sanitize_data(value)
            cleaned_dict[cleaned_key] = cleaned_value
        return cleaned_dict
        
    else:
        return data

# Custom CSS for beautiful styling
def load_css():
    st.markdown("""
    <style>
    .main {
        padding-top: 1rem;
    }
    
    .stAlert {
        margin-top: 1rem;
    }
    
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
        background-color: #fafafa;
    }
    
    /* Hireitpeople-inspired color palette */
    :root {
        --primary-blue: #2563eb;
        --light-blue: #3b82f6;
        --dark-blue: #1e40af;
        --gray-50: #f9fafb;
        --gray-100: #f3f4f6;
        --gray-200: #e5e7eb;
        --gray-600: #4b5563;
        --gray-800: #1f2937;
        --success-green: #10b981;
        --success-green-dark: #059669;
    }

    .feature-card {
        background: linear-gradient(135deg, var(--primary-blue) 0%, var(--dark-blue) 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(37, 99, 235, 0.25);
    }
    
    .latex-code {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        border-radius: 5px;
        padding: 1rem;
        font-family: 'Courier New', monospace;
        max-height: 400px;
        overflow-y: auto;
    }
    
    .success-message {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .error-message {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    .stats-card {
        background-color: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .section-header {
        color: var(--gray-800);
        border-bottom: 2px solid var(--primary-blue);
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    
    /* Modern preview containers inspired by hireitpeople.com */
    .preview-container {
        background: white;
        border: 2px solid var(--gray-200);
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .template-preview {
        border: 2px dashed var(--primary-blue);
        background: linear-gradient(135deg, rgba(37, 99, 235, 0.03) 0%, rgba(59, 130, 246, 0.03) 100%);
        position: relative;
    }
    
    .template-preview::before {
        content: "Template Matching Preview";
        position: absolute;
        top: -10px;
        left: 20px;
        background: var(--primary-blue);
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .final-preview {
        border: 2px solid var(--primary-blue);
        background: white;
        position: relative;
    }
    
    .final-preview::before {
        content: "Final Resume Preview";
        position: absolute;
        top: -10px;
        left: 20px;
        background: var(--success-green);
        color: white;
        padding: 4px 12px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Professional action buttons */
    .apply-button {
        background: var(--success-green) !important;
        border: none !important;
        border-radius: 8px !important;
        color: white !important;
        padding: 0.75rem 2rem !important;
        font-weight: 600 !important;
        margin: 1rem 0 !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .apply-button:hover {
        background: var(--success-green-dark) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3) !important;
    }
    
    /* Enhanced stats cards */
    .stats-card {
        background: white !important;
        padding: 1.5rem !important;
        border-radius: 12px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1) !important;
        border: 1px solid var(--gray-200) !important;
        transition: all 0.3s ease !important;
    }
    
    .stats-card:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.15) !important;
        transform: translateY(-2px) !important;
    }
    
    /* Modern tabs styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 4px !important;
        background-color: var(--gray-100) !important;
        border-radius: 10px !important;
        padding: 6px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 48px !important;
        padding: 12px 24px !important;
        background-color: transparent !important;
        border-radius: 8px !important;
        color: var(--gray-600) !important;
        font-weight: 500 !important;
        border: none !important;
        transition: all 0.3s ease !important;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: var(--primary-blue) !important;
        color: white !important;
        box-shadow: 0 2px 4px rgba(37, 99, 235, 0.2) !important;
    }
    </style>
    """, unsafe_allow_html=True)

def is_streamlit_cloud():
    """Detect if running on Streamlit Cloud."""
    return (
        os.environ.get('STREAMLIT_SHARING_MODE') == 'true' or 
        os.environ.get('STREAMLIT_SERVER_HEADLESS') == 'true' or
        'streamlit.app' in os.environ.get('HOSTNAME', '') or
        'share.streamlit.io' in str(os.environ.get('STREAMLIT_SERVER_BASE_URL_PATH', ''))
    )

def load_config():
    """Load configuration from Streamlit secrets, environment variables, or config.json."""
    import os
    from dotenv import load_dotenv
    
    # Check if we're running on Streamlit Cloud
    is_production = is_streamlit_cloud()
    
    if is_production:
        # Use Streamlit secrets in production
        try:
            config = {
                "openrouter": {
                    "api_key": st.secrets.get("OPENROUTER_API_KEY", ""),
                    "default_model": st.secrets.get("OPENROUTER_DEFAULT_MODEL", "mistralai/mistral-small-3.2-24b-instruct:free")
                },
                "rate_limiting": {
                    "enabled": st.secrets.get("RATE_LIMIT_ENABLED", "true").lower() == 'true',
                    "max_requests": int(st.secrets.get("RATE_LIMIT_MAX_REQUESTS", 30)),
                    "time_window": int(st.secrets.get("RATE_LIMIT_TIME_WINDOW", 60)),
                    "admin_ips": st.secrets.get("RATE_LIMIT_ADMIN_IPS", "").split(',') if st.secrets.get("RATE_LIMIT_ADMIN_IPS") else []
                },
                "ui": {
                    "default_port": int(st.secrets.get("DEFAULT_PORT", 8501)),
                    "auto_open_browser": st.secrets.get("AUTO_OPEN_BROWSER", "true").lower() == 'true'
                },
                "processing": {
                    "ocr_confidence_threshold": float(st.secrets.get("OCR_CONFIDENCE_THRESHOLD", 0.5)),
                    "max_file_size_mb": int(st.secrets.get("MAX_FILE_SIZE_MB", 10))
                }
            }
            logger.info("✅ Configuration loaded from Streamlit secrets")
            return config
        except Exception as e:
            logger.warning(f"Could not load Streamlit secrets: {e}")
    else:
        # Load .env file for local development
        load_dotenv()
        logger.info("🔧 Running locally - loading from .env and config.json")
    
    # Fallback: Load from config.json and environment variables
    config = {}
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
    except Exception as e:
        logger.warning(f"Could not load config.json: {e}")
    
    # Override with environment variables (higher priority)
    env_config = {
        "openrouter": {
            "api_key": os.environ.get('OPENROUTER_API_KEY', config.get('openrouter', {}).get('api_key', '')),
            "default_model": os.environ.get('OPENROUTER_DEFAULT_MODEL', config.get('openrouter', {}).get('default_model', 'mistralai/mistral-small-3.2-24b-instruct:free'))
        },
        "rate_limiting": {
            "enabled": os.environ.get('RATE_LIMIT_ENABLED', str(config.get('rate_limiting', {}).get('enabled', True))).lower() == 'true',
            "max_requests": int(os.environ.get('RATE_LIMIT_MAX_REQUESTS', config.get('rate_limiting', {}).get('max_requests', 30))),
            "time_window": int(os.environ.get('RATE_LIMIT_TIME_WINDOW', config.get('rate_limiting', {}).get('time_window', 60))),
            "admin_ips": os.environ.get('RATE_LIMIT_ADMIN_IPS', ','.join(config.get('rate_limiting', {}).get('admin_ips', []))).split(',') if os.environ.get('RATE_LIMIT_ADMIN_IPS') else []
        },
        "ui": {
            "default_port": int(os.environ.get('DEFAULT_PORT', config.get('ui', {}).get('default_port', 8501))),
            "auto_open_browser": os.environ.get('AUTO_OPEN_BROWSER', str(config.get('ui', {}).get('auto_open_browser', True))).lower() == 'true'
        },
        "processing": {
            "ocr_confidence_threshold": float(os.environ.get('OCR_CONFIDENCE_THRESHOLD', config.get('processing', {}).get('ocr_confidence_threshold', 0.5))),
            "max_file_size_mb": int(os.environ.get('MAX_FILE_SIZE_MB', config.get('processing', {}).get('max_file_size_mb', 10)))
        }
    }
    
    return env_config

def initialize_session_state():
    """Initialize session state variables."""
    if 'analysis_complete' not in st.session_state:
        st.session_state.analysis_complete = False
    if 'tex_content' not in st.session_state:
        st.session_state.tex_content = ""
    if 'cls_content' not in st.session_state:
        st.session_state.cls_content = ""
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = {}
    if 'openrouter_client' not in st.session_state:
        st.session_state.openrouter_client = None
    if 'uploaded_file_name' not in st.session_state:
        st.session_state.uploaded_file_name = ""
    if 'config' not in st.session_state:
        st.session_state.config = load_config()
    if 'preview_service' not in st.session_state:
        st.session_state.preview_service = PreviewService()
    if 'enhanced_generator' not in st.session_state:
        st.session_state.enhanced_generator = EnhancedLaTeXGenerator()
    if 'html_generator' not in st.session_state:
        # Initialize HTML generator with OpenRouter client if available
        openrouter_client = getattr(st.session_state, 'openrouter_client', None)
        logger.info(f"🏭 Initializing HTML generator with OpenRouter client: {bool(openrouter_client)}")
        st.session_state.html_generator = HTMLResumeGenerator(openrouter_client)
    if 'html_preview_component' not in st.session_state:
        st.session_state.html_preview_component = HTMLResumePreview()
    if 'ats_analyzer' not in st.session_state:
        st.session_state.ats_analyzer = ATSAnalyzer()
    if 'real_time_editor' not in st.session_state:
        st.session_state.real_time_editor = RealTimeEditor()
    if 'model_manager' not in st.session_state:
        st.session_state.model_manager = ModelManager()
    if 'critique_service' not in st.session_state:
        st.session_state.critique_service = ResumeCritiqueService()
    if 'advanced_parser' not in st.session_state:
        st.session_state.advanced_parser = AdvancedResumeParser()
    if 'parsed_resume' not in st.session_state:
        st.session_state.parsed_resume = None
    if 'parsed_resume_data' not in st.session_state:
        st.session_state.parsed_resume_data = None
    if 'smart_latex_generator' not in st.session_state:
        st.session_state.smart_latex_generator = SmartLaTeXGenerator()
    if 'enhancement_comparison' not in st.session_state:
        st.session_state.enhancement_comparison = None
    if 'show_comparison_page' not in st.session_state:
        st.session_state.show_comparison_page = False
    if 'original_parsed_resume' not in st.session_state:
        st.session_state.original_parsed_resume = None
    if 'openrouter_api_key' not in st.session_state:
        st.session_state.openrouter_api_key = ""
    if 'cover_letter_service' not in st.session_state:
        st.session_state.cover_letter_service = CoverLetterService()
    if 'research_service' not in st.session_state:
        st.session_state.research_service = CompanyResearchService()
    if 'company_research' not in st.session_state:
        st.session_state.company_research = None
    if 'cover_letter_text' not in st.session_state:
        st.session_state.cover_letter_text = ""
    # Wire OpenRouter client into auxiliary services if available
    try:
        if st.session_state.openrouter_client:
            if 'cover_letter_service' in st.session_state and st.session_state.cover_letter_service:
                st.session_state.cover_letter_service.set_client(st.session_state.openrouter_client)
            if 'research_service' in st.session_state and st.session_state.research_service:
                st.session_state.research_service.set_client(st.session_state.openrouter_client)
    except Exception:
        pass

def create_header():
    """Create the application header."""
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="color: #2c3e50; margin-bottom: 0.5rem;">📄 Resume to LaTeX Generator</h1>
        <p style="color: #7f8c8d; font-size: 1.2rem;">Transform your resume into professional LaTeX code with AI assistance</p>
    </div>
    """, unsafe_allow_html=True)

def create_sidebar():
    """Create the sidebar with settings and information."""
    with st.sidebar:
        st.markdown("## ⚙️ Settings")
        
        # OpenRouter API Key
        config_api_key = st.session_state.config.get('openrouter', {}).get('api_key', '')
        if config_api_key and config_api_key != 'your-openrouter-api-key-here':
            default_key = config_api_key
            help_text = "API key loaded from config.json"
        else:
            default_key = ""
            help_text = "Enter your OpenRouter API key for AI assistance, or add it to config.json"
        
        api_key = st.text_input(
            "OpenRouter API Key",
            value=default_key,
            type="password",
            help=help_text,
            placeholder="sk-or-..."
        )
        
        # Update session state with the API key
        st.session_state.openrouter_api_key = api_key
        
        if api_key:
            # Model selection with dynamic fetching
            st.markdown("#### 🤖 AI Model Selection")
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                # Get models from manager
                try:
                    categorized_models = st.session_state.model_manager.get_categorized_models()
                    
                    # Model category selection with count info
                    category_options = []
                    category_mapping = {}
                    
                    for cat_key, models_list in categorized_models.items():
                        count = len(models_list)
                        display_names = {
                            'favorites': f'⭐ Favorites ({count})',
                            'recommended': f'🎯 Recommended ({count})',
                            'free': f'💚 Free Models ({count})',
                            'coding': f'💻 Coding ({count})',
                            'vision': f'👁️ Vision ({count})',
                            'other': f'📦 Other ({count})'
                        }
                        display_name = display_names.get(cat_key, f'{cat_key.title()} ({count})')
                        category_options.append(cat_key)
                        category_mapping[cat_key] = display_name
                    
                    # Filter out truly empty categories for display
                    non_empty_categories = [cat for cat in category_options if len(categorized_models[cat]) > 0]
                    
                    if not non_empty_categories:
                        st.warning("⚠️ No models available. Please check your API connection and refresh.")
                        category = 'free'  # fallback
                    else:
                        category = st.selectbox(
                            "Model Category",
                            options=non_empty_categories,
                            format_func=lambda x: category_mapping[x],
                            help="Choose model category (numbers show available models)"
                        )
                    
                    # Model selection within category
                    models_in_category = categorized_models.get(category, [])
                    
                    if models_in_category:
                        model_options = []
                        model_ids = []
                        
                        for model in models_in_category:
                            name = model['name']
                            provider = model['provider']
                            is_free = "🆓" if model.get('free') else "💰"
                            is_fav = "⭐" if st.session_state.model_manager.is_favorite(model['id']) else ""
                            
                            display_name = f"{is_fav} {is_free} {name} ({provider})"
                            model_options.append(display_name)
                            model_ids.append(model['id'])
                        
                        selected_index = st.selectbox(
                            "Select Model",
                            range(len(model_options)),
                            format_func=lambda x: model_options[x],
                            help="Choose the AI model for assistance"
                        )
                        
                        selected_model = model_ids[selected_index]
                        selected_model_data = models_in_category[selected_index]
                        
                        # Model info
                        with st.expander("📋 Model Details"):
                            st.write(f"**Provider:** {selected_model_data['provider']}")
                            st.write(f"**Type:** {selected_model_data['type']}")
                            st.write(f"**Context:** {selected_model_data.get('context', 'Unknown')} tokens")
                            st.write(f"**Free:** {'Yes' if selected_model_data.get('free') else 'No'}")
                            if selected_model_data.get('capabilities'):
                                st.write(f"**Capabilities:** {', '.join(selected_model_data['capabilities'])}")
                        
                    else:
                        st.warning(f"No models available in {category} category")
                        selected_model = "mistralai/mistral-small-3.2-24b-instruct:free"
                        
                except Exception as e:
                    st.error(f"Error loading models: {e}")
                    selected_model = "mistralai/mistral-small-3.2-24b-instruct:free"
            
            with col2:
                # Favorites and refresh controls
                if st.button("🔄", help="Refresh models from API"):
                    with st.spinner("Refreshing models..."):
                        st.session_state.model_manager.refresh_models()
                        st.rerun()
                
                if 'selected_model' in locals():
                    is_fav = st.session_state.model_manager.is_favorite(selected_model)
                    fav_button_text = "💔" if is_fav else "❤️"
                    fav_help = "Remove from favorites" if is_fav else "Add to favorites"
                    
                    if st.button(fav_button_text, help=fav_help):
                        if is_fav:
                            st.session_state.model_manager.remove_favorite(selected_model)
                        else:
                            st.session_state.model_manager.add_favorite(selected_model)
                        st.rerun()
            
            # Initialize OpenRouter client
            if api_key and (not st.session_state.openrouter_client or 
                          st.session_state.openrouter_client.api_key != api_key):
                logger.info(f"🔑 Initializing OpenRouter client with model: {selected_model}")
                st.session_state.openrouter_client = OpenRouterClient(api_key, selected_model)
                
                # Update HTML generator with the new OpenRouter client for AI template adaptation
                logger.info("🔄 Updating HTML generator with new OpenRouter client")
                st.session_state.html_generator = HTMLResumeGenerator(st.session_state.openrouter_client)
                
                st.success("✅ AI assistant connected with intelligent template adaptation!")
                
                # API Logging Settings
                st.markdown("#### 📊 API Logging")
                
                # Initialize logging setting
                if 'enable_api_logging' not in st.session_state:
                    st.session_state.enable_api_logging = True
                
                enable_api_logging = st.checkbox(
                    "📈 Enable API Call Logging",
                    value=st.session_state.enable_api_logging,
                    key="api_logging_toggle",
                    help="Show detailed API calls, models used, token counts, and timing in logs"
                )
                
                # Update session state
                if enable_api_logging != st.session_state.enable_api_logging:
                    st.session_state.enable_api_logging = enable_api_logging
                
                if enable_api_logging:
                    st.caption("✅ API calls will be logged with detailed metrics")
                else:
                    st.caption("⚠️ API logging disabled - limited debugging info")
                
                # Data cleaning utility
                st.markdown("#### 🧹 Data Cleanup")
                if st.button("🧹 Clean Corrupted Data", help="Fix data corruption from excessive escaping"):
                    if st.session_state.parsed_resume:
                        st.session_state.parsed_resume = sanitize_data(st.session_state.parsed_resume)
                        st.success("✅ Data cleaned! Corruption from excessive escaping has been fixed.")
                        st.rerun()
                    else:
                        st.info("ℹ️ No resume data to clean")
        
        st.markdown("---")
        
        # Debug logs section (collapsible)
        with st.expander("🔍 Debug Logs", expanded=False):
            st.caption("Recent application logs for debugging")
            
            if st.button("🔄 Refresh Logs"):
                st.rerun()
            
            try:
                # Show last 20 lines of today's log file
                if os.path.exists(log_filename):
                    with open(log_filename, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        recent_lines = lines[-20:] if len(lines) > 20 else lines
                        log_text = ''.join(recent_lines)
                        if log_text.strip():
                            st.code(log_text, language='text')
                        else:
                            st.info("No logs yet today")
                else:
                    st.info("No log file found")
            except Exception as e:
                st.error(f"Error reading logs: {e}")
        
        st.markdown("---")
        
        # Information section
        st.markdown("## 📋 Supported Formats")
        st.markdown("""
        - **PDF** files (.pdf)
        - **Images** (.png, .jpg, .jpeg)
        - **Word Documents** (.docx)
        """)
        
        st.markdown("## 🚀 Features")
        st.markdown("""
        - **Smart OCR** for image processing
        - **Layout Analysis** with section detection
        - **AI-Powered** LaTeX optimization
        - **Professional** resume class
        - **Download** ready-to-compile files
        """)
        
        # Rate limiting admin interface (only show if admin features available)
        show_rate_limit_admin()
        
        st.markdown("---")
        st.markdown("## ℹ️ How it works")
        st.markdown("""
        1. **Upload** your resume file
        2. **Analyze** layout and extract text
        3. **Get AI assistance** for optimization
        4. **Download** LaTeX files
        5. **Compile** with your LaTeX editor
        """)

def show_rate_limit_admin():
    """Show rate limiting admin interface in sidebar."""
    try:
        limiter = IPRateLimiter()
        
        # Only show if rate limiting is enabled or user is admin
        if not limiter.enabled and not limiter.is_admin_ip(limiter.get_client_ip()):
            return
        
        st.markdown("---")
        st.markdown("## 🛡️ Rate Limiting")
        
        # Show current status
        status = limiter.get_rate_limit_status()
        
        col1, col2 = st.columns(2)
        with col1:
            if status.get('enabled', True):
                if status.get('is_admin', False):
                    st.success("👑 Admin")
                else:
                    remaining = status.get('remaining', 0)
                    if remaining > 10:
                        st.success(f"✅ {remaining} left")
                    elif remaining > 0:
                        st.warning(f"⚠️ {remaining} left")
                    else:
                        st.error("🚫 Limited")
            else:
                st.info("🔓 Disabled")
        
        with col2:
            st.metric("Window", f"{status.get('time_window', 60)}min")
        
        # Admin controls
        if status.get('is_admin', False):
            with st.expander("👑 Admin Controls"):
                # Show all IPs
                all_status = limiter.get_all_ips_status()
                if all_status:
                    st.markdown("**Active IPs:**")
                    for ip, ip_status in all_status.items():
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.text(f"{ip[:12]}...")
                        with col2:
                            used = ip_status.get('used', 0)
                            max_req = ip_status.get('max_requests', 30)
                            st.text(f"{used}/{max_req}")
                        with col3:
                            if st.button("🗑️", key=f"reset_{ip}", help="Reset this IP"):
                                if limiter.reset_ip_limits(ip):
                                    st.success("Reset!")
                                    st.rerun()
                else:
                    st.info("No active rate limits")
        
        # Rate limit info for non-admin users
        elif status.get('enabled', True):
            with st.expander("ℹ️ Rate Limit Info"):
                st.write(f"**Limit:** {status.get('max_requests', 30)} requests per {status.get('time_window', 60)} minutes")
                st.write(f"**Used:** {status.get('used', 0)} requests")
                st.write(f"**Your IP:** {status.get('ip', 'Unknown')}")
                
                if status.get('remaining', 0) == 0:
                    reset_time = status.get('reset_time')
                    if reset_time:
                        st.write(f"**Reset at:** {reset_time.strftime('%H:%M:%S')}")
    
    except Exception as e:
        logger.error(f"Error in rate limit admin interface: {e}")
        # Don't show errors to users - just log them

def create_input_section():
    """Create the input section with multiple input modes."""
    st.markdown('<h2 class="section-header">📤 Input Your Resume</h2>', unsafe_allow_html=True)
    
    # Input mode selection
    input_mode = st.radio(
        "Choose input method:",
        ["📄 Upload File", "📝 Paste LaTeX Code"],
        horizontal=True,
        help="Upload a resume file for analysis or paste existing LaTeX code for enhancement"
    )
    
    if input_mode == "📄 Upload File":
        create_file_upload_section()
    else:
        create_latex_input_section()

def create_file_upload_section():
    """Create the file upload section."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="upload-section">', unsafe_allow_html=True)
        
        uploaded_file = st.file_uploader(
            "Choose your resume file",
            type=['pdf', 'png', 'jpg', 'jpeg', 'docx'],
            help="📄 PDF format recommended for multi-page resumes. Images process single pages only."
        )
        
        if uploaded_file is not None:
            st.session_state.uploaded_file_name = uploaded_file.name
            file_details = {
                "Filename": uploaded_file.name,
                "File size": f"{uploaded_file.size / 1024:.1f} KB",
                "File type": uploaded_file.type
            }
            
            st.json(file_details)
            
            if st.button("🔍 Analyze Resume", type="primary", use_container_width=True):
                analyze_resume(uploaded_file)
        
        st.markdown('</div>', unsafe_allow_html=True)

def create_latex_input_section():
    """Create the LaTeX input section for users who already have LaTeX code."""
    st.markdown("### 📝 Paste Your LaTeX Code")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Main LaTeX content
        latex_content = st.text_area(
            "LaTeX Resume Code (.tex file content)",
            height=300,
            placeholder="""\\documentclass[10pt,a4paper,ragged2e,withhyper]{altacv}
\\usepackage[utf8]{inputenc}
\\usepackage{geometry}
...

\\name{Your Name}
\\tagline{Your Title}
\\personalinfo{%
  \\email{your.email@example.com}
  \\phone{+1234567890}
}

\\begin{document}
\\makecvheader

\\cvsection{Experience}
...

\\end{document}""",
            help="Paste your complete LaTeX resume code here"
        )
    
    with col2:
        # LaTeX class input (optional)
        st.markdown("#### 🎨 LaTeX Class (Optional)")
        
        class_input_method = st.radio(
            "Class file method:",
            ["📤 Upload .cls file", "📝 Paste class code", "🔧 Use default"],
            help="Provide your custom class file or use our default"
        )
        
        cls_content = ""
        
        if class_input_method == "📤 Upload .cls file":
            uploaded_cls = st.file_uploader(
                "Upload .cls file",
                type=['cls'],
                help="Upload your custom LaTeX class file"
            )
            
            if uploaded_cls is not None:
                cls_content = uploaded_cls.read().decode('utf-8')
                st.success(f"✅ Loaded {uploaded_cls.name}")
        
        elif class_input_method == "📝 Paste class code":
            cls_content = st.text_area(
                "LaTeX Class Code",
                height=150,
                placeholder="\\NeedsTeXFormat{LaTeX2e}\n\\ProvidesClass{your-class}...",
                help="Paste your LaTeX class code here"
            )
        
        else:  # Use default
            st.info("🔧 Will use default resume class")
            cls_content = ""
    
    # Process button
    if latex_content.strip():
        if st.button("🚀 Process LaTeX Code", type="primary", use_container_width=True):
            process_latex_input(latex_content, cls_content)
    else:
        st.info("👆 Paste your LaTeX code above to get started")

def process_latex_input(latex_content: str, cls_content: str = ""):
    """Process directly inputted LaTeX code."""
    try:
        with st.spinner("🔄 Processing your LaTeX code..."):
            # Use default class if none provided
            if not cls_content.strip():
                cls_content = st.session_state.enhanced_generator._get_altacv_class()
            
            # Set session state
            st.session_state.analysis_complete = True
            st.session_state.tex_content = latex_content
            st.session_state.cls_content = cls_content
            st.session_state.uploaded_file_name = "pasted_latex.tex"
            
            # Create mock analysis data for LaTeX input
            st.session_state.analysis_data = {
                'file_path': 'Direct LaTeX Input',
                'sections': [
                    {
                        'title': 'LaTeX Input',
                        'content': [],
                        'section_type': 'direct_input',
                        'y_position': 0
                    }
                ],
                'text_blocks': []
            }
            
            st.success("✅ LaTeX code processed successfully!")
            st.info("💡 You can now use the Preview, AI Enhancement, and Download features!")
            st.rerun()
            
    except Exception as e:
        st.error(f"❌ Error processing LaTeX code: {str(e)}")
        logger.error(f"LaTeX processing error: {e}")

def analyze_resume(uploaded_file):
    """Analyze the uploaded resume file."""
    try:
        with st.spinner("🔄 Analyzing your resume..."):
            # Store original file data for template matching
            uploaded_file.seek(0)
            file_data = uploaded_file.read()
            st.session_state.original_file_data = file_data
            st.session_state.uploaded_file_name = uploaded_file.name
            
            # Create temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=Path(uploaded_file.name).suffix) as tmp_file:
                tmp_file.write(file_data)
                tmp_path = tmp_file.name
            
            # Initialize analyzer
            analyzer = ResumeAnalyzer()
            
            # Analyze the file (this gives us the basic analysis data)
            success, _, _, analysis_data = analyzer.analyze(tmp_path)
            
            # Clean up temporary file
            os.unlink(tmp_path)
            
            if success:
                # Add vision analysis for better original layout matching
                if st.session_state.openrouter_client:
                    st.session_state.advanced_parser.openrouter_client = st.session_state.openrouter_client
                    
                    # Perform vision analysis on the uploaded file if it's an image
                    file_type = uploaded_file.type
                    if file_type in ['image/png', 'image/jpeg', 'image/jpg']:
                        # Reset file pointer and get image data
                        uploaded_file.seek(0)
                        image_data = uploaded_file.read()
                        
                        try:
                            vision_analysis = st.session_state.openrouter_client.analyze_resume_visual_layout(image_data)
                            analysis_data['vision_analysis'] = vision_analysis
                            st.success("✨ Enhanced with AI vision analysis for better original layout matching")
                        except Exception as e:
                            st.warning(f"⚠️ Vision analysis skipped: {str(e)}")
                            logger.warning(f"Vision analysis failed: {e}")
                
                # Get structured resume data
                parsed_resume = st.session_state.advanced_parser.parse_resume(analysis_data)
                
                # Generate proper LaTeX from structured data
                tex_content, cls_content = st.session_state.smart_latex_generator.generate_from_parsed_resume(parsed_resume)
                
                st.session_state.analysis_complete = True
                st.session_state.tex_content = tex_content
                st.session_state.cls_content = cls_content
                st.session_state.analysis_data = analysis_data
                st.session_state.parsed_resume = sanitize_data(parsed_resume)
                st.session_state.parsed_resume_data = parsed_resume  # Store structured resume data for ATS improvements
                st.session_state.original_parsed_resume = parsed_resume  # Store original for comparison
                
                # Show processing info
                total_blocks = len(analysis_data.get('text_blocks', []))
                st.success(f"✅ Resume analyzed successfully! Extracted {total_blocks} text elements.")
                
                # Show parsing method used
                if st.session_state.openrouter_client:
                    st.success("🤖 AI-powered parsing used for accurate content extraction!")
                else:
                    st.info("💡 Add OpenRouter API key for even better AI-powered parsing")
                
                # Show multi-page info for PDFs
                if uploaded_file.name.lower().endswith('.pdf'):
                    st.info("📄 Multi-page PDF processed - all content from every page analyzed.")
                
                st.rerun()
            else:
                st.error("❌ Failed to analyze resume. Please try a different file.")
                
    except Exception as e:
        st.error(f"❌ Error analyzing resume: {str(e)}")
        logger.error(f"Resume analysis error: {e}")

def display_analysis_results():
    """Display the analysis results."""
    if not st.session_state.analysis_complete:
        return
    
    # Check if this is direct LaTeX input
    is_latex_input = st.session_state.analysis_data.get('file_path') == 'Direct LaTeX Input'
    
    if is_latex_input:
        st.markdown('<h2 class="section-header">📝 LaTeX Input Processed</h2>', unsafe_allow_html=True)
        
        # Statistics for LaTeX input
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Input Type", "LaTeX Code")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("LaTeX Length", f"{len(st.session_state.tex_content)} chars")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Class Length", f"{len(st.session_state.cls_content)} chars")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            st.metric("Status", "Ready")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # LaTeX input info
        st.markdown("### 📋 LaTeX Information")
        
        with st.expander("📄 LaTeX Content Summary"):
            lines = st.session_state.tex_content.split('\n')
            st.write(f"**Total lines:** {len(lines)}")
            st.write(f"**Document class:** {lines[0] if lines else 'Unknown'}")
            
            # Extract sections from LaTeX
            latex_sections = []
            for line in lines:
                if '\\section{' in line or '\\cvsection{' in line:
                    section_name = line.split('{')[1].split('}')[0] if '{' in line and '}' in line else 'Unknown'
                    latex_sections.append(section_name)
            
            if latex_sections:
                st.write("**Detected sections:**")
                for section in latex_sections:
                    st.write(f"• {section}")
            
            st.write("**Sample content (first 5 lines):**")
            for i, line in enumerate(lines[:5]):
                if line.strip():
                    st.code(line)
    
    else:
        if st.session_state.openrouter_client:
            st.markdown('<h2 class="section-header">🤖 AI-Powered Analysis Results</h2>', unsafe_allow_html=True)
            st.success("✨ Using AI-enhanced parsing for accurate resume analysis")
        else:
            st.markdown('<h2 class="section-header">📊 Smart Analysis Results</h2>', unsafe_allow_html=True)
            st.info("💡 Add your OpenRouter API key for AI-enhanced analysis")
        
        # Parse resume with advanced parser first (use AI if available)
        if not st.session_state.parsed_resume:
            # Update parser with current OpenRouter client if available
            if st.session_state.openrouter_client:
                st.session_state.advanced_parser.openrouter_client = st.session_state.openrouter_client
            
            with st.spinner("🤖 AI is parsing your resume..."):
                parsed_result = st.session_state.advanced_parser.parse_resume(st.session_state.analysis_data)
                st.session_state.parsed_resume = sanitize_data(parsed_result)
        
        # Statistics using AI-parsed data
        parsed = st.session_state.parsed_resume
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            # Count actual resume sections from parsed data
            sections_count = 0
            # Handle both dict and object formats
            if hasattr(parsed, 'contact_info'):
                # Object format
                if parsed.contact_info: sections_count += 1
                if parsed.professional_summary: sections_count += 1
                if parsed.job_experiences: sections_count += len(parsed.job_experiences)
                if parsed.education: sections_count += len(parsed.education)
                if parsed.skills: sections_count += 1
                if parsed.projects: sections_count += len(parsed.projects)
            else:
                # Dict format
                if parsed.get('contact_info'): sections_count += 1
                if parsed.get('professional_summary'): sections_count += 1
                if parsed.get('job_experiences'): sections_count += len(parsed.get('job_experiences', []))
                if parsed.get('education'): sections_count += len(parsed.get('education', []))
                if parsed.get('skills'): sections_count += 1
                if parsed.get('projects'): sections_count += len(parsed.get('projects', []))
            # Handle certifications for both formats
            if hasattr(parsed, 'certifications'):
                if parsed.certifications: sections_count += 1
            else:
                if parsed.get('certifications'): sections_count += 1
            st.metric("Resume Sections", sections_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            # Count work experiences
            if hasattr(parsed, 'job_experiences'):
                experience_count = len(parsed.job_experiences) if parsed.job_experiences else 0
            else:
                experiences = parsed.get('job_experiences', []) or parsed.get('experience', []) or parsed.get('work_experience', [])
                experience_count = len(experiences) if experiences else 0
            st.metric("Work Experiences", experience_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col3:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            # Count total skills
            skills_count = 0
            if hasattr(parsed, 'skills') and parsed.skills:
                for skill_cat in parsed.skills:
                    if hasattr(skill_cat, 'skills'):
                        skills_count += len(skill_cat.skills) if skill_cat.skills else 0
                    else:
                        # Handle dict format
                        skills_count += len(skill_cat.get('skills', [])) if isinstance(skill_cat, dict) else 0
            elif isinstance(parsed, dict):
                skills_data = parsed.get('skills', [])
                if isinstance(skills_data, list):
                    for skill_item in skills_data:
                        if isinstance(skill_item, dict):
                            skills_count += len(skill_item.get('skills', []))
                        else:
                            skills_count += 1  # Count individual skill
            st.metric("Skills Identified", skills_count)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col4:
            st.markdown('<div class="stats-card">', unsafe_allow_html=True)
            # Show parsing method used
            if st.session_state.openrouter_client:
                st.metric("Parsing", "🤖 AI-Enhanced")
            else:
                st.metric("Parsing", "📝 Standard")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Display structured resume information
        display_parsed_resume_content()

def display_parsed_resume_content():
    """Display parsed resume content in a structured, user-friendly way."""
    if not st.session_state.parsed_resume:
        st.warning("Resume parsing not available.")
        return
    
    # Apply sanitization when accessing data to prevent corruption display
    parsed = sanitize_data(st.session_state.parsed_resume)
    # Update session state with cleaned data
    st.session_state.parsed_resume = parsed
    
    # Header with re-parse option
    col1, col2 = st.columns([3, 1])
    with col1:
        if st.session_state.openrouter_client:
            st.markdown("### 🤖 AI-Enhanced Resume Analysis")
        else:
            st.markdown("### 📋 Smart Resume Analysis")
    
    with col2:
        if st.session_state.openrouter_client:
            if st.button("🤖 Re-parse with AI", help="Use AI for more accurate parsing"):
                # Force re-parsing with AI
                st.session_state.advanced_parser.openrouter_client = st.session_state.openrouter_client
                with st.spinner("🤖 AI is analyzing your resume..."):
                    parsed_result = st.session_state.advanced_parser.parse_resume(st.session_state.analysis_data)
                    st.session_state.parsed_resume = sanitize_data(parsed_result)
                st.success("✅ Resume re-parsed with AI!")
                st.rerun()
        else:
            st.info("💡 Add API key for AI parsing")
    
    # Show detected language if available
    if parsed and hasattr(st.session_state.advanced_parser, '_detect_resume_language'):
        # Get some sample text to detect language
        sample_text = ""
        if st.session_state.analysis_data:
            for section in st.session_state.analysis_data.get('sections', []):
                for block in section.get('content', [])[:5]:  # First 5 blocks
                    sample_text += block.get('text', '') + " "
                    if len(sample_text) > 200:
                        break
                if len(sample_text) > 200:
                    break
        
        if sample_text:
            detected_lang = st.session_state.advanced_parser._detect_resume_language(sample_text)
            if detected_lang != 'English':
                st.info(f"🌍 Detected language: {detected_lang} - Original language preserved in parsing")
    
    # Contact Information
    contact_info = None
    if hasattr(parsed, 'contact_info'):
        contact_info = parsed.contact_info
    else:
        contact_info = parsed.get('contact_info')
    
    if contact_info:
        # Handle both object and dict format for contact_info
        name = getattr(contact_info, 'name', None) if hasattr(contact_info, 'name') else contact_info.get('name')
        email = getattr(contact_info, 'email', None) if hasattr(contact_info, 'email') else contact_info.get('email')
        
        if name or email:
            with st.expander("👤 Contact Information", expanded=True):
                col1, col2 = st.columns(2)
                
                with col1:
                    if name:
                        st.markdown(f"**Name:** {name}")
                    if email:
                        st.markdown(f"**Email:** {email}")
                    
                    phone = getattr(contact_info, 'phone', None) if hasattr(contact_info, 'phone') else contact_info.get('phone')
                    if phone:
                        st.markdown(f"**Phone:** {phone}")
                
                with col2:
                    location = getattr(contact_info, 'location', None) if hasattr(contact_info, 'location') else contact_info.get('location')
                    if location:
                        st.markdown(f"**Location:** {location}")
                    
                    linkedin = getattr(contact_info, 'linkedin', None) if hasattr(contact_info, 'linkedin') else contact_info.get('linkedin')
                    if linkedin:
                        st.markdown(f"**LinkedIn:** {linkedin}")
                    
                    github = getattr(contact_info, 'github', None) if hasattr(contact_info, 'github') else contact_info.get('github')
                    if github:
                        st.markdown(f"**GitHub:** {github}")
    
    # Professional Summary
    if hasattr(parsed, 'professional_summary') and parsed.professional_summary:
        with st.expander("📝 Professional Summary"):
            st.write(parsed.professional_summary)
    elif isinstance(parsed, dict) and parsed.get('professional_summary'):
        with st.expander("📝 Professional Summary"):
            st.write(parsed.get('professional_summary'))
    
    # Work Experience
    experiences = []
    if hasattr(parsed, 'job_experiences') and parsed.job_experiences:
        experiences = parsed.job_experiences
    elif isinstance(parsed, dict):
        experiences = parsed.get('job_experiences', []) or parsed.get('experience', []) or parsed.get('work_experience', [])
    
    if experiences:
        with st.expander(f"💼 Professional Experience ({len(experiences)} positions)", expanded=True):
            for i, job in enumerate(experiences):
                # Handle both object and dict format for job
                if hasattr(job, 'job_title'):
                    job_title = job.job_title or 'Position'
                    company = getattr(job, 'company', None)
                    location = getattr(job, 'location', None)
                    start_date = getattr(job, 'start_date', None)
                    end_date = getattr(job, 'end_date', None)
                    is_current = getattr(job, 'is_current', False)
                    description = getattr(job, 'description', [])
                else:
                    job_title = job.get('job_title') or job.get('title') or 'Position'
                    company = job.get('company')
                    location = job.get('location')
                    start_date = job.get('start_date')
                    end_date = job.get('end_date')
                    is_current = job.get('is_current', False)
                    description = job.get('description', [])
                
                st.markdown(f"#### {i+1}. {job_title}")
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    if company:
                        st.markdown(f"**Company:** {company}")
                    if location:
                        st.markdown(f"**Location:** {location}")
                
                with col2:
                    if start_date or end_date:
                        period = f"{start_date or 'Unknown'} - {end_date or 'Present'}"
                        st.markdown(f"**Period:** {period}")
                    if is_current:
                        st.success("🟢 Current Position")
                
                if description:
                    with st.expander(f"📄 Job Description ({len(description)} points)"):
                        for desc in description:
                            st.write(f"• {desc}")
                
                if i < len(experiences) - 1:
                    st.markdown("---")
    
    # Education
    education = []
    if hasattr(parsed, 'education') and parsed.education:
        education = parsed.education
    elif isinstance(parsed, dict):
        education = parsed.get('education', [])
    
    if education:
        with st.expander(f"🎓 Education ({len(education)} entries)"):
            for i, edu in enumerate(education):
                # Handle both object and dict format for education
                if hasattr(edu, 'degree'):
                    degree = edu.degree or 'Degree'
                    school = getattr(edu, 'school', None)
                    graduation_date = getattr(edu, 'graduation_date', None)
                    gpa = getattr(edu, 'gpa', None)
                    honors = getattr(edu, 'honors', None)
                    relevant_courses = getattr(edu, 'relevant_courses', [])
                else:
                    degree = edu.get('degree') or 'Degree'
                    school = edu.get('school')
                    graduation_date = edu.get('graduation_date')
                    gpa = edu.get('gpa')
                    honors = edu.get('honors')
                    relevant_courses = edu.get('relevant_courses', [])
                
                st.markdown(f"#### {i+1}. {degree}")
                
                col1, col2 = st.columns(2)
                with col1:
                    if school:
                        st.markdown(f"**School:** {school}")
                    if graduation_date:
                        st.markdown(f"**Graduation:** {graduation_date}")
                
                with col2:
                    if gpa:
                        st.markdown(f"**GPA:** {gpa}")
                    if honors:
                        st.markdown(f"**Honors:** {honors}")
                
                if relevant_courses:
                    st.markdown(f"**Relevant Courses:** {', '.join(relevant_courses)}")
                
                if i < len(education) - 1:
                    st.markdown("---")
    
    # Projects
    projects = []
    if hasattr(parsed, 'projects') and parsed.projects:
        projects = parsed.projects
    elif isinstance(parsed, dict):
        projects = parsed.get('projects', [])
    
    if projects:
        with st.expander(f"🚀 Projects ({len(projects)} projects)"):
            for i, project in enumerate(projects):
                # Handle both object and dict format for projects
                if hasattr(project, 'title'):
                    title = project.title or f'Project {i+1}'
                    description = getattr(project, 'description', None)
                    date = getattr(project, 'date', None)
                    link = getattr(project, 'link', None)
                    technologies = getattr(project, 'technologies', [])
                else:
                    title = project.get('title') or f'Project {i+1}'
                    description = project.get('description')
                    date = project.get('date')
                    link = project.get('link')
                    technologies = project.get('technologies', [])
                
                st.markdown(f"#### {i+1}. {title}")
                
                col1, col2 = st.columns([3, 1])
                with col1:
                    if description:
                        st.write(description)
                
                with col2:
                    if date:
                        st.markdown(f"**Date:** {date}")
                    if link:
                        st.markdown(f"**Link:** [View Project]({link})")
                
                if technologies:
                    st.markdown("**Technologies:**")
                    tech_cols = st.columns(min(len(technologies), 5))
                    for j, tech in enumerate(technologies):
                        with tech_cols[j % 5]:
                            st.code(tech)
                
                if i < len(projects) - 1:
                    st.markdown("---")
    
    # Skills
    skills = []
    if hasattr(parsed, 'skills') and parsed.skills:
        skills = parsed.skills
    elif isinstance(parsed, dict):
        skills = parsed.get('skills', [])
    
    if skills:
        with st.expander(f"⚡ Skills & Technologies ({len(skills)} categories)"):
            for skill_category in skills:
                # Handle both object and dict format for skill categories
                if hasattr(skill_category, 'category'):
                    category_name = skill_category.category
                    category_skills = getattr(skill_category, 'skills', [])
                else:
                    category_name = skill_category.get('category', 'Skills')
                    category_skills = skill_category.get('skills', [])
                
                st.markdown(f"**{category_name}:**")
                
                # Display skills in columns for better layout
                if category_skills:
                    skill_cols = st.columns(min(len(category_skills), 4))
                    for i, skill in enumerate(category_skills):
                        with skill_cols[i % 4]:
                            st.code(skill)
                st.markdown("")
    
    # Additional Sections
    if hasattr(parsed, 'additional_sections') and parsed.additional_sections:
        for section_name, content in parsed.additional_sections.items():
            if content and any(item.strip() for item in content):  # Only show non-empty sections
                with st.expander(f"📄 {section_name}"):
                    for item in content:
                        if item.strip():
                            st.write(f"• {item.strip()}")
    elif isinstance(parsed, dict) and parsed.get('additional_sections'):
        for section_name, content in parsed.get('additional_sections', {}).items():
            if content and any(item.strip() for item in content):  # Only show non-empty sections
                with st.expander(f"📄 {section_name}"):
                    for item in content:
                        if item.strip():
                            st.write(f"• {item.strip()}")
    
    # Certifications
    certifications = []
    if hasattr(parsed, 'certifications') and parsed.certifications:
        certifications = parsed.certifications
    elif isinstance(parsed, dict):
        certifications = parsed.get('certifications', [])
    
    if certifications:
        with st.expander(f"🏆 Certifications ({len(certifications)})"):
            for cert in certifications:
                st.write(f"• {cert}")
    
    # Languages
    languages = []
    if hasattr(parsed, 'languages') and parsed.languages:
        languages = parsed.languages
    elif isinstance(parsed, dict):
        languages = parsed.get('languages', [])
    
    if languages:
        with st.expander(f"🌍 Languages ({len(languages)})"):
            for lang in languages:
                st.write(f"• {lang}")

def display_latex_code():
    """Display the generated LaTeX code."""
    if not st.session_state.analysis_complete:
        return
    
    st.markdown('<h2 class="section-header">📝 Generated LaTeX Code</h2>', unsafe_allow_html=True)
    
    # AI Assistance section
    if st.session_state.openrouter_client:
        st.markdown("### 🤖 AI Assistance")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("🔧 Improve Resume Content", use_container_width=True):
                improve_resume_content_with_comparison()
        
        with col2:
            if st.button("📊 Detailed Critique", use_container_width=True):
                show_detailed_critique()
        
        with col3:
            if st.button("🔄 Regenerate LaTeX", use_container_width=True, help="Regenerate LaTeX from parsed resume data"):
                regenerate_latex_from_parsed_data()
        
        with col4:
            with st.popover("🎯 Quick Job Adapt", use_container_width=True):
                st.markdown("**Quick Job Adaptation**")
                quick_job = st.text_area(
                    "Job Description",
                    placeholder="Paste job description for quick adaptation...",
                    height=100,
                    key="quick_job_desc"
                )
                
                if quick_job and st.button("Adapt Now", key="quick_adapt"):
                    adapt_resume_to_job(quick_job, "moderate")
    
    # LaTeX code display and download
    tab1, tab2, tab3, tab4 = st.tabs(["📥 PDF Download", "📄 Main File (resume.tex)", "🎨 Style File (resume.cls)", "📦 Downloads"])
    
    with tab1:
        display_pdf_preview()
    
    with tab2:
        st.code(st.session_state.tex_content, language='latex')
        
        # Download button for .tex file
        st.download_button(
            label="📥 Download resume.tex",
            data=st.session_state.tex_content,
            file_name="resume.tex",
            mime="text/plain"
        )
    
    with tab3:
        st.code(st.session_state.cls_content, language='latex')
        
        # Download button for .cls file
        st.download_button(
            label="📥 Download resume.cls",
            data=st.session_state.cls_content,
            file_name="resume.cls",
            mime="text/plain"
        )
    
    with tab4:
        display_download_options()

def improve_latex_with_ai():
    """Improve LaTeX code using AI assistance."""
    if not st.session_state.openrouter_client:
        st.error("❌ Please enter your OpenRouter API key in the sidebar.")
        return
    
    try:
        with st.spinner("🤖 AI is improving your LaTeX code..."):
            improved_tex = st.session_state.openrouter_client.improve_latex_code(
                st.session_state.tex_content,
                st.session_state.cls_content
            )
            
            if improved_tex and not improved_tex.startswith("Error:"):
                st.session_state.tex_content = improved_tex
                st.success("✅ LaTeX code improved by AI!")
                st.rerun()
            else:
                st.error(f"❌ AI improvement failed: {improved_tex}")
                
    except Exception as e:
        st.error(f"❌ Error during AI improvement: {str(e)}")

def improve_resume_content_with_comparison():
    """Improve resume content and create inline comparison interface."""
    if not st.session_state.openrouter_client:
        st.error("❌ Please enter your OpenRouter API key in the sidebar.")
        return
    
    if not st.session_state.parsed_resume:
        st.error("❌ No parsed resume data available for improvement.")
        return
    
    try:
        # Initialize comparison service if not exists
        if 'comparison_service' not in st.session_state:
            st.session_state.comparison_service = ResumeEnhancementComparison()
        
        # Set OpenRouter client for AI improvements
        if st.session_state.openrouter_client:
            st.session_state.comparison_service.openrouter_client = st.session_state.openrouter_client
        
        # Only create comparison if not already done
        if not st.session_state.comparison_service.comparisons:
            # Prepare ALL sections without AI improvement initially
            # User will select sections and improve them manually using the interface
            
            # Add professional summary if available
            if st.session_state.parsed_resume.professional_summary:
                section_key = "professional_summary"
                section_name = "Professional Summary"
                original_text = st.session_state.parsed_resume.professional_summary
                
                st.session_state.comparison_service.add_section_comparison(
                    section_key, section_name, original_text, original_text  # Start with same content
                )
            
            # Add ALL professional experience sections
            if st.session_state.parsed_resume.job_experiences:
                for i, job in enumerate(st.session_state.parsed_resume.job_experiences):
                    section_key = f"experience_{i}"
                    section_name = f"Experience: {job.job_title or 'Position'} at {job.company or 'Company'}"
                    
                    # Convert job to text
                    original_text = f"{job.job_title or 'Position'} at {job.company or 'Company'}"
                    if job.start_date or job.end_date:
                        date_range = f"{job.start_date or ''} - {job.end_date or 'Present'}"
                        original_text += f"\n{date_range}"
                    if job.location:
                        original_text += f"\n{job.location}"
                    if job.description:
                        original_text += "\n" + "\n".join(f"• {desc}" for desc in job.description)
                    
                    st.session_state.comparison_service.add_section_comparison(
                        section_key, section_name, original_text, original_text  # Start with same content
                    )
            
            # Add ALL education sections
            if st.session_state.parsed_resume.education:
                for i, edu in enumerate(st.session_state.parsed_resume.education):
                    section_key = f"education_{i}"
                    section_name = f"Education: {edu.degree or 'Degree'} at {edu.school or 'School'}"
                    
                    original_text = f"{edu.degree or 'Degree'}\n{edu.school or 'School'}"
                    if edu.graduation_date:
                        original_text += f"\n{edu.graduation_date}"
                    if edu.gpa:
                        original_text += f"\nGPA: {edu.gpa}"
                    if edu.honors:
                        original_text += f"\nHonors: {edu.honors}"
                    if edu.relevant_courses:
                        original_text += f"\nRelevant Courses: {', '.join(edu.relevant_courses)}"
                    
                    st.session_state.comparison_service.add_section_comparison(
                        section_key, section_name, original_text, original_text  # Start with same content
                    )
            
            # Add skills section
            if st.session_state.parsed_resume.skills:
                section_key = "skills"
                section_name = "Technical Skills"
                
                original_text = ""
                for skill_cat in st.session_state.parsed_resume.skills:
                    if skill_cat.category:
                        original_text += f"{skill_cat.category}: {', '.join(skill_cat.skills)}\n"
                    else:
                        original_text += f"{', '.join(skill_cat.skills)}\n"
                
                st.session_state.comparison_service.add_section_comparison(
                    section_key, section_name, original_text.strip(), original_text.strip()  # Start with same content
                )
            
            # Add ALL project sections
            if st.session_state.parsed_resume.projects:
                for i, project in enumerate(st.session_state.parsed_resume.projects):
                    section_key = f"project_{i}"
                    section_name = f"Project: {project.title or f'Project {i+1}'}"
                    
                    original_text = f"{project.title or f'Project {i+1}'}"
                    if project.date:
                        original_text += f"\n{project.date}"
                    if project.description:
                        original_text += f"\n{project.description}"
                    if project.technologies:
                        original_text += f"\nTechnologies: {', '.join(project.technologies)}"
                    
                    st.session_state.comparison_service.add_section_comparison(
                        section_key, section_name, original_text, original_text  # Start with same content
                    )
            
            # Add contact information
            if st.session_state.parsed_resume.contact_info:
                section_key = "contact_info"
                section_name = "Contact Information"
                contact = st.session_state.parsed_resume.contact_info
                
                original_text = f"{contact.name or 'Name'}"
                if contact.email:
                    original_text += f"\nEmail: {contact.email}"
                if contact.phone:
                    original_text += f"\nPhone: {contact.phone}"
                if contact.location:
                    original_text += f"\nLocation: {contact.location}"
                if contact.linkedin:
                    original_text += f"\nLinkedIn: {contact.linkedin}"
                if contact.github:
                    original_text += f"\nGitHub: {contact.github}"
                
                st.session_state.comparison_service.add_section_comparison(
                    section_key, section_name, original_text, original_text  # Start with same content
                )
            
            # Add certifications if available
            if st.session_state.parsed_resume.certifications:
                section_key = "certifications"
                section_name = "Certifications"
                original_text = "\n".join(f"• {cert}" for cert in st.session_state.parsed_resume.certifications)
                
                st.session_state.comparison_service.add_section_comparison(
                    section_key, section_name, original_text, original_text  # Start with same content
                )
            
            # Add additional sections if available
            if st.session_state.parsed_resume.additional_sections:
                for section_name, items in st.session_state.parsed_resume.additional_sections.items():
                    if items and any(item.strip() for item in items):
                        section_key = f"additional_{section_name.lower().replace(' ', '_')}"
                        original_text = "\n".join(f"• {item}" for item in items if item.strip())
                        
                        st.session_state.comparison_service.add_section_comparison(
                            section_key, section_name, original_text, original_text  # Start with same content
                        )
        
        # Display the inline comparison interface
        display_inline_comparison(st.session_state.comparison_service)
                
    except Exception as e:
        st.error(f"❌ Error during resume improvement: {str(e)}")
        logger.error(f"Resume improvement error: {e}")

def _convert_parsed_resume_to_text(parsed_resume) -> str:
    """Convert parsed resume back to text for AI processing."""
    text_parts = []
    
    # Contact info
    if parsed_resume.contact_info:
        contact = parsed_resume.contact_info
        contact_parts = []
        if contact.name:
            contact_parts.append(f"Name: {contact.name}")
        if contact.email:
            contact_parts.append(f"Email: {contact.email}")
        if contact.phone:
            contact_parts.append(f"Phone: {contact.phone}")
        if contact.location:
            contact_parts.append(f"Location: {contact.location}")
        if contact_parts:
            text_parts.append("CONTACT INFORMATION\n" + "\n".join(contact_parts))
    
    # Professional summary
    if parsed_resume.professional_summary:
        text_parts.append(f"PROFESSIONAL SUMMARY\n{parsed_resume.professional_summary}")
    
    # Experience
    if parsed_resume.job_experiences:
        exp_parts = ["PROFESSIONAL EXPERIENCE"]
        for exp in parsed_resume.job_experiences:
            exp_text = f"{exp.job_title or 'Position'} | {exp.company or 'Company'} | {exp.start_date or ''} - {exp.end_date or 'Present'}"
            if exp.location:
                exp_text += f" | {exp.location}"
            exp_parts.append(exp_text)
            
            if exp.description:
                for desc in exp.description:
                    exp_parts.append(f"• {desc}")
            exp_parts.append("")
        
        text_parts.append("\n".join(exp_parts))
    
    # Education
    if parsed_resume.education:
        edu_parts = ["EDUCATION"]
        for edu in parsed_resume.education:
            edu_text = f"{edu.degree or 'Degree'} | {edu.school or 'School'} | {edu.graduation_date or ''}"
            if edu.gpa:
                edu_text += f" | GPA: {edu.gpa}"
            edu_parts.append(edu_text)
        
        text_parts.append("\n".join(edu_parts))
    
    # Skills
    if parsed_resume.skills:
        skills_parts = ["SKILLS"]
        for skill_cat in parsed_resume.skills:
            if skill_cat.category and skill_cat.skills:
                skills_parts.append(f"{skill_cat.category}: {', '.join(skill_cat.skills)}")
        
        text_parts.append("\n".join(skills_parts))
    
    # Projects
    if parsed_resume.projects:
        proj_parts = ["PROJECTS"]
        for proj in parsed_resume.projects:
            proj_text = f"{proj.title or 'Project'}"
            if proj.date:
                proj_text += f" | {proj.date}"
            proj_parts.append(proj_text)
            
            if proj.description:
                proj_parts.append(proj.description)
            if proj.technologies:
                proj_parts.append(f"Technologies: {', '.join(proj.technologies)}")
            proj_parts.append("")
        
        text_parts.append("\n".join(proj_parts))
    
    return "\n\n".join(text_parts)

def display_inline_comparison(comparison_service):
    """Display a beautiful, intuitive inline comparison interface."""
    if not comparison_service or not comparison_service.comparisons:
        st.warning("🚫 No sections available for improvement")
        return
    
    # Beautiful header with gradient effect
    st.markdown("""
    <div style="
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    ">
        <h2 style="color: white; margin: 0; font-size: 1.8rem;">
            ✨ Resume Section Optimizer
        </h2>
        <p style="color: #e0e7ff; margin: 0.5rem 0 0 0; font-size: 1rem;">
            Select any section, get AI-powered improvements, and enhance your resume
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Section selector with beautiful styling
    section_options = []
    section_keys = []
    
    for key, section in comparison_service.comparisons.items():
        # Add icons based on section type
        icon = "💼" if "experience" in section.section_name.lower() else \
               "🎓" if "education" in section.section_name.lower() else \
               "🛠️" if "skill" in section.section_name.lower() else \
               "🚀" if "project" in section.section_name.lower() else \
               "📝" if "summary" in section.section_name.lower() else \
               "📞" if "contact" in section.section_name.lower() else \
               "🏆" if "certification" in section.section_name.lower() else "📄"
        
        section_options.append(f"{icon} {section.section_name}")
        section_keys.append(key)
    
    if not section_options:
        st.error("❌ No sections available for optimization")
        return
    
    # Elegant section selector
    st.markdown("### 🎯 Choose Section to Optimize")
    selected_section_idx = st.selectbox(
        "",
        range(len(section_options)),
        format_func=lambda x: section_options[x],
        key="inline_section_selector",
        label_visibility="collapsed"
    )
    
    selected_section_key = section_keys[selected_section_idx]
    selected_section = comparison_service.comparisons[selected_section_key]
    
    # Global history management
    col1, col2, col3 = st.columns([2, 1, 1])
    with col3:
        if st.button("🗑️ Clear All History", help="Remove version history from all sections", type="secondary"):
            if comparison_service.clear_all_version_history():
                regenerate_latex_from_comparison(comparison_service)
                st.success("✅ All version history cleared!")
                st.rerun()
    
    # Main content area with tabs for better organization
    tab1, tab2, tab3 = st.tabs(["📝 Content View", "🤖 AI Improvements", "📚 Version History"])
    
    with tab1:
        # Content viewing area
        col_toggle, col_spacer = st.columns([1, 3])
        with col_toggle:
            # Toggle for showing original
            toggle_key = f"show_orig_{selected_section_key}"
            if toggle_key not in st.session_state:
                st.session_state[toggle_key] = False
            
            show_original = st.toggle(
                "Compare with original", 
                value=st.session_state[toggle_key],
                key=toggle_key,
                help="Show original version alongside current version"
            )
        
        if show_original:
            # Side-by-side comparison
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📄 Original Version")
                st.markdown("""
                <div style="
                    background-color: #f8fafc;
                    border-left: 4px solid #64748b;
                    padding: 1rem;
                    border-radius: 6px;
                    margin-bottom: 1rem;
                ">
                """, unsafe_allow_html=True)
                
                st.text_area(
                    "",
                    value=selected_section.original,
                    height=300,
                    disabled=True,
                    key=f"orig_display_{selected_section_key}",
                    label_visibility="collapsed"
                )
                st.markdown("</div>", unsafe_allow_html=True)
            
            with col2:
                st.markdown("### ✨ Enhanced Version")
                st.markdown("""
                <div style="
                    background-color: #f0fdf4;
                    border-left: 4px solid #22c55e;
                    padding: 1rem;
                    border-radius: 6px;
                    margin-bottom: 1rem;
                ">
                """, unsafe_allow_html=True)
                
                st.text_area(
                    "",
                    value=selected_section.current,
                    height=300,
                    disabled=True,
                    key=f"current_display_{selected_section_key}",
                    label_visibility="collapsed"
                )
                st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Single view
            st.markdown("### 📝 Current Version")
            st.markdown("""
            <div style="
                background: linear-gradient(135deg, #f0fdf4 0%, #ecfdf5 100%);
                border: 1px solid #22c55e;
                border-radius: 8px;
                padding: 1rem;
                margin-bottom: 1rem;
            ">
            """, unsafe_allow_html=True)
            
            st.text_area(
                "",
                value=selected_section.current,
                height=300,
                disabled=True,
                key=f"current_only_display_{selected_section_key}",
                label_visibility="collapsed"
            )
            st.markdown("</div>", unsafe_allow_html=True)
    
    with tab2:
        # AI Improvements section
        st.markdown("### 🎯 Intelligent Improvements")
        
        # Smart quick actions in a grid
        if st.session_state.openrouter_client:
            # Cache quick actions to avoid regenerating every time
            cache_key = f"quick_actions_{selected_section_key}"
            if cache_key not in st.session_state:
                with st.spinner("🤖 Analyzing section and generating smart suggestions..."):
                    st.session_state[cache_key] = generate_smart_quick_actions(selected_section, st.session_state.openrouter_client)
            
            quick_actions = st.session_state[cache_key]
            
            st.markdown("#### 🚀 One-Click Improvements")
            
            # Display actions in a nice grid
            cols = st.columns(2)
            for i, (action_text, action_prompt) in enumerate(quick_actions):
                with cols[i % 2]:
                    if st.button(
                        action_text, 
                        key=f"smart_action_{selected_section_key}_{i}",
                        use_container_width=True,
                        help=f"Apply: {action_prompt[:100]}..."
                    ):
                        with st.spinner("✨ Applying improvement..."):
                            improve_section_with_prompt(comparison_service, selected_section_key, action_prompt)
        
        else:
            st.info("🔑 **Add your OpenRouter API key** in the sidebar to unlock AI-powered improvements!")
        
        # Custom improvement section
        st.markdown("---")
        st.markdown("#### ✍️ Custom Improvement")
        
        custom_prompt = st.text_area(
            "Describe how you'd like to improve this section:",
            placeholder="""Examples:
• Make bullet points more action-oriented and impactful
• Add specific metrics and quantifiable achievements
• Emphasize leadership and management experience
• Include more technical details and tools used
• Make the language more concise and powerful
• Optimize for ATS with relevant keywords""",
            height=120,
            key=f"custom_prompt_{selected_section_key}"
        )
        
        col_apply, col_spacer = st.columns([1, 2])
        with col_apply:
            if st.button(
                "🎯 Apply Custom Improvement", 
                disabled=not custom_prompt.strip(),
                key=f"apply_custom_{selected_section_key}",
                type="primary",
                use_container_width=True
            ):
                if comparison_service.openrouter_client:
                    with st.spinner("🤖 Applying your custom improvement..."):
                        improve_section_with_prompt(comparison_service, selected_section_key, custom_prompt)
                else:
                    st.error("🔑 OpenRouter API key required for custom improvements")
    
    with tab3:
        # Version history
        if selected_section.versions:
            st.markdown("### 📚 Enhancement History")
            st.markdown("Track all the improvements made to this section:")
            
            version_names = ["📄 Original Version"] + [f"✨ {v.version_name}" for v in selected_section.versions]
            
            selected_version = st.selectbox(
                "Select version to preview or restore:",
                range(len(version_names)),
                format_func=lambda x: version_names[x],
                index=len(version_names) - 1,
                key=f"version_selector_{selected_section_key}"
            )
            
            # Show selected version content
            if selected_version == 0:
                preview_content = selected_section.original
            else:
                preview_content = selected_section.versions[selected_version - 1].content
            
            st.markdown("#### 👀 Preview Selected Version")
            st.text_area(
                "",
                value=preview_content,
                height=200,
                disabled=True,
                key=f"version_preview_{selected_section_key}_{selected_version}",
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Restore This Version", key=f"revert_{selected_section_key}", type="primary"):
                    if selected_version == 0:
                        comparison_service.revert_to_version(selected_section_key, -1)
                    else:
                        comparison_service.revert_to_version(selected_section_key, selected_version - 1)
                    
                    regenerate_latex_from_comparison(comparison_service)
                    st.success("✅ Version restored successfully!")
                    st.balloons()
            
            with col2:
                if st.button("🗑️ Clear History", key=f"clear_history_{selected_section_key}", help="Remove all version history for this section"):
                    if comparison_service.clear_version_history(selected_section_key):
                        regenerate_latex_from_comparison(comparison_service)
                        st.success("✅ Version history cleared!")
                        st.rerun()
        else:
            st.info("📝 No version history yet. Make some improvements to see them tracked here!")
    
    # Bottom status bar
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        versions_count = len(selected_section.versions)
        st.metric("🔄 Versions", versions_count, help="Number of improvements made")
    
    with col2:
        word_count = len(selected_section.current.split())
        st.metric("📝 Words", word_count, help="Current word count")
    
    with col3:
        if versions_count > 0:
            st.metric("📈 Status", "Enhanced", help="This section has been improved")
        else:
            st.metric("📊 Status", "Original", help="Original content, ready for improvement")

def generate_smart_quick_actions(selected_section, openrouter_client):
    """Generate AI-powered quick actions tailored to the specific section."""
    try:
        section_type = selected_section.section_type
        section_content = selected_section.current
        section_name = selected_section.section_name
        
        # Create a prompt to generate smart quick actions
        prompt = f"""
Generate 3-4 specific, actionable improvement suggestions for this resume section. Each suggestion should be:
1. Tailored to the specific content and section type
2. Professionally worded and concise 
3. Ready to use as improvement prompts

Section Type: {section_type}
Section Name: {section_name}
Current Content:
{section_content}

For each suggestion, provide:
- A short action button label (2-4 words with emoji)
- A detailed improvement prompt

Format as JSON array:
[
  {{"label": "🚀 Action Label", "prompt": "Detailed improvement instruction..."}},
  {{"label": "📊 Another Action", "prompt": "Another detailed instruction..."}}
]

Focus on the most impactful improvements for this specific section type and content.
"""
        
        # Get AI response
        response = openrouter_client._make_request(prompt, max_tokens=800)
        
        # Try to parse JSON response
        try:
            import json
            actions_data = json.loads(response)
            quick_actions = [(action["label"], action["prompt"]) for action in actions_data]
            
            # Validate we have actions
            if len(quick_actions) > 0:
                return quick_actions[:4]  # Limit to 4 actions max
                
        except (json.JSONDecodeError, KeyError):
            # Fallback to parsing text response
            lines = response.strip().split('\n')
            quick_actions = []
            
            for line in lines:
                if '|' in line and len(quick_actions) < 4:
                    parts = line.split('|', 1)
                    if len(parts) == 2:
                        label = parts[0].strip()
                        prompt = parts[1].strip()
                        if label and prompt:
                            quick_actions.append((label, prompt))
            
            if quick_actions:
                return quick_actions
        
        # Ultimate fallback - section-specific default actions
        return get_default_quick_actions_for_section(section_type, section_name)
        
    except Exception as e:
        logger.error(f"Error generating smart quick actions: {e}")
        return get_default_quick_actions_for_section(selected_section.section_type, selected_section.section_name)

def get_default_quick_actions_for_section(section_type, section_name):
    """Get default quick actions based on section type."""
    
    if "experience" in section_type.lower() or "experience" in section_name.lower():
        return [
            ("🚀 Action Verbs", "Replace weak verbs with strong action verbs (achieved, developed, implemented, led, optimized)"),
            ("📊 Add Metrics", "Add specific numbers, percentages, or quantifiable achievements where possible"),
            ("🎯 Show Impact", "Emphasize the business impact and results of your work"),
            ("✨ ATS Keywords", "Optimize for ATS by including relevant industry keywords")
        ]
    elif "education" in section_type.lower() or "education" in section_name.lower():
        return [
            ("🏆 Highlight Honors", "Emphasize academic achievements, honors, or high GPA if relevant"),
            ("📚 Relevant Courses", "Add relevant coursework that aligns with your career goals"),
            ("🔗 Connect to Career", "Show how your education relates to your professional objectives"),
            ("📅 Optimize Format", "Ensure proper formatting with dates and clear degree information")
        ]
    elif "skill" in section_type.lower() or "skill" in section_name.lower():
        return [
            ("📂 Categorize Skills", "Group skills into logical categories (Programming, Frameworks, Tools, etc.)"),
            ("⭐ Prioritize Top Skills", "Move most relevant skills to the beginning of each category"),
            ("🔄 Remove Outdated", "Remove outdated or basic skills that don't add value"),
            ("🎯 Match Job Requirements", "Align skills with current job market demands")
        ]
    elif "project" in section_type.lower() or "project" in section_name.lower():
        return [
            ("💻 Technical Details", "Add specific technologies, frameworks, and tools used"),
            ("📈 Show Results", "Include metrics like users, performance improvements, or business impact"),
            ("🔗 Add Links", "Include GitHub links or live demo URLs if available"),
            ("🎯 Business Value", "Explain the purpose and value of the project")
        ]
    elif "summary" in section_type.lower() or "summary" in section_name.lower():
        return [
            ("🎯 Focus Message", "Create a clear, focused professional brand statement"),
            ("📊 Add Numbers", "Include years of experience, key metrics, or achievements"),
            ("🔑 Key Skills", "Highlight 2-3 most important skills or specializations"),
            ("✂️ Make Concise", "Reduce to 2-3 impactful sentences")
        ]
    elif "contact" in section_type.lower() or "contact" in section_name.lower():
        return [
            ("🔗 Add LinkedIn", "Include professional LinkedIn profile URL"),
            ("💻 Add Portfolio", "Add GitHub, portfolio website, or professional links"),
            ("📍 Optimize Location", "Use city, state format appropriate for target jobs"),
            ("✨ Professional Email", "Ensure email address is professional and current")
        ]
    else:
        # Generic actions for any section
        return [
            ("✨ Improve Writing", "Enhance clarity, grammar, and professional tone"),
            ("🎯 Focus Content", "Remove unnecessary details and focus on key information"),
            ("📝 Better Format", "Improve formatting and structure for better readability"),
            ("🔑 Add Keywords", "Include relevant industry keywords for better ATS compatibility")
        ]

def improve_section_with_prompt(comparison_service, section_key, prompt):
    """Improve a section with a specific prompt."""
    try:
        result = comparison_service.enhance_section_with_custom_prompt(section_key, prompt)
        
        if not result.startswith("Error:") and not result.startswith("Enhancement failed:"):
            # Regenerate LaTeX from updated comparison
            regenerate_latex_from_comparison(comparison_service)
            st.success("✅ Section improved successfully!")
        else:
            st.error(f"❌ {result}")
            
    except Exception as e:
        st.error(f"❌ Error improving section: {str(e)}")

def regenerate_latex_from_comparison(comparison_service):
    """Regenerate LaTeX from the current comparison state."""
    try:
        # Build updated parsed resume from comparison data
        updated_resume = build_parsed_resume_from_comparison(comparison_service)
        
        # Generate new LaTeX
        tex_content, cls_content = st.session_state.smart_latex_generator.generate_from_parsed_resume(updated_resume)
        
        # Update session state
        st.session_state.tex_content = tex_content
        st.session_state.cls_content = cls_content
        st.session_state.parsed_resume = sanitize_data(updated_resume)
        
    except Exception as e:
        logger.error(f"Error regenerating LaTeX from comparison: {e}")

def build_parsed_resume_from_comparison(comparison_service):
    """Build a ParsedResume object from comparison data."""
    # For now, we'll use a simplified approach and just regenerate from the improved text
    # In a full implementation, we would parse the improved sections back into structured data
    
    # Use the current parsed resume as base and update with improved content where possible
    updated_resume = st.session_state.parsed_resume
    
    # TODO: In a full implementation, we would:
    # 1. Parse improved sections back into structured resume components
    # 2. Update the parsed resume with the new data
    # 3. Maintain proper data structure integrity
    
    # For now, trigger a LaTeX regeneration with the current parsed resume
    # The improvements will be reflected when the user exports or views the updated resume
    
    return updated_resume

def show_detailed_critique():
    """Show detailed resume critique using AI-parsed data."""
    try:
        with st.spinner("📊 Analyzing resume in detail using smartest AI parsing..."):
            # Use the AI-parsed resume data if available
            if st.session_state.parsed_resume:
                st.success("🤖 Using AI-parsed structured resume data for comprehensive critique!")
                
                # Update critique service with AI client if available
                if st.session_state.openrouter_client:
                    st.session_state.critique_service.openrouter_client = st.session_state.openrouter_client
                
                # Generate critique using the structured parsed resume data instead of raw analysis
                critique = st.session_state.critique_service.critique_parsed_resume(
                    st.session_state.parsed_resume,
                    st.session_state.tex_content
                )
            else:
                st.warning("⚠️ AI-parsed resume data not available. Falling back to basic analysis.")
                
                # Update critique service with AI client if available
                if st.session_state.openrouter_client:
                    st.session_state.critique_service.openrouter_client = st.session_state.openrouter_client
                
                # Generate critique using basic analysis data
                critique = st.session_state.critique_service.critique_resume(
                    st.session_state.analysis_data,
                    st.session_state.tex_content
                )
            
            # Display critique in a modal-like expander
            with st.expander("📊 **DETAILED RESUME CRITIQUE REPORT**", expanded=True):
                
                # Overall scores
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("Overall Score", f"{critique.overall_score}/100", 
                             delta=None if critique.overall_score >= 70 else f"{70-critique.overall_score} to target")
                
                with col2:
                    st.metric("ATS Score", f"{critique.ats_score}/100")
                
                with col3:
                    st.metric("Readability", f"{critique.readability_score}/100")
                
                with col4:
                    st.metric("Impact Score", f"{critique.impact_score}/100")
                
                # Summary
                st.markdown("### 📝 Executive Summary")
                st.markdown(critique.summary)
                
                # Top priorities
                if critique.top_priorities:
                    st.markdown("### 🎯 Top Priority Improvements")
                    for i, priority in enumerate(critique.top_priorities, 1):
                        st.markdown(f"**{i}.** {priority}")
                
                # Section analysis
                st.markdown("### 📋 Section-by-Section Analysis")
                
                for section_critique in critique.section_critiques:
                    with st.container():
                        st.markdown(f"#### {section_critique.section_name}")
                        
                        # Score and progress bar
                        score_col, bar_col = st.columns([1, 3])
                        with score_col:
                            st.metric("Score", f"{section_critique.score}/10")
                        with bar_col:
                            st.progress(section_critique.score / 10)
                        
                        # Create tabs for different feedback types
                        if section_critique.strengths or section_critique.weaknesses or section_critique.suggestions:
                            tabs = []
                            tab_names = []
                            
                            if section_critique.strengths:
                                tab_names.append("✅ Strengths")
                            if section_critique.weaknesses:
                                tab_names.append("⚠️ Issues")
                            if section_critique.suggestions:
                                tab_names.append("💡 Suggestions")
                            if section_critique.missing_elements:
                                tab_names.append("❌ Missing")
                            
                            if tab_names:
                                tabs = st.tabs(tab_names)
                                tab_index = 0
                                
                                if section_critique.strengths:
                                    with tabs[tab_index]:
                                        for strength in section_critique.strengths:
                                            st.success(strength)
                                    tab_index += 1
                                
                                if section_critique.weaknesses:
                                    with tabs[tab_index]:
                                        for weakness in section_critique.weaknesses:
                                            st.warning(weakness)
                                    tab_index += 1
                                
                                if section_critique.suggestions:
                                    with tabs[tab_index]:
                                        for suggestion in section_critique.suggestions:
                                            st.info(suggestion)
                                    tab_index += 1
                                
                                if section_critique.missing_elements:
                                    with tabs[tab_index]:
                                        for missing in section_critique.missing_elements:
                                            st.error(f"Missing: {missing}")
                        
                        st.markdown("---")
                
                # Generate AI enhancement if available
                if st.session_state.openrouter_client:
                    st.markdown("### 🤖 AI Enhancement Recommendations")
                    if st.button("🚀 Get AI Recommendations", use_container_width=True):
                        get_ai_enhancement_recommendations(critique)
                        
    except Exception as e:
        st.error(f"❌ Error generating critique: {str(e)}")
        logger.error(f"Critique generation error: {e}")

def get_ai_enhancement_recommendations(critique):
    """Get AI-powered enhancement recommendations."""
    try:
        with st.spinner("🤖 Generating AI enhancement recommendations..."):
            
            # Create a comprehensive prompt for AI analysis
            prompt = f"""
            Based on this resume critique analysis, provide specific, actionable recommendations for improvement:
            
            Overall Score: {critique.overall_score}/100
            ATS Score: {critique.ats_score}/100
            Top Issues: {'; '.join(critique.top_priorities[:3])}
            
            Current LaTeX Resume:
            {st.session_state.tex_content[:2000]}...
            
            Please provide:
            1. 3-5 specific improvements to make immediately
            2. Example rewrites for weak bullet points
            3. Suggestions for better ATS optimization
            4. Recommended sections to add or restructure
            
            Be specific and actionable. Focus on the highest-impact changes.
            """
            
            recommendations = st.session_state.openrouter_client._make_request(prompt, max_tokens=1500)
            
            if recommendations and not recommendations.startswith("Error:"):
                st.markdown("#### 🎯 AI Recommendations")
                st.markdown(recommendations)
                
                # Option to apply AI improvements
                if st.button("✨ Apply AI Improvements to Resume", type="primary"):
                    apply_ai_improvements(recommendations)
            else:
                st.error("❌ Failed to generate AI recommendations")
                
    except Exception as e:
        st.error(f"❌ Error getting AI recommendations: {str(e)}")

def apply_ai_improvements(recommendations):
    """Apply AI-generated improvements to the resume."""
    try:
        with st.spinner("✨ Applying AI improvements..."):
            
            improvement_prompt = f"""
            Based on these recommendations, improve this LaTeX resume:
            
            Recommendations:
            {recommendations}
            
            Current Resume:
            {st.session_state.tex_content}
            
            Return the improved LaTeX code incorporating the recommendations. 
            Focus on:
            - Better bullet points with quantifiable results
            - Improved ATS optimization
            - Better section organization
            - More impactful language
            
            Return ONLY the improved LaTeX code.
            """
            
            improved_latex = st.session_state.openrouter_client._make_request(improvement_prompt, max_tokens=3000)
            
            if improved_latex and not improved_latex.startswith("Error:"):
                # Clean up the response
                if improved_latex.startswith("```latex"):
                    improved_latex = improved_latex.replace("```latex", "").replace("```", "").strip()
                
                st.session_state.tex_content = improved_latex
                st.success("✅ AI improvements applied! Check the LaTeX code tab to see changes.")
                st.rerun()
            else:
                st.error("❌ Failed to apply improvements")
                
    except Exception as e:
        st.error(f"❌ Error applying improvements: {str(e)}")

def regenerate_latex_from_parsed_data():
    """Regenerate LaTeX from the current parsed resume data."""
    try:
        with st.spinner("🔄 Regenerating LaTeX from parsed resume data..."):
            if st.session_state.parsed_resume:
                # Get detected language for better formatting
                sample_text = ""
                if st.session_state.analysis_data:
                    for section in st.session_state.analysis_data.get('sections', []):
                        for block in section.get('content', [])[:5]:
                            sample_text += block.get('text', '') + " "
                            if len(sample_text) > 200:
                                break
                        if len(sample_text) > 200:
                            break
                
                detected_lang = "English"
                if sample_text and hasattr(st.session_state.advanced_parser, '_detect_resume_language'):
                    detected_lang = st.session_state.advanced_parser._detect_resume_language(sample_text)
                
                # Generate new LaTeX
                tex_content, cls_content = st.session_state.smart_latex_generator.generate_from_parsed_resume(
                    st.session_state.parsed_resume, 
                    detected_lang
                )
                
                # Update session state
                st.session_state.tex_content = tex_content
                st.session_state.cls_content = cls_content
                
                st.success("✅ LaTeX regenerated from structured resume data!")
                st.rerun()
            else:
                st.error("❌ No parsed resume data available. Please analyze a resume first.")
                
    except Exception as e:
        st.error(f"❌ Error regenerating LaTeX: {str(e)}")
        logger.error(f"LaTeX regeneration error: {e}")

def display_pdf_preview():
    """Compile and download PDF without preview display."""
    st.markdown("### 📥 PDF Download")
    
    if st.button("📄 Compile & Download PDF", type="primary", use_container_width=True):
        with st.spinner("🔄 Compiling LaTeX to PDF..."):
            success, message, pdf_bytes = st.session_state.preview_service.compile_and_download(
                st.session_state.tex_content,
                st.session_state.cls_content,
                f"resume_{st.session_state.uploaded_file_name.split('.')[0]}"
            )
            
            if success and pdf_bytes:
                st.success("✅ PDF compiled successfully!")
                
                st.download_button(
                    label="📥 Download PDF",
                    data=pdf_bytes,
                    file_name=f"resume_{st.session_state.uploaded_file_name.split('.')[0]}.pdf",
                    mime="application/pdf",
                    type="primary",
                    use_container_width=True
                )
                
            else:
                st.error(f"❌ Compilation failed: {message}")
                
                # Show LaTeX installation help if needed
                latex_status = st.session_state.preview_service.compiler.get_latex_installation_status()
                
                if not latex_status['latex_available']:
                    st.warning("⚠️ LaTeX not installed.")
                    
                    with st.expander("📖 LaTeX Installation Guide"):
                        st.markdown(latex_status['installation_guide'])
                        
                        st.markdown("#### Available Engines:")
                        for engine, available in latex_status['engines'].items():
                            status = "✅" if available else "❌"
                            st.write(f"{status} {engine}")
    
    # Compact LaTeX status
    latex_status = st.session_state.preview_service.compiler.get_latex_installation_status()
    
    if latex_status['latex_available']:
        st.info(f"✅ LaTeX ready ({latex_status['recommended_engine']})")
    else:
        st.warning("⚠️ LaTeX not installed - compilation unavailable")

def display_download_options():
    """Display download options including PDF compilation."""
    st.markdown("### 📦 Download Options")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 LaTeX Files")
        
        # Individual file downloads
        st.download_button(
            label="📥 Download resume.tex",
            data=st.session_state.tex_content,
            file_name="resume.tex",
            mime="text/plain",
            use_container_width=True
        )
        
        st.download_button(
            label="📥 Download resume.cls",
            data=st.session_state.cls_content,
            file_name="resume.cls", 
            mime="text/plain",
            use_container_width=True
        )
        
        # ZIP package
        if st.button("📦 Create ZIP Package", use_container_width=True):
            create_and_download_zip()
    
    with col2:
        st.markdown("#### 📄 Compiled PDF")
        
        if st.button("🚀 Compile to PDF", type="primary", use_container_width=True):
            compile_and_download_pdf()
        
        st.markdown("#### 🎯 Job Adaptation")
        st.info("💡 Paste a job description below to automatically adapt your resume for better ATS matching!")
        
        job_description = st.text_area(
            "Job Description",
            placeholder="""Example:
We are looking for a Senior Data Engineer with:
- 5+ years Python experience
- AWS, Docker, Kubernetes knowledge
- Machine learning pipeline development
- Real-time data processing with Kafka
- Experience with Apache Airflow

Paste the actual job description here...""",
            height=150,
            help="Paste the complete job description. The AI will analyze requirements and adapt your resume accordingly."
        )
        
        if job_description and job_description.strip():
            adaptation_level = st.select_slider(
                "Adaptation Level",
                options=["light", "moderate", "aggressive"],
                value="moderate",
                help="Light: Minor emphasis changes, Moderate: Reorder and emphasize, Aggressive: Significant restructuring"
            )
            
            if st.button("🎯 Adapt Resume to Job", type="primary", use_container_width=True):
                adapt_resume_to_job(job_description, adaptation_level)
        else:
            st.info("👆 Paste a job description above to unlock AI job adaptation")

def compile_and_download_pdf():
    """Compile LaTeX to PDF and offer download."""
    with st.spinner("🔄 Compiling to PDF..."):
        success, message, pdf_bytes = st.session_state.preview_service.compile_and_download(
            st.session_state.tex_content,
            st.session_state.cls_content,
            f"resume_{st.session_state.uploaded_file_name.split('.')[0]}"
        )
        
        if success and pdf_bytes:
            st.success("✅ PDF compiled successfully!")
            
            st.download_button(
                label="📥 Download PDF",
                data=pdf_bytes,
                file_name=f"resume_{st.session_state.uploaded_file_name.split('.')[0]}.pdf",
                mime="application/pdf",
                type="primary"
            )
        else:
            st.error(f"❌ Compilation failed: {message}")

def use_enhanced_generator():
    """Use the enhanced LaTeX generator for better results."""
    with st.spinner("🔄 Generating enhanced LaTeX..."):
        try:
            # Convert sections to a compatible format
            sections_data = st.session_state.analysis_data.get('sections', [])
            
            # Create a simpler enhanced version for now
            if sections_data:
                # Use AI to enhance the current LaTeX instead
                if st.session_state.openrouter_client:
                    prompt = f"""
                    Enhance this LaTeX resume to be more professional and complete:
                    
                    Current LaTeX:
                    {st.session_state.tex_content}
                    
                    Make it more comprehensive, professional, and visually appealing while maintaining the AltaCV style.
                    Return only the improved LaTeX code.
                    """
                    
                    enhanced_tex = st.session_state.openrouter_client._make_request(prompt, max_tokens=3000)
                    
                    if enhanced_tex and not enhanced_tex.startswith("Error:"):
                        # Clean up response
                        if enhanced_tex.startswith("```latex"):
                            enhanced_tex = enhanced_tex.replace("```latex", "").replace("```", "").strip()
                        
                        st.session_state.tex_content = enhanced_tex
                        st.success("✅ Enhanced LaTeX generated using AI!")
                        st.rerun()
                    else:
                        st.error("❌ AI enhancement failed. Please try the 'Improve LaTeX Code' button instead.")
                else:
                    st.error("❌ Please enter your OpenRouter API key to use enhanced generation.")
            else:
                st.error("❌ No analysis data available for enhancement.")
                
        except Exception as e:
            st.error(f"❌ Enhanced generation failed: {str(e)}")
            logger.error(f"Enhanced generation error: {e}")

def adapt_resume_to_job(job_description: str, adaptation_level: str = "moderate"):
    """Adapt resume to specific job description with comparison interface."""
    if not st.session_state.openrouter_client:
        st.error("❌ Please enter your OpenRouter API key for job adaptation.")
        return
    
    if not st.session_state.parsed_resume or not st.session_state.original_parsed_resume:
        st.error("❌ No parsed resume data available for adaptation.")
        return
    
    with st.spinner(f"🎯 Adapting resume to job description ({adaptation_level} level)..."):
        try:
            # Use the improvement service to adapt the resume content
            improvement_service = ResumeImprovementService(st.session_state.openrouter_client)
            
            # Convert parsed resume to text for adaptation
            original_text = _convert_parsed_resume_to_text(st.session_state.original_parsed_resume)
            
            # Create job adaptation prompt
            adaptation_prompt = f"""
Adapt this resume content to better match the following job description.

Job Description:
{job_description}

Current Resume:
{original_text}

Instructions for {adaptation_level} adaptation:
1. Keep all factual information accurate
2. Emphasize relevant skills and experiences that match the job requirements
3. Use keywords from the job description where appropriate
4. Restructure bullet points to highlight relevant achievements
5. Preserve the original language and maintain professional tone
6. Focus on quantifiable results that align with job requirements

Return the adapted resume content maintaining the same structure:
"""
            
            # Get adapted content using the AI client directly
            adapted_content = st.session_state.openrouter_client._make_request(adaptation_prompt, max_tokens=2000)
            
            if adapted_content and not adapted_content.startswith("Error:"):
                # Create mock analysis data from adapted content
                adapted_analysis_data = {
                    'sections': [
                        {
                            'section_type': 'other',
                            'title': 'Job Adapted Content',
                            'content': [{'text': adapted_content, 'font_size': 12, 'is_bold': False}]
                        }
                    ],
                    'text_blocks': [{'text': adapted_content}]
                }
                
                # Parse adapted content
                st.session_state.advanced_parser.openrouter_client = st.session_state.openrouter_client
                adapted_parsed_resume = st.session_state.advanced_parser.parse_resume(adapted_analysis_data)
                
                # Create comparison interface
                comparison_service = ResumeEnhancementComparison(st.session_state.openrouter_client)
                comparisons = comparison_service.create_comparison_from_parsed_resumes(
                    st.session_state.original_parsed_resume,
                    adapted_parsed_resume
                )
                
                # Store comparison data
                st.session_state.enhancement_comparison = comparison_service
                st.session_state.parsed_resume = sanitize_data(adapted_parsed_resume)  # Update current resume
                st.session_state.parsed_resume_data = adapted_parsed_resume  # Update structured data for ATS improvements
                
                # Regenerate LaTeX from adapted content
                tex_content, cls_content = st.session_state.smart_latex_generator.generate_from_parsed_resume(adapted_parsed_resume)
                st.session_state.tex_content = tex_content
                st.session_state.cls_content = cls_content
                
                st.success("✅ Resume adapted to job description!")
                
                # Show adaptation summary
                with st.expander("📊 Adaptation Summary"):
                    st.markdown(f"**Adaptation Level:** {adaptation_level.title()}")
                    st.markdown(f"**Job Focus:** Emphasized skills and experiences matching the job requirements")
                    st.markdown("**Changes Made:** Keywords optimized, bullet points restructured, relevant achievements highlighted")
                
                # Debug info
                st.info(f"Comparison sections created: {len(comparisons) if comparisons else 0}")
                
                # Button to go to comparison page
                if st.button("🔄 View Detailed Before/After Comparison", type="primary", key="job_adapt_comparison"):
                    if st.session_state.enhancement_comparison and st.session_state.enhancement_comparison.comparisons:
                        st.session_state.show_comparison_page = True
                        st.rerun()
                    else:
                        st.error("❌ No comparison data available. Please try the adaptation again.")
                    
            else:
                st.error(f"❌ Job adaptation failed: {adapted_content}")
                
        except Exception as e:
            st.error(f"❌ Job adaptation error: {str(e)}")
            logger.error(f"Job adaptation error: {e}")

def create_and_download_zip():
    """Create and offer ZIP download with both LaTeX files."""
    try:
        # Create a ZIP file in memory
        import io
        zip_buffer = io.BytesIO()
        
        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add .tex file
            zip_file.writestr("resume.tex", st.session_state.tex_content)
            # Add .cls file
            zip_file.writestr("resume.cls", st.session_state.cls_content)
            
            # Add README with instructions
            readme_content = """# Resume LaTeX Files

This package contains your generated LaTeX resume files.

## Files included:
- resume.tex - Main resume document
- resume.cls - Custom resume class with styling

## How to compile:
1. Ensure you have LaTeX installed (TeX Live, MiKTeX, etc.)
2. Place both files in the same directory
3. Run: pdflatex resume.tex
4. If needed, run it twice for proper formatting

## Requirements:
- LaTeX distribution with standard packages
- The resume.cls file must be in the same directory as resume.tex

## Troubleshooting:
- If you get package errors, install missing LaTeX packages
- Ensure both files are in the same directory
- Check that file permissions allow reading

Generated by Resume to LaTeX Generator
"""
            zip_file.writestr("README.md", readme_content)
        
        zip_buffer.seek(0)
        
        # Offer download
        st.download_button(
            label="📥 Download Complete Package (ZIP)",
            data=zip_buffer.getvalue(),
            file_name=f"resume_latex_{st.session_state.uploaded_file_name.split('.')[0]}.zip",
            mime="application/zip"
        )
        
        st.success("✅ ZIP package ready for download!")
        
    except Exception as e:
        st.error(f"❌ Error creating ZIP package: {str(e)}")

def create_footer():
    """Create the application footer."""
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #7f8c8d; padding: 2rem 0;">
        <p>Built with ❤️ using Streamlit • Resume to LaTeX Generator</p>
        <p>Transform your resume into professional LaTeX code with AI assistance</p>
    </div>
    """, unsafe_allow_html=True)

def auto_generate_html_preview():
    """Auto-generate HTML preview when resume is first loaded."""
    logger.info(f"🔄 AUTO_GENERATE_HTML_PREVIEW STARTED")
    try:
        if not st.session_state.parsed_resume:
            logger.warning(f"⚠️ No parsed resume available for auto-generation")
            return
            
        logger.info(f"📋 Converting parsed resume to dict format")
        # Convert parsed resume to dict format
        resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
        
        logger.info(f"📊 Resume dict keys: {list(resume_dict.keys()) if isinstance(resume_dict, dict) else 'Not dict'}")
        
        # Check if this is role-adapted data
        if resume_dict.get('_role_adapted'):
            logger.info(f"🎯 AUTO-PREVIEW: Role-adapted data detected: {resume_dict['_role_adapted']}")
        
        # Generate with default settings (keep original layout by default)
        logger.info(f"🏭 Calling generate_original_format_html for auto-preview")
        html_result = st.session_state.html_generator.generate_original_format_html(
            resume_dict,
            original_analysis=getattr(st.session_state, 'resume_analysis', None),
            enhancement_level="minimal",
            palette_id="professional_blue"
        )
        
        logger.info(f"📊 AUTO-PREVIEW HTML result received:")
        logger.info(f"   📋 Result type: {type(html_result)}")
        logger.info(f"   📋 Result keys: {list(html_result.keys()) if isinstance(html_result, dict) else 'Not dict'}")
        
        if isinstance(html_result, dict):
            html_content = html_result.get('html', '')
            css_content = html_result.get('css', '')
            logger.info(f"   📄 HTML length: {len(html_content)} chars")
            logger.info(f"   🎨 CSS length: {len(css_content)} chars")
            logger.debug(f"   📄 HTML sample: {html_content[:100]}")
        
        st.session_state.html_resume_content = html_result
        st.session_state.keep_original_layout = True  # Default to original layout
        
        logger.info(f"✅ AUTO_GENERATE_HTML_PREVIEW COMPLETED - stored in session_state.html_resume_content")
        
    except Exception as e:
        logger.error(f"❌ Auto HTML generation error: {e}")
        logger.error(f"📊 Auto-preview error traceback:", exc_info=True)

def generate_html_with_loading(template_changed=False, palette_changed=False, role_changed=False):
    """Generate HTML with loading animation for real-time updates."""
    if not st.session_state.parsed_resume:
        return
    
    # Show loading animation
    loading_placeholder = st.empty()
    with loading_placeholder.container():
        if template_changed:
            st.info("🎨 Switching template...")
        elif palette_changed:
            st.info("🎨 Applying new colors...")
        elif role_changed:
            st.info("🤖 Adapting content for target role...")
        else:
            st.info("🎨 Generating preview...")
        
        # Add progress bar for visual feedback
        progress_bar = st.progress(0)
        for i in range(100):
            progress_bar.progress(i + 1)
            if i < 50:
                continue  # Small delay for visual effect
    
    try:
        # Convert parsed resume to dict format
        resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
        
        # Apply role adaptation if selected
        target_role = getattr(st.session_state, 'target_role', "None (Original)")
        logger.info(f"🎯 Checking role adaptation - Target role: {target_role}")
        
        if target_role != "None (Original)":
            logger.info(f"📝 Starting role adaptation for: {target_role}")
            logger.info(f"🔗 HTML generator OpenRouter client available: {bool(st.session_state.html_generator.openrouter_client)}")
            
            original_keys = list(resume_dict.keys())
            resume_dict = st.session_state.html_generator.adapt_resume_for_role(resume_dict, target_role)
            
            # Check if adaptation was successful
            if resume_dict.get('_role_adapted'):
                logger.info(f"✅ Role adaptation successful for: {target_role}")
            else:
                logger.warning(f"⚠️ Role adaptation failed or returned original data for: {target_role}")
                logger.info(f"📊 Original keys: {original_keys}")
                logger.info(f"📊 Returned keys: {list(resume_dict.keys())}")
        
        # Check if we should keep original layout
        if hasattr(st.session_state, 'keep_original_layout') and st.session_state.keep_original_layout:
            # Get enhancement level from session state
            enhancement_level = "minimal"
            if hasattr(st.session_state, 'original_enhancement_level'):
                level_mapping = {
                    "Minimal (Keep exact layout)": "minimal",
                    "Enhanced (Improve readability)": "enhanced", 
                    "Modernized (Add subtle styling)": "modernized"
                }
                enhancement_level = level_mapping.get(st.session_state.original_enhancement_level, "minimal")
            
            # Generate HTML with original layout preserved
            html_result = st.session_state.html_generator.generate_original_format_html(
                resume_dict,
                original_analysis=getattr(st.session_state, 'resume_analysis', None),
                enhancement_level=enhancement_level,
                palette_id=st.session_state.selected_palette
            )
        else:
            # Generate HTML resume with templates
            html_result = st.session_state.html_generator.generate_resume_html(
                resume_dict,
                st.session_state.selected_template,
                st.session_state.selected_palette
            )
        
        st.session_state.html_resume_content = html_result
        
        # Log session state update with detailed information
        logger.info(f"💾 UPDATING SESSION STATE - st.session_state.html_resume_content")
        logger.info(f"📄 HTML result keys: {list(html_result.keys()) if isinstance(html_result, dict) else 'Not a dict'}")
        
        # Log old vs new content for comparison
        if hasattr(st.session_state, 'html_resume_content') and st.session_state.html_resume_content:
            old_content = st.session_state.html_resume_content
            if isinstance(old_content, dict):
                old_html = old_content.get('html', '')
                logger.info(f"📊 REPLACING old HTML content ({len(old_html)} chars)")
        
        if isinstance(html_result, dict):
            html_content = html_result.get('html', '')
            css_content = html_result.get('css', '')
            logger.info(f"📝 NEW HTML content length: {len(html_content)} chars")
            logger.info(f"🎨 NEW CSS content length: {len(css_content)} chars")
            
            # Log preview content sample for debugging
            html_sample = html_content[:300] if html_content else "No HTML content"
            logger.debug(f"📄 NEW HTML preview sample: {html_sample}")
            
            # If this is a role-adapted resume, check if the adapted content made it through
            if target_role != "None (Original)" and resume_dict.get('_role_adapted'):
                logger.info(f"🎯 SESSION STATE UPDATE - Role-adapted content for: {target_role}")
                # Check for specific role-adapted job titles in the HTML
                if 'software engineer' in html_content.lower() and target_role == "Software Engineer":
                    logger.info(f"✅ SESSION STATE: 'Software Engineer' job title FOUND in new HTML content")
                elif 'data engineer' in html_content.lower():
                    logger.error(f"❌ SESSION STATE: Still shows 'Data Engineer' - role adaptation failed to reach HTML")
                else:
                    logger.warning(f"⚠️ SESSION STATE: Role-adapted job title may not be in new HTML content")
                    
                # Check for role-adapted summary
                adapted_summary = resume_dict.get('professional_summary', '')
                if adapted_summary and len(adapted_summary) > 50:
                    summary_sample = adapted_summary[:50].lower()
                    if summary_sample in html_content.lower():
                        logger.info(f"✅ SESSION STATE: Adapted summary FOUND in new HTML content")
                    else:
                        logger.error(f"❌ SESSION STATE: Adapted summary NOT FOUND in new HTML content")
                        logger.debug(f"Looking for summary: {summary_sample}...")
        
        logger.info(f"✅ SESSION STATE UPDATE COMPLETED - html_resume_content now contains new data")
        
        # Show section validation feedback to user
        if getattr(st.session_state, 'keep_original_template', False) != True:  # Only for templates, not original format
            validation_summary = st.session_state.html_generator.get_section_validation_summary(
                resume_dict, 
                st.session_state.selected_template
            )
            
            # Display validation info
            if validation_summary['total_sections'] > 0:
                sections_text = ", ".join([f"{name} ({count})" for name, count in validation_summary['available_sections'].items()])
                st.success(f"✅ Template populated with {validation_summary['total_sections']} sections: {sections_text}")
            
            # Log validation details
            logger.info(f"📋 Section validation: {validation_summary}")
        
        # Debug: Log if adapted content made it to the HTML
        if target_role != "None (Original)" and resume_dict.get('_role_adapted'):
            logger.info(f"🔍 Role-adapted HTML content length: {len(html_result.get('html', ''))}")
            # Check if adapted content is in the HTML with comprehensive keyword detection
            html_content = html_result.get('html', '').lower()
            
            # Define role-specific keywords to check
            role_keywords = {
                "Software Engineer": ["software", "programming", "development", "engineer", "coding", "algorithm"],
                "Data Scientist": ["data", "analysis", "machine learning", "modeling", "research", "analytics"],
                "Frontend Developer": ["frontend", "ui", "javascript", "react", "html", "css"],
                "Backend Developer": ["backend", "api", "server", "database", "microservices"],
                "DevOps Engineer": ["devops", "infrastructure", "deployment", "kubernetes", "docker"],
                "Product Manager": ["product", "strategy", "roadmap", "stakeholder", "requirements"]
            }
            
            keywords_to_check = role_keywords.get(target_role, ["programming", "software", "development"])
            found_keywords = [kw for kw in keywords_to_check if kw in html_content]
            
            if found_keywords:
                logger.info(f"✅ Adapted keywords found in HTML: {found_keywords}")
            else:
                logger.warning(f"⚠️ No adapted keywords found in HTML. Checked: {keywords_to_check}")
                # Log a sample of the HTML content for debugging
                html_sample = html_content[:500] if html_content else "No HTML content"
                logger.debug(f"HTML content sample: {html_sample}")
                logger.debug(f"Resume dict has '_role_adapted': {resume_dict.get('_role_adapted', False)}")
        
        # Show user feedback about role adaptation (only if successful)
        if target_role != "None (Original)" and resume_dict.get('_role_adapted'):
            st.success(f"🎯 Resume content successfully adapted for **{target_role}** position!")
            st.info("💡 Your experiences and skills have been reframed to highlight relevance to the target role while keeping all information accurate.")
        elif target_role != "None (Original)":
            # Log the failure but don't clutter UI - just show a subtle notice
            logger.warning(f"Role adaptation failed for {target_role}")
            st.info("🔄 Processing role adaptation - if issues persist, check your OpenRouter API key in the sidebar.")
        
        # Show user feedback about template AI adaptation
        if html_result.get('ai_adapted', False):
            st.success("🎨 Template generated with AI-powered adaptation for optimal content matching!")
            st.info("💡 Your resume data has been intelligently adapted to match this template's style and requirements.")
        
        # Clear loading animation
        loading_placeholder.empty()
        
    except Exception as e:
        loading_placeholder.empty()
        st.error(f"❌ Error generating HTML resume: {str(e)}")
        logger.error(f"HTML generation error: {e}")
        logger.error(f"HTML generation error details: {type(e).__name__}: {str(e)}")
        import traceback
        logger.error(f"HTML generation traceback: {traceback.format_exc()}")

def display_integrated_template_matching():
    """Display integrated template matching interface within the HTML builder."""
    st.markdown("### 🎨 Template Matching & Layout Improvement")
    
    # Check if we have the necessary components
    if not hasattr(st.session_state, 'original_file_data') or not st.session_state.original_file_data:
        st.warning("⚠️ Original resume PDF required for template matching. Please upload your resume in the main interface.")
        return
        
    if not st.session_state.html_resume_content:
        st.warning("⚠️ Generated HTML resume required. Please generate a resume first.")
        return
    
    # Check for API key and OpenRouter client early
    if not getattr(st.session_state, 'openrouter_api_key', ''):
        st.warning("⚠️ OpenRouter API key required for template matching. Please add your API key in the sidebar.")
        return
    
    if not hasattr(st.session_state, 'openrouter_client') or not st.session_state.openrouter_client:
        st.warning("⚠️ No AI model connected. Please select a model in the sidebar settings.")
        return
    
    # Template reference options
    st.markdown("#### 📋 Template Reference")
    template_option = st.radio(
        "Choose template reference:",
        ["Use Original PDF as Template", "Upload Custom Template Image"],
        help="Select what to use as the target template for matching"
    )
    
    target_template_image = None
    
    if template_option == "Upload Custom Template Image":
        uploaded_template = st.file_uploader(
            "Upload template image (JPG, PNG, PDF)",
            type=['jpg', 'jpeg', 'png', 'pdf'],
            help="Upload an image or PDF of the template layout you want to match"
        )
        
        if uploaded_template:
            try:
                if uploaded_template.type == "application/pdf":
                    # Convert PDF template to image
                    from image_converter import image_converter
                    target_template_image = image_converter.pdf_to_image(uploaded_template.getvalue(), dpi=200, page_num=0)
                else:
                    # Use uploaded image directly
                    target_template_image = uploaded_template.getvalue()
                    
                if target_template_image:
                    st.success("✅ Template image loaded successfully")
                    # Show preview of template
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col2:
                        st.image(target_template_image, caption="Template Reference", use_column_width=True)
            except Exception as e:
                st.error(f"❌ Failed to process template image: {e}")
                return
    else:
        # Use original PDF - we'll extract it in the matching process
        st.info("✅ Will use your original resume PDF as template reference")
        target_template_image = "original_pdf"
    
    # Get the current AI model and client
    selected_model = st.session_state.openrouter_client.model
    client = st.session_state.openrouter_client
    
    # Show current AI model being used for multimodal tasks
    st.markdown("#### 🤖 AI Model (Multimodal)")
    
    try:
        # Get model info from the model manager
        all_models = client.get_available_models()
        selected_model_info = None
        for model in all_models:
            if model.get('id') == selected_model:
                selected_model_info = model
                break
        
        if selected_model_info:
            model_name = selected_model_info.get('name', selected_model)
            provider = selected_model_info.get('provider', 'Unknown')
            pricing = selected_model_info.get('pricing', {}).get('prompt', 0)
            try:
                pricing_float = float(pricing) if pricing else 0
                is_free = pricing_float == 0
                cost_info = "🆓 Free" if is_free else f"💰 ${pricing_float:.4f}/1k tokens"
            except (ValueError, TypeError):
                cost_info = "💰 Paid model"
            
            st.info(f"**Using:** {model_name} ({provider}) - {cost_info}")
        else:
            st.info(f"**Using:** {selected_model}")
        
        st.caption("💡 Change model in sidebar settings")
        
    except Exception as e:
        st.warning(f"⚠️ Could not load model info: {str(e)}")
        st.info(f"**Using:** {selected_model}")
    
    st.markdown("---")
    
    # Template matching settings
    st.markdown("#### ⚙️ Matching Settings")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        max_iterations = st.slider("Max Iterations", 1, 10, 5, 
                                 help="Maximum number of improvement iterations")
    with col2:
        target_similarity = st.slider("Target Similarity %", 70, 95, 85,
                                    help="Stop when this similarity score is reached")
    with col3:
        min_improvement = st.slider("Min Improvement %", 1, 10, 5,
                                  help="Stop if improvement per iteration is less than this")
    
    # Template matching button
    st.markdown("---")
    
    # Status display
    if 'template_matching_in_progress' not in st.session_state:
        st.session_state.template_matching_in_progress = False
    
    if not st.session_state.template_matching_in_progress:
        if st.button("🚀 Start Template Matching", type="primary", use_container_width=True):
            st.session_state.template_matching_in_progress = True
            
            # Run template matching
            with st.spinner("🔄 Analyzing template and improving layout..."):
                try:
                    # Initialize template matching system with properly selected model
                    from template_matcher import TemplateMatchingSystem
                    template_matcher = TemplateMatchingSystem(
                        openrouter_client=client,
                        use_ocr=False,
                        vision_model=selected_model  # This already uses the correct selected model from sidebar
                    )
                    
                    # Get resume data
                    resume_data = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
                    
                    # Determine target image
                    if target_template_image == "original_pdf":
                        target_pdf_bytes = st.session_state.original_file_data
                    else:
                        # For uploaded template, we'd need to create a mock PDF or handle differently
                        target_pdf_bytes = st.session_state.original_file_data
                    
                    # Run matching process
                    results = template_matcher.match_template(
                        original_pdf_bytes=target_pdf_bytes,
                        resume_data=resume_data,
                        initial_template=st.session_state.selected_template,
                        max_iterations=max_iterations,
                        resume_name="current_resume"
                    )
                    
                    # Update HTML content with improved version
                    if results.get('success') and results.get('final_html'):
                        # Parse the improved HTML
                        improved_html = results['final_html']
                        
                        # Extract CSS and HTML parts (simple extraction)
                        if '<style>' in improved_html and '</style>' in improved_html:
                            css_start = improved_html.find('<style>') + 7
                            css_end = improved_html.find('</style>')
                            css_content = improved_html[css_start:css_end]
                            
                            # Update session state
                            st.session_state.html_resume_content['css'] = css_content
                            st.session_state.html_resume_content['html'] = improved_html
                            
                            # Store matching results
                            st.session_state.template_matching_results = results
                            
                            st.success(f"✅ Template matching completed! Final similarity: {results['final_score']}%")
                            
                            # Show iteration results
                            if results.get('iterations'):
                                st.markdown("#### 📊 Matching Progress")
                                iterations_data = []
                                for i, iteration in enumerate(results['iterations'], 1):
                                    iterations_data.append({
                                        'Iteration': i,
                                        'Similarity Score': f"{iteration.similarity_score}%"
                                    })
                                
                                st.dataframe(iterations_data, use_container_width=True)
                            
                            # Show the improved resume preview
                            st.markdown("#### 🎨 Improved Resume Preview")
                            st.info("📋 Your resume has been improved to match the original layout!")
                            
                            # Use the HTML preview component to show the result
                            try:
                                st.session_state.html_preview_component.show_preview(
                                    html_content=improved_html,
                                    height=600
                                )
                            except Exception as e:
                                st.error(f"Error showing preview: {e}")
                                # Fallback to basic HTML display
                                st.components.v1.html(improved_html, height=600, scrolling=True)
                                
                        else:
                            st.warning("⚠️ Template matching completed but couldn't extract CSS properly")
                            
                    else:
                        st.error(f"❌ Template matching failed: {results.get('error', 'Unknown error')}")
                        
                except Exception as e:
                    st.error(f"❌ Template matching error: {str(e)}")
                finally:
                    st.session_state.template_matching_in_progress = False
                    st.rerun()
    else:
        st.info("🔄 Template matching in progress...")
        if st.button("⏹️ Stop Matching", type="secondary"):
            st.session_state.template_matching_in_progress = False
            st.rerun()
        
    # Show previous results if available
    if 'template_matching_results' in st.session_state and st.session_state.template_matching_results:
        results = st.session_state.template_matching_results
        
        st.markdown("---")
        st.markdown("#### 📈 Previous Matching Results")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Final Score", f"{results.get('final_score', 0)}%")
        with col2:
            st.metric("Iterations", results.get('total_iterations', 0))
        with col3:
            target_reached = results.get('target_reached', False)
            st.metric("Target", "✅ Reached" if target_reached else "⚠️ Partial")
            
        # Option to view detailed results
        with st.expander("🔍 View Detailed Results", expanded=False):
            # Show summary metrics
            st.markdown("#### 📊 Summary")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Iterations", results.get('total_iterations', 0))
                st.metric("Vision Model Used", results.get('vision_model_used', 'Unknown'))
            with col2:
                st.metric("Final Score", f"{results.get('final_score', 0)}%")
                st.metric("Target Reached", "✅ Yes" if results.get('target_reached') else "❌ No")
            
            # Show iteration progress if available
            if results.get('iterations'):
                st.markdown("#### 📈 Iteration Progress")
                iteration_data = []
                for i, iteration in enumerate(results['iterations'], 1):
                    iteration_data.append({
                        'Iteration': i,
                        'Similarity Score': f"{iteration.similarity_score}%",
                        'Improvements Made': len(iteration.improvements_made) if hasattr(iteration, 'improvements_made') else 0
                    })
                st.dataframe(iteration_data, use_container_width=True)
            
            # Raw JSON in a separate expander for technical users
            with st.expander("🔧 Raw JSON Data (Technical)", expanded=False):
                st.json(results)

def display_template_matching_interface():
    """Display the advanced template matching interface using multimodal AI."""
    if not st.session_state.parsed_resume:
        st.info("👆 Please analyze a resume first to use template matching")
        return
    
    st.markdown("## 🎯 AI-Powered Template Matching")
    st.markdown("""
    This feature uses **advanced multimodal AI vision models** to analyze your original resume layout 
    and iteratively improve your generated resume to match the visual structure and formatting. 
    The AI compares images of both resumes and suggests improvements.
    """)
    
    # Template matching settings
    st.markdown("### ⚙️ Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # AI Model (Multimodal)
        st.markdown("#### 🤖 AI Model (Multimodal)")
        
        # Use the AI model already selected in the sidebar
        if hasattr(st.session_state, 'openrouter_client') and st.session_state.openrouter_client:
            selected_model = st.session_state.openrouter_client.model
            
            # Show currently selected model
            try:
                all_models = st.session_state.openrouter_client.get_available_models()
                model_info = None
                for model in all_models:
                    if model.get('id') == selected_model:
                        model_info = model
                        break
                
                if model_info:
                    model_name = model_info.get('name', selected_model)
                    provider = model_info.get('provider', 'Unknown')
                    pricing = model_info.get('pricing', {}).get('prompt', 0)
                    try:
                        pricing_float = float(pricing) if pricing else 0
                        is_free = pricing_float == 0
                        cost_info = "🆓 Free" if is_free else f"💰 ${pricing_float:.4f}/1K tokens"
                    except (ValueError, TypeError):
                        cost_info = "💰 Paid model"
                    
                    st.info(f"🤖 **Using:** {model_name} ({provider}) - {cost_info}")
                else:
                    st.info(f"🤖 **Using:** {selected_model}")
                st.caption("💡 Change model in the sidebar settings")
                
            except Exception as e:
                st.warning(f"⚠️ Model info unavailable: {str(e)}")
                st.info(f"🤖 **Using:** {selected_model}")
        else:
            st.warning("⚠️ No AI model connected. Please select a model in the sidebar settings.")
            selected_model = None
    
    with col2:
        st.markdown("#### 🎯 Matching Parameters")
        
        max_iterations = st.slider(
            "Max Iterations", 
            min_value=1, 
            max_value=10, 
            value=5,
            help="Maximum number of improvement iterations"
        )
        
        target_score = st.slider(
            "Target Score %", 
            min_value=50, 
            max_value=95, 
            value=85,
            help="Target similarity percentage to achieve"
        )
        
        min_improvement = st.slider(
            "Min Improvement %", 
            min_value=1, 
            max_value=10, 
            value=5,
            help="Minimum improvement required per iteration"
        )
        
        # API logging toggle
        st.markdown("#### 📊 Debugging")
        show_api_logs = st.checkbox(
            "🔍 Show API call logs", 
            value=False,
            help="Display real-time API calls and token usage (useful for debugging)"
        )
        st.session_state.show_api_logs = show_api_logs
    
    # Check if we have the original file
    original_file_data = getattr(st.session_state, 'original_file_data', None)
    if not original_file_data and hasattr(st.session_state, 'uploaded_file'):
        # Try to get from uploaded file if available
        try:
            st.session_state.uploaded_file.seek(0)
            original_file_data = st.session_state.uploaded_file.read()
        except:
            original_file_data = None
    
    if original_file_data and st.session_state.openrouter_client:
        
        # Template selection for starting point
        st.markdown("### 🎨 Starting Template")
        templates = st.session_state.html_generator.get_available_templates()
        template_options = {t["id"]: f"{t['name']} - {t['description']}" for t in templates}
        
        selected_template = st.selectbox(
            "Choose starting template:",
            options=list(template_options.keys()),
            format_func=lambda x: template_options[x],
            index=0
        )
        
        # Start template matching process
        if st.button("🚀 Start Template Matching", type="primary", use_container_width=True):
            
            # Initialize template matching system with the selected AI model from sidebar
            ai_model_to_use = st.session_state.openrouter_client.model
            st.session_state.template_matcher = TemplateMatchingSystem(
                st.session_state.openrouter_client,
                use_ocr=False,  # OCR disabled by default, using multimodal approach
                vision_model=ai_model_to_use
            )
            
            # Update settings
            st.session_state.template_matcher.max_iterations = max_iterations
            st.session_state.template_matcher.target_similarity_score = target_score
            st.session_state.template_matcher.min_improvement_threshold = min_improvement
            
            # Get resume name from uploaded file
            resume_name = getattr(st.session_state, 'uploaded_file_name', 'resume')
            if resume_name.endswith('.pdf'):
                resume_name = resume_name[:-4]  # Remove .pdf extension
            
            # Convert parsed resume to dict
            resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
            
            # Start matching process
            try:
                with st.spinner("🔄 Starting template matching process..."):
                    results = st.session_state.template_matcher.match_template(
                        original_pdf_bytes=original_file_data,
                        resume_data=resume_dict,
                        initial_template=selected_template,
                        max_iterations=max_iterations,
                        resume_name=resume_name
                    )
                
                # Store results in session state
                st.session_state.template_matching_results = results
                
                # Display results
                if results.get('success'):
                    st.success("✅ Template matching completed!")
                    
                    # Store the final HTML as the current resume
                    final_html = results.get('final_html', '')
                    st.session_state.html_resume_content = final_html
                    st.session_state.selected_template = selected_template
                    
                    # Dual preview system with apply confirmation
                    st.markdown("### 🎨 Template Matching Results")
                    st.info(f"📊 Final similarity score: {results.get('final_score', 0)}%")
                    
                    if final_html:
                        # Create two columns for dual preview
                        col1, col2 = st.columns([1, 1])
                        
                        with col1:
                            st.markdown('<div class="final-preview preview-container">', unsafe_allow_html=True)
                            st.markdown("#### 📄 Current Resume Preview")
                            try:
                                # Show current resume
                                current_html = st.session_state.html_resume_content
                                st.session_state.html_preview_component.show_preview(
                                    html_content=current_html,
                                    height=600
                                )
                            except Exception as e:
                                st.error(f"Error displaying current resume: {e}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        with col2:
                            st.markdown('<div class="template-preview preview-container">', unsafe_allow_html=True)
                            st.markdown("#### ✨ Template Matched Preview")
                            try:
                                # Show template matched version
                                st.session_state.html_preview_component.show_preview(
                                    html_content=final_html,
                                    height=600
                                )
                            except Exception as e:
                                st.error(f"Error displaying template matched resume: {e}")
                            st.markdown('</div>', unsafe_allow_html=True)
                        
                        # Apply confirmation section
                        st.markdown("---")
                        st.markdown("### 🤔 Apply Template Matching?")
                        
                        col_info, col_action = st.columns([2, 1])
                        
                        with col_info:
                            st.markdown(f"""
                            **Template Matching Completed Successfully!**
                            - 📊 Similarity Score: **{results.get('final_score', 0)}%**
                            - 🔄 Iterations Used: **{results.get('total_iterations', 0)}**
                            - 🎯 Target: {'✅ Reached' if results.get('target_reached', False) else '⚠️ Partial Success'}
                            
                            **What happens when you apply?**
                            - Your current resume preview will be updated
                            - Template matched styling will become your active resume
                            - You can continue editing or export the new version
                            """)
                        
                        with col_action:
                            st.markdown('<br>', unsafe_allow_html=True)
                            if st.button("✅ Apply Template Matching", key="apply_template_match", help="Apply the template matched resume as your current resume"):
                                # Apply the template matched resume
                                st.session_state.html_resume_content = final_html
                                st.success("🎉 Template matching applied successfully!")
                                st.info("💡 Your resume preview has been updated with the new template matching!")
                                st.rerun()
                            
                            if st.button("❌ Keep Current", key="reject_template_match", help="Keep your current resume and discard template matching"):
                                st.info("👍 Keeping your current resume. Template matching results discarded.")
                    
                    # Show detailed comparison interface in expander
                    with st.expander("🔍 View Detailed Analysis & Iterations", expanded=False):
                        st.session_state.template_matcher.create_comparison_interface(results)
                    
                else:
                    st.error(f"❌ Template matching failed: {results.get('error', 'Unknown error')}")
                    
            except Exception as e:
                st.error(f"❌ Error during template matching: {str(e)}")
                logger.error(f"Template matching error: {e}")
        
        # Show previous results if available
        if hasattr(st.session_state, 'template_matching_results'):
            results = st.session_state.template_matching_results
            st.markdown("---")
            st.markdown("### 📈 Previous Template Matching Results")
            
            # Show metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Final Score", f"{results.get('final_score', 0)}%")
            with col2:
                st.metric("Iterations", results.get('total_iterations', 0))
            with col3:
                target_reached = results.get('target_reached', False)
                st.metric("Status", "✅ Success" if target_reached else "⚠️ Partial")
            
            # Show the final resume preview
            final_html = results.get('final_html', '')
            if final_html:
                st.markdown("#### 🎨 Final Improved Resume")
                try:
                    st.session_state.html_preview_component.show_preview(
                        html_content=final_html,
                        height=600
                    )
                except Exception as e:
                    st.error(f"Error showing preview: {e}")
            
            # Detailed analysis in expander
            with st.expander("🔍 View Detailed Analysis", expanded=False):
                st.session_state.template_matcher.create_comparison_interface(results)
            
    elif not st.session_state.openrouter_client:
        st.warning("🔑 OpenRouter API key required for template matching")
        st.info("Add your API key in the sidebar to enable this feature")
        
    elif not original_file_data:
        st.warning("📄 Original file data not available")
        st.info("Please re-upload your resume to use template matching")
    
    # Show dependencies info and API logs
    col1, col2 = st.columns(2)
    
    with col1:
        with st.expander("📋 Dependencies Information"):
            dependencies = image_converter.get_available_methods()
            st.markdown("**Image Conversion Methods:**")
            for method, available in dependencies.items():
                status = "✅ Available" if available else "❌ Not Available"
                st.markdown(f"- **{method}**: {status}")
            
            if not dependencies.get('pdf2image'):
                st.warning("⚠️ PDF to image conversion not available. Install with: `pip install pdf2image`")
            
            if not dependencies.get('selenium'):
                st.warning("⚠️ HTML to image conversion not available. Install with: `pip install selenium`")
    
    with col2:
        with st.expander("🔍 API Call Logs (Live)"):
            if st.session_state.get('show_api_logs', False):
                st.markdown("**Real-time API call logging is enabled.**")
                st.markdown("API calls will appear above as they happen.")
                
                if st.button("🧹 Clear Session Logs", use_container_width=True):
                    # This would clear any session-stored logs if we implement them
                    st.success("Session logs cleared!")
                    
            else:
                st.markdown("**API logging is disabled.**")
                st.markdown("Enable 'Show API call logs' above to see real-time API usage.")
            
            st.markdown("**Logging includes:**")
            st.markdown("- 🤖 Model used")
            st.markdown("- 📊 Token counts (input → output)")
            st.markdown("- ⏱️ Response time")
            st.markdown("- ✅/❌ Success/failure status")

def display_html_resume_builder():
    """Display the HTML resume builder interface."""
    st.markdown('<h2 class="section-header">🌐 HTML Resume Builder</h2>', unsafe_allow_html=True)
    
    # Initialize HTML content in session state
    if 'html_resume_content' not in st.session_state:
        st.session_state.html_resume_content = ""
    if 'selected_template' not in st.session_state:
        st.session_state.selected_template = "modern"
    if 'selected_palette' not in st.session_state:
        st.session_state.selected_palette = "professional_blue"
    
    # Auto-generate HTML when resume is parsed but no HTML exists
    if (st.session_state.parsed_resume and 
        not st.session_state.html_resume_content and
        'auto_generated' not in st.session_state):
        st.session_state.auto_generated = True
        auto_generate_html_preview()
    
    # Template selection with original format option
    st.markdown("### 🎨 Template Selection")
    
    # Option to keep original format
    col1, col2 = st.columns([1, 1])
    
    with col1:
        # Get previous state
        prev_keep_original = getattr(st.session_state, 'keep_original_layout', True)
        
        keep_original = st.checkbox(
            "📄 Keep Original Layout", 
            value=prev_keep_original,
            help="Generate HTML that mimics your original resume's layout and styling"
        )
        
        # Store in session state and trigger regeneration if changed
        if keep_original != prev_keep_original:
            st.session_state.keep_original_layout = keep_original
            if st.session_state.html_resume_content:  # Only regenerate if we have content
                generate_html_with_loading(template_changed=True)
                st.rerun()
        else:
            st.session_state.keep_original_layout = keep_original
    
    with col2:
        if not keep_original:
            use_preset_templates = st.checkbox(
                "🎨 Use Professional Templates", 
                value=True,
                help="Choose from our professionally designed templates"
            )
        else:
            use_preset_templates = False
            st.info("💡 Original layout will be preserved with modern HTML/CSS")
    
    # Role Adaptation Section
    st.markdown("---")
    st.markdown("#### 🎯 Role Adaptation (AI-Powered)")
    
    col_role1, col_role2 = st.columns([2, 1])
    with col_role1:
        # Target role selection
        target_roles = [
            "Software Engineer",
            "Frontend Developer", 
            "Backend Developer",
            "Full-Stack Developer",
            "DevOps Engineer",
            "Data Scientist",
            "Data Engineer",
            "Machine Learning Engineer",
            "Product Manager",
            "Project Manager",
            "Business Analyst",
            "Marketing Manager",
            "Sales Manager",
            "Financial Analyst",
            "Operations Manager",
            "HR Manager",
            "Consultant",
            "Designer (UI/UX)",
            "Content Writer",
            "Digital Marketing Specialist"
        ]
        
        current_target_role = getattr(st.session_state, 'target_role', "None (Original)")
        
        # Calculate index safely 
        try:
            if current_target_role == "None (Original)" or current_target_role not in target_roles:
                role_index = 0
            else:
                role_index = target_roles.index(current_target_role) + 1
        except ValueError:
            role_index = 0
        
        selected_role = st.selectbox(
            "Target Role:",
            ["None (Original)"] + target_roles,
            index=role_index,
            help="AI will adapt your resume content to emphasize skills and experiences relevant to this role"
        )
        
        # Update session state if changed
        if selected_role != getattr(st.session_state, 'target_role', "None (Original)"):
            logger.info(f"🎯 Role changed from {getattr(st.session_state, 'target_role', 'None')} to {selected_role}")
            st.session_state.target_role = selected_role
            if selected_role != "None (Original)":
                logger.info(f"🔄 Triggering HTML regeneration for role: {selected_role}")
                # Force regeneration of HTML content
                generate_html_with_loading(role_changed=True)
                # Clear any cached preview content to force refresh
                if hasattr(st.session_state, 'last_displayed_html'):
                    delattr(st.session_state, 'last_displayed_html')
                st.rerun()
            else:
                # When reverting to original, also regenerate
                logger.info("🔄 Reverting to original content")
                generate_html_with_loading(role_changed=True)
                st.rerun()
    
    with col_role2:
        if selected_role != "None (Original)":
            if hasattr(st.session_state, 'html_generator') and st.session_state.html_generator.openrouter_client:
                # Check if content has already been adapted
                if hasattr(st.session_state, 'html_resume_content') and st.session_state.html_resume_content:
                    current_target = getattr(st.session_state, 'target_role', "None (Original)")
                    if current_target != "None (Original)":
                        st.success(f"✅ Content adapted for: **{selected_role}**")
                    else:
                        st.info(f"🤖 AI will adapt content for: **{selected_role}**")
                else:
                    st.info(f"🤖 AI will adapt content for: **{selected_role}**")
            else:
                st.warning("⚠️ AI adaptation requires OpenRouter API key")
        else:
            st.info("📄 Using original resume content")
    
    st.markdown("---")
    
    # Template and palette selection
    col1, col2 = st.columns(2)
    
    with col1:
        if use_preset_templates and not keep_original:
            st.markdown("#### 🎨 Choose Template")
            templates = st.session_state.html_generator.get_available_templates()
            
            # Create scrollable container for templates
            with st.container():
                # Add custom CSS for scrollable template container
                st.markdown("""
                <style>
                .template-container {
                    max-height: 250px;
                    overflow-y: auto;
                    overflow-x: hidden;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 10px;
                    background-color: #fafafa;
                    margin-bottom: 15px;
                }
                .template-container::-webkit-scrollbar {
                    width: 8px;
                }
                .template-container::-webkit-scrollbar-track {
                    background: #f1f1f1;
                    border-radius: 4px;
                }
                .template-container::-webkit-scrollbar-thumb {
                    background: #c1c1c1;
                    border-radius: 4px;
                }
                .template-container::-webkit-scrollbar-thumb:hover {
                    background: #a8a8a8;
                }
                .template-item {
                    margin-bottom: 6px;
                    padding: 8px;
                    border-radius: 6px;
                    background: white;
                    border: 1px solid #e9ecef;
                    transition: all 0.2s ease;
                }
                .template-item:hover {
                    background: #f1f3f4;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }
                .template-category {
                    font-weight: bold;
                    color: #495057;
                    margin: 15px 0 10px 0;
                    padding: 6px 0;
                    border-bottom: 2px solid #dee2e6;
                    font-size: 1.1em;
                }
                .template-category:first-child {
                    margin-top: 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                # Group templates by category for better organization
                template_categories = {}
                for template in templates:
                    category = template.get('category', 'general')
                    if category not in template_categories:
                        template_categories[category] = []
                    template_categories[category].append(template)
                
                # Display templates by category in a scrollable container
                st.markdown('<div class="template-container">', unsafe_allow_html=True)
                
                for category, category_templates in template_categories.items():
                    if len(template_categories) > 1:  # Only show category headers if multiple categories
                        st.markdown(f'<div class="template-category">{category.title()}</div>', unsafe_allow_html=True)
                    
                    # Display templates in a more compact grid format
                    for i in range(0, len(category_templates), 2):
                        cols = st.columns(2)
                        
                        for j, col in enumerate(cols):
                            if i + j < len(category_templates):
                                template = category_templates[i + j]
                                
                                with col:
                                    # Highlight selected template
                                    button_type = "primary" if st.session_state.selected_template == template['id'] else "secondary"
                                    
                                    if st.button(
                                        f"**{template['name']}**", 
                                        key=f"template_{template['id']}",
                                        use_container_width=True,
                                        type=button_type,
                                        help=template['description']
                                    ):
                                        if st.session_state.selected_template != template['id']:
                                            st.session_state.selected_template = template['id']
                                            generate_html_with_loading(template_changed=True)
                                            st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown("#### 🎯 Original Format Options")
            
            # Original format enhancement options
            current_enhancement = getattr(st.session_state, 'original_enhancement_level', "Minimal (Keep exact layout)")
            enhance_original = st.selectbox(
                "Enhancement Level:",
                ["Minimal (Keep exact layout)", "Enhanced (Improve readability)", "Modernized (Add subtle styling)"],
                index=["Minimal (Keep exact layout)", "Enhanced (Improve readability)", "Modernized (Add subtle styling)"].index(current_enhancement),
                help="How much to enhance the original design",
                key="enhancement_selector"
            )
            
            # Trigger regeneration if enhancement level changed
            if enhance_original != getattr(st.session_state, 'original_enhancement_level', None):
                st.session_state.original_enhancement_level = enhance_original
                generate_html_with_loading(template_changed=True)
                st.rerun()
    
    with col2:
        st.markdown("#### 🎨 Choose Color Scheme")
        palettes = st.session_state.html_generator.get_available_palettes()
        
        for palette in palettes:
            # Show color preview and button
            col_a, col_b = st.columns([1, 3])
            with col_a:
                st.markdown(
                    f'<div style="width:30px;height:30px;background:{palette["primary"]};border-radius:50%;border:2px solid #ddd;display:inline-block;margin-right:10px;"></div>'
                    f'<div style="width:20px;height:20px;background:{palette["secondary"]};border-radius:50%;border:2px solid #ddd;display:inline-block;"></div>', 
                    unsafe_allow_html=True
                )
            with col_b:
                # Highlight selected palette
                button_type = "primary" if st.session_state.selected_palette == palette['id'] else "secondary"
                
                if st.button(
                    palette['name'],
                    key=f"palette_{palette['id']}",
                    use_container_width=True,
                    type=button_type
                ):
                    if st.session_state.selected_palette != palette['id']:
                        st.session_state.selected_palette = palette['id']
                        generate_html_with_loading(palette_changed=True)
                        st.rerun()
    # Display preview and download options
    if st.session_state.html_resume_content:
        logger.info(f"🖥️ MAIN PREVIEW DISPLAY STARTING")
        logger.info(f"   📊 HTML content type: {type(st.session_state.html_resume_content)}")
        
        if isinstance(st.session_state.html_resume_content, dict):
            html_content = st.session_state.html_resume_content.get('html', '')
            css_content = st.session_state.html_resume_content.get('css', '')
            template_info = st.session_state.html_resume_content.get('template', 'unknown')
            palette_info = st.session_state.html_resume_content.get('palette', 'unknown')
            
            logger.info(f"   📄 HTML content length: {len(html_content)} chars")
            logger.info(f"   🎨 CSS content length: {len(css_content)} chars") 
            logger.info(f"   🎨 Template: {template_info}, Palette: {palette_info}")
            logger.debug(f"   📄 HTML preview (first 300 chars): {html_content[:300]}")
            
            # Check for role-adapted content in final preview
            if 'software engineer' in html_content.lower():
                logger.info(f"   ✅ 'SOFTWARE ENGINEER' found in preview HTML")
            elif 'data engineer' in html_content.lower():
                logger.info(f"   📊 'Data Engineer' found in preview HTML (original)")
            else:
                logger.warning(f"   ⚠️ Neither 'Software Engineer' nor 'Data Engineer' found in preview HTML")
            
            # Check summary content
            if 'professional' in html_content.lower():
                logger.info(f"   ✅ Professional content found in HTML")
            
        st.markdown("---")
        
        # Enhanced tabs with new features
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["👁️ Preview", "✏️ Edit", "🎯 ATS Score", "🔧 Customize", "🎨 Template Match", "💾 Download"])
        
        tabs_new = st.tabs(["Preview", "Edit", "ATS Score", "Customize", "Template Match", "Download", "Cover Letter"])
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = tabs_new
        with tab1:
            st.markdown("### 👁️ Live Preview")
            
            logger.info(f"🖥️ DISPLAYING PREVIEW TO USER")
            logger.info(f"   📊 Calling html_preview.show_preview()")
            logger.info(f"   📏 HTML size being sent to preview: {len(st.session_state.html_resume_content['html'])} chars")
            logger.info(f"   📏 CSS size being sent to preview: {len(st.session_state.html_resume_content['css'])} chars")
            
            # Simple, clean preview - just show the resume
            try:
                html_preview.show_preview(
                    st.session_state.html_resume_content['html'],
                    st.session_state.html_resume_content['css'],
                    height=800
                )
                logger.info(f"✅ PREVIEW DISPLAYED SUCCESSFULLY")
            except Exception as e:
                logger.error(f"❌ PREVIEW DISPLAY ERROR: {e}")
                logger.error(f"📊 Preview error details:", exc_info=True)
        
        with tab2:
            # Store original data for reset functionality
            if 'original_resume_data' not in st.session_state:
                st.session_state.original_resume_data = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
            
            # Real-time editing interface
            resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
            updated_resume_dict = st.session_state.real_time_editor.show_editing_interface(resume_dict)
            
            # Update parsed resume if changes were made
            if updated_resume_dict != resume_dict:
                # Convert back and update session state
                st.session_state.parsed_resume = sanitize_data(updated_resume_dict)
                
                # Regenerate HTML with updates
                if st.button("🔄 Update Preview", key="update_preview_from_edit"):
                    with st.spinner("Updating preview..."):
                        html_result = st.session_state.html_generator.generate_resume_html(
                            updated_resume_dict,
                            st.session_state.selected_template,
                            st.session_state.selected_palette
                        )
                        st.session_state.html_resume_content = html_result
                        st.success("✅ Preview updated!")
                        st.rerun()
            
            # Custom AI Improvement Section
            if st.session_state.openrouter_client:
                st.markdown("---")
                st.markdown("#### 🤖 **Custom AI Improvement**")
                
                col1, col2 = st.columns([3, 1])
                
                with col1:
                    custom_improvement_request = st.text_area(
                        "Improvement Request",
                        placeholder="E.g., 'Add more technical details to my experience', 'Make my summary more impactful', 'Include specific achievements with metrics'",
                        height=80,
                        help="Describe what improvements you want to make to your resume"
                    )
                
                with col2:
                    improvement_type = st.selectbox(
                        "Improvement Type",
                        ["Quick Enhancement", "Comprehensive Rewrite"],
                        help="Quick: Style and minor content changes\nComprehensive: Deep content analysis and rewriting"
                    )
                
                # Additional information field
                additional_resume_info = st.text_area(
                    "Additional Information (Optional)",
                    placeholder="Add any extra details, achievements, or information you'd like to include in your resume...",
                    height=100,
                    help="This information will be incorporated into your resume during the improvement process"
                )
                
                if st.button("✨ Apply Custom AI Improvements", use_container_width=True, type="primary"):
                    if custom_improvement_request.strip():
                        with st.spinner("🤖 Applying custom improvements..."):
                            try:
                                # Get current resume data
                                current_resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
                                
                                # Combine HTML and CSS for AI processing
                                complete_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
{st.session_state.html_resume_content['css']}
</style>
</head>
<body>
{st.session_state.html_resume_content['html']}
</body>
</html>
                                """
                                
                                # Apply custom improvements
                                if improvement_type == "Comprehensive Rewrite":
                                    improved_html = st.session_state.openrouter_client.custom_improve_resume(
                                        complete_html, 
                                        custom_improvement_request,
                                        current_resume_dict,
                                        additional_resume_info
                                    )
                                else:
                                    # Quick enhancement
                                    improved_html = st.session_state.openrouter_client.improve_html_resume(
                                        complete_html, 
                                        custom_improvement_request,
                                        current_resume_dict
                                    )
                                
                                if improved_html and not improved_html.startswith("Error:"):
                                    # Parse back into HTML and CSS
                                    if '<style>' in improved_html:
                                        css_start = improved_html.find('<style>') + 7
                                        css_end = improved_html.find('</style>')
                                        css_content = improved_html[css_start:css_end]
                                        
                                        html_start = improved_html.find('<body>') + 6
                                        html_end = improved_html.find('</body>')
                                        html_content = improved_html[html_start:html_end]
                                        
                                        st.session_state.html_resume_content['html'] = html_content
                                        st.session_state.html_resume_content['css'] = css_content
                                    else:
                                        st.session_state.html_resume_content['html'] = improved_html
                                    
                                    st.success("✅ Custom improvements applied! Check the Preview tab to see the changes.")
                                    st.info("💡 Your resume has been enhanced based on your specific requirements.")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Custom improvement failed: {improved_html}")
                                    
                            except Exception as e:
                                st.error(f"❌ Error during custom improvement: {str(e)}")
                                logger.error(f"Custom improvement error: {e}")
                    else:
                        st.warning("⚠️ Please enter an improvement request.")
            else:
                st.markdown("---")
                st.info("🔑 Connect your OpenRouter API key in the sidebar to access custom AI improvements!")
        
        with tab3:
            st.markdown("### 🎯 **ATS Compatibility Analysis**")
            
            # Job description input for better analysis
            col1, col2 = st.columns([2, 1])
            
            with col1:
                job_description = st.text_area(
                    "📋 Job Description (Optional)",
                    placeholder="Paste the job description here for more accurate ATS analysis...",
                    height=150,
                    help="Adding a job description will provide more targeted keyword analysis"
                )
            
            with col2:
                st.markdown("**Analysis Options:**")
                include_job_match = st.checkbox("🎯 Job-specific analysis", value=bool(job_description))
                show_keyword_suggestions = st.checkbox("💡 Keyword suggestions", value=True)
                show_improvement_tips = st.checkbox("📈 Improvement tips", value=True)
            
            # Run ATS analysis
            if st.button("🚀 Analyze ATS Compatibility", use_container_width=True):
                with st.spinner("🔍 Analyzing your resume for ATS compatibility..."):
                    try:
                        # Convert resume data for analysis
                        resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
                        
                        # Run ATS analysis
                        ats_score = st.session_state.ats_analyzer.analyze_resume(
                            resume_dict, 
                            job_description if include_job_match else ""
                        )
                        
                        # Store score for later use
                        st.session_state.last_ats_score = ats_score
                        
                        # Display results
                        display_ats_score_dashboard(ats_score)
                        
                        # Additional insights
                        if show_keyword_suggestions:
                            st.markdown("#### 🔤 **Keyword Optimization Tips**")
                            if job_description:
                                st.info("💡 Based on the job description, consider adding industry-specific keywords to your experience descriptions")
                            else:
                                st.info("💡 Add a job description above for personalized keyword suggestions")
                        
                        if show_improvement_tips and ats_score.overall_score < 80:
                            st.markdown("#### 🚀 **Quick Wins**")
                            quick_tips = [
                                "Use bullet points in experience descriptions",
                                "Add quantifiable achievements (%, $, numbers)",
                                "Include relevant technical skills",
                                "Use standard section headers",
                                "Keep formatting simple and clean"
                            ]
                            
                            for tip in quick_tips[:3]:
                                st.markdown(f"• {tip}")
                    
                    except Exception as e:
                        st.error(f"❌ ATS analysis failed: {str(e)}")
            
            # Show current score if available
            if 'last_ats_score' in st.session_state:
                st.markdown("#### 📊 **Last Analysis Results**")
                display_ats_score_dashboard(st.session_state.last_ats_score)
                
                # Add ATS improvement functionality
                if st.session_state.openrouter_client and st.session_state.last_ats_score.overall_score < 90:
                    st.markdown("#### 🚀 **AI-Powered ATS Improvement**")
                    
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**Current Score: {st.session_state.last_ats_score.overall_score}/100**")
                        if st.session_state.last_ats_score.overall_score < 80:
                            st.warning("Your resume needs improvement for better ATS compatibility!")
                        else:
                            st.info("Good score! You can still optimize further for better results.")
                    
                    with col2:
                        if st.button("✨ Apply ATS Improvements", use_container_width=True, type="primary"):
                            with st.spinner("🤖 Optimizing resume for ATS compatibility..."):
                                try:
                                    # Generate ATS improvement prompt
                                    improvement_prompt = st.session_state.ats_analyzer.generate_ats_improvement_prompt(
                                        st.session_state.last_ats_score, 
                                        job_description if include_job_match else ""
                                    )
                                    
                                    # Combine HTML and CSS for AI processing
                                    complete_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
{st.session_state.html_resume_content['css']}
</style>
</head>
<body>
{st.session_state.html_resume_content['html']}
</body>
</html>
                                    """
                                    
                                    # Apply ATS improvements
                                    improved_html = st.session_state.openrouter_client.improve_resume_for_ats(
                                        complete_html,
                                        st.session_state.parsed_resume_data,
                                        improvement_prompt,
                                        job_description if include_job_match else ""
                                    )
                                    
                                    if improved_html and not improved_html.startswith("Error:"):
                                        # Parse back into HTML and CSS
                                        if '<style>' in improved_html:
                                            css_start = improved_html.find('<style>') + 7
                                            css_end = improved_html.find('</style>')
                                            css_content = improved_html[css_start:css_end]
                                            
                                            html_start = improved_html.find('<body>') + 6
                                            html_end = improved_html.find('</body>')
                                            html_content = improved_html[html_start:html_end]
                                            
                                            st.session_state.html_resume_content['html'] = html_content
                                            st.session_state.html_resume_content['css'] = css_content
                                        else:
                                            st.session_state.html_resume_content['html'] = improved_html
                                        
                                        st.success("✅ Resume optimized for ATS! Check the Preview tab to see the improvements.")
                                        st.info("💡 Run another ATS analysis to see your improved score!")
                                        st.rerun()
                                    else:
                                        st.error(f"❌ ATS improvement failed: {improved_html}")
                                        
                                except Exception as e:
                                    st.error(f"❌ Error during ATS improvement: {str(e)}")
                                    
                elif st.session_state.openrouter_client and st.session_state.last_ats_score.overall_score >= 90:
                    st.success("🎉 Excellent ATS score! Your resume is well-optimized.")
                elif not st.session_state.openrouter_client:
                    st.info("🔑 Connect your OpenRouter API key to apply AI-powered ATS improvements!")
        
        with tab4:
            st.markdown("### 🔧 Customize Your Resume")
            
            # AI-powered customizations
            if st.session_state.openrouter_client:
                st.markdown("#### 🤖 AI-Powered Customization")
                
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    custom_request = st.text_area(
                        "Improvement Request",
                        placeholder="E.g., 'Make it more colorful', 'Add subtle animations', 'Make text larger', 'Reorganize sections for better flow'",
                        height=100
                    )
                
                with col2:
                    customization_type = st.radio(
                        "Customization Type",
                        ["Quick Improvement", "Custom with Data"],
                        help="Quick: Fast style changes only\nCustom: Deep improvements using all your resume data"
                    )
                
                # Additional info field for custom improvements
                additional_info = ""
                if customization_type == "Custom with Data":
                    additional_info = st.text_area(
                        "Additional Information (Optional)",
                        placeholder="Add any extra details, achievements, or information you'd like to include in your resume...",
                        height=80,
                        help="This information will be integrated into your resume during the improvement process"
                    )
                
                if st.button("✨ Apply AI Customization") and custom_request:
                    with st.spinner("🤖 Applying customizations..."):
                        try:
                            # Combine HTML and CSS for AI processing
                            complete_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
{st.session_state.html_resume_content['css']}
</style>
</head>
<body>
{st.session_state.html_resume_content['html']}
</body>
</html>
                            """
                            
                            # Choose method based on customization type
                            if customization_type == "Custom with Data" and hasattr(st.session_state, 'parsed_resume_data'):
                                improved_html = st.session_state.openrouter_client.custom_improve_resume(
                                    complete_html, 
                                    custom_request,
                                    st.session_state.parsed_resume_data,
                                    additional_info
                                )
                            else:
                                # Pass resume data if available for context
                                resume_data = getattr(st.session_state, 'parsed_resume_data', None)
                                improved_html = st.session_state.openrouter_client.improve_html_resume(
                                    complete_html, 
                                    custom_request,
                                    resume_data
                                )
                            
                            if improved_html and not improved_html.startswith("Error:"):
                                # Parse back into HTML and CSS
                                if '<style>' in improved_html:
                                    css_start = improved_html.find('<style>') + 7
                                    css_end = improved_html.find('</style>')
                                    css_content = improved_html[css_start:css_end]
                                    
                                    html_start = improved_html.find('<body>') + 6
                                    html_end = improved_html.find('</body>')
                                    html_content = improved_html[html_start:html_end]
                                    
                                    st.session_state.html_resume_content['html'] = html_content
                                    st.session_state.html_resume_content['css'] = css_content
                                else:
                                    st.session_state.html_resume_content['html'] = improved_html
                                
                                st.success("✅ Resume customized successfully!")
                                st.rerun()
                            else:
                                st.error(f"❌ Customization failed: {improved_html}")
                                
                        except Exception as e:
                            st.error(f"❌ Error during customization: {str(e)}")
                
                st.markdown("---")
                st.markdown("#### 🎨 AI Color Customization")
                
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    color_description = st.text_input(
                        "Color Theme Description",
                        placeholder="e.g., 'modern blue tech', 'warm professional orange', 'elegant dark theme', 'bright creative colors'",
                        help="Describe the color scheme you want in natural language"
                    )
                
                with col2:
                    if st.button("🎨 Apply Color Theme", use_container_width=True) and color_description:
                        with st.spinner("🤖 Customizing colors..."):
                            try:
                                # Use AI to customize colors
                                customized_resume = st.session_state.html_generator.customize_colors_with_ai(
                                    st.session_state.html_resume_content,
                                    color_description
                                )
                                
                                if customized_resume != st.session_state.html_resume_content:
                                    st.session_state.html_resume_content = customized_resume
                                    st.success("✅ Colors customized successfully!")
                                    st.rerun()
                                else:
                                    st.warning("⚠️ No changes made to colors")
                                    
                            except Exception as e:
                                st.error(f"❌ Color customization error: {str(e)}")
                
                # AI Color Suggestions
                st.markdown("##### 💡 AI Color Suggestions")
                if st.button("🔮 Get AI Color Suggestions"):
                    with st.spinner("Getting personalized color suggestions..."):
                        try:
                            resume_data = getattr(st.session_state, 'parsed_resume_data', {})
                            suggestions = st.session_state.html_generator.get_ai_color_suggestions(
                                resume_data,
                                resume_data.get('title', '')
                            )
                            
                            for i, suggestion in enumerate(suggestions):
                                if st.button(f"🎨 {suggestion}", key=f"color_suggestion_{i}"):
                                    # Extract color name for customization
                                    color_name = suggestion.split(' - ')[0]
                                    with st.spinner(f"Applying {color_name}..."):
                                        customized_resume = st.session_state.html_generator.customize_colors_with_ai(
                                            st.session_state.html_resume_content,
                                            color_name
                                        )
                                        st.session_state.html_resume_content = customized_resume
                                        st.success(f"✅ Applied {color_name}!")
                                        st.rerun()
                                        
                        except Exception as e:
                            st.error(f"❌ Error getting color suggestions: {str(e)}")
            else:
                st.info("🔑 Connect your OpenRouter API key for AI-powered customizations!")
        
        with tab5:
            display_integrated_template_matching()
            
        with tab7:
            st.markdown("### Cover Letter Generator")
            # Inputs
            company_name = st.text_input("Company Name", value=getattr(st.session_state, 'cover_company', ""))
            job_desc = st.text_area("Job Description", value=getattr(st.session_state, 'cover_job_desc', ""), height=160)

            # Persist inputs
            st.session_state.cover_company = company_name
            st.session_state.cover_job_desc = job_desc

            # Model browsing support info
            browsing_supported = False
            if getattr(st.session_state, 'openrouter_client', None):
                try:
                    # Best-effort check via service helper
                    st.session_state.cover_letter_service.set_client(st.session_state.openrouter_client)
                    browsing_supported = st.session_state.cover_letter_service.model_supports_browsing(
                        st.session_state.openrouter_client.model
                    )
                except Exception:
                    browsing_supported = False
            st.caption(f"Model browsing supported: {'Yes' if browsing_supported else 'No'}")

            col_a, col_b = st.columns(2)
            with col_a:
                if st.button("Research Company", use_container_width=True):
                    if company_name.strip():
                        with st.spinner("Fetching company info..."):
                            try:
                                research = st.session_state.research_service.research(company_name, job_desc)
                                st.session_state.company_research = research
                                st.success("Company research updated.")
                            except Exception as e:
                                st.error(f"Research failed: {e}")
                    else:
                        st.warning("Please enter a company name.")
            with col_b:
                if st.button("Generate Cover Letter", use_container_width=True):
                    if not getattr(st.session_state, 'openrouter_client', None):
                        st.warning("Please add your OpenRouter API key in the sidebar.")
                    elif not st.session_state.parsed_resume:
                        st.warning("Upload and analyze your resume first.")
                    elif not job_desc.strip() or not company_name.strip():
                        st.warning("Provide both company name and job description.")
                    else:
                        with st.spinner("Composing cover letter..."):
                            resume_dict = convert_parsed_resume_to_dict(st.session_state.parsed_resume)
                            letter = st.session_state.cover_letter_service.generate_cover_letter(
                                resume_dict,
                                job_desc,
                                company_name,
                                st.session_state.company_research
                            )
                            st.session_state.cover_letter_text = letter
                            st.success("Draft ready. You can edit below.")

            # Research preview
            if st.session_state.company_research:
                with st.expander("Research Findings", expanded=False):
                    r = st.session_state.company_research
                    st.write({
                        'company': r.get('company'),
                        'domain': r.get('domain'),
                        'description': r.get('description'),
                        'overview': (r.get('overview') or '')[:400],
                        'about_excerpt': (r.get('about_text') or '')[:400],
                        'careers_excerpt': (r.get('careers_text') or '')[:400],
                        'role_keywords': r.get('role_keywords'),
                    })
                    if r.get('sources'):
                        st.markdown("**Sources:**")
                        for s in r['sources']:
                            st.write(f"- {s}")

            # Editor and preview
            st.markdown("#### Draft")
            st.session_state.cover_letter_text = st.text_area(
                "Cover Letter Text (editable)",
                value=st.session_state.cover_letter_text or "",
                height=260
            )
            if st.session_state.cover_letter_text:
                st.markdown("#### Preview")
                st.markdown(st.session_state.cover_letter_text)
                st.download_button(
                    "Download Cover Letter (.txt)",
                    st.session_state.cover_letter_text.encode('utf-8'),
                    file_name=f"cover_letter_{(company_name or 'company').replace(' ', '_')}.txt",
                    mime="text/plain"
                )

        with tab6:
            st.markdown("### 💾 Download Your Resume")
            
            # Enhanced download options
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 📱 **Quick Downloads**")
                html_preview.create_download_links(
                    st.session_state.html_resume_content['html'],
                    st.session_state.html_resume_content['css']
                )
            
            with col2:
                st.markdown("#### 🎯 **Export Options**")
                
                # Export format options
                export_format = st.selectbox(
                    "Choose format:",
                    ["HTML (Recommended)", "Print-Optimized HTML", "Email-Friendly HTML"],
                    help="Different formats for different use cases"
                )
                
                if st.button("📄 Generate Export", use_container_width=True):
                    with st.spinner(f"Generating {export_format}..."):
                        if export_format == "Print-Optimized HTML":
                            # Add print-specific styles
                            print_css = st.session_state.html_resume_content['css'] + """
                            
                            /* Print-specific optimizations */
                            @media print {
                                body { 
                                    background: white !important; 
                                    color: black !important;
                                    font-size: 12pt !important;
                                }
                                .resume-container { 
                                    box-shadow: none !important;
                                    max-width: none !important;
                                    margin: 0 !important;
                                }
                                @page {
                                    margin: 0.5in;
                                    size: A4;
                                }
                            }
                            """
                            
                            complete_html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>Resume</title>
<style>{print_css}</style></head>
<body>{st.session_state.html_resume_content['html']}</body></html>"""
                            
                            st.download_button(
                                "📄 Download Print Version",
                                complete_html.encode('utf-8'),
                                "resume_print.html",
                                "text/html"
                            )
                        
                        elif export_format == "Email-Friendly HTML":
                            # Inline CSS version
                            st.info("💡 This version has inline CSS for better email compatibility")
                            
                            # Simple inline CSS version (basic implementation)
                            email_html = f"""<!DOCTYPE html>
<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
{st.session_state.html_resume_content['html']}
</body></html>"""
                            
                            st.download_button(
                                "📧 Download Email Version",
                                email_html.encode('utf-8'),
                                "resume_email.html",
                                "text/html"
                            )
            
            # Usage instructions
            with st.expander("📋 **How to Use Your Resume**"):
                st.markdown("""
                **For Job Applications:**
                1. Download the HTML file
                2. Open in your browser
                3. Print/Save as PDF (Ctrl+P)
                4. Attach PDF to applications
                
                **For Online Profiles:**
                1. Use the HTML file for personal websites
                2. Customize colors and content as needed
                3. Host on GitHub Pages or similar
                
                **For Email Signatures:**
                1. Use the Email-Friendly version
                2. Copy relevant sections
                3. Paste into email signature settings
                """)
            
            # Session stats (no signup needed)
            st.markdown("---")
            st.markdown("#### 📊 **Session Stats**")
            
            stats_col1, stats_col2, stats_col3 = st.columns(3)
            
            with stats_col1:
                templates_used = len(set([st.session_state.get('selected_template', 'none')]))
                st.metric("Templates Tried", templates_used)
            
            with stats_col2:
                palettes_used = len(set([st.session_state.get('selected_palette', 'none')]))  
                st.metric("Color Schemes", palettes_used)
            
            with stats_col3:
                if 'original_resume_data' in st.session_state:
                    st.metric("Editing Session", "Active ✅")
                else:
                    st.metric("Editing Session", "Ready 📝")

def convert_parsed_resume_to_dict(parsed_resume) -> Dict[str, Any]:
    """Convert parsed resume object to dictionary format."""
    try:
        # Handle dataclass objects
        if hasattr(parsed_resume, '__dict__'):
            resume_dict = {}
            
            # Convert each attribute
            for attr_name in dir(parsed_resume):
                if not attr_name.startswith('_'):
                    attr_value = getattr(parsed_resume, attr_name)
                    
                    # Convert dataclass objects to dict
                    if hasattr(attr_value, '__dict__') and not callable(attr_value):
                        resume_dict[attr_name] = attr_value.__dict__
                    elif isinstance(attr_value, list) and attr_value and hasattr(attr_value[0], '__dict__'):
                        resume_dict[attr_name] = [item.__dict__ for item in attr_value]
                    elif not callable(attr_value):
                        resume_dict[attr_name] = attr_value
            
            return resume_dict
        
        # Already a dictionary
        elif isinstance(parsed_resume, dict):
            return parsed_resume
        
        else:
            # Fallback - try to convert to dict
            return dict(parsed_resume)
            
    except Exception as e:
        logger.error(f"Error converting parsed resume to dict: {e}")
        return {}

def main():
    """Main application function."""
    # Load custom CSS
    load_css()
    
    # Initialize session state
    initialize_session_state()
    
    # Initialize output format preference
    if 'output_format' not in st.session_state:
        st.session_state.output_format = 'html'
    
    # Check if we should show comparison page
    if st.session_state.get('show_comparison_page', False):
        try:
            # Show the enhancement comparison page
            display_enhancement_comparison_page(st.session_state.enhancement_comparison)
            return
        except Exception as e:
            st.error(f"❌ Error displaying comparison page: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
            st.session_state.show_comparison_page = False  # Reset to prevent loop
    
    # Create layout
    create_header()
    
    
    create_sidebar()
    
    # Main content area
    if not st.session_state.analysis_complete:
        create_input_section()
        
        # Feature showcase
        st.markdown('<h2 class="section-header">✨ Why Choose Our Generator?</h2>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="feature-card">
                <h3>🎯 Precise Analysis</h3>
                <p>Advanced OCR and layout detection to capture every detail of your resume structure.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="feature-card">
                <h3>🤖 AI-Powered</h3>
                <p>Get intelligent suggestions and improvements from leading AI models.</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="feature-card">
                <h3>📁 Ready to Use</h3>
                <p>Download complete LaTeX package with professional styling and documentation.</p>
            </div>
            """, unsafe_allow_html=True)
    
    else:
        # Output format selection
        st.markdown("### 🎯 Choose Output Format")
        
        format_col1, format_col2 = st.columns(2)
        
        with format_col1:
            if st.button("🌐 Modern HTML Resume", 
                        type="primary" if st.session_state.output_format == 'html' else "secondary",
                        use_container_width=True):
                st.session_state.output_format = 'html'
                st.rerun()
        
        with format_col2:
            if st.button("📄 LaTeX Document",
                        type="primary" if st.session_state.output_format == 'latex' else "secondary", 
                        use_container_width=True):
                st.session_state.output_format = 'latex'
                st.rerun()
        
        # Show format description
        if st.session_state.output_format == 'html':
            st.info("🌐 **HTML Format**: Live preview, responsive design, easy customization, instant download")
        else:
            st.info("📄 **LaTeX Format**: Academic/research standard, precise typography, publication-ready")
        
        # Show results
        display_analysis_results()
        
        if st.session_state.output_format == 'html':
            # HTML format - now includes integrated template matching
            display_html_resume_builder()
        else:
            display_latex_code()
    
    create_footer()

if __name__ == "__main__":
    main()
