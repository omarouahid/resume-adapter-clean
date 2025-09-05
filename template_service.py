"""Template service for listing and rendering resume templates without Streamlit."""
from pathlib import Path
from typing import Dict, Any, List, Optional
from professional_templates import ProfessionalTemplates
from engineering_templates import EngineeringTemplates
from freelancer_templates import FreelancerTemplates

class TemplateService:
    """Load templates and provide simple rendering with placeholder substitution."""
    def __init__(self) -> None:
        self.sources = [
            ProfessionalTemplates(),
            EngineeringTemplates(),
            FreelancerTemplates(),
        ]
        # build lookup map
        self.templates: Dict[str, Dict[str, Any]] = {}
        for src in self.sources:
            for tid, data in src.templates.items():
                info = data.get("info")
                category = getattr(info, "category", "")
                if not category:
                    category = src.__class__.__name__.replace("Templates", "").lower()
                self.templates[tid] = {
                    "html": data.get("html", ""),
                    "css": data.get("css", ""),
                    "name": getattr(info, "name", tid),
                    "description": getattr(info, "description", ""),
                    "category": category,
                }

        # load any file-based templates shipped with the repo
        self._load_file_templates(Path(__file__).parent / "templates")

    def _load_file_templates(self, directory: Path) -> None:
        """Load templates stored as .html/.css pairs in a directory."""
        if not directory.exists():
            return
        for html_path in directory.glob("*.html"):
            tid = html_path.stem
            css_path = directory / f"{tid}.css"
            html = html_path.read_text(encoding="utf-8")
            css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
            self.templates[tid] = {
                "html": html,
                "css": css,
                "name": tid.replace("_", " ").title(),
                "description": "Built-in example template",
                "category": "built-in",
            }

    def list_templates(self) -> List[Dict[str, str]]:
        """Return metadata for available templates."""
        return [
            {
                "id": tid,
                "name": data["name"],
                "description": data["description"],
                "category": data["category"],
            }
            for tid, data in self.templates.items()
        ]

    def match_template(self, job_description: str) -> Optional[str]:
        """Very naive template matcher based on job description keywords."""
        jd = (job_description or "").lower()
        if "engineer" in jd or "developer" in jd:
            for tid, data in self.templates.items():
                if data.get("category", "").lower().startswith("engineering"):
                    return tid
        if "freelance" in jd or "contract" in jd:
            for tid, data in self.templates.items():
                if data.get("category", "").lower().startswith("freelancer"):
                    return tid
        # default to first available template
        return next(iter(self.templates)) if self.templates else None

    def render(self, template_id: str, resume_data: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, str]]:
        """Render the template with very basic placeholder replacement."""
        template = self.templates.get(template_id)
        if not template:
            return None

        html = template["html"]
        css = template["css"]
        data = resume_data or {}
        replacements = {
            "{{NAME}}": data.get("name", "Your Name"),
            "{{EMAIL}}": data.get("email", "email@example.com"),
            "{{PHONE}}": data.get("phone", ""),
            "{{LOCATION}}": data.get("location", ""),
            "{{LINKEDIN}}": data.get("linkedin", ""),
            "{{PROFESSIONAL_SUMMARY}}": data.get("professional_summary", ""),
            "{{WORK_EXPERIENCE}}": "",
            "{{EDUCATION}}": "",
            "{{SKILLS}}": "",
            "{{PROJECTS}}": "",
        }
        for key, val in replacements.items():
            html = html.replace(key, val)
        return {"html": html, "css": css}

# Global instance
template_service = TemplateService()
