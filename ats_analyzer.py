#!/usr/bin/env python3
"""
ATS Analyzer - Analyze resume compatibility with Applicant Tracking Systems.
No signup required - works with session data only.
"""

import re
import streamlit as st
from typing import Dict, List, Tuple, Optional, Any
import logging
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ATSScore:
    """ATS compatibility score breakdown."""
    overall_score: int  # 0-100
    keyword_score: int
    format_score: int
    content_score: int
    readability_score: int
    recommendations: List[str]
    strengths: List[str]
    warnings: List[str]

class ATSAnalyzer:
    """Analyze resume for ATS compatibility without requiring user accounts."""
    
    def __init__(self):
        """Initialize ATS analyzer."""
        self.common_keywords = {
            'software_engineering': [
                'python', 'javascript', 'react', 'node.js', 'sql', 'git', 'aws', 'docker',
                'kubernetes', 'microservices', 'api', 'database', 'agile', 'scrum',
                'testing', 'ci/cd', 'devops', 'linux', 'java', 'c++', 'html', 'css'
            ],
            'data_science': [
                'machine learning', 'python', 'r', 'sql', 'pandas', 'numpy', 'scikit-learn',
                'tensorflow', 'pytorch', 'statistics', 'data visualization', 'tableau',
                'power bi', 'excel', 'hadoop', 'spark', 'deep learning', 'nlp'
            ],
            'marketing': [
                'digital marketing', 'seo', 'sem', 'social media', 'content marketing',
                'email marketing', 'google analytics', 'a/b testing', 'conversion optimization',
                'brand management', 'campaign management', 'crm', 'lead generation'
            ],
            'finance': [
                'financial analysis', 'excel', 'financial modeling', 'valuation', 'dcf',
                'budgeting', 'forecasting', 'risk management', 'compliance', 'audit',
                'gaap', 'ifrs', 'financial reporting', 'treasury', 'investment'
            ],
            'sales': [
                'crm', 'salesforce', 'lead generation', 'prospecting', 'closing',
                'negotiation', 'account management', 'pipeline management', 'quota attainment',
                'relationship building', 'presentation', 'product demos'
            ]
        }
        
        self.ats_friendly_formats = [
            'clear section headers',
            'standard fonts',
            'consistent formatting',
            'bullet points',
            'chronological order',
            'no images or graphics',
            'simple layout'
        ]
        
        self.red_flags = [
            'gaps in employment',
            'inconsistent dates',
            'too many job changes',
            'unclear job titles',
            'missing contact info',
            'poor grammar',
            'typos'
        ]
    
    def analyze_resume(self, resume_data: Dict[str, Any], job_description: str = "") -> ATSScore:
        """
        Analyze resume for ATS compatibility.
        
        Args:
            resume_data: Parsed resume data
            job_description: Optional job posting to match against
            
        Returns:
            ATS compatibility score and recommendations
        """
        
        scores = {}
        recommendations = []
        strengths = []
        warnings = []
        
        # Analyze keywords
        keyword_result = self._analyze_keywords(resume_data, job_description)
        scores['keyword'] = keyword_result['score']
        recommendations.extend(keyword_result['recommendations'])
        strengths.extend(keyword_result['strengths'])
        
        # Analyze format
        format_result = self._analyze_format(resume_data)
        scores['format'] = format_result['score']
        recommendations.extend(format_result['recommendations'])
        strengths.extend(format_result['strengths'])
        
        # Analyze content quality
        content_result = self._analyze_content(resume_data)
        scores['content'] = content_result['score']
        recommendations.extend(content_result['recommendations'])
        strengths.extend(content_result['strengths'])
        warnings.extend(content_result['warnings'])
        
        # Analyze readability
        readability_result = self._analyze_readability(resume_data)
        scores['readability'] = readability_result['score']
        recommendations.extend(readability_result['recommendations'])
        
        # Calculate overall score
        overall_score = int(
            scores['keyword'] * 0.3 +
            scores['format'] * 0.25 +
            scores['content'] * 0.3 +
            scores['readability'] * 0.15
        )
        
        return ATSScore(
            overall_score=overall_score,
            keyword_score=scores['keyword'],
            format_score=scores['format'],
            content_score=scores['content'],
            readability_score=scores['readability'],
            recommendations=recommendations[:10],  # Top 10
            strengths=strengths[:5],  # Top 5
            warnings=warnings[:5]  # Top 5
        )
    
    def generate_ats_improvement_prompt(self, ats_score: ATSScore, job_description: str = "") -> str:
        """
        Generate a comprehensive prompt for improving resume based on ATS analysis.
        
        Args:
            ats_score: ATS analysis results
            job_description: Optional job description for targeted improvements
            
        Returns:
            Detailed improvement prompt for AI
        """
        
        job_context = ""
        if job_description.strip():
            job_context = f"""

Target Job Description:
{job_description}

Optimize the resume specifically for this job posting by incorporating relevant keywords and requirements.
"""
        
        recommendations_text = "\n".join([f"• {rec}" for rec in ats_score.recommendations])
        warnings_text = "\n".join([f"• {warning}" for warning in ats_score.warnings]) if ats_score.warnings else "None"
        
        return f"""
Improve this resume to achieve better ATS compatibility and higher scoring.

Current ATS Analysis:
- Overall Score: {ats_score.overall_score}/100
- Keyword Score: {ats_score.keyword_score}/100
- Format Score: {ats_score.format_score}/100
- Content Score: {ats_score.content_score}/100
- Readability Score: {ats_score.readability_score}/100

Key Recommendations to Address:
{recommendations_text}

Warnings to Fix:
{warnings_text}
{job_context}
CRITICAL ATS IMPROVEMENT REQUIREMENTS:
1. Include ALL relevant keywords naturally in context
2. Use standard section headings (Experience, Education, Skills, etc.)
3. Optimize for ATS parsing with clear, simple formatting
4. Include quantifiable achievements with numbers and metrics
5. Use action verbs and industry-standard terminology
6. Ensure consistent date formatting and clear job titles
7. Add technical skills section if missing
8. Include relevant certifications and education details
9. Make contact information easily scannable
10. Structure content for both ATS and human readability

Focus on achieving a score above 80/100 while maintaining professional presentation.
        """
    
    def _analyze_keywords(self, resume_data: Dict[str, Any], job_description: str) -> Dict:
        """Analyze keyword optimization."""
        score = 50  # Base score
        recommendations = []
        strengths = []
        
        # Extract all text from resume
        resume_text = self._extract_resume_text(resume_data).lower()
        
        # If job description provided, analyze against it
        if job_description:
            job_keywords = self._extract_keywords_from_job(job_description.lower())
            matched_keywords = []
            
            for keyword in job_keywords:
                if keyword in resume_text:
                    matched_keywords.append(keyword)
            
            match_ratio = len(matched_keywords) / len(job_keywords) if job_keywords else 0
            score = int(match_ratio * 100)
            
            if match_ratio > 0.7:
                strengths.append(f"Strong keyword match ({len(matched_keywords)}/{len(job_keywords)})")
            elif match_ratio < 0.3:
                missing_keywords = set(job_keywords) - set(matched_keywords)
                recommendations.append(f"Add these keywords: {', '.join(list(missing_keywords)[:5])}")
        
        else:
            # Analyze against common industry keywords
            detected_field = self._detect_field(resume_text)
            if detected_field:
                field_keywords = self.common_keywords[detected_field]
                found_keywords = [kw for kw in field_keywords if kw in resume_text]
                
                keyword_coverage = len(found_keywords) / len(field_keywords)
                score = int(keyword_coverage * 100)
                
                if keyword_coverage > 0.6:
                    strengths.append(f"Good {detected_field} keyword coverage")
                else:
                    missing = [kw for kw in field_keywords[:5] if kw not in resume_text]
                    recommendations.append(f"Consider adding: {', '.join(missing)}")
        
        # General keyword recommendations
        if len(resume_text.split()) < 200:
            recommendations.append("Resume appears short - add more relevant details")
        
        if not any(skill in resume_text for skill in ['python', 'excel', 'sql', 'javascript']):
            recommendations.append("Add specific technical skills mentioned in job postings")
        
        return {
            'score': min(100, max(0, score)),
            'recommendations': recommendations,
            'strengths': strengths
        }
    
    def _analyze_format(self, resume_data: Dict[str, Any]) -> Dict:
        """Analyze resume format for ATS compatibility."""
        score = 70  # Base score
        recommendations = []
        strengths = []
        
        # Check for essential sections
        has_contact = bool(resume_data.get('contact_info'))
        has_experience = bool(resume_data.get('job_experiences'))
        has_education = bool(resume_data.get('education'))
        has_skills = bool(resume_data.get('skills'))
        
        section_score = sum([has_contact, has_experience, has_education, has_skills]) * 25
        score = min(100, score + (section_score - 70))
        
        if has_contact:
            strengths.append("Contact information present")
        else:
            recommendations.append("Add complete contact information")
        
        if has_experience:
            strengths.append("Work experience section included")
            
            # Check experience format
            experiences = resume_data.get('job_experiences', [])
            if experiences:
                first_exp = experiences[0]
                if hasattr(first_exp, 'description') and first_exp.description:
                    if len(first_exp.description) >= 2:
                        strengths.append("Good experience detail level")
                    else:
                        recommendations.append("Add more bullet points per job (3-5 recommended)")
        else:
            recommendations.append("Add work experience section")
        
        if has_skills:
            skills = resume_data.get('skills', [])
            if len(skills) >= 2:
                strengths.append("Multiple skill categories")
            else:
                recommendations.append("Organize skills into categories (Technical, Soft Skills, etc.)")
        
        # Check for professional summary
        if resume_data.get('professional_summary'):
            strengths.append("Professional summary included")
            if len(resume_data['professional_summary']) > 200:
                recommendations.append("Keep summary concise (2-3 lines)")
        else:
            recommendations.append("Add professional summary at the top")
        
        return {
            'score': min(100, max(0, score)),
            'recommendations': recommendations,
            'strengths': strengths
        }
    
    def _analyze_content(self, resume_data: Dict[str, Any]) -> Dict:
        """Analyze content quality."""
        score = 60  # Base score
        recommendations = []
        strengths = []
        warnings = []
        
        # Analyze experience descriptions
        experiences = resume_data.get('job_experiences', [])
        if experiences:
            total_bullets = 0
            action_words = 0
            quantified = 0
            
            action_verbs = [
                'achieved', 'developed', 'implemented', 'managed', 'led', 'created',
                'improved', 'increased', 'decreased', 'optimized', 'delivered',
                'coordinated', 'supervised', 'designed', 'built'
            ]
            
            for exp in experiences:
                if hasattr(exp, 'description') and exp.description:
                    descriptions = exp.description if isinstance(exp.description, list) else [exp.description]
                    total_bullets += len(descriptions)
                    
                    for desc in descriptions:
                        desc_lower = desc.lower()
                        
                        # Check for action verbs
                        if any(verb in desc_lower for verb in action_verbs):
                            action_words += 1
                        
                        # Check for quantification
                        if re.search(r'\d+[%$\w]*', desc):
                            quantified += 1
            
            if total_bullets > 0:
                action_ratio = action_words / total_bullets
                quant_ratio = quantified / total_bullets
                
                score += int(action_ratio * 20)
                score += int(quant_ratio * 20)
                
                if action_ratio > 0.7:
                    strengths.append("Strong use of action verbs")
                elif action_ratio < 0.3:
                    recommendations.append("Start bullet points with strong action verbs")
                
                if quant_ratio > 0.5:
                    strengths.append("Good quantification of achievements")
                elif quant_ratio < 0.2:
                    recommendations.append("Add numbers/metrics to show impact (%, $, time saved)")
        
        # Check for employment gaps
        if experiences and len(experiences) > 1:
            sorted_exp = sorted(experiences, key=lambda x: getattr(x, 'start_date', '') or '', reverse=True)
            for i in range(len(sorted_exp) - 1):
                current_end = getattr(sorted_exp[i], 'end_date', '')
                next_start = getattr(sorted_exp[i + 1], 'start_date', '')
                
                if current_end and next_start and current_end.lower() not in ['present', 'current']:
                    # Simple gap detection (could be improved with proper date parsing)
                    warnings.append("Check for employment gaps - consider explanations")
                    break
        
        # Check resume length (estimated)
        total_text = self._extract_resume_text(resume_data)
        word_count = len(total_text.split())
        
        if word_count < 150:
            recommendations.append("Resume appears too brief - add more detail")
        elif word_count > 800:
            warnings.append("Resume might be too long - consider condensing")
        else:
            strengths.append("Good resume length")
        
        return {
            'score': min(100, max(0, score)),
            'recommendations': recommendations,
            'strengths': strengths,
            'warnings': warnings
        }
    
    def _analyze_readability(self, resume_data: Dict[str, Any]) -> Dict:
        """Analyze readability and clarity."""
        score = 75  # Base score
        recommendations = []
        
        text = self._extract_resume_text(resume_data)
        
        # Simple readability metrics
        sentences = text.split('.')
        words = text.split()
        
        if len(words) > 0:
            avg_words_per_sentence = len(words) / max(len(sentences), 1)
            
            if avg_words_per_sentence > 25:
                score -= 10
                recommendations.append("Use shorter sentences for better readability")
            elif avg_words_per_sentence < 10:
                score += 10
        
        # Check for common issues
        if text.count(',') / len(words) > 0.1:
            recommendations.append("Simplify complex sentences")
        
        # Check for passive voice (simple detection)
        passive_indicators = ['was', 'were', 'been', 'being']
        passive_count = sum(text.lower().count(word) for word in passive_indicators)
        
        if passive_count > len(words) * 0.05:
            recommendations.append("Use active voice instead of passive voice")
        
        return {
            'score': min(100, max(0, score)),
            'recommendations': recommendations
        }
    
    def _extract_resume_text(self, resume_data: Dict[str, Any]) -> str:
        """Extract all text from resume data."""
        text_parts = []
        
        # Professional summary
        if resume_data.get('professional_summary'):
            text_parts.append(resume_data['professional_summary'])
        
        # Experience descriptions
        experiences = resume_data.get('job_experiences', [])
        for exp in experiences:
            if hasattr(exp, 'description') and exp.description:
                if isinstance(exp.description, list):
                    text_parts.extend(exp.description)
                else:
                    text_parts.append(exp.description)
        
        # Skills
        skills = resume_data.get('skills', [])
        for skill_cat in skills:
            if hasattr(skill_cat, 'skills'):
                text_parts.extend(skill_cat.skills)
            elif isinstance(skill_cat, dict) and 'skills' in skill_cat:
                text_parts.extend(skill_cat['skills'])
        
        return ' '.join(text_parts)
    
    def _extract_keywords_from_job(self, job_description: str) -> List[str]:
        """Extract relevant keywords from job description."""
        # Simple keyword extraction - could be enhanced with NLP
        common_tech_terms = [
            'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
            'sql', 'nosql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure',
            'docker', 'kubernetes', 'git', 'agile', 'scrum', 'rest', 'api',
            'machine learning', 'ai', 'data science', 'analytics', 'tableau',
            'power bi', 'excel', 'leadership', 'management', 'communication'
        ]
        
        found_keywords = []
        job_lower = job_description.lower()
        
        for term in common_tech_terms:
            if term in job_lower:
                found_keywords.append(term)
        
        # Extract requirements section keywords
        requirements_match = re.search(r'(requirements?|qualifications?|skills?):?\s*([^:]*?)(?=\n\n|\Z)', 
                                     job_description, re.IGNORECASE | re.DOTALL)
        
        if requirements_match:
            requirements_text = requirements_match.group(2)
            # Extract words that look like skills/technologies
            skill_words = re.findall(r'\b[A-Za-z][A-Za-z0-9\.\+\-]{2,}\b', requirements_text)
            found_keywords.extend([word.lower() for word in skill_words[:10]])
        
        return list(set(found_keywords))  # Remove duplicates
    
    def _detect_field(self, resume_text: str) -> Optional[str]:
        """Detect the likely field/industry from resume text."""
        field_scores = {}
        
        for field, keywords in self.common_keywords.items():
            score = sum(1 for keyword in keywords if keyword in resume_text)
            field_scores[field] = score
        
        if field_scores:
            detected_field = max(field_scores, key=field_scores.get)
            if field_scores[detected_field] > 2:  # Minimum threshold
                return detected_field
        
        return None

