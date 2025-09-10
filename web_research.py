#!/usr/bin/env python3
"""
Web Research Service - Company research and information gathering for cover letters.
"""

import logging
import requests
import time
import re
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import urljoin, urlparse, quote_plus
import json

logger = logging.getLogger(__name__)

class CompanyResearchService:
    """Service for researching companies and gathering relevant information."""
    
    def __init__(self):
        """Initialize the company research service."""
        self.client = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })
        logger.info("Company Research Service initialized")
    
    def set_client(self, openrouter_client):
        """Set the OpenRouter client for AI-powered features."""
        self.client = openrouter_client
        logger.info("OpenRouter client set for company research service")
    
    def research_company(self, company_name: str, max_sources: int = 3) -> List[Tuple[str, str]]:
        """
        Research a company and gather information from multiple sources.
        
        Args:
            company_name: Name of the company to research
            max_sources: Maximum number of sources to gather
            
        Returns:
            List of (source_url, content) tuples
        """
        
        logger.info(f"🔍 Starting company research for: {company_name}")
        
        if not company_name or not company_name.strip():
            logger.warning("Empty company name provided")
            return []
        
        research_results = []
        
        try:
            # First try DuckDuckGo search to find relevant URLs
            ddg_urls = self._search_duckduckgo(company_name, max_results=max_sources)
            logger.info(f"🦆 DuckDuckGo found {len(ddg_urls)} URLs: {ddg_urls[:3]}...")
            
            # Combine DuckDuckGo results with generated URLs and fallback URLs
            generated_urls = self._generate_company_urls(company_name)
            fallback_urls = self._get_fallback_urls(company_name)
            potential_urls = ddg_urls + generated_urls + fallback_urls
            logger.info(f"🔗 Total {len(potential_urls)} potential URLs to try (DDG: {len(ddg_urls)}, Generated: {len(generated_urls)}, Fallback: {len(fallback_urls)})")
            
            # Try to visit each URL and extract information
            successful_extractions = 0
            for url in potential_urls[:max_sources * 3]:  # Try more than needed in case some fail
                if successful_extractions >= max_sources:
                    break
                
                logger.info(f"📥 Attempting to visit ({successful_extractions + 1}/{max_sources}): {url}")
                
                try:
                    content = self._fetch_website_content(url)
                    if content:
                        # Extract relevant information using AI if available
                        if self.client:
                            extracted_info = self._extract_company_info_ai(content, company_name, url)
                        else:
                            extracted_info = self._extract_company_info_basic(content, company_name)
                        
                        if extracted_info and len(extracted_info.strip()) > 100:
                            research_results.append((url, extracted_info))
                            successful_extractions += 1
                            logger.info(f"🎯 AI EXTRACTION SUCCESS: {url} - {len(extracted_info)} chars of relevant info")
                        else:
                            logger.warning(f"⚠️ Limited content extracted from {url}")
                    else:
                        logger.error(f"❌ DOWNLOAD FAILED (empty): {url}")
                        
                except Exception as e:
                    logger.error(f"❌ EXTRACTION ERROR for {url}: {e}")
                    continue
                
                # Rate limiting
                time.sleep(1.5)
            
            logger.info(f"📊 AI RESEARCH SUMMARY for '{company_name}':")
            logger.info(f"   🎯 Successful extractions: {successful_extractions}/{max_sources}")
            logger.info(f"   📄 Total content gathered: {sum(len(content) for _, content in research_results)} chars")
            
            return research_results
            
        except Exception as e:
            logger.error(f"Company research failed for {company_name}: {e}")
            return []
    
    def _generate_company_urls(self, company_name: str) -> List[str]:
        """Generate potential URLs for a company."""
        
        # Clean company name
        clean_name = re.sub(r'[^\w\s-]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)  # Remove spaces
        
        # Generate variations
        variations = [
            clean_name,
            clean_name.replace('-', ''),
            clean_name.replace('inc', '').replace('llc', '').replace('ltd', ''),
        ]
        
        urls = []
        for variation in variations[:3]:  # Limit variations
            if variation:
                urls.extend([
                    f"https://www.{variation}.com",
                    f"https://{variation}.com",
                    f"https://www.{variation}.net",
                    f"https://{variation}.net",
                    f"https://www.{variation}.org"
                ])
        
        # Add about pages
        for base_url in urls[:5]:  # Only add about pages for first few
            urls.append(f"{base_url}/about")
            urls.append(f"{base_url}/company")
            urls.append(f"{base_url}/about-us")
        
        return urls[:15]  # Return first 15 URLs
    
    def _search_duckduckgo(self, company_name: str, max_results: int = 5) -> List[str]:
        """Search DuckDuckGo for company information URLs using web scraping."""
        
        logger.info(f"🦆 Searching DuckDuckGo for: {company_name}")
        
        try:
            # Use web scraping approach since API doesn't return search results
            query = f"{company_name} company about careers"
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            logger.info(f"🔍 DuckDuckGo search URL: {search_url}")
            
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code != 200:
                logger.warning(f"DuckDuckGo search failed with status {response.status_code}")
                return []
            
            # Simple HTML parsing to extract URLs
            content = response.text
            urls = []
            
            # Look for result links in the HTML
            import re
            # Pattern to find URLs in DuckDuckGo results
            url_pattern = r'href="(/l/\?uddg=[^"]+)"'
            matches = re.findall(url_pattern, content)
            
            for match in matches[:max_results * 2]:
                # Decode the DuckDuckGo redirect URL
                try:
                    from urllib.parse import unquote
                    decoded = unquote(match)
                    # Extract actual URL from DuckDuckGo's redirect
                    if 'uddg=' in decoded:
                        actual_url = decoded.split('uddg=')[1].split('&')[0]
                        actual_url = unquote(actual_url)
                        if actual_url.startswith('http') and self._is_relevant_url(actual_url, company_name):
                            urls.append(actual_url)
                except:
                    continue
            
            # Also try direct pattern matching for URLs
            direct_pattern = r'https?://[^\s<>"\']+\.(?:com|org|net|edu|gov|io|co)[^\s<>"\']*'
            direct_matches = re.findall(direct_pattern, content)
            
            for url in direct_matches:
                if self._is_relevant_url(url, company_name) and url not in urls:
                    urls.append(url)
                if len(urls) >= max_results:
                    break
            
            logger.info(f"🦆 DuckDuckGo found {len(urls)} relevant URLs")
            return urls[:max_results]
            
        except Exception as e:
            logger.error(f"DuckDuckGo search failed: {e}")
            # Fallback to known good URLs
            return self._get_fallback_urls(company_name)
    
    def _is_relevant_url(self, url: str, company_name: str) -> bool:
        """Check if a URL is relevant for the company."""
        url_lower = url.lower()
        company_lower = company_name.lower().replace(' ', '')
        
        # Check if company name is in URL
        if company_lower in url_lower:
            return True
        
        # Check for relevant domains
        relevant_domains = [
            'wikipedia.org', 'linkedin.com', 'crunchbase.com',
            'bloomberg.com', 'reuters.com', 'forbes.com',
            'techcrunch.com', 'venturebeat.com'
        ]
        
        return any(domain in url_lower for domain in relevant_domains)
    
    def _get_fallback_urls(self, company_name: str) -> List[str]:
        """Get fallback URLs when search fails."""
        company_lower = company_name.lower().replace(' ', '').replace('inc', '').replace('llc', '')
        
        return [
            f"https://en.wikipedia.org/wiki/{company_name.replace(' ', '_')}",
            f"https://www.crunchbase.com/organization/{company_lower}",
            f"https://www.linkedin.com/company/{company_lower}",
        ]
    
    def _fetch_website_content(self, url: str, timeout: int = 10) -> Optional[str]:
        """Fetch content from a website URL."""
        
        logger.info(f"📡 VISITING WEBSITE: {url}")
        logger.debug(f"🔧 Request headers: {dict(self.session.headers)}")
        
        max_retries = 2
        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=timeout, allow_redirects=True)
                
                logger.info(f"📊 HTTP Response: {response.status_code} {response.reason}")
                
                if response.status_code == 200:
                    content = response.text
                    logger.info(f"📏 Content-Length: {len(content)} characters")
                    logger.info(f"📝 Content-Type: {response.headers.get('content-type', 'unknown')}")
                    
                    return content
                else:
                    logger.warning(f"⚠️ HTTP {response.status_code}: {url}")
                    return None
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"🔌 CONNECTION ERROR for {url}: {e}")
                if attempt < max_retries - 1:
                    retry_delay = 2.0 + attempt
                    logger.info(f"🔄 Retry attempt {attempt + 1} for {url} after {retry_delay}s delay")
                    time.sleep(retry_delay)
                else:
                    return None
            except requests.exceptions.Timeout as e:
                logger.error(f"⏰ TIMEOUT ERROR for {url}: {e}")
                return None
            except Exception as e:
                logger.error(f"⚠️ Attempt {attempt + 1} failed for {url}: {e}")
                if attempt < max_retries - 1:
                    retry_delay = 2.0 + attempt * 0.5
                    logger.info(f"🔄 Retry attempt {attempt + 1} for {url} after {retry_delay}s delay")
                    time.sleep(retry_delay)
                else:
                    return None
        
        return None
    
    def _extract_company_info_ai(self, html_content: str, company_name: str, source_url: str) -> str:
        """Extract company information using AI with improved processing."""
        
        if not self.client:
            return self._extract_company_info_basic(html_content, company_name)
        
        # Better HTML cleaning before sending to AI
        cleaned_content = self._clean_html_content(html_content)
        
        # Truncate content to manageable size but keep more
        truncated_content = cleaned_content[:12000] if len(cleaned_content) > 12000 else cleaned_content
        
        prompt = f"""
You are analyzing a webpage about {company_name} to extract relevant information for job applications and cover letters.

COMPANY: {company_name}
SOURCE: {source_url}

WEBPAGE CONTENT:
{truncated_content}

TASK: Extract key company information that would be valuable for someone writing a cover letter or preparing for a job interview.

EXTRACT AND FORMAT:
• Company Mission/Values: [What the company stands for]
• Products/Services: [Main offerings, key business areas]
• Recent News/Achievements: [Recent accomplishments, awards, milestones]
• Company Culture: [Work environment, values, employee focus]
• Industry Position: [Market leadership, competitive advantages]
• Size/Locations: [Company scale, geographic presence]
• Notable Leadership: [Key executives if mentioned]

REQUIREMENTS:
1. Focus ONLY on factual, relevant information
2. Ignore navigation menus, cookies notices, ads, and generic website elements
3. Use bullet points for easy reading
4. Keep each section concise (1-3 sentences max)
5. If a section has no relevant information, write "Not mentioned"
6. Return ONLY the structured information, no additional commentary

If this webpage doesn't contain meaningful information about {company_name} (e.g., it's an error page, landing page with no content, or unrelated), respond with exactly: "INSUFFICIENT_CONTENT"
        """
        
        try:
            extracted_info = self.client._make_request(prompt, max_tokens=1000, prompt_type="company_research")
            
            if extracted_info and "INSUFFICIENT_CONTENT" not in extracted_info and len(extracted_info.strip()) > 50:
                return extracted_info
            else:
                logger.warning(f"AI found insufficient content for {company_name} from {source_url}")
                return ""
                
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
            return self._extract_company_info_basic(html_content, company_name)
    
    def _clean_html_content(self, html_content: str) -> str:
        """Clean HTML content to make it more suitable for AI processing."""
        import re
        
        # Remove common unwanted elements
        html_content = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<style[^>]*>.*?</style>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<nav[^>]*>.*?</nav>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<header[^>]*>.*?</header>', '', html_content, flags=re.DOTALL)
        html_content = re.sub(r'<footer[^>]*>.*?</footer>', '', html_content, flags=re.DOTALL)
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', html_content)
        
        # Clean up whitespace and special characters
        clean_text = re.sub(r'\s+', ' ', clean_text)
        clean_text = re.sub(r'&[a-zA-Z0-9]+;', ' ', clean_text)  # HTML entities
        clean_text = clean_text.strip()
        
        return clean_text
    
    def _extract_company_info_basic(self, html_content: str, company_name: str) -> str:
        """Extract company information using basic text processing."""
        
        # Remove HTML tags
        clean_text = re.sub(r'<[^>]+>', ' ', html_content)
        clean_text = re.sub(r'\s+', ' ', clean_text).strip()
        
        # Look for paragraphs containing the company name
        sentences = clean_text.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if company_name.lower() in sentence.lower() and len(sentence) > 50:
                relevant_sentences.append(sentence.strip())
        
        # Return first few relevant sentences
        if relevant_sentences:
            return '. '.join(relevant_sentences[:5]) + '.'
        
        # Fallback: return first part of content
        return clean_text[:1000] + '...' if len(clean_text) > 1000 else clean_text