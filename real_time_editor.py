#!/usr/bin/env python3
"""
Real-Time Editor - Live editing capabilities for resume content.
Works entirely in session state - no user accounts needed.
"""

import streamlit as st
from typing import Dict, List, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)

class RealTimeEditor:
    """Real-time editing interface for resume content."""
    
    def __init__(self):
        """Initialize real-time editor."""
        self.session_key = "realtime_editor_data"
        
        # Initialize session state for editor
        if self.session_key not in st.session_state:
            st.session_state[self.session_key] = {
                'editing_mode': False,
                'current_section': None,
                'unsaved_changes': False,
                'edit_history': []
            }
    
    def show_editing_interface(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Show real-time editing interface.
        
        Args:
            resume_data: Current resume data
            
        Returns:
            Updated resume data
        """
        
        st.markdown("*Click any section below to edit directly*")
        
        # Editor controls
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("💾 Save Changes", disabled=not st.session_state[self.session_key]['unsaved_changes']):
                self._save_changes()
                st.success("✅ Changes saved!")
        
        with col2:
            if st.button("↩️ Undo", disabled=len(st.session_state[self.session_key]['edit_history']) == 0):
                resume_data = self._undo_last_change(resume_data)
                st.success("✅ Last change undone!")
                st.rerun()
        
        with col3:
            if st.button("🔄 Reset All"):
                if st.session_state.get('original_resume_data'):
                    resume_data = st.session_state.original_resume_data.copy()
                    st.session_state[self.session_key]['edit_history'] = []
                    st.success("✅ Reset to original!")
                    st.rerun()
        
        with col4:
            auto_save = st.checkbox("🔄 Auto-save", value=True, help="Save changes automatically")
        
        # Unsaved changes indicator
        if st.session_state[self.session_key]['unsaved_changes']:
            st.warning("⚠️ You have unsaved changes")
        
        st.markdown("---")
        
        # Editable sections - safely copy the resume data
        import copy
        updated_data = copy.deepcopy(resume_data)
        
        # Contact Information Editor
        updated_data = self._edit_contact_info(updated_data, auto_save)
        
        # Professional Summary Editor  
        updated_data = self._edit_professional_summary(updated_data, auto_save)
        
        # Experience Editor
        updated_data = self._edit_experience(updated_data, auto_save)
        
        # Education Editor
        updated_data = self._edit_education(updated_data, auto_save)
        
        # Skills Editor
        updated_data = self._edit_skills(updated_data, auto_save)
        
        return updated_data
    
    def _edit_contact_info(self, resume_data: Dict[str, Any], auto_save: bool) -> Dict[str, Any]:
        """Edit contact information section."""
        
        with st.expander("👤 **Contact Information**", expanded=False):
            contact_info = resume_data.get('contact_info', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input(
                    "Full Name", 
                    value=self._get_contact_field(contact_info, 'name'),
                    key="edit_name"
                )
                
                new_email = st.text_input(
                    "Email", 
                    value=self._get_contact_field(contact_info, 'email'),
                    key="edit_email"
                )
                
                new_phone = st.text_input(
                    "Phone", 
                    value=self._get_contact_field(contact_info, 'phone'),
                    key="edit_phone"
                )
            
            with col2:
                new_location = st.text_input(
                    "Location", 
                    value=self._get_contact_field(contact_info, 'location'),
                    key="edit_location"
                )
                
                new_linkedin = st.text_input(
                    "LinkedIn", 
                    value=self._get_contact_field(contact_info, 'linkedin'),
                    key="edit_linkedin"
                )
                
                new_github = st.text_input(
                    "GitHub", 
                    value=self._get_contact_field(contact_info, 'github'),
                    key="edit_github"
                )
            
            # Update contact info
            updated_contact = {
                'name': new_name,
                'email': new_email,
                'phone': new_phone,
                'location': new_location,
                'linkedin': new_linkedin,
                'github': new_github
            }
            
            # Check for changes
            if updated_contact != self._get_current_contact(contact_info):
                resume_data['contact_info'] = updated_contact
                self._mark_unsaved_changes()
                
                if auto_save:
                    self._save_changes()
        
        return resume_data
    
    def _edit_professional_summary(self, resume_data: Dict[str, Any], auto_save: bool) -> Dict[str, Any]:
        """Edit professional summary section."""
        
        with st.expander("📝 **Professional Summary**", expanded=False):
            current_summary = resume_data.get('professional_summary', '')
            
            new_summary = st.text_area(
                "Professional Summary",
                value=current_summary,
                height=100,
                help="2-3 lines highlighting your key qualifications",
                key="edit_summary"
            )
            
            # Word count and guidance
            word_count = len(new_summary.split())
            col1, col2 = st.columns(2)
            
            with col1:
                if word_count < 20:
                    st.warning(f"⚠️ {word_count} words - Consider adding more detail")
                elif word_count > 60:
                    st.warning(f"⚠️ {word_count} words - Consider making it more concise")
                else:
                    st.success(f"✅ {word_count} words - Good length!")
            
            with col2:
                if st.button("🤖 AI Improve", key="improve_summary"):
                    if st.session_state.get('openrouter_client'):
                        with st.spinner("Improving summary..."):
                            improved_summary = self._ai_improve_text(new_summary, "professional summary")
                            if improved_summary:
                                st.session_state.edit_summary = improved_summary
                                st.rerun()
            
            # Update summary if changed
            if new_summary != current_summary:
                resume_data['professional_summary'] = new_summary
                self._mark_unsaved_changes()
                
                if auto_save:
                    self._save_changes()
        
        return resume_data
    
    def _edit_experience(self, resume_data: Dict[str, Any], auto_save: bool) -> Dict[str, Any]:
        """Edit work experience section."""
        
        with st.expander("💼 **Work Experience**", expanded=False):
            experiences = resume_data.get('job_experiences', [])
            
            # Add new experience button
            if st.button("➕ Add New Job", key="add_job"):
                new_job = {
                    'job_title': 'New Position',
                    'company': 'Company Name',
                    'start_date': '2023',
                    'end_date': 'Present',
                    'location': '',
                    'description': ['• Key achievement or responsibility']
                }
                experiences.append(new_job)
                resume_data['job_experiences'] = experiences
                self._mark_unsaved_changes()
                st.rerun()
            
            # Edit existing experiences
            for i, exp in enumerate(experiences):
                st.markdown(f"##### Job {i+1}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    job_title = st.text_input(
                        "Job Title", 
                        value=self._get_exp_field(exp, 'job_title'),
                        key=f"job_title_{i}"
                    )
                    
                    company = st.text_input(
                        "Company", 
                        value=self._get_exp_field(exp, 'company'),
                        key=f"company_{i}"
                    )
                
                with col2:
                    start_date = st.text_input(
                        "Start Date", 
                        value=self._get_exp_field(exp, 'start_date'),
                        key=f"start_date_{i}"
                    )
                    
                    end_date = st.text_input(
                        "End Date", 
                        value=self._get_exp_field(exp, 'end_date'),
                        key=f"end_date_{i}"
                    )
                
                with col3:
                    location = st.text_input(
                        "Location", 
                        value=self._get_exp_field(exp, 'location'),
                        key=f"location_{i}"
                    )
                    
                    if st.button("🗑️", key=f"delete_job_{i}", help="Delete this job"):
                        experiences.pop(i)
                        resume_data['job_experiences'] = experiences
                        self._mark_unsaved_changes()
                        st.rerun()
                
                # Job description bullets
                current_desc = self._get_exp_field(exp, 'description')
                if isinstance(current_desc, list):
                    desc_text = '\n'.join(current_desc)
                else:
                    desc_text = current_desc or ''
                
                new_desc = st.text_area(
                    f"Job Description (Job {i+1})",
                    value=desc_text,
                    height=100,
                    help="Enter each bullet point on a new line",
                    key=f"description_{i}"
                )
                
                # AI improvement button
                if st.button(f"🤖 AI Improve", key=f"improve_job_{i}"):
                    if st.session_state.get('openrouter_client'):
                        with st.spinner("Improving job description..."):
                            improved_desc = self._ai_improve_text(
                                new_desc, 
                                f"job description for {job_title} at {company}"
                            )
                            if improved_desc:
                                st.session_state[f"description_{i}"] = improved_desc
                                st.rerun()
                
                # Update experience data
                updated_exp = {
                    'job_title': job_title,
                    'company': company,
                    'start_date': start_date,
                    'end_date': end_date,
                    'location': location,
                    'description': [line.strip() for line in new_desc.split('\n') if line.strip()]
                }
                
                experiences[i] = updated_exp
            
            resume_data['job_experiences'] = experiences
            if experiences != resume_data.get('job_experiences', []):
                self._mark_unsaved_changes()
                
                if auto_save:
                    self._save_changes()
        
        return resume_data
    
    def _edit_education(self, resume_data: Dict[str, Any], auto_save: bool) -> Dict[str, Any]:
        """Edit education section."""
        
        with st.expander("🎓 **Education**", expanded=False):
            education = resume_data.get('education', [])
            
            # Add new education button
            if st.button("➕ Add Education", key="add_education"):
                new_edu = {
                    'degree': 'Bachelor of Science',
                    'school': 'University Name',
                    'graduation_date': '2023',
                    'gpa': '',
                    'honors': '',
                    'relevant_courses': []
                }
                education.append(new_edu)
                resume_data['education'] = education
                self._mark_unsaved_changes()
                st.rerun()
            
            # Edit existing education
            for i, edu in enumerate(education):
                st.markdown(f"##### Education {i+1}")
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    degree = st.text_input(
                        "Degree", 
                        value=self._get_edu_field(edu, 'degree'),
                        key=f"degree_{i}"
                    )
                    
                    school = st.text_input(
                        "School", 
                        value=self._get_edu_field(edu, 'school'),
                        key=f"school_{i}"
                    )
                
                with col2:
                    grad_date = st.text_input(
                        "Graduation Date", 
                        value=self._get_edu_field(edu, 'graduation_date'),
                        key=f"grad_date_{i}"
                    )
                    
                    gpa = st.text_input(
                        "GPA (optional)", 
                        value=self._get_edu_field(edu, 'gpa'),
                        key=f"gpa_{i}"
                    )
                
                with col3:
                    if st.button("🗑️", key=f"delete_edu_{i}", help="Delete this education"):
                        education.pop(i)
                        resume_data['education'] = education
                        self._mark_unsaved_changes()
                        st.rerun()
                
                # Update education data
                updated_edu = {
                    'degree': degree,
                    'school': school,
                    'graduation_date': grad_date,
                    'gpa': gpa
                }
                
                education[i] = updated_edu
            
            resume_data['education'] = education
            if education != resume_data.get('education', []):
                self._mark_unsaved_changes()
                
                if auto_save:
                    self._save_changes()
        
        return resume_data
    
    def _edit_skills(self, resume_data: Dict[str, Any], auto_save: bool) -> Dict[str, Any]:
        """Edit skills section."""
        
        with st.expander("🛠️ **Skills**", expanded=False):
            skills = resume_data.get('skills', [])
            
            # Add new skill category
            if st.button("➕ Add Skill Category", key="add_skill_cat"):
                new_skill_cat = {
                    'category': 'New Category',
                    'skills': ['Skill 1', 'Skill 2', 'Skill 3']
                }
                skills.append(new_skill_cat)
                resume_data['skills'] = skills
                self._mark_unsaved_changes()
                st.rerun()
            
            # Edit existing skill categories
            for i, skill_cat in enumerate(skills):
                st.markdown(f"##### Skill Category {i+1}")
                
                col1, col2, col3 = st.columns([2, 3, 1])
                
                with col1:
                    category = st.text_input(
                        "Category", 
                        value=self._get_skill_field(skill_cat, 'category'),
                        key=f"skill_cat_{i}"
                    )
                
                with col2:
                    current_skills = self._get_skill_field(skill_cat, 'skills')
                    if isinstance(current_skills, list):
                        skills_text = ', '.join(current_skills)
                    else:
                        skills_text = current_skills or ''
                    
                    skills_input = st.text_input(
                        "Skills (comma-separated)", 
                        value=skills_text,
                        key=f"skills_{i}",
                        help="Enter skills separated by commas"
                    )
                
                with col3:
                    if st.button("🗑️", key=f"delete_skill_{i}", help="Delete this category"):
                        skills.pop(i)
                        resume_data['skills'] = skills
                        self._mark_unsaved_changes()
                        st.rerun()
                
                # Update skills data
                updated_skills = {
                    'category': category,
                    'skills': [skill.strip() for skill in skills_input.split(',') if skill.strip()]
                }
                
                skills[i] = updated_skills
            
            resume_data['skills'] = skills
            if skills != resume_data.get('skills', []):
                self._mark_unsaved_changes()
                
                if auto_save:
                    self._save_changes()
        
        return resume_data
    
    def _get_contact_field(self, contact_info: Any, field: str) -> str:
        """Get contact info field safely."""
        if hasattr(contact_info, field):
            return getattr(contact_info, field) or ''
        elif isinstance(contact_info, dict):
            return contact_info.get(field, '')
        return ''
    
    def _get_current_contact(self, contact_info: Any) -> Dict[str, str]:
        """Get current contact info as dict."""
        return {
            'name': self._get_contact_field(contact_info, 'name'),
            'email': self._get_contact_field(contact_info, 'email'),
            'phone': self._get_contact_field(contact_info, 'phone'),
            'location': self._get_contact_field(contact_info, 'location'),
            'linkedin': self._get_contact_field(contact_info, 'linkedin'),
            'github': self._get_contact_field(contact_info, 'github')
        }
    
    def _get_exp_field(self, exp: Any, field: str) -> str:
        """Get experience field safely."""
        if hasattr(exp, field):
            value = getattr(exp, field)
            return str(value) if value is not None else ''
        elif isinstance(exp, dict):
            value = exp.get(field, '')
            return str(value) if value is not None else ''
        return ''
    
    def _get_edu_field(self, edu: Any, field: str) -> str:
        """Get education field safely."""
        if hasattr(edu, field):
            value = getattr(edu, field)
            return str(value) if value is not None else ''
        elif isinstance(edu, dict):
            value = edu.get(field, '')
            return str(value) if value is not None else ''
        return ''
    
    def _get_skill_field(self, skill_cat: Any, field: str):
        """Get skill field safely."""
        if hasattr(skill_cat, field):
            return getattr(skill_cat, field)
        elif isinstance(skill_cat, dict):
            return skill_cat.get(field, [])
        return []
    
    def _mark_unsaved_changes(self):
        """Mark that there are unsaved changes."""
        st.session_state[self.session_key]['unsaved_changes'] = True
    
    def _save_changes(self):
        """Save current changes."""
        st.session_state[self.session_key]['unsaved_changes'] = False
        
        # Add to edit history for undo functionality
        if 'parsed_resume' in st.session_state:
            st.session_state[self.session_key]['edit_history'].append(
                st.session_state.parsed_resume.copy()
            )
            
            # Limit history to last 10 changes
            if len(st.session_state[self.session_key]['edit_history']) > 10:
                st.session_state[self.session_key]['edit_history'].pop(0)
    
    def _undo_last_change(self, current_data: Dict[str, Any]) -> Dict[str, Any]:
        """Undo last change."""
        history = st.session_state[self.session_key]['edit_history']
        
        if history:
            # Get last saved state
            previous_data = history.pop()
            st.session_state[self.session_key]['unsaved_changes'] = False
            return previous_data
        
        return current_data
    
    def _ai_improve_text(self, text: str, context: str) -> Optional[str]:
        """Use AI to improve text content."""
        if not st.session_state.get('openrouter_client'):
            return None
        
        try:
            prompt = f"""
Improve this {context} to be more professional and impactful:

Current text: {text}

Requirements:
1. Make it more professional and engaging
2. Use strong action verbs where appropriate
3. Keep it concise and clear
4. Maintain factual accuracy
5. Return ONLY the improved text, no explanations

Improved text:
            """
            
            improved = st.session_state.openrouter_client._make_request(prompt, max_tokens=500)
            
            if improved and not improved.startswith("Error:"):
                return improved.strip()
        
        except Exception as e:
            logger.error(f"AI text improvement error: {e}")
        
        return None

# Global instance
real_time_editor = RealTimeEditor()