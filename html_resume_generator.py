#!/usr/bin/env python3
"""
HTML Resume Generator - Modern resume generation with templates and themes.
"""

import os
import json
import hashlib
import time
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
import logging
from pathlib import Path

# Import our new template systems
try:
    from professional_templates import professional_templates
    from freelancer_templates import freelancer_templates
    from engineering_templates import engineering_templates
    PROFESSIONAL_TEMPLATES_AVAILABLE = True
except ImportError:
    PROFESSIONAL_TEMPLATES_AVAILABLE = False
    professional_templates = None
    freelancer_templates = None
    engineering_templates = None

logger = logging.getLogger(__name__)

@dataclass
class ColorPalette:
    """Color palette for resume themes."""
    name: str
    primary: str      # Main brand color
    secondary: str    # Accent color  
    text_dark: str    # Dark text color
    text_light: str   # Light text color
    background: str   # Background color
    section_bg: str   # Section background
    border: str       # Border color
    link: str         # Link color

@dataclass
class CacheEntry:
    """Cache entry for storing processed resume results."""
    cache_key: str
    result: Dict[str, Any]
    timestamp: float
    expiry_hours: int = 24  # Cache expires after 24 hours
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        return (time.time() - self.timestamp) > (self.expiry_hours * 3600)

@dataclass 
class ResumeTemplate:
    """Resume template definition."""
    id: str
    name: str
    description: str
    category: str     # modern, classic, creative, minimal
    html_template: str
    css_template: str
    preview_image: Optional[str] = None

