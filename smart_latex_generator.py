#!/usr/bin/env python3
"""
Smart LaTeX Generator - Creates professional LaTeX from parsed resume data
"""

from typing import Dict, List, Tuple
from advanced_resume_parser import ParsedResume, JobExperience, Education, Project, SkillCategory
import re
import logging

logger = logging.getLogger(__name__)

class SmartLaTeXGenerator:
    """Generate high-quality LaTeX from structured resume data."""
    
    def __init__(self):
        self.class_content = self._get_professional_class()
    
    def generate_from_parsed_resume(self, parsed_resume: ParsedResume, original_language: str = "English") -> Tuple[str, str]:
        """Generate LaTeX content from structured resume data."""
        
        if not parsed_resume:
            logger.warning("No parsed resume data available")
            return self._get_fallback_template(), self.class_content
        
        # Build LaTeX document sections
        latex_sections = []
        
        # Header with contact information
        if parsed_resume.contact_info:
            header_section = self._generate_header_section(parsed_resume.contact_info)
            latex_sections.append(header_section)
        
        # Professional summary
        if parsed_resume.professional_summary:
            summary_section = self._generate_summary_section(parsed_resume.professional_summary)
            latex_sections.append(summary_section)
        
        # Professional experience
        if parsed_resume.job_experiences:
            experience_section = self._generate_experience_section(parsed_resume.job_experiences)
            latex_sections.append(experience_section)
        
        # Education
        if parsed_resume.education:
            education_section = self._generate_education_section(parsed_resume.education)
            latex_sections.append(education_section)
        
        # Skills
        if parsed_resume.skills:
            skills_section = self._generate_skills_section(parsed_resume.skills)
            latex_sections.append(skills_section)
        
        # Projects
        if parsed_resume.projects:
            projects_section = self._generate_projects_section(parsed_resume.projects)
            latex_sections.append(projects_section)
        
        # Certifications
        if parsed_resume.certifications:
            cert_section = self._generate_certifications_section(parsed_resume.certifications)
            latex_sections.append(cert_section)
        
        # Additional sections
        if parsed_resume.additional_sections:
            for section_name, items in parsed_resume.additional_sections.items():
                if items and any(item.strip() for item in items):
                    additional_section = self._generate_additional_section(section_name, items)
                    latex_sections.append(additional_section)
        
        # Combine into complete document
        document_content = "\n\n".join(latex_sections)
        tex_content = self._get_document_template().replace("{{DOCUMENT_CONTENT}}", document_content)
        
        return tex_content, self.class_content
    
    def _generate_header_section(self, contact_info) -> str:
        """Generate professional header section."""
        header_parts = []
        
        # Name (large and prominent)
        if contact_info.name:
            header_parts.append(f"\\name{{{contact_info.name}}}")
        
        # Contact information
        contact_items = []
        if contact_info.email:
            contact_items.append(f"\\href{{mailto:{contact_info.email}}}{{{contact_info.email}}}")
        if contact_info.phone:
            contact_items.append(contact_info.phone)
        if contact_info.location:
            contact_items.append(contact_info.location)
        if contact_info.linkedin:
            linkedin_url = contact_info.linkedin if contact_info.linkedin.startswith('http') else f"https://www.{contact_info.linkedin}"
            contact_items.append(f"\\href{{{linkedin_url}}}{{LinkedIn}}")
        if contact_info.github:
            github_url = contact_info.github if contact_info.github.startswith('http') else f"https://www.{contact_info.github}"
            contact_items.append(f"\\href{{{github_url}}}{{GitHub}}")
        
        if contact_items:
            bullet_separator = ' $\\bullet$ '
            header_parts.append(f"\\contact{{{bullet_separator.join(contact_items)}}}")
        
        return "\n".join(header_parts)
    
    def _generate_summary_section(self, summary: str) -> str:
        """Generate professional summary section."""
        # Clean and format the summary
        cleaned_summary = self._clean_latex_text(summary)
        
        return f"""\\section{{Professional Summary}}
\\begin{{quote}}
\\itshape {cleaned_summary}
\\end{{quote}}"""
    
    def _generate_experience_section(self, experiences: List[JobExperience]) -> str:
        """Generate professional experience section."""
        section_parts = ["\\section{Professional Experience}"]
        
        for exp in experiences:
            # Job header
            job_title = self._clean_latex_text(exp.job_title) if exp.job_title else "Position"
            company = self._clean_latex_text(exp.company) if exp.company else "Company"
            
            # Date range
            start_date = exp.start_date if exp.start_date else ""
            end_date = exp.end_date if exp.end_date else "Present"
            date_range = f"{start_date} -- {end_date}" if start_date else end_date
            
            # Location
            location = f", {exp.location}" if exp.location else ""
            
            # Job entry
            section_parts.append(f"\\resumeItem{{{job_title}}}{{{company}{location}}}{{{date_range}}}")
            
            # Job description
            if exp.description:
                section_parts.append("\\begin{itemize}[leftmargin=0.5in]")
                for desc in exp.description:
                    cleaned_desc = self._clean_latex_text(desc)
                    if cleaned_desc.strip():
                        section_parts.append(f"    \\item {cleaned_desc}")
                section_parts.append("\\end{itemize}")
            
            section_parts.append("")  # Add spacing between jobs
        
        return "\n".join(section_parts)
    
    def _generate_education_section(self, education_list: List[Education]) -> str:
        """Generate education section."""
        section_parts = ["\\section{Education}"]
        
        for edu in education_list:
            degree = self._clean_latex_text(edu.degree) if edu.degree else "Degree"
            school = self._clean_latex_text(edu.school) if edu.school else "Institution"
            grad_date = edu.graduation_date if edu.graduation_date else ""
            
            # Additional info
            additional_info = []
            if edu.gpa:
                additional_info.append(f"GPA: {edu.gpa}")
            if edu.honors:
                additional_info.append(edu.honors)
            
            additional_text = f" ({', '.join(additional_info)})" if additional_info else ""
            
            section_parts.append(f"\\resumeItem{{{degree}}}{{{school}{additional_text}}}{{{grad_date}}}")
            
            # Relevant courses
            if edu.relevant_courses:
                courses = ", ".join(edu.relevant_courses)
                section_parts.append(f"\\textit{{Relevant Courses:}} {self._clean_latex_text(courses)}")
            
            section_parts.append("")
        
        return "\n".join(section_parts)
    
    def _generate_skills_section(self, skills: List[SkillCategory]) -> str:
        """Generate skills section with categories."""
        section_parts = ["\\section{Technical Skills}"]
        
        for skill_cat in skills:
            category_name = skill_cat.category if skill_cat.category else "Skills"
            skills_list = ", ".join(skill_cat.skills) if skill_cat.skills else ""
            
            if skills_list:
                section_parts.append(f"\\textbf{{{category_name}:}} {self._clean_latex_text(skills_list)}")
                section_parts.append("")
        
        # If no categories, create a simple list
        if len(skills) == 1 and not skills[0].category:
            all_skills = ", ".join(skills[0].skills) if skills[0].skills else ""
            section_parts = ["\\section{Technical Skills}", f"\\resumeSkills{{{self._clean_latex_text(all_skills)}}}"]
        
        return "\n".join(section_parts)
    
    def _generate_projects_section(self, projects: List[Project]) -> str:
        """Generate projects section."""
        section_parts = ["\\section{Projects}"]
        
        for project in projects:
            title = self._clean_latex_text(project.title) if project.title else "Project"
            date = project.date if project.date else ""
            
            section_parts.append(f"\\resumeItem{{{title}}}{{}}{{{date}}}")
            
            # Project description
            if project.description:
                cleaned_desc = self._clean_latex_text(project.description)
                section_parts.append(f"{cleaned_desc}")
            
            # Technologies used
            if project.technologies:
                tech_list = ", ".join(project.technologies)
                section_parts.append(f"\\textit{{Technologies:}} {self._clean_latex_text(tech_list)}")
            
            section_parts.append("")
        
        return "\n".join(section_parts)
    
    def _generate_certifications_section(self, certifications: List[str]) -> str:
        """Generate certifications section."""
        section_parts = ["\\section{Certifications}"]
        section_parts.append("\\begin{itemize}[leftmargin=0.2in]")
        
        for cert in certifications:
            cleaned_cert = self._clean_latex_text(cert)
            if cleaned_cert.strip():
                section_parts.append(f"    \\item {cleaned_cert}")
        
        section_parts.append("\\end{itemize}")
        return "\n".join(section_parts)
    
    def _generate_additional_section(self, section_name: str, items: List[str]) -> str:
        """Generate additional sections."""
        cleaned_name = self._clean_latex_text(section_name)
        section_parts = [f"\\section{{{cleaned_name}}}"]
        section_parts.append("\\begin{itemize}[leftmargin=0.2in]")
        
        for item in items:
            cleaned_item = self._clean_latex_text(item)
            if cleaned_item.strip():
                section_parts.append(f"    \\item {cleaned_item}")
        
        section_parts.append("\\end{itemize}")
        return "\n".join(section_parts)
    
    def _clean_latex_text(self, text: str) -> str:
        """Clean text for LaTeX compilation."""
        if not text:
            return ""
        
        # LaTeX special characters that need escaping
        latex_chars = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '{': '\\{',
            '}': '\\}',
            '~': '\\textasciitilde{}',
            '\\': '\\textbackslash{}'
        }
        
        # Replace special characters
        cleaned = text
        for char, replacement in latex_chars.items():
            cleaned = cleaned.replace(char, replacement)
        
        # Handle quotes
        cleaned = cleaned.replace('"', "``").replace('"', "''")
        cleaned = cleaned.replace('"', "''")
        
        # Remove excessive whitespace
        cleaned = re.sub(r'\s+', ' ', cleaned)
        cleaned = cleaned.strip()
        
        return cleaned
    
    def _get_document_template(self) -> str:
        """Get the main document template."""
        return r"""
\documentclass[11pt,a4paper]{resume}

\usepackage{hyperref}
\hypersetup{
    colorlinks=true,
    linkcolor=blue,
    urlcolor=blue,
    citecolor=blue
}

\begin{document}

{{DOCUMENT_CONTENT}}

\end{document}
"""
    
    def _get_professional_class(self) -> str:
        """Get professional resume class definition."""
        return r"""
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2024/01/01 Professional Resume class]

\LoadClass[11pt,a4paper]{article}

\usepackage[left=0.7in,top=0.6in,right=0.7in,bottom=0.6in]{geometry}
\usepackage[parfill]{parskip}
\usepackage{array}
\usepackage{ifthen}
\usepackage{enumitem}
\usepackage{xcolor}
\usepackage{titlesec}
\usepackage{url}

% Define colors
\definecolor{primary}{RGB}{0, 0, 0}
\definecolor{secondary}{RGB}{100, 100, 100}
\definecolor{accent}{RGB}{0, 100, 200}

% Remove page numbers
\pagestyle{empty}

% Name command
\def\name#1{\def\@name{#1}}
\def\@name{}

% Contact command  
\def\contact#1{\def\@contact{#1}}
\def\@contact{}

% Make header
\newcommand{\makeheader}{
  \begin{center}
    {\Huge\scshape\@name}
    \vspace{0.1in}
    
    \ifthenelse{\equal{\@contact}{}}{}{
      \\[0.1in]
      {\large\@contact}
    }
  \end{center}
  \vspace{0.2in}
}

% Section formatting
\titleformat{\section}
  {\Large\scshape\raggedright}
  {}{0em}
  {}
  [\titlerule]

\titlespacing{\section}{0pt}{12pt}{8pt}

% Resume item command for experience/education
\newcommand{\resumeItem}[3]{
  \vspace{0.05in}
  \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #3 \\
    \textit{#2} &
  \end{tabular*}
  \vspace{-0.05in}
}

% Skills command
\newcommand{\resumeSkills}[1]{
  \begin{flushleft}
  #1
  \end{flushleft}
}

% Custom itemize for better spacing
\setlist[itemize]{
  leftmargin=0.2in,
  topsep=0pt,
  partopsep=0pt,
  parsep=0pt,
  itemsep=2pt
}

% Quote environment for summary
\renewenvironment{quote}{
  \begin{center}
  \begin{minipage}{0.9\textwidth}
  \setlength{\parindent}{0pt}
  \setlength{\parskip}{0.5em}
}{
  \end{minipage}
  \end{center}
}
"""
    
    def _get_fallback_template(self) -> str:
        """Fallback template if no parsed data is available."""
        return r"""
\documentclass[11pt,a4paper]{resume}

\usepackage{hyperref}

\name{Your Name}
\contact{your.email@example.com $\bullet$ (123) 456-7890 $\bullet$ City, State}

\begin{document}

\section{Professional Summary}
\begin{quote}
\itshape Professional summary goes here.
\end{quote}

\section{Professional Experience}
\resumeItem{Job Title}{Company Name}{Date Range}
\begin{itemize}
    \item Achievement or responsibility
    \item Another achievement
\end{itemize}

\section{Education}
\resumeItem{Degree}{University Name}{Graduation Date}

\section{Technical Skills}
\resumeSkills{Skill 1, Skill 2, Skill 3}

\end{document}
"""