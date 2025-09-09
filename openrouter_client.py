"""
OpenRouter API client for resume analysis and LaTeX generation assistance.
"""

import requests
import json
from typing import Dict, List, Optional, Any, Tuple
import logging
import streamlit as st
import time
from rate_limiter import IPRateLimiter, RateLimitExceeded

logger = logging.getLogger(__name__)

# Create a dedicated logger for OpenRouter API calls
api_logger = logging.getLogger(f"{__name__}.api_calls")
api_logger.setLevel(logging.INFO)

# Add console handler if not already present
if not api_logger.handlers:
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    api_logger.addHandler(console_handler)
    api_logger.propagate = False  # Prevent double logging

class OpenRouterClient:
    """Client for interacting with OpenRouter API."""
    
    def __init__(self, api_key: str, model: str = "openai/gpt-4o"):
        """
        Initialize OpenRouter client.
        
        Args:
            api_key: OpenRouter API key
            model: Model to use (default: gpt-4o)
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://openrouter.ai/api/v1"
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/resume-adapter/resume-latex-generator",
            "X-Title": "Resume LaTeX Generator"
        }
        
        # Initialize rate limiter
        self.rate_limiter = IPRateLimiter()
    
    def _log_api_call(self, 
                     endpoint: str, 
                     model: str, 
                     prompt_type: str, 
                     input_tokens: int = 0, 
                     output_tokens: int = 0, 
                     duration_ms: int = 0,
                     success: bool = True,
                     error_message: str = None) -> None:
        """
        Log OpenRouter API call details.
        
        Args:
            endpoint: API endpoint called
            model: Model used for the request
            prompt_type: Type of prompt (vision_analysis, text_generation, etc.)
            input_tokens: Estimated input tokens
            output_tokens: Actual output tokens from response
            duration_ms: Request duration in milliseconds
            success: Whether the request was successful
            error_message: Error message if request failed
        """
        log_data = {
            "endpoint": endpoint,
            "model": model,
            "prompt_type": prompt_type,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "duration_ms": duration_ms,
            "success": success,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if success:
            # Always log to console/file
            api_logger.info(
                f"🤖 OpenRouter API Call - "
                f"Model: {model} | "
                f"Type: {prompt_type} | "
                f"Tokens: {input_tokens}→{output_tokens} | "
                f"Duration: {duration_ms}ms"
            )
            
            # Also show in Streamlit for user visibility (if enabled)
            if st.session_state.get('enable_api_logging', True):
                st.info(
                    f"🤖 **API Call:** {model} | {prompt_type} | "
                    f"{input_tokens}→{output_tokens} tokens | {duration_ms}ms"
                )
        else:
            # Always log errors to console/file
            api_logger.error(
                f"❌ OpenRouter API Error - "
                f"Model: {model} | "
                f"Type: {prompt_type} | "
                f"Error: {error_message} | "
                f"Duration: {duration_ms}ms"
            )
            
            # Always show errors in Streamlit
            st.error(f"❌ **API Error:** {model} | {prompt_type} | {error_message}")
    
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough approximation: 1 token ≈ 4 characters for English text
        return max(1, len(text) // 4)
    
    def _make_api_request(self, 
                         data: Dict[str, Any], 
                         prompt_type: str, 
                         timeout: int = 60) -> Tuple[Dict[str, Any], bool]:
        """
        Make OpenRouter API request with comprehensive logging.
        
        Args:
            data: Request payload
            prompt_type: Type of prompt for logging
            timeout: Request timeout in seconds
            
        Returns:
            Tuple of (response_data, success)
        """
        model = data.get("model", "unknown")
        start_time = time.time()
        
        # Estimate input tokens
        prompt_text = ""
        if "messages" in data:
            for message in data["messages"]:
                if isinstance(message.get("content"), str):
                    prompt_text += message["content"]
                elif isinstance(message.get("content"), list):
                    for content_item in message["content"]:
                        if content_item.get("type") == "text":
                            prompt_text += content_item.get("text", "")
        
        input_tokens = self._estimate_tokens(prompt_text)
        
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=timeout
            )
            
            duration_ms = int((time.time() - start_time) * 1000)
            
            response.raise_for_status()
            result = response.json()
            
            # Extract output tokens from response
            output_tokens = 0
            if "usage" in result:
                output_tokens = result["usage"].get("completion_tokens", 0)
            elif "choices" in result and result["choices"]:
                # Estimate based on response length
                response_text = result["choices"][0]["message"]["content"]
                output_tokens = self._estimate_tokens(response_text)
            
            # Log successful call
            self._log_api_call(
                endpoint="/chat/completions",
                model=model,
                prompt_type=prompt_type,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                duration_ms=duration_ms,
                success=True
            )
            
            return result, True
            
        except Exception as e:
            duration_ms = int((time.time() - start_time) * 1000)
            
            # Log failed call
            self._log_api_call(
                endpoint="/chat/completions",
                model=model,
                prompt_type=prompt_type,
                input_tokens=input_tokens,
                output_tokens=0,
                duration_ms=duration_ms,
                success=False,
                error_message=str(e)
            )
            
            return {}, False
    
    def analyze_resume_structure(self, analysis_data: Dict) -> Dict[str, Any]:
        """
        Analyze resume structure and suggest LaTeX improvements.
        
        Args:
            analysis_data: Resume analysis data from ResumeAnalyzer
            
        Returns:
            Analysis and suggestions from AI
        """
        prompt = self._create_structure_analysis_prompt(analysis_data)
        
        response = self._make_request(prompt, max_tokens=2000, prompt_type="structure_analysis")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            # Fallback to raw response if not valid JSON
            return {"suggestions": response, "improved_latex": ""}
    
    def improve_latex_code(self, tex_content: str, cls_content: str, 
                          original_image_path: str = None) -> str:
        """
        Get AI assistance to improve LaTeX code to match original resume exactly.
        
        Args:
            tex_content: Generated LaTeX content
            cls_content: LaTeX class content
            original_image_path: Path to original resume image (if available)
            
        Returns:
            Improved LaTeX code
        """
        prompt = self._create_latex_improvement_prompt(tex_content, cls_content)
        
        response = self._make_request(prompt, max_tokens=3000, prompt_type="latex_improvement")
        
        return response
    
    def fix_latex_errors(self, tex_content: str, error_message: str) -> str:
        """
        Get AI help to fix LaTeX compilation errors.
        
        Args:
            tex_content: LaTeX content with errors
            error_message: LaTeX error message
            
        Returns:
            Fixed LaTeX code
        """
        prompt = f"""
        The following LaTeX code has compilation errors:
        
        ERROR MESSAGE:
        {error_message}
        
        LATEX CODE:
        {tex_content}
        
        Please fix the errors and return the corrected LaTeX code. Only return the corrected code, no explanations.
        """
        
        response = self._make_request(prompt, max_tokens=3000, prompt_type="latex_error_fix")
        return response
    
    def suggest_layout_improvements(self, sections_data: List[Dict]) -> Dict[str, str]:
        """
        Suggest layout improvements based on resume sections.
        
        Args:
            sections_data: List of resume sections with positioning data
            
        Returns:
            Layout improvement suggestions
        """
        prompt = f"""
        Analyze the following resume sections and suggest LaTeX layout improvements:
        
        SECTIONS DATA:
        {json.dumps(sections_data, indent=2)}
        
        Provide suggestions for:
        1. Better spacing and positioning
        2. Font size optimization
        3. Section ordering
        4. Visual hierarchy improvements
        
        Return as JSON with keys: spacing, fonts, ordering, hierarchy
        """
        
        response = self._make_request(prompt, max_tokens=1500, prompt_type="layout_suggestions")
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {"suggestions": response}
    
    def _create_structure_analysis_prompt(self, analysis_data: Dict) -> str:
        """Create prompt for structure analysis."""
        sections = analysis_data.get('sections', [])
        text_blocks = analysis_data.get('text_blocks', [])
        
        return f"""
        Analyze this resume structure and suggest improvements for LaTeX generation:
        
        RESUME SECTIONS ({len(sections)} sections found):
        {json.dumps(sections, indent=2)}
        
        TEXT BLOCKS ({len(text_blocks)} blocks found):
        {json.dumps(text_blocks[:10], indent=2)}  # First 10 blocks
        
        Please analyze:
        1. Section classification accuracy
        2. Text block grouping quality
        3. Font size and styling detection
        4. Layout structure analysis
        
        Provide suggestions for improving the LaTeX generation to match the original exactly.
        
        Return as JSON with keys: section_analysis, text_analysis, layout_suggestions, latex_improvements
        """
    
    def _create_latex_improvement_prompt(self, tex_content: str, cls_content: str) -> str:
        """Create prompt for LaTeX improvement."""
        return f"""
        Improve this LaTeX code to create a resume that matches the original as closely as possible:
        
        CURRENT .TEX FILE:
        {tex_content}
        
        CURRENT .CLS FILE:
        {cls_content}
        
        Please improve the code to:
        1. Match exact spacing and positioning from the original
        2. Use appropriate font sizes and weights
        3. Ensure proper alignment and margins
        4. Add any missing formatting elements
        5. Optimize the layout for professional appearance
        
        Return ONLY the improved .tex file content. Keep the same class structure but modify as needed.
        Focus on making the output identical to the original resume layout.
        """
    
    def get_available_vision_models(self) -> Dict[str, Dict[str, Any]]:
        """
        Get available vision models from OpenRouter API with their pricing and capabilities.
        
        Returns:
            Dictionary of models with their metadata
        """
        try:
            # Get all available models from OpenRouter API
            all_models = self.get_available_models()
            vision_models = {}
            
            for model in all_models:
                model_id = model.get('id', '')
                model_name = model.get('name', model_id)
                
                # Check if model supports vision/multimodal capabilities
                context_length = model.get('context_length', 0)
                modalities = model.get('architecture', {}).get('modalities', [])
                description = model.get('description', '')
                
                # Filter for vision-capable models (expanded to catch more models)
                is_vision_model = (
                    'vision' in modalities or
                    'image' in modalities or
                    'multimodal' in modalities or
                    'vision' in model_name.lower() or
                    'vision' in description.lower() or
                    'multimodal' in description.lower() or
                    'image' in description.lower() or
                    'visual' in model_name.lower() or
                    'visual' in description.lower() or
                    'vl' in model_name.lower() or
                    'vl' in model_id.lower() or
                    'gemini' in model_name.lower() or  # Gemini models support vision
                    'claude' in model_name.lower() or  # Claude 3+ supports vision
                    'gpt-4' in model_name.lower() or   # GPT-4 variants support vision
                    model_id in [
                        'anthropic/claude-3-haiku:beta',
                        'anthropic/claude-3-haiku',
                        'anthropic/claude-3-sonnet',
                        'anthropic/claude-3-opus',
                        'anthropic/claude-3-5-sonnet',
                        'anthropic/claude-3-5-haiku',
                        'openai/gpt-4o',
                        'openai/gpt-4o-mini',
                        'openai/gpt-4-turbo',
                        'openai/gpt-4-vision-preview',
                        'google/gemini-pro-vision',
                        'google/gemini-flash-1.5',
                        'google/gemini-pro-1.5',
                        'google/gemini-1.5-pro',
                        'google/gemini-1.5-flash',
                        'meta-llama/llama-3.2-11b-vision-instruct',
                        'meta-llama/llama-3.2-90b-vision-instruct'
                    ]
                )
                
                if is_vision_model:
                    # Extract pricing information
                    pricing = model.get('pricing', {})
                    prompt_cost = pricing.get('prompt', '0')
                    completion_cost = pricing.get('completion', '0')
                    
                    # Convert cost to float (handle string format like "0.000001")
                    try:
                        prompt_cost_float = float(prompt_cost)
                        completion_cost_float = float(completion_cost)
                        avg_cost = (prompt_cost_float + completion_cost_float) / 2
                    except (ValueError, TypeError):
                        avg_cost = 0.0
                    
                    # Determine if model is free (cost is 0)
                    is_free = avg_cost == 0.0
                    
                    # Extract provider from model ID
                    provider = model_id.split('/')[0].title() if '/' in model_id else 'Unknown'
                    
                    # Build capabilities list
                    capabilities = ['vision']
                    if 'multimodal' in description.lower() or 'multimodal' in modalities:
                        capabilities.append('multimodal')
                    if is_free:
                        capabilities.append('free')
                    if context_length > 100000:
                        capabilities.append('large_context')
                    
                    # Set recommended free model (prefer Claude Haiku)
                    is_recommended = model_id == 'anthropic/claude-3-haiku:beta' and is_free
                    
                    vision_models[model_id] = {
                        "name": model_name,
                        "provider": provider,
                        "is_free": is_free,
                        "cost_per_1k_tokens": avg_cost * 1000,  # Convert to per-1k tokens
                        "description": f"{description} {'- Free' if is_free else ''}".strip(),
                        "capabilities": capabilities,
                        "context_length": context_length,
                        "recommended": is_recommended
                    }
            
            # If no vision models found, fallback to basic set
            if not vision_models:
                logger.warning("No vision models found from API, using fallback list")
                vision_models = {
                    "anthropic/claude-3-haiku:beta": {
                        "name": "Claude 3 Haiku",
                        "provider": "Anthropic",
                        "is_free": True,
                        "cost_per_1k_tokens": 0.0,
                        "description": "Fast, lightweight vision model - Free",
                        "capabilities": ["vision", "fast_response"],
                        "context_length": 200000,
                        "recommended": True
                    }
                }
            
            logger.info(f"Found {len(vision_models)} vision models from OpenRouter API")
            return vision_models
            
        except Exception as e:
            logger.error(f"Failed to fetch vision models from API: {e}")
            # Fallback to basic Claude Haiku if API fails
            return {
                "anthropic/claude-3-haiku:beta": {
                    "name": "Claude 3 Haiku",
                    "provider": "Anthropic",
                    "is_free": True,
                    "cost_per_1k_tokens": 0.0,
                    "description": "Fast, lightweight vision model - Free",
                    "capabilities": ["vision", "fast_response"],
                    "context_length": 200000,
                    "recommended": True
                }
            }
    
    def get_free_vision_models(self) -> Dict[str, Dict[str, Any]]:
        """Get only free vision models."""
        all_models = self.get_available_vision_models()
        return {k: v for k, v in all_models.items() if v.get('is_free', False)}
    
    def get_recommended_vision_model(self, prefer_free: bool = True) -> str:
        """Get recommended vision model."""
        models = self.get_available_vision_models()
        
        if prefer_free:
            free_models = self.get_free_vision_models()
            if free_models:
                # Return the first recommended free model
                for model_id, model_info in free_models.items():
                    if model_info.get('recommended', False):
                        return model_id
                # If no recommended, return first free model
                return list(free_models.keys())[0]
        
        # Return best overall model if no free preference
        return "anthropic/claude-3-5-sonnet"

    def analyze_resume_visual_layout(self, image_data: bytes, model: str = None) -> Dict[str, Any]:
        """
        Analyze resume visual layout using OpenRouter vision models.
        
        Args:
            image_data: Resume image as bytes
            model: Specific model to use (defaults to recommended free model)
            
        Returns:
            Analysis of layout, sections, styling, and structure
        """
        if model is None:
            model = self.get_recommended_vision_model(prefer_free=True)
            
        import base64
        
        # Encode image for API
        image_b64 = base64.b64encode(image_data).decode('utf-8')
        
        prompt = """COMPREHENSIVE RESUME LAYOUT ANALYSIS

