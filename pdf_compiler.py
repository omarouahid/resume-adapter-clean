"""
PDF Compiler Service - Compiles LaTeX to PDF and provides preview
"""

import os
import subprocess
import tempfile
import base64
from pathlib import Path
import logging
from typing import Tuple, Optional
import platform
import shutil
import os

logger = logging.getLogger(__name__)

class PDFCompiler:
    """Service for compiling LaTeX to PDF and generating previews."""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.latex_engines = ['pdflatex', 'xelatex', 'lualatex']
        self._setup_latex_path()
    
    def _setup_latex_path(self):
        """Setup LaTeX PATH for Windows MiKTeX installation."""
        if platform.system() == "Windows":
            # Common MiKTeX installation paths
            miktex_paths = [
                os.path.expanduser(r"~\AppData\Local\Programs\MiKTeX\miktex\bin\x64"),
                r"C:\Program Files\MiKTeX\miktex\bin\x64",
                r"C:\MiKTeX\miktex\bin\x64"
            ]
            
            for miktex_path in miktex_paths:
                if os.path.exists(miktex_path):
                    # Add to PATH if not already there
                    current_path = os.environ.get('PATH', '')
                    if miktex_path not in current_path:
                        os.environ['PATH'] = f"{miktex_path};{current_path}"
                        logger.info(f"Added MiKTeX to PATH: {miktex_path}")
                    break
            else:
                logger.warning("MiKTeX not found in common installation paths")
    
    def _install_required_packages(self):
        """Install common LaTeX packages needed for resumes."""
        if platform.system() == "Windows":
            required_packages = [
                'altacv',      # The AltaCV class
                'fontawesome', # Font Awesome icons
                'academicons', # Academic icons
                'ragged2e',    # Text alignment
                'geometry',    # Page geometry
                'xcolor',      # Colors
                'hyperref',    # Hyperlinks
                'enumitem',    # List formatting
                'fontspec',    # Font specifications (for XeLaTeX)
                'polyglossia', # Language support
                'microtype'    # Typography improvements
            ]
            
            for package in required_packages:
                try:
                    cmd = ['miktex', 'packages', 'install', package]
                    subprocess.run(cmd, capture_output=True, timeout=30)
                except Exception:
                    pass  # Continue if installation fails
    
    def _install_missing_packages_from_error(self, error_msg: str):
        """Try to install packages mentioned in error messages."""
        if platform.system() == "Windows":
            # Extract package names from common error patterns
            import re
            
            # Pattern: "File `package.sty' not found"
            sty_matches = re.findall(r"File `([^']+)\.sty' not found", error_msg)
            # Pattern: "! LaTeX Error: File `package.cls' not found"  
            cls_matches = re.findall(r"File `([^']+)\.cls' not found", error_msg)
            
            packages = set(sty_matches + cls_matches)
            
            for package in packages:
                try:
                    logger.info(f"Attempting to install package: {package}")
                    cmd = ['miktex', 'packages', 'install', package]
                    subprocess.run(cmd, capture_output=True, timeout=30)
                except Exception as e:
                    logger.warning(f"Failed to install package {package}: {e}")
    
    def compile_latex_to_pdf(self, tex_content: str, cls_content: str, 
                           filename: str = "resume") -> Tuple[bool, str, Optional[bytes]]:
        """
        Compile LaTeX content to PDF.
        
        Args:
            tex_content: LaTeX document content
            cls_content: LaTeX class content
            filename: Base filename (without extension)
        
        Returns:
            Tuple of (success, message, pdf_bytes)
        """
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Always use "resume" as the base name for LaTeX files to match \documentclass{resume}
                # But still use the provided filename for the final PDF
                tex_path = Path(temp_dir) / "resume.tex"
                cls_path = Path(temp_dir) / "resume.cls"
                
                with open(tex_path, 'w', encoding='utf-8') as f:
                    f.write(tex_content)
                
                with open(cls_path, 'w', encoding='utf-8') as f:
                    f.write(cls_content)
                
                # Try to compile with different engines
                pdf_bytes = None
                last_error = ""
                
                # Install required packages first
                self._install_required_packages()
                
                for engine in self.latex_engines:
                    success, error, pdf_bytes = self._compile_with_engine(
                        tex_path, engine, temp_dir
                    )
                    
                    if success and pdf_bytes:
                        return True, f"Successfully compiled with {engine}", pdf_bytes
                    
                    # Try to install missing packages and retry once
                    if error and ("not found" in error or "missing" in error.lower()):
                        logger.info(f"Installing missing packages for {engine}...")
                        self._install_missing_packages_from_error(error)
                        
                        # Retry compilation
                        success, retry_error, pdf_bytes = self._compile_with_engine(
                            tex_path, engine, temp_dir
                        )
                        
                        if success and pdf_bytes:
                            return True, f"Successfully compiled with {engine} after installing packages", pdf_bytes
                    
                    last_error = error
                    logger.warning(f"Failed to compile with {engine}: {error}")
                
                return False, f"Compilation failed with all engines. Last error: {last_error}", None
                
            except Exception as e:
                logger.error(f"PDF compilation error: {e}")
                return False, f"Compilation error: {str(e)}", None
    
    def _compile_with_engine(self, tex_path: Path, engine: str, 
                           work_dir: str) -> Tuple[bool, str, Optional[bytes]]:
        """Compile with a specific LaTeX engine."""
        
        try:
            # Check if engine is available
            if not self._is_engine_available(engine):
                return False, f"{engine} not available", None
            
            # Run compilation twice for better results (bibliography, cross-references)
            cmd = [
                engine,
                '-interaction=nonstopmode',
                '-output-directory=' + work_dir,
                '-halt-on-error',
                str(tex_path)
            ]
            
            # First compilation
            result1 = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=60  # Increased timeout
            )
            
            # Second compilation for cross-references
            result = subprocess.run(
                cmd,
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            # Check for PDF output (always named "resume.pdf" since tex file is "resume.tex")
            pdf_path = Path(work_dir) / "resume.pdf"
            
            if pdf_path.exists() and pdf_path.stat().st_size > 0:
                with open(pdf_path, 'rb') as f:
                    pdf_bytes = f.read()
                return True, "Success", pdf_bytes
            else:
                # Get detailed error information
                error_msg = ""
                if result.stderr:
                    error_msg += f"STDERR: {result.stderr}\n"
                if result.stdout:
                    error_msg += f"STDOUT: {result.stdout}\n"
                
                # Check for log file for more details  
                log_path = Path(work_dir) / "resume.log"
                if log_path.exists():
                    try:
                        with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                            log_content = f.read()
                            # Extract key error information
                            error_lines = [line for line in log_content.split('\n') if 'error' in line.lower() or 'failed' in line.lower()]
                            if error_lines:
                                error_msg += f"LOG ERRORS: {'; '.join(error_lines[:3])}"
                    except Exception:
                        pass
                
                return False, f"No PDF generated. {error_msg.strip()}", None
                
        except subprocess.TimeoutExpired:
            return False, "Compilation timeout", None
        except FileNotFoundError:
            return False, f"{engine} not found", None
        except Exception as e:
            return False, str(e), None
    
    def _is_engine_available(self, engine: str) -> bool:
        """Check if LaTeX engine is available."""
        try:
            result = subprocess.run(
                [engine, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0
        except:
            return False
    
    def create_preview_image(self, pdf_bytes: bytes) -> Optional[str]:
        """
        Convert PDF to image for preview.
        
        Args:
            pdf_bytes: PDF file content as bytes
        
        Returns:
            Base64 encoded image string or None
        """
        try:
            # Try using pdf2image if available
            try:
                from pdf2image import convert_from_bytes
                
                images = convert_from_bytes(pdf_bytes, first_page=1, last_page=1, dpi=150)
                
                if images:
                    import io
                    img_buffer = io.BytesIO()
                    images[0].save(img_buffer, format='PNG')
                    img_base64 = base64.b64encode(img_buffer.getvalue()).decode()
                    return img_base64
                    
            except ImportError:
                logger.warning("pdf2image not available, trying alternative preview")
            
            # Fallback: Save PDF and indicate preview not available
            return None
            
        except Exception as e:
            logger.error(f"Preview generation error: {e}")
            return None
    
    def get_latex_installation_status(self) -> dict:
        """Check LaTeX installation status."""
        status = {
            'latex_available': False,
            'engines': {},
            'recommended_engine': None,
            'installation_guide': ""
        }
        
        # Check each engine
        for engine in self.latex_engines:
            status['engines'][engine] = self._is_engine_available(engine)
            
            if status['engines'][engine] and not status['recommended_engine']:
                status['recommended_engine'] = engine
        
        status['latex_available'] = any(status['engines'].values())
        
        if not status['latex_available']:
            status['installation_guide'] = self._get_installation_guide()
        
        return status
    
    def _get_installation_guide(self) -> str:
        """Get LaTeX installation guide based on OS."""
        import platform
        
        os_name = platform.system().lower()
        
        if 'windows' in os_name:
            return """
To install LaTeX on Windows:
1. Download MiKTeX from https://miktex.org/download
2. Run the installer with default settings
3. Restart your computer
4. The application will automatically install missing packages
"""
        elif 'darwin' in os_name:  # macOS
            return """
To install LaTeX on macOS:
1. Download MacTeX from https://www.tug.org/mactex/
2. Run the installer (requires ~4GB space)
3. Restart your terminal/application
4. Alternatively, use Homebrew: brew install --cask mactex
"""
        else:  # Linux
            return """
To install LaTeX on Linux:
Ubuntu/Debian: sudo apt-get install texlive-full
CentOS/RHEL: sudo yum install texlive-scheme-full
Arch: sudo pacman -S texlive-most
"""

class PreviewService:
    """Service for handling resume previews."""
    
    def __init__(self):
        self.compiler = PDFCompiler()
    
    def generate_preview(self, tex_content: str, cls_content: str) -> dict:
        """
        Generate preview for LaTeX content.
        
        Returns:
            Dict with preview data, compilation status, and messages
        """
        
        result = {
            'success': False,
            'pdf_available': False,
            'preview_image': None,
            'pdf_base64': None,
            'message': '',
            'latex_status': self.compiler.get_latex_installation_status()
        }
        
        # Check if LaTeX is available
        if not result['latex_status']['latex_available']:
            result['message'] = "LaTeX not installed. Preview unavailable."
            result['installation_guide'] = result['latex_status']['installation_guide']
            return result
        
        # Try to compile
        success, message, pdf_bytes = self.compiler.compile_latex_to_pdf(
            tex_content, cls_content
        )
        
        result['success'] = success
        result['message'] = message
        
        if success and pdf_bytes:
            result['pdf_available'] = True
            result['pdf_base64'] = base64.b64encode(pdf_bytes).decode()
            
            # Generate preview image
            preview_img = self.compiler.create_preview_image(pdf_bytes)
            if preview_img:
                result['preview_image'] = preview_img
        
        return result
    
    def compile_and_download(self, tex_content: str, cls_content: str, 
                           filename: str = "resume") -> Tuple[bool, str, Optional[bytes]]:
        """Compile LaTeX and return PDF for download."""
        return self.compiler.compile_latex_to_pdf(tex_content, cls_content, filename)

