#!/usr/bin/env python3
"""
Resume to LaTeX Generator
A Python system that analyzes resume files (PDF, PNG, DOCX) and generates LaTeX code to recreate them.
"""

import os
import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
from PIL import Image, ImageDraw, ImageFont
import cv2
import numpy as np
try:
    import easyocr
    HAS_EASYOCR = True
except ImportError:
    HAS_EASYOCR = False

try:
    from transformers import TrOCRProcessor, VisionEncoderDecoderModel
    from PIL import Image as PILImage
    HAS_TROCR = True
except (ImportError, ValueError):
    # Handle both ImportError and numpy compatibility issues
    HAS_TROCR = False
from pdf2image import convert_from_path
import fitz  # PyMuPDF
from docx import Document
from docx.shared import Inches
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TextBlock:
    """Represents a block of text with position and styling information."""
    text: str
    x: int
    y: int
    width: int
    height: int
    font_size: int
    is_bold: bool = False
    is_italic: bool = False
    alignment: str = "left"  # left, center, right
    
@dataclass
class ResumeSection:
    """Represents a section of the resume (header, experience, education, etc.)."""
    title: str
    content: List[TextBlock]
    section_type: str  # header, experience, education, skills, etc.
    y_position: int

class DocumentProcessor:
    """Base class for document processing."""
    
    def __init__(self):
        self.text_blocks = []
        self.sections = []
        self.page_width = 0
        self.page_height = 0
    
    def extract_text_blocks(self, file_path: str) -> List[TextBlock]:
        """Extract text blocks from document. To be implemented by subclasses."""
        raise NotImplementedError
    
    def analyze_layout(self) -> None:
        """Analyze the layout and group text blocks into sections."""
        if not self.text_blocks:
            return
            
        # Sort text blocks by y-position (top to bottom)
        sorted_blocks = sorted(self.text_blocks, key=lambda x: x.y)
        
        # Improved section detection with multiple strategies
        sections = self._detect_sections_improved(sorted_blocks)
        
        # Classify sections
        self.sections = []
        for i, section_blocks in enumerate(sections):
            section_type = self._classify_section(section_blocks, i)
            section_title = self._extract_section_title(section_blocks)
            
            resume_section = ResumeSection(
                title=section_title,
                content=section_blocks,
                section_type=section_type,
                y_position=min(block.y for block in section_blocks)
            )
            self.sections.append(resume_section)
    
    def _detect_sections_improved(self, sorted_blocks):
        """Improved section detection using multiple strategies."""
        sections = []
        current_section = []
        
        # Strategy 1: Look for section headers (larger font, bold, specific keywords)
        section_indicators = []
        for i, block in enumerate(sorted_blocks):
            is_section_header = self._is_section_header(block, sorted_blocks, i)
            if is_section_header:
                section_indicators.append(i)
        
        # Strategy 2: Use spacing-based detection as fallback
        if not section_indicators:
            return self._detect_sections_by_spacing(sorted_blocks)
        
        # Create sections based on detected headers
        last_header_idx = 0
        for header_idx in section_indicators:
            if header_idx > last_header_idx:
                section_blocks = sorted_blocks[last_header_idx:header_idx]
                if section_blocks:
                    sections.append(section_blocks)
            last_header_idx = header_idx
        
        # Add remaining blocks as final section
        if last_header_idx < len(sorted_blocks):
            final_section = sorted_blocks[last_header_idx:]
            if final_section:
                sections.append(final_section)
        
        return sections if sections else [sorted_blocks]
    
    def _detect_sections_by_spacing(self, sorted_blocks):
        """Original spacing-based section detection."""
        current_section = []
        sections = []
        last_y = -1
        section_gap_threshold = 25  # Increased threshold
        
        for block in sorted_blocks:
            if last_y != -1 and (block.y - last_y) > section_gap_threshold:
                if current_section:
                    sections.append(current_section)
                    current_section = [block]
            else:
                current_section.append(block)
            
            last_y = block.y + block.height
        
        if current_section:
            sections.append(current_section)
        
        return sections
    
    def _is_section_header(self, block, all_blocks, index):
        """Determine if a text block is likely a section header."""
        text = block.text.lower().strip()
        
        # Check for common section keywords in multiple languages
        section_keywords = [
            # English
            'professional summary', 'summary', 'profile', 'objective',
            'professional experience', 'experience', 'work experience', 'employment',
            'education', 'academic background', 'qualifications',
            'skills', 'technical skills', 'core competencies', 'technologies',
            'projects', 'key projects', 'notable projects',
            'certifications', 'licenses', 'achievements', 'awards',
            'languages', 'publications', 'references',
            # Spanish
            'resumen profesional', 'resumen', 'perfil', 'objetivo',
            'experiencia profesional', 'experiencia', 'experiencia laboral', 'empleo',
            'educación', 'formación académica', 'calificaciones',
            'habilidades', 'competencias', 'tecnologías',
            'proyectos', 'certificaciones', 'logros', 'idiomas',
            # French
            'résumé professionnel', 'résumé', 'profil', 'objectif',
            'expérience professionnelle', 'expérience', 'emploi',
            'éducation', 'formation', 'qualifications',
            'compétences', 'technologies', 'projets',
            'certifications', 'réalisations', 'langues',
            # German
            'berufliches profil', 'zusammenfassung', 'profil', 'ziel',
            'berufserfahrung', 'erfahrung', 'beschäftigung',
            'bildung', 'ausbildung', 'qualifikationen',
            'fähigkeiten', 'kompetenzen', 'technologien',
            'projekte', 'zertifizierungen', 'erfolge', 'sprachen'
        ]
        
        # Exact or partial keyword match
        for keyword in section_keywords:
            if keyword in text or text in keyword:
                return True
        
        # Font size analysis - headers are usually larger
        avg_font_size = sum(b.font_size for b in all_blocks) / len(all_blocks)
        if block.font_size > avg_font_size * 1.2:  # 20% larger than average
            return True
        
        # Bold text that's standalone (likely a header)
        if block.is_bold and len(text.split()) <= 4:
            return True
        
        # All caps text (often used for headers)
        if text.isupper() and len(text) > 2:
            return True
        
        return False
    
    def _classify_section(self, blocks: List[TextBlock], section_index: int) -> str:
        """Classify what type of section this is based on content and position."""
        if section_index == 0:
            return "header"
        
        # Look for common section keywords
        text_content = " ".join([block.text.lower() for block in blocks])
        
        if any(keyword in text_content for keyword in ['experience', 'employment', 'work', 'career']):
            return "experience"
        elif any(keyword in text_content for keyword in ['education', 'academic', 'degree', 'university', 'college']):
            return "education"
        elif any(keyword in text_content for keyword in ['skills', 'technical', 'programming', 'languages']):
            return "skills"
        elif any(keyword in text_content for keyword in ['projects', 'portfolio']):
            return "projects"
        elif any(keyword in text_content for keyword in ['contact', 'phone', 'email', '@']):
            return "contact"
        else:
            return "other"
    
    def _extract_section_title(self, blocks: List[TextBlock]) -> str:
        """Extract the title of a section."""
        if not blocks:
            return ""
        
        # Usually the first or largest text block is the title
        title_block = max(blocks, key=lambda x: x.font_size)
        return title_block.text.strip()

