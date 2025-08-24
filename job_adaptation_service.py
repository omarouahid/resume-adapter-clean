"""
Job Adaptation Service - Adapts resumes to specific job descriptions
"""

import json
import re
from typing import Dict, List, Tuple
from openrouter_client import OpenRouterClient

class JobAdaptationService:
    """Service for adapting resumes to specific job descriptions."""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
    
    def adapt_resume_to_job(self, latex_content: str, job_description: str, 
                           adaptation_level: str = "moderate") -> Dict:
        """
        Adapt a resume to match a specific job description.
        
        Args:
            latex_content: Original resume LaTeX
            job_description: Target job description
            adaptation_level: "light", "moderate", or "aggressive"
        
        Returns:
            Dict with adapted LaTeX and analysis
        """
        
        # Analyze the job description
        job_analysis = self._analyze_job_description(job_description)
        
        # Generate adaptation prompt
        prompt = self._create_adaptation_prompt(
            latex_content, job_description, job_analysis, adaptation_level
        )
        
        # Get AI adaptation
        try:
            adapted_latex = self.client._make_request(prompt, max_tokens=4000)
            
            # Clean up response
            if adapted_latex.startswith("```latex"):
                adapted_latex = adapted_latex.replace("```latex", "").replace("```", "").strip()
            
            return {
                "adapted_latex": adapted_latex,
                "job_analysis": job_analysis,
                "adaptation_summary": self._generate_adaptation_summary(job_analysis),
                "success": True
            }
            
        except Exception as e:
            return {
                "adapted_latex": latex_content,
                "job_analysis": job_analysis,
                "error": str(e),
                "success": False
            }
    
    def _analyze_job_description(self, job_description: str) -> Dict:
        """Analyze job description to extract key requirements."""
        
        analysis = {
            "key_skills": [],
            "technologies": [],
            "experience_level": "mid",
            "industry": "technology",
            "role_type": "technical",
            "company_size": "unknown",
            "keywords": []
        }
        
        text_lower = job_description.lower()
        
        # Extract technologies
        tech_patterns = [
            r'\b(python|java|javascript|typescript|react|angular|vue|node\.?js|express)\b',
            r'\b(sql|mysql|postgresql|mongodb|redis|elasticsearch)\b',
            r'\b(aws|azure|gcp|docker|kubernetes|jenkins|git)\b',
            r'\b(machine learning|ai|data science|analytics|pandas|numpy)\b',
            r'\b(html|css|sass|less|bootstrap|tailwind)\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text_lower)
            analysis["technologies"].extend(matches)
        
        # Extract experience level
        if any(word in text_lower for word in ['senior', '5+ years', 'lead', 'principal']):
            analysis["experience_level"] = "senior"
        elif any(word in text_lower for word in ['junior', 'entry', '0-2 years', 'graduate']):
            analysis["experience_level"] = "junior"
        
        # Extract key skills
        skill_patterns = [
            r'(?:skills?|experience|proficiency).*?(?:in|with|of)\s*([^.!?]*)',
            r'(?:must have|required|essential).*?([^.!?]*)',
            r'(?:responsible for|duties include).*?([^.!?]*)'
        ]
        
        for pattern in skill_patterns:
            matches = re.findall(pattern, text_lower, re.IGNORECASE)
            for match in matches:
                skills = [s.strip() for s in match.split(',') if s.strip()]
                analysis["key_skills"].extend(skills[:3])  # Limit to avoid noise
        
        # Extract role type
        if any(word in text_lower for word in ['manager', 'lead', 'director', 'head']):
            analysis["role_type"] = "leadership"
        elif any(word in text_lower for word in ['engineer', 'developer', 'programmer']):
            analysis["role_type"] = "technical"
        elif any(word in text_lower for word in ['analyst', 'scientist', 'researcher']):
            analysis["role_type"] = "analytical"
        
        # Extract keywords for ATS optimization
        keywords = []
        lines = job_description.split('\n')
        for line in lines:
            if any(indicator in line.lower() for indicator in ['requirements', 'qualifications', 'skills', 'experience']):
                words = re.findall(r'\b[A-Za-z]+\b', line)
                keywords.extend([w for w in words if len(w) > 3])
        
        analysis["keywords"] = list(set(keywords[:20]))  # Top 20 unique keywords
        
        return analysis
    
    def _create_adaptation_prompt(self, latex_content: str, job_description: str, 
                                 job_analysis: Dict, adaptation_level: str) -> str:
        """Create prompt for resume adaptation."""
        
        level_instructions = {
            "light": "Make minimal changes, only emphasize relevant skills and experience",
            "moderate": "Adjust content to highlight relevant experience, add missing keywords, reorder sections if beneficial",
            "aggressive": "Significantly restructure content, add new relevant skills, modify descriptions to match job requirements"
        }
        
        return f"""
You are an expert resume writer and career coach. Adapt the following resume to better match the target job description.

ADAPTATION LEVEL: {adaptation_level.upper()}
INSTRUCTIONS: {level_instructions[adaptation_level]}

TARGET JOB DESCRIPTION:
{job_description}

JOB ANALYSIS:
- Key Skills Required: {', '.join(job_analysis['key_skills'][:5])}
- Technologies: {', '.join(job_analysis['technologies'][:10])}
- Experience Level: {job_analysis['experience_level']}
- Role Type: {job_analysis['role_type']}
- ATS Keywords: {', '.join(job_analysis['keywords'][:10])}

CURRENT RESUME (LaTeX):
{latex_content}

Please adapt the resume to:
1. Emphasize relevant experience and skills
2. Include important keywords naturally
3. Adjust section ordering if beneficial
4. Modify descriptions to match job requirements
5. Maintain professional formatting and AltaCV structure
6. Ensure ATS compatibility

Return ONLY the adapted LaTeX code, no explanations.
"""
    
    def _generate_adaptation_summary(self, job_analysis: Dict) -> str:
        """Generate a summary of the adaptation changes."""
        return f"""
Resume adapted for {job_analysis['role_type']} role at {job_analysis['experience_level']} level.

Key adaptations:
• Emphasized {len(job_analysis['technologies'])} relevant technologies
• Highlighted {len(job_analysis['key_skills'])} key skills
• Optimized for {len(job_analysis['keywords'])} ATS keywords
• Adjusted for {job_analysis['experience_level']} experience level
"""

class ResumeImprovementService:
    """Service for general resume improvements and suggestions."""
    
    def __init__(self, openrouter_client: OpenRouterClient):
        self.client = openrouter_client
    
    def analyze_and_improve(self, latex_content: str, analysis_data: Dict) -> Dict:
        """Analyze resume and provide detailed improvements."""
        
        # Create analysis prompt
        prompt = f"""
You are an expert resume consultant. Analyze the following resume and provide detailed improvement suggestions.

RESUME ANALYSIS DATA:
{json.dumps(analysis_data, indent=2)}

CURRENT RESUME (LaTeX):
{latex_content}

Please provide:
1. OVERALL ASSESSMENT (1-10 score with reasoning)
2. STRUCTURE IMPROVEMENTS (section ordering, layout)
3. CONTENT IMPROVEMENTS (writing, achievements, keywords)
4. FORMATTING IMPROVEMENTS (design, readability)
5. ATS OPTIMIZATION suggestions
6. SPECIFIC ACTION ITEMS (prioritized list)

Format as JSON with these keys: overall_score, structure_feedback, content_feedback, formatting_feedback, ats_suggestions, action_items
"""
        
        try:
            response = self.client._make_request(prompt, max_tokens=3000)
            
            # Try to parse as JSON, fallback to text
            try:
                return json.loads(response)
            except:
                return {
                    "overall_feedback": response,
                    "success": True
                }
                
        except Exception as e:
            return {
                "error": str(e),
                "success": False
            }
    
    def improve_resume_content(self, resume_text: str) -> str:
        """Improve resume content with AI assistance."""
        improvement_prompt = f"""
Improve this resume content to make it more professional, impactful, and ATS-friendly.

Current Resume Content:
{resume_text}

Instructions:
1. Make bullet points more action-oriented and results-focused
2. Add quantifiable achievements where possible
3. Use stronger action verbs
4. Improve clarity and conciseness
5. Optimize for ATS scanning
6. Maintain all factual information accurately
7. Preserve the original language and structure
8. Focus on impact and achievements

Return the improved resume content in the same format:
"""
        
        try:
            improved_content = self.client._make_request(improvement_prompt, max_tokens=2000)
            return improved_content if improved_content else "Error: No response from AI"
        except Exception as e:
            return f"Error: {str(e)}"
    
    def generate_improved_version(self, latex_content: str, improvement_areas: List[str]) -> str:
        """Generate an improved version based on specific areas."""
        
        areas_text = ", ".join(improvement_areas)
        
        prompt = f"""
Improve the following resume focusing on: {areas_text}

CURRENT RESUME:
{latex_content}

Create an improved version that addresses the specified areas while maintaining the AltaCV structure.
Return ONLY the improved LaTeX code.
"""
        
        try:
            improved = self.client._make_request(prompt, max_tokens=4000)
            if improved.startswith("```latex"):
                improved = improved.replace("```latex", "").replace("```", "").strip()
            return improved
        except:
            return latex_content