class HTMLResumeGenerator:
    """Generate modern HTML resumes with customizable templates and themes."""
    
    def __init__(self, openrouter_client=None):
        """Initialize the HTML resume generator."""
        self.templates_dir = Path("templates")
        self.templates_dir.mkdir(exist_ok=True)
        
        # Store OpenRouter client for AI-powered template adaptation
        self.openrouter_client = openrouter_client
        
        # Initialize built-in color palettes
        self.color_palettes = self._init_color_palettes()
        
        # Initialize built-in templates
        self.templates = self._init_templates()
        
        # Initialize caching system
        self.cache = {}  # In-memory cache: {cache_key: CacheEntry}
        self.cache_dir = Path("cache")
        self.cache_dir.mkdir(exist_ok=True)
        
        # Clear cache on startup for fresh start
        logger.info("🗑️ CLEARING CACHE ON STARTUP for fresh testing")
        self.clear_cache()
        
        # Load existing cache from disk (should be empty after clear)
        self._load_cache_from_disk()
        
        logger.info(f"HTML Resume Generator initialized with {len(self.templates)} templates and {len(self.color_palettes)} color palettes")
        logger.info(f"Cache system initialized with {len(self.cache)} cached entries")
        if self.openrouter_client:
            logger.info("AI-powered template adaptation enabled")
    
    def _init_color_palettes(self) -> Dict[str, ColorPalette]:
        """Initialize built-in color palettes."""
        palettes = {
            "professional_blue": ColorPalette(
                name="Professional Blue",
                primary="#2c5282",      # Deep blue
                secondary="#3182ce",    # Medium blue
                text_dark="#1a202c",    # Very dark gray for maximum contrast
                text_light="#2d3748",   # Darker gray for better readability
                background="#ffffff",   # White
                section_bg="#f7fafc",   # Very light gray
                border="#e2e8f0",       # Light border
                link="#2c5282"          # Darker blue for better contrast
            ),
            "modern_green": ColorPalette(
                name="Modern Green",
                primary="#2f855a",      # Darker green for better contrast
                secondary="#38a169",    # Original green as secondary
                text_dark="#1a202c",    # Very dark gray for maximum contrast
                text_light="#2d3748",   # Darker gray for better readability
                background="#ffffff",   # White
                section_bg="#f0fff4",   # Very light green
                border="#c6f6d5",       # Light green border
                link="#2f855a"          # Darker green for better contrast
            ),
            "elegant_purple": ColorPalette(
                name="Elegant Purple",
                primary="#553c9a",      # Purple - darker for better contrast
                secondary="#7c3aed",    # Light purple
                text_dark="#1a202c",    # Very dark gray for maximum contrast
                text_light="#2d3748",   # Darker gray for better readability
                background="#ffffff",   # White
                section_bg="#faf5ff",   # Very light purple
                border="#e9d8fd",       # Light purple border
                link="#553c9a"          # Darker purple for better contrast
            ),
            "classic_black": ColorPalette(
                name="Classic Black",
                primary="#1a202c",      # Very dark gray
                secondary="#2d3748",    # Dark gray
                text_dark="#1a202c",    # Very dark gray for headings
                text_light="#2d3748",   # Darker gray for better contrast
                background="#ffffff",   # White
                section_bg="#f7fafc",   # Very light gray
                border="#e2e8f0",       # Light border
                link="#1a202c"          # Very dark for maximum contrast
            ),
            "creative_orange": ColorPalette(
                name="Creative Orange",
                primary="#c05621",      # Darker orange for better contrast
                secondary="#dd6b20",    # Original orange as secondary
                text_dark="#1a202c",    # Very dark gray
                text_light="#2d3748",   # Darker gray for better readability
                background="#ffffff",   # White
                section_bg="#fffaf0",   # Very light orange
                border="#fbd38d",       # Light orange border
                link="#c05621"          # Darker orange for better contrast
            ),
            "minimal_gray": ColorPalette(
                name="Minimal Gray",
                primary="#2d3748",      # Darker gray for better contrast
                secondary="#4a5568",    # Medium gray
                text_dark="#1a202c",    # Very dark gray for maximum contrast
                text_light="#2d3748",   # Darker gray for better readability  
                background="#ffffff",   # White
                section_bg="#f7fafc",   # Very light gray
                border="#e2e8f0",       # Light border
                link="#2d3748"          # Darker gray for better contrast
            )
        }
        
        # Validate accessibility for all palettes
        for palette_id, palette in palettes.items():
            accessibility_results = self._validate_color_accessibility(palette)
            accessible_count = sum(accessibility_results.values())
            total_checks = len(accessibility_results)
            logger.info(f"Palette '{palette.name}' accessibility: {accessible_count}/{total_checks} checks passed")
        
        return palettes
    
    def _init_templates(self) -> Dict[str, ResumeTemplate]:
        """Initialize built-in resume templates including professional and freelancer templates."""
        templates = {}
        
        # Add professional templates if available
        if PROFESSIONAL_TEMPLATES_AVAILABLE and professional_templates:
            for template_id, template_data in professional_templates.get_all_templates().items():
                template_info = template_data.get("info")
                if template_info:
                    templates[f"prof_{template_id}"] = ResumeTemplate(
                        id=f"prof_{template_id}",
                        name=template_info.name,
                        description=f"{template_info.description} - Elegant and corporate-ready design",
                        category="business",
                        html_template=template_data.get("html", ""),
                        css_template=template_data.get("css", "")
                    )
        
        # Add freelancer templates if available
        if PROFESSIONAL_TEMPLATES_AVAILABLE and freelancer_templates:
            for template_id, template_data in freelancer_templates.get_all_templates().items():
                template_info = template_data.get("info")
                if template_info:
                    templates[f"freelancer_{template_id}"] = ResumeTemplate(
                        id=f"freelancer_{template_id}",
                        name=template_info.name,
                        description=f"{template_info.description} - Dynamic and versatile layout",
                        category="creative",
                        html_template=template_data.get("html", ""),
                        css_template=template_data.get("css", "")
                    )
        
        # Add engineering templates if available
        if PROFESSIONAL_TEMPLATES_AVAILABLE and engineering_templates:
            for template_id, template_data in engineering_templates.get_all_templates().items():
                template_info = template_data.get("info")
                if template_info:
                    templates[f"eng_{template_id}"] = ResumeTemplate(
                        id=f"eng_{template_id}",
                        name=template_info.name,
                        description=f"{template_info.description} - Technical and structured design for {template_info.experience_level} level",
                        category="technical",
                        html_template=template_data.get("html", ""),
                        css_template=template_data.get("css", "")
                    )
        
        # Original built-in templates (keep as fallback)
        templates["modern"] = ResumeTemplate(
            id="modern",
            name="Sidebar Pro",
            description="Clean sidebar design with excellent information hierarchy",
            category="modern",
            html_template=self._get_modern_html_template(),
            css_template=self._get_modern_css_template()
        )
        
        templates["classic"] = ResumeTemplate(
            id="classic",
            name="Traditional Elite",
            description="Timeless single-column layout, perfect for conservative industries",
            category="classic", 
            html_template=self._get_classic_html_template(),
            css_template=self._get_classic_css_template()
        )
        
        # Creative Template
        templates["creative"] = ResumeTemplate(
            id="creative",
            name="Bold Expression",
            description="Eye-catching design with strong visual impact and personality",
            category="creative",
            html_template=self._get_creative_html_template(),
            css_template=self._get_creative_css_template()
        )
        
        # Minimal Template
        templates["minimal"] = ResumeTemplate(
            id="minimal",
            name="Pure Minimalist",
            description="Ultra-clean design focusing on content clarity and readability",
            category="minimal",
            html_template=self._get_minimal_html_template(),
            css_template=self._get_minimal_css_template()
        )
        
        # Shine Template (inspired by xriley/Shine-Theme)
        templates["shine"] = ResumeTemplate(
            id="shine",
            name="Contemporary Shine",
            description="Modern responsive design with polished aesthetics",
            category="modern",
            html_template=self._get_shine_html_template(),
            css_template=self._get_shine_css_template()
        )
        
        # Timeline Template
        templates["timeline"] = ResumeTemplate(
            id="timeline",
            name="Career Journey",
            description="Chronological timeline showcasing professional progression",
            category="modern",
            html_template=self._get_timeline_html_template(),
            css_template=self._get_timeline_css_template()
        )
        
        # Card Template
        templates["card"] = ResumeTemplate(
            id="card",
            name="Sectioned Cards",
            description="Organized card-based layout with clear visual separation",
            category="modern",
            html_template=self._get_card_html_template(),
            css_template=self._get_card_css_template()
        )
        
        # Split Template
        templates["split"] = ResumeTemplate(
            id="split",
            name="Dual Column",
            description="Balanced two-panel design for optimal information distribution",
            category="modern",
            html_template=self._get_split_html_template(),
            css_template=self._get_split_css_template()
        )
        
        # Gradient Template
        templates["gradient"] = ResumeTemplate(
            id="gradient",
            name="Dynamic Gradients",
            description="Modern design with subtle gradient backgrounds and visual depth",
            category="creative",
            html_template=self._get_gradient_html_template(),
            css_template=self._get_gradient_css_template()
        )
        
        # Balanced Template (optimized space utilization)
        templates["balanced"] = ResumeTemplate(
            id="balanced",
            name="Space Optimized",
            description="Intelligently balanced layout that maximizes space utilization and content density",
            category="professional",
            html_template=self._get_balanced_html_template(),
            css_template=self._get_balanced_css_template()
        )
        
        return templates
    
    def adapt_resume_for_role(self, resume_data: Dict, target_role: str) -> Dict:
        """Adapt resume content for a specific target role using AI."""
        logger.info(f"🎯 Role adaptation requested for: {target_role}")
        logger.info(f"📊 Resume data keys: {list(resume_data.keys())}")
        
        if not self.openrouter_client:
            logger.warning("❌ No OpenRouter client available")
            return resume_data
            
        if target_role == "None (Original)":
            logger.info("ℹ️ Target role is 'None (Original)', returning original data")
            return resume_data
        
        # PHASE 1: Check cache for role adaptation
        logger.info(f"🔄 ROLE ADAPTATION PHASE 1: Checking cache for {target_role}")
        cache_key = self._generate_cache_key(resume_data, "role_adaptation", "none", target_role=target_role)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            # Return the cached adapted resume data
            logger.info(f"🚀 ROLE ADAPTATION CACHE HIT - Using cached result for: {target_role}")
            return cached_result.get('adapted_data', resume_data)
        
        logger.info(f"🔄 ROLE ADAPTATION PHASE 2: Cache miss - proceeding with AI adaptation")
            
        try:
            import json
            
            # Create adapted resume data copy
            adapted_resume = resume_data.copy()
            
            # Define role-specific adaptation prompts
            role_adaptations = {
                "Software Engineer": {
                    "focus": "technical skills, programming languages, software development lifecycle, code quality",
                    "keywords": ["programming", "software development", "algorithms", "debugging", "testing", "code review"]
                },
                "Frontend Developer": {
                    "focus": "UI/UX skills, JavaScript frameworks, responsive design, user experience",
                    "keywords": ["React", "Vue", "Angular", "HTML", "CSS", "JavaScript", "responsive design", "user interface"]
                },
                "Backend Developer": {
                    "focus": "server-side development, databases, APIs, system architecture",
                    "keywords": ["API", "database", "server", "backend", "microservices", "system design", "scalability"]
                },
                "Data Scientist": {
                    "focus": "data analysis, machine learning, statistical modeling, research",
                    "keywords": ["machine learning", "data analysis", "Python", "R", "statistics", "modeling", "research"]
                },
                "Product Manager": {
                    "focus": "product strategy, stakeholder management, market analysis, user research",
                    "keywords": ["product strategy", "roadmap", "stakeholder management", "user research", "market analysis"]
                },
                "DevOps Engineer": {
                    "focus": "CI/CD, infrastructure, automation, cloud platforms, monitoring",
                    "keywords": ["CI/CD", "Docker", "Kubernetes", "AWS", "automation", "infrastructure", "monitoring"]
                }
            }
            
            adaptation_info = role_adaptations.get(target_role, {
                "focus": "relevant skills and experiences for the target role",
                "keywords": []
            })
            
            # Simplified approach: adapt just the key textual content
            resume_text = []
            
            # Handle both 'experience' and 'job_experiences' keys
            experience_key = None
            if 'experience' in resume_data:
                experience_key = 'experience'
            elif 'job_experiences' in resume_data:
                experience_key = 'job_experiences'
            
            if experience_key:
                experience_data = resume_data[experience_key]
                logger.info(f"📝 Found {len(experience_data)} experience entries using key '{experience_key}'")
                
                for i, exp in enumerate(experience_data):
                    if isinstance(exp, dict):
                        # Try multiple possible keys for job title
                        job_title = exp.get('job_title') or exp.get('title') or exp.get('position') or 'N/A'
                        
                        # Try multiple possible keys for description
                        description = exp.get('description') or exp.get('summary') or exp.get('responsibilities') or ''
                        
                        # If description is a list, join it
                        if isinstance(description, list):
                            description = '. '.join(str(item) for item in description if item)
                        
                        if description:
                            resume_text.append(f"Job: {job_title} - {description}")
                            logger.debug(f"Experience {i}: {job_title} - {str(description)[:50]}...")
                        else:
                            logger.warning(f"Experience entry {i} has no description field")
                    else:
                        logger.warning(f"Experience entry {i} is not a dict: {type(exp)}")
            else:
                logger.warning("⚠️ No 'experience' or 'job_experiences' key in resume data")
            
            if 'skills' in resume_data:
                skills_data = resume_data['skills']
                logger.info(f"🛠️ Found skills data: {type(skills_data)}")
                logger.debug(f"🛠️ Skills data sample: {str(skills_data)[:100]}...")
                
                skills_list = []
                if isinstance(skills_data, list):
                    for skill in skills_data:
                        if isinstance(skill, dict):
                            # Extract skill name from dict (try common keys)
                            skill_name = skill.get('name') or skill.get('skill') or skill.get('title') or str(skill)
                            skills_list.append(str(skill_name))
                        else:
                            skills_list.append(str(skill))
                elif isinstance(skills_data, str):
                    skills_list = [skills_data]
                else:
                    skills_list = [str(skills_data)]
                
                skills_text = ', '.join(skills_list)
                resume_text.append(f"Skills: {skills_text}")
                logger.debug(f"Skills: {skills_text}")
            else:
                logger.warning("⚠️ No 'skills' key in resume data")
            
            current_text = '\n'.join(resume_text)
            logger.info(f"📄 Extracted text for adaptation: {len(current_text)} chars")
            logger.debug(f"Text sample: {current_text[:200]}...")
            
            # Build comprehensive adaptation prompt
            prompt = f"""
            Adapt this resume content for a {target_role} position. KEEP ALL EXISTING FACTS, DATES, COMPANIES, AND ACHIEVEMENTS. Only reframe the language and emphasis to highlight skills relevant to {adaptation_info['focus']}. Use keywords like: {', '.join(adaptation_info['keywords'])}.

            Current resume content:
            Professional Summary: {resume_data.get('professional_summary', 'N/A')}
            {current_text}

            RULES:
            1. Keep all original companies, dates, technologies, and specific achievements
            2. Only change the wording and emphasis to match {target_role} requirements
            3. Job descriptions must be in bullet point format with • symbols
            4. Do not invent new information - only reframe existing content
            5. Use clean text without quotes or extra formatting

            IMPORTANT: Return the adapted content in EXACTLY this plain text format (no markdown, no bold formatting):

            Summary: [Reframed professional summary emphasizing {target_role} skills]
            Job: {target_role} - • [Reframed detailed bullet point 1] • [Reframed detailed bullet point 2] • [Reframed detailed bullet point 3] • [Reframed detailed bullet point 4] • [Reframed detailed bullet point 5] • [Additional points as needed]
            Job: {target_role} - • [Reframed detailed bullet point 1] • [Reframed detailed bullet point 2] • [Reframed detailed bullet point 3] • [Reframed detailed bullet point 4] • [Reframed detailed bullet point 5] • [Additional points as needed]  
            Job: {target_role} - • [Reframed detailed bullet point 1] • [Reframed detailed bullet point 2] • [Reframed detailed bullet point 3] • [Reframed detailed bullet point 4] • [Reframed detailed bullet point 5] • [Additional points as needed]
            Skills: [Same skills list with {target_role}-focused emphasis]
            
            CRITICAL: 
            1. You MUST provide a "Job:" line for EVERY job position in the resume. Count the jobs in the current resume and provide exactly that many "Job:" lines.
            2. For each job, maintain the SAME NUMBER of bullet points as the original (or more if beneficial). Do NOT reduce the detail level.
            3. Each bullet point should be substantial and detailed, preserving all specific achievements, technologies, metrics, and accomplishments.
            4. Only change the wording and emphasis to highlight {target_role} skills, but keep all factual details.
            
            Use ONLY plain text format. Do NOT use markdown formatting like **bold** or *italics*. 
            Start each line with the exact keywords shown above (Summary:, Job:, Skills:).
            PRESERVE all factual information - only adjust the presentation and emphasis.
            """

            # Early exit if no content to adapt
            if not current_text.strip():
                logger.warning("⚠️ No content found to adapt")
                return resume_data
            
            logger.info(f"🤖 Making OpenRouter API call for role adaptation: {target_role}")
            logger.debug(f"📤 Sending prompt (first 300 chars): {prompt[:300]}...")
            
            try:
                response = self.openrouter_client._make_request(prompt, max_tokens=4000)
                logger.info(f"📨 Received response: {len(response)} chars")
                logger.debug(f"Response preview: {response[:100]}...")
            except Exception as api_error:
                logger.error(f"❌ OpenRouter API call failed: {api_error}")
                return resume_data
            
            # Parse the simplified response and update the resume data
            try:
                adapted_content = response.strip()
                logger.info(f"🔍 PARSING AI RESPONSE - Total length: {len(adapted_content)} chars")
                logger.debug(f"📄 Full AI response: {adapted_content}")
                
                # Create a copy of the original resume data
                adapted_data = resume_data.copy()
                logger.info(f"📋 ORIGINAL DATA KEYS: {list(adapted_data.keys())}")
                
                # Log original values for comparison
                original_summary = adapted_data.get('professional_summary', 'N/A')
                logger.info(f"📝 ORIGINAL SUMMARY: {original_summary[:100]}...")
                
                if 'job_experiences' in adapted_data:
                    for i, job in enumerate(adapted_data['job_experiences']):
                        original_title = self._safe_get_value(job, 'job_title', 'N/A')
                        logger.info(f"📊 ORIGINAL JOB {i}: {original_title}")
                
                # Parse the response line by line
                lines = adapted_content.split('\n')
                job_updates = []  # Changed to list to preserve order and handle multiple jobs
                skills_update = None
                summary_update = None
                
                logger.info(f"🔍 PARSING {len(lines)} LINES from AI response:")
                for line_num, line in enumerate(lines):
                    line = line.strip()
                    logger.debug(f"Line {line_num}: '{line}'")
                    
                    # Handle both plain and markdown formats
                    if line.startswith('Summary:') or line.startswith('**Summary:**'):
                        if line.startswith('**Summary:**'):
                            summary_update = line[12:].strip()  # Remove "**Summary:**" prefix
                        else:
                            summary_update = line[8:].strip()  # Remove "Summary:" prefix
                        logger.info(f"✅ FOUND SUMMARY UPDATE: {summary_update[:100]}...")
                    elif line.startswith('Job:') or line.startswith('**Job:**'):
                        # Extract job title and description
                        if line.startswith('**Job:**'):
                            job_part = line[8:].strip()  # Remove "**Job:**" prefix
                        else:
                            job_part = line[4:].strip()  # Remove "Job:" prefix
                        
                        if ' - ' in job_part:
                            job_title, description = job_part.split(' - ', 1)
                            job_updates.append((job_title.strip(), description.strip()))  # Store as tuple
                            logger.info(f"✅ FOUND JOB UPDATE {len(job_updates)}: '{job_title.strip()}' - {description[:50]}...")
                        else:
                            logger.warning(f"⚠️ MALFORMED JOB LINE: {line}")
                    elif line.startswith('Skills:') or line.startswith('**Skills:**'):
                        if line.startswith('**Skills:**'):
                            skills_update = line[11:].strip()  # Remove "**Skills:**" prefix
                        else:
                            skills_update = line[7:].strip()  # Remove "Skills:" prefix
                        logger.info(f"✅ FOUND SKILLS UPDATE: {skills_update[:50]}...")
                    elif line.strip() and not line.startswith('#') and not line.startswith('---'):
                        logger.debug(f"📄 UNPARSED LINE: {line}")
                
                logger.info(f"🎯 PARSING COMPLETE - Found {len(job_updates)} jobs, summary: {bool(summary_update)}, skills: {bool(skills_update)}")
                
                # Apply updates to experience (using the correct key)
                if experience_key and experience_key in adapted_data and job_updates:
                    logger.info(f"🔄 APPLYING UPDATES - {len(job_updates)} job updates to {len(adapted_data[experience_key])} existing jobs")
                    update_items = job_updates  # Already a list of tuples
                    logger.info(f"📊 AVAILABLE UPDATES: {[title for title, _ in update_items]}")
                    
                    for i, exp in enumerate(adapted_data[experience_key]):
                        if isinstance(exp, dict):
                            # Get original job title using flexible key matching
                            original_job_title = exp.get('job_title') or exp.get('title') or exp.get('position') or 'N/A'
                            original_desc = exp.get('description', ['N/A'])[0] if isinstance(exp.get('description', []), list) else exp.get('description', 'N/A')
                            
                            logger.info(f"🔍 PROCESSING JOB {i}: '{original_job_title}'")
                            logger.debug(f"📝 Original desc: {str(original_desc)[:50]}...")
                            
                            # Find matching updated job (by index or approximate match)
                            if i < len(update_items):
                                update_title, new_desc = update_items[i]
                                
                                # Update BOTH job title and description
                                title_key = 'job_title' if 'job_title' in exp else 'title' if 'title' in exp else 'position'
                                desc_key = 'description' if 'description' in exp else 'summary' if 'summary' in exp else 'responsibilities'
                                
                                logger.info(f"🔧 UPDATING KEYS: title_key='{title_key}', desc_key='{desc_key}'")
                                
                                # Update the job title to the adapted one
                                adapted_data[experience_key][i][title_key] = update_title
                                # Update the description to the adapted one  
                                adapted_data[experience_key][i][desc_key] = new_desc
                                
                                # Verify the update worked
                                updated_title = adapted_data[experience_key][i][title_key]
                                updated_desc = adapted_data[experience_key][i][desc_key]
                                
                                logger.info(f"✅ SUCCESSFULLY UPDATED JOB {i}:")
                                logger.info(f"   📊 TITLE: '{original_job_title}' → '{updated_title}'")
                                logger.info(f"   📝 DESC: {str(updated_desc)[:50]}...")
                                
                                if updated_title != update_title:
                                    logger.error(f"❌ TITLE UPDATE FAILED! Expected: '{update_title}', Got: '{updated_title}'")
                                    
                            else:
                                logger.warning(f"⚠️ NO UPDATE AVAILABLE for job {i}: '{original_job_title}' (only {len(update_items)} updates available)")
                        else:
                            logger.warning(f"⚠️ JOB {i} is not a dict: {type(exp)}")
                else:
                    logger.warning(f"⚠️ SKIPPING JOB UPDATES - experience_key: {experience_key}, has_updates: {bool(job_updates)}")
                
                # Apply professional summary update
                if summary_update:
                    original_summary = adapted_data.get('professional_summary', 'N/A')
                    adapted_data['professional_summary'] = summary_update
                    logger.info(f"✅ SUMMARY UPDATE APPLIED:")
                    logger.info(f"   📝 OLD: {original_summary[:50]}...")
                    logger.info(f"   📝 NEW: {summary_update[:50]}...")
                    
                    # Verify the update worked
                    final_summary = adapted_data.get('professional_summary')
                    if final_summary != summary_update:
                        logger.error(f"❌ SUMMARY UPDATE FAILED! Expected: {summary_update[:30]}..., Got: {final_summary[:30] if final_summary else 'None'}...")
                else:
                    logger.warning(f"⚠️ NO SUMMARY UPDATE FOUND in AI response")
                
                # Apply skills update while preserving structure
                if skills_update:
                    logger.info(f"📊 SKILLS UPDATE (preserved structure): {skills_update[:50]}...")
                else:
                    logger.warning(f"⚠️ NO SKILLS UPDATE FOUND in AI response")
                
                # Mark as adapted and log final state
                adapted_data['_role_adapted'] = target_role
                
                logger.info(f"🎯 FINAL ADAPTED DATA VERIFICATION:")
                logger.info(f"   📋 Keys: {list(adapted_data.keys())}")
                logger.info(f"   🎯 Role marker: {adapted_data.get('_role_adapted')}")
                logger.info(f"   📝 Summary (final): {adapted_data.get('professional_summary', 'N/A')[:50]}...")
                
                if 'job_experiences' in adapted_data:
                    logger.info(f"   📊 Final job titles:")
                    for i, job in enumerate(adapted_data['job_experiences']):
                        final_title = self._safe_get_value(job, 'job_title', 'N/A')
                        logger.info(f"      Job {i}: '{final_title}'")
                
                logger.info(f"✅ ROLE ADAPTATION PHASE 3: Successfully completed for {target_role}")
                
                # PHASE 4: Cache the successful role adaptation
                logger.info(f"🔄 ROLE ADAPTATION PHASE 4: Saving to cache")
                cache_result = {"adapted_data": adapted_data}
                self._save_to_cache(cache_key, cache_result, expiry_hours=12)  # Cache for 12 hours
                
                logger.info(f"🎯 ROLE ADAPTATION COMPLETED - All phases finished for {target_role}")
                return adapted_data
                
            except Exception as e:
                logger.warning(f"Failed to parse AI response for role adaptation: {target_role}, Error: {e}")
                logger.debug(f"Raw response: {response[:500]}...")
                return resume_data
                
        except Exception as e:
            logger.error(f"Role adaptation failed: {e}")
            return resume_data
    
    def generate_resume_html(self, 
                           resume_data: Dict[str, Any], 
                           template_id: str = "modern",
                           palette_id: str = "professional_blue",
                           country_standards: Dict[str, Any] = None,
                           profile_image_data: bytes = None,
                           translate_content: bool = False) -> Dict[str, str]:
        """
        Generate complete HTML resume with template and color palette.
        
        Args:
            resume_data: Parsed resume data
            template_id: Template to use
            palette_id: Color palette to use
            
        Returns:
            Dict with 'html' and 'css' keys
        """
        
        logger.info(f"🎨 GENERATE_RESUME_HTML STARTED")
        logger.info(f"   📋 Template: {template_id}")
        logger.info(f"   🎨 Palette: {palette_id}")
        logger.info(f"   📊 Resume data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else 'Not dict'}")
        
        # PHASE 1: Check template generation cache
        logger.info(f"🔄 TEMPLATE GENERATION PHASE 1: Checking cache")
        cache_key = self._generate_cache_key(resume_data, template_id, palette_id)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            logger.info(f"🚀 TEMPLATE GENERATION CACHE HIT - Using cached result")
            return cached_result
            
        logger.info(f"🔄 TEMPLATE GENERATION PHASE 2: Cache miss - proceeding with generation")
        
        # Check if this is role-adapted data at the start of HTML generation
        if resume_data.get('_role_adapted'):
            logger.info(f"🎯 HTML GENERATION - Role-adapted data detected: {resume_data['_role_adapted']}")
            adapted_summary = resume_data.get('professional_summary', 'N/A')
            logger.info(f"   📝 Role-adapted summary: {adapted_summary[:100]}...")
            
            # Log job titles at HTML generation start
            job_experiences = resume_data.get('job_experiences', [])
            if job_experiences:
                logger.info(f"   📊 Role-adapted job titles at HTML gen start:")
                for i, job in enumerate(job_experiences):
                    job_title = self._safe_get_value(job, 'job_title', 'N/A')
                    logger.info(f"      Job {i}: '{job_title}'")
        else:
            logger.info(f"📋 HTML GENERATION - Original (non-adapted) data")
        
        if template_id not in self.templates:
            raise ValueError(f"Template '{template_id}' not found")
        
        if palette_id not in self.color_palettes:
            raise ValueError(f"Color palette '{palette_id}' not found")
        
        template = self.templates[template_id]
        palette = self.color_palettes[palette_id]
        
        logger.info(f"✅ Template and palette loaded successfully")
        
        # Use AI-powered template adaptation for ALL templates if OpenRouter client is available
        if self.openrouter_client:
            try:
                logger.info(f"Using AI-powered adaptation for template: {template_id}")
                
                # Get template info for AI context
                template_info = {
                    'name': template.name,
                    'description': template.description,
                    'category': template.category
                }
                
                # Get template with CSS embedded for AI processing
                template_with_css = f"""
<!DOCTYPE html>
<html>
<head>
<style>
{self._apply_color_palette(template.css_template, palette)}
</style>
</head>
<body>
{template.html_template}
</body>
</html>
                """
                
                # Get original layout analysis if available
                original_layout_analysis = None
                if hasattr(resume_data, 'get') and 'analysis_data' in resume_data:
                    analysis_data = resume_data.get('analysis_data', {})
                    if 'layout_analysis' in analysis_data:
                        original_layout_analysis = analysis_data['layout_analysis']
                
                # Use AI to adapt resume data to template with country standards, profile image, translation, and layout analysis
                complete_html = self.openrouter_client.adapt_resume_to_template(
                    resume_data, 
                    template_info,
                    template_with_css,
                    country_standards=country_standards,
                    profile_image_data=profile_image_data,
                    translate_content=translate_content,
                    original_layout_analysis=original_layout_analysis
                )
                
                if complete_html and not complete_html.startswith("Error:"):
                    # Parse the AI-generated HTML back into HTML and CSS
                    if '<style>' in complete_html:
                        css_start = complete_html.find('<style>') + 7
                        css_end = complete_html.find('</style>')
                        ai_css_content = complete_html[css_start:css_end]
                        
                        html_start = complete_html.find('<body>') + 6
                        html_end = complete_html.find('</body>')
                        ai_html_content = complete_html[html_start:html_end]
                        
                        logger.info("Successfully generated AI-adapted template content")
                        return {
                            "html": ai_html_content,
                            "css": ai_css_content,
                            "template": template_id,
                            "palette": palette_id,
                            "ai_adapted": True
                        }
                    else:
                        # Fallback: treat entire response as HTML
                        logger.warning("AI response didn't contain expected CSS structure, using as HTML")
                        css_content = self._apply_color_palette(template.css_template, palette)
                        return {
                            "html": complete_html,
                            "css": css_content,
                            "template": template_id,
                            "palette": palette_id,
                            "ai_adapted": True
                        }
                else:
                    logger.warning(f"AI template adaptation failed: {complete_html[:100]}...")
                    
            except Exception as e:
                logger.error(f"AI template adaptation error: {e}")
        
        # Fallback to traditional template population
        logger.info(f"🔧 USING TRADITIONAL TEMPLATE POPULATION for: {template_id}")
        html_content = self._populate_html_template(
            template.html_template, 
            resume_data,
            template_id,
            profile_image_data
        )
        
        logger.info(f"📄 HTML TEMPLATE POPULATION COMPLETED")
        logger.info(f"   📏 Generated HTML length: {len(html_content)} chars")
        logger.debug(f"   📄 HTML preview (first 200 chars): {html_content[:200]}")
        
        # Check if role-adapted content made it into HTML
        if resume_data.get('_role_adapted'):
            role = resume_data['_role_adapted']
            logger.info(f"🔍 CHECKING ROLE-ADAPTED CONTENT IN GENERATED HTML:")
            
            # Check for adapted job titles in HTML
            job_experiences = resume_data.get('job_experiences', [])
            for i, job in enumerate(job_experiences):
                job_title = self._safe_get_value(job, 'job_title', 'N/A')
                if job_title.lower() in html_content.lower():
                    logger.info(f"   ✅ Job {i} title '{job_title}' FOUND in HTML")
                else:
                    logger.error(f"   ❌ Job {i} title '{job_title}' NOT FOUND in HTML")
            
            # Check for adapted summary
            adapted_summary = resume_data.get('professional_summary', '')
            if adapted_summary and adapted_summary[:50] in html_content:
                logger.info(f"   ✅ Adapted summary FOUND in HTML")
            else:
                logger.error(f"   ❌ Adapted summary NOT FOUND in HTML")
                logger.debug(f"   📝 Looking for: {adapted_summary[:50]}...")
        
        # Generate CSS with color palette
        css_content = self._apply_color_palette(
            template.css_template,
            palette
        )
        
        logger.info(f"🎨 CSS GENERATION COMPLETED")
        logger.info(f"   📏 Generated CSS length: {len(css_content)} chars")
        
        # Final result logging
        result = {
            "html": html_content,
            "css": css_content,
            "template": template_id,
            "palette": palette_id,
            "ai_adapted": False
        }
        
        # Replace image placeholder if profile image data is provided
        if profile_image_data:
            result = self._replace_image_placeholder(result, profile_image_data)
        
        logger.info(f"🔄 TEMPLATE GENERATION PHASE 3: Generation completed successfully")
        logger.info(f"   📊 Result keys: {list(result.keys())}")
        logger.info(f"   📄 Total HTML size: {len(result['html'])} chars")
        logger.info(f"   🎨 Total CSS size: {len(result['css'])} chars")
        
        # PHASE 4: Cache the result for future use
        logger.info(f"🔄 TEMPLATE GENERATION PHASE 4: Saving to cache")
        self._save_to_cache(cache_key, result)
        
        logger.info(f"🎯 TEMPLATE GENERATION COMPLETED - All phases finished")
        
        # Replace image placeholder if profile image data is provided
        if profile_image_data:
            result = self._replace_image_placeholder(result, profile_image_data)
        
        return result
    
    def _replace_image_placeholder(self, html_result: Dict[str, str], profile_image_data) -> Dict[str, str]:
        """Replace image placeholders with actual base64 image data."""
        import base64
        import re
        
        if not profile_image_data:
            return html_result
        
        # Extract image data
        if isinstance(profile_image_data, dict):
            image_b64 = profile_image_data.get('data', '')
            image_type = profile_image_data.get('type', 'image/jpeg').replace('image/', '')
        else:
            # Fallback for direct bytes
            image_b64 = base64.b64encode(profile_image_data).decode('utf-8')
            image_type = 'jpeg'
        
        if not image_b64:
            logger.warning("No image data found in profile_image_data")
            return html_result
        
        # Create the data URI
        data_uri = f"data:image/{image_type};base64,{image_b64}"
        
        # Replace placeholder in HTML
        html_content = html_result.get('html', '')
        replacements_made = 0
        
        # 1. Replace direct placeholder tokens (Modern template)
        if '{{PROFILE_IMAGE_PLACEHOLDER}}' in html_content:
            html_content = html_content.replace('{{PROFILE_IMAGE_PLACEHOLDER}}', data_uri)
            replacements_made += 1
            logger.info("✅ Successfully replaced {{PROFILE_IMAGE_PLACEHOLDER}} with actual image data")
        
        # 2. Replace profile-image-placeholder divs (Shine template)
        placeholder_pattern = r'<div[^>]*class="[^"]*profile-image-placeholder[^"]*"[^>]*></div>'
        if re.search(placeholder_pattern, html_content):
            circular_img = f'<img src="{data_uri}" class="profile-photo circular" alt="Professional headshot" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid rgba(255,255,255,0.3);">'
            html_content = re.sub(placeholder_pattern, circular_img, html_content)
            replacements_made += 1
            logger.info("✅ Successfully replaced profile-image-placeholder div with circular image")
        
        # 3. Replace profile-gradient-circle content (Gradient template)  
        gradient_pattern = r'<div[^>]*class="[^"]*profile-gradient-circle[^"]*"[^>]*>.*?</div>'
        if re.search(gradient_pattern, html_content, re.DOTALL):
            circular_img = f'<div class="profile-gradient-circle"><img src="{data_uri}" class="profile-photo circular" alt="Professional headshot" style="width: 150px; height: 150px; border-radius: 50%; object-fit: cover; border: 4px solid rgba(255,255,255,0.3);"></div>'
            html_content = re.sub(gradient_pattern, circular_img, html_content, flags=re.DOTALL)
            replacements_made += 1
            logger.info("✅ Successfully replaced profile-gradient-circle with circular image")
        
        # 4. Replace profile-circle content (Card template)
        circle_pattern = r'<div[^>]*class="[^"]*profile-circle[^"]*"[^>]*>.*?</div>'
        if re.search(circle_pattern, html_content, re.DOTALL):
            circular_img = f'<div class="profile-circle"><img src="{data_uri}" class="profile-photo circular" alt="Professional headshot" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid rgba(255,255,255,0.2);"></div>'
            html_content = re.sub(circle_pattern, circular_img, html_content, flags=re.DOTALL)
            replacements_made += 1
            logger.info("✅ Successfully replaced profile-circle with circular image")
        
        # 5. Handle profile-avatar circles (Timeline template)
        avatar_pattern = r'<div[^>]*class="[^"]*profile-avatar[^"]*"[^>]*>.*?</div>'
        if re.search(avatar_pattern, html_content, re.DOTALL):
            circular_img = f'<div class="profile-avatar"><img src="{data_uri}" class="profile-photo circular" alt="Professional headshot" style="width: 120px; height: 120px; border-radius: 50%; object-fit: cover; border: 3px solid #fff;"></div>'
            html_content = re.sub(avatar_pattern, circular_img, html_content, flags=re.DOTALL)
            replacements_made += 1
            logger.info("✅ Successfully replaced profile-avatar with circular image")
        
        if replacements_made == 0:
            logger.warning("⚠️ No image placeholders found in HTML content")
        else:
            logger.info(f"✅ Made {replacements_made} image replacements")
        
        # Update the result
        return {
            **html_result,
            'html': html_content
        }
    
    def generate_original_format_html(self, 
                                    resume_data: Dict[str, Any],
                                    original_analysis: Dict[str, Any] = None,
                                    enhancement_level: str = "minimal",
                                    palette_id: str = "professional_blue") -> Dict[str, str]:
        """
        Generate HTML that preserves the original resume format and layout.
        
        Args:
            resume_data: Parsed resume data
            original_analysis: Analysis data from the original resume (positioning, fonts, etc.)
            enhancement_level: Level of enhancement (minimal, enhanced, modernized)
            palette_id: Color palette to use
            
        Returns:
            Dict with 'html' and 'css' keys that mimic original layout
        """
        
        if palette_id not in self.color_palettes:
            palette_id = "professional_blue"  # fallback
        
        # Check cache first
        cache_key = self._generate_cache_key(resume_data, "original_format", palette_id, 
                                           enhancement_level=enhancement_level)
        cached_result = self._get_from_cache(cache_key)
        if cached_result:
            return cached_result
        
        palette = self.color_palettes[palette_id]
        
        # Generate HTML that preserves original structure
        html_content = self._generate_original_layout_html(resume_data, original_analysis)
        
        # Generate CSS that matches original formatting
        css_content = self._generate_original_layout_css(
            resume_data, 
            original_analysis, 
            enhancement_level, 
            palette
        )
        
        result = {
            "html": html_content,
            "css": css_content,
            "template": "original_format",
            "palette": palette_id,
            "enhancement_level": enhancement_level
        }
        
        # Cache the result
        self._save_to_cache(cache_key, result)
        
        return result
    
    def _populate_html_template(self, html_template: str, resume_data: Dict[str, Any], template_id: str = "", profile_image_data: Dict[str, Any] = None) -> str:
        """
        Populate HTML template with resume data, handling both old and new template formats.
        Also dynamically adds missing sections to templates.
        """
        
        # Log template population details
        logger.info(f"📋 Populating template '{template_id}' with resume data")
        logger.debug(f"🔍 Resume data keys: {list(resume_data.keys()) if isinstance(resume_data, dict) else 'Not a dict'}")
        
        # Check if this is role-adapted data
        if resume_data.get('_role_adapted'):
            logger.info(f"🎯 TEMPLATE POPULATION - Processing role-adapted data for: {resume_data['_role_adapted']}")
            
            # Log professional summary
            adapted_summary = resume_data.get('professional_summary', 'N/A')
            logger.info(f"📝 ADAPTED SUMMARY in template data: {adapted_summary[:100]}...")
            
            # Log work experience sample to verify adapted content
            job_experiences = resume_data.get('job_experiences', [])
            if job_experiences:
                logger.info(f"📊 ADAPTED JOBS in template data ({len(job_experiences)} total):")
                for i, job in enumerate(job_experiences):
                    job_title = self._safe_get_value(job, 'job_title', 'No title')
                    job_desc = self._safe_get_value(job, 'description', 'No description')
                    logger.info(f"   Job {i}: '{job_title}' - {str(job_desc)[:50]}...")
            else:
                logger.warning(f"⚠️ NO JOB EXPERIENCES found in adapted data!")
        else:
            logger.info(f"📋 TEMPLATE POPULATION - Processing original (non-adapted) resume data")
        
        # Extract data with safe defaults
        contact_info = resume_data.get('contact_info', {})
        name = self._safe_get_value(contact_info, 'name', 'Your Name')
        email = self._safe_get_value(contact_info, 'email', 'your.email@example.com')
        phone = self._safe_get_value(contact_info, 'phone', '(555) 123-4567')
        location = self._safe_get_value(contact_info, 'location', 'Your Location')
        linkedin = self._safe_get_value(contact_info, 'linkedin', '')
        github = self._safe_get_value(contact_info, 'github', '')
        
        professional_summary = resume_data.get('professional_summary', 'Experienced professional with a track record of success in delivering high-quality solutions and driving business growth.')
        
        # Build sections with comprehensive data and ensure they return strings
        work_experience_html = self._ensure_string_output(self._build_work_experience_section(resume_data.get('job_experiences', [])), "work_experience")
        education_html = self._ensure_string_output(self._build_education_section(resume_data.get('education', [])), "education")
        skills_html = self._ensure_string_output(self._build_skills_section(resume_data.get('skills', [])), "skills")
        projects_html = self._ensure_string_output(self._build_projects_section(resume_data.get('projects', [])), "projects")
        certifications_html = self._ensure_string_output(self._build_certifications_section(resume_data.get('certifications', [])), "certifications")
        
        # Generate name initials for avatar (only if we have a name)
        name_initials = ""
        if name and name != "Your Name":
            name_parts = name.strip().split()
            if len(name_parts) >= 2:
                name_initials = (name_parts[0][0] + name_parts[-1][0]).upper()
            elif len(name_parts) == 1:
                name_initials = name_parts[0][:2].upper()
        
        # Create replacement mapping for both old and new template formats
        replacements = {
            # Old format (legacy templates)
            "{{name}}": name,
            "{{email}}": email,
            "{{phone}}": phone,
            "{{location}}": location,
            "{{linkedin}}": linkedin,
            "{{github}}": github,
            "{{professional_summary}}": professional_summary,
            "{{experience_section}}": work_experience_html,
            "{{education_section}}": education_html,
            "{{skills_section}}": skills_html,
            
            # New format (professional templates)
            "{{NAME}}": name,
            "{{EMAIL}}": email,
            "{{PHONE}}": phone,
            "{{LOCATION}}": location,
            "{{LINKEDIN}}": linkedin,
            "{{GITHUB}}": github,
            "{{PROFESSIONAL_SUMMARY}}": professional_summary,
            "{{WORK_EXPERIENCE}}": work_experience_html,
            "{{EDUCATION}}": education_html,
            "{{SKILLS}}": skills_html,
            "{{PROJECTS}}": projects_html,
            "{{CERTIFICATIONS}}": certifications_html,
            
            # Additional professional template placeholders
            "{{JOB_TITLE}}": self._infer_job_title(resume_data),
            "{{PROFESSIONAL_TITLE}}": self._infer_job_title(resume_data),
            "{{TAGLINE}}": self._generate_tagline(resume_data),
            "{{PORTFOLIO_URL}}": github or linkedin,
            "{{AVAILABILITY}}": "Available for new opportunities",
            "{{SERVICES}}": self._ensure_string_output(self._build_services_section(resume_data), "services"),
            "{{CLIENT_WORK}}": work_experience_html,  # Map to work experience for professional context
            "{{TECHNICAL_SKILLS}}": self._ensure_string_output(self._build_technical_skills_section(resume_data.get('skills', [])), "technical_skills"),
            "{{TESTIMONIALS}}": self._ensure_string_output(self._build_testimonials_section(resume_data.get('testimonials', [])), "testimonials"),
            "{{EDUCATION_CERTIFICATIONS}}": education_html + certifications_html,
            
            # Avatar and image placeholders
            "{{name_initials}}": name_initials
        }
        
        # Handle profile image placeholder logic
        if profile_image_data:
            # Add image placeholder that will be replaced later
            profile_image_html = '<img src="{{PROFILE_IMAGE_PLACEHOLDER}}" class="profile-photo" alt="Professional headshot" style="width: 150px; height: 200px; border-radius: 8px; border: 2px solid #ddd;">'
            replacements.update({
                "{{PROFILE_IMAGE}}": profile_image_html,
                "{{profile_image}}": profile_image_html,
                "{{PROFILE_PHOTO}}": profile_image_html,
                "{{profile_photo}}": profile_image_html
            })
        else:
            # Remove image placeholders if no image is provided
            replacements.update({
                "{{PROFILE_IMAGE}}": "",
                "{{profile_image}}": "",
                "{{PROFILE_PHOTO}}": "",
                "{{profile_photo}}": ""
            })
        
        # Apply all replacements with safety checks
        populated_html = html_template
        for placeholder, value in replacements.items():
            # Ensure value is a string - fix for "list object has no attribute replace" error
            if isinstance(value, list):
                # Convert lists to strings (comma-separated)
                safe_value = ', '.join(str(item) for item in value) if value else ""
                logger.warning(f"Converted list to string for placeholder {placeholder}: {safe_value[:100]}...")
            elif value is None:
                safe_value = ""
            else:
                safe_value = str(value)
            
            populated_html = populated_html.replace(placeholder, safe_value)
        
        # Handle profile image placeholders - remove them if no actual image exists
        # Check if the original resume had any image data
        has_profile_image = False
        if 'profile_image' in resume_data or 'photo' in resume_data:
            has_profile_image = bool(resume_data.get('profile_image') or resume_data.get('photo'))
        
        # Also check if profile image data is provided as parameter
        if profile_image_data:
            has_profile_image = True
        
        if not has_profile_image:
            # Remove or hide image placeholder elements
            import re
            
            # Remove profile-image-placeholder divs
            populated_html = re.sub(r'<div[^>]*class="[^"]*profile-image-placeholder[^"]*"[^>]*></div>', '', populated_html)
            populated_html = re.sub(r'<div[^>]*class="[^"]*profile-image-wrapper[^"]*"[^>]*>.*?</div>', '', populated_html, flags=re.DOTALL)
            
            # If name_initials is empty (no real name), also remove avatar elements
            if not name_initials:
                populated_html = re.sub(r'<div[^>]*class="[^"]*profile-avatar[^"]*"[^>]*>.*?</div>', '', populated_html, flags=re.DOTALL)
        
        # Handle missing sections by dynamically adding them if data exists but template doesn't
        populated_html = self._add_missing_sections(populated_html, resume_data, template_id)
        
        # Detect and fill empty gaps in the template
        populated_html = self._detect_and_fill_empty_gaps(populated_html, resume_data, template_id)
        
        return populated_html
    
    def _ensure_string_output(self, section_output, section_name: str) -> str:
        """Ensure section building methods return strings, not lists or other types."""
        if isinstance(section_output, str):
            return section_output
        elif isinstance(section_output, list):
            # Convert list to HTML string
            html_items = []
            for item in section_output:
                if isinstance(item, dict):
                    # Convert dict items to simple HTML
                    html_items.append('<div>' + ', '.join([f"{k}: {v}" for k, v in item.items()]) + '</div>')
                else:
                    html_items.append(f'<div>{str(item)}</div>')
            result = '\n'.join(html_items)
            logger.warning(f"Converted list output to HTML for {section_name} section: {len(section_output)} items")
            return result
        elif section_output is None:
            return ""
        else:
            logger.warning(f"Converting non-string output to string for {section_name} section: {type(section_output)}")
            return str(section_output)
    
    def get_section_validation_summary(self, resume_data: Dict[str, Any], template_id: str) -> Dict[str, Any]:
        """Get a summary of section validation results for user feedback."""
        html_lower = ""  # We don't have the final HTML here, so simulate checks
        
        available_sections = {}
        missing_sections = []
        
        # Define sections to check
        section_checks = [
            {'name': 'Work Experience', 'data_key': 'job_experiences'},
            {'name': 'Education', 'data_key': 'education'},
            {'name': 'Skills', 'data_key': 'skills'},
            {'name': 'Projects', 'data_key': 'projects'},
            {'name': 'Certifications', 'data_key': 'certifications'},
            {'name': 'Testimonials', 'data_key': 'testimonials'},
            {'name': 'Languages', 'data_key': 'languages'},
            {'name': 'Awards & Recognitions', 'data_key': 'awards'},
            {'name': 'Publications', 'data_key': 'publications'},
            {'name': 'Volunteer', 'data_key': 'volunteer'},
            {'name': 'Courses', 'data_key': 'courses'},
            {'name': 'Achievements', 'data_key': 'achievements'},
            {'name': 'Interests', 'data_key': 'interests'}
        ]
        
        for section in section_checks:
            data = resume_data.get(section['data_key'])
            if data and len(data) > 0:
                available_sections[section['name']] = len(data)
        
        return {
            'template_id': template_id,
            'available_sections': available_sections,
            'total_sections': len(available_sections),
            'validation_message': f"Template validation: {len(available_sections)} sections available for {template_id}"
        }
    
    def _safe_get_value(self, obj, key: str, default: str = "") -> str:
        """Safely get value from object or dict."""
        if hasattr(obj, key):
            return str(getattr(obj, key, default))
        elif isinstance(obj, dict):
            return str(obj.get(key, default))
        return default
    
    def _build_work_experience_section(self, job_experiences: list) -> str:
        """Build work experience HTML section."""
        if not job_experiences:
            return "<div class='experience-item'><h3>Work Experience</h3><p>Your work experience will appear here</p></div>"
        
        # Log work experience processing
        logger.info(f"🏢 BUILDING WORK EXPERIENCE SECTION with {len(job_experiences)} jobs")
        
        experience_html = ""
        for i, job in enumerate(job_experiences):
            # Try multiple possible keys for job title
            job_title = (self._safe_get_value(job, 'job_title', '') or 
                        self._safe_get_value(job, 'position', '') or 
                        self._safe_get_value(job, 'title', '') or 
                        'Job Title')
            logger.info(f"🏢 PROCESSING JOB {i}: '{job_title}'")
            
            # Log all job fields for debugging
            if isinstance(job, dict):
                logger.debug(f"📊 Job {i} fields: {list(job.keys())}")
                for key, value in job.items():
                    if key in ['job_title', 'title', 'position']:
                        logger.info(f"   📌 {key}: '{value}'")
                    elif key in ['description', 'summary', 'responsibilities']:
                        logger.debug(f"   📝 {key}: {str(value)[:50]}...")
            else:
                logger.warning(f"⚠️ Job {i} is not a dict: {type(job)}")
            company = self._safe_get_value(job, 'company', 'Company')
            start_date = self._safe_get_value(job, 'start_date', '')
            end_date = self._safe_get_value(job, 'end_date', 'Present')
            job_location = self._safe_get_value(job, 'location', '')
            # Handle different description formats after role adaptation  
            if isinstance(job, dict):
                descriptions = job.get('description', [])
            elif hasattr(job, 'description'):
                descriptions = getattr(job, 'description', [])
            else:
                descriptions = []
            
            experience_html += f"""
            <div class="experience-item">
                <div class="job-header">
                    <div class="job-title-company">
                        <h3 class="job-title">{job_title}</h3>
                        <span class="job-date">{start_date} - {end_date}</span>
                    </div>
                    <div class="company">{company}</div>
                    {f'<div class="location">{job_location}</div>' if job_location else ''}
                </div>
                <div class="job-description">
                    <ul>
            """
            
            if descriptions:
                # Handle both string and list descriptions
                if isinstance(descriptions, str):
                    # Single string description (from role adaptation) - may contain bullet points
                    if '•' in descriptions:
                        # Split by bullet points and create list items
                        bullet_points = [point.strip() for point in descriptions.split('•') if point.strip()]
                        for point in bullet_points:
                            experience_html += f"<li>{point}</li>"
                    else:
                        # Single description without bullet points
                        experience_html += f"<li>{descriptions}</li>"
                else:
                    # List of descriptions (original format)
                    for desc in descriptions:
                        experience_html += f"<li>{desc}</li>"
            else:
                experience_html += "<li>Key responsibilities and achievements for this role</li>"
            
            experience_html += "</ul></div></div>"
        
        return experience_html
    
    def _build_education_section(self, education_list: list) -> str:
        """Build education HTML section."""
        if not education_list:
            return "<div class='education-item'><h3>Education</h3><p>Your education will appear here</p></div>"
        
        education_html = ""
        for edu in education_list:
            degree = self._safe_get_value(edu, 'degree', 'Degree')
            # Try multiple possible keys for school/institution
            school = (self._safe_get_value(edu, 'school', '') or 
                     self._safe_get_value(edu, 'institution', '') or 
                     self._safe_get_value(edu, 'university', '') or 
                     'School')
            graduation_date = self._safe_get_value(edu, 'graduation_date', '')
            gpa = self._safe_get_value(edu, 'gpa', '')
            honors = self._safe_get_value(edu, 'honors', '')
            
            education_html += f"""
            <div class="education-item">
                <h3 class="degree-name">{degree}</h3>
                <div class="education-meta">
                    <div class="school-name">{school}</div>
                    <div class="graduation-date">{graduation_date}</div>
                    {f'<div class="gpa">GPA: {gpa}</div>' if gpa else ''}
                    {f'<div class="honors">{honors}</div>' if honors else ''}
                </div>
            </div>
            """
        
        return education_html
    
    def _build_skills_section(self, skills: list) -> str:
        """Build skills HTML section."""
        if not skills:
            return "<div class='skills-category'><h4>Technical Skills</h4><div class='skills-list'>Your skills will appear here</div></div>"
        
        # Debug: Log the skills structure
        logger.debug(f"Building skills section with: {type(skills)} - {skills[:2] if len(skills) > 2 else skills}")
        
        skills_html = ""
        for i, skill_category in enumerate(skills):
            logger.debug(f"Processing skill category {i}: {type(skill_category)} - {skill_category}")
            
            # Handle different skill category formats
            if isinstance(skill_category, str):
                # If it's a string, treat as a simple skill item
                skills_html += f"""
                <div class="skills-category">
                    <h4>Skills</h4>
                    <div class="skills-list">
                        {skill_category}
                    </div>
                </div>
                """
                continue
            category = self._safe_get_value(skill_category, 'category', 'Skills')
            
            # Handle different skill_list formats after role adaptation
            if isinstance(skill_category, dict):
                skill_list = skill_category.get('skills', [])
            elif hasattr(skill_category, 'skills'):
                skill_list = getattr(skill_category, 'skills', [])
            else:
                skill_list = []
            
            if skill_list:
                skills_html += f"""
                <div class="skills-category">
                    <h4>{category}</h4>
                    <div class="skills-list">
                        {', '.join(skill_list)}
                    </div>
                </div>
                """
        
        return skills_html or "<div class='skills-category'><h4>Technical Skills</h4><div class='skills-list'>Your skills will appear here</div></div>"
    
    def _build_projects_section(self, projects: list) -> str:
        """Build projects HTML section."""
        if not projects:
            return "<div class='project-item'><h3>Projects</h3><p>Your projects will appear here</p></div>"
        
        projects_html = ""
        for project in projects:
            title = self._safe_get_value(project, 'title', 'Project Title')
            description = self._safe_get_value(project, 'description', 'Project description')
            # Handle different technologies formats after role adaptation
            if isinstance(project, dict):
                technologies = project.get('technologies', [])
            elif hasattr(project, 'technologies'):
                technologies = getattr(project, 'technologies', [])
            else:
                technologies = []
            date = self._safe_get_value(project, 'date', '')
            url = self._safe_get_value(project, 'url', '')
            
            projects_html += f"""
            <div class="project-item">
                <div class="project-header">
                    <h3 class="project-title">{title}</h3>
                    {f'<a href="{url}" class="project-link" target="_blank">View Project</a>' if url else ''}
                </div>
                <div class="project-description">{description}</div>
                {f'<div class="project-tech">Technologies: {", ".join(technologies)}</div>' if technologies else ''}
                {f'<div class="project-date">{date}</div>' if date else ''}
            </div>
            """
        
        return projects_html
    
    def _build_certifications_section(self, certifications: list) -> str:
        """Build certifications HTML section."""
        if not certifications:
            return ""
        
        cert_html = "<div class='certifications-section'><h3>Certifications</h3>"
        for cert in certifications:
            if isinstance(cert, str):
                cert_html += f"<div class='certification-item'>{cert}</div>"
            else:
                name = self._safe_get_value(cert, 'name', str(cert))
                issuer = self._safe_get_value(cert, 'issuer', '')
                date = self._safe_get_value(cert, 'date', '')
                
                cert_html += f"""
                <div class="certification-item">
                    <div class="cert-name">{name}</div>
                    {f'<div class="cert-issuer">{issuer}</div>' if issuer else ''}
                    {f'<div class="cert-date">{date}</div>' if date else ''}
                </div>
                """
        
        cert_html += "</div>"
        return cert_html
    
    def _build_technical_skills_section(self, skills: list) -> str:
        """Build technical skills section for tech-focused templates."""
        if not skills:
            return "<div class='tech-skills-grid'><div class='skill-group'><h3>Technical Skills</h3><div class='skill-tags'>Your technical skills will appear here</div></div></div>"
        
        tech_skills_html = "<div class='tech-skills-grid'>"
        for skill_category in skills:
            category = self._safe_get_value(skill_category, 'category', 'Skills')
            # Handle different skill_list formats after role adaptation
            if isinstance(skill_category, dict):
                skill_list = skill_category.get('skills', [])
            elif hasattr(skill_category, 'skills'):
                skill_list = getattr(skill_category, 'skills', [])
            else:
                skill_list = []
            
            if skill_list:
                tech_skills_html += f"""
                <div class="skill-group">
                    <h3>{category}</h3>
                    <div class="skill-tags">
                        {''.join([f'<span class="skill-tag">{skill}</span>' for skill in skill_list])}
                    </div>
                </div>
                """
        
        tech_skills_html += "</div>"
        return tech_skills_html
    
    def _build_services_section(self, resume_data: Dict[str, Any]) -> str:
        """Build services section for freelancer templates."""
        # Infer services from skills and experience
        services_html = "<div class='services-grid'>"
        
        # Default services based on skills
        skills = resume_data.get('skills', [])
        if skills:
            for skill_category in skills[:3]:  # Limit to top 3 categories
                category = self._safe_get_value(skill_category, 'category', 'Service')
                # Handle different skill_list formats after role adaptation
                if isinstance(skill_category, dict):
                    skill_list = skill_category.get('skills', [])
                elif hasattr(skill_category, 'skills'):
                    skill_list = getattr(skill_category, 'skills', [])
                else:
                    skill_list = []
                
                if skill_list:
                    services_html += f"""
                    <div class="service-card">
                        <h3 class="service-title">{category}</h3>
                        <div class="service-description">Professional {category.lower()} services including {', '.join(skill_list[:3])}</div>
                    </div>
                    """
        else:
            # Default services
            default_services = [
                ("Consulting", "Strategic consulting and advisory services"),
                ("Development", "Custom development and technical solutions"),
                ("Design", "Creative design and user experience services")
            ]
            
            for title, desc in default_services:
                services_html += f"""
                <div class="service-card">
                    <h3 class="service-title">{title}</h3>
                    <div class="service-description">{desc}</div>
                </div>
                """
        
        services_html += "</div>"
        return services_html
    
    def _build_testimonials_section(self, testimonials: list) -> str:
        """Build testimonials section."""
        if not testimonials:
            return "<div class='testimonials'><div class='testimonial-card'><div class='testimonial-text'>Client testimonials will appear here when available.</div><div class='testimonial-author'>Satisfied Client</div></div></div>"

        testimonials_html = "<div class='testimonials'>"
        for testimonial in testimonials:
            text = self._safe_get_value(testimonial, 'text', 'Great work and professional service.')
            author = self._safe_get_value(testimonial, 'author', 'Client')
            company = self._safe_get_value(testimonial, 'company', '')
            
            testimonials_html += f"""
            <div class="testimonial-card">
                <div class="testimonial-text">"{text}"</div>
                <div class="testimonial-author">{author}</div>
                {f'<div class="testimonial-company">{company}</div>' if company else ''}
            </div>
            """

        testimonials_html += "</div>"
        return testimonials_html

    def _build_awards_section(self, awards: list) -> str:
        """Build awards/recognitions section."""
        if not awards:
            return ""
        html = "<div class='awards-section'><h3>Awards & Recognitions</h3><ul>"
        for a in awards:
            if isinstance(a, str):
                html += f"<li>{a}</li>"
            elif isinstance(a, dict):
                name = self._safe_get_value(a, 'name', 'Award')
                org = self._safe_get_value(a, 'issuer', '')
                year = self._safe_get_value(a, 'year', '')
                detail = self._safe_get_value(a, 'details', '')
                meta = " ".join([p for p in [org, year] if p])
                html += f"<li><strong>{name}</strong>{f' — {meta}' if meta else ''}{f': {detail}' if detail else ''}</li>"
        html += "</ul></div>"
        return html

    def _build_publications_section(self, publications: list) -> str:
        """Build publications section."""
        if not publications:
            return ""
        html = "<div class='publications-section'><h3>Publications</h3><ul>"
        for p in publications:
            if isinstance(p, str):
                html += f"<li>{p}</li>"
            else:
                title = self._safe_get_value(p, 'title', 'Publication')
                venue = self._safe_get_value(p, 'venue', '')
                year = self._safe_get_value(p, 'year', '')
                link = self._safe_get_value(p, 'url', '')
                suffix = " ".join([v for v in [venue, year] if v])
                if link:
                    html += f"<li><a href='{link}' target='_blank'>{title}</a>{f' — {suffix}' if suffix else ''}</li>"
                else:
                    html += f"<li>{title}{f' — {suffix}' if suffix else ''}</li>"
        html += "</ul></div>"
        return html

    def _build_languages_section(self, languages: list) -> str:
        """Build languages section (general template usage)."""
        if not languages:
            return ""
        items = []
        for lang in languages:
            if isinstance(lang, str):
                items.append(lang)
            elif isinstance(lang, dict):
                n = self._safe_get_value(lang, 'name', '')
                prof = self._safe_get_value(lang, 'proficiency', '')
                items.append(f"{n}{f' ({prof})' if prof else ''}")
        if not items:
            return ""
        return "<div class='languages-section'><h3>Languages</h3><div>" + ", ".join(items) + "</div></div>"

    def _build_volunteer_section(self, volunteer: list) -> str:
        """Build volunteer section."""
        if not volunteer:
            return ""
        html = "<div class='volunteer-section'><h3>Volunteer</h3>"
        for v in volunteer:
            role = self._safe_get_value(v, 'role', 'Volunteer')
            org = self._safe_get_value(v, 'organization', '')
            desc = self._safe_get_value(v, 'description', '')
            html += f"<div class='volunteer-item'><strong>{role}</strong>{f' — {org}' if org else ''}{f': {desc}' if desc else ''}</div>"
        html += "</div>"
        return html

    def _build_interests_section(self, interests: list) -> str:
        """Build interests/hobbies section."""
        if not interests:
            return ""
        items = []
        for it in interests:
            items.append(str(it))
        if not items:
            return ""
        return "<div class='interests-section'><h3>Interests</h3><div>" + ", ".join(items[:12]) + "</div></div>"

    def _build_achievements_section(self, achievements: list) -> str:
        """Build achievements section."""
        if not achievements:
            return ""
        html = "<div class='achievements-section'><h3>Achievements</h3><ul>"
        for a in achievements:
            html += f"<li>{str(a)}</li>"
        html += "</ul></div>"
        return html

    def _build_courses_section(self, courses: list) -> str:
        """Build courses/professional training section."""
        if not courses:
            return ""
        html = "<div class='courses-section'><h3>Courses</h3><ul>"
        for c in courses:
            if isinstance(c, str):
                html += f"<li>{c}</li>"
            else:
                title = self._safe_get_value(c, 'title', 'Course')
                provider = self._safe_get_value(c, 'provider', '')
                year = self._safe_get_value(c, 'year', '')
                meta = " ".join([p for p in [provider, year] if p])
                html += f"<li>{title}{f' — {meta}' if meta else ''}</li>"
        html += "</ul></div>"
        return html
    
    def _infer_job_title(self, resume_data: Dict[str, Any]) -> str:
        """Infer professional title from resume data."""
        job_experiences = resume_data.get('job_experiences', [])
        if job_experiences:
            # Get the most recent job title
            recent_job = job_experiences[0]
            return self._safe_get_value(recent_job, 'job_title', 'Professional')
        
        # Infer from skills
        skills = resume_data.get('skills', [])
        if skills:
            for skill_category in skills:
                category = self._safe_get_value(skill_category, 'category', '')
                if 'software' in category.lower() or 'programming' in category.lower():
                    return 'Software Developer'
                elif 'design' in category.lower():
                    return 'Designer'
                elif 'marketing' in category.lower():
                    return 'Marketing Professional'
                elif 'data' in category.lower():
                    return 'Data Analyst'
        
        return 'Professional'
    
    def _generate_tagline(self, resume_data: Dict[str, Any]) -> str:
        """Generate a professional tagline."""
        job_title = self._infer_job_title(resume_data)
        return f"Experienced {job_title} dedicated to delivering exceptional results"
    
    def _add_missing_sections(self, html: str, resume_data: Dict[str, Any], template_id: str) -> str:
        """Dynamically add missing sections to the template if data exists."""
        missing_sections = []
        html_lower = html.lower()
        
        # Define all possible sections with their detection keywords and builders
        section_checks = [
            {
                'name': 'Projects',
                'data_key': 'projects',
                'keywords': ['project', '{{projects}}', 'projects-section'],
                'builder': self._build_projects_section,
                'class': 'projects-section',
                'priority': 1
            },
            {
                'name': 'Certifications', 
                'data_key': 'certifications',
                'keywords': ['certification', '{{certifications}}', 'certifications-section'],
                'builder': self._build_certifications_section,
                'class': 'certifications-section',
                'priority': 2
            },
            {
                'name': 'Awards & Recognitions',
                'data_key': 'awards',
                'keywords': ['award', 'recognition', 'awards-section', '{{awards}}'],
                'builder': self._build_awards_section,
                'class': 'awards-section',
                'priority': 2
            },
            {
                'name': 'Publications',
                'data_key': 'publications',
                'keywords': ['publication', 'publications-section', '{{publications}}', 'papers', 'articles'],
                'builder': self._build_publications_section,
                'class': 'publications-section',
                'priority': 2
            },
            {
                'name': 'Work Experience',
                'data_key': 'job_experiences',
                'keywords': ['work', 'experience', '{{work_experience}}', 'job', 'employment', 'work-experience'],
                'builder': self._build_work_experience_section,
                'class': 'work-experience-section',
                'priority': 0  # Highest priority
            },
            {
                'name': 'Education',
                'data_key': 'education', 
                'keywords': ['education', '{{education}}', 'education-section', 'degree'],
                'builder': self._build_education_section,
                'class': 'education-section',
                'priority': 0  # Highest priority
            },
            {
                'name': 'Skills',
                'data_key': 'skills',
                'keywords': ['skill', '{{skills}}', '{{technical_skills}}', 'skills-section', 'technical'],
                'builder': self._build_skills_section,
                'class': 'skills-section', 
                'priority': 0  # Highest priority
            },
            {
                'name': 'Languages',
                'data_key': 'languages',
                'keywords': ['language', 'languages-section', '{{languages}}'],
                'builder': self._build_languages_section,
                'class': 'languages-section',
                'priority': 3
            },
            {
                'name': 'Testimonials',
                'data_key': 'testimonials',
                'keywords': ['testimonial', '{{testimonials}}', 'testimonials-section', 'reference'],
                'builder': self._build_testimonials_section,
                'class': 'testimonials-section',
                'priority': 3
            },
            {
                'name': 'Volunteer',
                'data_key': 'volunteer',
                'keywords': ['volunteer', 'volunteering', 'volunteer-section', '{{volunteer}}'],
                'builder': self._build_volunteer_section,
                'class': 'volunteer-section',
                'priority': 3
            },
            {
                'name': 'Courses',
                'data_key': 'courses',
                'keywords': ['course', 'courses', 'training', 'courses-section', '{{courses}}'],
                'builder': self._build_courses_section,
                'class': 'courses-section',
                'priority': 3
            },
            {
                'name': 'Achievements',
                'data_key': 'achievements',
                'keywords': ['achievement', 'achievements-section', '{{achievements}}'],
                'builder': self._build_achievements_section,
                'class': 'achievements-section',
                'priority': 3
            },
            {
                'name': 'Interests',
                'data_key': 'interests',
                'keywords': ['interest', 'hobbies', 'interests-section', '{{interests}}'],
                'builder': self._build_interests_section,
                'class': 'interests-section',
                'priority': 4
            },
        ]
        
        # Check each section
        for section in section_checks:
            data = resume_data.get(section['data_key'])
            if data and len(data) > 0:  # Has data
                # Check if section exists in template
                section_exists = any(keyword in html_lower for keyword in section['keywords'])
                if not section_exists:
                    logger.warning(f"Missing section detected: {section['name']} - has data but not in template")
                    try:
                        section_html = section['builder'](data)
                        if section_html and section_html.strip():
                            missing_sections.append({
                                'html': f"<section class='{section['class']}'><h2>{section['name']}</h2>{section_html}</section>",
                                'priority': section['priority'],
                                'name': section['name']
                            })
                    except Exception as e:
                        logger.error(f"Error building {section['name']} section: {e}")
        
        # Sort by priority (0 = highest priority)
        missing_sections.sort(key=lambda x: x['priority'])
        
        # Add missing sections in appropriate locations
        if missing_sections:
            logger.info(f"Adding {len(missing_sections)} missing sections to template {template_id}: {[s['name'] for s in missing_sections]}")
            sections_html = '\n'.join([section['html'] for section in missing_sections])
            
            # Try to find appropriate insertion points in order of preference
            insertion_points = [
                "</body>",
                "</div><!-- End resume content -->", 
                "</div><!-- resume-container -->",
                "</main>",
                "</article>",
                "</section>",
                "</div>"  # Last div as fallback
            ]
            
            inserted = False
            for point in insertion_points:
                if point in html:
                    html = html.replace(point, f'{sections_html}\n{point}', 1)
                    inserted = True
                    logger.info(f"Inserted missing sections before: {point}")
                    break
            
            if not inserted:
                html += f"\n{sections_html}"
                logger.warning("No suitable insertion point found, appended sections to end")
        
        return html
    
    def _detect_and_fill_empty_gaps(self, html: str, resume_data: Dict[str, Any], template_id: str) -> str:
        """Detect empty gaps in templates and fill them with appropriate content."""
        # Patterns that indicate empty or placeholder content
        empty_patterns = [
            r'<div[^>]*>\s*</div>',  # Empty divs
            r'<section[^>]*>\s*</section>',  # Empty sections
            r'<p[^>]*>\s*</p>',  # Empty paragraphs
            r'<div[^>]*class="[^"]*empty[^"]*"[^>]*>.*?</div>',  # Divs with "empty" class
            r'<div[^>]*>\s*<h[1-6][^>]*>[^<]*</h[1-6]>\s*</div>',  # Divs with only headers
            r'placeholder[^"]*"[^>]*>',  # Elements with placeholder attributes
            r'>Your [^<]+ will appear here<',  # Placeholder text
            r'>Coming soon<',  # Coming soon text
            r'>TBD<',  # To be determined text
        ]
        
        gaps_found = 0
        for pattern in empty_patterns:
            gaps_found += len(re.findall(pattern, html, re.IGNORECASE | re.DOTALL))
        
        if gaps_found > 0:
            logger.info(f"Detected {gaps_found} empty gaps in template {template_id}")
            
            # Try to fill gaps with available data
            html = self._fill_empty_content_gaps(html, resume_data)
        
        return html
    
    def _fill_empty_content_gaps(self, html: str, resume_data: Dict[str, Any]) -> str:
        """Fill empty content gaps with relevant resume data."""
        
        # Replace common placeholder patterns with actual content
        replacements = []
        
        # Check for available sections that could fill gaps
        if resume_data.get('projects'):
            projects_html = self._build_projects_section(resume_data['projects'])
            replacements.append({
                'pattern': r'<div[^>]*>\s*<h[1-6][^>]*>(?:Projects?|Portfolio)</h[1-6]>\s*<p[^>]*>.*?will appear here.*?</p>\s*</div>',
                'replacement': f'<div class="projects-section"><h2>Projects</h2>{projects_html}</div>'
            })
        
        if resume_data.get('certifications'):
            cert_html = self._build_certifications_section(resume_data['certifications'])
            replacements.append({
                'pattern': r'<div[^>]*>\s*<h[1-6][^>]*>(?:Certifications?|Licenses?)</h[1-6]>\s*<p[^>]*>.*?will appear here.*?</p>\s*</div>',
                'replacement': f'<div class="certifications-section"><h2>Certifications</h2>{cert_html}</div>'
            })
        
        if resume_data.get('skills'):
            # For empty skill sections, add a condensed skills list
            skills_text = self._build_condensed_skills_text(resume_data['skills'])
            replacements.append({
                'pattern': r'<div[^>]*>\s*<h[1-6][^>]*>(?:Skills?|Technical Skills?)</h[1-6]>\s*<p[^>]*>.*?will appear here.*?</p>\s*</div>',
                'replacement': f'<div class="skills-section"><h3>Key Skills</h3><p>{skills_text}</p></div>'
            })
        
        # Professional summary for empty sections
        if resume_data.get('professional_summary'):
            summary = resume_data['professional_summary'][:200] + "..." if len(resume_data['professional_summary']) > 200 else resume_data['professional_summary']
            replacements.append({
                'pattern': r'<div[^>]*>\s*<h[1-6][^>]*>(?:About|Summary|Profile)</h[1-6]>\s*<p[^>]*>.*?will appear here.*?</p>\s*</div>',
                'replacement': f'<div class="summary-section"><h3>Professional Summary</h3><p>{summary}</p></div>'
            })
        
        # Apply replacements
        for replacement in replacements:
            if re.search(replacement['pattern'], html, re.IGNORECASE | re.DOTALL):
                html = re.sub(replacement['pattern'], replacement['replacement'], html, flags=re.IGNORECASE | re.DOTALL)
                logger.info("Filled empty content gap with relevant resume data")
        
        return html
    
    def _build_condensed_skills_text(self, skills: list) -> str:
        """Build a condensed skills text for filling small gaps."""
        if not skills:
            return "Technical and professional skills"
        
        skill_names = []
        for skill_category in skills:
            if isinstance(skill_category, dict):
                skill_list = skill_category.get('skills', [])
            elif hasattr(skill_category, 'skills'):
                skill_list = getattr(skill_category, 'skills', [])
            else:
                continue
            
            skill_names.extend(skill_list[:3])  # Take top 3 from each category
            if len(skill_names) >= 8:  # Limit to 8 total skills for condensed version
                break
        
        return ', '.join(skill_names[:8]) if skill_names else "Technical and professional skills"
    
    def _apply_color_palette(self, css_template: str, palette: ColorPalette) -> str:
        """Apply color palette to CSS template."""
        
        # Helper function to convert hex to RGB
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Get RGB values for rgba() CSS functions
        primary_rgb = ', '.join(map(str, hex_to_rgb(palette.primary)))
        secondary_rgb = ', '.join(map(str, hex_to_rgb(palette.secondary)))
        
        # Calculate high contrast color for text on primary/secondary backgrounds
        text_contrast_color = self._get_high_contrast_text_color(palette.primary)
        
        css_with_colors = css_template.replace("{{primary_color}}", palette.primary)
        css_with_colors = css_with_colors.replace("{{secondary_color}}", palette.secondary)
        css_with_colors = css_with_colors.replace("{{text_dark}}", palette.text_dark)
        css_with_colors = css_with_colors.replace("{{text_light}}", palette.text_light)
        css_with_colors = css_with_colors.replace("{{background_color}}", palette.background)
        css_with_colors = css_with_colors.replace("{{section_bg}}", palette.section_bg)
        css_with_colors = css_with_colors.replace("{{border_color}}", palette.border)
        css_with_colors = css_with_colors.replace("{{link_color}}", palette.link)
        css_with_colors = css_with_colors.replace("{{text_contrast_color}}", text_contrast_color)
        
        # Apply RGB values for rgba() functions
        css_with_colors = css_with_colors.replace("{{primary_rgb}}", primary_rgb)
        css_with_colors = css_with_colors.replace("{{secondary_rgb}}", secondary_rgb)
        
        return css_with_colors
    
    def _calculate_contrast_ratio(self, color1: str, color2: str) -> float:
        """Calculate contrast ratio between two colors for accessibility."""
        def hex_to_rgb(hex_color):
            hex_color = hex_color.lstrip('#')
            return [int(hex_color[i:i+2], 16) for i in (0, 2, 4)]
        
        def relative_luminance(rgb):
            """Calculate relative luminance of a color."""
            rgb_normalized = [c / 255.0 for c in rgb]
            rgb_linear = []
            for c in rgb_normalized:
                if c <= 0.04045:
                    rgb_linear.append(c / 12.92)
                else:
                    rgb_linear.append(((c + 0.055) / 1.055) ** 2.4)
            return 0.2126 * rgb_linear[0] + 0.7152 * rgb_linear[1] + 0.0722 * rgb_linear[2]
        
        rgb1 = hex_to_rgb(color1)
        rgb2 = hex_to_rgb(color2)
        
        l1 = relative_luminance(rgb1)
        l2 = relative_luminance(rgb2)
        
        # Ensure l1 is the lighter color
        if l1 < l2:
            l1, l2 = l2, l1
        
        return (l1 + 0.05) / (l2 + 0.05)
    
    def _get_luminance(self, hex_color: str) -> float:
        """Calculate relative luminance of a color according to WCAG guidelines."""
        # Convert hex to RGB
        rgb = hex_to_rgb(hex_color)
        
        # Convert to relative luminance values
        def get_relative_luminance(c):
            c = c / 255.0
            if c <= 0.03928:
                return c / 12.92
            else:
                return pow((c + 0.055) / 1.055, 2.4)
        
        r = get_relative_luminance(rgb[0])
        g = get_relative_luminance(rgb[1])
        b = get_relative_luminance(rgb[2])
        
        # Calculate luminance using WCAG formula
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
    
    def _get_high_contrast_text_color(self, background_color: str) -> str:
        """Calculate the best contrast text color (white or very dark) for a given background."""        
        # Calculate contrast ratios with white and very dark gray
        white_contrast = self._calculate_contrast_ratio("#ffffff", background_color)
        dark_contrast = self._calculate_contrast_ratio("#1a202c", background_color)
        
        # Choose the color with better contrast (minimum 4.5:1 for AA compliance)
        if white_contrast >= dark_contrast and white_contrast >= 4.5:
            return "#ffffff"
        elif dark_contrast >= 4.5:
            return "#1a202c"
        else:
            # If neither meets AA standard, choose the one with higher contrast
            return "#ffffff" if white_contrast > dark_contrast else "#1a202c"
    
    def _validate_color_accessibility(self, palette: ColorPalette) -> Dict[str, bool]:
        """Validate color combinations meet WCAG accessibility standards."""
        results = {}
        
        # Check text on background contrast (should be at least 4.5:1 for AA)
        results['text_on_bg'] = self._calculate_contrast_ratio(palette.text_dark, palette.background) >= 4.5
        results['light_text_on_bg'] = self._calculate_contrast_ratio(palette.text_light, palette.background) >= 4.5
        results['text_on_section'] = self._calculate_contrast_ratio(palette.text_dark, palette.section_bg) >= 4.5
        
        # Check links have sufficient contrast
        results['links'] = self._calculate_contrast_ratio(palette.link, palette.background) >= 4.5
        
        # Log any accessibility issues
        for check, passed in results.items():
            if not passed:
                logger.warning(f"Accessibility issue in palette '{palette.name}': {check} fails contrast requirement")
        
        return results
    
    def _generate_cache_key(self, resume_data: Dict[str, Any], template_id: str, palette_id: str, 
                           target_role: str = None, enhancement_level: str = "standard") -> str:
        """Generate a unique cache key for the given parameters."""
        # Create a deterministic hash of all parameters that affect the result
        resume_hash = self._hash_resume_data(resume_data)
        key_data = {
            "template_id": template_id,
            "palette_id": palette_id,
            "enhancement_level": enhancement_level,
            "target_role": target_role,
            "resume_hash": resume_hash
        }
        
        # Create hash from the key data
        key_string = json.dumps(key_data, sort_keys=True)
        cache_key = hashlib.md5(key_string.encode()).hexdigest()
        
        # Log cache key generation details
        logger.info(f"🔑 CACHE KEY GENERATION:")
        logger.info(f"   📋 Template: {template_id}")
        logger.info(f"   🎨 Palette: {palette_id}")
        logger.info(f"   📈 Enhancement: {enhancement_level}")
        logger.info(f"   🎯 Role: {target_role}")
        logger.info(f"   📊 Resume hash: {resume_hash[:8]}...")
        logger.info(f"   🔑 Generated key: {cache_key[:8]}...")
        
        return cache_key
    
    def _hash_resume_data(self, resume_data: Dict[str, Any]) -> str:
        """Generate a hash of resume data for cache key generation."""
        # Remove non-content fields that don't affect output
        # Include _role_adapted in exclusions but handle it separately in cache key
        content_data = {k: v for k, v in resume_data.items() 
                       if k not in ['_role_adapted', 'timestamp', 'cache_key']}
        
        # Create deterministic JSON string
        content_string = json.dumps(content_data, sort_keys=True, default=str)
        return hashlib.md5(content_string.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Retrieve result from cache if available and not expired."""
        if cache_key in self.cache:
            entry = self.cache[cache_key]
            if not entry.is_expired():
                cache_age_hours = (time.time() - entry.timestamp) / 3600
                logger.info(f"✅ Cache HIT for key: {cache_key[:8]}... (age: {cache_age_hours:.1f}h)")
                return entry.result
            else:
                # Remove expired entry
                cache_age_hours = (time.time() - entry.timestamp) / 3600
                logger.info(f"⏰ Cache EXPIRED for key: {cache_key[:8]}... (age: {cache_age_hours:.1f}h)")
                del self.cache[cache_key]
                # Also remove from disk
                try:
                    cache_file = self.cache_dir / f"{cache_key}.json"
                    if cache_file.exists():
                        cache_file.unlink()
                        logger.debug(f"🗑️ Removed expired cache file: {cache_key[:8]}...")
                except Exception as e:
                    logger.debug(f"Failed to remove expired cache file: {e}")
        
        logger.info(f"❌ Cache MISS for key: {cache_key[:8]}... (total cache entries: {len(self.cache)})")
        logger.debug(f"🔍 Available cache keys: {[k[:8] + '...' for k in self.cache.keys()]}")
        return None
    
    def _save_to_cache(self, cache_key: str, result: Dict[str, Any], expiry_hours: int = 24):
        """Save result to cache with expiration."""
        logger.info(f"💾 CACHE SAVE PHASE:")
        logger.info(f"   🔑 Key: {cache_key[:8]}...")
        logger.info(f"   📊 Result keys: {list(result.keys())}")
        logger.info(f"   ⏰ Expiry: {expiry_hours}h")
        
        entry = CacheEntry(
            cache_key=cache_key,
            result=result.copy(),  # Create a copy to avoid reference issues
            timestamp=time.time(),
            expiry_hours=expiry_hours
        )
        
        # Save to memory
        self.cache[cache_key] = entry
        logger.info(f"   ✅ Saved to memory cache (total entries: {len(self.cache)})")
        
        # Save to disk for persistence across app restarts
        self._save_cache_to_disk(cache_key, entry)
        logger.info(f"   ✅ CACHE SAVE COMPLETED for key: {cache_key[:8]}...")
    
    def _save_cache_to_disk(self, cache_key: str, entry: CacheEntry):
        """Save cache entry to disk for persistence."""
        try:
            cache_file = self.cache_dir / f"{cache_key}.json"
            logger.debug(f"💿 DISK SAVE: Saving to {cache_file}")
            
            cache_data = {
                "cache_key": entry.cache_key,
                "result": entry.result,
                "timestamp": entry.timestamp,
                "expiry_hours": entry.expiry_hours
            }
            
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
                
            # Verify file was created
            file_size = cache_file.stat().st_size
            logger.debug(f"   ✅ Disk file created: {file_size} bytes")
            
        except Exception as e:
            logger.error(f"❌ DISK SAVE FAILED: {e}")
            import traceback
            logger.debug(f"📄 Disk save traceback: {traceback.format_exc()}")
    
    def _load_cache_from_disk(self):
        """Load cached entries from disk on startup."""
        loaded_count = 0
        expired_count = 0
        error_count = 0
        
        try:
            logger.info(f"🔄 Loading cache from disk: {self.cache_dir}")
            cache_files = list(self.cache_dir.glob("*.json"))
            logger.info(f"📁 Found {len(cache_files)} cache files on disk")
            
            for cache_file in cache_files:
                try:
                    logger.debug(f"📂 Loading cache file: {cache_file.name}")
                    with open(cache_file, 'r', encoding='utf-8') as f:
                        cache_data = json.load(f)
                    
                    # Validate required fields
                    required_fields = ["cache_key", "result", "timestamp"]
                    for field in required_fields:
                        if field not in cache_data:
                            raise ValueError(f"Missing required field: {field}")
                    
                    entry = CacheEntry(
                        cache_key=cache_data["cache_key"],
                        result=cache_data["result"],
                        timestamp=cache_data["timestamp"],
                        expiry_hours=cache_data.get("expiry_hours", 24)
                    )
                    
                    # Only load if not expired
                    if not entry.is_expired():
                        self.cache[entry.cache_key] = entry
                        loaded_count += 1
                        cache_age_hours = (time.time() - entry.timestamp) / 3600
                        logger.debug(f"✅ Loaded cache entry: {entry.cache_key[:8]}... (age: {cache_age_hours:.1f}h)")
                    else:
                        # Remove expired cache file
                        expired_count += 1
                        logger.debug(f"⏰ Removing expired cache file: {cache_file.name}")
                        cache_file.unlink()
                        
                except Exception as e:
                    error_count += 1
                    logger.error(f"❌ Failed to load cache file {cache_file.name}: {e}")
                    logger.debug(f"📄 Error details: {str(e)}")
                    # Remove corrupted cache file
                    try:
                        cache_file.unlink()
                        logger.debug(f"🗑️ Removed corrupted cache file: {cache_file.name}")
                    except Exception as cleanup_error:
                        logger.warning(f"Failed to remove corrupted file {cache_file.name}: {cleanup_error}")
                        
            logger.info(f"📊 Cache loading complete: {loaded_count} loaded, {expired_count} expired, {error_count} errors")
            
        except Exception as e:
            logger.error(f"❌ Critical error loading cache from disk: {e}")
            import traceback
            logger.debug(f"📄 Traceback: {traceback.format_exc()}")
    
    def clear_cache(self):
        """Clear all cached results."""
        self.cache.clear()
        try:
            for cache_file in self.cache_dir.glob("*.json"):
                cache_file.unlink()
        except Exception as e:
            logger.warning(f"Failed to clear disk cache: {e}")
        logger.info("🗑️ Cache cleared")
    
    def invalidate_resume_cache(self, resume_data: Dict[str, Any]):
        """Invalidate all cached results for a specific resume."""
        resume_hash = self._hash_resume_data(resume_data)
        keys_to_remove = []
        
        for cache_key, entry in self.cache.items():
            # Check if this cache entry is for the same resume
            try:
                # Reconstruct what the cache key would be for this resume
                if resume_hash in cache_key or self._is_cache_for_resume(cache_key, resume_hash):
                    keys_to_remove.append(cache_key)
            except Exception as e:
                logger.debug(f"Error checking cache key {cache_key}: {e}")
        
        # Remove matching cache entries
        for key in keys_to_remove:
            del self.cache[key]
            # Also remove from disk
            try:
                cache_file = self.cache_dir / f"{key}.json"
                if cache_file.exists():
                    cache_file.unlink()
            except Exception as e:
                logger.debug(f"Failed to remove cache file for {key}: {e}")
        
        if keys_to_remove:
            logger.info(f"🗑️ Invalidated {len(keys_to_remove)} cache entries for updated resume")
        else:
            logger.debug("No cache entries found to invalidate for this resume")
    
    def _is_cache_for_resume(self, cache_key: str, resume_hash: str) -> bool:
        """Check if a cache key corresponds to a specific resume hash."""
        # This is a simple check - in practice, you might want a more sophisticated approach
        return resume_hash in cache_key
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics for monitoring."""
        stats = {
            "total_entries": len(self.cache),
            "expired_entries": 0,
            "valid_entries": 0,
            "cache_types": {},
            "oldest_entry": None,
            "newest_entry": None
        }
        
        if not self.cache:
            return stats
        
        timestamps = []
        for entry in self.cache.values():
            timestamps.append(entry.timestamp)
            
            if entry.is_expired():
                stats["expired_entries"] += 1
            else:
                stats["valid_entries"] += 1
                
            # Try to categorize cache types
            if "role_adaptation" in entry.cache_key:
                cache_type = "role_adaptation"
            elif "original_format" in entry.cache_key:
                cache_type = "original_format"  
            else:
                cache_type = "template_generation"
                
            stats["cache_types"][cache_type] = stats["cache_types"].get(cache_type, 0) + 1
        
        if timestamps:
            import time
            stats["oldest_entry"] = time.ctime(min(timestamps))
            stats["newest_entry"] = time.ctime(max(timestamps))
        
        return stats
    
    def get_available_templates(self) -> List[Dict[str, str]]:
        """Get list of available templates."""
        return [
            {
                "id": template.id,
                "name": template.name,
                "description": template.description,
                "category": template.category
            }
            for template in self.templates.values()
        ]
    
    def get_available_palettes(self) -> List[Dict[str, str]]:
        """Get list of available color palettes."""
        return [
            {
                "id": palette_id,
                "name": palette.name,
                "primary": palette.primary,
                "secondary": palette.secondary
            }
            for palette_id, palette in self.color_palettes.items()
        ]
    
    def customize_colors_with_ai(self, resume_html: Dict[str, str], color_description: str) -> Dict[str, str]:
        """Use AI to customize colors based on natural language description."""
        if not self.openrouter_client:
            logger.warning("AI color customization requires OpenRouter client")
            return resume_html
            
        try:
            # Combine HTML and CSS for AI processing
            complete_html = f"""
<!DOCTYPE html>
<html>
<head>
<style>
{resume_html['css']}
</style>
</head>
<body>
{resume_html['html']}
</body>
</html>
"""
            
            logger.info(f"Using AI to customize colors: {color_description}")
            
            # Use AI to customize colors
            customized_html = self.openrouter_client.customize_resume_colors(
                complete_html, 
                color_description
            )
            
            if customized_html and not customized_html.startswith("Error:"):
                # Parse the AI response back into HTML and CSS
                if '<style>' in customized_html:
                    css_start = customized_html.find('<style>') + 7
                    css_end = customized_html.find('</style>')
                    ai_css = customized_html[css_start:css_end]
                    
                    # Extract HTML content (body)
                    if '<body>' in customized_html:
                        html_start = customized_html.find('<body>') + 6
                        html_end = customized_html.find('</body>')
                        ai_html = customized_html[html_start:html_end]
                    else:
                        ai_html = resume_html['html']  # Fallback
                    
                    logger.info("Successfully customized colors with AI")
                    return {
                        "html": ai_html,
                        "css": ai_css,
                        "complete_html": customized_html
                    }
                else:
                    logger.warning("AI response didn't contain CSS, using as complete HTML")
                    return {
                        "html": customized_html,
                        "css": "",
                        "complete_html": customized_html
                    }
            else:
                logger.error(f"AI color customization failed: {customized_html}")
                return resume_html
                
        except Exception as e:
            logger.error(f"AI color customization error: {e}")
            return resume_html
    
    def get_ai_color_suggestions(self, resume_data: Dict, job_role: str = "") -> List[str]:
        """Get AI suggestions for appropriate color schemes based on resume content and job role."""
        if not self.openrouter_client:
            return [
                "Professional Blue - Clean and trustworthy",
                "Modern Green - Fresh and innovative", 
                "Elegant Purple - Creative and sophisticated",
                "Classic Black - Timeless and formal"
            ]
            
        try:
            # Build context for AI
            context = f"""
Resume Role: {resume_data.get('title', 'Professional')}
Industry: {job_role or 'General'}
Experience Level: {'Senior' if len(resume_data.get('work_experience', [])) > 3 else 'Entry-Mid Level'}
Skills: {', '.join(resume_data.get('skills', [])[:5])}
"""
            
            prompt = f"""
Based on this professional profile, suggest 5-6 appropriate color schemes for a resume:

{context}

Provide color scheme suggestions in this format:
1. [Color Name] - [Brief description of why it fits]

Focus on professional, industry-appropriate colors that enhance readability and convey the right impression.
"""
            
            response = self.openrouter_client._make_request(
                prompt,
                max_tokens=400,
                temperature=0.7
            )
            
            if response and not response.startswith("Error:"):
                # Parse suggestions into list
                suggestions = []
                lines = response.strip().split('\n')
                for line in lines:
                    if line.strip() and (line.strip()[0].isdigit() or line.strip().startswith('-')):
                        # Clean up the suggestion
                        suggestion = line.strip()
                        if suggestion[0].isdigit():
                            suggestion = suggestion[2:].strip()  # Remove "1. "
                        if suggestion.startswith('-'):
                            suggestion = suggestion[1:].strip()  # Remove "- "
                        if suggestion:
                            suggestions.append(suggestion)
                
                return suggestions[:6] if suggestions else self._get_default_color_suggestions()
            else:
                return self._get_default_color_suggestions()
                
        except Exception as e:
            logger.error(f"AI color suggestions error: {e}")
            return self._get_default_color_suggestions()
    
    def _get_default_color_suggestions(self) -> List[str]:
        """Get default color suggestions when AI is unavailable."""
        return [
            "Professional Blue - Clean, trustworthy, and widely accepted",
            "Modern Green - Fresh, innovative, great for tech roles",
            "Elegant Purple - Creative, sophisticated, perfect for design roles",
            "Classic Black - Timeless, formal, excellent for executive positions",
            "Minimal Gray - Clean, modern, suitable for any industry",
            "Creative Orange - Bold, energetic, ideal for marketing roles"
        ]
    
    def export_resume(self, resume_html: Dict[str, str], output_dir: str = "output") -> Dict[str, str]:
        """Export resume as complete HTML package."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create complete HTML file with embedded CSS
        complete_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume</title>
    <style>
{resume_html['css']}
    </style>
</head>
<body>
{resume_html['html']}
</body>
</html>
        """
        
        # Write files
        html_file = output_path / "resume.html"
        css_file = output_path / "style.css"
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(complete_html)
        
        with open(css_file, 'w', encoding='utf-8') as f:
            f.write(resume_html['css'])
        
        return {
            "html_file": str(html_file),
            "css_file": str(css_file),
            "template": resume_html.get("template", "unknown"),
            "palette": resume_html.get("palette", "unknown")
        }
    
    def _get_modern_html_template(self) -> str:
        """Get modern template HTML."""
        return """
<div class="resume-container">
    <aside class="sidebar">
        <div class="profile-section">
            <div class="profile-header">
                <h1 class="name">{{name}}</h1>
                <div class="name-underline"></div>
            </div>
            {{profile_image}}
            <div class="contact-info">
                <div class="contact-item">
                    <i class="icon">✉️</i>
                    <span>{{email}}</span>
                </div>
                <div class="contact-item">
                    <i class="icon">📱</i>
                    <span>{{phone}}</span>
                </div>
                <div class="contact-item">
                    <i class="icon">📍</i>
                    <span>{{location}}</span>
                </div>
                <div class="contact-item">
                    <i class="icon">🔗</i>
                    <span>{{linkedin}}</span>
                </div>
                <div class="contact-item">
                    <i class="icon">⚡</i>
                    <span>{{github}}</span>
                </div>
            </div>
        </div>
        
        <div class="skills-section">
            <h2 class="section-title">
                <span class="title-text">Skills & Expertise</span>
                <div class="title-accent"></div>
            </h2>
            <div class="skills-content">
                {{skills_section}}
            </div>
        </div>
    </aside>
    
    <main class="main-content">
        <section class="summary-section">
            <h2 class="section-title">
                <span class="title-text">Professional Summary</span>
                <div class="title-accent"></div>
            </h2>
            <div class="summary-card">
                <p class="summary-text">{{professional_summary}}</p>
            </div>
        </section>
        
        <section class="experience-section">
            <h2 class="section-title">
                <span class="title-text">Professional Experience</span>
                <div class="title-accent"></div>
            </h2>
            <div class="timeline">
                {{experience_section}}
            </div>
        </section>
        
        <section class="education-section">
            <h2 class="section-title">
                <span class="title-text">Education</span>
                <div class="title-accent"></div>
            </h2>
            <div class="education-content">
                {{education_section}}
            </div>
        </section>
    </main>
</div>
        """
    
    def _get_modern_css_template(self) -> str:
        """Get modern template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    font-size: 16px;
    padding: 2rem 0;
}

.resume-container {
    display: flex;
    max-width: 1200px;
    margin: 0 auto;
    min-height: 95vh;
    background: {{background_color}};
    box-shadow: 0 20px 60px rgba(0,0,0,0.15);
    border-radius: 20px;
    overflow: hidden;
    position: relative;
}

.resume-container::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, {{primary_color}}, {{secondary_color}});
}

.sidebar {
    width: 35%;
    min-width: 280px;
    max-width: 380px;
    background: linear-gradient(135deg, {{primary_color}} 0%, {{secondary_color}} 100%);
    color: white;
    padding: 3rem 2.5rem;
    position: relative;
    overflow: hidden;
}

.sidebar::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 100%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
    animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { opacity: 0.3; }
    50% { opacity: 0.1; }
}

.main-content {
    flex: 1;
    padding: 3rem 2.5rem;
    background: {{background_color}};
    min-width: 0; /* Allow flex shrinking */
    overflow-wrap: break-word;
}

.profile-header {
    text-align: center;
    margin-bottom: 2.5rem;
}

.name {
    font-size: 2.2rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -0.5px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.name-underline {
    width: 60px;
    height: 3px;
    background: rgba(255,255,255,0.8);
    margin: 0 auto;
    border-radius: 2px;
}

.contact-info {
    margin-bottom: 3rem;
}

.contact-item {
    display: flex;
    align-items: center;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    padding: 0.5rem;
    border-radius: 8px;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.contact-item:hover {
    background: rgba(255,255,255,0.2);
    transform: translateX(5px);
}

.contact-item .icon {
    margin-right: 1rem;
    width: 20px;
    font-size: 1.2rem;
}

.section-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 2rem;
    color: {{primary_color}};
    position: relative;
    display: flex;
    align-items: center;
    gap: 1rem;
}

.title-text {
    position: relative;
}

.title-accent {
    flex: 1;
    height: 2px;
    background: linear-gradient(90deg, {{primary_color}}, transparent);
    border-radius: 1px;
}

.sidebar .section-title {
    color: {{text_contrast_color}};
    font-size: 1.3rem;
    font-weight: 700;
}

.sidebar .title-accent {
    background: linear-gradient(90deg, rgba(255,255,255,0.8), transparent);
}

.skills-content {
    position: relative;
    z-index: 2;
}

.skills-category {
    margin-bottom: 1.5rem;
    padding: 1rem;
    border-radius: 12px;
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.skills-category:hover {
    background: rgba(255,255,255,0.15);
    transform: translateY(-2px);
}

.skills-category h4 {
    font-size: 1.1rem;
    margin-bottom: 0.8rem;
    color: rgba(255,255,255,0.95);
    font-weight: 600;
}

.skills-list {
    font-size: 0.9rem;
    line-height: 1.7;
    color: rgba(255,255,255,0.85);
}

.summary-section {
    margin-bottom: 3rem;
}

.summary-card {
    background: {{section_bg}};
    padding: 2rem;
    border-radius: 16px;
    border-left: 4px solid {{primary_color}};
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}

.summary-card:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

.summary-text {
    font-size: 1.05rem;
    line-height: 1.8;
    color: {{text_dark}};
    text-align: justify;
}

.experience-section, .education-section {
    margin-bottom: 3rem;
}

.timeline {
    position: relative;
    padding-left: 2rem;
}

.timeline::before {
    content: '';
    position: absolute;
    left: 0;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(180deg, {{primary_color}}, {{secondary_color}});
    border-radius: 1px;
}

.experience-item, .education-item {
    margin-bottom: 2.5rem;
    padding: 2rem;
    background: {{section_bg}};
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    position: relative;
    transition: all 0.3s ease;
    border-left: 4px solid {{primary_color}};
}

.timeline .experience-item::before {
    content: '';
    position: absolute;
    left: -2.75rem;
    top: 2rem;
    width: 12px;
    height: 12px;
    background: {{primary_color}};
    border-radius: 50%;
    border: 3px solid {{background_color}};
    box-shadow: 0 0 0 3px {{primary_color}};
}

.experience-item:hover, .education-item:hover {
    box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    transform: translateY(-2px);
}

.experience-header h3, .education-item h3 {
    font-size: 1.3rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.8rem;
}

.experience-meta, .education-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1.2rem;
    font-size: 0.95rem;
    color: {{text_light}};
}

.company, .school {
    font-weight: 600;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding-left: 0;
    margin-top: 1rem;
}

.experience-description li {
    position: relative;
    padding-left: 2rem;
    margin-bottom: 0.8rem;
    color: {{text_dark}};
    line-height: 1.7;
}

.experience-description li:before {
    content: '▸';
    position: absolute;
    left: 0;
    top: 0;
    color: {{primary_color}};
    font-weight: bold;
    font-size: 1.2rem;
}

.education-content .education-item {
    border-left: 4px solid {{secondary_color}};
}

@media (max-width: 768px) {
    body {
        padding: 1rem 0;
    }
    
    .resume-container {
        flex-direction: column;
        margin: 0 1rem;
        border-radius: 16px;
    }
    
    .sidebar {
        width: 100%;
        padding: 2rem 1.5rem;
    }
    
    .main-content {
        padding: 2rem 1.5rem;
    }
    
    .name {
        font-size: 1.8rem;
    }
    
    .timeline {
        padding-left: 0;
    }
    
    .timeline::before {
        display: none;
    }
    
    .timeline .experience-item::before {
        display: none;
    }
    
    .experience-meta, .education-meta {
        flex-direction: column;
        gap: 0.5rem;
    }
}

@media print {
    body {
        background: white;
        padding: 0;
    }
    
    .resume-container {
        box-shadow: none;
        border-radius: 0;
    }
    
    .sidebar::before,
    .experience-item:hover,
    .education-item:hover,
    .summary-card:hover {
        transform: none;
        box-shadow: none;
    }
}
        """
    
    def _get_classic_html_template(self) -> str:
        """Get classic template HTML."""
        return """
<div class="resume-container">
    <header class="header">
        <h1 class="name">{{name}}</h1>
        <div class="contact-info">
            <span class="contact-item">{{email}}</span>
            <span class="contact-item">{{phone}}</span>
            <span class="contact-item">{{location}}</span>
            <span class="contact-item">{{linkedin}}</span>
            <span class="contact-item">{{github}}</span>
        </div>
    </header>
    
    <section class="summary-section">
        <h2 class="section-title">Professional Summary</h2>
        <p class="summary-text">{{professional_summary}}</p>
    </section>
    
    <section class="experience-section">
        <h2 class="section-title">Professional Experience</h2>
        {{experience_section}}
    </section>
    
    <section class="education-section">
        <h2 class="section-title">Education</h2>
        {{education_section}}
    </section>
    
    <section class="skills-section">
        <h2 class="section-title">Skills & Competencies</h2>
        {{skills_section}}
    </section>
</div>
        """
    
    def _get_timeline_css_template(self) -> str:
        """Get Timeline template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Poppins', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: #f7f9fc;
}

.timeline-container {
    max-width: 1000px;
    margin: 0 auto;
    background: {{background_color}};
    box-shadow: 0 8px 30px rgba(0,0,0,0.08);
    border-radius: 12px;
    overflow: hidden;
}

.timeline-header {
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 3rem 2.5rem;
    position: relative;
    overflow: hidden;
}

.timeline-header::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 50%);
    transform: rotate(45deg);
}

.header-content {
    position: relative;
    z-index: 2;
    text-align: center;
}

.profile-name {
    font-size: 2.8rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    letter-spacing: -0.02em;
}

.profile-title {
    font-size: 1.3rem;
    font-weight: 400;
    opacity: 0.95;
    margin-bottom: 1.5rem;
}

.contact-timeline {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1.5rem;
}

.contact-timeline-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 400;
    background: rgba(255,255,255,0.15);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.timeline-content {
    padding: 3rem 2.5rem;
}

.timeline-section {
    margin-bottom: 3rem;
}

.timeline-section:last-child {
    margin-bottom: 0;
}

.timeline-title {
    font-size: 1.8rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 2rem;
    position: relative;
    display: inline-block;
}

.timeline-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    border-radius: 2px;
}

.timeline-wrapper {
    position: relative;
    padding-left: 2rem;
}

.timeline-wrapper::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, {{primary_color}}, {{secondary_color}});
}

.timeline-item {
    position: relative;
    margin-bottom: 2.5rem;
    background: {{section_bg}};
    border-radius: 10px;
    padding: 1.5rem;
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    border-left: 4px solid {{primary_color}};
    margin-left: 1.25rem;
}

.timeline-item::before {
    content: '';
    position: absolute;
    left: -2.08rem;
    top: 1.875rem;
    width: 12px;
    height: 12px;
    background: {{primary_color}};
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 3px {{primary_color}};
}

.timeline-item:last-child {
    margin-bottom: 0;
}

.timeline-item-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 1rem;
    flex-wrap: wrap;
}

.timeline-item-title {
    font-weight: 600;
    color: {{text_dark}};
    font-size: 1.2rem;
    margin-bottom: 0.3rem;
}

.timeline-item-company {
    color: {{primary_color}};
    font-weight: 500;
    font-size: 1.05rem;
}

.timeline-date {
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 0.4rem 1rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    white-space: nowrap;
}

.timeline-description {
    color: {{text_light}};
    line-height: 1.7;
    margin-top: 0.6rem;
}

.timeline-description ul {
    list-style: none;
    padding-left: 0;
    margin-top: 0.6rem;
}

.timeline-description li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
}

.timeline-description li::before {
    content: '→';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-weight: bold;
    font-size: 1.1rem;
}

.skills-showcase {
    background: linear-gradient(135deg, rgba({{primary_rgb}}, 0.08), rgba({{secondary_rgb}}, 0.08));
    padding: 2.5rem;
    border-radius: 15px;
    margin: 2.5rem 0;
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 1.5rem;
}

.skill-category {
    background: {{background_color}};
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    border-top: 4px solid {{primary_color}};
}

.skill-category h4 {
    color: {{primary_color}};
    margin-bottom: 1rem;
    font-weight: 600;
    font-size: 1.1rem;
}

.skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.6rem;
}

.skill-tag {
    background: linear-gradient(135deg, rgba({{primary_rgb}}, 0.08), rgba({{secondary_rgb}}, 0.08));
    color: {{text_dark}};
    padding: 0.5rem 1rem;
    border-radius: 25px;
    font-size: 0.85rem;
    font-weight: 500;
    border: 1px solid rgba({{primary_rgb}}, 0.3);
    transition: all 0.3s ease;
    position: relative;
}

.skill-tag:hover {
    background: {{primary_color}};
    color: white;
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.education-timeline .timeline-item {
    border-left-color: {{secondary_color}};
}

.education-timeline .timeline-item::before {
    background: {{secondary_color}};
    box-shadow: 0 0 0 3px {{secondary_color}};
}

@media (max-width: 768px) {
    .timeline-header {
        padding: 2rem 1.5rem;
    }
    
    .profile-name {
        font-size: 2.2rem;
    }
    
    .timeline-content {
        padding: 2rem 1.5rem;
    }
    
    .timeline-wrapper {
        padding-left: 1.25rem;
    }
    
    .timeline-item {
        margin-left: 1rem;
        padding: 1.25rem;
    }
    
    .timeline-item::before {
        left: -1.75rem;
    }
    
    .timeline-item-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .timeline-date {
        margin-top: 0.5rem;
    }
    
    .skills-showcase {
        padding: 1.5rem 1.25rem;
    }
    
    .skills-grid {
        grid-template-columns: 1fr;
    }
}
        """
    
    def _get_card_css_template(self) -> str:
        """Get Card template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    padding: 2rem 1rem;
}

.card-container {
    max-width: 1200px;
    margin: 0 auto;
    position: relative;
}

.card-hero {
    background: {{background_color}};
    border-radius: 20px;
    margin-bottom: 2rem;
    overflow: hidden;
    position: relative;
    box-shadow: 0 20px 40px rgba(0,0,0,0.15);
}

.hero-content {
    padding: 3rem 2rem;
    text-align: center;
    position: relative;
    z-index: 2;
}

.hero-decoration {
    position: absolute;
    top: 0;
    right: 0;
    width: 300px;
    height: 300px;
    background: linear-gradient(135deg, {{primary_color}}20, {{secondary_color}}20);
    border-radius: 50%;
    transform: translate(30%, -30%);
    z-index: 1;
}

.profile-circle {
    width: 120px;
    height: 120px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    border-radius: 50%;
    margin: 0 auto 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    position: relative;
    z-index: 3;
}

.profile-icon {
    font-size: 3rem;
    filter: brightness(0) invert(1);
}

.card-name {
    font-size: 3rem;
    font-weight: 800;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
    position: relative;
    z-index: 3;
}

.card-title {
    font-size: 1.3rem;
    font-weight: 500;
    color: {{text_light}};
    margin-bottom: 2rem;
    position: relative;
    z-index: 3;
}

.hero-contacts {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 2rem;
    position: relative;
    z-index: 3;
}

.hero-contact {
    background: linear-gradient(135deg, {{primary_color}}15, {{secondary_color}}15);
    padding: 0.75rem 1.5rem;
    border-radius: 25px;
    font-weight: 500;
    color: {{primary_color}};
    border: 1px solid {{primary_color}}30;
}

.cards-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.info-card {
    background: {{background_color}};
    border-radius: 15px;
    padding: 0;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
    overflow: hidden;
    transition: all 0.3s ease;
    position: relative;
}

.info-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0,0,0,0.15);
}

.card-header {
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: relative;
    overflow: hidden;
}

.card-header::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: rgba(255,255,255,0.1);
    border-radius: 50%;
    transform: translate(30%, -30%);
}

.card-heading {
    font-size: 1.3rem;
    font-weight: 600;
    position: relative;
    z-index: 2;
}

.card-icon {
    font-size: 2rem;
    opacity: 0.8;
    position: relative;
    z-index: 2;
}

.card-content {
    padding: 2rem;
}

.summary-text {
    font-size: 1rem;
    line-height: 1.8;
    color: {{text_dark}};
}

.experience-item,
.education-item {
    background: {{section_bg}};
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    border-radius: 10px;
    border-left: 4px solid {{primary_color}};
    transition: all 0.3s ease;
}

.experience-item:last-child,
.education-item:last-child {
    margin-bottom: 0;
}

.experience-item:hover,
.education-item:hover {
    background: {{primary_color}}08;
    transform: translateX(5px);
}

.experience-header h3,
.education-item h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
}

.experience-meta,
.education-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.9rem;
    color: {{text_light}};
}

.company,
.school {
    font-weight: 600;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.4rem;
    line-height: 1.6;
    font-size: 0.9rem;
}

.experience-description li::before {
    content: '▸';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-weight: bold;
}

.skills-category {
    background: {{section_bg}};
    padding: 1.25rem;
    margin-bottom: 1rem;
    border-radius: 8px;
    border-left: 3px solid {{secondary_color}};
}

.skills-category:last-child {
    margin-bottom: 0;
}

.skills-category h4 {
    font-size: 1rem;
    font-weight: 600;
    color: {{text_dark}};
    margin-bottom: 0.75rem;
}

.skills-list {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    font-size: 0.85rem;
    color: {{text_dark}};
}

.skill-item {
    background: linear-gradient(135deg, {{primary_color}}12, {{secondary_color}}12);
    color: {{primary_color}};
    padding: 0.3rem 0.8rem;
    border-radius: 15px;
    font-weight: 500;
    border: 1px solid {{primary_color}}20;
}

.card-footer {
    background: {{background_color}};
    border-radius: 15px;
    padding: 2rem;
    text-align: center;
    box-shadow: 0 10px 25px rgba(0,0,0,0.1);
}

.social-links {
    display: flex;
    justify-content: center;
    gap: 1.5rem;
}

.social-link {
    display: inline-flex;
    align-items: center;
    padding: 0.75rem 1.5rem;
    text-decoration: none;
    border-radius: 25px;
    font-weight: 600;
    transition: all 0.3s ease;
    color: white;
}

.social-link.linkedin {
    background: linear-gradient(135deg, #0077B5, #00A0DC);
}

.social-link.github {
    background: linear-gradient(135deg, #333, #666);
}

.social-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.2);
}

@media (max-width: 768px) {
    body {
        padding: 1rem 0.5rem;
    }
    
    .hero-content {
        padding: 2rem 1.5rem;
    }
    
    .card-name {
        font-size: 2.2rem;
    }
    
    .hero-contacts {
        flex-direction: column;
        gap: 1rem;
    }
    
    .cards-grid {
        grid-template-columns: 1fr;
        gap: 1.5rem;
    }
    
    .card-content {
        padding: 1.5rem;
    }
    
    .social-links {
        flex-direction: column;
        gap: 1rem;
    }
}

@media (max-width: 480px) {
    .profile-circle {
        width: 100px;
        height: 100px;
        margin-bottom: 1.5rem;
    }
    
    .profile-icon {
        font-size: 2.5rem;
    }
    
    .card-name {
        font-size: 2rem;
    }
    
    .card-header {
        padding: 1.25rem;
    }
    
    .card-content {
        padding: 1.25rem;
    }
}
        """
    
    def _get_split_css_template(self) -> str:
        """Get Split template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Nunito', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: #f8f9fa;
}

.split-container {
    display: grid;
    grid-template-columns: 350px 1fr;
    min-height: 100vh;
    max-width: 1400px;
    margin: 0 auto;
    box-shadow: 0 0 30px rgba(0,0,0,0.1);
    background: {{background_color}};
}

.split-sidebar {
    background: linear-gradient(180deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 2.5rem 2rem;
    position: relative;
    overflow: hidden;
}

.split-sidebar::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100%;
    height: 100%;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="20" cy="20" r="2" fill="rgba(255,255,255,0.1)"/><circle cx="80" cy="40" r="1" fill="rgba(255,255,255,0.05)"/><circle cx="40" cy="80" r="1.5" fill="rgba(255,255,255,0.08)"/></svg>');
    opacity: 0.6;
}

.profile-section {
    text-align: center;
    margin-bottom: 3rem;
    position: relative;
    z-index: 2;
}

.profile-avatar {
    width: 120px;
    height: 120px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    margin: 0 auto 1.5rem;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 3px solid rgba(255,255,255,0.3);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

.avatar-text {
    font-size: 2.5rem;
    font-weight: 700;
    color: white;
}

.profile-name {
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.profile-role {
    font-size: 1.1rem;
    font-weight: 400;
    opacity: 0.9;
    margin-bottom: 2rem;
}

.sidebar-title {
    font-size: 1.2rem;
    font-weight: 700;
    margin-bottom: 1.5rem;
    position: relative;
    padding-bottom: 0.5rem;
}

.sidebar-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 40px;
    height: 2px;
    background: rgba(255,255,255,0.4);
}

.contact-section,
.skills-sidebar {
    margin-bottom: 2.5rem;
    position: relative;
    z-index: 2;
}

.contact-list {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 1rem;
    background: rgba(255,255,255,0.1);
    padding: 0.8rem;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.contact-item:hover {
    background: rgba(255,255,255,0.2);
    transform: translateX(5px);
}

.contact-icon {
    font-size: 1.2rem;
    width: 24px;
    text-align: center;
}

.contact-text {
    font-size: 0.9rem;
    font-weight: 500;
}

.sidebar-skills .skills-category {
    margin-bottom: 1.5rem;
}

.sidebar-skills .skills-category h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    color: rgba(255,255,255,0.9);
}

.sidebar-skills .skills-list {
    font-size: 0.85rem;
    line-height: 1.8;
    color: rgba(255,255,255,0.8);
    font-weight: 400;
}

.split-main {
    padding: 3rem 2.5rem;
    background: {{background_color}};
}

.main-section {
    margin-bottom: 3rem;
}

.main-section:last-child {
    margin-bottom: 0;
}

.section-title {
    font-size: 2rem;
    font-weight: 700;
    color: {{primary_color}};
    margin-bottom: 2rem;
    position: relative;
    display: inline-block;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -8px;
    left: 0;
    width: 100%;
    height: 3px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    border-radius: 2px;
}

.summary-content {
    font-size: 1.1rem;
    line-height: 1.8;
    color: {{text_dark}};
    text-align: justify;
}

.experience-timeline,
.education-list {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.experience-item,
.education-item {
    background: {{section_bg}};
    padding: 2rem;
    border-radius: 12px;
    border-left: 5px solid {{primary_color}};
    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
    transition: all 0.3s ease;
}

.experience-item:hover,
.education-item:hover {
    box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    transform: translateY(-3px);
}

.experience-header h3,
.education-item h3 {
    font-size: 1.4rem;
    font-weight: 700;
    color: {{primary_color}};
    margin-bottom: 0.8rem;
}

.experience-meta,
.education-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1.2rem;
    font-size: 1rem;
    color: {{text_light}};
}

.company,
.school {
    font-weight: 700;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 2rem;
    margin-bottom: 0.8rem;
    line-height: 1.7;
    font-size: 1rem;
}

.experience-description li::before {
    content: '▶';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-weight: bold;
    font-size: 0.9rem;
}

@media (max-width: 1024px) {
    .split-container {
        grid-template-columns: 300px 1fr;
    }
    
    .split-sidebar {
        padding: 2rem 1.5rem;
    }
    
    .split-main {
        padding: 2.5rem 2rem;
    }
}

@media (max-width: 768px) {
    .split-container {
        grid-template-columns: 1fr;
        min-height: auto;
    }
    
    .split-sidebar {
        padding: 2rem 1.5rem;
    }
    
    .profile-section {
        margin-bottom: 2rem;
    }
    
    .contact-section,
    .skills-sidebar {
        margin-bottom: 2rem;
    }
    
    .split-main {
        padding: 2rem 1.5rem;
    }
    
    .section-title {
        font-size: 1.6rem;
    }
}
        """
    
    def _get_gradient_css_template(self) -> str:
        """Get Gradient template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;500;600;700;800;900&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Montserrat', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
}

.gradient-container {
    max-width: 1200px;
    margin: 0 auto;
    background: {{background_color}};
    min-height: 100vh;
    position: relative;
    overflow: hidden;
}

.gradient-header {
    height: 400px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    position: relative;
    overflow: hidden;
    display: flex;
    align-items: center;
    justify-content: center;
}

.header-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0,0,0,0.1);
    z-index: 2;
    display: flex;
    align-items: center;
    justify-content: center;
}

.gradient-shapes {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 1;
}

.shape {
    position: absolute;
    border-radius: 50%;
    background: rgba(255,255,255,0.1);
    animation: float 6s ease-in-out infinite;
}

.shape-1 {
    width: 200px;
    height: 200px;
    top: 10%;
    right: 10%;
    animation-delay: 0s;
}

.shape-2 {
    width: 150px;
    height: 150px;
    bottom: 20%;
    left: 5%;
    animation-delay: 2s;
}

.shape-3 {
    width: 100px;
    height: 100px;
    top: 60%;
    right: 30%;
    animation-delay: 4s;
}

@keyframes float {
    0%, 100% { transform: translateY(0px); }
    50% { transform: translateY(-20px); }
}

.profile-section {
    display: flex;
    align-items: center;
    gap: 2rem;
    text-align: left;
    color: white;
    z-index: 3;
    position: relative;
    padding: 2rem;
}

.profile-image-wrapper {
    flex-shrink: 0;
}

.profile-gradient-circle {
    width: 150px;
    height: 150px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 4px solid rgba(255,255,255,0.3);
    backdrop-filter: blur(10px);
}

.profile-initial {
    font-size: 4rem;
    font-weight: 900;
    color: white;
}

.profile-info {
    flex: 1;
}

.gradient-name {
    font-size: 3.5rem;
    font-weight: 900;
    margin-bottom: 0.5rem;
    text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
}

.gradient-title {
    font-size: 1.5rem;
    font-weight: 400;
    opacity: 0.95;
    margin-bottom: 1.5rem;
}

.contact-gradient {
    display: flex;
    flex-wrap: wrap;
    gap: 2rem;
}

.gradient-contact {
    background: rgba(255,255,255,0.15);
    padding: 0.8rem 1.5rem;
    border-radius: 30px;
    font-weight: 500;
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.2);
}

.gradient-content {
    padding: 3rem;
    position: relative;
    z-index: 2;
    margin-top: -50px;
    border-radius: 30px 30px 0 0;
    background: {{background_color}};
}

.content-grid {
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 3rem;
}

.gradient-section {
    margin-bottom: 3rem;
}

.gradient-section:last-child {
    margin-bottom: 0;
}

.section-header {
    display: flex;
    align-items: center;
    gap: 1rem;
    margin-bottom: 2rem;
}

.gradient-section-title {
    font-size: 2rem;
    font-weight: 800;
    color: {{primary_color}};
    position: relative;
}

.title-line {
    flex: 1;
    height: 3px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    border-radius: 2px;
}

.gradient-summary {
    font-size: 1.1rem;
    line-height: 1.8;
    color: {{text_dark}};
    text-align: justify;
}

.gradient-experience,
.gradient-education {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.experience-item,
.education-item {
    background: linear-gradient(135deg, {{section_bg}}, rgba({{primary_rgb}}, 0.05));
    padding: 2rem;
    border-radius: 15px;
    border: 1px solid rgba({{primary_rgb}}, 0.1);
    box-shadow: 0 5px 20px rgba(0,0,0,0.08);
    position: relative;
    overflow: hidden;
}

.experience-item::before,
.education-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    width: 5px;
    height: 100%;
    background: linear-gradient(180deg, {{primary_color}}, {{secondary_color}});
}

.experience-header h3,
.education-item h3 {
    font-size: 1.3rem;
    font-weight: 700;
    color: {{primary_color}};
    margin-bottom: 0.8rem;
}

.experience-meta,
.education-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    color: {{text_light}};
}

.company,
.school {
    font-weight: 700;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 2rem;
    margin-bottom: 0.6rem;
    line-height: 1.7;
}

.experience-description li::before {
    content: '●';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-weight: bold;
    font-size: 1.2rem;
}

.content-sidebar {
    display: flex;
    flex-direction: column;
    gap: 2rem;
}

.gradient-card {
    background: linear-gradient(135deg, rgba({{primary_rgb}}, 0.08), rgba({{secondary_rgb}}, 0.08));
    padding: 2rem;
    border-radius: 20px;
    border: 1px solid rgba({{primary_rgb}}, 0.15);
    position: relative;
    overflow: hidden;
}

.gradient-card::before {
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 100px;
    height: 100px;
    background: radial-gradient(circle, rgba({{primary_rgb}}, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    transform: translate(30%, -30%);
}

.card-title {
    font-size: 1.3rem;
    font-weight: 700;
    color: {{primary_color}};
    margin-bottom: 1.5rem;
    position: relative;
    z-index: 2;
}

.gradient-skills .skills-category {
    margin-bottom: 1.5rem;
}

.gradient-skills .skills-category:last-child {
    margin-bottom: 0;
}

.gradient-skills .skills-category h4 {
    font-size: 1rem;
    font-weight: 600;
    color: {{text_dark}};
    margin-bottom: 0.8rem;
}

.gradient-skills .skills-list {
    font-size: 0.9rem;
    line-height: 1.7;
    color: {{text_dark}};
}

.gradient-links {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.gradient-link {
    display: inline-block;
    text-decoration: none;
    padding: 1rem 1.5rem;
    border-radius: 25px;
    font-weight: 600;
    text-align: center;
    transition: all 0.3s ease;
    color: white;
    position: relative;
    z-index: 2;
}

.gradient-link.linkedin {
    background: linear-gradient(135deg, #0077B5, #00A0DC);
}

.gradient-link.github {
    background: linear-gradient(135deg, #333, #666);
}

.gradient-link:hover {
    transform: translateY(-3px);
    box-shadow: 0 10px 25px rgba(0,0,0,0.2);
}

@media (max-width: 1024px) {
    .content-grid {
        grid-template-columns: 1fr;
        gap: 2rem;
    }
    
    .gradient-content {
        padding: 2rem;
    }
}

@media (max-width: 768px) {
    .gradient-header {
        height: 300px;
    }
    
    .profile-section {
        flex-direction: column;
        text-align: center;
        gap: 1.5rem;
        padding: 1.5rem;
    }
    
    .profile-gradient-circle {
        width: 120px;
        height: 120px;
    }
    
    .profile-initial {
        font-size: 3rem;
    }
    
    .gradient-name {
        font-size: 2.5rem;
    }
    
    .contact-gradient {
        justify-content: center;
        gap: 1rem;
    }
    
    .gradient-contact {
        font-size: 0.9rem;
        padding: 0.6rem 1.2rem;
    }
    
    .gradient-content {
        padding: 2rem 1.5rem;
        margin-top: -30px;
    }
    
    .gradient-section-title {
        font-size: 1.6rem;
    }
}

@media (max-width: 480px) {
    .gradient-header {
        height: 250px;
    }
    
    .profile-section {
        padding: 1rem;
    }
    
    .gradient-name {
        font-size: 2rem;
    }
    
    .gradient-content {
        padding: 1.5rem 1rem;
    }
    
    .gradient-card {
        padding: 1.5rem;
    }
}
        """
    
    def _get_classic_css_template(self) -> str:
        """Get classic template CSS."""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Times New Roman', serif;
    line-height: 1.6;
    color: {{text_dark}};
    background-color: {{background_color}};
}