Analyze this resume image with extreme precision for template replication:

**STRUCTURAL ANALYSIS:**
1. **Layout Architecture**: 
   - Column structure (single/two/three column, percentages)
   - Page margins (exact measurements if possible)
   - Content area width and positioning
   - Header/footer presence and size

2. **Section Mapping**:
   - Exact order of all sections from top to bottom
   - Section titles and formatting
   - Section spacing and separation methods
   - Content organization within each section

3. **Typography Precision**:
   - Header hierarchy levels (H1, H2, H3 equivalent sizes)
   - Body text size and line height
   - Font weights (normal, bold, light) for different elements
   - Text alignment patterns (left, center, justified)

4. **Spacing Measurements**:
   - Vertical spacing between sections
   - Paragraph spacing within sections  
   - Indentation levels for lists and subsections
   - Margin and padding patterns

5. **Visual Elements Detail**:
   - Border styles, colors, and thickness
   - Bullet point styles and indentation
   - Background colors or shading
   - Lines, dividers, or separators
   - Icons or symbols used

6. **Color Scheme Analysis**:
   - Primary text color (usually black/dark gray)
   - Header colors (if different)
   - Accent colors for highlights or links
   - Background colors or patterns

7. **Content Density & Flow**:
   - Information density per section
   - Text-to-whitespace ratio
   - Reading flow and visual guidance
   - Emphasis techniques used

