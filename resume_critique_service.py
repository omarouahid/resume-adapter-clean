#!/usr/bin/env python3
"""
Resume Critique Service - Provides detailed analysis and constructive feedback
"""

import json
import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)

@dataclass
class CritiquePoint:
    """Individual critique point with severity and suggestions."""
    category: str  # structure, content, formatting, ats_optimization
    severity: str  # low, medium, high, critical
    issue: str
    suggestion: str
    example: Optional[str] = None

@dataclass
class SectionCritique:
    """Critique for a specific resume section."""
    section_name: str
    strengths: List[str]
    weaknesses: List[str]
    suggestions: List[str]
    missing_elements: List[str]
    score: int  # 1-10

@dataclass
class ResumeCritique:
    """Complete resume critique with detailed feedback."""
    overall_score: int  # 1-100
    section_critiques: List[SectionCritique]
    critique_points: List[CritiquePoint]
    ats_score: int  # 1-100
    readability_score: int  # 1-100
    impact_score: int  # 1-100
    summary: str
    top_priorities: List[str]

class ResumeCritiqueService:
    """Service for analyzing and critiquing resumes."""
    
    def __init__(self, openrouter_client=None):
        self.openrouter_client = openrouter_client
        
        # Define industry-standard expectations
        self.expected_sections = {
            'header': {
                'required': True,
                'elements': ['name', 'email', 'phone', 'location'],
                'optional': ['linkedin', 'github', 'website']
            },
            'summary': {
                'required': True,
                'elements': ['professional_title', 'years_experience', 'key_skills'],
                'max_lines': 4,
                'min_lines': 2
            },
            'experience': {
                'required': True,
                'elements': ['job_title', 'company', 'dates', 'achievements'],
                'bullet_points': {'min': 2, 'max': 5}
            },
            'education': {
                'required': True,
                'elements': ['degree', 'school', 'graduation_date'],
                'optional': ['gpa', 'honors', 'relevant_courses']
            },
            'skills': {
                'required': True,
                'categories': ['technical', 'soft_skills'],
                'max_items': 15
            }
        }
        
        # ATS optimization keywords
        self.ats_keywords = {
            'action_verbs': [
                'achieved', 'developed', 'implemented', 'managed', 'led', 'created',
                'improved', 'increased', 'reduced', 'optimized', 'designed', 'built',
                'coordinated', 'collaborated', 'analyzed', 'researched', 'delivered'
            ],
            'quantifiers': ['%', 'million', 'thousand', 'k', '$', '+', 'increased', 'decreased'],
            'impact_words': ['impact', 'result', 'outcome', 'achievement', 'success']
        }
    
    def critique_parsed_resume(self, parsed_resume, tex_content: str = "") -> ResumeCritique:
        """Provide comprehensive critique using AI-parsed structured resume data."""
        
        section_critiques = []
        
        # Critique contact information
        if parsed_resume.contact_info:
            contact_critique = self._critique_contact_info(parsed_resume.contact_info)
            section_critiques.append(contact_critique)
        
        # Critique professional summary
        if parsed_resume.professional_summary:
            summary_critique = self._critique_professional_summary(parsed_resume.professional_summary)
            section_critiques.append(summary_critique)
        
        # Critique job experiences
        if parsed_resume.job_experiences:
            experience_critique = self._critique_job_experiences(parsed_resume.job_experiences)
            section_critiques.append(experience_critique)
        
        # Critique education
        if parsed_resume.education:
            education_critique = self._critique_education(parsed_resume.education)
            section_critiques.append(education_critique)
        
        # Critique skills
        if parsed_resume.skills:
            skills_critique = self._critique_skills(parsed_resume.skills)
            section_critiques.append(skills_critique)
        
        # Critique projects if any
        if parsed_resume.projects:
            projects_critique = self._critique_projects(parsed_resume.projects)
            section_critiques.append(projects_critique)
        
        # Generate critique points from parsed data
        critique_points = self._generate_critique_points_from_parsed_data(parsed_resume, tex_content)
        
        # Calculate scores
        ats_score = self._calculate_ats_score_from_parsed_data(parsed_resume)
        readability_score = self._calculate_readability_score_from_parsed_data(parsed_resume)
        impact_score = self._calculate_impact_score_from_parsed_data(parsed_resume)
        
        # Overall score (weighted average)
        overall_score = int((ats_score * 0.3 + readability_score * 0.3 + impact_score * 0.4))
        
        # Generate summary and priorities
        summary = self._generate_summary_from_parsed_data(overall_score, parsed_resume)
        top_priorities = self._get_top_priorities(critique_points)
        
        return ResumeCritique(
            overall_score=overall_score,
            section_critiques=section_critiques,
            critique_points=critique_points,
            ats_score=ats_score,
            readability_score=readability_score,
            impact_score=impact_score,
            summary=summary,
            top_priorities=top_priorities
        )

    def critique_resume(self, analysis_data: Dict, tex_content: str = "") -> ResumeCritique:
        """Provide comprehensive critique of the resume."""
        
        sections = analysis_data.get('sections', [])
        text_blocks = analysis_data.get('text_blocks', [])
        
        # Analyze each section
        section_critiques = []
        for section in sections:
            critique = self._critique_section(section)
            section_critiques.append(critique)
        
        # Generate critique points
        critique_points = self._generate_critique_points(sections, tex_content)
        
        # Calculate scores
        ats_score = self._calculate_ats_score(sections, tex_content)
        readability_score = self._calculate_readability_score(text_blocks)
        impact_score = self._calculate_impact_score(sections)
        
        # Overall score (weighted average)
        overall_score = int((ats_score * 0.3 + readability_score * 0.3 + impact_score * 0.4))
        
        # Generate summary and priorities
        summary = self._generate_summary(overall_score, section_critiques, critique_points)
        top_priorities = self._get_top_priorities(critique_points)
        
        return ResumeCritique(
            overall_score=overall_score,
            section_critiques=section_critiques,
            critique_points=critique_points,
            ats_score=ats_score,
            readability_score=readability_score,
            impact_score=impact_score,
            summary=summary,
            top_priorities=top_priorities
        )
    
    def _critique_section(self, section: Dict) -> SectionCritique:
        """Critique a specific section of the resume."""
        
        section_type = section.get('section_type', 'other')
        section_title = section.get('title', 'Unknown')
        content = section.get('content', [])
        
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 5  # Default score
        
        # Get text content for all sections
        text_content = ' '.join([block.get('text', '') for block in content]).lower()
        
        if section_type in self.expected_sections:
            expected = self.expected_sections[section_type]
            
            if section_type == 'header':
                score, strengths, weaknesses, suggestions, missing_elements = self._critique_header(content, text_content)
            elif section_type == 'experience':
                score, strengths, weaknesses, suggestions, missing_elements = self._critique_experience(content, text_content)
            elif section_type == 'education':
                score, strengths, weaknesses, suggestions, missing_elements = self._critique_education(content, text_content)
            elif section_type == 'skills':
                score, strengths, weaknesses, suggestions, missing_elements = self._critique_skills(content, text_content)
            else:
                score, strengths, weaknesses, suggestions = self._critique_generic_section(content, text_content)
                missing_elements = []  # Add missing_elements for consistency
        else:
            # Generic section critique
            score, strengths, weaknesses, suggestions = self._critique_generic_section(content, text_content)
            missing_elements = []  # Add missing_elements for consistency
        
        return SectionCritique(
            section_name=section_title,
            strengths=strengths,
            weaknesses=weaknesses,
            suggestions=suggestions,
            missing_elements=missing_elements,
            score=score
        )
    
    def _critique_header(self, content: List[Dict], text_content: str) -> Tuple[int, List[str], List[str], List[str], List[str]]:
        """Critique header section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 7
        
        # Check for required elements
        has_email = '@' in text_content
        has_phone = any(char.isdigit() for char in text_content) and ('phone' in text_content or '+' in text_content or '(' in text_content)
        has_location = any(location_word in text_content for location_word in ['city', 'state', 'country', 'street', 'ave'])
        
        if has_email:
            strengths.append("✅ Email address present")
        else:
            missing_elements.append("Email address")
            weaknesses.append("❌ Missing email address")
            score -= 2
        
        if has_phone:
            strengths.append("✅ Phone number present")
        else:
            missing_elements.append("Phone number")
            weaknesses.append("❌ Missing phone number")
            score -= 1
        
        if has_location:
            strengths.append("✅ Location information present")
        else:
            suggestions.append("💡 Consider adding city/state for location context")
        
        # Check for professional links
        if 'linkedin' in text_content:
            strengths.append("✅ LinkedIn profile included")
        else:
            suggestions.append("💡 Add LinkedIn profile URL for professional networking")
        
        if 'github' in text_content or 'portfolio' in text_content:
            strengths.append("✅ Professional portfolio/GitHub link included")
        
        # Check name prominence
        name_blocks = [block for block in content if block.get('font_size', 0) > 14]
        if name_blocks:
            strengths.append("✅ Name appears prominently sized")
        else:
            weaknesses.append("⚠️ Name should be more prominent (larger font)")
            suggestions.append("💡 Make your name the largest text in the header section")
            score -= 1
        
        return max(1, score), strengths, weaknesses, suggestions, missing_elements
    
    def _critique_experience(self, content: List[Dict], text_content: str) -> Tuple[int, List[str], List[str], List[str], List[str]]:
        """Critique experience section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 6
        
        # Check for quantifiable achievements
        has_numbers = any(char.isdigit() for char in text_content)
        has_percentages = '%' in text_content
        has_dollar_amounts = '$' in text_content
        
        if has_numbers or has_percentages or has_dollar_amounts:
            strengths.append("✅ Includes quantifiable achievements")
            score += 1
        else:
            weaknesses.append("❌ Lacks quantifiable achievements and metrics")
            suggestions.append("💡 Add specific numbers, percentages, and dollar amounts to demonstrate impact")
            score -= 2
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] if verb in text_content)
        if action_verb_count >= 3:
            strengths.append(f"✅ Uses strong action verbs ({action_verb_count} found)")
        else:
            weaknesses.append("⚠️ Limited use of strong action verbs")
            suggestions.append("💡 Start bullet points with action verbs like 'developed', 'managed', 'increased'")
            score -= 1
        
        # Check for job titles and companies
        if any(word in text_content for word in ['engineer', 'manager', 'analyst', 'developer', 'consultant', 'director']):
            strengths.append("✅ Clear job titles present")
        else:
            weaknesses.append("❌ Job titles unclear or missing")
            missing_elements.append("Clear job titles")
            score -= 1
        
        # Check for company information
        if any(word in text_content for word in ['inc', 'corp', 'llc', 'ltd', 'company']):
            strengths.append("✅ Company names included")
        else:
            suggestions.append("💡 Ensure all company names are clearly stated")
        
        # Check for dates
        if re.search(r'\b\d{4}\b', text_content):
            strengths.append("✅ Employment dates included")
        else:
            missing_elements.append("Employment dates")
            weaknesses.append("❌ Missing employment dates")
            score -= 1
        
        return max(1, score), strengths, weaknesses, suggestions, missing_elements
    
    def _critique_education(self, content: List[Dict], text_content: str) -> Tuple[int, List[str], List[str], List[str], List[str]]:
        """Critique education section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 7
        
        # Check for degree information
        degree_keywords = ['bachelor', 'master', 'phd', 'doctorate', 'associate', 'bs', 'ba', 'ms', 'ma', 'mba']
        has_degree = any(degree in text_content for degree in degree_keywords)
        
        if has_degree:
            strengths.append("✅ Degree type clearly specified")
        else:
            weaknesses.append("❌ Degree type unclear or missing")
            missing_elements.append("Degree type (BS, MS, etc.)")
            score -= 2
        
        # Check for school/university
        school_keywords = ['university', 'college', 'institute', 'school']
        has_school = any(school in text_content for school in school_keywords)
        
        if has_school:
            strengths.append("✅ Educational institution mentioned")
        else:
            weaknesses.append("❌ School/university name missing")
            missing_elements.append("School/university name")
            score -= 1
        
        # Check for graduation date
        if re.search(r'\b\d{4}\b', text_content):
            strengths.append("✅ Graduation date included")
        else:
            suggestions.append("💡 Consider adding graduation year")
        
        # Check for GPA (if recent graduate)
        if 'gpa' in text_content or re.search(r'\d\.\d', text_content):
            strengths.append("✅ GPA included (good for recent graduates)")
        
        # Check for relevant coursework or honors
        if any(word in text_content for word in ['honors', 'magna cum laude', 'summa cum laude', 'dean\'s list']):
            strengths.append("✅ Academic honors mentioned")
        
        return max(1, score), strengths, weaknesses, suggestions, missing_elements
    
    def _critique_skills(self, content: List[Dict], text_content: str) -> Tuple[int, List[str], List[str], List[str], List[str]]:
        """Critique skills section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 6
        
        # Count skills mentioned
        skill_items = len([block for block in content if len(block.get('text', '').split()) <= 3])
        
        if skill_items >= 8:
            strengths.append(f"✅ Good variety of skills listed ({skill_items} items)")
            score += 1
        elif skill_items >= 5:
            strengths.append("✅ Adequate number of skills listed")
        else:
            weaknesses.append("⚠️ Limited number of skills listed")
            suggestions.append("💡 Add more relevant technical and soft skills")
            score -= 1
        
        # Check for technical skills
        tech_keywords = ['python', 'java', 'sql', 'excel', 'javascript', 'aws', 'docker', 'git']
        tech_skills_found = sum(1 for skill in tech_keywords if skill in text_content.lower())
        
        if tech_skills_found >= 3:
            strengths.append("✅ Strong technical skills representation")
        else:
            suggestions.append("💡 Include more specific technical skills relevant to your field")
        
        # Check for organization (categories)
        if len(content) > 10:  # Likely has categories if many text blocks
            strengths.append("✅ Skills appear to be well-organized")
        else:
            suggestions.append("💡 Consider organizing skills into categories (Technical, Leadership, etc.)")
        
        return max(1, score), strengths, weaknesses, suggestions, missing_elements
    
    def _critique_generic_section(self, content: List[Dict], text_content: str) -> Tuple[int, List[str], List[str], List[str]]:
        """Critique generic section."""
        strengths = []
        weaknesses = []
        suggestions = []
        score = 5
        
        if len(content) > 0:
            strengths.append("✅ Section has content")
        else:
            weaknesses.append("❌ Section appears empty")
            score = 1
        
        if len(text_content) > 50:
            strengths.append("✅ Sufficient detail provided")
            score += 1
        else:
            suggestions.append("💡 Consider adding more relevant details")
        
        return max(1, score), strengths, weaknesses, suggestions
    
    def _generate_critique_points(self, sections: List[Dict], tex_content: str) -> List[CritiquePoint]:
        """Generate specific critique points."""
        points = []
        
        # Check overall structure
        section_types = [s.get('section_type', 'other') for s in sections]
        
        # Missing critical sections
        if 'experience' not in section_types:
            points.append(CritiquePoint(
                category="structure",
                severity="critical",
                issue="Missing experience section",
                suggestion="Add a dedicated work experience section - it's essential for most resumes"
            ))
        
        if 'skills' not in section_types:
            points.append(CritiquePoint(
                category="structure",
                severity="high",
                issue="Missing skills section",
                suggestion="Add a skills section to highlight your technical and professional competencies"
            ))
        
        # Check for summary/objective
        if 'summary' not in section_types and 'objective' not in section_types:
            points.append(CritiquePoint(
                category="content",
                severity="medium",
                issue="Missing professional summary",
                suggestion="Add a brief professional summary to introduce yourself and highlight key qualifications",
                example="'Experienced software engineer with 5+ years developing scalable web applications...'"
            ))
        
        # ATS optimization checks
        if tex_content:
            # Check for excessive formatting
            if tex_content.count('\\textbf{') > 20:
                points.append(CritiquePoint(
                    category="ats_optimization",
                    severity="medium",
                    issue="Excessive bold formatting may confuse ATS",
                    suggestion="Use bold formatting sparingly - only for section headers and key achievements"
                ))
            
            # Check for tables (can be ATS-problematic)
            if 'tabular' in tex_content:
                points.append(CritiquePoint(
                    category="ats_optimization",
                    severity="medium",
                    issue="Tables can be problematic for ATS parsing",
                    suggestion="Consider using simple lists instead of complex table layouts"
                ))
        
        return points
    
    def _calculate_ats_score(self, sections: List[Dict], tex_content: str) -> int:
        """Calculate ATS optimization score."""
        score = 70  # Base score
        
        # Check for standard sections
        section_types = [s.get('section_type', 'other') for s in sections]
        required_sections = ['header', 'experience', 'education', 'skills']
        
        for section in required_sections:
            if section in section_types:
                score += 5
            else:
                score -= 10
        
        # Check for action verbs and quantifiable results
        all_text = ' '.join([' '.join([block.get('text', '') for block in section.get('content', [])]) for section in sections])
        
        action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] if verb in all_text.lower())
        score += min(action_verb_count * 2, 20)  # Max 20 points for action verbs
        
        # Check for numbers and quantifiable results
        if any(char.isdigit() for char in all_text):
            score += 10
        
        return min(100, max(1, score))
    
    def _calculate_readability_score(self, text_blocks: List[Dict]) -> int:
        """Calculate readability and formatting score."""
        if not text_blocks:
            return 50
        
        score = 70  # Base score
        
        # Check for consistent formatting
        font_sizes = [block.get('font_size', 12) for block in text_blocks]
        if len(set(font_sizes)) <= 4:  # Not too many different font sizes
            score += 10
        else:
            score -= 5
        
        # Check text length variability (good for readability)
        text_lengths = [len(block.get('text', '')) for block in text_blocks if block.get('text', '')]
        if text_lengths:
            avg_length = sum(text_lengths) / len(text_lengths)
            if 10 <= avg_length <= 100:  # Good length range
                score += 10
        
        # Check for appropriate use of bold/italic
        bold_count = sum(1 for block in text_blocks if block.get('is_bold', False))
        if 0 < bold_count <= len(text_blocks) * 0.2:  # 5-20% bold is good
            score += 10
        
        return min(100, max(1, score))
    
    def _calculate_impact_score(self, sections: List[Dict]) -> int:
        """Calculate impact and achievement score."""
        score = 50  # Base score
        
        all_text = ' '.join([' '.join([block.get('text', '') for block in section.get('content', [])]) for section in sections])
        
        # Check for quantifiable achievements
        has_percentages = '%' in all_text
        has_numbers = any(char.isdigit() for char in all_text)
        has_dollar_signs = '$' in all_text
        
        if has_percentages:
            score += 15
        if has_numbers:
            score += 10
        if has_dollar_signs:
            score += 15
        
        # Check for impact words
        impact_words = ['achieved', 'improved', 'increased', 'reduced', 'saved', 'generated', 'led', 'managed']
        impact_count = sum(1 for word in impact_words if word in all_text.lower())
        score += min(impact_count * 3, 15)
        
        return min(100, max(1, score))
    
    def _generate_summary(self, overall_score: int, section_critiques: List[SectionCritique], 
                         critique_points: List[CritiquePoint]) -> str:
        """Generate overall critique summary."""
        
        if overall_score >= 85:
            summary = "🌟 **Excellent Resume!** Your resume demonstrates strong professional presentation with clear structure and compelling content."
        elif overall_score >= 70:
            summary = "✅ **Good Resume** with solid fundamentals. With some focused improvements, this could be exceptional."
        elif overall_score >= 55:
            summary = "⚠️ **Average Resume** that covers the basics but needs significant improvements to stand out."
        else:
            summary = "❌ **Resume Needs Major Work** - several critical areas require attention before this will be effective."
        
        # Add specific insights
        critical_issues = [p for p in critique_points if p.severity == 'critical']
        high_issues = [p for p in critique_points if p.severity == 'high']
        
        if critical_issues:
            summary += f"\n\n🚨 **Critical Issues ({len(critical_issues)})**: These must be addressed immediately."
        
        if high_issues:
            summary += f"\n\n⚠️ **High Priority ({len(high_issues)})**: Important improvements that will significantly impact effectiveness."
        
        return summary
    
    def _get_top_priorities(self, critique_points: List[CritiquePoint]) -> List[str]:
        """Get top priority improvements."""
        
        # Sort by severity
        severity_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        sorted_points = sorted(critique_points, key=lambda p: severity_order.get(p.severity, 0), reverse=True)
        
        priorities = []
        for point in sorted_points[:5]:  # Top 5 priorities
            priority_text = f"**{point.severity.upper()}**: {point.issue} - {point.suggestion}"
            priorities.append(priority_text)
        
        return priorities

    def get_critique_as_text(self, critique: ResumeCritique) -> str:
        """Convert critique to formatted text for display."""
        
        text_parts = [
            f"# 📊 RESUME CRITIQUE REPORT",
            f"**Overall Score: {critique.overall_score}/100**",
            "",
            f"## 📈 Detailed Scores",
            f"- **ATS Optimization**: {critique.ats_score}/100",
            f"- **Readability**: {critique.readability_score}/100", 
            f"- **Impact & Achievements**: {critique.impact_score}/100",
            "",
            f"## 📝 Executive Summary",
            critique.summary,
            "",
            f"## 🎯 Top Priorities",
        ]
        
        for i, priority in enumerate(critique.top_priorities, 1):
            text_parts.append(f"{i}. {priority}")
        
        text_parts.extend([
            "",
            "## 📋 Section-by-Section Analysis"
        ])
        
        for section_critique in critique.section_critiques:
            text_parts.extend([
                f"### {section_critique.section_name} (Score: {section_critique.score}/10)",
                ""
            ])
            
            if section_critique.strengths:
                text_parts.append("**Strengths:**")
                for strength in section_critique.strengths:
                    text_parts.append(f"- {strength}")
                text_parts.append("")
            
            if section_critique.weaknesses:
                text_parts.append("**Areas for Improvement:**")
                for weakness in section_critique.weaknesses:
                    text_parts.append(f"- {weakness}")
                text_parts.append("")
            
            if section_critique.suggestions:
                text_parts.append("**Suggestions:**")
                for suggestion in section_critique.suggestions:
                    text_parts.append(f"- {suggestion}")
                text_parts.append("")
            
            if section_critique.missing_elements:
                text_parts.append("**Missing Elements:**")
                for missing in section_critique.missing_elements:
                    text_parts.append(f"- {missing}")
                text_parts.append("")
        
        return "\n".join(text_parts)
    
    # Methods for critiquing parsed resume data
    
    def _critique_contact_info(self, contact_info) -> SectionCritique:
        """Critique contact information section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 8
        
        if contact_info.name:
            strengths.append("Name is clearly provided")
        else:
            missing_elements.append("Name")
            score -= 2
        
        if contact_info.email:
            if "@" in contact_info.email:
                strengths.append("Valid email format")
            else:
                weaknesses.append("Email format appears invalid")
                score -= 1
        else:
            missing_elements.append("Email address")
            score -= 2
        
        if contact_info.phone:
            strengths.append("Phone number provided")
        else:
            missing_elements.append("Phone number")
            score -= 1
        
        if contact_info.location:
            strengths.append("Location information provided")
        
        if contact_info.linkedin:
            strengths.append("LinkedIn profile included")
        else:
            suggestions.append("Add LinkedIn profile for professional networking")
        
        if contact_info.github:
            strengths.append("GitHub profile included - great for tech roles")
        
        return SectionCritique("Contact Information", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _critique_professional_summary(self, summary: str) -> SectionCritique:
        """Critique professional summary section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 6
        
        if len(summary) < 50:
            weaknesses.append("Summary is too brief - should be 2-4 sentences")
            score -= 2
        elif len(summary) > 300:
            weaknesses.append("Summary is too long - should be concise")
            score -= 1
        else:
            strengths.append("Summary is appropriate length")
            score += 1
        
        # Check for action verbs
        action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] if verb in summary.lower())
        if action_verb_count >= 2:
            strengths.append("Uses strong action verbs")
            score += 1
        else:
            suggestions.append("Include more action verbs to demonstrate impact")
        
        # Check for quantifiable achievements
        quantifier_count = sum(1 for q in self.ats_keywords['quantifiers'] if q in summary.lower())
        if quantifier_count > 0:
            strengths.append("Includes quantifiable achievements")
            score += 1
        else:
            suggestions.append("Add specific numbers or percentages to demonstrate impact")
        
        return SectionCritique("Professional Summary", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _critique_job_experiences(self, experiences) -> SectionCritique:
        """Critique job experiences section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 7
        
        if len(experiences) == 0:
            missing_elements.append("Work experience")
            return SectionCritique("Professional Experience", strengths, weaknesses, suggestions, missing_elements, 1)
        
        # Check each job experience
        total_bullet_points = 0
        jobs_with_achievements = 0
        
        for job in experiences:
            if not job.job_title:
                missing_elements.append("Job title for one or more positions")
                score -= 1
            
            if not job.company:
                missing_elements.append("Company name for one or more positions")
                score -= 1
            
            if not job.start_date:
                missing_elements.append("Start date for one or more positions")
                score -= 1
            
            if job.description:
                total_bullet_points += len(job.description)
                
                # Check for action verbs and quantifiable achievements
                job_text = " ".join(job.description).lower()
                action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] if verb in job_text)
                quantifier_count = sum(1 for q in self.ats_keywords['quantifiers'] if q in job_text)
                
                if action_verb_count >= 2:
                    jobs_with_achievements += 1
                
                if len(job.description) < 2:
                    weaknesses.append(f"Job at {job.company} has too few bullet points (minimum 2-3)")
                    score -= 1
                elif len(job.description) > 6:
                    suggestions.append(f"Consider reducing bullet points for {job.company} (maximum 5-6)")
                
        if jobs_with_achievements > len(experiences) * 0.7:
            strengths.append("Most positions demonstrate measurable achievements")
            score += 1
        else:
            suggestions.append("Add more quantifiable achievements and action verbs to job descriptions")
        
        if total_bullet_points / len(experiences) >= 3:
            strengths.append("Good detail level in job descriptions")
        else:
            weaknesses.append("Job descriptions need more detail")
            score -= 1
        
        return SectionCritique("Professional Experience", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _critique_education(self, education_list) -> SectionCritique:
        """Critique education section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 8
        
        if len(education_list) == 0:
            missing_elements.append("Education information")
            return SectionCritique("Education", strengths, weaknesses, suggestions, missing_elements, 3)
        
        for edu in education_list:
            if not edu.degree:
                missing_elements.append("Degree information")
                score -= 1
            
            if not edu.school:
                missing_elements.append("School/Institution name")
                score -= 1
            
            if not edu.graduation_date:
                suggestions.append("Consider adding graduation date")
            
            if edu.gpa and float(edu.gpa.replace("GPA: ", "").split()[0]) >= 3.5:
                strengths.append(f"Strong GPA included ({edu.gpa})")
            
            if edu.honors:
                strengths.append("Academic honors mentioned")
                score += 1
            
            if edu.relevant_courses:
                strengths.append("Relevant coursework listed")
                score += 1
        
        return SectionCritique("Education", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _critique_skills(self, skills_list) -> SectionCritique:
        """Critique skills section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 6
        
        if len(skills_list) == 0:
            missing_elements.append("Technical skills")
            return SectionCritique("Technical Skills", strengths, weaknesses, suggestions, missing_elements, 1)
        
        total_skills = sum(len(skill_cat.skills) for skill_cat in skills_list)
        
        if total_skills < 5:
            weaknesses.append("Too few skills listed")
            score -= 2
        elif total_skills > 20:
            suggestions.append("Consider reducing skills to most relevant 10-15")
            score -= 1
        else:
            strengths.append("Good number of skills listed")
            score += 1
        
        # Check for categorization
        categorized_skills = sum(1 for skill_cat in skills_list if skill_cat.category)
        if categorized_skills > 0:
            strengths.append("Skills are well-categorized")
            score += 1
        else:
            suggestions.append("Consider categorizing skills (e.g., Programming Languages, Frameworks, Tools)")
        
        return SectionCritique("Technical Skills", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _critique_projects(self, projects_list) -> SectionCritique:
        """Critique projects section."""
        strengths = []
        weaknesses = []
        suggestions = []
        missing_elements = []
        score = 7
        
        if len(projects_list) == 0:
            suggestions.append("Consider adding relevant projects to showcase skills")
            return SectionCritique("Projects", strengths, weaknesses, suggestions, missing_elements, 5)
        
        for project in projects_list:
            if not project.title:
                missing_elements.append("Project title")
                score -= 1
            
            if not project.description:
                missing_elements.append("Project description")
                score -= 1
            
            if project.technologies:
                strengths.append("Technologies used are clearly listed")
                score += 1
            else:
                suggestions.append("Add technologies used for each project")
        
        if len(projects_list) >= 2:
            strengths.append("Multiple projects demonstrate diverse skills")
        
        return SectionCritique("Projects", strengths, weaknesses, suggestions, missing_elements, max(1, score))
    
    def _generate_critique_points_from_parsed_data(self, parsed_resume, tex_content: str) -> List[CritiquePoint]:
        """Generate critique points from parsed resume data."""
        critique_points = []
        
        # Overall structure critique
        if not parsed_resume.professional_summary:
            critique_points.append(CritiquePoint(
                "structure", "high", 
                "Missing professional summary",
                "Add a compelling 2-3 sentence professional summary at the top",
                "Professional Software Engineer with 5+ years experience..."
            ))
        
        # ATS optimization critique
        if not parsed_resume.contact_info or not parsed_resume.contact_info.email:
            critique_points.append(CritiquePoint(
                "ats_optimization", "critical",
                "Missing contact email",
                "Add a professional email address in the header",
                "john.doe@email.com"
            ))
        
        return critique_points
    
    def _calculate_ats_score_from_parsed_data(self, parsed_resume) -> int:
        """Calculate ATS score from parsed resume data."""
        score = 50  # Base score
        
        # Contact information
        if parsed_resume.contact_info:
            if parsed_resume.contact_info.email: score += 10
            if parsed_resume.contact_info.phone: score += 10
            if parsed_resume.contact_info.name: score += 10
        
        # Required sections
        if parsed_resume.professional_summary: score += 5
        if parsed_resume.job_experiences: score += 10
        if parsed_resume.education: score += 5
        if parsed_resume.skills: score += 10
        
        return min(100, score)
    
    def _calculate_readability_score_from_parsed_data(self, parsed_resume) -> int:
        """Calculate readability score from parsed resume data."""
        score = 60  # Base score
        
        # Check if sections are well-structured
        if parsed_resume.job_experiences:
            for job in parsed_resume.job_experiences:
                if job.description and len(job.description) >= 2:
                    score += 5
        
        if parsed_resume.skills:
            score += 10  # Well-structured skills section
        
        return min(100, score)
    
    def _calculate_impact_score_from_parsed_data(self, parsed_resume) -> int:
        """Calculate impact score from parsed resume data."""
        score = 40  # Base score
        
        # Check for quantifiable achievements in job descriptions
        if parsed_resume.job_experiences:
            for job in parsed_resume.job_experiences:
                if job.description:
                    job_text = " ".join(job.description).lower()
                    quantifier_count = sum(1 for q in self.ats_keywords['quantifiers'] if q in job_text)
                    action_verb_count = sum(1 for verb in self.ats_keywords['action_verbs'] if verb in job_text)
                    
                    score += min(15, quantifier_count * 5)  # Up to 15 points for quantifiers
                    score += min(10, action_verb_count * 2)  # Up to 10 points for action verbs
        
        return min(100, score)
    
    def _generate_summary_from_parsed_data(self, overall_score: int, parsed_resume) -> str:
        """Generate summary based on parsed resume data."""
        if overall_score >= 80:
            summary = "This is a strong resume with well-structured content and clear presentation."
        elif overall_score >= 60:
            summary = "This resume has good fundamentals but could benefit from specific improvements."
        else:
            summary = "This resume needs significant improvements to effectively showcase qualifications."
        
        # Add specific insights based on parsed data
        if parsed_resume.job_experiences and len(parsed_resume.job_experiences) > 3:
            summary += " The extensive work experience demonstrates career progression."
        
        if parsed_resume.skills and len(parsed_resume.skills) > 0:
            summary += " Technical skills are clearly presented."
        
        return summary