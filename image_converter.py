#!/usr/bin/env python3
"""
Image conversion utilities for PDF to image and HTML to image conversion.
Used for visual comparison in the iterative template matching system.
"""

import os
import io
import tempfile
import logging
from typing import Optional, List, Tuple
from pathlib import Path

# Import libraries with fallbacks
try:
    from pdf2image import convert_from_bytes, convert_from_path
    PDF2IMAGE_AVAILABLE = True
except ImportError:
    PDF2IMAGE_AVAILABLE = False

try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

try:
    import wkhtmltopdf
    WKHTMLTOPDF_AVAILABLE = True
except ImportError:
    WKHTMLTOPDF_AVAILABLE = False

logger = logging.getLogger(__name__)

class ImageConverter:
    """Utility class for converting PDFs and HTML to images."""
    
    def __init__(self):
        """Initialize the image converter."""
        self.temp_dir = tempfile.gettempdir()
        
    def pdf_to_image(self, pdf_data: bytes, dpi: int = 200, page_num: int = 0) -> Optional[bytes]:
        """
        Convert PDF to image.
        
        Args:
            pdf_data: PDF file as bytes
            dpi: Resolution for conversion (default: 200)
            page_num: Page number to convert (0-based, default: first page)
            
        Returns:
            Image as bytes (JPEG format) or None if failed
        """
        if not PDF2IMAGE_AVAILABLE:
            logger.error("pdf2image library not available. Install with: pip install pdf2image")
            return None
            
        try:
            # Convert PDF to images
            images = convert_from_bytes(
                pdf_data,
                dpi=dpi,
                first_page=page_num + 1,
                last_page=page_num + 1,
                fmt='jpeg'
            )
            
            if not images:
                logger.error("No images generated from PDF")
                return None
                
            # Convert PIL Image to bytes
            img_bytes = io.BytesIO()
            images[0].save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"PDF to image conversion failed: {e}")
            return None
    
    def pdf_to_images_all_pages(self, pdf_data: bytes, dpi: int = 200, resume_name: str = "resume") -> List[Tuple[bytes, str]]:
        """
        Convert all pages of PDF to images with proper naming.
        
        Args:
            pdf_data: PDF file as bytes
            dpi: Resolution for conversion (default: 200)
            resume_name: Base name for the resume (used in image naming)
            
        Returns:
            List of tuples: (image_bytes, image_name)
        """
        if not PDF2IMAGE_AVAILABLE:
            logger.error("pdf2image library not available. Install with: pip install pdf2image")
            return []
            
        try:
            # Convert all pages of PDF to images
            images = convert_from_bytes(pdf_data, dpi=dpi, fmt='jpeg')
            
            if not images:
                logger.error("No images generated from PDF")
                return []
            
            results = []
            for i, image in enumerate(images):
                # Convert PIL Image to bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                # Create descriptive name
                page_name = f"{resume_name}_page_{i+1}.jpg"
                results.append((img_bytes.getvalue(), page_name))
            
            return results
            
        except Exception as e:
            logger.error(f"PDF to images conversion failed: {e}")
            return []
    
    def pdf_file_to_images_all_pages(self, pdf_path: str, dpi: int = 200, resume_name: str = None) -> List[Tuple[bytes, str]]:
        """
        Convert all pages of PDF file to images with proper naming.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion (default: 200)
            resume_name: Base name for the resume (defaults to filename without extension)
            
        Returns:
            List of tuples: (image_bytes, image_name)
        """
        if not PDF2IMAGE_AVAILABLE:
            logger.error("pdf2image library not available. Install with: pip install pdf2image")
            return []
            
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return []
        
        if resume_name is None:
            resume_name = Path(pdf_path).stem  # Get filename without extension
            
        try:
            # Convert all pages of PDF to images
            images = convert_from_path(pdf_path, dpi=dpi, fmt='jpeg')
            
            if not images:
                logger.error("No images generated from PDF file")
                return []
            
            results = []
            for i, image in enumerate(images):
                # Convert PIL Image to bytes
                img_bytes = io.BytesIO()
                image.save(img_bytes, format='JPEG', quality=95)
                img_bytes.seek(0)
                
                # Create descriptive name
                page_name = f"{resume_name}_page_{i+1}.jpg"
                results.append((img_bytes.getvalue(), page_name))
            
            return results
            
        except Exception as e:
            logger.error(f"PDF file to images conversion failed: {e}")
            return []
    
    def pdf_file_to_image(self, pdf_path: str, dpi: int = 200, page_num: int = 0) -> Optional[bytes]:
        """
        Convert PDF file to image.
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion (default: 200)
            page_num: Page number to convert (0-based, default: first page)
            
        Returns:
            Image as bytes (JPEG format) or None if failed
        """
        if not PDF2IMAGE_AVAILABLE:
            logger.error("pdf2image library not available. Install with: pip install pdf2image")
            return None
            
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file not found: {pdf_path}")
            return None
            
        try:
            # Convert PDF file to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=page_num + 1,
                last_page=page_num + 1,
                fmt='jpeg'
            )
            
            if not images:
                logger.error("No images generated from PDF file")
                return None
                
            # Convert PIL Image to bytes
            img_bytes = io.BytesIO()
            images[0].save(img_bytes, format='JPEG', quality=95)
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"PDF file to image conversion failed: {e}")
            return None
    
    def html_to_image_selenium(self, html_content: str, width: int = 1200, height: int = 1600) -> Optional[bytes]:
        """
        Convert HTML to image using Selenium WebDriver.
        
        Args:
            html_content: HTML content as string
            width: Browser width (default: 1200)
            height: Browser height (default: 1600)
            
        Returns:
            Image as bytes (PNG format) or None if failed
        """
        if not SELENIUM_AVAILABLE:
            logger.error("Selenium not available. Install with: pip install selenium")
            return None
            
        driver = None
        temp_file = None
        
        try:
            # Create temporary HTML file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            # Setup Chrome options
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            chrome_options.add_argument('--disable-gpu')
            chrome_options.add_argument(f'--window-size={width},{height}')
            chrome_options.add_argument('--hide-scrollbars')
            
            # Initialize WebDriver
            driver = webdriver.Chrome(options=chrome_options)
            driver.set_window_size(width, height)
            
            # Load HTML file - fix Windows file path
            file_path = temp_file.name.replace('\\', '/')
            if not file_path.startswith('/'):
                file_path = '/' + file_path
            driver.get(f'file://{file_path}')
            
            # Wait for page to load completely with timeout handling
            try:
                WebDriverWait(driver, 15).until(
                    lambda d: d.execute_script('return document.readyState') == 'complete'
                )
                
                # Additional wait for fonts and styles to load
                import time
                time.sleep(3)
                
                # Set page dimensions before screenshot
                driver.execute_script(f"document.body.style.width = '{width}px'")
                driver.execute_script(f"document.body.style.height = '{height}px'")
                
                # Take screenshot
                screenshot = driver.get_screenshot_as_png()
                
                return screenshot
                
            except Exception as wait_error:
                logger.warning(f"Wait timeout or error: {wait_error}, attempting screenshot anyway")
                # Try to take screenshot anyway
                try:
                    screenshot = driver.get_screenshot_as_png()
                    return screenshot
                except Exception as screenshot_error:
                    logger.error(f"Screenshot failed: {screenshot_error}")
                    return None
            
        except Exception as e:
            logger.error(f"HTML to image conversion (Selenium) failed: {e}")
            return None
            
        finally:
            # Clean up
            if driver:
                try:
                    driver.quit()
                except:
                    pass
                    
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def html_to_image_playwright(self, html_content: str, width: int = 1200, height: int = 1600) -> Optional[bytes]:
        """
        Convert HTML to image using Playwright (alternative to Selenium).
        
        Args:
            html_content: HTML content as string
            width: Browser width (default: 1200)
            height: Browser height (default: 1600)
            
        Returns:
            Image as bytes (PNG format) or None if failed
        """
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.error("Playwright not available. Install with: pip install playwright")
            return None
            
        temp_file = None
        
        try:
            # Create temporary HTML file
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
            temp_file.write(html_content)
            temp_file.close()
            
            with sync_playwright() as p:
                # Launch browser
                browser = p.chromium.launch(headless=True)
                page = browser.new_page()
                
                # Set viewport size
                page.set_viewport_size({"width": width, "height": height})
                
                # Navigate to HTML file - fix Windows file path
                file_path = temp_file.name.replace('\\', '/')
                if not file_path.startswith('/'):
                    file_path = '/' + file_path
                
                page.goto(f'file://{file_path}')
                
                # Wait for page to load with multiple strategies
                try:
                    page.wait_for_load_state('domcontentloaded', timeout=10000)
                    page.wait_for_load_state('networkidle', timeout=15000)
                    
                    # Additional wait for fonts and styles
                    page.wait_for_timeout(2000)
                    
                    # Set viewport explicitly
                    page.set_viewport_size({"width": width, "height": height})
                    
                    # Take screenshot with error handling
                    screenshot = page.screenshot(full_page=True, type='png', timeout=30000)
                    
                    browser.close()
                    return screenshot
                    
                except Exception as page_error:
                    logger.warning(f"Playwright page error: {page_error}, attempting screenshot anyway")
                    try:
                        screenshot = page.screenshot(full_page=True, type='png')
                        browser.close()
                        return screenshot
                    except Exception as screenshot_error:
                        logger.error(f"Playwright screenshot failed: {screenshot_error}")
                        browser.close()
                        return None
                
        except Exception as e:
            logger.error(f"HTML to image conversion (Playwright) failed: {e}")
            return None
            
        finally:
            if temp_file and os.path.exists(temp_file.name):
                try:
                    os.unlink(temp_file.name)
                except:
                    pass
    
    def html_to_image(self, html_content: str, width: int = 1200, height: int = 1600, method: str = "auto") -> Optional[bytes]:
        """
        Convert HTML to image using the best available method with comprehensive fallback.
        
        Args:
            html_content: HTML content as string
            width: Browser width (default: 1200)
            height: Browser height (default: 1600)
            method: Conversion method ("auto", "selenium", "playwright", "api_fallback")
            
        Returns:
            Image as bytes (PNG format) or None if failed
        """
        methods_tried = []
        
        # Try Selenium first if available and requested
        if method == "selenium" or (method == "auto" and SELENIUM_AVAILABLE):
            methods_tried.append("selenium")
            try:
                result = self.html_to_image_selenium(html_content, width, height)
                if result:
                    logger.info("Successfully converted HTML to image using Selenium")
                    return result
            except Exception as e:
                logger.warning(f"Selenium method failed: {e}")
                
        # Try Playwright as fallback
        if method == "playwright" or method == "auto":
            methods_tried.append("playwright")
            try:
                result = self.html_to_image_playwright(html_content, width, height)
                if result:
                    logger.info("Successfully converted HTML to image using Playwright")
                    return result
            except Exception as e:
                logger.warning(f"Playwright method failed: {e}")
        
        # Try API-based fallback (if available)
        if method == "auto" or method == "api_fallback":
            methods_tried.append("api_fallback")
            try:
                result = self._html_to_image_api_fallback(html_content, width, height)
                if result:
                    logger.info("Successfully converted HTML to image using API fallback")
                    return result
            except Exception as e:
                logger.warning(f"API fallback method failed: {e}")
        
        # Generate error image as final fallback
        methods_tried.append("error_image")
        try:
            result = self._generate_error_image(width, height, methods_tried)
            if result:
                logger.warning("Generated error placeholder image as final fallback")
                return result
        except Exception as e:
            logger.error(f"Even error image generation failed: {e}")
                
        logger.error(f"All HTML to image conversion methods failed. Tried: {methods_tried}")
        return None
    
    def _html_to_image_api_fallback(self, html_content: str, width: int, height: int) -> Optional[bytes]:
        """
        API-based fallback for HTML to image conversion.
        This would use a service like htmlcsstoimage.com or similar.
        """
        # This is a placeholder for API-based conversion
        # Could implement services like:
        # - htmlcsstoimage.com
        # - htmlpdf.app
        # - webpage-screenshot APIs
        
        logger.info("API-based HTML to image conversion not implemented yet")
        return None
    
    def _generate_error_image(self, width: int, height: int, methods_tried: list) -> Optional[bytes]:
        """
        Generate an error placeholder image when all conversion methods fail.
        """
        try:
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a white background image
            img = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(img)
            
            # Try to use a default font, fall back to default if not available
            try:
                font_large = ImageFont.truetype("arial.ttf", 36)
                font_medium = ImageFont.truetype("arial.ttf", 20)
                font_small = ImageFont.truetype("arial.ttf", 16)
            except:
                font_large = ImageFont.load_default()
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Draw error message
            error_title = "HTML to Image Conversion Failed"
            draw.text((width//2 - 200, height//2 - 100), error_title, fill='red', font=font_large)
            
            error_msg = "Unable to convert HTML resume to image for template matching"
            draw.text((width//2 - 250, height//2 - 50), error_msg, fill='black', font=font_medium)
            
            methods_msg = f"Methods tried: {', '.join(methods_tried[:-1])}"  # Exclude 'error_image' itself
            draw.text((width//2 - 200, height//2), methods_msg, fill='gray', font=font_small)
            
            suggestion = "The resume generation will continue without template matching"
            draw.text((width//2 - 220, height//2 + 30), suggestion, fill='gray', font=font_small)
            
            # Convert PIL image to bytes
            img_bytes = io.BytesIO()
            img.save(img_bytes, format='PNG')
            img_bytes.seek(0)
            
            return img_bytes.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to generate error image: {e}")
            return None
    
    def get_available_methods(self) -> dict:
        """
        Get information about available conversion methods.
        
        Returns:
            Dictionary with availability status of different methods
        """
        return {
            "pdf2image": PDF2IMAGE_AVAILABLE,
            "selenium": SELENIUM_AVAILABLE,
            "playwright": False,  # Check during runtime
            "wkhtmltopdf": WKHTMLTOPDF_AVAILABLE
        }
    
    def install_dependencies(self) -> List[str]:
        """
        Get list of commands to install missing dependencies.
        
        Returns:
            List of pip install commands for missing dependencies
        """
        commands = []
        
        if not PDF2IMAGE_AVAILABLE:
            commands.append("pip install pdf2image")
            
        if not SELENIUM_AVAILABLE:
            commands.append("pip install selenium")
            commands.append("# Also need to install ChromeDriver: https://chromedriver.chromium.org/")
            
        return commands

# Global instance for easy import
image_converter = ImageConverter()