.resume-container {
    max-width: 800px;
    margin: 2rem auto;
    padding: 2rem;
    background: {{background_color}};
    box-shadow: 0 0 15px rgba(0,0,0,0.1);
}

.header {
    text-align: center;
    margin-bottom: 2rem;
    padding-bottom: 1rem;
    border-bottom: 2px solid {{primary_color}};
}

.name {
    font-size: 2rem;
    font-weight: bold;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
}

.contact-info {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.9rem;
    color: {{text_light}};
}

.contact-item {
    white-space: nowrap;
}

.section-title {
    font-size: 1.3rem;
    font-weight: bold;
    color: {{primary_color}};
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 1px;
}

.summary-section, .experience-section, .education-section, .skills-section {
    margin-bottom: 2rem;
}

.summary-text {
    font-size: 1rem;
    line-height: 1.7;
    text-align: justify;
    color: {{text_dark}};
}

.experience-item, .education-item {
    margin-bottom: 1.5rem;
}

.experience-header h3, .education-item h3 {
    font-size: 1.1rem;
    font-weight: bold;
    color: {{primary_color}};
    margin-bottom: 0.3rem;
}

.experience-meta, .education-meta {
    font-size: 0.9rem;
    color: {{text_light}};
    margin-bottom: 0.5rem;
    font-style: italic;
}