class PDFProcessor(DocumentProcessor):
    """Process PDF files."""
    
    def extract_text_blocks(self, file_path: str) -> List[TextBlock]:
        """Extract text blocks from PDF using PyMuPDF - handles multiple pages."""
        try:
            doc = fitz.open(file_path)
            text_blocks = []
            page_count = doc.page_count
            
            # Set default page dimensions
            self.page_width = 612  # Default A4 width
            self.page_height = 792  # Default A4 height
            
            # Process all pages
            for page_num in range(page_count):
                page = doc[page_num]
                
                # Set page dimensions from first page
                if page_num == 0:
                    self.page_width = page.rect.width
                    self.page_height = page.rect.height
                
                blocks = page.get_text("dict")
                
                for block in blocks["blocks"]:
                    if "lines" in block:
                        for line in block["lines"]:
                            for span in line["spans"]:
                                if span["text"].strip():
                                    # Adjust Y coordinate for multi-page layout
                                    # Add page offset to maintain proper ordering
                                    y_offset = page_num * self.page_height if page_num > 0 else 0
                                    
                                    text_block = TextBlock(
                                        text=span["text"].strip(),
                                        x=int(span["bbox"][0]),
                                        y=int(span["bbox"][1]) + y_offset,
                                        width=int(span["bbox"][2] - span["bbox"][0]),
                                        height=int(span["bbox"][3] - span["bbox"][1]),
                                        font_size=int(span["size"]),
                                        is_bold=bool(span["flags"] & 2**4),
                                        is_italic=bool(span["flags"] & 2**1)
                                    )
                                    text_blocks.append(text_block)
            
            # Store text blocks before closing document
            self.text_blocks = text_blocks
            
            # Close document after processing
            doc.close()
            
            logger.info(f"Processed {page_count} pages, extracted {len(text_blocks)} text blocks")
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return []

