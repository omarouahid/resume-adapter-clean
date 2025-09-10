#!/usr/bin/env python3
"""
Cover Letter Service - Generate professional cover letters with company research integration.
"""

import logging
import requests
import time
import re
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import urljoin, urlparse
import json
try:
    from enhanced_web_research import EnhancedWebResearch
    ENHANCED_RESEARCH_AVAILABLE = True
except ImportError:
    from web_research import CompanyResearchService
    ENHANCED_RESEARCH_AVAILABLE = False

logger = logging.getLogger(__name__)

class CoverLetterService:
    """Service for generating personalized cover letters with company research."""
    
    def __init__(self):
        """Initialize the cover letter service."""
        self.client = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
        if ENHANCED_RESEARCH_AVAILABLE:
            self.research_service = EnhancedWebResearch()
            logger.info("Cover Letter Service initialized with Enhanced Web Research")
        else:
            self.research_service = CompanyResearchService()
            logger.info("Cover Letter Service initialized with Basic Web Research")
    
    def set_client(self, openrouter_client):
        """Set the OpenRouter client for AI-powered features."""
        self.client = openrouter_client
        self.research_service.set_client(openrouter_client)
        logger.info("OpenRouter client set for cover letter service")
    
    def model_supports_browsing(self, model_name: str) -> bool:
        """Check if the model supports web browsing capabilities."""
        # For now, assume most models can handle web research tasks
        browsing_models = [
            "anthropic/claude-3-sonnet",
            "anthropic/claude-3-haiku", 
            "openai/gpt-4",
            "openai/gpt-4-turbo",
            "openai/gpt-3.5-turbo"
        ]
        
        # Check if model name contains any browsing-capable model
        for browsing_model in browsing_models:
            if browsing_model in model_name.lower():
                return True
        
        # Default to True for most modern models
        return True
    
    def generate_cover_letter(self, resume_dict: Dict[str, Any], job_description: str, 
                            company_name: str, research_data: Optional[List[Tuple[str, str]]] = None,
                            word_target: int = 400, char_limit: Optional[int] = None,
                            ddg_only: bool = True, attach_pages: int = 3,
                            return_research_data: bool = False) -> Tuple[str, Optional[List]]:
        """
        Generate a personalized cover letter based on resume and job description.
        
        Args:
            resume_dict: Parsed resume data
            job_description: Target job description
            company_name: Company name
            research_data: Optional company research data
            word_target: Target word count for the cover letter (default: 400)
            char_limit: Optional character limit
            ddg_only: Whether to use DuckDuckGo only for research (default: True)
            attach_pages: Number of pages to attach for research (default: 3)
            return_research_data: Whether to return research data (default: False)
            
        Returns:
            Tuple of (cover_letter_text, research_data)
        """
        
        if not self.client:
            logger.error("OpenRouter client not set")
            return "Error: AI client not configured", None
        
        try:
            logger.info(f"Generating cover letter for {company_name}")
            
            # Format resume data for the prompt
            formatted_resume = self._format_resume_for_letter(resume_dict)
            
            # Perform company research if not provided and ddg_only is True
            if not research_data and ddg_only:
                logger.info(f"Performing company research for {company_name}")
                research_data = self.research_service.research_company(company_name, max_sources=attach_pages)
            
            # Include research data if available
            research_context = ""
            if research_data:
                research_context = self._format_research_for_prompt(research_data)
            
            # Create the cover letter generation prompt
            prompt = f"""
Create a professional, personalized cover letter based on the following information:

RESUME DATA:
{formatted_resume}

JOB DESCRIPTION:
{job_description}

COMPANY: {company_name}

{research_context}

REQUIREMENTS:
1. Use the ACTUAL contact information from the resume data (name, email, phone, etc.) - DO NOT use ANY placeholders
2. DO NOT include placeholders like [Date], [Company Address], [Your Name], [Email Address], etc.
3. Generate a current date (use today's date in a professional format)
4. For company address, either use a general format like "Dear Hiring Manager" without address, or create a realistic business address format
5. Create a compelling cover letter that matches the candidate's experience to the job requirements
6. Use specific examples from the resume that align with the job description
7. Show knowledge of the company (if research data provided)
8. Maintain a professional yet engaging tone
9. Keep it to 3-4 paragraphs maximum
10. Include a strong opening and closing
11. Avoid generic phrases and make it personal to this specific opportunity
12. Format as a proper business letter with complete, real information
13. Target approximately {word_target} words

CRITICAL: The cover letter must be 100% complete with NO placeholders, brackets, or incomplete sections. Everything must be filled in with actual content.

Return ONLY the complete cover letter text with proper formatting, no additional explanations.
            """
            
            # Generate the cover letter
            cover_letter = self.client._make_request(prompt, max_tokens=1500, prompt_type="cover_letter_generation")
            
            # Post-process to remove any remaining placeholders
            cover_letter = self._remove_placeholders(cover_letter, resume_dict, company_name)
            
            logger.info("Cover letter generated successfully")
            
            if return_research_data:
                return cover_letter, research_data
            else:
                return cover_letter, None
            
        except Exception as e:
            logger.error(f"Cover letter generation failed: {e}")
            return f"Error generating cover letter: {str(e)}", None
    
    def format_company_research(self, company_name: str, research_data: List[Tuple[str, str]]) -> str:
        """
        Format company research data into a readable summary.
        
        Args:
            company_name: Name of the company
            research_data: List of (source, content) tuples
            
        Returns:
            Formatted research summary
        """
        
        if not self.client:
            logger.warning("No AI client available, returning raw research")
            return self._format_raw_research(company_name, research_data)
        
        try:
            logger.info(f"Formatting research data for {company_name}")
            
            # Combine research data
            combined_research = ""
            for source, content in research_data:
                combined_research += f"\n--- Source: {source} ---\n{content}\n"
            
            prompt = f"""
Format this company research data into a concise, useful summary for cover letter writing:

COMPANY: {company_name}

RESEARCH DATA:
{combined_research}

REQUIREMENTS:
1. Create a structured summary with key company information
2. Include: company mission/values, recent news, key products/services, company culture
3. Highlight information that would be useful for personalizing a cover letter
4. Keep it concise but informative
5. Use bullet points for easy reading
6. Remove any duplicate information

Return a well-formatted research summary.
            """
            
            formatted_summary = self.client._make_request(prompt, max_tokens=1000, prompt_type="research_formatting")
            
            logger.info("Research data formatted successfully")
            return formatted_summary
            
        except Exception as e:
            logger.error(f"Research formatting failed: {e}")
            return self._format_raw_research(company_name, research_data)
    
    def _format_resume_for_letter(self, resume_dict: Dict[str, Any]) -> str:
        """Format resume data for cover letter generation."""
        
        formatted_parts = []
        
        # Contact info
        if 'contact_info' in resume_dict:
            contact = resume_dict['contact_info']
            contact_details = []
            
            if contact.get('name'):
                contact_details.append(f"Name: {contact['name']}")
            if contact.get('email'):
                contact_details.append(f"Email: {contact['email']}")
            if contact.get('phone'):
                contact_details.append(f"Phone: {contact['phone']}")
            if contact.get('address'):
                contact_details.append(f"Address: {contact['address']}")
            if contact.get('city') or contact.get('state'):
                location = f"{contact.get('city', '')}, {contact.get('state', '')}".strip(', ')
                if location:
                    contact_details.append(f"Location: {location}")
            
            if contact_details:
                formatted_parts.append("CONTACT INFORMATION:")
                formatted_parts.extend([f"- {detail}" for detail in contact_details])
        
        # Professional summary
        if 'professional_summary' in resume_dict:
            summary = resume_dict['professional_summary']
            if summary:
                formatted_parts.append(f"PROFESSIONAL SUMMARY:\n{summary}")
        
        # Work experience
        if 'job_experiences' in resume_dict:
            experiences = resume_dict['job_experiences']
            if experiences:
                formatted_parts.append("KEY WORK EXPERIENCE:")
                for exp in experiences[:3]:  # Top 3 experiences
                    title = exp.get('job_title', 'N/A')
                    company = exp.get('company', 'N/A')
                    duration = f"{exp.get('start_date', 'N/A')} - {exp.get('end_date', 'Present')}"
                    formatted_parts.append(f"- {title} at {company} ({duration})")
        
        # Skills
        if 'skills' in resume_dict:
            skills = resume_dict['skills']
            if skills:
                if isinstance(skills, list):
                    # Handle list of strings or list of dictionaries
                    skill_strings = []
                    for skill in skills[:10]:  # Top 10 skills
                        if isinstance(skill, dict):
                            # Extract skill name from dict (common keys: name, skill, title)
                            skill_name = skill.get('name') or skill.get('skill') or skill.get('title') or str(skill)
                            skill_strings.append(str(skill_name))
                        else:
                            skill_strings.append(str(skill))
                    skills_str = ', '.join(skill_strings)
                else:
                    skills_str = str(skills)
                formatted_parts.append(f"KEY SKILLS: {skills_str}")
        
        return '\n\n'.join(formatted_parts)
    
    def _format_research_for_prompt(self, research_data: List[Tuple[str, str]]) -> str:
        """Format research data for inclusion in prompts."""
        
        if not research_data:
            return ""
        
        research_parts = ["COMPANY RESEARCH:"]
        
        for source, content in research_data[:3]:  # Limit to first 3 sources
            # Truncate long content
            truncated_content = content[:500] + "..." if len(content) > 500 else content
            research_parts.append(f"Source: {source}")
            research_parts.append(f"Content: {truncated_content}")
            research_parts.append("")
        
        return '\n'.join(research_parts)
    
    def _format_raw_research(self, company_name: str, research_data: List[Tuple[str, str]]) -> str:
        """Format research data without AI assistance."""
        
        formatted_parts = [f"## Company Research: {company_name}\n"]
        
        for i, (source, content) in enumerate(research_data, 1):
            formatted_parts.append(f"### Source {i}: {source}")
            formatted_parts.append(content)
            formatted_parts.append("")
        
        return '\n'.join(formatted_parts)
    
    def _remove_placeholders(self, cover_letter: str, resume_dict: Dict[str, Any], company_name: str) -> str:
        """Remove any remaining placeholders from the cover letter."""
        import re
        from datetime import datetime
        
        # Get actual contact info
        contact_info = resume_dict.get('contact_info', {})
        name = contact_info.get('name', 'N/A')
        email = contact_info.get('email', 'N/A')
        phone = contact_info.get('phone', 'N/A')
        
        # Current date
        current_date = datetime.now().strftime("%B %d, %Y")
        
        # Replace common placeholders
        replacements = {
            r'\[Date\]': current_date,
            r'\[Your Name\]': name,
            r'\[Email Address\]': email,
            r'\[Phone Number\]': phone,
            r'\[Company Name\]': company_name,
            r'\[Company Address\]': f"{company_name}\nCorporate Headquarters",
            r'\[Hiring Manager Name\]': "Hiring Manager",
            r'\[Address\]': "",
            r'\[City\]': contact_info.get('city', ''),
            r'\[State\]': contact_info.get('state', ''),
            r'\[ZIP\]': contact_info.get('zip', ''),
        }
        
        # Apply replacements
        for pattern, replacement in replacements.items():
            cover_letter = re.sub(pattern, replacement, cover_letter, flags=re.IGNORECASE)
        
        # Remove any remaining brackets with content (catch-all)
        cover_letter = re.sub(r'\[[^\]]*\]', '', cover_letter)
        
        # Clean up any double spaces or empty lines
        cover_letter = re.sub(r'\n\s*\n', '\n\n', cover_letter)
        cover_letter = re.sub(r' +', ' ', cover_letter)
        
        return cover_letter.strip()