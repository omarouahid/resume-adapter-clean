#!/usr/bin/env python3
"""
Resume Enhancement Comparison - Side-by-side comparison with iterative improvements
"""

import streamlit as st
from typing import Dict, List, Tuple, Optional
import json
import difflib
from dataclasses import dataclass, asdict
import logging

logger = logging.getLogger(__name__)

@dataclass
class SectionVersion:
    """A version of a resume section."""
    content: str
    version_name: str
    timestamp: str
    prompt_used: Optional[str] = None

@dataclass
class SectionComparison:
    """Comparison data for a resume section."""
    section_name: str
    section_type: str  # experience, education, skills, etc.
    original: str
    current: str
    versions: List[SectionVersion]
    selected_version_index: int = -1  # -1 means current version

class ResumeEnhancementComparison:
    """Handles resume enhancement comparison and iterative improvements."""
    
    def __init__(self, openrouter_client=None):
        self.openrouter_client = openrouter_client
        self.comparisons = {}
    
    def create_comparison_from_parsed_resumes(self, original_resume, enhanced_resume) -> Dict[str, SectionComparison]:
        """Create comparison data from original and enhanced parsed resumes."""
        comparisons = {}
        
        # Compare contact information
        if original_resume.contact_info or enhanced_resume.contact_info:
            orig_contact = self._format_contact_info(original_resume.contact_info) if original_resume.contact_info else ""
            enhanced_contact = self._format_contact_info(enhanced_resume.contact_info) if enhanced_resume.contact_info else ""
            
            comparisons["contact_info"] = SectionComparison(
                section_name="Contact Information",
                section_type="contact",
                original=orig_contact,
                current=enhanced_contact,
                versions=[]
            )
        
        # Compare professional summary
        if original_resume.professional_summary or enhanced_resume.professional_summary:
            comparisons["professional_summary"] = SectionComparison(
                section_name="Professional Summary",
                section_type="summary",
                original=original_resume.professional_summary or "",
                current=enhanced_resume.professional_summary or "",
                versions=[]
            )
        
        # Compare job experiences
        if original_resume.job_experiences or enhanced_resume.job_experiences:
            orig_exp = self._format_job_experiences(original_resume.job_experiences)
            enhanced_exp = self._format_job_experiences(enhanced_resume.job_experiences)
            
            comparisons["job_experiences"] = SectionComparison(
                section_name="Professional Experience",
                section_type="experience",
                original=orig_exp,
                current=enhanced_exp,
                versions=[]
            )
        
        # Compare education
        if original_resume.education or enhanced_resume.education:
            orig_edu = self._format_education(original_resume.education)
            enhanced_edu = self._format_education(enhanced_resume.education)
            
            comparisons["education"] = SectionComparison(
                section_name="Education",
                section_type="education",
                original=orig_edu,
                current=enhanced_edu,
                versions=[]
            )
        
        # Compare skills
        if original_resume.skills or enhanced_resume.skills:
            orig_skills = self._format_skills(original_resume.skills)
            enhanced_skills = self._format_skills(enhanced_resume.skills)
            
            comparisons["skills"] = SectionComparison(
                section_name="Skills & Technologies",
                section_type="skills",
                original=orig_skills,
                current=enhanced_skills,
                versions=[]
            )
        
        # Compare projects
        if original_resume.projects or enhanced_resume.projects:
            orig_projects = self._format_projects(original_resume.projects)
            enhanced_projects = self._format_projects(enhanced_resume.projects)
            
            comparisons["projects"] = SectionComparison(
                section_name="Projects",
                section_type="projects",
                original=orig_projects,
                current=enhanced_projects,
                versions=[]
            )
        
        self.comparisons = comparisons
        return comparisons
    
    def enhance_section_with_custom_prompt(self, section_key: str, custom_prompt: str) -> str:
        """Enhance a specific section with a custom prompt."""
        if section_key not in self.comparisons:
            return "Section not found"
        
        if not self.openrouter_client:
            return "Error: OpenRouter client not available"
        
        section = self.comparisons[section_key]
        current_content = section.current
        
        # Build version history context
        history_context = ""
        if section.versions:
            history_context = "\n\nPrevious Enhancement History:\n"
            for i, version in enumerate(section.versions, 1):
                history_context += f"\n--- Version {i}: {version.version_name} ({version.timestamp}) ---\n"
                if version.prompt_used:
                    history_context += f"Request: {version.prompt_used}\n"
                history_context += f"Content:\n{version.content}\n"
        
        # Create enhancement prompt with full context
        enhancement_prompt = f"""
Improve this resume section based on the user's request.

Original {section.section_name}:
{section.original}

Current {section.section_name}:
{current_content}
{history_context}

User's improvement request: {custom_prompt}

Instructions:
1. Keep all factual information accurate
2. Consider the evolution shown in the version history to understand what improvements have been made
3. Improve based on the user's specific request while building on previous enhancements
4. Maintain professional language
5. Preserve the original language if not English
6. Return ONLY the improved section content, no explanations

Improved {section.section_name}:
"""
        
        try:
            enhanced_content = self.openrouter_client._make_request(enhancement_prompt, max_tokens=1000)
            
            if enhanced_content and not enhanced_content.startswith("Error:"):
                # Create new version
                from datetime import datetime
                version = SectionVersion(
                    content=enhanced_content.strip(),
                    version_name=f"Custom Enhancement {len(section.versions) + 1}",
                    timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    prompt_used=custom_prompt
                )
                
                # Add to versions and update current
                section.versions.append(version)
                section.current = enhanced_content.strip()
                section.selected_version_index = len(section.versions) - 1
                
                return enhanced_content.strip()
            else:
                return f"Enhancement failed: {enhanced_content}"
                
        except Exception as e:
            logger.error(f"Section enhancement error: {e}")
            return f"Error enhancing section: {str(e)}"
    
    def add_section_comparison(self, section_key: str, section_name: str, original_content: str, improved_content: str):
        """Add a new section comparison."""
        self.comparisons[section_key] = SectionComparison(
            section_name=section_name,
            section_type="general",
            original=original_content,
            current=improved_content,
            versions=[]
        )
    
    def revert_to_version(self, section_key: str, version_index: int):
        """Revert a section to a specific version."""
        if section_key not in self.comparisons:
            return False
        
        section = self.comparisons[section_key]
        
        if version_index == -1:  # Original version
            section.current = section.original
            section.selected_version_index = -1
        elif 0 <= version_index < len(section.versions):
            section.current = section.versions[version_index].content
            section.selected_version_index = version_index
        else:
            return False
        
        return True
    
    def clear_version_history(self, section_key: str) -> bool:
        """Clear all version history for a section, keeping only the current version."""
        if section_key not in self.comparisons:
            return False
        
        section = self.comparisons[section_key]
        section.versions.clear()
        section.selected_version_index = -1
        return True
    
    def clear_all_version_history(self) -> bool:
        """Clear version history for all sections."""
        for section_key in self.comparisons.keys():
            self.clear_version_history(section_key)
        return True
    
    def get_diff_html(self, section_key: str) -> str:
        """Get HTML diff between original and current version."""
        if section_key not in self.comparisons:
            return ""
        
        section = self.comparisons[section_key]
        
        # Split into lines for better diff visualization
        orig_lines = section.original.split('\n')
        current_lines = section.current.split('\n')
        
        # Generate HTML diff
        differ = difflib.HtmlDiff()
        diff_html = differ.make_file(
            orig_lines, 
            current_lines,
            "Original",
            "Enhanced",
            context=True,
            numlines=2
        )
        
        return diff_html
    
    def _format_contact_info(self, contact_info) -> str:
        """Format contact info for comparison."""
        if not contact_info:
            return ""
        
        parts = []
        if contact_info.name:
            parts.append(f"Name: {contact_info.name}")
        if contact_info.email:
            parts.append(f"Email: {contact_info.email}")
        if contact_info.phone:
            parts.append(f"Phone: {contact_info.phone}")
        if contact_info.location:
            parts.append(f"Location: {contact_info.location}")
        if contact_info.linkedin:
            parts.append(f"LinkedIn: {contact_info.linkedin}")
        if contact_info.github:
            parts.append(f"GitHub: {contact_info.github}")
        
        return "\n".join(parts)
    
    def _format_job_experiences(self, experiences) -> str:
        """Format job experiences for comparison."""
        if not experiences:
            return ""
        
        formatted = []
        for exp in experiences:
            job_parts = []
            
            # Job header
            title = exp.job_title or "Position"
            company = exp.company or "Company"
            dates = f"{exp.start_date or ''} - {exp.end_date or 'Present'}"
            
            job_parts.append(f"{title} | {company} | {dates}")
            if exp.location:
                job_parts.append(f"Location: {exp.location}")
            
            # Job description
            if exp.description:
                job_parts.append("Responsibilities:")
                for desc in exp.description:
                    job_parts.append(f"• {desc}")
            
            formatted.append("\n".join(job_parts))
        
        return "\n\n".join(formatted)
    
    def _format_education(self, education_list) -> str:
        """Format education for comparison."""
        if not education_list:
            return ""
        
        formatted = []
        for edu in education_list:
            edu_parts = []
            
            degree = edu.degree or "Degree"
            school = edu.school or "Institution"
            grad_date = edu.graduation_date or ""
            
            edu_parts.append(f"{degree} | {school} | {grad_date}")
            
            if edu.gpa:
                edu_parts.append(f"GPA: {edu.gpa}")
            if edu.honors:
                edu_parts.append(f"Honors: {edu.honors}")
            if edu.relevant_courses:
                edu_parts.append(f"Relevant Courses: {', '.join(edu.relevant_courses)}")
            
            formatted.append("\n".join(edu_parts))
        
        return "\n\n".join(formatted)
    
    def _format_skills(self, skills) -> str:
        """Format skills for comparison."""
        if not skills:
            return ""
        
        formatted = []
        for skill_cat in skills:
            if skill_cat.category and skill_cat.skills:
                formatted.append(f"{skill_cat.category}: {', '.join(skill_cat.skills)}")
            elif skill_cat.skills:
                formatted.append(', '.join(skill_cat.skills))
        
        return "\n".join(formatted)
    
    def _format_projects(self, projects) -> str:
        """Format projects for comparison."""
        if not projects:
            return ""
        
        formatted = []
        for project in projects:
            project_parts = []
            
            title = project.title or "Project"
            if project.date:
                project_parts.append(f"{title} | {project.date}")
            else:
                project_parts.append(title)
            
            if project.description:
                project_parts.append(project.description)
            
            if project.technologies:
                project_parts.append(f"Technologies: {', '.join(project.technologies)}")
            
            formatted.append("\n".join(project_parts))
        
        return "\n\n".join(formatted)