class ImageProcessor(DocumentProcessor):
    """Process image files (PNG, JPG) without Tesseract."""
    
    def __init__(self):
        super().__init__()
        self.ocr_method = self._initialize_ocr()
    
    def _initialize_ocr(self):
        """Initialize the best available OCR method."""
        if HAS_EASYOCR:
            try:
                import easyocr
                self.reader = easyocr.Reader(['en'])
                return 'easyocr'
            except Exception as e:
                logger.warning(f"Failed to initialize EasyOCR: {e}")
        
        if HAS_TROCR:
            try:
                self.processor = TrOCRProcessor.from_pretrained('microsoft/trocr-base-printed')
                self.model = VisionEncoderDecoderModel.from_pretrained('microsoft/trocr-base-printed')
                return 'trocr'
            except Exception as e:
                logger.warning(f"Failed to initialize TrOCR: {e}")
        
        logger.warning("No OCR method available. Will attempt manual text detection.")
        return 'manual'
    
    def extract_text_blocks(self, file_path: str) -> List[TextBlock]:
        """Extract text blocks from image using available OCR method."""
        try:
            if self.ocr_method == 'easyocr':
                return self._extract_with_easyocr(file_path)
            elif self.ocr_method == 'trocr':
                return self._extract_with_trocr(file_path)
            else:
                return self._extract_with_manual_detection(file_path)
                
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            return []
    
    def _extract_with_easyocr(self, file_path: str) -> List[TextBlock]:
        """Extract text using EasyOCR."""
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Could not load image")
        
        self.page_height, self.page_width = image.shape[:2]
        
        # Use EasyOCR to detect text
        results = self.reader.readtext(image)
        
        text_blocks = []
        for (bbox, text, confidence) in results:
            if confidence > 0.5 and text.strip():  # Confidence threshold
                # Extract bounding box coordinates
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                
                x, y = int(x1), int(y1)
                width, height = int(x2 - x1), int(y2 - y1)
                
                text_block = TextBlock(
                    text=text.strip(),
                    x=x,
                    y=y,
                    width=width,
                    height=height,
                    font_size=self._estimate_font_size(height),
                    is_bold=self._detect_bold_from_image(image, x, y, width, height),
                    is_italic=False  # EasyOCR doesn't detect italic easily
                )
                text_blocks.append(text_block)
        
        self.text_blocks = text_blocks
        return text_blocks
    
    def _extract_with_trocr(self, file_path: str) -> List[TextBlock]:
        """Extract text using TrOCR (Microsoft's Transformer OCR)."""
        image = PILImage.open(file_path).convert('RGB')
        self.page_width, self.page_height = image.size
        
        # First, detect text regions using OpenCV
        cv_image = cv2.imread(file_path)
        text_regions = self._detect_text_regions(cv_image)
        
        text_blocks = []
        for region in text_regions:
            x, y, w, h = region
            
            # Extract region from PIL image
            region_image = image.crop((x, y, x + w, y + h))
            
            # Use TrOCR to extract text
            pixel_values = self.processor(region_image, return_tensors="pt").pixel_values
            generated_ids = self.model.generate(pixel_values)
            generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=True)[0]
            
            if generated_text.strip():
                text_block = TextBlock(
                    text=generated_text.strip(),
                    x=x,
                    y=y,
                    width=w,
                    height=h,
                    font_size=self._estimate_font_size(h),
                    is_bold=self._detect_bold_from_image(cv_image, x, y, w, h),
                    is_italic=False
                )
                text_blocks.append(text_block)
        
        self.text_blocks = text_blocks
        return text_blocks
    
    def _extract_with_manual_detection(self, file_path: str) -> List[TextBlock]:
        """Extract text regions using computer vision without OCR."""
        logger.warning("No OCR available. Creating placeholder text blocks based on detected regions.")
        
        image = cv2.imread(file_path)
        if image is None:
            raise ValueError("Could not load image")
        
        self.page_height, self.page_width = image.shape[:2]
        
        # Detect text regions using computer vision
        text_regions = self._detect_text_regions(image)
        
        text_blocks = []
        for i, (x, y, w, h) in enumerate(text_regions):
            # Create placeholder text (user will need to manually replace)
            placeholder_text = f"[Text Block {i+1}]"
            
            text_block = TextBlock(
                text=placeholder_text,
                x=x,
                y=y,
                width=w,
                height=h,
                font_size=self._estimate_font_size(h),
                is_bold=self._detect_bold_from_image(image, x, y, w, h),
                is_italic=False
            )
            text_blocks.append(text_block)
        
        logger.info(f"Created {len(text_blocks)} placeholder text blocks. Please manually replace text in the generated LaTeX.")
        self.text_blocks = text_blocks
        return text_blocks
    
    def _detect_text_regions(self, image: np.ndarray) -> List[Tuple[int, int, int, int]]:
        """Detect text regions using computer vision techniques."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply morphological operations to detect text areas
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        
        # Apply different techniques to detect text
        # Method 1: Edge detection + dilation
        edges = cv2.Canny(gray, 50, 150)
        dilated = cv2.dilate(edges, kernel, iterations=2)
        
        # Method 2: Adaptive threshold
        adaptive_thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2
        )
        
        # Combine both methods
        combined = cv2.bitwise_or(dilated, adaptive_thresh)
        
        # Find contours
        contours, _ = cv2.findContours(combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Filter contours to likely text regions
        text_regions = []
        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            
            # Filter based on size and aspect ratio
            if (w > 20 and h > 8 and w < image.shape[1] * 0.9 and h < image.shape[0] * 0.3 and
                w / h > 1.5):  # Text is usually wider than tall
                text_regions.append((x, y, w, h))
        
        # Sort by y-coordinate (top to bottom)
        text_regions.sort(key=lambda r: r[1])
        
        return text_regions
    
    def _detect_bold_from_image(self, image: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
        """Detect if text in region appears bold by analyzing thickness."""
        try:
            # Extract the region
            region = image[y:y+h, x:x+w]
            gray_region = cv2.cvtColor(region, cv2.COLOR_BGR2GRAY)
            
            # Calculate the ratio of dark pixels (text) to total pixels
            _, binary = cv2.threshold(gray_region, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            dark_pixels = np.sum(binary == 0)
            total_pixels = binary.size
            
            # Bold text typically has more dark pixels
            density = dark_pixels / total_pixels if total_pixels > 0 else 0
            
            # Threshold for considering text as bold
            return density > 0.3
            
        except Exception:
            return False
    
    def _estimate_font_size(self, height: int) -> int:
        """Estimate font size based on text height."""
        return max(8, min(24, int(height * 0.8)))

class DOCXProcessor(DocumentProcessor):
    """Process DOCX files."""
    
    def extract_text_blocks(self, file_path: str) -> List[TextBlock]:
        """Extract text blocks from DOCX file."""
        try:
            doc = Document(file_path)
            text_blocks = []
            
            # Approximate page dimensions (A4 in pixels at 96 DPI)
            self.page_width = 612
            self.page_height = 792
            
            y_position = 50  # Start from top margin
            
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    # Get formatting info from the first run
                    font_size = 12
                    is_bold = False
                    is_italic = False
                    alignment = "left"
                    
                    if paragraph.runs:
                        run = paragraph.runs[0]
                        if run.font.size:
                            font_size = int(run.font.size.pt)
                        is_bold = run.bold or False
                        is_italic = run.italic or False
                    
                    # Map alignment
                    if paragraph.alignment == 1:  # CENTER
                        alignment = "center"
                    elif paragraph.alignment == 2:  # RIGHT
                        alignment = "right"
                    
                    text_block = TextBlock(
                        text=paragraph.text.strip(),
                        x=50,  # Left margin
                        y=y_position,
                        width=self.page_width - 100,  # Account for margins
                        height=font_size + 4,
                        font_size=font_size,
                        is_bold=is_bold,
                        is_italic=is_italic,
                        alignment=alignment
                    )
                    text_blocks.append(text_block)
                    y_position += font_size + 8  # Line spacing
            
            self.text_blocks = text_blocks
            return text_blocks
            
        except Exception as e:
            logger.error(f"Error processing DOCX: {e}")
            return []

class LaTeXGenerator:
    """Generate LaTeX code from processed resume data."""
    
    def __init__(self):
        self.template = self._get_base_template()
        self.class_content = self._get_class_content()
    
    def generate(self, sections: List[ResumeSection], output_dir: str = ".") -> Tuple[str, str]:
        """Generate LaTeX .tex and .cls files."""
        
        # Generate the main .tex content
        tex_content = self._generate_tex_content(sections)
        
        # Write files only if output_dir is provided and not "."
        if output_dir and output_dir != ".":
            tex_path = os.path.join(output_dir, "resume.tex")
            cls_path = os.path.join(output_dir, "resume.cls")
            
            with open(tex_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            
            with open(cls_path, 'w', encoding='utf-8') as f:
                f.write(self.class_content)
            
            logger.info(f"Generated LaTeX files: {tex_path}, {cls_path}")
        
        return tex_content, self.class_content
    
    def _generate_tex_content(self, sections: List[ResumeSection]) -> str:
        """Generate the main .tex file content."""
        
        content_parts = []
        header_section = None
        
        # Find header section
        for section in sections:
            if section.section_type == "header":
                header_section = section
                break
        
        # Generate header
        if header_section:
            content_parts.append(self._generate_header(header_section))
        
        # Generate other sections
        for section in sections:
            if section.section_type != "header":
                content_parts.append(self._generate_section(section))
        
        # Combine with template
        document_content = "\n\n".join(content_parts)
        
        tex_content = self.template.replace("{{DOCUMENT_CONTENT}}", document_content)
        
        return tex_content
    
    def _generate_header(self, section: ResumeSection) -> str:
        """Generate header section LaTeX code."""
        
        # Extract name (usually the largest text)
        name_block = max(section.content, key=lambda x: x.font_size)
        name = name_block.text
        
        # Extract contact info
        contact_info = []
        for block in section.content:
            if block != name_block:
                text = block.text
                if '@' in text or 'phone' in text.lower() or text.startswith('+') or text.startswith('('):
                    contact_info.append(text)
        
        header_tex = f"\\name{{{name}}}\n"
        
        if contact_info:
            contact_str = " \\textbullet\\ ".join(contact_info)
            header_tex += f"\\contact{{{contact_str}}}\n"
        
        return header_tex
    
    def _generate_section(self, section: ResumeSection) -> str:
        """Generate a regular section LaTeX code."""
        
        section_title = self._clean_section_title(section.title)
        section_tex = f"\\section{{{section_title}}}\n"
        
        if section.section_type == "experience":
            section_tex += self._generate_experience_section(section)
        elif section.section_type == "education":
            section_tex += self._generate_education_section(section)
        elif section.section_type == "skills":
            section_tex += self._generate_skills_section(section)
        else:
            section_tex += self._generate_generic_section(section)
        
        return section_tex
    
    def _generate_experience_section(self, section: ResumeSection) -> str:
        """Generate experience section with proper formatting."""
        content = []
        
        # Group related content
        items = self._group_experience_items(section.content)
        
        for item in items:
            if 'title' in item and 'company' in item:
                content.append(f"\\resumeItem{{{item['title']}}}{{{item['company']}}}{{{item.get('date', '')}}}")
                if 'description' in item:
                    for desc in item['description']:
                        content.append(f"  \\item {desc}")
        
        return "\n".join(content)
    
    def _generate_education_section(self, section: ResumeSection) -> str:
        """Generate education section."""
        content = []
        
        for block in section.content[1:]:  # Skip title
            if block.font_size > 10:  # Likely degree/school name
                content.append(f"\\resumeItem{{{block.text}}}{{}}{{}}")
        
        return "\n".join(content)
    
    def _generate_skills_section(self, section: ResumeSection) -> str:
        """Generate skills section."""
        skills_text = " ".join([block.text for block in section.content[1:]])  # Skip title
        return f"\\resumeSkills{{{skills_text}}}"
    
    def _generate_generic_section(self, section: ResumeSection) -> str:
        """Generate generic section."""
        content = []
        for block in section.content[1:]:  # Skip title
            content.append(f"\\item {block.text}")
        
        if content:
            return "\\begin{itemize}\n" + "\n".join(content) + "\n\\end{itemize}"
        else:
            return ""
    
    def _group_experience_items(self, blocks: List[TextBlock]) -> List[Dict]:
        """Group text blocks into experience items."""
        # This is a simplified version - in practice, you'd use more sophisticated logic
        items = []
        current_item = {}
        
        for block in blocks[1:]:  # Skip section title
            text = block.text
            
            # Detect job titles, companies, dates based on formatting and content
            if block.is_bold and block.font_size > 11:
                if current_item:
                    items.append(current_item)
                current_item = {'title': text}
            elif re.search(r'\b(inc|ltd|corp|llc|company)\b', text.lower()):
                current_item['company'] = text
            elif re.search(r'\b\d{4}\b', text):  # Contains year
                current_item['date'] = text
            else:
                if 'description' not in current_item:
                    current_item['description'] = []
                current_item['description'].append(text)
        
        if current_item:
            items.append(current_item)
        
        return items
    
    def _clean_section_title(self, title: str) -> str:
        """Clean section title for LaTeX."""
        return re.sub(r'[^\w\s]', '', title).title()
    
    def _get_base_template(self) -> str:
        """Get the base LaTeX template."""
        return r"""