.company, .school {
    font-weight: bold;
}

.experience-description {
    list-style-type: disc;
    padding-left: 2rem;
    margin-top: 0.5rem;
}

.experience-description li {
    margin-bottom: 0.3rem;
    color: {{text_dark}};
}

.skills-category {
    margin-bottom: 1rem;
}

.skills-category h4 {
    font-size: 1rem;
    color: {{text_dark}};
    margin-bottom: 0.3rem;
    font-weight: bold;
}

.skills-list {
    font-size: 0.95rem;
    line-height: 1.5;
    color: {{text_dark}};
}

@media (max-width: 768px) {
    .resume-container {
        margin: 1rem;
        padding: 1.5rem;
    }
    
    .name {
        font-size: 1.7rem;
    }
    
    .contact-info {
        flex-direction: column;
        gap: 0.3rem;
    }
}
        """
    
    def _get_creative_html_template(self) -> str:
        """Get creative template HTML."""
        return """
<div class="resume-container">
    <div class="creative-header">
        <div class="header-bg"></div>
        <div class="header-content">
            <h1 class="name">{{name}}</h1>
            <div class="contact-grid">
                <div class="contact-item">📧 {{email}}</div>
                <div class="contact-item">📱 {{phone}}</div>
                <div class="contact-item">📍 {{location}}</div>
                <div class="contact-item">💼 {{linkedin}}</div>
                <div class="contact-item">💻 {{github}}</div>
            </div>
        </div>
    </div>
    
    <div class="content-grid">
        <div class="left-column">
            <section class="summary-card">
                <h2 class="section-title">About Me</h2>
                <p class="summary-text">{{professional_summary}}</p>
            </section>
            
            <section class="skills-card">
                <h2 class="section-title">Skills</h2>
                {{skills_section}}
            </section>
        </div>
        
        <div class="right-column">
            <section class="experience-card">
                <h2 class="section-title">Experience</h2>
                {{experience_section}}
            </section>
            
            <section class="education-card">
                <h2 class="section-title">Education</h2>
                {{education_section}}
            </section>
        </div>
    </div>
