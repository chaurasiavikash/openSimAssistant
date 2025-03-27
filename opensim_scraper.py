import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import json
from typing import List, Dict, Any, Set
import re

class OpenSimScraper:
    """Scraper for OpenSim documentation"""
    
    def __init__(self, base_urls=None, output_dir="data"):
        # Default OpenSim documentation URLs
        self.base_urls = base_urls or [
            "https://simtk.org/projects/opensim",
            "https://simtk-confluence.stanford.edu/display/OpenSim/User%27s+Guide",
            "https://simtk-confluence.stanford.edu/display/OpenSim/Tutorials"
        ]
        
        self.output_dir = output_dir
        self.visited_urls = set()
        self.documents = []
        
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
    
    def scrape(self, max_pages=50):
        """
        Scrape OpenSim documentation
        
        Args:
            max_pages: Maximum number of pages to scrape
        """
        print(f"Starting to scrape OpenSim documentation (max {max_pages} pages)...")
        
        for base_url in self.base_urls:
            self._scrape_from_url(base_url, max_pages=max_pages)
        
        print(f"Scraping completed. Collected {len(self.documents)} documents.")
        
        # Save the collected documents
        self._save_documents()
        
        return self.documents
    
    def _scrape_from_url(self, url, depth=0, max_depth=3, max_pages=50):
        """
        Recursively scrape from a URL
        
        Args:
            url: URL to scrape
            depth: Current recursion depth
            max_depth: Maximum recursion depth
            max_pages: Maximum number of pages to scrape
        """
        # Check if we've reached the limits
        if depth > max_depth or len(self.visited_urls) >= max_pages or url in self.visited_urls:
            return
        
        # Add to visited URLs
        self.visited_urls.add(url)
        
        print(f"Scraping: {url}")
        
        try:
            # Implement polite scraping with delays
            time.sleep(1)
            
            # Get the page content
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse the page
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Process the page content
            self._process_page(url, soup)
            
            # Find links to follow
            links = self._extract_links(url, soup)
            
            # Follow the links recursively
            for link in links:
                if len(self.visited_urls) < max_pages:
                    self._scrape_from_url(link, depth + 1, max_depth, max_pages)
        
        except Exception as e:
            print(f"Error scraping {url}: {e}")
    
    def _process_page(self, url, soup):
        """
        Process a page and extract content
        
        Args:
            url: URL of the page
            soup: BeautifulSoup object of the page
        """
        # Extract title
        title = self._extract_title(soup)
        
        # Extract content
        content = self._extract_content(soup)
        
        if not content:
            return
        
        # Determine content type and section
        content_type = self._determine_content_type(url, title)
        section = self._determine_section(url, title)
        
        # Create document
        document = {
            "content": content,
            "metadata": {
                "title": title,
                "source": url,
                "section": section,
                "type": content_type
            }
        }
        
        # Add to documents
        self.documents.append(document)
        
        print(f"Added document: {title} ({content_type})")
    
    def _extract_title(self, soup):
        """Extract title from BeautifulSoup object"""
        # Try different approaches for finding the title
        if soup.title and soup.title.string:
            return soup.title.string.strip()
        
        # Look for main heading
        for heading in ['h1', 'h2', 'h3']:
            if soup.find(heading):
                return soup.find(heading).get_text().strip()
        
        return "Unknown Title"
    
    def _extract_content(self, soup):
        """Extract main content from BeautifulSoup object"""
        # Try to find the main content
        # This is site-specific and might need adjustments
        
        # Identify common content containers
        content_selectors = [
            'div.wiki-content', 
            'div.main-content',
            'article',
            'div.content',
            'div.documentation',
            'div#content',
            'div.confluenceContent'
        ]
        
        content = None
        
        # Try each selector
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                content = content_element
                break
        
        # If we couldn't find a content container, use the body
        if not content:
            content = soup.find('body')
        
        if not content:
            return ""
        
        # Remove navigation, headers, footers, etc.
        for element in content.select('nav, header, footer, .sidebar, .navigation, .menu, script, style, .hidden'):
            element.decompose()
        
        # Get the text content
        text = content.get_text(separator='\n', strip=True)
        
        # Clean up the text
        text = re.sub(r'\n{3,}', '\n\n', text)  # Remove excessive newlines
        
        return text
    
    def _extract_links(self, base_url, soup):
        """
        Extract relevant links to follow
        
        Args:
            base_url: Base URL for resolving relative links
            soup: BeautifulSoup object
        
        Returns:
            List of URLs to follow
        """
        links = []
        
        # Extract all links
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href']
            
            # Skip empty links, anchors, javascript, etc.
            if not href or href.startswith('#') or href.startswith('javascript:'):
                continue
            
            # Resolve relative links
            full_url = urljoin(base_url, href)
            
            # Skip external links or non-documentation links
            parsed_url = urlparse(full_url)
            base_parsed = urlparse(base_url)
            
            if parsed_url.netloc != base_parsed.netloc:
                continue
            
            # Skip links to files (e.g., .pdf, .zip)
            if any(full_url.endswith(ext) for ext in ['.pdf', '.zip', '.exe', '.dmg']):
                continue
            
            # Add the link if we haven't visited it yet
            if full_url not in self.visited_urls:
                links.append(full_url)
        
        return links
    
    def _determine_content_type(self, url, title):
        """Determine the content type based on URL and title"""
        # This is heuristic and may need adjustments for different documentation structures
        title_lower = title.lower()
        url_lower = url.lower()
        
        if 'tutorial' in title_lower or 'tutorial' in url_lower:
            return 'tutorial'
        elif 'guide' in title_lower or 'guide' in url_lower:
            return 'guide'
        elif 'api' in title_lower or 'api' in url_lower or 'reference' in title_lower:
            return 'api'
        elif 'how' in title_lower and 'to' in title_lower:
            return 'how-to'
        elif 'faq' in title_lower or 'faq' in url_lower:
            return 'faq'
        elif 'example' in title_lower or 'example' in url_lower:
            return 'example'
        else:
            return 'documentation'
    
    def _determine_section(self, url, title):
        """Determine the section based on URL and title"""
        # Extract section from URL path
        path = urlparse(url).path
        path_parts = path.split('/')
        
        # Try to determine section from URL parts
        for part in path_parts:
            if part and part not in ['display', 'projects', 'opensim']:
                return part.replace('+', ' ').replace('%20', ' ')
        
        # Fallback to a generic section name
        return "General"
    
    def _save_documents(self):
        """Save the collected documents to JSON"""
        output_file = os.path.join(self.output_dir, "opensim_docs.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.documents, f, ensure_ascii=False, indent=2)
        
        print(f"Saved {len(self.documents)} documents to {output_file}")

def main():
    # Create scraper
    scraper = OpenSimScraper()
    
    # Start scraping
    documents = scraper.scrape(max_pages=20)  # Limit to 20 pages for testing
    
    print(f"Collected {len(documents)} documents.")

if __name__ == "__main__":
    main()