\documentclass[11pt,a4paper,sans]{resume}

\usepackage{hyperref}

\name{}
\contact{}

\begin{document}

\makeheader

{{DOCUMENT_CONTENT}}

\end{document}
"""
    
    def _get_class_content(self) -> str:
        """Get the resume.cls content."""
        return r"""
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{resume}[2024/01/01 Resume class]

\LoadClass[11pt,letterpaper]{article}

\usepackage[parfill]{parskip}
\usepackage{array}
\usepackage{ifthen}
\usepackage[left=0.7in,top=0.6in,right=0.7in,bottom=0.6in]{geometry}
\usepackage{enumitem}

% Define colors
\usepackage{xcolor}
\definecolor{primary}{RGB}{0, 0, 0}
\definecolor{secondary}{RGB}{100, 100, 100}

% Remove page numbers
\pagestyle{empty}

% Name command
\def \name#1{\def\@name{#1}}
\def \@name {}

% Contact command  
\def \contact#1{\def\@contact{#1}}
\def \@contact {}

% Make header
\def \makeheader {
  \begin{center}
    {\Huge \scshape \@name}
    \vspace{0.1in}
    
    \ifthenelse{\equal{\@contact}{}}{}{
      \\
      \@contact
    }
  \end{center}
  \vspace{0.2in}
}

