#!/usr/bin/env python3
"""
Advanced Resume Parser - Extracts structured information from resumes
"""

import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class ContactInfo:
    """Contact information extracted from resume."""
    name: str = ""
    email: str = ""
    phone: str = ""
    location: str = ""
    linkedin: str = ""
    github: str = ""
    website: str = ""
    address: str = ""

@dataclass
class JobExperience:
    """A single job experience entry."""
    job_title: str = ""
    company: str = ""
    start_date: str = ""
    end_date: str = ""
    location: str = ""
    description: List[str] = None
    is_current: bool = False
    
    def __post_init__(self):
        if self.description is None:
            self.description = []

@dataclass
class Education:
    """Education entry."""
    degree: str = ""
    school: str = ""
    graduation_date: str = ""
    location: str = ""
    gpa: str = ""
    honors: str = ""
    relevant_courses: List[str] = None
    
    def __post_init__(self):
        if self.relevant_courses is None:
            self.relevant_courses = []

@dataclass
class Project:
    """Project entry."""
    title: str = ""
    description: str = ""
    technologies: List[str] = None
    link: str = ""
    date: str = ""
    
    def __post_init__(self):
        if self.technologies is None:
            self.technologies = []

@dataclass
class SkillCategory:
    """Skills organized by category."""
    category: str = ""
    skills: List[str] = None
    
    def __post_init__(self):
        if self.skills is None:
            self.skills = []

@dataclass
class ParsedResume:
    """Complete parsed resume structure."""
    contact_info: ContactInfo = None
    professional_summary: str = ""
    job_experiences: List[JobExperience] = None
    education: List[Education] = None
    projects: List[Project] = None
    skills: List[SkillCategory] = None
    certifications: List[str] = None
    languages: List[str] = None
    additional_sections: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.contact_info is None:
            self.contact_info = ContactInfo()
        if self.job_experiences is None:
            self.job_experiences = []
        if self.education is None:
            self.education = []
        if self.projects is None:
            self.projects = []
        if self.skills is None:
            self.skills = []
        if self.certifications is None:
            self.certifications = []
        if self.languages is None:
            self.languages = []
        if self.additional_sections is None:
            self.additional_sections = {}