def display_enhancement_comparison_page():
    """Display the enhancement comparison interface."""
    try:
        st.markdown("# 🔄 Resume Enhancement Comparison")
        st.markdown("Compare original vs enhanced sections and make iterative improvements")
        st.success("✅ Successfully loaded comparison page!")
    except Exception as e:
        st.error(f"❌ Error loading comparison page: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
        return
    
    # Debug information - always show for now to debug the issue
    with st.expander("🔧 Debug Info", expanded=True):
        debug_info = {
            "has_enhancement_comparison": 'enhancement_comparison' in st.session_state,
            "enhancement_comparison_is_none": st.session_state.get('enhancement_comparison') is None,
        }
        
        if st.session_state.get('enhancement_comparison'):
            debug_info["has_comparisons_attr"] = hasattr(st.session_state.enhancement_comparison, 'comparisons')
            if hasattr(st.session_state.enhancement_comparison, 'comparisons'):
                debug_info["comparisons_is_none"] = st.session_state.enhancement_comparison.comparisons is None
                if st.session_state.enhancement_comparison.comparisons:
                    debug_info["comparison_keys"] = list(st.session_state.enhancement_comparison.comparisons.keys())
                    debug_info["num_comparisons"] = len(st.session_state.enhancement_comparison.comparisons)
                    
                    # Show first comparison details
                    first_key = list(st.session_state.enhancement_comparison.comparisons.keys())[0]
                    first_comp = st.session_state.enhancement_comparison.comparisons[first_key]
                    debug_info["first_comparison"] = {
                        "section_name": first_comp.section_name,
                        "has_original": bool(first_comp.original),
                        "has_current": bool(first_comp.current),
                        "original_length": len(first_comp.original) if first_comp.original else 0,
                        "current_length": len(first_comp.current) if first_comp.current else 0,
                    }
        
        st.json(debug_info)
    
    # Check if we have comparison data
    if ('enhancement_comparison' not in st.session_state or 
        not st.session_state.enhancement_comparison or
        not hasattr(st.session_state.enhancement_comparison, 'comparisons') or
        not st.session_state.enhancement_comparison.comparisons):
        
        st.warning("⚠️ No comparison data available. Please enhance your resume first from the main analysis page.")
        
        if st.button("← Back to Main Analysis"):
            st.session_state.show_comparison_page = False
            st.rerun()
        return
    
    comparison_service = st.session_state.enhancement_comparison
    
    # Section selector
    st.markdown("## 📋 Select Section to Compare")
    
    section_options = []
    section_keys = []
    
    for key, section in comparison_service.comparisons.items():
        section_options.append(f"{section.section_name}")
        section_keys.append(key)
    
    if not section_options:
        st.error("No sections available for comparison")
        return
    
    selected_section_idx = st.selectbox(
        "Choose a section:",
        range(len(section_options)),
        format_func=lambda x: section_options[x]
    )
    
    selected_section_key = section_keys[selected_section_idx]
    selected_section = comparison_service.comparisons[selected_section_key]
    
    # Display comparison
    st.markdown(f"## 🔍 Comparing: {selected_section.section_name}")
    
    # Version selector
    if selected_section.versions:
        st.markdown("### 📚 Version History")
        
        version_options = ["Original", "Latest Enhanced"]
        version_options.extend([v.version_name for v in selected_section.versions])
        
        selected_version = st.selectbox(
            "Select version to view:",
            range(len(version_options)),
            format_func=lambda x: version_options[x],
            index=1 if selected_section.selected_version_index == -1 else selected_section.selected_version_index + 2
        )
        
        # Revert to selected version
        if st.button("🔄 Use This Version"):
            if selected_version == 0:  # Original
                comparison_service.revert_to_version(selected_section_key, -1)
                st.success("✅ Reverted to original version")
                st.rerun()
            elif selected_version == 1:  # Latest enhanced
                # Keep current
                st.success("✅ Using latest enhanced version")
            else:  # Specific version
                version_idx = selected_version - 2
                comparison_service.revert_to_version(selected_section_key, version_idx)
                st.success(f"✅ Reverted to {selected_section.versions[version_idx].version_name}")
                st.rerun()
    
    # Side-by-side comparison
    st.markdown("### 📊 Side-by-Side Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📄 Original")
        st.text_area(
            "Original Content",
            value=selected_section.original,
            height=400,
            disabled=True,
            key=f"orig_{selected_section_key}"
        )
    
    with col2:
        st.markdown("#### ✨ Enhanced")
        st.text_area(
            "Enhanced Content", 
            value=selected_section.current,
            height=400,
            disabled=True,
            key=f"enhanced_{selected_section_key}"
        )
    
    # Custom enhancement
    st.markdown("### 🎯 Custom Enhancement")
    
    custom_prompt = st.text_area(
        "Enter your improvement request:",
        placeholder="""Examples:
• Make the bullet points more action-oriented
• Add more quantifiable achievements
• Make it more concise
• Emphasize leadership experience
• Add more technical details
• Improve the language flow""",
        height=100
    )
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button("🚀 Enhance with Custom Prompt", type="primary", disabled=not custom_prompt.strip()):
            if not comparison_service.openrouter_client:
                st.error("❌ OpenRouter API key required for custom enhancements")
            else:
                with st.spinner("🤖 Applying custom enhancement..."):
                    result = comparison_service.enhance_section_with_custom_prompt(selected_section_key, custom_prompt)
                    
                    if not result.startswith("Error:") and not result.startswith("Enhancement failed:"):
                        st.success("✅ Section enhanced with custom prompt!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result}")
    
    with col2:
        if st.button("📋 Show Detailed Diff"):
            st.session_state.show_diff = True
    
    with col3:
        if st.button("← Back to Main"):
            st.session_state.show_comparison_page = False
            st.rerun()
    
    # Show detailed diff if requested
    if st.session_state.get('show_diff', False):
        st.markdown("### 🔍 Detailed Differences")
        
        if selected_section.original.strip() and selected_section.current.strip():
            # Simple text diff
            original_lines = selected_section.original.split('\n')
            current_lines = selected_section.current.split('\n')
            
            diff = list(difflib.unified_diff(
                original_lines, 
                current_lines,
                fromfile='Original',
                tofile='Enhanced',
                lineterm=''
            ))
            
            if diff:
                diff_text = '\n'.join(diff)
                st.code(diff_text, language='diff')
            else:
                st.info("No differences found between versions")
        else:
            st.warning("Cannot generate diff - one of the versions is empty")
        
        if st.button("Hide Diff"):
            st.session_state.show_diff = False
            st.rerun()
    
    # Version history details
    if selected_section.versions:
        st.markdown("### 📚 Enhancement History")
        
        for i, version in enumerate(reversed(selected_section.versions)):
            with st.expander(f"{version.version_name} - {version.timestamp}"):
                if version.prompt_used:
                    st.markdown(f"**Prompt used:** {version.prompt_used}")
                
                st.text_area(
                    f"Content from {version.version_name}:",
                    value=version.content,
                    height=200,
                    disabled=True,
                    key=f"version_{selected_section_key}_{i}"
                )