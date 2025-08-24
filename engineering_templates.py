#!/usr/bin/env python3
"""
Engineering Resume Templates
Specialized templates for IT engineers, software developers, and technical professionals.
"""

from typing import Dict, List
from dataclasses import dataclass

@dataclass
class EngineeringTemplateInfo:
    """Information about an engineering resume template."""
    id: str
    name: str
    description: str
    specialization: List[str]
    experience_level: str
    ats_optimized: bool
    github_integration: bool

class EngineeringTemplates:
    """Collection of resume templates specifically designed for IT engineers and technical professionals."""
    
    def __init__(self):
        self.templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[str, Dict]:
        """Initialize the collection of engineering templates."""
        return {
            "senior_software_engineer": {
                "info": EngineeringTemplateInfo(
                    id="senior_software_engineer",
                    name="Technical Authority",
                    description="Bold header with prominent skills section, ideal for showcasing technical leadership and architecture experience",
                    specialization=["Full-Stack", "Backend", "Frontend", "DevOps", "Architecture"],
                    experience_level="Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._senior_software_engineer_template(),
                "css": self._senior_software_engineer_css()
            },
            
            "fullstack_developer": {
                "info": EngineeringTemplateInfo(
                    id="fullstack_developer",
                    name="Balanced Portfolio",
                    description="Dual-column layout with equal emphasis on skills and projects, perfect for showcasing diverse technical abilities",
                    specialization=["Full-Stack", "React", "Node.js", "Python", "JavaScript"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._fullstack_developer_template(),
                "css": self._fullstack_developer_css()
            },
            
            "backend_engineer": {
                "info": EngineeringTemplateInfo(
                    id="backend_engineer",
                    name="System Architecture",
                    description="Technical-focused layout emphasizing system design and performance metrics with clean data presentation",
                    specialization=["Backend", "API", "Microservices", "Database", "System Design"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._backend_engineer_template(),
                "css": self._backend_engineer_css()
            },
            
            "devops_engineer": {
                "info": EngineeringTemplateInfo(
                    id="devops_engineer",
                    name="Infrastructure Grid",
                    description="Grid-based layout highlighting infrastructure achievements with organized sections for automation and cloud platforms",
                    specialization=["DevOps", "AWS", "Docker", "Kubernetes", "CI/CD", "Infrastructure"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._devops_engineer_template(),
                "css": self._devops_engineer_css()
            },
            
            "data_engineer": {
                "info": EngineeringTemplateInfo(
                    id="data_engineer",
                    name="Analytics Dashboard",
                    description="Data-visualization inspired layout with metric cards and progress indicators for technical achievements",
                    specialization=["Data Engineering", "ETL", "Big Data", "Spark", "Kafka", "Analytics"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._data_engineer_template(),
                "css": self._data_engineer_css()
            },
            
            "mobile_developer": {
                "info": EngineeringTemplateInfo(
                    id="mobile_developer",
                    name="App Interface",
                    description="Mobile-app inspired clean design with card-based sections and modern interface elements",
                    specialization=["Mobile", "iOS", "Android", "React Native", "Flutter", "Swift", "Kotlin"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._mobile_developer_template(),
                "css": self._mobile_developer_css()
            },
            
            "frontend_engineer": {
                "info": EngineeringTemplateInfo(
                    id="frontend_engineer",
                    name="Modern Interface",
                    description="Sleek, responsive design with visual hierarchy emphasizing user experience and modern web aesthetics",
                    specialization=["Frontend", "React", "Vue", "Angular", "UI/UX", "CSS", "JavaScript"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._frontend_engineer_template(),
                "css": self._frontend_engineer_css()
            },
            
            "security_engineer": {
                "info": EngineeringTemplateInfo(
                    id="security_engineer",
                    name="Shield Layout",
                    description="Professional template with security-focused sections and structured presentation of compliance achievements",
                    specialization=["Security", "Cybersecurity", "Penetration Testing", "Compliance", "Risk Assessment"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._security_engineer_template(),
                "css": self._security_engineer_css()
            },
            
            "ml_engineer": {
                "info": EngineeringTemplateInfo(
                    id="ml_engineer",
                    name="Research Publication",
                    description="Academic-inspired layout with sections for research papers, model metrics, and scientific project presentation",
                    specialization=["Machine Learning", "AI", "Deep Learning", "Python", "TensorFlow", "PyTorch"],
                    experience_level="Mid-Senior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._ml_engineer_template(),
                "css": self._ml_engineer_css()
            },
            
            "junior_developer": {
                "info": EngineeringTemplateInfo(
                    id="junior_developer",
                    name="Fresh Graduate",
                    description="Clean, education-focused layout highlighting projects, learning journey, and technical growth with modern styling",
                    specialization=["Entry-Level", "Bootcamp", "Computer Science", "Self-Taught"],
                    experience_level="Junior",
                    ats_optimized=True,
                    github_integration=True
                ),
                "html": self._junior_developer_template(),
                "css": self._junior_developer_css()
            }
        }
    
    def get_template_by_id(self, template_id: str) -> Dict:
        """Get a specific template by ID."""
        return self.templates.get(template_id, {})
    
    def get_templates_by_specialization(self, specialization: str) -> Dict[str, Dict]:
        """Get templates suitable for a specific specialization."""
        return {k: v for k, v in self.templates.items() 
                if specialization in v.get("info", {}).specialization}
    
    def get_templates_by_experience_level(self, level: str) -> Dict[str, Dict]:
        """Get templates suitable for a specific experience level."""
        return {k: v for k, v in self.templates.items() 
                if v.get("info", {}).experience_level == level}
    
    def get_all_templates(self) -> Dict[str, Dict]:
        """Get all available templates."""
        return self.templates
    
    def get_template_info_list(self) -> List[EngineeringTemplateInfo]:
        """Get list of all template information."""
        return [template["info"] for template in self.templates.values()]
    
    def _senior_software_engineer_template(self) -> str:
        return """
<div class="engineering-resume senior-engineer">
    <header class="engineer-header">
        <div class="engineer-info">
            <h1 class="engineer-name">{{NAME}}</h1>
            <h2 class="engineer-title">{{PROFESSIONAL_TITLE}}</h2>
            <div class="engineer-summary">{{PROFESSIONAL_SUMMARY}}</div>
        </div>
        <div class="contact-tech-card">
            <div class="contact-section">
                <div class="contact-item">
                    <span class="contact-label">📧</span>
                    <span class="contact-value">{{EMAIL}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-label">📱</span>
                    <span class="contact-value">{{PHONE}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-label">📍</span>
                    <span class="contact-value">{{LOCATION}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-label">💼</span>
                    <span class="contact-value">{{LINKEDIN}}</span>
                </div>
                <div class="contact-item">
                    <span class="contact-label">🔗</span>
                    <span class="contact-value">{{GITHUB}}</span>
                </div>
            </div>
        </div>
    </header>
    
    <section class="tech-stack-highlight">
        <h3>🛠️ Technical Expertise</h3>
        <div class="tech-grid">
            {{TECHNICAL_SKILLS}}
        </div>
    </section>
    
    <section class="experience-section">
        <h3>💼 Professional Experience</h3>
        <div class="experience-timeline">
            {{WORK_EXPERIENCE}}
        </div>
    </section>
    
    <section class="projects-showcase">
        <h3>🚀 Key Projects & Achievements</h3>
        <div class="projects-grid">
            {{PROJECTS}}
        </div>
    </section>
    
    <section class="education-certs">
        <div class="education-column">
            <h4>🎓 Education</h4>
            {{EDUCATION}}
        </div>
        <div class="certs-column">
            <h4>📜 Certifications</h4>
            {{CERTIFICATIONS}}
        </div>
    </section>
</div>
        """.strip()
    
    def _senior_software_engineer_css(self) -> str:
        return """
/* Senior Software Engineer Template CSS */
.engineering-resume {
    max-width: 1000px;
    margin: 0 auto;
    padding: 0;
    font-family: 'JetBrains Mono', 'SF Mono', 'Monaco', 'Inconsolata', 'Fira Code', 'Droid Sans Mono', 'Source Code Pro', monospace;
    line-height: 1.6;
    color: #2d3748;
    background: #f8fafc;
}

.engineer-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 50px 40px;
    display: grid;
    grid-template-columns: 2fr 1fr;
    gap: 40px;
    align-items: center;
}

.engineer-name {
    font-size: 42px;
    font-weight: 700;
    margin: 0 0 10px 0;
    letter-spacing: -1px;
}

.engineer-title {
    font-size: 24px;
    font-weight: 300;
    margin: 0 0 20px 0;
    opacity: 0.9;
}

.engineer-summary {
    font-size: 16px;
    line-height: 1.7;
    opacity: 0.9;
    max-width: 500px;
}

.contact-tech-card {
    background: rgba(255, 255, 255, 0.1);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 30px;
    border: 1px solid rgba(255, 255, 255, 0.2);
}

.contact-item {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 12px;
    font-size: 14px;
}

.contact-label {
    font-size: 16px;
    width: 24px;
}

.contact-value {
    font-weight: 500;
}

.tech-stack-highlight {
    padding: 40px;
    background: white;
    border-bottom: 1px solid #e2e8f0;
}

.tech-stack-highlight h3 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
    margin: 0 0 25px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.tech-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
}

.skill-group {
    background: #f7fafc;
    padding: 20px;
    border-radius: 10px;
    border-left: 4px solid #667eea;
}

.skill-group h3 {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin: 0 0 12px 0;
}

.skill-tags {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
}

.skill-tag {
    background: #667eea;
    color: white;
    padding: 4px 12px;
    border-radius: 15px;
    font-size: 12px;
    font-weight: 500;
}

.experience-section {
    padding: 40px;
    background: white;
}

.experience-section h3 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
    margin: 0 0 30px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.experience-timeline {
    position: relative;
    padding-left: 30px;
}

.experience-timeline::before {
    content: '';
    position: absolute;
    left: 15px;
    top: 0;
    bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, #667eea, #764ba2);
}

.experience-item {
    position: relative;
    margin-bottom: 40px;
    background: #f8fafc;
    padding: 25px;
    border-radius: 12px;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.experience-item::before {
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

.job-header {
    margin-bottom: 15px;
}

.job-title-company {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 8px;
}

.job-title {
    font-size: 20px;
    font-weight: 700;
    color: #2d3748;
}

.job-date {
    font-size: 14px;
    color: #718096;
    font-weight: 500;
}

.company {
    font-size: 16px;
    color: #667eea;
    font-weight: 600;
}

.job-description ul {
    margin: 0;
    padding-left: 0;
    list-style: none;
}

.job-description li {
    position: relative;
    padding-left: 20px;
    margin-bottom: 6px;
    font-size: 14px;
    line-height: 1.6;
    color: #4a5568;
}

.job-description li::before {
    content: '▶';
    position: absolute;
    left: 0;
    color: #667eea;
    font-size: 12px;
}

.projects-showcase {
    padding: 40px;
    background: #f8fafc;
}

.projects-showcase h3 {
    font-size: 24px;
    font-weight: 700;
    color: #2d3748;
    margin: 0 0 30px 0;
    display: flex;
    align-items: center;
    gap: 10px;
}

.projects-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
    gap: 25px;
}

.project-item {
    background: white;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07);
    transition: transform 0.2s, box-shadow 0.2s;
}

.project-item:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.1);
}

.project-header {
    display: flex;
    justify-content: space-between;
    align-items: baseline;
    margin-bottom: 12px;
}

.project-title {
    font-size: 18px;
    font-weight: 700;
    color: #2d3748;
}

.project-link {
    font-size: 13px;
    color: #667eea;
    text-decoration: none;
    font-weight: 500;
}

.project-description {
    font-size: 14px;
    color: #4a5568;
    line-height: 1.6;
    margin-bottom: 12px;
}

.project-tech {
    font-size: 12px;
    color: #718096;
    font-weight: 500;
}

.education-certs {
    padding: 40px;
    background: white;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
}

.education-certs h4 {
    font-size: 20px;
    font-weight: 700;
    color: #2d3748;
    margin: 0 0 20px 0;
    display: flex;
    align-items: center;
    gap: 8px;
}

.education-item {
    background: #f7fafc;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 15px;
    border-left: 4px solid #48bb78;
}

.degree-name {
    font-size: 16px;
    font-weight: 600;
    color: #2d3748;
    margin-bottom: 5px;
}

.school-name {
    font-size: 14px;
    color: #48bb78;
    font-weight: 500;
}

.graduation-date {
    font-size: 13px;
    color: #718096;
}

/* Responsive design */
@media (max-width: 768px) {
    .engineer-header {
        grid-template-columns: 1fr;
        text-align: center;
        gap: 25px;
        padding: 30px 20px;
    }
    
    .engineer-name {
        font-size: 32px;
    }
    
    .tech-grid, .projects-grid {
        grid-template-columns: 1fr;
    }
    
    .education-certs {
        grid-template-columns: 1fr;
        gap: 25px;
    }
    
    .job-title-company {
        flex-direction: column;
        align-items: flex-start;
    }
    
    .project-header {
        flex-direction: column;
        align-items: flex-start;
        gap: 5px;
    }
}

/* Print optimization */
@media print {
    .engineering-resume {
        background: white !important;
    }
    
    .engineer-header {
        background: #f7fafc !important;
        color: #2d3748 !important;
    }
    
    .project-item, .experience-item {
        box-shadow: none !important;
        border: 1px solid #e2e8f0 !important;
    }
}
        """.strip()
    
    # Placeholder implementations for other templates (they would follow similar patterns)
    def _fullstack_developer_template(self) -> str:
        # Customize the template for full-stack focus
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "⚡ Full-Stack Technologies"
        ).replace(
            "Senior Software Engineer", 
            "Full-Stack Developer"
        )
    
    def _fullstack_developer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _backend_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "🏗️ Backend & Infrastructure"
        )
    
    def _backend_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _devops_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "☁️ DevOps & Cloud Platforms"
        )
    
    def _devops_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _data_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "📊 Data Engineering Stack"
        )
    
    def _data_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _mobile_developer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "📱 Mobile Development"
        )
    
    def _mobile_developer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _frontend_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "🎨 Frontend & UI Technologies"
        )
    
    def _frontend_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _security_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "🔒 Security & Compliance"
        )
    
    def _security_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _ml_engineer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "🛠️ Technical Expertise", 
            "🤖 ML & AI Technologies"
        )
    
    def _ml_engineer_css(self) -> str:
        return self._senior_software_engineer_css()
    
    def _junior_developer_template(self) -> str:
        return self._senior_software_engineer_template().replace(
            "💼 Professional Experience", 
            "🌱 Experience & Learning Journey"
        ).replace(
            "🚀 Key Projects & Achievements", 
            "💡 Personal Projects & Portfolio"
        )
    
    def _junior_developer_css(self) -> str:
        return self._senior_software_engineer_css()

# Global instance for easy import
engineering_templates = EngineeringTemplates()