class AdvancedResumeParser:
    """Advanced parser that extracts structured resume information."""
    
    def __init__(self, openrouter_client=None):
        self.openrouter_client = openrouter_client
        # Common patterns for parsing
        self.date_patterns = [
            r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',  # MM/DD/YYYY
            r'\b(\d{4})-(\d{1,2})-(\d{1,2})\b',  # YYYY-MM-DD
            r'\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+(\d{4})\b',  # Month YYYY
            r'\b(\d{1,2})/(\d{4})\b',  # MM/YYYY
            r'\b(\d{4})\b'  # YYYY only
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        self.phone_patterns = [
            r'\b(\+\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b',
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b'
        ]
        
        # Job title keywords
        self.job_title_keywords = [
            'engineer', 'developer', 'manager', 'analyst', 'specialist', 'consultant',
            'director', 'coordinator', 'assistant', 'associate', 'senior', 'junior',
            'lead', 'principal', 'architect', 'designer', 'scientist', 'researcher'
        ]
        
        # Company indicators
        self.company_indicators = [
            'inc', 'corp', 'llc', 'ltd', 'company', 'co', 'corporation', 'group',
            'solutions', 'technologies', 'systems', 'services', 'consulting'
        ]
        
        # Education keywords
        self.degree_keywords = [
            'bachelor', 'master', 'phd', 'doctorate', 'associate', 'bs', 'ba', 'ms', 
            'ma', 'mba', 'bsc', 'msc', 'beng', 'meng', 'degree', 'diploma', 'certificate'
        ]
        
        # Common section headers
        self.section_mappings = {
            'experience': ['experience', 'work experience', 'professional experience', 'employment', 'career', 'work history'],
            'education': ['education', 'academic background', 'qualifications', 'degrees'],
            'projects': ['projects', 'key projects', 'notable projects', 'personal projects', 'portfolio'],
            'skills': ['skills', 'technical skills', 'core competencies', 'technologies', 'expertise'],
            'summary': ['summary', 'professional summary', 'profile', 'objective', 'about'],
            'certifications': ['certifications', 'licenses', 'credentials'],
            'languages': ['languages', 'language skills']
        }
    
    def parse_resume(self, analysis_data: Dict) -> ParsedResume:
        """Parse resume data into structured format using AI assistance."""
        
        # If we have AI client, use AI-powered parsing
        if self.openrouter_client:
            return self._ai_parse_resume(analysis_data)
        else:
            # Fallback to rule-based parsing
            return self._rule_based_parse_resume(analysis_data)
    
    def _ai_parse_resume(self, analysis_data: Dict) -> ParsedResume:
        """Use AI to parse resume content more accurately."""
        
        # Extract all text content from the resume
        all_text_blocks = []
        sections = analysis_data.get('sections', [])
        
        for section in sections:
            section_info = {
                'section_type': section.get('section_type', 'other'),
                'section_title': section.get('title', 'Unknown'),
                'content': []
            }
            
            for block in section.get('content', []):
                text = block.get('text', '').strip()
                if text:
                    section_info['content'].append({
                        'text': text,
                        'font_size': block.get('font_size', 12),
                        'is_bold': block.get('is_bold', False),
                        'is_italic': block.get('is_italic', False)
                    })
            
            if section_info['content']:
                all_text_blocks.append(section_info)
        
        # Create comprehensive AI prompt for parsing
        prompt = self._create_parsing_prompt(all_text_blocks)
        
        try:
            ai_response = self.openrouter_client._make_request(prompt, max_tokens=2000)
            
            if ai_response and not ai_response.startswith("Error:"):
                # Parse AI response into structured format
                return self._parse_ai_response(ai_response)
            else:
                logger.warning(f"AI parsing failed: {ai_response}")
                return self._rule_based_parse_resume(analysis_data)
                
        except Exception as e:
            logger.error(f"AI parsing error: {e}")
            return self._rule_based_parse_resume(analysis_data)
    
    def _create_parsing_prompt(self, text_blocks: List[Dict]) -> str:
        """Create a comprehensive prompt for AI parsing."""
        
        resume_text = ""
        for section in text_blocks:
            resume_text += f"\n[{section['section_title']}]\n"
            for content in section['content']:
                emphasis = ""
                if content['is_bold']:
                    emphasis += " (BOLD)"
                if content['font_size'] > 12:
                    emphasis += " (LARGE)"
                resume_text += f"{content['text']}{emphasis}\n"
        
        # Detect language from the content
        detected_language = self._detect_resume_language(resume_text)
        
        prompt = f"""
Parse this resume content into a structured JSON format. The resume appears to be in {detected_language}. 

IMPORTANT: Preserve the original language of ALL content. Do not translate anything. Extract information exactly as written in the original language.

Resume Content:
{resume_text}

Please return a JSON object with the following structure (return ONLY the JSON, no other text):

{{
    "contact_info": {{
        "name": "Full Name",
        "email": "email@domain.com", 
        "phone": "phone number",
        "location": "City, State",
        "linkedin": "LinkedIn URL",
        "github": "GitHub URL"
    }},
    "professional_summary": "Professional summary text",
    "job_experiences": [
        {{
            "job_title": "Job Title",
            "company": "Company Name",
            "start_date": "Start Date",
            "end_date": "End Date or Present",
            "location": "City, State",
            "is_current": true/false,
            "description": ["bullet point 1", "bullet point 2"]
        }}
    ],
    "education": [
        {{
            "degree": "Degree Name",
            "school": "School Name", 
            "graduation_date": "Graduation Date",
            "gpa": "GPA if mentioned",
            "honors": "Honors if mentioned"
        }}
    ],
    "projects": [
        {{
            "title": "Project Name",
            "description": "Project description",
            "technologies": ["tech1", "tech2"],
            "date": "Date if mentioned"
        }}
    ],
    "skills": [
        {{
            "category": "Category Name",
            "skills": ["skill1", "skill2", "skill3"]
        }}
    ],
    "certifications": ["certification1", "certification2"],
    "additional_sections": {{
        "Awards and Achievements": ["award1", "award2"],
        "Volunteer Experience": ["volunteer activity 1"],
        "Publications": ["publication 1"],
        "Languages": ["English", "Spanish"],
        "Interests": ["interest1", "interest2"]
    }}
}}

CRITICAL PARSING INSTRUCTIONS:
1. ANALYZE ALL TEXT PROVIDED - content can be in any order throughout the document
2. Preserve original language - do NOT translate any content  
3. COMPREHENSIVE SECTION SEARCH - Look for these sections EVERYWHERE in the document:
   - Work Experience/Employment/Career History/Professional Experience
   - Projects/Personal Projects/Technical Projects/Portfolio Projects
   - Skills/Technical Skills/Core Competencies/Expertise
   - Education/Academic Background/Qualifications
   - Certifications/Licenses/Professional Certifications
   - Awards/Achievements/Honors/Recognition
   - Volunteer Work/Community Service/Extracurricular Activities
4. PROJECTS ARE CRITICAL - Search aggressively for:
   - Personal projects, side projects, academic projects
   - GitHub repositories, portfolio items, coding projects
   - Freelance work, client projects, consulting work
   - Technical implementations, software development
   - Any project-related content regardless of section name
5. For job experiences, carefully identify separate jobs/positions regardless of location
6. Group related skills into logical categories (Technical, Soft Skills, Languages, Tools)
7. Extract dates accurately in their original format
8. For descriptions, extract individual bullet points or responsibilities
9. If a field is not found, use empty string "" or empty array []
10. Distinguish between different jobs at the same company
11. Use context clues to identify sections regardless of position
12. Search the ENTIRE document thoroughly - projects might be in experience section
13. Look for URLs, links, GitHub profiles, portfolio websites
14. Extract ALL quantifiable achievements (numbers, percentages, metrics)
15. Don't miss sections due to unconventional naming or placement
16. For additional_sections, use MEANINGFUL and DESCRIPTIVE section names based on the actual content:
   - Use "Awards and Achievements" not "Awards" or generic names
   - Use "Volunteer Experience" not "Volunteer" 
   - Use "Publications and Research" not "Publications"
   - Use "Languages" not "Language Skills"
   - Use "Professional Interests" or "Hobbies and Interests" not "Interests"
   - Use "Professional Associations" not "Memberships"
   - Use "Patents and Intellectual Property" not "Patents"
   - NEVER use generic names like "Section Name", "Additional Info", "Other", or "Miscellaneous"
   - Always infer the most appropriate descriptive name from the content
"""
        
        return prompt
    
    def _detect_resume_language(self, text: str) -> str:
        """Detect the primary language of the resume content."""
        # Simple language detection based on common keywords and patterns
        text_lower = text.lower()
        
        # Language indicators
        language_indicators = {
            'spanish': ['experiencia', 'educación', 'habilidades', 'trabajo', 'empresa', 'universidad', 'colegio', 'certificación'],
            'french': ['expérience', 'éducation', 'compétences', 'travail', 'entreprise', 'université', 'certification'],
            'german': ['erfahrung', 'bildung', 'fähigkeiten', 'arbeit', 'unternehmen', 'universität', 'zertifizierung'],
            'italian': ['esperienza', 'educazione', 'competenze', 'lavoro', 'azienda', 'università', 'certificazione'],
            'portuguese': ['experiência', 'educação', 'habilidades', 'trabalho', 'empresa', 'universidade', 'certificação'],
            'dutch': ['ervaring', 'onderwijs', 'vaardigheden', 'werk', 'bedrijf', 'universiteit', 'certificering'],
            'chinese': ['经验', '教育', '技能', '工作', '公司', '大学', '证书', '學歷', '經驗'],
            'japanese': ['経験', '教育', 'スキル', '仕事', '会社', '大学', '資格'],
            'korean': ['경험', '교육', '기술', '일', '회사', '대학', '자격증'],
            'arabic': ['خبرة', 'تعليم', 'مهارات', 'عمل', 'شركة', 'جامعة', 'شهادة'],
            'russian': ['опыт', 'образование', 'навыки', 'работа', 'компания', 'университет', 'сертификат'],
        }
        
        # Count matches for each language
        language_scores = {}
        for lang, keywords in language_indicators.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            if score > 0:
                language_scores[lang] = score
        
        # Return the language with highest score, default to English
        if language_scores:
            detected_lang = max(language_scores, key=language_scores.get)
            return detected_lang.title()
        
        return 'English'
    
    def _parse_ai_response(self, ai_response: str) -> ParsedResume:
        """Parse the AI response JSON into ParsedResume object."""
        
        try:
            # Clean up the response - sometimes AI adds explanation text
            response_text = ai_response.strip()
            
            # Find JSON in response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start != -1 and json_end != 0:
                json_text = response_text[json_start:json_end]
                
                import json
                parsed_data = json.loads(json_text)
                
                # Convert parsed data to ParsedResume objects
                resume = ParsedResume()
                
                # Contact Info
                if 'contact_info' in parsed_data:
                    contact_data = parsed_data['contact_info']
                    resume.contact_info = ContactInfo(
                        name=contact_data.get('name', ''),
                        email=contact_data.get('email', ''),
                        phone=contact_data.get('phone', ''),
                        location=contact_data.get('location', ''),
                        linkedin=contact_data.get('linkedin', ''),
                        github=contact_data.get('github', ''),
                        website=contact_data.get('website', '')
                    )
                
                # Professional Summary
                resume.professional_summary = parsed_data.get('professional_summary', '')
                
                # Job Experiences
                if 'job_experiences' in parsed_data:
                    for job_data in parsed_data['job_experiences']:
                        job = JobExperience(
                            job_title=job_data.get('job_title', ''),
                            company=job_data.get('company', ''),
                            start_date=job_data.get('start_date', ''),
                            end_date=job_data.get('end_date', ''),
                            location=job_data.get('location', ''),
                            is_current=job_data.get('is_current', False),
                            description=job_data.get('description', [])
                        )
                        resume.job_experiences.append(job)
                
                # Education
                if 'education' in parsed_data:
                    for edu_data in parsed_data['education']:
                        edu = Education(
                            degree=edu_data.get('degree', ''),
                            school=edu_data.get('school', ''),
                            graduation_date=edu_data.get('graduation_date', ''),
                            gpa=edu_data.get('gpa', ''),
                            honors=edu_data.get('honors', '')
                        )
                        resume.education.append(edu)
                
                # Projects
                if 'projects' in parsed_data:
                    for proj_data in parsed_data['projects']:
                        project = Project(
                            title=proj_data.get('title', ''),
                            description=proj_data.get('description', ''),
                            technologies=proj_data.get('technologies', []),
                            date=proj_data.get('date', '')
                        )
                        resume.projects.append(project)
                
                # Skills
                if 'skills' in parsed_data:
                    for skill_data in parsed_data['skills']:
                        skill_cat = SkillCategory(
                            category=skill_data.get('category', ''),
                            skills=skill_data.get('skills', [])
                        )
                        resume.skills.append(skill_cat)
                
                # Additional sections
                resume.certifications = parsed_data.get('certifications', [])
                resume.additional_sections = parsed_data.get('additional_sections', {})
                
                return resume
                
            else:
                logger.warning("No valid JSON found in AI response")
                return ParsedResume()
                
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            logger.error(f"AI Response: {ai_response}")
            return ParsedResume()
        except Exception as e:
            logger.error(f"Error parsing AI response: {e}")
            return ParsedResume()
    
    def _rule_based_parse_resume(self, analysis_data: Dict) -> ParsedResume:
        """Fallback rule-based parsing method."""
        
        parsed_resume = ParsedResume()
        sections = analysis_data.get('sections', [])
        
        for section in sections:
            section_type = section.get('section_type', 'other')
            content = section.get('content', [])
            
            if section_type == 'header':
                parsed_resume.contact_info = self._parse_contact_info(content)
            elif section_type == 'experience':
                parsed_resume.job_experiences = self._parse_job_experiences(content)
            elif section_type == 'education':
                parsed_resume.education = self._parse_education(content)
            elif section_type == 'skills':
                parsed_resume.skills = self._parse_skills(content)
            elif section_type == 'projects':
                parsed_resume.projects = self._parse_projects(content)
            elif 'summary' in section.get('title', '').lower() or 'objective' in section.get('title', '').lower():
                parsed_resume.professional_summary = self._parse_summary(content)
            else:
                # Handle additional sections
                section_title = section.get('title', 'Other')
                parsed_resume.additional_sections[section_title] = [block.get('text', '') for block in content]
        
        return parsed_resume
    
    def _parse_contact_info(self, content: List[Dict]) -> ContactInfo:
        """Parse contact information from header section."""
        contact = ContactInfo()
        
        all_text = ' '.join([block.get('text', '') for block in content])
        
        # Extract name (usually the largest text or first line)
        if content:
            # Find the largest text block (likely the name)
            name_block = max(content, key=lambda x: x.get('font_size', 0))
            contact.name = name_block.get('text', '').strip()
        
        # Extract email
        email_match = re.search(self.email_pattern, all_text, re.IGNORECASE)
        if email_match:
            contact.email = email_match.group()
        
        # Extract phone
        for pattern in self.phone_patterns:
            phone_match = re.search(pattern, all_text)
            if phone_match:
                contact.phone = phone_match.group()
                break
        
        # Extract LinkedIn
        linkedin_match = re.search(r'linkedin\.com/in/[\w-]+', all_text, re.IGNORECASE)
        if linkedin_match:
            contact.linkedin = linkedin_match.group()
        
        # Extract GitHub
        github_match = re.search(r'github\.com/[\w-]+', all_text, re.IGNORECASE)
        if github_match:
            contact.github = github_match.group()
        
        # Extract location (common patterns)
        location_patterns = [
            r'\b[A-Z][a-z]+,\s*[A-Z]{2}\b',  # City, ST
            r'\b[A-Z][a-z]+,\s*[A-Z][a-z]+\b',  # City, State
        ]
        
        for pattern in location_patterns:
            location_match = re.search(pattern, all_text)
            if location_match:
                contact.location = location_match.group()
                break
        
        return contact
    
    def _parse_job_experiences(self, content: List[Dict]) -> List[JobExperience]:
        """Parse job experience entries."""
        experiences = []
        
        # Group content by potential job entries
        job_groups = self._group_job_content(content)
        
        for group in job_groups:
            job = JobExperience()
            
            # Find job title (usually bold or larger font)
            title_candidates = [block for block in group if block.get('is_bold', False) or block.get('font_size', 0) > 11]
            if title_candidates:
                job.job_title = title_candidates[0].get('text', '')
            
            # Find company (look for company indicators)
            for block in group:
                text = block.get('text', '').lower()
                if any(indicator in text for indicator in self.company_indicators):
                    job.company = block.get('text', '')
                    break
            
            # Extract dates
            dates = self._extract_dates_from_group(group)
            if dates:
                if len(dates) >= 2:
                    job.start_date = dates[0]
                    job.end_date = dates[1]
                elif len(dates) == 1:
                    job.start_date = dates[0]
                    job.end_date = "Present"
                    job.is_current = True
            
            # Extract description (remaining text)
            description = []
            for block in group:
                text = block.get('text', '').strip()
                if (text and text != job.job_title and text != job.company and 
                    not any(date in text for date in dates) and len(text) > 10):
                    description.append(text)
            
            job.description = description
            
            if job.job_title or job.company:  # Only add if we found meaningful info
                experiences.append(job)
        
        return experiences
    
    def _parse_education(self, content: List[Dict]) -> List[Education]:
        """Parse education entries."""
        education_list = []
        
        # Group content by potential education entries
        edu_groups = self._group_education_content(content)
        
        for group in edu_groups:
            edu = Education()
            
            # Find degree
            for block in group:
                text = block.get('text', '').lower()
                if any(degree in text for degree in self.degree_keywords):
                    edu.degree = block.get('text', '')
                    break
            
            # Find school (look for university/college keywords)
            school_keywords = ['university', 'college', 'institute', 'school', 'academy']
            for block in group:
                text = block.get('text', '').lower()
                if any(keyword in text for keyword in school_keywords):
                    edu.school = block.get('text', '')
                    break
            
            # Extract graduation date
            dates = self._extract_dates_from_group(group)
            if dates:
                edu.graduation_date = dates[-1]  # Usually the last/most recent date
            
            # Extract GPA
            for block in group:
                text = block.get('text', '')
                gpa_match = re.search(r'gpa:?\s*(\d+\.?\d*)', text, re.IGNORECASE)
                if gpa_match:
                    edu.gpa = gpa_match.group(1)
                    break
            
            if edu.degree or edu.school:
                education_list.append(edu)
        
        return education_list
    
    def _parse_projects(self, content: List[Dict]) -> List[Project]:
        """Parse project entries."""
        projects = []
        
        project_groups = self._group_project_content(content)
        
        for group in project_groups:
            project = Project()
            
            # Find project title (usually first or bold)
            if group:
                title_block = group[0]
                for block in group:
                    if block.get('is_bold', False):
                        title_block = block
                        break
                project.title = title_block.get('text', '')
            
            # Extract description
            description_parts = []
            for block in group[1:]:  # Skip title
                text = block.get('text', '').strip()
                if text and len(text) > 5:
                    description_parts.append(text)
            
            project.description = ' '.join(description_parts)
            
            # Extract technologies (look for common tech keywords)
            tech_keywords = ['python', 'java', 'javascript', 'react', 'node', 'sql', 'aws', 'docker', 'git']
            technologies = []
            for keyword in tech_keywords:
                if keyword in project.description.lower():
                    technologies.append(keyword.title())
            project.technologies = technologies
            
            # Extract dates
            dates = self._extract_dates_from_group(group)
            if dates:
                project.date = dates[0]
            
            if project.title:
                projects.append(project)
        
        return projects
    
    def _parse_skills(self, content: List[Dict]) -> List[SkillCategory]:
        """Parse skills section."""
        skills = []
        
        # Try to categorize skills
        all_skills_text = ' '.join([block.get('text', '') for block in content])
        
        # Common skill categories
        categories = {
            'Programming Languages': ['python', 'java', 'javascript', 'c++', 'c#', 'php', 'ruby', 'go', 'rust'],
            'Web Technologies': ['html', 'css', 'react', 'angular', 'vue', 'node', 'express', 'django'],
            'Databases': ['sql', 'mysql', 'postgresql', 'mongodb', 'redis', 'oracle'],
            'Cloud & DevOps': ['aws', 'azure', 'gcp', 'docker', 'kubernetes', 'jenkins', 'terraform'],
            'Tools & Frameworks': ['git', 'jira', 'slack', 'visual studio', 'eclipse']
        }
        
        for category_name, keywords in categories.items():
            found_skills = []
            for keyword in keywords:
                if keyword in all_skills_text.lower():
                    found_skills.append(keyword.title())
            
            if found_skills:
                skills.append(SkillCategory(category=category_name, skills=found_skills))
        
        # If no categorization worked, create a general category
        if not skills:
            skill_items = []
            for block in content:
                text = block.get('text', '').strip()
                if text and len(text) < 50:  # Likely individual skills
                    skill_items.append(text)
            
            if skill_items:
                skills.append(SkillCategory(category="Technical Skills", skills=skill_items))
        
        return skills
    
    def _parse_summary(self, content: List[Dict]) -> str:
        """Parse professional summary."""
        summary_parts = []
        for block in content[1:]:  # Skip title
            text = block.get('text', '').strip()
            if text:
                summary_parts.append(text)
        
        return ' '.join(summary_parts)
    
    def _group_job_content(self, content: List[Dict]) -> List[List[Dict]]:
        """Group content blocks into job entries."""
        groups = []
        current_group = []
        
        for i, block in enumerate(content):
            text = block.get('text', '').lower()
            
            # Check if this might be a new job entry
            is_job_title = (
                block.get('is_bold', False) and 
                any(keyword in text for keyword in self.job_title_keywords)
            )
            
            is_company = any(indicator in text for indicator in self.company_indicators)
            
            # Start new group if we detect a job title or company
            if (is_job_title or is_company) and current_group and i > 0:
                groups.append(current_group)
                current_group = [block]
            else:
                current_group.append(block)
        
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _group_education_content(self, content: List[Dict]) -> List[List[Dict]]:
        """Group content blocks into education entries."""
        groups = []
        current_group = []
        
        for block in content:
            text = block.get('text', '').lower()
            
            # Check if this might be a new education entry
            is_degree = any(keyword in text for keyword in self.degree_keywords)
            is_school = any(keyword in text for keyword in ['university', 'college', 'institute'])
            
            if (is_degree or is_school) and current_group:
                groups.append(current_group)
                current_group = [block]
            else:
                current_group.append(block)
        
        if current_group:
            groups.append(current_group)
        
        return groups if groups else [content]  # Return all content as one group if no clear separation
    
    def _group_project_content(self, content: List[Dict]) -> List[List[Dict]]:
        """Group content blocks into project entries."""
        # Simple grouping - assume each bold item starts a new project
        groups = []
        current_group = []
        
        for block in content:
            if block.get('is_bold', False) and current_group:
                groups.append(current_group)
                current_group = [block]
            else:
                current_group.append(block)
        
        if current_group:
            groups.append(current_group)
        
        return groups if groups else [content]
    
    def _extract_dates_from_group(self, group: List[Dict]) -> List[str]:
        """Extract dates from a group of text blocks."""
        dates = []
        
        for block in group:
            text = block.get('text', '')
            
            # Try each date pattern
            for pattern in self.date_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                for match in matches:
                    if isinstance(match, tuple):
                        if len(match) >= 2:  # Month Year format
                            dates.append(f"{match[0]} {match[1]}")
                        else:
                            dates.append(match[0])
                    else:
                        dates.append(match)
        
        return dates