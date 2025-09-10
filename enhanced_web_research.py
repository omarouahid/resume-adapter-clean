#!/usr/bin/env python3
"""
Enhanced Web Research Service with multiple strategies for reliable company data extraction.
"""

import logging
import requests
import time
import re
import json
import random
from typing import Dict, List, Tuple, Any, Optional
from urllib.parse import quote_plus, urljoin
from bs4 import BeautifulSoup
import cloudscraper

logger = logging.getLogger(__name__)

class EnhancedWebResearch:
    """Enhanced web research service with multiple scraping strategies."""
    
    def __init__(self):
        """Initialize the enhanced research service."""
        self.client = None
        
        # Multiple session types for different scenarios
        self.standard_session = requests.Session()
        self.cloudscraper_session = cloudscraper.create_scraper()
        
        # Rotate user agents to avoid blocking
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        ]
        
        self._configure_sessions()
        logger.info("Enhanced Web Research Service initialized")
    
    def _configure_sessions(self):
        """Configure all session types with proper headers."""
        for session in [self.standard_session, self.cloudscraper_session]:
            session.headers.update({
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.5',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'cross-site',
                'Cache-Control': 'max-age=0'
            })
    
    def set_client(self, openrouter_client):
        """Set the OpenRouter client for AI-powered features."""
        self.client = openrouter_client
        logger.info("OpenRouter client set for enhanced research service")
    
    def research_company(self, company_name: str, max_sources: int = 3) -> List[Tuple[str, str]]:
        """Research company using multiple strategies."""
        logger.info(f"🔍 Starting enhanced research for: {company_name}")
        
        if not company_name or not company_name.strip():
            logger.warning("Empty company name provided")
            return []
        
        research_results = []
        
        try:
            # Strategy 1: Try Google search via SerpAPI (if available)
            search_urls = self._search_multiple_engines(company_name, max_results=max_sources)
            logger.info(f"🔗 Found {len(search_urls)} URLs from search engines")
            
            # Strategy 2: Generate direct company URLs
            direct_urls = self._generate_company_urls(company_name)
            logger.info(f"🏢 Generated {len(direct_urls)} direct company URLs")
            
            # Strategy 3: Use knowledge base URLs
            knowledge_urls = self._get_knowledge_base_urls(company_name)
            logger.info(f"📚 Found {len(knowledge_urls)} knowledge base URLs")
            
            # Combine all URLs, prioritizing search results
            all_urls = search_urls + direct_urls + knowledge_urls
            
            # Remove duplicates while preserving order
            unique_urls = list(dict.fromkeys(all_urls))
            
            successful_extractions = 0
            for url in unique_urls[:max_sources * 4]:  # Try more URLs to ensure success
                if successful_extractions >= max_sources:
                    break
                
                logger.info(f"📥 Attempting extraction ({successful_extractions + 1}/{max_sources}): {url}")
                
                try:
                    content = self._fetch_content_multi_strategy(url)
                    if content:
                        extracted_info = self._extract_with_multiple_methods(content, company_name, url)
                        
                        if extracted_info and len(extracted_info.strip()) > 200:  # Ensure meaningful content
                            research_results.append((url, extracted_info))
                            successful_extractions += 1
                            logger.info(f"✅ SUCCESS: {url} - {len(extracted_info)} chars extracted")
                        else:
                            logger.warning(f"⚠️ Limited content from {url}")
                    else:
                        logger.warning(f"❌ Failed to fetch content from {url}")
                        
                except Exception as e:
                    logger.error(f"❌ Error processing {url}: {e}")
                    continue
                
                # Rate limiting with some randomness
                time.sleep(random.uniform(1.0, 2.0))
            
            logger.info(f"📊 Research completed: {successful_extractions}/{max_sources} sources, {sum(len(content) for _, content in research_results)} total chars")
            return research_results
            
        except Exception as e:
            logger.error(f"Enhanced research failed for {company_name}: {e}")
            return []
    
    def _search_multiple_engines(self, company_name: str, max_results: int = 5) -> List[str]:
        """Search multiple search engines for company information."""
        urls = []
        
        # Try DuckDuckGo HTML search
        urls.extend(self._search_duckduckgo_html(company_name, max_results))
        
        # Try Bing search
        urls.extend(self._search_bing(company_name, max_results))
        
        # If we have SerpAPI key, could add Google here
        # urls.extend(self._search_google_serpapi(company_name, max_results))
        
        return urls
    
    def _search_duckduckgo_html(self, company_name: str, max_results: int = 3) -> List[str]:
        """Enhanced DuckDuckGo search with better parsing."""
        logger.info(f"🦆 Searching DuckDuckGo HTML for: {company_name}")
        
        try:
            query = f"{company_name} company about careers"
            search_url = f"https://html.duckduckgo.com/html/?q={quote_plus(query)}"
            
            # Use cloudscraper to bypass anti-bot
            session = self.cloudscraper_session
            session.headers['User-Agent'] = random.choice(self.user_agents)
            
            response = session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                urls = []
                
                # Find all result links
                for result in soup.find_all('a', class_='result__a'):
                    href = result.get('href')
                    if href and href.startswith('//duckduckgo.com/l/?uddg='):
                        # Decode DDG redirect
                        try:
                            from urllib.parse import unquote
                            actual_url = unquote(href.split('uddg=')[1].split('&')[0])
                            if self._is_relevant_company_url(actual_url, company_name):
                                urls.append(actual_url)
                        except:
                            continue
                
                # Also try direct result URLs
                for link in soup.find_all('a', href=True):
                    href = link['href']
                    if href.startswith('http') and self._is_relevant_company_url(href, company_name):
                        if href not in urls:
                            urls.append(href)
                
                logger.info(f"🦆 DuckDuckGo found {len(urls)} URLs")
                return urls[:max_results]
            else:
                logger.warning(f"DuckDuckGo search failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
        
        return []
    
    def _search_bing(self, company_name: str, max_results: int = 3) -> List[str]:
        """Search Bing for company information."""
        logger.info(f"🔍 Searching Bing for: {company_name}")
        
        try:
            query = f"{company_name} company information about"
            search_url = f"https://www.bing.com/search?q={quote_plus(query)}"
            
            session = self.cloudscraper_session
            session.headers['User-Agent'] = random.choice(self.user_agents)
            
            response = session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                urls = []
                
                # Find organic results
                for result in soup.find_all('h2'):
                    link = result.find('a')
                    if link and link.get('href'):
                        url = link['href']
                        if url.startswith('http') and self._is_relevant_company_url(url, company_name):
                            urls.append(url)
                
                logger.info(f"🔍 Bing found {len(urls)} URLs")
                return urls[:max_results]
            else:
                logger.warning(f"Bing search failed with status {response.status_code}")
                
        except Exception as e:
            logger.error(f"Bing search error: {e}")
        
        return []
    
    def _generate_company_urls(self, company_name: str) -> List[str]:
        """Generate potential direct company URLs."""
        clean_name = re.sub(r'[^\w\s-]', '', company_name.lower())
        clean_name = re.sub(r'\s+', '', clean_name)
        
        variations = [
            clean_name,
            clean_name.replace('-', ''),
            clean_name.replace('inc', '').replace('llc', '').replace('ltd', '').replace('corp', ''),
        ]
        
        urls = []
        for variation in variations[:3]:
            if variation:
                base_urls = [
                    f"https://www.{variation}.com",
                    f"https://{variation}.com",
                    f"https://www.{variation}.net",
                    f"https://www.{variation}.org",
                ]
                
                urls.extend(base_urls)
                
                # Add important pages
                for base in base_urls[:2]:
                    urls.extend([
                        f"{base}/about",
                        f"{base}/about-us", 
                        f"{base}/company",
                        f"{base}/careers",
                    ])
        
        return urls[:20]
    
    def _get_knowledge_base_urls(self, company_name: str) -> List[str]:
        """Get URLs from knowledge bases like Wikipedia, Crunchbase."""
        company_slug = company_name.replace(' ', '_')
        company_lower = company_name.lower().replace(' ', '-').replace('inc', '').replace('llc', '')
        
        return [
            f"https://en.wikipedia.org/wiki/{company_slug}",
            f"https://www.crunchbase.com/organization/{company_lower}",
            f"https://www.linkedin.com/company/{company_lower}/",
            f"https://www.glassdoor.com/Overview/Working-at-{company_slug}-EI_IE.htm",
        ]
    
    def _is_relevant_company_url(self, url: str, company_name: str) -> bool:
        """Check if URL is relevant for the company."""
        url_lower = url.lower()
        company_parts = company_name.lower().split()
        
        # Check if main company name parts are in URL
        for part in company_parts:
            if len(part) > 3 and part in url_lower:  # Skip short words
                return True
        
        # Check for known relevant domains
        relevant_domains = [
            'wikipedia.org', 'crunchbase.com', 'linkedin.com',
            'glassdoor.com', 'bloomberg.com', 'reuters.com',
            'sec.gov', 'investor'
        ]
        
        return any(domain in url_lower for domain in relevant_domains)
    
    def _fetch_content_multi_strategy(self, url: str) -> Optional[str]:
        """Try multiple strategies to fetch content."""
        strategies = [
            ("CloudScraper", self.cloudscraper_session),
            ("Standard Session", self.standard_session),
        ]
        
        for strategy_name, session in strategies:
            try:
                # Rotate user agent
                session.headers['User-Agent'] = random.choice(self.user_agents)
                
                logger.info(f"📡 Trying {strategy_name} for: {url}")
                response = session.get(url, timeout=15, allow_redirects=True)
                
                if response.status_code == 200:
                    logger.info(f"✅ {strategy_name} success: {len(response.text)} chars")
                    return response.text
                else:
                    logger.warning(f"⚠️ {strategy_name} failed: HTTP {response.status_code}")
                    
            except Exception as e:
                logger.warning(f"⚠️ {strategy_name} error: {e}")
                continue
        
        return None
    
    def _extract_with_multiple_methods(self, html_content: str, company_name: str, source_url: str) -> str:
        """Extract content using multiple methods."""
        
        # Method 1: AI extraction (if available)
        if self.client:
            ai_result = self._extract_with_ai(html_content, company_name, source_url)
            if ai_result and len(ai_result.strip()) > 200:
                return ai_result
        
        # Method 2: BeautifulSoup structured extraction
        bs_result = self._extract_with_beautifulsoup(html_content, company_name, source_url)
        if bs_result and len(bs_result.strip()) > 200:
            return bs_result
        
        # Method 3: Regex-based extraction
        regex_result = self._extract_with_regex(html_content, company_name)
        if regex_result and len(regex_result.strip()) > 100:
            return regex_result
        
        return ""
    
    def _extract_with_ai(self, html_content: str, company_name: str, source_url: str) -> str:
        """Extract using AI with enhanced cleaning."""
        try:
            # Better content cleaning
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
                element.decompose()
            
            # Get text content
            clean_text = soup.get_text(separator=' ', strip=True)
            
            # Clean up whitespace
            clean_text = re.sub(r'\s+', ' ', clean_text)
            
            # Truncate for AI processing
            truncated = clean_text[:15000] if len(clean_text) > 15000 else clean_text
            
            prompt = f"""
Extract key company information from this webpage about {company_name}.

COMPANY: {company_name}
SOURCE: {source_url}

CONTENT:
{truncated}

Extract and format the following information in a structured way:

**Company Overview:**
- Mission/Vision/Values
- Main products/services
- Industry focus

**Company Details:**
- Size and locations
- Key leadership
- Recent achievements/news

**Work Environment:**
- Company culture
- Employee benefits/values
- Work environment

REQUIREMENTS:
1. Only include factual information that's actually mentioned in the content
2. Ignore navigation menus, ads, cookie notices, and generic website elements  
3. Use bullet points for readability
4. Keep each section concise (2-3 points max)
5. If no relevant information is found for a section, write "Not mentioned"
6. Focus on information that would be useful for job applications

If this webpage doesn't contain meaningful information about {company_name}, respond with "INSUFFICIENT_INFORMATION".
            """
            
            result = self.client._make_request(prompt, max_tokens=1200, prompt_type="company_research")
            
            if result and "INSUFFICIENT_INFORMATION" not in result:
                return result
            
        except Exception as e:
            logger.error(f"AI extraction failed: {e}")
        
        return ""
    
    def _extract_with_beautifulsoup(self, html_content: str, company_name: str, source_url: str) -> str:
        """Extract using BeautifulSoup parsing."""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'header', 'footer']):
                element.decompose()
            
            extracted_info = []
            
            # Look for specific content patterns
            # About sections
            about_sections = soup.find_all(['div', 'section'], class_=re.compile(r'about|company|mission', re.I))
            for section in about_sections[:3]:
                text = section.get_text(strip=True)[:500]
                if company_name.lower() in text.lower() and len(text) > 50:
                    extracted_info.append(f"About: {text}")
            
            # Meta description
            meta_desc = soup.find('meta', attrs={'name': 'description'})
            if meta_desc and meta_desc.get('content'):
                content = meta_desc['content'][:300]
                if company_name.lower() in content.lower():
                    extracted_info.append(f"Description: {content}")
            
            # Title
            title = soup.find('title')
            if title and company_name.lower() in title.text.lower():
                extracted_info.append(f"Page Title: {title.text.strip()}")
            
            # Paragraphs with company mentions
            paragraphs = soup.find_all('p')
            company_mentions = 0
            for p in paragraphs:
                text = p.get_text(strip=True)
                if company_name.lower() in text.lower() and len(text) > 100:
                    extracted_info.append(f"Content: {text[:400]}")
                    company_mentions += 1
                    if company_mentions >= 3:
                        break
            
            if extracted_info:
                return f"**Source: {source_url}**\n\n" + "\n\n".join(extracted_info)
            
        except Exception as e:
            logger.error(f"BeautifulSoup extraction failed: {e}")
        
        return ""
    
    def _extract_with_regex(self, html_content: str, company_name: str) -> str:
        """Extract using regex patterns."""
        try:
            # Remove HTML tags
            clean_text = re.sub(r'<[^>]+>', ' ', html_content)
            clean_text = re.sub(r'\s+', ' ', clean_text).strip()
            
            # Find sentences mentioning the company
            sentences = clean_text.split('.')
            relevant_sentences = []
            
            for sentence in sentences:
                if company_name.lower() in sentence.lower() and len(sentence.strip()) > 50:
                    relevant_sentences.append(sentence.strip())
                    if len(relevant_sentences) >= 5:
                        break
            
            if relevant_sentences:
                return "Key Information:\n" + "\n".join(f"• {s}." for s in relevant_sentences)
            
        except Exception as e:
            logger.error(f"Regex extraction failed: {e}")
        
        return ""