#!/usr/bin/env python3
"""
Professional Resume Templates
Modern, ATS-friendly resume templates for various industries and roles.
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class TemplateInfo:
    """Information about a resume template."""
    id: str
    name: str
    description: str
    category: str
    industry: List[str]
    ats_friendly: bool
    preview_url: str = ""

class ProfessionalTemplates:
    """Collection of professional resume templates optimized for ATS and modern hiring."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize the collection of professional templates."""
        return {
            "modern_corporate": {
                "info": TemplateInfo(
                    id="modern_corporate",
                    name="Modern Corporate",
                    description="Clean, professional template perfect for corporate positions and traditional industries",
                    category="corporate",
                    industry=["Finance", "Consulting", "Law", "Healthcare", "Insurance"],
                    ats_friendly=True
                ),
                "html": self._modern_corporate_template(),
                "css": self._modern_corporate_css()
            },
            
            "tech_minimal": {
                "info": TemplateInfo(
                    id="tech_minimal",
                    name="Tech Minimal",
                    description="Minimalist design emphasizing technical skills and projects, ideal for software engineers",
                    category="tech",
                    industry=["Software Engineering", "Data Science", "DevOps", "Cybersecurity"],
                    ats_friendly=True
                ),
                "html": self._tech_minimal_template(),
                "css": self._tech_minimal_css()
            },
            
            "executive_premium": {
                "info": TemplateInfo(
                    id="executive_premium",
                    name="Executive Premium",
                    description="Sophisticated layout for senior-level positions and executives",
                    category="executive",
                    industry=["Executive", "Management", "Strategy", "Operations"],
                    ats_friendly=True
                ),
                "html": self._executive_premium_template(),
                "css": self._executive_premium_css()
            },
            
            "creative_professional": {
                "info": TemplateInfo(
                    id="creative_professional",
                    name="Creative Professional",
                    description="Balance of creativity and professionalism for design and creative roles",
                    category="creative",
                    industry=["Design", "Marketing", "Media", "Creative"],
                    ats_friendly=True
                ),
                "html": self._creative_professional_template(),
                "css": self._creative_professional_css()
            },
            
            "faang_optimized": {
                "info": TemplateInfo(
                    id="faang_optimized",
                    name="Tech Elite",
                    description="Precision-focused layout with emphasis on achievements and quantifiable results, optimized for competitive environments",
                    category="tech",
                    industry=["Software Engineering", "Product Management", "Data Science"],
                    ats_friendly=True
                ),
                "html": self._faang_optimized_template(),
                "css": self._faang_optimized_css()
            },
            
            "consulting_classic": {
                "info": TemplateInfo(
                    id="consulting_classic",
                    name="Consulting Classic",
                    description="Traditional, results-focused template for consulting and strategy roles",
                    category="consulting",
                    industry=["Consulting", "Strategy", "Business Analysis", "Finance"],
                    ats_friendly=True
                ),
                "html": self._consulting_classic_template(),
                "css": self._consulting_classic_css()
            },
            
            "healthcare_professional": {
                "info": TemplateInfo(
                    id="healthcare_professional",
                    name="Healthcare Professional",
                    description="Clean, trustworthy design for healthcare and medical professionals",
                    category="healthcare",
                    industry=["Healthcare", "Medical", "Nursing", "Research"],
                    ats_friendly=True
                ),
                "html": self._healthcare_professional_template(),
                "css": self._healthcare_professional_css()
            },
            
            "academic_research": {
                "info": TemplateInfo(
                    id="academic_research",
                    name="Academic Research",
                    description="Comprehensive layout for academic positions and research roles",
                    category="academic",
                    industry=["Academia", "Research", "Education", "Science"],
                    ats_friendly=True
                ),
                "html": self._academic_research_template(),
                "css": self._academic_research_css()
            },
            
            "startup_dynamic": {
                "info": TemplateInfo(
                    id="startup_dynamic",
                    name="Startup Dynamic",
                    description="Modern, flexible template for startup environments and growth roles",
                    category="startup",
                    industry=["Startups", "Product", "Growth", "Marketing"],
                    ats_friendly=True
                ),
                "html": self._startup_dynamic_template(),
                "css": self._startup_dynamic_css()
            },
            
            "sales_results": {
                "info": TemplateInfo(
                    id="sales_results",
                    name="Sales Results",
                    description="Impact-focused template highlighting achievements and metrics for sales professionals",
                    category="sales",
                    industry=["Sales", "Business Development", "Account Management"],
                    ats_friendly=True
                ),
                "html": self._sales_results_template(),
                "css": self._sales_results_css()
            }
        }
    
    def get_template_by_id(self, template_id: str) -> Dict:
        """Get a specific template by ID."""
        return self.templates.get(template_id, {})
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all templates in a specific category."""
        return {k: v for k, v in self.templates.items() 
                if v.get("info", {}).category == category}
    
    def get_templates_by_industry(self, industry: str) -> Dict[str, Dict]:
        """Get templates suitable for a specific industry."""
        return {k: v for k, v in self.templates.items() 
                if industry in v.get("info", {}).industry}
    
    def get_all_templates(self) -> Dict[str, Dict]:
        """Get all available templates."""
        return self.templates
    
    def get_template_info_list(self) -> List[TemplateInfo]:
        """Get list of all template information."""
        return [template["info"] for template in self.templates.values()]
    
    # Template HTML structures (placeholder implementations)
    def _modern_corporate_template(self) -> str:
        return """