% Section command
\renewcommand{\section}[1]{
  \vspace{0.1in}
  {\Large \scshape #1}
  \vspace{0.05in}
  \hrule
  \vspace{0.1in}
}

% Resume item command
\newcommand{\resumeItem}[3]{
  \vspace{0.05in}
  \begin{tabular*}{\textwidth}{l@{\extracolsep{\fill}}r}
    \textbf{#1} & #3 \\
    \textit{#2} & \\
  \end{tabular*}
  \vspace{-0.1in}
}

% Resume skills command
\newcommand{\resumeSkills}[1]{
  \begin{itemize}[leftmargin=0.1in, label={}]
    \item #1
  \end{itemize}
}

% Custom itemize
\renewenvironment{itemize}{
  \begin{list}{$\cdot$}{
    \setlength{\itemsep}{0pt}
    \setlength{\parsep}{0pt}
    \setlength{\topsep}{0pt}
    \setlength{\partopsep}{0pt}
    \setlength{\leftmargin}{0.2in}
  }
}{
  \end{list}
}
"""

class ResumeAnalyzer:
    """Main class that orchestrates the resume analysis and LaTeX generation."""
    
    def __init__(self):
        self.processors = {
            '.pdf': PDFProcessor(),
            '.png': ImageProcessor(),
            '.jpg': ImageProcessor(),
            '.jpeg': ImageProcessor(),
            '.docx': DOCXProcessor()
        }
        self.latex_generator = LaTeXGenerator()
    
    def analyze(self, file_path: str, output_dir: str = None) -> Tuple[bool, str, str, Dict]:
        """Analyze a resume file and generate LaTeX code."""
        
        file_path = Path(file_path)
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False, "", "", {}
        
        extension = file_path.suffix.lower()
        if extension not in self.processors:
            logger.error(f"Unsupported file type: {extension}")
            return False, "", "", {}
        
        logger.info(f"Processing {file_path} with {extension} processor...")
        
        # Process the document
        processor = self.processors[extension]
        text_blocks = processor.extract_text_blocks(str(file_path))
        
        if not text_blocks:
            logger.error("No text blocks extracted from document")
            return False, "", "", {}
        
        logger.info(f"Extracted {len(text_blocks)} text blocks")
        
        # Analyze layout
        processor.analyze_layout()
        logger.info(f"Identified {len(processor.sections)} sections")
        
        # Generate LaTeX
        tex_content, cls_content = self.latex_generator.generate(
            processor.sections, 
            output_dir
        )
        
        # Create analysis data
        analysis_data = {
            'file_path': str(file_path),
            'sections': [asdict(section) for section in processor.sections],
            'text_blocks': [asdict(block) for block in text_blocks]
        }
        
        logger.info("Analysis complete!")
        return True, tex_content, cls_content, analysis_data