CRITICAL: Provide measurements, percentages, and specific values wherever possible.

Return detailed JSON: {layout_type, column_structure, sections_order, typography_scale, spacing_measurements, visual_elements, color_palette, content_flow, replication_notes}"""

        data = {
            "model": model,  # User-selected vision model
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 2000,
            "temperature": 0.1
        }
        
        result, success = self._make_api_request(data, "resume_layout_analysis", timeout=60)
        
        if success and result.get("choices"):
            analysis_text = result["choices"][0]["message"]["content"]
            
            # Try to parse as JSON, fallback to structured text
            try:
                return json.loads(analysis_text)
            except json.JSONDecodeError:
                # Parse structured response manually
                return {"raw_analysis": analysis_text, "layout_type": "single_column"}
        else:
            logger.error(f"Vision analysis failed")
            return {"layout_type": "single_column", "error": "API request failed"}

    def compare_resume_images(self, original_image: bytes, generated_image: bytes, model: str = None) -> Dict[str, Any]:
        """
        Compare original resume with generated HTML resume using multimodal AI.
        
        Args:
            original_image: Original resume image (from PDF)
            generated_image: Generated HTML resume image
            model: Specific model to use (defaults to recommended free model)
            
        Returns:
            Comparison analysis with improvement suggestions
        """
        if model is None:
            model = self.get_recommended_vision_model(prefer_free=True)
            
        import base64
        
        original_b64 = base64.b64encode(original_image).decode('utf-8')
        generated_b64 = base64.b64encode(generated_image).decode('utf-8')
        
        prompt = """
TEMPLATE MATCHING ANALYSIS: Compare these two resume images for EXACT replication.

ORIGINAL TEMPLATE (First Image):
This is the TARGET DESIGN that must be replicated exactly.

GENERATED VERSION (Second Image):
This is the current HTML version that needs improvement.

CRITICAL ANALYSIS REQUIRED:

1. **Layout Precision Analysis**:
   - Measure header height and positioning differences
   - Compare section spacing and margins (top/bottom/left/right)
   - Analyze column widths and text alignment
   - Check page proportions and content density
   - Identify any missing or misplaced elements

2. **Typography Matching**:
   - Compare exact font sizes for each element type (headers, body, labels)
   - Analyze font weights (bold, regular, light differences)
   - Check line heights and text spacing
   - Examine text hierarchy and emphasis patterns

3. **Visual Style Replication**:
   - Color differences (backgrounds, text, accents)
   - Border styles, thickness, and positioning
   - Bullet point styles and indentation
   - White space distribution and balance
   - Any decorative elements or styling

4. **Structural Organization**:
   - Section order and arrangement
   - Content grouping and separation
   - Information hierarchy and prominence
   - Overall visual flow and balance

5. **Actionable CSS/HTML Improvements**:
   - Specific CSS property changes needed (with exact values)
   - HTML structure modifications required
   - Styling adjustments for exact template matching
   - Priority order for most impactful changes

SCORING: Rate similarity 0-100 where 85+ means visually nearly identical.

Return as JSON: {layout_differences, typography_issues, visual_elements, content_organization, improvement_actions, similarity_score}
"""

        data = {
            "model": model,  # User-selected vision model
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{original_b64}"
                            }
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{generated_b64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 3000,
            "temperature": 0.1
        }
        
        result, success = self._make_api_request(data, "resume_image_comparison", timeout=90)
        
        if success and result.get("choices"):
            analysis_text = result["choices"][0]["message"]["content"]
            
            try:
                analysis = json.loads(analysis_text)
                return analysis
            except json.JSONDecodeError:
                return {
                    "raw_analysis": analysis_text,
                    "similarity_score": 50,
                    "improvement_actions": ["Manual parsing required"]
                }
        else:
            logger.error(f"Image comparison failed")
            return {
                "error": "API request failed",
                "similarity_score": 0,
                "improvement_actions": ["Comparison failed"]
            }

    def generate_iterative_improvements(self, current_html: str, comparison_feedback: Dict[str, Any], iteration: int = 1) -> str:
        """
        Generate improved HTML/CSS based on comparison feedback (GAN-like approach).
        
        Args:
            current_html: Current HTML resume
            comparison_feedback: Feedback from image comparison
            iteration: Current iteration number
            
        Returns:
            Improved HTML with modifications
        """
        improvement_actions = comparison_feedback.get('improvement_actions', [])
        layout_differences = comparison_feedback.get('layout_differences', '')
        typography_issues = comparison_feedback.get('typography_issues', '')
        visual_elements = comparison_feedback.get('visual_elements', '')
        similarity_score = comparison_feedback.get('similarity_score', 0)
        
        prompt = f"""
You are an expert web developer improving an HTML resume to EXACTLY MATCH a target template design.

TEMPLATE MATCHING TASK - ITERATION {iteration}
CURRENT SIMILARITY SCORE: {similarity_score}/100 (TARGET: 85+)

CURRENT HTML RESUME:
{current_html}

VISUAL COMPARISON FEEDBACK FROM ORIGINAL TEMPLATE:
Layout Differences: {layout_differences}
Typography Issues: {typography_issues}
Visual Elements: {visual_elements}