<div class="resume-container">
    <header class="resume-header">
        <h1 class="name">{{NAME}}</h1>
        <div class="contact-info">
            <span class="email">{{EMAIL}}</span>
            <span class="phone">{{PHONE}}</span>
            <span class="location">{{LOCATION}}</span>
            <span class="linkedin">{{LINKEDIN}}</span>
        </div>
    </header>
    
    <section class="professional-summary">
        <h2>Professional Summary</h2>
        <p class="summary-text">{{PROFESSIONAL_SUMMARY}}</p>
    </section>
    
    <section class="experience">
        <h2>Professional Experience</h2>
        {{WORK_EXPERIENCE}}
    </section>
    
    <section class="education">
        <h2>Education</h2>
        {{EDUCATION}}
    </section>
    
    <section class="skills">
        <h2>Core Competencies</h2>
        {{SKILLS}}
    </section>
    
    <section class="projects">
        <h2>Key Projects</h2>
        {{PROJECTS}}
    </section>
</div>
        """.strip()
    
    def _modern_corporate_css(self) -> str:
        return """
/* Modern Corporate Template CSS */
.resume-container {
    max-width: 800px;
    margin: 0 auto;
    padding: 40px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: white;
}

.resume-header {
    text-align: center;
    margin-bottom: 30px;
    padding-bottom: 20px;
    border-bottom: 2px solid #2c5aa0;
}

.name {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 15px 0;
    color: #2c5aa0;
    letter-spacing: 1px;
}

.contact-info {
    display: flex;
    justify-content: center;
    flex-wrap: wrap;
    gap: 20px;
    font-size: 14px;
    color: #666;
}

.contact-info span {
    display: flex;
    align-items: center;
}

section {
    margin-bottom: 25px;
}

section h2 {
    font-size: 18px;
    font-weight: 600;
    color: #2c5aa0;
    margin-bottom: 15px;
    padding-bottom: 5px;
    border-bottom: 1px solid #e0e0e0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.professional-summary p {
    font-size: 15px;
    line-height: 1.7;
    color: #555;
    margin: 0;
}

.experience-item {
    margin-bottom: 20px;
    padding-left: 0;
}

.job-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 5px;
}

.job-title {
    font-weight: 600;
    font-size: 16px;
    color: #333;
}

.company {
    font-weight: 500;
    color: #2c5aa0;
}

.date-location {
    font-size: 14px;
    color: #666;
    text-align: right;
}

.job-description {
    margin-top: 8px;
}

.job-description ul {
    margin: 0;
    padding-left: 20px;
}

.job-description li {
    margin-bottom: 3px;
    font-size: 14px;
    line-height: 1.5;
}

.skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
}

.skill-category {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 5px;
    border-left: 4px solid #2c5aa0;
}

.skill-category h3 {
    font-size: 14px;
    font-weight: 600;
    margin: 0 0 8px 0;
    color: #333;
}

.skill-list {
    font-size: 13px;
    color: #666;
    margin: 0;
}

/* Print optimization */
@media print {
    .resume-container {
        padding: 0;
        box-shadow: none;
        max-width: none;
        margin: 0;
        background: white;
    }
    
    .resume-header {
        page-break-inside: avoid;
    }
    
    section {
        page-break-inside: avoid;
    }
}

/* ATS Optimization */
h1, h2, h3, h4, h5, h6 {
    font-family: inherit;
}

/* Responsive design */
@media (max-width: 768px) {
    .resume-container {
        padding: 20px;
    }
    
    .name {
        font-size: 28px;
    }
    
    .contact-info {
        flex-direction: column;
        gap: 10px;
    }
    
    .job-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .date-location {
        text-align: left;
        margin-top: 5px;
    }
    
    .skills-grid {
        grid-template-columns: 1fr;
    }
}
        """.strip()
    
    def _tech_minimal_template(self) -> str:
        return """
<div class="resume-container">
    <header class="resume-header">
        <div class="header-content">
            <h1 class="name">{{NAME}}</h1>
            <div class="title">{{JOB_TITLE}}</div>
        </div>
        <div class="contact-links">
            <a href="mailto:{{EMAIL}}" class="contact-link">{{EMAIL}}</a>
            <a href="{{LINKEDIN}}" class="contact-link">LinkedIn</a>
            <a href="{{GITHUB}}" class="contact-link">GitHub</a>
            <span class="location">{{LOCATION}}</span>
        </div>
    </header>
    
    <section class="summary">
        <p>{{PROFESSIONAL_SUMMARY}}</p>
    </section>
    
    <section class="technical-skills">
        <h2>Technical Skills</h2>
        {{TECHNICAL_SKILLS}}
    </section>
    
    <section class="experience">
        <h2>Experience</h2>
        {{WORK_EXPERIENCE}}
    </section>
    
    <section class="projects">
        <h2>Projects</h2>
        {{PROJECTS}}
    </section>
    
    <section class="education">
        <h2>Education</h2>
        {{EDUCATION}}
    </section>