</div>
        """
    
    def _get_creative_css_template(self) -> str:
        """Get creative template CSS."""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: linear-gradient(135deg, {{section_bg}}, {{background_color}});
    min-height: 100vh;
}

.resume-container {
    max-width: 1000px;
    margin: 2rem auto;
    background: {{background_color}};
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 20px 40px rgba(0,0,0,0.1);
}

.creative-header {
    position: relative;
    height: 200px;
    overflow: hidden;
}

.header-bg {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(45deg, {{primary_color}}, {{secondary_color}});
    opacity: 0.9;
}

.header-bg::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><circle cx="25" cy="25" r="2" fill="white" opacity="0.3"/><circle cx="75" cy="75" r="1.5" fill="white" opacity="0.2"/><circle cx="50" cy="10" r="1" fill="white" opacity="0.4"/></svg>');
}

.header-content {
    position: relative;
    z-index: 2;
    padding: 2rem;
    text-align: center;
    color: white;
}

.name {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.3);
}

.contact-grid {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 1rem;
    font-size: 0.9rem;
}

.contact-item {
    background: rgba(255,255,255,0.2);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.content-grid {
    display: grid;
    grid-template-columns: 1fr 2fr;
    gap: 2rem;
    padding: 2rem;
}

.left-column, .right-column {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

.summary-card, .skills-card, .experience-card, .education-card {
    background: {{section_bg}};
    padding: 1.5rem;
    border-radius: 15px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    border-left: 4px solid {{primary_color}};
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 1rem;
    position: relative;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 30px;
    height: 3px;
    background: {{secondary_color}};
    border-radius: 2px;
}

.summary-text {
    font-size: 1rem;
    line-height: 1.7;
    color: {{text_dark}};
}

.skills-category {
    margin-bottom: 1rem;
}

.skills-category h4 {
    font-size: 1rem;
    color: {{text_dark}};
    margin-bottom: 0.5rem;
    font-weight: 600;
}

.skills-list {
    background: {{background_color}};
    padding: 0.8rem;
    border-radius: 10px;
    font-size: 0.9rem;
    line-height: 1.5;
}

.experience-item, .education-item {
    margin-bottom: 1.5rem;
    position: relative;
}

.experience-header h3, .education-item h3 {
    font-size: 1.1rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
}

.experience-meta, .education-meta {
    font-size: 0.9rem;
    color: {{text_light}};
    margin-bottom: 0.8rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.company, .school {
    font-weight: 600;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
    color: {{text_dark}};
}

.experience-description li::before {
    content: '●';
    position: absolute;
    left: 0;
    color: {{secondary_color}};
    font-size: 1.2rem;
    line-height: 1;
}

@media (max-width: 768px) {
    .resume-container {
        margin: 1rem;
        border-radius: 15px;
    }
    
    .content-grid {
        grid-template-columns: 1fr;
        padding: 1.5rem;
    }
    
    .name {
        font-size: 2rem;
    }
    
    .contact-grid {
        flex-direction: column;
        gap: 0.5rem;
    }
}
        """
    
    def _get_minimal_html_template(self) -> str:
        """Get minimal template HTML."""
        return """
<div class="resume-container">
    <header class="minimal-header">
        <h1 class="name">{{name}}</h1>
        <div class="contact-line">
            {{email}} • {{phone}} • {{location}} • {{linkedin}} • {{github}}
        </div>
    </header>
    
    <section class="section">
        <h2 class="section-title">Summary</h2>
        <div class="section-content">
            <p class="summary-text">{{professional_summary}}</p>
        </div>
    </section>
    
    <section class="section">
        <h2 class="section-title">Experience</h2>
        <div class="section-content">
            {{experience_section}}
        </div>
    </section>
    
    <section class="section">
        <h2 class="section-title">Education</h2>
        <div class="section-content">
            {{education_section}}
        </div>
    </section>
    
    <section class="section">
        <h2 class="section-title">Skills</h2>
        <div class="section-content">
            {{skills_section}}
        </div>
    </section>
</div>
        """
    
    def _get_minimal_css_template(self) -> str:
        """Get minimal template CSS."""
        return """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Helvetica Neue', Arial, sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background-color: {{background_color}};
}

.resume-container {
    max-width: 750px;
    margin: 3rem auto;
    padding: 3rem;
    background: {{background_color}};
}

.minimal-header {
    text-align: center;
    margin-bottom: 3rem;
    padding-bottom: 1rem;
}

.name {
    font-size: 2.2rem;
    font-weight: 300;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
    letter-spacing: 2px;
}

.contact-line {
    font-size: 0.9rem;
    color: {{text_light}};
    letter-spacing: 0.5px;
}

.section {
    margin-bottom: 2.5rem;
}

.section-title {
    font-size: 1rem;
    font-weight: 600;
    color: {{primary_color}};
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-bottom: 1rem;
    border-bottom: 1px solid {{border_color}};
    padding-bottom: 0.3rem;
}

.section-content {
    padding-left: 0;
}

.summary-text {
    font-size: 1rem;
    line-height: 1.7;
    color: {{text_dark}};
}

.experience-item, .education-item {
    margin-bottom: 2rem;
}

.experience-header h3, .education-item h3 {
    font-size: 1.1rem;
    font-weight: 500;
    color: {{text_dark}};
    margin-bottom: 0.3rem;
}

.experience-meta, .education-meta {
    font-size: 0.9rem;
    color: {{text_light}};
    margin-bottom: 0.8rem;
}

.company, .school {
    font-weight: 500;
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    margin-bottom: 0.4rem;
    color: {{text_dark}};
    font-size: 0.95rem;
    line-height: 1.6;
}

.skills-category {
    margin-bottom: 1rem;
}

.skills-category h4 {
    font-size: 0.95rem;
    color: {{text_dark}};
    font-weight: 500;
    margin-bottom: 0.3rem;
}

.skills-list {
    font-size: 0.9rem;
    color: {{text_light}};
    line-height: 1.5;
}

@media (max-width: 768px) {
    .resume-container {
        margin: 1rem;
        padding: 2rem;
    }
    
    .name {
        font-size: 1.8rem;
        letter-spacing: 1px;
    }
    
    .contact-line {
        font-size: 0.8rem;
        line-height: 1.4;
    }
}
        """
    
    def _generate_original_layout_html(self, resume_data: Dict[str, Any], original_analysis: Dict[str, Any] = None) -> str:
        """Generate HTML that preserves original resume layout structure."""
        
        # Extract data safely
        contact_info = resume_data.get('contact_info', {})
        name = getattr(contact_info, 'name', '') if hasattr(contact_info, 'name') else contact_info.get('name', 'Your Name')
        email = getattr(contact_info, 'email', '') if hasattr(contact_info, 'email') else contact_info.get('email', '')
        phone = getattr(contact_info, 'phone', '') if hasattr(contact_info, 'phone') else contact_info.get('phone', '')
        location = getattr(contact_info, 'location', '') if hasattr(contact_info, 'location') else contact_info.get('location', '')
        linkedin = getattr(contact_info, 'linkedin', '') if hasattr(contact_info, 'linkedin') else contact_info.get('linkedin', '')
        github = getattr(contact_info, 'github', '') if hasattr(contact_info, 'github') else contact_info.get('github', '')
        
        professional_summary = resume_data.get('professional_summary', '')
        
        # Analyze original layout if analysis data is available
        layout_type = "single_column"  # default
        if original_analysis and 'layout_analysis' in original_analysis:
            layout_type = original_analysis['layout_analysis'].get('type', 'single_column')
        
        # Generate HTML based on detected layout
        if layout_type == "two_column" or layout_type == "sidebar":
            return self._generate_sidebar_layout_html(resume_data, original_analysis)
        else:
            return self._generate_single_column_layout_html(resume_data, original_analysis)
    
    def _generate_single_column_layout_html(self, resume_data: Dict[str, Any], original_analysis: Dict[str, Any] = None) -> str:
        """Generate single-column layout HTML that matches original structure."""
        
        # Extract data safely
        contact_info = resume_data.get('contact_info', {})
        name = getattr(contact_info, 'name', '') if hasattr(contact_info, 'name') else contact_info.get('name', 'Your Name')
        email = getattr(contact_info, 'email', '') if hasattr(contact_info, 'email') else contact_info.get('email', '')
        phone = getattr(contact_info, 'phone', '') if hasattr(contact_info, 'phone') else contact_info.get('phone', '')
        location = getattr(contact_info, 'location', '') if hasattr(contact_info, 'location') else contact_info.get('location', '')
        linkedin = getattr(contact_info, 'linkedin', '') if hasattr(contact_info, 'linkedin') else contact_info.get('linkedin', '')
        github = getattr(contact_info, 'github', '') if hasattr(contact_info, 'github') else contact_info.get('github', '')
        
        professional_summary = resume_data.get('professional_summary', '')

        # Build contact info line
        contact_parts = []
        if email: contact_parts.append(email)
        if phone: contact_parts.append(phone)
        if location: contact_parts.append(location)
        if linkedin: contact_parts.append(linkedin)
        if github: contact_parts.append(github)
        contact_line = ' • '.join(contact_parts)

        # Build experience section
        experience_html = ""
        job_experiences = resume_data.get('job_experiences', [])
        for job in job_experiences:
            job_title = getattr(job, 'job_title', '') if hasattr(job, 'job_title') else job.get('job_title', '')
            company = getattr(job, 'company', '') if hasattr(job, 'company') else job.get('company', '')
            start_date = getattr(job, 'start_date', '') if hasattr(job, 'start_date') else job.get('start_date', '')
            end_date = getattr(job, 'end_date', 'Present') if hasattr(job, 'end_date') else job.get('end_date', 'Present')
            job_location = getattr(job, 'location', '') if hasattr(job, 'location') else job.get('location', '')
            descriptions = getattr(job, 'description', []) if hasattr(job, 'description') else job.get('description', [])
            
            experience_html += f'''
            <div class="original-experience-item">
                <div class="job-title">{job_title}</div>
                <div class="job-details">
                    <span class="company">{company}</span>
                    {f'<span class="job-location">{job_location}</span>' if job_location else ''}
                    <span class="job-dates">{start_date} - {end_date}</span>
                </div>
                <ul class="job-description">
            '''
            
            # Handle both string and list descriptions
            if isinstance(descriptions, str):
                # Single string description (from role adaptation) - may contain bullet points
                if '•' in descriptions:
                    # Split by bullet points and create list items
                    bullet_points = [point.strip() for point in descriptions.split('•') if point.strip()]
                    for point in bullet_points:
                        experience_html += f"<li>{point}</li>"
                else:
                    # Single description without bullet points
                    experience_html += f"<li>{descriptions}</li>"
            else:
                # List of descriptions (original format)
                for desc in descriptions:
                    experience_html += f"<li>{desc}</li>"
            
            experience_html += "</ul></div>"
        
        # Build education section
        education_html = ""
        education_list = resume_data.get('education', [])
        for edu in education_list:
            degree = getattr(edu, 'degree', '') if hasattr(edu, 'degree') else edu.get('degree', '')
            school = getattr(edu, 'school', '') if hasattr(edu, 'school') else edu.get('school', '')
            graduation_date = getattr(edu, 'graduation_date', '') if hasattr(edu, 'graduation_date') else edu.get('graduation_date', '')
            gpa = getattr(edu, 'gpa', '') if hasattr(edu, 'gpa') else edu.get('gpa', '')
            
            education_html += f'''
            <div class="original-education-item">
                <div class="degree">{degree}</div>
                <div class="school">{school}</div>
                <div class="graduation-info">
                    <span class="graduation-date">{graduation_date}</span>
                    {f'<span class="gpa">GPA: {gpa}</span>' if gpa else ''}
                </div>
            </div>
            '''
        
        # Build skills section
        skills_html = ""
        skills = resume_data.get('skills', [])
        for skill_category in skills:
            # Handle different skill_category formats after role adaptation - fix for original format
            if isinstance(skill_category, str):
                # If it's a string, treat as a simple skill item
                skills_html += f'''
                <div class="original-skills-category">
                    <span class="skills-category-name">Skills:</span>
                    <span class="skills-list">{skill_category}</span>
                </div>
                '''
                continue
            
            category = getattr(skill_category, 'category', '') if hasattr(skill_category, 'category') else skill_category.get('category', 'Skills') if isinstance(skill_category, dict) else 'Skills'
            if hasattr(skill_category, 'skills'):
                skill_list = getattr(skill_category, 'skills', [])
            elif isinstance(skill_category, dict):
                skill_list = skill_category.get('skills', [])
            else:
                skill_list = []
            
            if skill_list:
                skills_html += f'''
                <div class="original-skills-category">
                    <span class="skills-category-name">{category}:</span>
                    <span class="skills-list">{', '.join(skill_list)}</span>
                </div>
                '''

        # Build projects section (if available)
        projects_html = ""
        projects = resume_data.get('projects', [])
        for proj in projects:
            if hasattr(proj, '__dict__'):
                title = getattr(proj, 'title', '') or 'Project'
                description = getattr(proj, 'description', '') or ''
                date = getattr(proj, 'date', '') or ''
                link = getattr(proj, 'link', '') or ''
                technologies = getattr(proj, 'technologies', []) or []
            elif isinstance(proj, dict):
                title = proj.get('title') or 'Project'
                description = proj.get('description', '')
                date = proj.get('date', '')
                link = proj.get('link', '')
                technologies = proj.get('technologies', []) or []
            else:
                title, description, date, link, technologies = str(proj), '', '', '', []

            tech_text = f"<div class=\"project-tech\">{', '.join(technologies)}</div>" if technologies else ''
            link_text = f"<span class=\"project-link\"><a href=\"{link}\" target=\"_blank\">Link</a></span>" if link else ''
            date_text = f"<span class=\"project-date\">{date}</span>" if date else ''
            meta = ' '.join([s for s in [date_text, link_text] if s])
            projects_html += f'''
            <div class="original-project-item">
                <div class="project-title">{title}</div>
                {f'<div class="project-meta">{meta}</div>' if meta else ''}
                {f'<div class="project-description">{description}</div>' if description else ''}
                {tech_text}
            </div>
            '''

        # Build certifications section
        certifications_html = ""
        certs = resume_data.get('certifications', [])
        for cert in certs:
            certifications_html += f"<div class=\"original-cert-item\">{cert}</div>"

        # Build languages section
        languages_html = ""
        languages = resume_data.get('languages', [])
        for lang in languages:
            languages_html += f"<div class=\"original-lang-item\">{lang}</div>"

        # Build additional sections (generic)
        additional_sections_html = ""
        additional = resume_data.get('additional_sections', {}) or {}
        # Some parsers may place these at the top-level; include them if so
        for key in ['remote_work', 'timezone', 'visa_sponsorship']:
            if key in resume_data and key not in additional:
                val = resume_data.get(key)
                if isinstance(val, list):
                    additional[key] = val
                elif isinstance(val, str) and val.strip():
                    additional[key] = [val]

        if isinstance(additional, dict):
            for section_name, items in additional.items():
                if not items:
                    continue
                # Normalize items to list[str]
                if isinstance(items, str):
                    items = [items]
                section_items = ''.join(
                    f"<li>{str(it).strip()}</li>" for it in items if str(it).strip()
                )
                if section_items:
                    additional_sections_html += f'''
                    <div class="original-section">
                        <h2 class="original-section-title">{section_name.replace('_',' ')}</h2>
                        <ul class="original-list">
                            {section_items}
                        </ul>
                    </div>
                    '''

        return f'''
        <div class="original-resume-container">
            <div class="original-header">
                <h1 class="original-name">{name}</h1>
                <div class="original-contact">{contact_line}</div>
            </div>
            
            {f'<div class="original-summary">{professional_summary}</div>' if professional_summary else ''}
            
            {f'<div class="original-section"><h2 class="original-section-title">Professional Experience</h2>{experience_html}</div>' if experience_html else ''}
            
            {f'<div class="original-section"><h2 class="original-section-title">Education</h2>{education_html}</div>' if education_html else ''}
            
            {f'<div class="original-section"><h2 class="original-section-title">Skills</h2>{skills_html}</div>' if skills_html else ''}

            {f'<div class="original-section"><h2 class="original-section-title">Projects</h2>{projects_html}</div>' if projects_html else ''}

            {f'<div class="original-section"><h2 class="original-section-title">Certifications</h2>{certifications_html}</div>' if certifications_html else ''}

            {f'<div class="original-section"><h2 class="original-section-title">Languages</h2>{languages_html}</div>' if languages_html else ''}

            {additional_sections_html}
        </div>
        '''
    
    def _generate_sidebar_layout_html(self, resume_data: Dict[str, Any], original_analysis: Dict[str, Any] = None) -> str:
        """Generate sidebar layout HTML for original format."""
        # This would implement sidebar layout similar to modern template but matching original structure
        # For now, fallback to single column
        return self._generate_single_column_layout_html(resume_data, original_analysis)
    
    def _generate_original_layout_css(self, 
                                    resume_data: Dict[str, Any], 
                                    original_analysis: Dict[str, Any] = None,
                                    enhancement_level: str = "minimal",
                                    palette: ColorPalette = None) -> str:
        """Generate CSS that preserves original formatting while applying enhancements."""
        
        # Base CSS that mimics original layout
        base_css = '''
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    line-height: 1.5;
    color: {{text_dark}};
    background-color: {{background_color}};
    padding: 20px;
}

.original-resume-container {
    max-width: 800px;
    margin: 0 auto;
    background: {{background_color}};
    padding: 40px;
}

.original-header {
    text-align: center;
    margin-bottom: 30px;
    border-bottom: 1px solid {{border_color}};
    padding-bottom: 20px;
}

.original-name {
    font-size: 24px;
    font-weight: bold;
    color: {{primary_color}};
    margin-bottom: 8px;
}

.original-contact {
    font-size: 14px;
    color: {{text_light}};
    line-height: 1.4;
}

.original-summary {
    font-size: 16px;
    line-height: 1.6;
    margin-bottom: 25px;
    text-align: justify;
}

.original-section {
    margin-bottom: 25px;
}

.original-section-title {
    font-size: 16px;
    font-weight: bold;
    color: {{primary_color}};
    margin-bottom: 15px;
    text-transform: uppercase;
    border-bottom: 1px solid {{border_color}};
    padding-bottom: 5px;
}

.original-experience-item {
    margin-bottom: 20px;
}

.job-title {
    font-size: 16px;
    font-weight: bold;
    color: {{text_dark}};
}

.job-details {
    font-size: 14px;
    color: {{text_light}};
    margin-bottom: 8px;
}

.company {
    font-weight: bold;
    color: {{secondary_color}};
}

.job-location::before {
    content: " • ";
}

.job-dates::before {
    content: " • ";
}

.job-description {
    list-style-type: disc;
    padding-left: 20px;
    margin-top: 5px;
}

.job-description li {
    font-size: 14px;
    margin-bottom: 3px;
    line-height: 1.5;
}

.original-education-item {
    margin-bottom: 15px;
}

.degree {
    font-size: 16px;
    font-weight: bold;
    color: {{text_dark}};
}

.school {
    font-size: 14px;
    color: {{secondary_color}};
    font-weight: bold;
}

.graduation-info {
    font-size: 14px;
    color: {{text_light}};
}

.gpa::before {
    content: " • ";
}

.original-skills-category {
    margin-bottom: 8px;
    font-size: 14px;
}

.skills-category-name {
    font-weight: bold;
    color: {{primary_color}};
}

.skills-list {
    color: {{text_dark}};
}

/* Projects */
.original-project-item {
    margin-bottom: 15px;
}

.project-title {
    font-size: 16px;
    font-weight: bold;
    color: {{text_dark}};
}

.project-meta {
    font-size: 13px;
    color: {{text_light}};
    margin-bottom: 6px;
}

.project-description {
    font-size: 14px;
    margin-top: 6px;
}

.project-tech {
    font-size: 13px;
    color: {{text_light}};
}

/* Certifications, Languages, and generic lists */
.original-cert-item, .original-lang-item {
    font-size: 14px;
    margin-bottom: 6px;
}

.original-list {
    margin-left: 18px;
    list-style-type: disc;
}

@media print {
    body {
        background: white;
        padding: 0;
    }
    
    .original-resume-container {
        box-shadow: none;
        padding: 0;
    }
}
        '''
        
        # Apply enhancement level modifications
        if enhancement_level == "enhanced":
            base_css += '''
/* Enhanced styling */
.original-header {
    background: linear-gradient(135deg, {{section_bg}}, {{background_color}});
    border-radius: 10px;
    padding: 30px;
    margin-bottom: 40px;
}

.original-experience-item, .original-education-item {
    padding: 15px;
    background: {{section_bg}};
    border-left: 4px solid {{primary_color}};
    border-radius: 5px;
    margin-bottom: 20px;
}

.original-section-title {
    font-size: 18px;
    color: {{primary_color}};
    position: relative;
}

.original-section-title::after {
    content: '';
    position: absolute;
    bottom: -3px;
    left: 0;
    width: 30px;
    height: 3px;
    background: {{secondary_color}};
}
            '''
        elif enhancement_level == "modernized":
            base_css += '''
/* Modernized styling */
.original-resume-container {
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border-radius: 15px;
    overflow: hidden;
}

.original-header {
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 40px;
    margin-bottom: 0;
}

.original-name {
    color: white;
    font-size: 28px;
}

.original-contact {
    color: rgba(255,255,255,0.9);
}

.original-section {
    padding: 0 40px;
}

.original-section:last-child {
    padding-bottom: 40px;
}

.original-experience-item, .original-education-item {
    background: {{section_bg}};
    padding: 20px;
    border-radius: 10px;
    border-left: 5px solid {{primary_color}};
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.job-title, .degree {
    color: {{text_dark}};
    font-size: 18px;
}

.original-section-title {
    font-size: 20px;
    margin-bottom: 20px;
    position: relative;
}

.original-section-title::after {
    content: '';
    position: absolute;
    bottom: -5px;
    left: 0;
    width: 50px;
    height: 4px;
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    border-radius: 2px;
}

/* Smooth transitions */
.original-experience-item, .original-education-item {
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.original-experience-item:hover, .original-education-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}
            '''
        
        # Apply color palette
        if palette:
            # Calculate high contrast color for text on primary/secondary backgrounds
            text_contrast_color = self._get_high_contrast_text_color(palette.primary)
            
            base_css = base_css.replace("{{primary_color}}", palette.primary)
            base_css = base_css.replace("{{secondary_color}}", palette.secondary)
            base_css = base_css.replace("{{text_dark}}", palette.text_dark)
            base_css = base_css.replace("{{text_light}}", palette.text_light)
            base_css = base_css.replace("{{background_color}}", palette.background)
            base_css = base_css.replace("{{section_bg}}", palette.section_bg)
            base_css = base_css.replace("{{border_color}}", palette.border)
            base_css = base_css.replace("{{link_color}}", palette.link)
            base_css = base_css.replace("{{text_contrast_color}}", text_contrast_color)
        
        return base_css
    
    def _get_shine_html_template(self) -> str:
        """Get Shine template HTML (inspired by xriley/Shine-Theme)."""
        return """
<div class="shine-container">
    <div class="shine-header">
        <div class="profile-section">
            <div class="profile-image-placeholder"></div>
            <h1 class="profile-name">{{name}}</h1>
            <p class="profile-title">Professional Developer</p>
        </div>
        <div class="contact-section">
            <div class="contact-item">
                <i class="contact-icon">📧</i>
                <span>{{email}}</span>
            </div>
            <div class="contact-item">
                <i class="contact-icon">📱</i>
                <span>{{phone}}</span>
            </div>
            <div class="contact-item">
                <i class="contact-icon">📍</i>
                <span>{{location}}</span>
            </div>
            <div class="contact-item">
                <i class="contact-icon">🔗</i>
                <span>{{linkedin}}</span>
            </div>
            <div class="contact-item">
                <i class="contact-icon">💻</i>
                <span>{{github}}</span>
            </div>
        </div>
    </div>
    
    <div class="shine-content">
        <section class="shine-section">
            <h2 class="section-heading">About Me</h2>
            <p class="about-text">{{professional_summary}}</p>
        </section>
        
        <section class="shine-section">
            <h2 class="section-heading">Work Experience</h2>
            <div class="experience-list">
                {{experience_section}}
            </div>
        </section>
        
        <section class="shine-section">
            <h2 class="section-heading">Tech Stack</h2>
            <div class="tech-stack">
                {{skills_section}}
            </div>
        </section>
        
        <section class="shine-section">
            <h2 class="section-heading">Education</h2>
            <div class="education-list">
                {{education_section}}
            </div>
        </section>
    </div>
</div>
        """
    
    def _get_timeline_html_template(self) -> str:
        """Get Timeline template HTML (CodePen inspiration)."""
        return """
<div class="timeline-container">
    <div class="timeline-header">
        <div class="header-content">
            <div class="profile-avatar">
                <span class="avatar-placeholder">👤</span>
            </div>
            <h1 class="profile-name">{{name}}</h1>
            <p class="profile-title">{{job_title}}</p>
            <div class="contact-timeline">
                <div class="contact-timeline-item">📧 {{email}}</div>
                <div class="contact-timeline-item">📱 {{phone}}</div>
                <div class="contact-timeline-item">📍 {{location}}</div>
                <div class="contact-timeline-item">🔗 {{linkedin}}</div>
                <div class="contact-timeline-item">💻 {{github}}</div>
            </div>
        </div>
    </div>
    
    <div class="timeline-content">
        <section class="timeline-section">
            <h2 class="timeline-title">Professional Summary</h2>
            <div class="about-timeline">
                <p>{{professional_summary}}</p>
            </div>
        </section>
        
        <section class="timeline-section">
            <h2 class="timeline-title">Professional Journey</h2>
            <div class="timeline-wrapper">
                {{experience_section}}
            </div>
        </section>
        
        <section class="timeline-section">
            <h2 class="timeline-title">Skills & Expertise</h2>
            <div class="skills-showcase">
                <div class="skills-grid">
                    {{skills_section}}
                </div>
            </div>
        </section>
        
        <section class="timeline-section">
            <h2 class="timeline-title">Education</h2>
            <div class="timeline-wrapper education-timeline">
                {{education_section}}
            </div>
        </section>
    </div>
</div>
        """
    
    def _get_card_html_template(self) -> str:
        """Get Card template HTML (CodePen inspiration - Card layout)."""
        return """
<div class="card-container">
    <div class="card-hero">
        <div class="hero-content">
            <div class="profile-circle">
                <span class="profile-icon">👨‍💻</span>
            </div>
            <h1 class="card-name">{{name}}</h1>
            <p class="card-title">{{job_title}}</p>
            <div class="hero-contacts">
                <span class="hero-contact">{{email}}</span>
                <span class="hero-contact">{{phone}}</span>
                <span class="hero-contact">{{location}}</span>
            </div>
        </div>
        <div class="hero-decoration"></div>
    </div>
    
    <div class="cards-grid">
        <div class="info-card summary-card">
            <div class="card-header">
                <h2 class="card-heading">Professional Summary</h2>
                <div class="card-icon">💼</div>
            </div>
            <div class="card-content">
                <p class="summary-text">{{professional_summary}}</p>
            </div>
        </div>
        
        <div class="info-card experience-card">
            <div class="card-header">
                <h2 class="card-heading">Experience</h2>
                <div class="card-icon">🏢</div>
            </div>
            <div class="card-content">
                {{experience_section}}
            </div>
        </div>
        
        <div class="info-card skills-card">
            <div class="card-header">
                <h2 class="card-heading">Skills</h2>
                <div class="card-icon">⚡</div>
            </div>
            <div class="card-content">
                {{skills_section}}
            </div>
        </div>
        
        <div class="info-card education-card">
            <div class="card-header">
                <h2 class="card-heading">Education</h2>
                <div class="card-icon">🎓</div>
            </div>
            <div class="card-content">
                {{education_section}}
            </div>
        </div>
    </div>
    
    <div class="card-footer">
        <div class="social-links">
            <a href="{{linkedin}}" class="social-link linkedin">LinkedIn</a>
            <a href="{{github}}" class="social-link github">GitHub</a>
        </div>
    </div>
</div>
        """
    
    def _get_split_html_template(self) -> str:
        """Get Split template HTML (CodePen inspiration - Split layout)."""
        return """
<div class="split-container">
    <div class="split-sidebar">
        <div class="profile-section">
            <div class="profile-avatar">
                <span class="avatar-text">{{name_initials}}</span>
            </div>
            <h1 class="profile-name">{{name}}</h1>
            <p class="profile-role">{{job_title}}</p>
        </div>
        
        <div class="contact-section">
            <h3 class="sidebar-title">Contact</h3>
            <div class="contact-list">
                <div class="contact-item">
                    <span class="contact-icon">📧</span>
                    <span class="contact-text">{{email}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">📱</span>
                    <span class="contact-text">{{phone}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">📍</span>
                    <span class="contact-text">{{location}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">🔗</span>
                    <span class="contact-text">{{linkedin}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-icon">💻</span>
                    <span class="contact-text">{{github}}</span>
                </div>
            </div>
        </div>
        
        <div class="skills-sidebar">
            <h3 class="sidebar-title">Skills</h3>
            <div class="sidebar-skills">
                {{skills_section}}
            </div>
        </div>
    </div>
    
    <div class="split-main">
        <section class="main-section summary-section">
            <h2 class="section-title">Professional Summary</h2>
            <p class="summary-content">{{professional_summary}}</p>
        </section>
        
        <section class="main-section experience-section">
            <h2 class="section-title">Professional Experience</h2>
            <div class="experience-timeline">
                {{experience_section}}
            </div>
        </section>
        
        <section class="main-section education-section">
            <h2 class="section-title">Education</h2>
            <div class="education-list">
                {{education_section}}
            </div>
        </section>
    </div>
</div>
        """
    
    def _get_gradient_html_template(self) -> str:
        """Get Gradient template HTML (CodePen inspiration - Gradient design)."""
        return """
<div class="gradient-container">
    <div class="gradient-header">
        <div class="header-overlay">
            <div class="profile-section">
                <div class="profile-image-wrapper">
                    <div class="profile-gradient-circle">
                        <span class="profile-initial">{{name_initials}}</span>
                    </div>
                </div>
                <div class="profile-info">
                    <h1 class="gradient-name">{{name}}</h1>
                    <p class="gradient-title">{{job_title}}</p>
                    <div class="contact-gradient">
                        <span class="gradient-contact">{{email}}</span>
                        <span class="gradient-contact">{{phone}}</span>
                        <span class="gradient-contact">{{location}}</span>
                    </div>
                </div>
            </div>
        </div>
        <div class="gradient-shapes">
            <div class="shape shape-1"></div>
            <div class="shape shape-2"></div>
            <div class="shape shape-3"></div>
        </div>
    </div>
    
    <div class="gradient-content">
        <div class="content-grid">
            <div class="content-main">
                <section class="gradient-section">
                    <div class="section-header">
                        <h2 class="gradient-section-title">About Me</h2>
                        <div class="title-line"></div>
                    </div>
                    <p class="gradient-summary">{{professional_summary}}</p>
                </section>
                
                <section class="gradient-section">
                    <div class="section-header">
                        <h2 class="gradient-section-title">Experience</h2>
                        <div class="title-line"></div>
                    </div>
                    <div class="gradient-experience">
                        {{experience_section}}
                    </div>
                </section>
                
                <section class="gradient-section">
                    <div class="section-header">
                        <h2 class="gradient-section-title">Education</h2>
                        <div class="title-line"></div>
                    </div>
                    <div class="gradient-education">
                        {{education_section}}
                    </div>
                </section>
            </div>
            
            <div class="content-sidebar">
                <div class="gradient-card skills-card">
                    <h3 class="card-title">Skills & Technologies</h3>
                    <div class="gradient-skills">
                        {{skills_section}}
                    </div>
                </div>
                
                <div class="gradient-card links-card">
                    <h3 class="card-title">Connect</h3>
                    <div class="gradient-links">
                        <a href="{{linkedin}}" class="gradient-link linkedin">LinkedIn</a>
                        <a href="{{github}}" class="gradient-link github">GitHub</a>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
        """
    
    def _get_shine_css_template(self) -> str:
        """Get Shine template CSS."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;500;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Roboto', sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background-color: #f8f9fa;
}

.shine-container {
    max-width: 900px;
    margin: 2rem auto;
    background: {{background_color}};
    box-shadow: 0 0 30px rgba(0,0,0,0.1);
    border-radius: 10px;
    overflow: hidden;
}

.shine-header {
    background: linear-gradient(135deg, {{primary_color}}, {{secondary_color}});
    color: white;
    padding: 3rem 2rem;
    text-align: center;
    position: relative;
}

.shine-header::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="shine-pattern" x="0" y="0" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23shine-pattern)"/></svg>');
    opacity: 0.3;
}

.profile-section {
    position: relative;
    z-index: 2;
    margin-bottom: 2rem;
}

.profile-image-placeholder {
    width: 120px;
    height: 120px;
    background: rgba(255,255,255,0.2);
    border-radius: 50%;
    margin: 0 auto 1.5rem;
    border: 4px solid rgba(255,255,255,0.3);
    position: relative;
}

.profile-image-placeholder::before {
    content: '👤';
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    font-size: 3rem;
    opacity: 0.7;
}

.profile-name {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.profile-title {
    font-size: 1.2rem;
    font-weight: 300;
    opacity: 0.9;
}

.contact-section {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1rem;
    position: relative;
    z-index: 2;
}

.contact-item {
    display: flex;
    align-items: center;
    background: rgba(255,255,255,0.1);
    padding: 0.8rem;
    border-radius: 8px;
    backdrop-filter: blur(10px);
    transition: all 0.3s ease;
}

.contact-item:hover {
    background: rgba(255,255,255,0.2);
    transform: translateY(-2px);
}

.contact-icon {
    margin-right: 0.8rem;
    font-size: 1.2rem;
    width: 24px;
}

.shine-content {
    padding: 3rem 2rem;
}

.shine-section {
    margin-bottom: 3rem;
}

.section-heading {
    font-size: 1.8rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 1.5rem;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid {{primary_color}};
    position: relative;
}

.section-heading::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 50px;
    height: 2px;
    background: {{secondary_color}};
}

.about-text {
    font-size: 1.1rem;
    line-height: 1.8;
    text-align: justify;
    color: {{text_dark}};
}

.experience-list .experience-item,
.education-list .education-item {
    background: {{section_bg}};
    padding: 2rem;
    margin-bottom: 1.5rem;
    border-radius: 10px;
    border-left: 4px solid {{primary_color}};
    transition: all 0.3s ease;
}

.experience-item:hover,
.education-item:hover {
    box-shadow: 0 5px 20px rgba(0,0,0,0.1);
    transform: translateY(-2px);
}

.experience-header h3,
.education-item h3 {
    font-size: 1.3rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
}

.experience-meta,
.education-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
    margin-bottom: 1rem;
    font-size: 0.95rem;
    color: {{text_light}};
}

.company, .school {
    font-weight: 600;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.5rem;
    line-height: 1.6;
}

.experience-description li::before {
    content: '▶';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-size: 0.8rem;
}

.tech-stack .skills-category {
    background: {{section_bg}};
    padding: 1.5rem;
    margin-bottom: 1rem;
    border-radius: 10px;
    border-left: 4px solid {{secondary_color}};
}

.tech-stack .skills-category h4 {
    font-size: 1.1rem;
    font-weight: 600;
    color: {{text_dark}};
    margin-bottom: 0.8rem;
}

.tech-stack .skills-list {
    font-size: 1rem;
    line-height: 1.6;
    color: {{text_dark}};
}

@media (max-width: 768px) {
    .shine-container {
        margin: 1rem;
        border-radius: 8px;
    }
    
    .shine-header {
        padding: 2rem 1.5rem;
    }
    
    .profile-name {
        font-size: 2rem;
    }
    
    .contact-section {
        grid-template-columns: 1fr;
    }
    
    .shine-content {
        padding: 2rem 1.5rem;
    }
    
    .section-heading {
        font-size: 1.5rem;
    }
}
        """
    
    def _get_balanced_html_template(self) -> str:
        """Get balanced template HTML with optimized space utilization."""
        return """
<div class="balanced-container">
    <header class="balanced-header">
        <div class="header-content">
            <h1 class="name">{{name}}</h1>
            <div class="contact-row">
                <div class="contact-item">✉️ {{email}}</div>
                <div class="contact-item">📱 {{phone}}</div>
                <div class="contact-item">📍 {{location}}</div>
                <div class="contact-item">🔗 {{linkedin}}</div>
            </div>
        </div>
        {{profile_image}}
    </header>
    
    <div class="balanced-layout">
        <div class="primary-column">
            <section class="summary-section">
                <h2 class="section-title">Professional Summary</h2>
                <div class="summary-content">{{professional_summary}}</div>
            </section>
            
            <section class="experience-section">
                <h2 class="section-title">Experience</h2>
                <div class="experience-content">{{experience_section}}</div>
            </section>
            
            <section class="education-section">
                <h2 class="section-title">Education</h2>
                <div class="education-content">{{education_section}}</div>
            </section>
        </div>
        
        <div class="secondary-column">
            <section class="skills-section">
                <h2 class="section-title">Skills</h2>
                <div class="skills-content">{{skills_section}}</div>
            </section>
            
            <section class="additional-section">
                <h2 class="section-title">Additional</h2>
                <div class="additional-content">{{additional_sections}}</div>
            </section>
        </div>
    </div>
</div>
        """
    
    def _get_balanced_css_template(self) -> str:
        """Get balanced template CSS with intelligent space optimization."""
        return """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: {{text_dark}};
    background: {{background_color}};
    font-size: 15px;
}

.balanced-container {
    max-width: 1000px;
    margin: 2rem auto;
    background: {{background_color}};
    box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    border-radius: 12px;
    overflow: hidden;
}

.balanced-header {
    background: linear-gradient(135deg, {{primary_color}} 0%, {{secondary_color}} 100%);
    color: white;
    padding: 2.5rem 3rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 2rem;
}

.header-content {
    flex: 1;
    min-width: 300px;
}

.name {
    font-size: 2.5rem;
    font-weight: 700;
    margin-bottom: 1rem;
    letter-spacing: -0.5px;
}

.contact-row {
    display: flex;
    flex-wrap: wrap;
    gap: 1.5rem;
    font-size: 0.95rem;
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(255,255,255,0.15);
    padding: 0.5rem 1rem;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.balanced-layout {
    display: grid;
    grid-template-columns: 1.8fr 1fr;
    gap: 0;
    min-height: 70vh;
}

.primary-column {
    padding: 3rem;
    background: {{background_color}};
}

.secondary-column {
    padding: 3rem 2.5rem;
    background: {{section_bg}};
    border-left: 1px solid {{border_color}};
}

.section-title {
    font-size: 1.4rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 1.5rem;
    text-transform: uppercase;
    letter-spacing: 1px;
    position: relative;
    padding-bottom: 0.5rem;
}

.section-title::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 50px;
    height: 3px;
    background: {{primary_color}};
    border-radius: 2px;
}

.summary-section, .experience-section, .education-section {
    margin-bottom: 2.5rem;
}

.skills-section, .additional-section {
    margin-bottom: 2rem;
}

.summary-content {
    font-size: 1.05rem;
    line-height: 1.7;
    text-align: justify;
    color: {{text_dark}};
    background: {{section_bg}};
    padding: 2rem;
    border-radius: 8px;
    border-left: 4px solid {{primary_color}};
}

.experience-item, .education-item {
    margin-bottom: 2rem;
    padding: 1.5rem;
    background: {{section_bg}};
    border-radius: 8px;
    border-left: 4px solid {{secondary_color}};
    transition: all 0.3s ease;
}

.experience-item:hover, .education-item:hover {
    transform: translateX(5px);
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.experience-header h3, .education-item h3 {
    font-size: 1.2rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.5rem;
}

.experience-meta, .education-meta {
    font-size: 0.9rem;
    color: {{text_light}};
    margin-bottom: 1rem;
    display: flex;
    flex-wrap: wrap;
    gap: 1rem;
}

.company, .school {
    font-weight: 500;
    color: {{secondary_color}};
}

.experience-description {
    list-style: none;
    padding: 0;
}

.experience-description li {
    position: relative;
    padding-left: 1.5rem;
    margin-bottom: 0.6rem;
    line-height: 1.6;
    color: {{text_dark}};
}

.experience-description li:before {
    content: '→';
    position: absolute;
    left: 0;
    color: {{primary_color}};
    font-weight: bold;
}

.skills-category {
    margin-bottom: 1.5rem;
    padding: 1.5rem;
    background: {{background_color}};
    border-radius: 8px;
    border: 1px solid {{border_color}};
}

.skills-category h4 {
    font-size: 1rem;
    font-weight: 600;
    color: {{primary_color}};
    margin-bottom: 0.8rem;
}

.skills-list {
    font-size: 0.9rem;
    line-height: 1.6;
    color: {{text_dark}};
}

/* Responsive design */
@media (max-width: 768px) {
    .balanced-layout {
        grid-template-columns: 1fr;
    }
    
    .secondary-column {
        border-left: none;
        border-top: 1px solid {{border_color}};
    }
    
    .balanced-header {
        padding: 2rem;
        flex-direction: column;
        text-align: center;
    }
    
    .contact-row {
        justify-content: center;
    }
    
    .primary-column, .secondary-column {
        padding: 2rem;
    }
    
    .name {
        font-size: 2rem;
    }
}

@media print {
    body {
        background: white !important;
    }
    
    .balanced-container {
        box-shadow: none;
        margin: 0;
        max-width: none;
    }
    
    .balanced-layout {
        grid-template-columns: 1.8fr 1fr;
    }
    
    .section-title {
        font-size: 1.2rem;
    }
}
        """