CRITICAL IMPROVEMENT ACTIONS (IMPLEMENT ALL):
{json.dumps(improvement_actions, indent=2)}

TEMPLATE MATCHING PRIORITY:
The goal is to make the HTML resume visually IDENTICAL to the original template. Focus on:
1. EXACT layout replication - positioning, spacing, margins
2. EXACT typography matching - fonts, sizes, weights, line heights
3. EXACT visual element matching - colors, borders, styling
4. EXACT section arrangement and hierarchy

Based on this feedback, generate an improved version that addresses EVERY issue identified:

1. **Layout Adjustments**:
   - Modify CSS for better spacing and positioning
   - Adjust section arrangements to match target
   - Fix alignment and proportions

2. **Typography Improvements**:
   - Adjust font sizes and weights
   - Fix line heights and spacing
   - Improve text hierarchy

3. **Visual Styling**:
   - Update colors and styling elements
   - Add/modify borders and lines
   - Adjust bullet points and list styling

4. **Structural Changes**:
   - Reorder sections if needed
   - Modify HTML structure for better layout
   - Improve responsive behavior

Return ONLY the complete improved HTML document. Make targeted changes based on the feedback while preserving the overall structure and content.

Focus on the highest impact changes that will increase the similarity score.
"""

        # Create request data
        data = {
            "model": self.model,  # Use client's default model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "max_tokens": 4000,
            "temperature": 0.3
        }
        
        result, success = self._make_api_request(data, "html_iterative_improvement", timeout=90)
        
        if success and result.get("choices"):
            improved_html = result["choices"][0]["message"]["content"]
            return self._extract_html_from_response(improved_html)
        else:
            logger.error(f"Iterative improvement failed")
            return current_html

    def generate_html_resume(self, resume_data: Dict[str, Any], template_style: str = "modern", ensure_complete: bool = True, country_standards: Dict[str, Any] = None, profile_image_data: bytes = None, translate_content: bool = False) -> str:
        """
        Generate HTML resume from parsed resume data.
        
        Args:
            resume_data: Parsed resume data
            template_style: Style preference (modern, classic, creative, minimal)
            
        Returns:
            Complete HTML resume with embedded CSS
        """
        
        # Format resume data for the prompt
        formatted_data = self._format_resume_data_for_html(resume_data)
        
        # Handle country-specific requirements
        country_guidance = ""
        profile_image_guidance = ""
        translation_guidance = ""
        
        if country_standards:
            country_guidance = self._generate_country_specific_guidance(country_standards)
        
        if profile_image_data:
            profile_image_guidance = self._generate_profile_image_guidance(country_standards, profile_image_data)
        
        if translate_content:
            translation_guidance = self._generate_translation_guidance(country_standards)
        
        # Check for layout hints from template matching
        layout_guidance = ""
        css_specifications = ""
        if 'layout_hints' in resume_data:
            layout_analysis = resume_data['layout_hints']
            
            # Generate specific CSS based on layout analysis
            css_specifications = self._generate_css_from_layout_analysis(layout_analysis)
            
            layout_guidance = f"""

CRITICAL - ORIGINAL LAYOUT ANALYSIS (REPLICATE THIS EXACTLY):
{json.dumps(layout_analysis, indent=2)}

TEMPLATE-SPECIFIC CSS REQUIREMENTS:
{css_specifications}

LAYOUT MATCHING REQUIREMENTS:
- Replicate the original layout structure EXACTLY as analyzed
- Match the layout type: {layout_analysis.get('layout_type', 'Unknown')}
- Follow the visual hierarchy and spacing patterns identified
- Maintain the same section ordering and positioning
- Use similar typography scale and emphasis patterns
- Preserve the original color scheme and visual elements where identified
- This is a template matching task - the goal is visual similarity to the original

"""
        
        completeness_instruction = ""
        if ensure_complete:
            completeness_instruction = """
CRITICAL: Generate a COMPLETE, COMPREHENSIVE resume that includes ALL sections and content:
- ALL work experiences with detailed descriptions 
- ALL education entries with full details
- ALL skills organized in proper categories
- ALL projects with complete descriptions
- ALL certifications and achievements
- Contact information and professional summary
- Any additional sections (languages, volunteer work, etc.)

Do NOT truncate or summarize content. Include everything provided in full detail.
If the resume is long, design it to flow across multiple pages naturally.
"""
        
        prompt = f"""
Create a complete, comprehensive HTML resume with embedded CSS based on this parsed resume data.

Resume Data:
{formatted_data}
{country_guidance}
{profile_image_guidance}
{translation_guidance}
{layout_guidance}
{completeness_instruction}

Requirements:
1. Create a complete HTML document with embedded CSS
2. {"PRIORITY: Replicate the original layout structure exactly as described in the layout analysis above" if 'layout_hints' in resume_data else f"Use {template_style} design style that supports multi-page content"}
3. {"Match the visual hierarchy, spacing, and typography patterns from the original" if 'layout_hints' in resume_data else "Make it responsive and mobile-friendly"}
4. Use semantic HTML elements
5. Include print-friendly styles with proper page breaks
6. Make it ATS-friendly with proper structure
7. Use professional typography and spacing
8. Include subtle animations and hover effects
9. Ensure good contrast and accessibility
10. Design for multi-page printing if content requires it
11. Include ALL provided content without truncation or summarization
12. **CRITICAL IMAGE LOGIC**: IF profile image guidance is provided above, use the exact placeholder {{PROFILE_IMAGE_PLACEHOLDER}}; IF NO image guidance provided, do NOT include any image elements

Return ONLY the complete HTML document with <html>, <head>, and <body> tags.
{"Make it visually identical to the original layout while being production-ready and comprehensive." if 'layout_hints' in resume_data else "Make it production-ready, visually appealing, and comprehensive."}
        """
        
        # Create request data with higher token limit for complete resumes
        max_tokens = 6000 if ensure_complete else 3000
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": 0.3
        }
        
        result, success = self._make_api_request(data, "html_resume_generation", timeout=90)
        
        if success and result.get("choices"):
            html_content = result["choices"][0]["message"]["content"]
            
            # Extract clean HTML from response
            html_content = self._extract_html_from_response(html_content)
            
            # Check if resume seems incomplete and try to complete it
            if ensure_complete and self._is_resume_incomplete(html_content, resume_data):
                completed_html = self._complete_partial_resume(html_content, resume_data, template_style)
                return self._extract_html_from_response(completed_html) if completed_html else html_content
            
            return html_content
        else:
            return f"<html><body><h1>Error generating resume</h1><p>API request failed</p></body></html>"
    
    def improve_html_resume(self, html_content: str, improvement_request: str, resume_data: Dict[str, Any] = None) -> str:
        """
        Improve existing HTML resume based on user request.
        
        Args:
            html_content: Current HTML resume content
            improvement_request: User's improvement request
            resume_data: Original resume data for context (optional)
            
        Returns:
            Improved HTML resume
        """
        
        # If we have resume data, include it for better context
        data_context = ""
        if resume_data:
            formatted_data = self._format_resume_data_for_html(resume_data)
            data_context = f"""

Original Resume Data for Context:
{formatted_data}

Use this data to ensure all important information is preserved and properly presented in the improved resume.
"""
        
        prompt = f"""
Improve this HTML resume based on the user's request.

Current HTML Resume:
{html_content[:2000]}{'...' if len(html_content) > 2000 else ''}