</div>
        """.strip()
    
    def _tech_minimal_css(self) -> str:
        return """
/* Tech Minimal Template CSS */
.resume-container {
    max-width: 900px;
    margin: 0 auto;
    padding: 50px 40px;
    font-family: 'SF Pro Text', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #1a1a1a;
    background: white;
}

.resume-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 40px;
    padding-bottom: 25px;
    border-bottom: 1px solid #e1e1e1;
}

.header-content {
    flex: 1;
}

.name {
    font-size: 36px;
    font-weight: 700;
    margin: 0 0 5px 0;
    color: #000;
    letter-spacing: -0.5px;
}

.title {
    font-size: 16px;
    color: #666;
    font-weight: 400;
}

.contact-links {
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 8px;
}

.contact-link {
    color: #0066cc;
    text-decoration: none;
    font-size: 14px;
    transition: color 0.2s;
}

.contact-link:hover {
    color: #0052a3;
}

.location {
    font-size: 14px;
    color: #666;
}

section {
    margin-bottom: 30px;
}

h2 {
    font-size: 18px;
    font-weight: 600;
    color: #000;
    margin: 0 0 20px 0;
    text-transform: none;
    letter-spacing: -0.2px;
}

.summary p {
    font-size: 16px;
    line-height: 1.7;
    color: #333;
    margin: 0;
}

.tech-skills-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.skill-group {
    padding: 0;
}

.skill-group h3 {
    font-size: 14px;
    font-weight: 600;
    color: #000;
    margin: 0 0 10px 0;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.skill-tag {
    background: #f5f5f5;
    padding: 4px 12px;
    border-radius: 12px;
    font-size: 13px;
    color: #333;
    border: 1px solid #e1e1e1;
}

.experience-item {
    margin-bottom: 25px;
}

.job-header {
    margin-bottom: 8px;
}

.job-title-company {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 2px;
}

.job-title {
    font-size: 16px;
    font-weight: 600;
    color: #000;
}

.job-date {
    font-size: 14px;
    color: #666;
}

.company {
    font-size: 15px;
    color: #666;
    font-weight: 400;
}

.job-description ul {
    margin: 0;
    padding-left: 0;
    list-style: none;
}

.job-description li {
    position: relative;
    padding-left: 15px;
    margin-bottom: 4px;
    font-size: 14px;
    line-height: 1.6;
    color: #333;
}

.job-description li::before {
    content: '•';
    position: absolute;
    left: 0;
    color: #666;
}

.project-item {
    margin-bottom: 20px;
    padding: 20px;
    background: #f9f9f9;
    border-radius: 8px;
    border-left: 4px solid #0066cc;
}

.project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
}

.project-title {
    font-size: 16px;
    font-weight: 600;
    color: #000;
}

.project-link {
    font-size: 13px;
    color: #0066cc;
    text-decoration: none;
}

.project-tech {
    font-size: 13px;
    color: #666;
    margin-bottom: 8px;
}

.project-description {
    font-size: 14px;
    line-height: 1.6;
    color: #333;
    margin: 0;
}

/* Print optimization */
@media print {
    .resume-container {
        padding: 0;
        max-width: none;
        margin: 0;
    }
    
    .contact-link {
        color: #000 !important;
    }
    
    .project-item {
        background: white;
        border: 1px solid #ddd;
    }
}

/* Responsive design */
@media (max-width: 768px) {
    .resume-container {
        padding: 30px 20px;
    }
    
    .resume-header {
        flex-direction: column;
        gap: 20px;
    }
    
    .contact-links {
        align-items: flex-start;
    }
    
    .job-title-company {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .project-header {
        flex-direction: column;
        align-items: flex-start;
    }
}
        """.strip()
    
    # Placeholder implementations for other templates
    def _executive_premium_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _executive_premium_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder
    
    def _creative_professional_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _creative_professional_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder
    
    def _faang_optimized_template(self) -> str:
        return self._tech_minimal_template()  # Placeholder
    
    def _faang_optimized_css(self) -> str:
        return self._tech_minimal_css()  # Placeholder
    
    def _consulting_classic_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _consulting_classic_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder
    
    def _healthcare_professional_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _healthcare_professional_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder
    
    def _academic_research_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _academic_research_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder
    
    def _startup_dynamic_template(self) -> str:
        return self._tech_minimal_template()  # Placeholder
    
    def _startup_dynamic_css(self) -> str:
        return self._tech_minimal_css()  # Placeholder
    
    def _sales_results_template(self) -> str:
        return self._modern_corporate_template()  # Placeholder
    
    def _sales_results_css(self) -> str:
        return self._modern_corporate_css()  # Placeholder

# Global instance for easy import
professional_templates = ProfessionalTemplates()