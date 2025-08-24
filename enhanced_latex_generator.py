"""
Enhanced LaTeX Generator for Exact Resume Recreation
"""

import os
import re
from typing import List, Dict, Tuple
from dataclasses import asdict
from resume_analyzer import ResumeSection, TextBlock

class EnhancedLaTeXGenerator:
    """Enhanced LaTeX generator that recreates the exact original layout."""
    
    def __init__(self):
        self.page_width = 595.27  # A4 width in points
        self.page_height = 841.89  # A4 height in points
        
    def generate_exact_recreation(self, sections, analysis_data: Dict) -> Tuple[str, str]:
        """Generate LaTeX that exactly recreates the original resume."""
        
        # Analyze the original layout
        layout_analysis = self._analyze_original_layout(analysis_data)
        
        # Generate LaTeX based on detected style
        if layout_analysis['style'] == 'altacv':
            return self._generate_altacv_style(sections, analysis_data, layout_analysis)
        elif layout_analysis['style'] == 'moderncv':
            return self._generate_moderncv_style(sections, analysis_data, layout_analysis)
        else:
            return self._generate_custom_style(sections, analysis_data, layout_analysis)
    
    def _analyze_original_layout(self, analysis_data: Dict) -> Dict:
        """Analyze the original layout to determine style and measurements."""
        text_blocks = analysis_data.get('text_blocks', [])
        
        analysis = {
            'style': 'custom',
            'colors': {'primary': 'black', 'accent': 'blue'},
            'fonts': {'main': 11, 'header': 24, 'section': 14},
            'spacing': {'section_gap': 20, 'line_height': 12},
            'margins': {'left': 50, 'right': 50, 'top': 50, 'bottom': 50},
            'layout': 'single_column'
        }
        
        if text_blocks:
            # Detect font sizes
            font_sizes = [block['font_size'] for block in text_blocks]
            analysis['fonts']['main'] = self._most_common(font_sizes)
            analysis['fonts']['header'] = max(font_sizes)
            analysis['fonts']['section'] = sorted(set(font_sizes), reverse=True)[1] if len(set(font_sizes)) > 1 else max(font_sizes)
            
            # Detect margins
            x_positions = [block['x'] for block in text_blocks]
            analysis['margins']['left'] = min(x_positions)
            
            # Detect if it's a two-column layout
            x_positions_right = [x for x in x_positions if x > self.page_width / 2]
            if len(x_positions_right) > len(text_blocks) * 0.3:
                analysis['layout'] = 'two_column'
        
        return analysis
    
    def _most_common(self, lst):
        """Find the most common value in a list."""
        return max(set(lst), key=lst.count) if lst else 11
    
    def _generate_altacv_style(self, sections: List[ResumeSection], analysis_data: Dict, layout: Dict) -> Tuple[str, str]:
        """Generate AltaCV style LaTeX."""
        
        text_blocks = analysis_data.get('text_blocks', [])
        
        # Extract personal information
        name = "Your Name"
        tagline = ""
        email = ""
        phone = ""
        linkedin = ""
        location = ""
        
        for block in text_blocks:
            text = block['text']
            if block['font_size'] >= layout['fonts']['header'] and len(text.split()) <= 3:
                name = text
            elif 'engineer' in text.lower() or 'developer' in text.lower():
                tagline = text
            elif '@' in text:
                email = text.replace('faAt : ', '').replace('\\faAt : ', '')
            elif any(char.isdigit() for char in text) and ('+' in text or 'phone' in text.lower()):
                phone = text.replace('faPhone : ', '').replace('\\faPhone : ', '')
            elif 'linkedin' in text.lower() or 'faLinkedin' in text:
                linkedin = text.replace('faLinkedin : ', '').replace('\\faLinkedin : ', '')
            elif any(city in text.lower() for city in ['casablanca', 'morocco', 'rabat', 'marrakech']):
                location = text.replace('faMapMarker  : ', '').replace('\\faMapMarker : ', '')
        
        # Generate content sections
        content_sections = []
        
        # Handle both dict and object formats
        if sections:
            for section in sections:
                # Get section data (handle both dict and object)
                if hasattr(section, 'section_type'):
                    section_type = section.section_type
                    title = section.title
                else:
                    section_type = section.get('section_type', 'other')
                    title = section.get('title', '')
                
                if section_type == 'header':
                    continue
                elif 'summary' in title.lower() or 'profile' in title.lower():
                    content_sections.append(self._generate_summary_section(section))
                elif 'experience' in title.lower() or 'employment' in title.lower():
                    content_sections.append(self._generate_experience_section(section))
                elif 'education' in title.lower():
                    content_sections.append(self._generate_education_section(section))
                elif 'skills' in title.lower() or 'technical' in title.lower():
                    content_sections.append(self._generate_skills_section(section))
                else:
                    content_sections.append(self._generate_generic_section(section))
        
        # Generate main LaTeX content
        tex_content = f"""\\documentclass[10pt,a4paper,ragged2e,withhyper]{{altacv}}
\\usepackage[utf8]{{inputenc}}
\\usepackage{{geometry}}
\\usepackage{{enumitem}}
\\usepackage{{xcolor}}
\\usepackage{{hyperref}}

% Define colors
\\definecolor{{darkblue}}{{RGB}}{{0, 51, 102}}
\\definecolor{{lightgray}}{{RGB}}{{240, 240, 240}}

% Set up the page margins
\\geometry{{left=1.25cm,right=1.25cm,top=1.5cm,bottom=1.5cm,columnsep=1.2cm}}

% Set up the color of sections and subsections
\\colorlet{{heading}}{{darkblue}}
\\colorlet{{accent}}{{darkblue}}
\\colorlet{{emphasis}}{{black}}
\\colorlet{{body}}{{black!80!white}}

% Adjust font sizes
\\renewcommand{{\\namefont}}{{\\Huge\\bfseries}}
\\renewcommand{{\\personalinfofont}}{{\\large}}
\\renewcommand{{\\cvsectionfont}}{{\\Large\\bfseries}}
\\renewcommand{{\\cvsubsectionfont}}{{\\large\\bfseries}}
\\renewcommand{{\\cveventfont}}{{\\normalsize\\bfseries}}

% Personal information
\\name{{{name}}}
\\tagline{{{tagline}}}
\\personalinfo{{%
  \\email{{{email}}}
  \\phone{{{phone}}}
  \\linkedin{{{linkedin}}}
  \\location{{{location}}}
}}

\\begin{{document}}
\\makecvheader

{chr(10).join(content_sections)}

\\end{{document}}"""

        # Generate CLS content (copy the AltaCV class)
        cls_content = self._get_altacv_class()
        
        return tex_content, cls_content
    
    def _generate_summary_section(self, section) -> str:
        """Generate professional summary section."""
        content = []
        
        # Handle both dict and object formats
        section_content = section.get('content', []) if hasattr(section, 'get') else getattr(section, 'content', [])
        
        for block in section_content:
            # Handle both dict and object formats for blocks
            text = block.get('text', '') if hasattr(block, 'get') else getattr(block, 'text', '')
            if len(text) > 50:  # Likely summary content
                content.append(text)
        
        summary_text = ' '.join(content) if content else 'Professional summary content here.'
        return f"""\\cvsection{{Professional Summary}}
\\begin{{minipage}}{{\\textwidth}}
{summary_text}
\\end{{minipage}}"""
    
    def _generate_experience_section(self, section) -> str:
        """Generate experience section with proper job entries."""
        # Handle both dict and object formats
        section_content = section.get('content', []) if hasattr(section, 'get') else getattr(section, 'content', [])
        
        # Group content into jobs
        jobs = self._parse_experience_blocks(section_content)
        
        section_tex = "\\cvsection{Professional Experience}\n"
        
        for job in jobs:
            if job.get('title') and job.get('company'):
                section_tex += f"\\cvevent{{{job['title']}}}{{{job['company']}}}{{{job.get('date', '')}}}{{{job.get('location', '')}}}\n"
                
                if job.get('descriptions'):
                    section_tex += "\\begin{itemize}[noitemsep]\n"
                    for desc in job['descriptions']:
                        section_tex += f"\\item {desc}\n"
                    section_tex += "\\end{itemize}\n"
                
                section_tex += "\n"
        
        return section_tex
    
    def _parse_experience_blocks(self, blocks) -> List[Dict]:
        """Parse text blocks into structured job entries."""
        jobs = []
        current_job = {}
        
        for block in blocks:
            # Handle both dict and object formats
            text = block.get('text', '') if hasattr(block, 'get') else getattr(block, 'text', '')
            is_bold = block.get('is_bold', False) if hasattr(block, 'get') else getattr(block, 'is_bold', False)
            
            text = text.strip()
            
            # Skip section headers
            if 'experience' in text.lower() and len(text.split()) <= 3:
                continue
            
            # Detect job titles (usually bold and specific keywords)
            if is_bold and any(keyword in text.lower() for keyword in ['engineer', 'developer', 'analyst', 'manager', 'specialist']):
                if current_job:
                    jobs.append(current_job)
                current_job = {'title': text, 'descriptions': []}
            
            # Detect companies (usually has "at" or specific patterns)
            elif ' at ' in text.lower() or any(keyword in text.lower() for keyword in ['technologies', 'solutions', 'systems', 'inc', 'ltd', 'corp']):
                current_job['company'] = text
            
            # Detect dates (contains years)
            elif re.search(r'\b20\d{2}\b', text):
                current_job['date'] = text
            
            # Detect locations
            elif any(location in text.lower() for location in ['casablanca', 'morocco', 'rabat', 'paris', 'london', 'new york']):
                current_job['location'] = text
            
            # Everything else is likely a description
            elif len(text) > 20 and not text.isupper():
                if 'descriptions' not in current_job:
                    current_job['descriptions'] = []
                current_job['descriptions'].append(text)
        
        if current_job:
            jobs.append(current_job)
        
        return jobs
    
    def _generate_education_section(self, section: ResumeSection) -> str:
        """Generate education section."""
        return f"""\\cvsection{{Education}}
\\cvevent{{Your Degree}}{{Your University}}{{Year}}{{Location}}"""
    
    def _generate_skills_section(self, section: ResumeSection) -> str:
        """Generate skills section."""
        skills = []
        for block in section.content:
            if 'skills' not in block.text.lower():
                skills.append(block.text)
        
        skills_text = ', '.join(skills)
        return f"""\\cvsection{{Technical Skills}}
\\begin{{itemize}}[noitemsep]
\\item {skills_text}
\\end{{itemize}}"""
    
    def _generate_generic_section(self, section: ResumeSection) -> str:
        """Generate generic section."""
        content = []
        for block in section.content:
            if block.text.strip() and len(block.text) > 3:
                content.append(f"\\item {block.text}")
        
        return f"""\\cvsection{{{section.title}}}
\\begin{{itemize}}[noitemsep]
{chr(10).join(content)}
\\end{{itemize}}"""
    
    def _generate_custom_style(self, sections: List[ResumeSection], analysis_data: Dict, layout: Dict) -> Tuple[str, str]:
        """Generate custom style when no standard template is detected."""
        return self._generate_altacv_style(sections, analysis_data, layout)
    
    def _generate_moderncv_style(self, sections: List[ResumeSection], analysis_data: Dict, layout: Dict) -> Tuple[str, str]:
        """Generate ModernCV style LaTeX."""
        return self._generate_altacv_style(sections, analysis_data, layout)
    
    def _get_altacv_class(self) -> str:
        """Return the AltaCV class content."""
        try:
            # Try to read the existing altacv class if available
            if os.path.exists('tests/altacv(3).cls'):
                with open('tests/altacv(3).cls', 'r', encoding='utf-8') as f:
                    return f.read()
        except:
            pass
        
        # Fallback to a basic altacv-compatible class
        return """% AltaCV Class File
\\NeedsTeXFormat{LaTeX2e}[1995/12/01]
\\ProvidesClass{altacv}[2022/01/01 AltaCV v1.0]

\\LoadClass{article}

% Basic packages
\\RequirePackage{xcolor}
\\RequirePackage{geometry}
\\RequirePackage{fontawesome}
\\RequirePackage{hyperref}

% Define basic commands
\\newcommand{\\name}[1]{\\def\\@name{#1}}
\\newcommand{\\tagline}[1]{\\def\\@tagline{#1}}
\\newcommand{\\personalinfo}[1]{\\def\\@personalinfo{#1}}

\\newcommand{\\makecvheader}{
  \\begin{center}
    {\\namefont\\@name}\\\\
    {\\personalinfofont\\@tagline}\\\\
    \\@personalinfo
  \\end{center}
}

\\newcommand{\\cvsection}[1]{
  \\vspace{1em}
  {\\cvsectionfont #1}
  \\vspace{0.5em}
}

\\newcommand{\\cvevent}[4]{
  \\textbf{#1} \\hfill #3\\\\
  \\textit{#2} \\hfill #4\\\\
}

% Font definitions
\\newcommand{\\namefont}{\\Huge\\bfseries}
\\newcommand{\\personalinfofont}{\\large}
\\newcommand{\\cvsectionfont}{\\Large\\bfseries}
\\newcommand{\\cvsubsectionfont}{\\large\\bfseries}
\\newcommand{\\cveventfont}{\\normalsize\\bfseries}"""