User's Improvement Request:
{improvement_request}
{data_context}
Requirements:
1. Apply the requested improvements
2. Maintain professional appearance
3. Keep the HTML structure intact
4. Ensure responsive design
5. Maintain accessibility standards
6. Include ALL sections and data from the original resume
7. Return the complete improved HTML document

Return ONLY the complete improved HTML document.
        """
        
        return self._make_request(prompt, max_tokens=4000, prompt_type="resume_improvement")
    
    def custom_improve_resume(self, html_content: str, user_prompt: str, resume_data: Dict[str, Any], additional_info: str = "") -> str:
        """
        Custom AI improvement that combines user prompt with additional information.
        
        Args:
            html_content: Current HTML resume content
            user_prompt: User's improvement request
            resume_data: Original resume data for context
            additional_info: Additional information provided by user
            
        Returns:
            Improved HTML resume
        """
        
        formatted_data = self._format_resume_data_for_html(resume_data)
        
        additional_context = ""
        if additional_info.strip():
            additional_context = f"""

Additional Information Provided by User:
{additional_info}

Incorporate this additional information into the resume improvements where relevant.
"""
        
        prompt = f"""
You are creating a custom-improved resume based on the user's specific requirements and additional information.

Current HTML Resume:
{html_content[:1500]}{'...' if len(html_content) > 1500 else ''}

Original Resume Data (use this as the complete source of truth):
{formatted_data}

User's Improvement Request:
{user_prompt}
{additional_context}

IMPORTANT INSTRUCTIONS:
1. Use the Original Resume Data as your primary source - it contains ALL the complete information
2. Apply the user's specific improvements and requests
3. Include ALL sections from the original data (work experience, education, skills, projects, etc.)
4. If additional information was provided, integrate it appropriately into the resume
5. Maintain professional formatting and ATS-friendly structure
6. Ensure the resume is comprehensive and complete
7. Use modern, clean design that prints well
8. Include proper contact information and all achievements

Return ONLY the complete improved HTML document with embedded CSS.
        """
        
        return self._make_request(prompt, max_tokens=5000, prompt_type="custom_improvement")
    
    def improve_resume_for_ats(self, html_content: str, resume_data: Dict[str, Any], ats_improvement_prompt: str, job_description: str = "") -> str:
        """
        Improve resume specifically for ATS optimization based on analysis results.
        
        Args:
            html_content: Current HTML resume content
            resume_data: Original resume data for context
            ats_improvement_prompt: Detailed ATS improvement instructions
            job_description: Optional job description for targeted optimization
            
        Returns:
            ATS-optimized HTML resume
        """
        
        formatted_data = self._format_resume_data_for_html(resume_data)
        
        prompt = f"""
You are an expert ATS optimization specialist. Improve this resume to maximize ATS compatibility and scoring.

Current HTML Resume:
{html_content[:1500]}{'...' if len(html_content) > 1500 else ''}

Complete Resume Data (use as primary source):
{formatted_data}

{ats_improvement_prompt}

ADDITIONAL ATS OPTIMIZATION GUIDELINES:
- Use clean, semantic HTML structure that ATS systems can parse
- Include proper heading tags (h1, h2, h3) for section organization
- Ensure all text is searchable (no text in images)
- Use standard fonts and clear formatting
- Include ALL data from the original resume
- Add relevant keywords naturally throughout the content
- Use bullet points for easy parsing
- Include contact information in a standard format
- Optimize meta tags and page structure for ATS scanning

Return ONLY the complete, ATS-optimized HTML document with embedded CSS.
Make it both ATS-friendly AND visually appealing for human reviewers.
        """
        
        return self._make_request(prompt, max_tokens=5000, prompt_type="custom_improvement")
    
    def adapt_resume_to_template(self, resume_data: Dict[str, Any], template_info: Dict[str, Any], template_html: str, country_standards: Dict[str, Any] = None, profile_image_data: bytes = None, translate_content: bool = False) -> str:
        """
        Use AI to intelligently adapt resume data to match the specific template's style and requirements.
        
        Args:
            resume_data: Original parsed resume data
            template_info: Template metadata including name, description, category
            template_html: The template HTML structure
            
        Returns:
            Complete HTML resume adapted for the specific template
        """
        
        # Format resume data for the prompt
        formatted_data = self._format_resume_data_for_html(resume_data)
        
        # Handle country-specific requirements
        country_guidance = ""
        profile_image_guidance = ""
        translation_guidance = ""
        
        if country_standards:
            country_guidance = self._generate_country_specific_guidance(country_standards)
        
        if profile_image_data:
            profile_image_guidance = self._generate_profile_image_guidance(country_standards, profile_image_data)
        
        if translate_content:
            translation_guidance = self._generate_translation_guidance(country_standards)
        
        template_name = template_info.get('name', 'Professional Template')
        template_description = template_info.get('description', '')
        template_category = template_info.get('category', 'professional')
        
        prompt = f"""
You are an expert resume writer and template designer. Adapt this resume data to perfectly match the style, tone, and structure requirements of the specific template.

Template Information:
- Name: {template_name}
- Description: {template_description}
- Category: {template_category}

Template HTML Structure:
{template_html[:1000]}{'...' if len(template_html) > 1000 else ''}

Resume Data to Adapt:
{formatted_data}
{country_guidance}
{profile_image_guidance}
{translation_guidance}

TEMPLATE ADAPTATION REQUIREMENTS:

1. **Content Adaptation**: 
   - Rewrite content to match the template's professional tone and style
   - For corporate templates: Use formal, achievement-focused language
   - For creative templates: Use more dynamic, personality-showing language
   - For tech templates: Emphasize technical skills and project details
   - For freelancer templates: Focus on client results and portfolio highlights

2. **Structure Optimization**:
   - Organize information to flow perfectly with the template design
   - Prioritize sections based on template focus (e.g., projects first for portfolio templates)
   - Ensure content length matches template spacing and layout

3. **Professional Enhancement**:
   - Add quantifiable metrics and achievements where appropriate
   - Enhance bullet points with action verbs and impact statements
   - Improve professional summary to match template's target audience

4. **Template-Specific Features**:
   - For executive templates: Emphasize leadership and strategic achievements
   - For startup templates: Highlight adaptability and growth impact  
   - For consulting templates: Focus on problem-solving and client outcomes
   - For academic templates: Emphasize research, publications, and teaching

5. **Image Handling Logic**:
   - IF profile image guidance is provided above: MUST include the placeholder exactly as specified
   - Use the exact placeholder format: {{PROFILE_IMAGE_PLACEHOLDER}}
   - IF no profile image guidance is provided: Do NOT include any image placeholders or img tags
   - NEVER create empty image elements or broken image links
   - The placeholder will be automatically replaced with actual image data after generation

6. **Complete HTML Generation**:
   - Return the FULL HTML document with all template placeholders filled
   - Include proper HTML structure with embedded CSS
   - Ensure all sections are comprehensive and complete
   - Make it production-ready and ATS-friendly
   - Apply image logic: include image elements ONLY if image data was provided

Generate the complete, adapted HTML resume that perfectly matches this template's requirements and showcases the candidate's strengths in the most effective way for the template's target use case.

Return ONLY the complete HTML document - no explanations or additional text.
        """
        
        return self._make_request(prompt, max_tokens=6000, prompt_type="template_adaptation")
    
    def customize_resume_colors(self, html_content: str, color_scheme: str) -> str:
        """
        Customize resume colors based on a color scheme.
        
        Args:
            html_content: Current HTML resume
            color_scheme: Color scheme description (e.g., "blue professional", "green modern")
            
        Returns:
            HTML resume with updated colors
        """
        
        prompt = f"""