def display_ats_score_dashboard(ats_score: ATSScore):
    """Display ATS score dashboard in Streamlit."""
    
    st.markdown("### 🎯 ATS Compatibility Score")
    
    # Overall score with color coding
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        score_color = "🟢" if ats_score.overall_score >= 80 else "🟡" if ats_score.overall_score >= 60 else "🔴"
        st.metric(
            "Overall Score", 
            f"{ats_score.overall_score}/100",
            delta=None,
            help="Your resume's ATS compatibility score"
        )
        st.markdown(f"{score_color} **{get_score_label(ats_score.overall_score)}**")
    
    with col2:
        st.metric("Keywords", f"{ats_score.keyword_score}/100", help="Keyword optimization score")
    
    with col3:
        st.metric("Format", f"{ats_score.format_score}/100", help="ATS-friendly formatting score")
    
    with col4:
        st.metric("Content", f"{ats_score.content_score}/100", help="Content quality score")
    
    # Detailed breakdown
    col1, col2 = st.columns(2)
    
    with col1:
        if ats_score.strengths:
            st.markdown("#### ✅ **Strengths**")
            for strength in ats_score.strengths:
                st.markdown(f"• {strength}")
    
    with col2:
        if ats_score.warnings:
            st.markdown("#### ⚠️ **Areas to Review**")
            for warning in ats_score.warnings:
                st.markdown(f"• {warning}")
    
    # Recommendations
    if ats_score.recommendations:
        st.markdown("#### 🚀 **Improvement Recommendations**")
        
        for i, rec in enumerate(ats_score.recommendations, 1):
            st.markdown(f"{i}. {rec}")
    
    # Score interpretation
    with st.expander("📊 How to Interpret Your Score"):
        st.markdown("""
        **Score Ranges:**
        - 🟢 **80-100**: Excellent ATS compatibility
        - 🟡 **60-79**: Good, with room for improvement  
        - 🔴 **Below 60**: Needs significant optimization
        
        **What This Means:**
        - Higher scores indicate better ATS compatibility
        - Focus on red-flagged areas first
        - Even small improvements can boost your score significantly
        """)

def get_score_label(score: int) -> str:
    """Get descriptive label for ATS score."""
    if score >= 80:
        return "Excellent"
    elif score >= 70:
        return "Very Good"
    elif score >= 60:
        return "Good"
    elif score >= 50:
        return "Fair"
    else:
        return "Needs Work"