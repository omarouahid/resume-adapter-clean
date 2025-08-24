#!/usr/bin/env python3
"""
Freelancer Resume Templates
Specialized templates for freelancers, contractors, and gig workers.
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class FreelancerTemplateInfo:
    """Information about a freelancer resume template."""
    id: str
    name: str
    description: str
    category: str
    specialization: List[str]
    project_focused: bool
    portfolio_integrated: bool

class FreelancerTemplates:
    """Collection of resume templates specifically designed for freelancers and independent contractors."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize the collection of freelancer templates."""
        return {
            "portfolio_showcase": {
                "info": FreelancerTemplateInfo(
                    id="portfolio_showcase",
                    name="Portfolio Showcase",
                    description="Emphasizes portfolio projects with visual hierarchy and client results",
                    category="creative",
                    specialization=["Designer", "Developer", "Creative", "Writer"],
                    project_focused=True,
                    portfolio_integrated=True
                ),
                "html": self._portfolio_showcase_template(),
                "css": self._portfolio_showcase_css()
            },
            
            "client_results": {
                "info": FreelancerTemplateInfo(
                    id="client_results",
                    name="Impact Metrics",
                    description="Results-driven layout with emphasis on testimonials, outcomes, and measurable client impacts",
                    category="results",
                    specialization=["Consultant", "Marketer", "Business", "Sales"],
                    project_focused=True,
                    portfolio_integrated=False
                ),
                "html": self._client_results_template(),
                "css": self._client_results_css()
            },
            
            "technical_contractor": {
                "info": FreelancerTemplateInfo(
                    id="technical_contractor",
                    name="Tech Portfolio",
                    description="Code-focused layout with technical project showcases and skill demonstrations",
                    category="technical",
                    specialization=["Developer", "Engineer", "DevOps", "Data Scientist"],
                    project_focused=True,
                    portfolio_integrated=True
                ),
                "html": self._technical_contractor_template(),
                "css": self._technical_contractor_css()
            },
            
            "multi_discipline": {
                "info": FreelancerTemplateInfo(
                    id="multi_discipline",
                    name="Versatile Professional",
                    description="Flexible layout accommodating diverse skill sets with organized sections for multiple specializations",
                    category="versatile",
                    specialization=["Multi-skill", "Virtual Assistant", "General"],
                    project_focused=True,
                    portfolio_integrated=False
                ),
                "html": self._multi_discipline_template(),
                "css": self._multi_discipline_css()
            },
            
            "consulting_expert": {
                "info": FreelancerTemplateInfo(
                    id="consulting_expert",
                    name="Consulting Expert",
                    description="Authority-focused template for independent consultants and subject matter experts",
                    category="consulting",
                    specialization=["Consultant", "Expert", "Advisor", "Strategist"],
                    project_focused=True,
                    portfolio_integrated=False
                ),
                "html": self._consulting_expert_template(),
                "css": self._consulting_expert_css()
            },
            
            "creative_studio": {
                "info": FreelancerTemplateInfo(
                    id="creative_studio",
                    name="Creative Studio",
                    description="Artistic yet professional template for creative professionals",
                    category="creative",
                    specialization=["Designer", "Artist", "Creative Director", "Photographer"],
                    project_focused=True,
                    portfolio_integrated=True
                ),
                "html": self._creative_studio_template(),
                "css": self._creative_studio_css()
            }
        }
    
    def get_template_by_id(self, template_id: str) -> Dict:
        """Get a specific template by ID."""
        return self.templates.get(template_id, {})
    
    def get_templates_by_category(self, category: str) -> Dict[str, Dict]:
        """Get all templates in a specific category."""
        return {k: v for k, v in self.templates.items() 
                if v.get("info", {}).category == category}
    
    def get_templates_by_specialization(self, specialization: str) -> Dict[str, Dict]:
        """Get templates suitable for a specific specialization."""
        return {k: v for k, v in self.templates.items() 
                if specialization in v.get("info", {}).specialization}
    
    def get_all_templates(self) -> Dict[str, Dict]:
        """Get all available templates."""
        return self.templates
    
    def get_template_info_list(self) -> List[FreelancerTemplateInfo]:
        """Get list of all template information."""
        return [template["info"] for template in self.templates.values()]
    
    def _portfolio_showcase_template(self) -> str:
        return """
<div class="freelancer-resume">
    <header class="header-section">
        <div class="hero-content">
            <h1 class="freelancer-name">{{NAME}}</h1>
            <h2 class="freelancer-title">{{PROFESSIONAL_TITLE}}</h2>
            <p class="freelancer-tagline">{{TAGLINE}}</p>
        </div>
        <div class="contact-card">
            <div class="contact-item">
                <span class="label">Email:</span>
                <span class="value">{{EMAIL}}</span>
            </div>
            <div class="contact-item">
                <span class="label">Portfolio:</span>
                <span class="value">{{PORTFOLIO_URL}}</span>
            </div>
            <div class="contact-item">
                <span class="label">Location:</span>
                <span class="value">{{LOCATION}}</span>
            </div>
            <div class="contact-item">
                <span class="label">Available:</span>
                <span class="value">{{AVAILABILITY}}</span>
            </div>
        </div>
    </header>
    
    <section class="about-section">
        <h3>About</h3>
        <p>{{PROFESSIONAL_SUMMARY}}</p>
    </section>
    
    <section class="services-section">
        <h3>Services & Expertise</h3>
        <div class="services-grid">
            {{SERVICES}}
        </div>
    </section>
    
    <section class="portfolio-section">
        <h3>Featured Projects</h3>
        <div class="portfolio-grid">
            {{PROJECTS}}
        </div>
    </section>
    
    <section class="client-section">
        <h3>Client Experience</h3>
        <div class="client-timeline">
            {{CLIENT_WORK}}
        </div>
    </section>
    
    <section class="skills-section">
        <h3>Technical Skills</h3>
        <div class="skills-categories">
            {{SKILLS}}
        </div>
    </section>
    
    <section class="testimonials-section">
        <h3>Client Testimonials</h3>
        <div class="testimonials">
            {{TESTIMONIALS}}
        </div>
    </section>
    
    <section class="credentials-section">
        <h3>Education & Certifications</h3>
        {{EDUCATION_CERTIFICATIONS}}
    </section>
</div>
        """.strip()
    
    def _portfolio_showcase_css(self) -> str:
        return """
/* Portfolio Showcase Template CSS */
.freelancer-resume {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    line-height: 1.6;
    color: #2d3748;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.header-section {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 60px 40px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    min-height: 300px;
}

.hero-content {
    flex: 2;
    max-width: 60%;
}

.freelancer-name {
    font-size: 48px;
    font-weight: 700;
    margin: 0 0 10px 0;
    line-height: 1.1;
    letter-spacing: -1px;
}

.freelancer-title {
    font-size: 24px;
    font-weight: 300;
    margin: 0 0 15px 0;
    opacity: 0.9;
}

.freelancer-tagline {
    font-size: 18px;
    line-height: 1.6;
    opacity: 0.8;
    margin: 0;
    max-width: 500px;
}

.contact-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
    min-width: 280px;
}

.contact-item {
    display: flex;
    justify-content: space-between;
    margin-bottom: 12px;
    font-size: 14px;
}

.contact-item:last-child {
    margin-bottom: 0;
}

.label {
    font-weight: 600;
    opacity: 0.9;
}

.value {
    opacity: 0.8;
    text-align: right;
}

section {
    padding: 50px 40px;
    background: white;
}

section:nth-child(even) {
    background: #f8fafc;
}

h3 {
    font-size: 28px;
    font-weight: 700;
    margin: 0 0 30px 0;
    color: #1a202c;
    position: relative;
    padding-bottom: 15px;
}

h3::after {
    content: '';
    position: absolute;
    bottom: 0;
    left: 0;
    width: 60px;
    height: 3px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 2px;
}

.about-section p {
    font-size: 18px;
    line-height: 1.8;
    color: #4a5568;
    max-width: 800px;
}

.services-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 25px;
}

.service-card {
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    border: 1px solid #e2e8f0;
    transition: transform 0.2s, box-shadow 0.2s;
}

.service-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
}

.service-title {
    font-size: 18px;
    font-weight: 600;
    color: #1a202c;
    margin: 0 0 10px 0;
}

.service-description {
    font-size: 14px;
    color: #718096;
    line-height: 1.5;
}

.portfolio-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 30px;
}

.project-card {
    background: white;
    border-radius: 15px;
    overflow: hidden;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    transition: transform 0.3s, box-shadow 0.3s;
}

.project-card:hover {
    transform: translateY(-5px);
    box-shadow: 0 15px 35px rgba(0, 0, 0, 0.1);
}

.project-image {
    height: 200px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 14px;
    text-align: center;
}

.project-content {
    padding: 25px;
}

.project-title {
    font-size: 18px;
    font-weight: 600;
    margin: 0 0 10px 0;
    color: #1a202c;
}

.project-description {
    font-size: 14px;
    color: #718096;
    line-height: 1.6;
    margin-bottom: 15px;
}

.project-tech {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.tech-tag {
    background: #edf2f7;
    color: #4a5568;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12px;
    font-weight: 500;
}

.client-timeline {
    position: relative;
    padding-left: 30px;
}

.client-timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #667eea 0%, #764ba2 100%);
}

.client-item {
    position: relative;
    margin-bottom: 40px;
    background: white;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.client-item::before {
    content: '';
    position: absolute;
    left: -37px;
    top: 25px;
    width: 12px;
    height: 12px;
    background: #667eea;
    border-radius: 50%;
    border: 3px solid white;
    box-shadow: 0 0 0 2px #667eea;
}

.client-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 15px;
}

.client-role {
    font-size: 18px;
    font-weight: 600;
    color: #1a202c;
}

.client-company {
    font-size: 16px;
    color: #667eea;
    font-weight: 500;
}

.client-period {
    font-size: 14px;
    color: #718096;
}

.client-description {
    font-size: 14px;
    color: #4a5568;
    line-height: 1.6;
}

.skills-categories {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 30px;
}

.skill-category {
    background: white;
    padding: 25px;
    border-radius: 12px;
    border-left: 4px solid #667eea;
}

.skill-category h4 {
    font-size: 16px;
    font-weight: 600;
    color: #1a202c;
    margin: 0 0 15px 0;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.skill-tag {
    background: #edf2f7;
    color: #4a5568;
    padding: 6px 14px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}

.testimonials {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 30px;
}

.testimonial-card {
    background: white;
    padding: 30px;
    border-radius: 15px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    position: relative;
}

.testimonial-card::before {
    content: '"';
    font-size: 60px;
    color: #667eea;
    opacity: 0.3;
    position: absolute;
    top: 10px;
    left: 20px;
    line-height: 1;
}

.testimonial-text {
    font-size: 16px;
    line-height: 1.7;
    color: #4a5568;
    margin: 20px 0 20px 0;
    font-style: italic;
}

.testimonial-author {
    font-size: 14px;
    font-weight: 600;
    color: #1a202c;
    margin-bottom: 5px;
}

.testimonial-company {
    font-size: 13px;
    color: #718096;
}

.credentials-section {
    background: #1a202c !important;
    color: white;
}

.credentials-section h3 {
    color: white;
}

.credentials-section h3::after {
    background: white;
}

.education-item, .certification-item {
    background: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
}

.education-degree, .certification-name {
    font-size: 16px;
    font-weight: 600;
    margin-bottom: 5px;
}

.education-school, .certification-issuer {
    font-size: 14px;
    opacity: 0.8;
}

/* Responsive design */
@media (max-width: 768px) {
    .header-section {
        flex-direction: column;
        text-align: center;
        gap: 30px;
        padding: 40px 20px;
    }
    
    .hero-content {
        max-width: 100%;
    }
    
    .freelancer-name {
        font-size: 36px;
    }
    
    section {
        padding: 40px 20px;
    }
    
    .portfolio-grid, .services-grid {
        grid-template-columns: 1fr;
    }
    
    .client-timeline {
        padding-left: 0;
    }
    
    .client-timeline::before {
        display: none;
    }
    
    .client-item::before {
        display: none;
    }
    
    .client-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}

/* Print optimization */
@media print {
    .freelancer-resume {
        background: white !important;
    }
    
    .header-section {
        background: #f8fafc !important;
        color: #1a202c !important;
    }
    
    .credentials-section {
        background: #f8fafc !important;
        color: #1a202c !important;
    }
    
    .project-card, .service-card, .client-item, .testimonial-card {
        box-shadow: none !important;
        border: 1px solid #e2e8f0 !important;
    }
}
        """.strip()
    
    def _client_results_template(self) -> str:
        return """
<div class="results-resume">
    <header class="header">
        <div class="personal-info">
            <h1 class="name">{{NAME}}</h1>
            <h2 class="title">{{PROFESSIONAL_TITLE}}</h2>
            <div class="contact-info">
                <span>{{EMAIL}}</span> • 
                <span>{{PHONE}}</span> • 
                <span>{{LOCATION}}</span> • 
                <span>{{LINKEDIN}}</span>
            </div>
        </div>
        <div class="value-proposition">
            <h3>Value Delivered</h3>
            <div class="metrics">
                {{KEY_METRICS}}
            </div>
        </div>
    </header>
    
    <section class="executive-summary">
        <h3>Executive Summary</h3>
        <p>{{PROFESSIONAL_SUMMARY}}</p>
    </section>
    
    <section class="client-results">
        <h3>Client Results & Impact</h3>
        <div class="results-grid">
            {{CLIENT_RESULTS}}
        </div>
    </section>
    
    <section class="service-offerings">
        <h3>Service Offerings</h3>
        <div class="services-list">
            {{SERVICES}}
        </div>
    </section>
    
    <section class="experience-highlights">
        <h3>Selected Client Engagements</h3>
        {{CLIENT_ENGAGEMENTS}}
    </section>
    
    <section class="testimonials">
        <h3>Client Testimonials</h3>
        {{CLIENT_TESTIMONIALS}}
    </section>
    
    <section class="credentials">
        <div class="credentials-grid">
            <div class="education-column">
                <h4>Education</h4>
                {{EDUCATION}}
            </div>
            <div class="certifications-column">
                <h4>Certifications</h4>
                {{CERTIFICATIONS}}
            </div>
        </div>
    </section>
</div>
        """.strip()
    
    def _client_results_css(self) -> str:
        return """
/* Client Results Template CSS */
.results-resume {
    max-width: 900px;
    margin: 0 auto;
    padding: 40px;
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    line-height: 1.6;
    color: #333;
    background: white;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 40px;
    padding: 30px;
    background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
    color: white;
    border-radius: 10px;
}

.personal-info {
    flex: 2;
}

.name {
    font-size: 32px;
    font-weight: 700;
    margin: 0 0 8px 0;
    letter-spacing: -0.5px;
}

.title {
    font-size: 18px;
    font-weight: 400;
    margin: 0 0 15px 0;
    opacity: 0.9;
}

.contact-info {
    font-size: 14px;
    opacity: 0.8;
}

.value-proposition {
    flex: 1;
    text-align: right;
    background: rgba(255, 255, 255, 0.1);
    padding: 20px;
    border-radius: 8px;
    backdrop-filter: blur(10px);
}

.value-proposition h3 {
    font-size: 16px;
    font-weight: 600;
    margin: 0 0 15px 0;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

.metrics {
    display: flex;
    flex-direction: column;
    gap: 10px;
}

.metric-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 14px;
}

.metric-value {
    font-size: 20px;
    font-weight: 700;
    color: #fbbf24;
}

section {
    margin-bottom: 35px;
}

h3 {
    font-size: 22px;
    font-weight: 700;
    color: #1e3a8a;
    margin: 0 0 20px 0;
    padding-bottom: 10px;
    border-bottom: 2px solid #e5e7eb;
    position: relative;
}

h3::after {
    content: '';
    position: absolute;
    bottom: -2px;
    left: 0;
    width: 40px;
    height: 2px;
    background: #3b82f6;
}

.executive-summary p {
    font-size: 16px;
    line-height: 1.8;
    color: #4b5563;
}

.results-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 25px;
}

.result-card {
    background: #f9fafb;
    padding: 25px;
    border-radius: 10px;
    border-left: 4px solid #3b82f6;
    transition: transform 0.2s;
}

.result-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.result-title {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 10px 0;
}

.result-description {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.6;
    margin-bottom: 15px;
}

.result-metric {
    font-size: 24px;
    font-weight: 700;
    color: #3b82f6;
    margin: 0;
}

.services-list {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
}

.service-item {
    padding: 20px;
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    transition: border-color 0.2s;
}

.service-item:hover {
    border-color: #3b82f6;
}

.service-name {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 8px 0;
}

.service-description {
    font-size: 14px;
    color: #6b7280;
    line-height: 1.5;
}

.engagement-item {
    margin-bottom: 30px;
    padding: 25px;
    background: #f9fafb;
    border-radius: 10px;
}

.engagement-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 15px;
}

.engagement-title {
    font-size: 18px;
    font-weight: 600;
    color: #1f2937;
}

.engagement-client {
    font-size: 16px;
    color: #3b82f6;
    font-weight: 500;
}

.engagement-period {
    font-size: 14px;
    color: #6b7280;
}

.engagement-description {
    font-size: 14px;
    color: #4b5563;
    line-height: 1.6;
    margin-bottom: 15px;
}

.engagement-results {
    background: white;
    padding: 15px;
    border-radius: 6px;
    border-left: 3px solid #10b981;
}

.engagement-results h5 {
    font-size: 14px;
    font-weight: 600;
    color: #065f46;
    margin: 0 0 8px 0;
}

.engagement-results ul {
    margin: 0;
    padding-left: 20px;
    font-size: 14px;
    color: #047857;
}

.testimonial-item {
    background: white;
    padding: 25px;
    border-radius: 10px;
    border: 1px solid #e5e7eb;
    margin-bottom: 20px;
    position: relative;
}

.testimonial-item::before {
    content: '"';
    font-size: 40px;
    color: #3b82f6;
    opacity: 0.3;
    position: absolute;
    top: 15px;
    right: 20px;
}

.testimonial-text {
    font-size: 15px;
    line-height: 1.7;
    color: #4b5563;
    margin-bottom: 15px;
    font-style: italic;
}

.testimonial-author {
    font-size: 14px;
    font-weight: 600;
    color: #1f2937;
}

.testimonial-position {
    font-size: 13px;
    color: #6b7280;
}

.credentials-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
}

.credentials-grid h4 {
    font-size: 16px;
    font-weight: 600;
    color: #1f2937;
    margin: 0 0 15px 0;
    padding-bottom: 8px;
    border-bottom: 1px solid #e5e7eb;
}

.education-item, .certification-item {
    margin-bottom: 15px;
    font-size: 14px;
    color: #4b5563;
}

.degree-name, .cert-name {
    font-weight: 600;
    color: #1f2937;
}

.school-name, .cert-issuer {
    color: #6b7280;
}

/* Responsive design */
@media (max-width: 768px) {
    .results-resume {
        padding: 20px;
    }
    
    .header {
        flex-direction: column;
        gap: 20px;
    }
    
    .value-proposition {
        text-align: left;
    }
    
    .results-grid, .services-list {
        grid-template-columns: 1fr;
    }
    
    .engagement-header {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .credentials-grid {
        grid-template-columns: 1fr;
        gap: 25px;
    }
}

/* Print optimization */
@media print {
    .results-resume {
        padding: 0;
    }
    
    .header {
        background: #f3f4f6 !important;
        color: #1f2937 !important;
    }
    
    .result-card, .engagement-item {
        break-inside: avoid;
    }
}
        """.strip()
    
    # Placeholder implementations for other templates
    def _technical_contractor_template(self) -> str:
        return self._portfolio_showcase_template()  # Placeholder
    
    def _technical_contractor_css(self) -> str:
        return self._portfolio_showcase_css()  # Placeholder
    
    def _multi_discipline_template(self) -> str:
        return self._client_results_template()  # Placeholder
    
    def _multi_discipline_css(self) -> str:
        return self._client_results_css()  # Placeholder
    
    def _consulting_expert_template(self) -> str:
        return self._client_results_template()  # Placeholder
    
    def _consulting_expert_css(self) -> str:
        return self._client_results_css()  # Placeholder
    
    def _creative_studio_template(self) -> str:
        return self._portfolio_showcase_template()  # Placeholder
    
    def _creative_studio_css(self) -> str:
        return self._portfolio_showcase_css()  # Placeholder

# Global instance for easy import
freelancer_templates = FreelancerTemplates()