Update the colors in this HTML resume to match the requested color scheme.

Current HTML Resume:
{html_content[:2000]}{'...' if len(html_content) > 2000 else ''}

Requested Color Scheme: {color_scheme}

Requirements:
1. Update CSS colors to match the scheme
2. Ensure good contrast for readability
3. Maintain professional appearance
4. Keep all functionality intact
5. Use complementary colors throughout

Return ONLY the complete HTML document with updated colors.
        """
        
        return self._make_request(prompt, max_tokens=3000, prompt_type="color_customization")
    
    def _format_resume_data_for_html(self, resume_data: Dict[str, Any]) -> str:
        """Format resume data for HTML generation prompts."""
        
        formatted_parts = []
        
        # Add debug info about the data structure
        logger.debug(f"Formatting resume data with keys: {list(resume_data.keys())}")
        
        # Contact Information
        if 'contact_info' in resume_data:
            contact = resume_data['contact_info']
            formatted_parts.append(f"CONTACT INFO:")
            if hasattr(contact, 'name'):
                formatted_parts.append(f"Name: {contact.name}")
                formatted_parts.append(f"Email: {contact.email}")
                formatted_parts.append(f"Phone: {contact.phone}")
                formatted_parts.append(f"Location: {contact.location}")
                if contact.linkedin:
                    formatted_parts.append(f"LinkedIn: {contact.linkedin}")
                if contact.github:
                    formatted_parts.append(f"GitHub: {contact.github}")
            else:
                formatted_parts.append(f"Name: {contact.get('name', '')}")
                formatted_parts.append(f"Email: {contact.get('email', '')}")
                formatted_parts.append(f"Phone: {contact.get('phone', '')}")
                formatted_parts.append(f"Location: {contact.get('location', '')}")
                if contact.get('linkedin'):
                    formatted_parts.append(f"LinkedIn: {contact.get('linkedin')}")
                if contact.get('github'):
                    formatted_parts.append(f"GitHub: {contact.get('github')}")
        
        # Professional Summary
        if 'professional_summary' in resume_data:
            formatted_parts.append(f"\nPROFESSIONAL SUMMARY:")
            formatted_parts.append(resume_data['professional_summary'])
        
        # Work Experience
        if 'job_experiences' in resume_data:
            formatted_parts.append(f"\nWORK EXPERIENCE:")
            for job in resume_data['job_experiences']:
                if hasattr(job, 'job_title'):
                    formatted_parts.append(f"- {job.job_title} at {job.company} ({job.start_date} - {job.end_date})")
                    if job.location:
                        formatted_parts.append(f"  Location: {job.location}")
                    if job.description:
                        if isinstance(job.description, str):
                            formatted_parts.append(f"  • {job.description}")
                        elif isinstance(job.description, list):
                            for desc in job.description:
                                if desc:
                                    formatted_parts.append(f"  • {desc}")
                        else:
                            formatted_parts.append(f"  • {str(job.description)}")
                else:
                    formatted_parts.append(f"- {job.get('job_title', '')} at {job.get('company', '')} ({job.get('start_date', '')} - {job.get('end_date', '')})")
                    if job.get('location'):
                        formatted_parts.append(f"  Location: {job.get('location')}")
                    if job.get('description'):
                        description = job.get('description', [])
                        if isinstance(description, str):
                            # If description is a string, treat it as a single item
                            formatted_parts.append(f"  • {description}")
                        elif isinstance(description, list):
                            # If description is a list, process each item
                            for desc in description:
                                if desc:  # Skip empty descriptions
                                    formatted_parts.append(f"  • {desc}")
                        else:
                            # Handle other types by converting to string
                            formatted_parts.append(f"  • {str(description)}")
        
        # Education
        if 'education' in resume_data:
            formatted_parts.append(f"\nEDUCATION:")
            for edu in resume_data['education']:
                if hasattr(edu, 'degree'):
                    formatted_parts.append(f"- {edu.degree} from {edu.school} ({edu.graduation_date})")
                    if edu.gpa:
                        formatted_parts.append(f"  GPA: {edu.gpa}")
                else:
                    formatted_parts.append(f"- {edu.get('degree', '')} from {edu.get('school', '')} ({edu.get('graduation_date', '')})")
                    if edu.get('gpa'):
                        formatted_parts.append(f"  GPA: {edu.get('gpa')}")
        
        # Skills
        if 'skills' in resume_data:
            formatted_parts.append(f"\nSKILLS:")
            skills_data = resume_data['skills']
            
            # Handle different skill data structures
            if isinstance(skills_data, str):
                # Simple string of skills
                formatted_parts.append(f"- {skills_data}")
            elif isinstance(skills_data, list):
                if not skills_data:
                    formatted_parts.append("- No skills listed")
                else:
                    # Check first item to determine structure
                    first_skill = skills_data[0]
                    if isinstance(first_skill, str):
                        # List of skill strings
                        formatted_parts.append(f"- {', '.join(skills_data)}")
                    elif isinstance(first_skill, dict):
                        # List of skill categories (dictionaries)
                        for skill_cat in skills_data:
                            if isinstance(skill_cat, dict):
                                category = skill_cat.get('category', 'Skills')
                                skills = skill_cat.get('skills', [])
                                if isinstance(skills, list):
                                    formatted_parts.append(f"- {category}: {', '.join(map(str, skills))}")
                                else:
                                    formatted_parts.append(f"- {category}: {str(skills)}")
                            else:
                                formatted_parts.append(f"- {str(skill_cat)}")
                    elif hasattr(first_skill, 'category'):
                        # List of skill category objects
                        for skill_cat in skills_data:
                            formatted_parts.append(f"- {skill_cat.category}: {', '.join(skill_cat.skills)}")
                    else:
                        # Unknown structure, convert to strings
                        for skill in skills_data:
                            formatted_parts.append(f"- {str(skill)}")
            else:
                # Unknown type, convert to string
                formatted_parts.append(f"- {str(skills_data)}")
        
        return '\n'.join(formatted_parts)
    
    def _generate_css_from_layout_analysis(self, layout_analysis: Dict[str, Any]) -> str:
        """Generate specific CSS specifications based on layout analysis."""
        css_specs = []
        
        # Column structure CSS
        if 'column_structure' in layout_analysis:
            column_info = layout_analysis['column_structure']
            css_specs.append(f"COLUMN LAYOUT: {column_info}")
        
        # Typography specifications
        if 'typography_scale' in layout_analysis:
            typo_info = layout_analysis['typography_scale']
            css_specs.append(f"TYPOGRAPHY SCALE: {typo_info}")
        
        # Spacing measurements
        if 'spacing_measurements' in layout_analysis:
            spacing_info = layout_analysis['spacing_measurements']
            css_specs.append(f"SPACING REQUIREMENTS: {spacing_info}")
        
        # Color palette
        if 'color_palette' in layout_analysis:
            color_info = layout_analysis['color_palette']
            css_specs.append(f"COLOR SCHEME: {color_info}")
        
        # Visual elements
        if 'visual_elements' in layout_analysis:
            visual_info = layout_analysis['visual_elements']
            css_specs.append(f"VISUAL ELEMENTS: {visual_info}")
        
        # Generate specific CSS rules based on analysis
        if 'sections_order' in layout_analysis:
            sections = layout_analysis['sections_order']
            css_specs.append(f"SECTION ORDER: {sections}")
        
        # Layout type specific CSS
        layout_type = layout_analysis.get('layout_type', 'single_column')
        if layout_type == 'two_column':
            css_specs.append("CSS STRUCTURE: Use CSS Grid or Flexbox for two-column layout")
        elif layout_type == 'sidebar':
            css_specs.append("CSS STRUCTURE: Implement sidebar layout with proper width ratios")
        
        return '\n'.join([f"- {spec}" for spec in css_specs])
    
    def _generate_country_specific_guidance(self, country_standards: Dict[str, Any]) -> str:
        """Generate country-specific formatting guidance."""
        if not country_standards:
            return ""
        
        guidance_parts = ["\nCOUNTRY-SPECIFIC RESUME STANDARDS:"]
        
        # Add format style
        format_style = country_standards.get('format_style', 'generic')
        guidance_parts.append(f"- Format Style: {format_style}")
        
        # Add length requirements
        length = country_standards.get('length', '1-2 pages')
        guidance_parts.append(f"- Length: {length}")
        
        # Add specific requirements
        requirements = country_standards.get('specific_requirements', [])
        if requirements:
            guidance_parts.append("- Specific Requirements:")
            for req in requirements:
                guidance_parts.append(f"  • {req}")
        
        # Add photo placement guidance
        photo_placement = country_standards.get('photo_placement', 'none')
        if photo_placement != 'none':
            guidance_parts.append(f"- Photo Placement: {photo_placement}")
        
        guidance_parts.append("- CRITICAL: Follow these country standards exactly for proper local compliance.")
        
        return '\n'.join(guidance_parts) + '\n'
    
    def _generate_profile_image_guidance(self, country_standards: Dict[str, Any], profile_image_data: bytes) -> str:
        """Generate profile image integration guidance with placeholder approach."""
        if not profile_image_data:
            return ""
        
        guidance_parts = ["\nPROFILE IMAGE INTEGRATION REQUIRED:"]
        guidance_parts.append("- A professional profile photo has been uploaded and MUST be included")
        guidance_parts.append("- Use a PLACEHOLDER that will be replaced with the actual image after generation")
        
        # Add placement guidance based on country standards
        if country_standards:
            photo_placement = country_standards.get('photo_placement', 'top-right')
            guidance_parts.append(f"- Placement: {photo_placement} (country standard)")
        else:
            guidance_parts.append("- Placement: top-right corner (default)")
        
        guidance_parts.extend([
            "- Size: Professional headshot, approximately 150x200px",
            "- Style: Rounded corners with subtle border",
            "- HTML Structure: Use the EXACT placeholder format below:",
            "- <img src='{{PROFILE_IMAGE_PLACEHOLDER}}' class='profile-photo' alt='Professional headshot' style='width: 150px; height: 200px; border-radius: 8px; border: 2px solid #ddd;'>",
            "",
            "CRITICAL REQUIREMENTS:",
            "- Use EXACTLY this placeholder: {{PROFILE_IMAGE_PLACEHOLDER}}",
            "- Add CSS classes and inline styles for professional appearance",
            "- Position according to country standards or default placement",
            "- The placeholder will be automatically replaced with actual image data",
            "- Ensure proper spacing and integration with the overall layout",
            "- Do NOT use any actual base64 data - only the placeholder"
        ])
        
        return '\n'.join(guidance_parts) + '\n'
    
    def _generate_translation_guidance(self, country_standards: Dict[str, Any] = None) -> str:
        """Generate translation and localization guidance."""
        if not country_standards:
            return ""
        
        # Map countries to their primary languages
        country_language_map = {
            "🇫🇷 France": "French",
            "🇩🇪 Germany": "German", 
            "🇪🇸 Spain": "Spanish",
            "🇮🇹 Italy": "Italian",
            "🇳🇱 Netherlands": "Dutch",
            "🇸🇪 Sweden": "Swedish",
            "🇧🇷 Brazil": "Portuguese",
            "🇲🇽 Mexico": "Spanish",
            "🇯🇵 Japan": "Japanese",
            "🇰🇷 South Korea": "Korean"
        }
        
        country_name = country_standards.get('country', 'the target country')
        # Get explicit language from mapping, fallback to country standards or generic
        language = country_language_map.get(country_name, country_standards.get('language', 'the local language'))
        
        guidance_parts = ["\nCRITICAL TRANSLATION & LOCALIZATION REQUIREMENTS:"]
        guidance_parts.append(f"🌐 **PRIMARY REQUIREMENT**: TRANSLATE ALL CONTENT TO {language.upper()}")
        guidance_parts.append(f"- Transform ALL English text into professional {language}")
        guidance_parts.append(f"- Use native {language} professional terminology and conventions")
        guidance_parts.append(f"- Adapt job titles, skills, and descriptions to {language} equivalents")
        guidance_parts.append("- Convert measurements, dates, and formats to local standards")
        guidance_parts.append("- Adjust cultural references and examples to be locally relevant")
        guidance_parts.append(f"- Use appropriate professional titles and job descriptions for the {country_name} market")
        guidance_parts.append(f"- Ensure all technical terms are appropriately translated to {language}")
        guidance_parts.append(f"- Maintain professional tone while adapting to {country_name} business culture")
        guidance_parts.append(f"- MANDATORY: The final resume must be written entirely in {language}, not English")
        guidance_parts.append("- IMPORTANT: Keep original meaning while making content culturally appropriate")
        
        return '\n'.join(guidance_parts) + '\n'
    
    def _extract_html_from_response(self, content: str) -> str:
        """
        Extract HTML content from AI response, removing any explanatory text.
        
        Args:
            content: Raw AI response content
            
        Returns:
            Cleaned HTML content
        """
        import re
        
        # If content looks like pure HTML already, return as-is
        if content.strip().startswith('<!DOCTYPE') or content.strip().startswith('<html'):
            return content
        
        # Try to extract HTML document from response
        html_pattern = r'```html\s*(.*?)\s*```'
        html_match = re.search(html_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if html_match:
            return html_match.group(1).strip()
        
        # Try to find HTML document tags
        html_doc_pattern = r'(<!DOCTYPE.*?</html>)'
        html_doc_match = re.search(html_doc_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if html_doc_match:
            return html_doc_match.group(1).strip()
        
        # Try to find just <html> tags
        html_tag_pattern = r'(<html.*?</html>)'
        html_tag_match = re.search(html_tag_pattern, content, re.DOTALL | re.IGNORECASE)
        
        if html_tag_match:
            return html_tag_match.group(1).strip()
        
        # If no HTML structure found, check if it contains explanatory text
        # Remove common AI response prefixes
        lines = content.split('\n')
        cleaned_lines = []
        skip_explanations = True
        
        for line in lines:
            line_lower = line.lower().strip()
            
            # Skip explanatory lines
            if skip_explanations and any(phrase in line_lower for phrase in [
                "i've reviewed", "here's the", "i've created", "here is the", 
                "the html document", "complete html", "i've analyzed"
            ]):
                continue
            
            # Start including content from HTML tags
            if '<' in line and any(tag in line_lower for tag in ['<!doctype', '<html', '<head', '<body']):
                skip_explanations = False
            
            if not skip_explanations:
                cleaned_lines.append(line)
        
        if cleaned_lines:
            return '\n'.join(cleaned_lines).strip()
        
        # Fallback: return original content
        return content

    def _make_request(self, prompt: str, max_tokens: int = 2000, prompt_type: str = "general") -> str:
        """Make request to OpenRouter API with rate limiting."""
        
        # Log the prompt being sent
        logger.info(f"🚀 SENDING PROMPT TO AI - Type: {prompt_type}")
        logger.info(f"   📏 Prompt length: {len(prompt)} characters")
        logger.info(f"   🎯 Max tokens requested: {max_tokens}")
        logger.info(f"   🤖 Model: {self.model}")
        
        # Log first 500 characters of prompt for debugging
        prompt_preview = prompt[:500] + ("..." if len(prompt) > 500 else "")
        logger.debug(f"   📄 PROMPT PREVIEW:\n{prompt_preview}")
        
        # Log full prompt if in debug mode (can be enabled by setting log level)
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"   📋 FULL PROMPT:\n{'-'*50}\n{prompt}\n{'-'*50}")
        
        # Check rate limit before making request
        if not self.rate_limiter.record_request():
            status = self.rate_limiter.get_rate_limit_status()
            
            # Show user-friendly rate limit message
            if status.get('remaining', 0) == 0:
                reset_time = status.get('reset_time')
                if reset_time:
                    st.error(f"🚫 **Rate limit exceeded!** \n\nYou've reached the limit of {status.get('max_requests', 30)} requests per {status.get('time_window', 60)} minutes. \n\nNext request available at: **{reset_time.strftime('%H:%M:%S')}**")
                else:
                    st.error(f"🚫 **Rate limit exceeded!** Please wait before making another request.")
                
                # Show rate limit info
                with st.expander("ℹ️ Rate Limiting Info"):
                    st.write(f"**Max requests:** {status.get('max_requests', 30)} per {status.get('time_window', 60)} minutes")
                    st.write(f"**Your IP:** {status.get('ip', 'Unknown')}")
                    if status.get('retry_after'):
                        st.write(f"**Retry after:** {status.get('retry_after')} seconds")
                
                raise RateLimitExceeded("Rate limit exceeded", status)
        
        data = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": "You are an expert web developer specializing in HTML/CSS resume design. Create modern, professional HTML resumes with clean CSS styling. Focus on responsive design, accessibility, and ATS-friendly formatting."
                },
                {
                    "role": "user", 
                    "content": prompt
                }
            ],
            "max_tokens": max_tokens,
            "temperature": 0.3  # Lower temperature for more consistent output
        }
        
        try:
            # Show rate limit status to user
            status = self.rate_limiter.get_rate_limit_status()
            if status.get('enabled', True) and not status.get('is_admin', False):
                remaining = status.get('remaining', 0)
                if remaining <= 5:  # Warning when getting low
                    st.warning(f"⚠️ Only {remaining} API requests remaining in this session.")
            
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Log the response
            logger.info(f"✅ AI RESPONSE RECEIVED - Type: {prompt_type}")
            logger.info(f"   📏 Response length: {len(content)} characters")
            
            # Log response preview
            response_preview = content[:300] + ("..." if len(content) > 300 else "")
            logger.debug(f"   📄 RESPONSE PREVIEW:\n{response_preview}")
            
            # Log full response if in debug mode
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"   📋 FULL RESPONSE:\n{'-'*50}\n{content}\n{'-'*50}")
            
            # Extract HTML if the response contains explanatory text
            return self._extract_html_from_response(content)
            
        except requests.exceptions.RequestException as e:
            logger.error(f"OpenRouter API request failed: {e}")
            return f"Error: Unable to get AI assistance - {str(e)}"
        except (KeyError, IndexError) as e:
            logger.error(f"Unexpected API response format: {e}")
            return "Error: Unexpected response format from AI service"

    def generate_text(self, prompt: str, system_prompt: str = None, max_tokens: int = 1200, temperature: float = 0.3) -> str:
        """General-purpose text generation with optional custom system prompt."""
        # Rate limit
        if not self.rate_limiter.record_request():
            status = self.rate_limiter.get_rate_limit_status()
            raise RateLimitExceeded("Rate limit exceeded", status)

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are a helpful assistant."})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=data,
                timeout=60
            )
            response.raise_for_status()
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Extract HTML if this looks like an HTML generation request
            if any(keyword in prompt.lower() for keyword in ['html', 'resume', 'css', 'document']):
                return self._extract_html_from_response(content)
            
            return content
        except Exception as e:
            logger.error(f"OpenRouter generate_text failed: {e}")
            return f"Error: Unable to generate text - {e}"
    
    def get_available_models(self) -> List[Dict]:
        """Get list of available models from OpenRouter."""
        try:
            response = requests.get(
                f"{self.base_url}/models",
                headers=self.headers,
                timeout=30
            )
            response.raise_for_status()
            return response.json().get("data", [])
        except Exception as e:
            logger.error(f"Failed to fetch available models: {e}")
            return []
    
    def _is_resume_incomplete(self, html_content: str, resume_data: Dict[str, Any]) -> bool:
        """
        Check if the generated HTML resume appears to be incomplete.
        
        Args:
            html_content: Generated HTML content
            resume_data: Original resume data
            
        Returns:
            True if resume appears incomplete
        """
        if not html_content or len(html_content.strip()) < 1000:
            return True
            
        # Check for common truncation indicators
        string_indicators = [
            "...", "[truncated]", "[more content]", "[continued]",
            "<!-- incomplete", "/* incomplete", "// TODO"
        ]
        
        # Check for missing closing tags
        missing_closing_tags = "</body></html>" not in html_content.lower()
        
        if any(indicator in html_content for indicator in string_indicators) or missing_closing_tags:
            return True
            
        # Check if key sections are missing
        essential_sections = []
        if resume_data.get('job_experiences') or resume_data.get('experience'):
            essential_sections.append('experience')
        if resume_data.get('education'):
            essential_sections.append('education') 
        if resume_data.get('skills'):
            essential_sections.append('skill')
            
        missing_sections = 0
        for section in essential_sections:
            if section not in html_content.lower():
                missing_sections += 1
                
        # If more than half of essential sections are missing, likely incomplete
        return missing_sections > len(essential_sections) // 2
    
    def _complete_partial_resume(self, partial_html: str, resume_data: Dict[str, Any], template_style: str) -> str:
        """
        Complete a partial HTML resume by asking the LLM to finish it.
        
        Args:
            partial_html: Incomplete HTML content
            resume_data: Original resume data
            template_style: Style preference
            
        Returns:
            Completed HTML or None if completion fails
        """
        formatted_data = self._format_resume_data_for_html(resume_data)
        
        prompt = f"""
The following HTML resume appears to be incomplete or truncated. Please complete it using ALL the resume data provided.

Incomplete HTML:
{partial_html}

Complete Resume Data:
{formatted_data}

Instructions:
1. Take the partial HTML and complete it with ALL missing content
2. Maintain the same {template_style} style and structure
3. Add any missing sections (work experience, education, skills, etc.)
4. Ensure ALL provided resume data is included
5. Make it flow naturally across multiple pages if needed
6. Return the COMPLETE HTML document

Return ONLY the complete HTML document.
        """
        
        data = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 8000,  # Higher limit for completion
            "temperature": 0.2
        }
        
        result, success = self._make_api_request(data, "html_resume_completion", timeout=120)
        
        if success and result.get("choices"):
            return result["choices"][0]["message"]["content"]
        else:
            return None
