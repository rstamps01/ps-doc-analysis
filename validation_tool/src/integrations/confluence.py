import requests
import time
import json
import re
from typing import Dict, Any, Optional, List
from urllib.parse import urljoin
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ConfluenceIntegration:
    """Confluence API integration for reading page content."""
    
    def __init__(self, base_url: str, username: str = None, api_token: str = None, 
                 oauth_token: str = None):
        """
        Initialize Confluence integration.
        
        Args:
            base_url: Confluence instance base URL (e.g., https://company.atlassian.net)
            username: Username for basic auth
            api_token: API token for basic auth
            oauth_token: OAuth 2.0 token for bearer auth
        """
        self.base_url = base_url.rstrip('/')
        self.api_base = f"{self.base_url}/wiki/rest/api"
        self.rate_limit_delay = 1.0  # Delay between requests
        
        # Set up authentication
        self.session = requests.Session()
        if oauth_token:
            self.session.headers.update({
                'Authorization': f'Bearer {oauth_token}',
                'Content-Type': 'application/json'
            })
        elif username and api_token:
            self.session.auth = (username, api_token)
            self.session.headers.update({
                'Content-Type': 'application/json'
            })
        else:
            logger.warning("No authentication provided for Confluence")
    
    def _rate_limit_delay(self):
        """Apply rate limiting delay."""
        time.sleep(self.rate_limit_delay)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated request to Confluence API.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to api_base)
            **kwargs: Additional arguments for requests
            
        Returns:
            Response object
        """
        url = urljoin(self.api_base + '/', endpoint.lstrip('/'))
        self._rate_limit_delay()
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as error:
            logger.error(f"Confluence API request failed: {error}")
            raise
    
    def get_page_content(self, page_id: str, expand: List[str] = None) -> Dict[str, Any]:
        """
        Get page content by ID.
        
        Args:
            page_id: Confluence page ID
            expand: List of fields to expand (e.g., ['body.storage', 'metadata.labels'])
            
        Returns:
            Page content dictionary
        """
        if expand is None:
            expand = ['body.storage', 'body.view', 'metadata.labels', 'version', 'space']
        
        params = {
            'expand': ','.join(expand)
        }
        
        try:
            response = self._make_request('GET', f'/content/{page_id}', params=params)
            content = response.json()
            
            logger.info(f"Retrieved page content for ID: {page_id}")
            return content
            
        except Exception as error:
            logger.error(f"Error getting page content for {page_id}: {error}")
            raise
    
    def search_content(self, cql: str, limit: int = 25, start: int = 0) -> Dict[str, Any]:
        """
        Search content using CQL (Confluence Query Language).
        
        Args:
            cql: CQL query string
            limit: Maximum number of results
            start: Starting index for pagination
            
        Returns:
            Search results dictionary
        """
        params = {
            'cql': cql,
            'limit': limit,
            'start': start,
            'expand': 'body.storage,metadata.labels,version,space'
        }
        
        try:
            response = self._make_request('GET', '/content/search', params=params)
            results = response.json()
            
            logger.info(f"Search returned {len(results.get('results', []))} results")
            return results
            
        except Exception as error:
            logger.error(f"Error searching content with CQL '{cql}': {error}")
            raise
    
    def get_page_by_title(self, space_key: str, title: str) -> Optional[Dict[str, Any]]:
        """
        Get page by space key and title.
        
        Args:
            space_key: Confluence space key
            title: Page title
            
        Returns:
            Page content dictionary or None if not found
        """
        params = {
            'spaceKey': space_key,
            'title': title,
            'expand': 'body.storage,body.view,metadata.labels,version'
        }
        
        try:
            response = self._make_request('GET', '/content', params=params)
            results = response.json()
            
            pages = results.get('results', [])
            if pages:
                logger.info(f"Found page '{title}' in space '{space_key}'")
                return pages[0]
            else:
                logger.warning(f"Page '{title}' not found in space '{space_key}'")
                return None
                
        except Exception as error:
            logger.error(f"Error getting page '{title}' in space '{space_key}': {error}")
            raise
    
    def extract_structured_data(self, page_content: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from page content.
        
        Args:
            page_content: Page content from Confluence API
            
        Returns:
            Structured data dictionary
        """
        structured_data = {
            'page_id': page_content.get('id'),
            'title': page_content.get('title'),
            'type': page_content.get('type'),
            'status': page_content.get('status'),
            'space': page_content.get('space', {}).get('key'),
            'version': page_content.get('version', {}).get('number'),
            'created_date': page_content.get('version', {}).get('when'),
            'labels': [label.get('name') for label in page_content.get('metadata', {}).get('labels', {}).get('results', [])],
            'content': {}
        }
        
        # Extract body content
        body = page_content.get('body', {})
        
        # Storage format (raw Confluence markup)
        if 'storage' in body:
            storage_content = body['storage'].get('value', '')
            structured_data['content']['storage'] = storage_content
            structured_data['content']['parsed_storage'] = self._parse_storage_format(storage_content)
        
        # View format (rendered HTML)
        if 'view' in body:
            view_content = body['view'].get('value', '')
            structured_data['content']['view'] = view_content
            structured_data['content']['parsed_view'] = self._parse_html_content(view_content)
        
        return structured_data
    
    def _parse_storage_format(self, storage_content: str) -> Dict[str, Any]:
        """
        Parse Confluence storage format content.
        
        Args:
            storage_content: Raw storage format content
            
        Returns:
            Parsed content dictionary
        """
        parsed = {
            'text_content': '',
            'tables': [],
            'macros': [],
            'links': [],
            'images': []
        }
        
        # Remove Confluence macros and extract text
        # This is a simplified parser - a full implementation would use proper XML parsing
        text_content = re.sub(r'<ac:.*?</ac:.*?>', '', storage_content, flags=re.DOTALL)
        text_content = re.sub(r'<ac:.*?/>', '', text_content)
        
        # Parse with BeautifulSoup for better HTML handling
        try:
            soup = BeautifulSoup(text_content, 'html.parser')
            parsed['text_content'] = soup.get_text(strip=True)
            
            # Extract tables
            tables = soup.find_all('table')
            for table in tables:
                table_data = []
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data.append(row_data)
                parsed['tables'].append(table_data)
            
            # Extract links
            links = soup.find_all('a')
            for link in links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                parsed['links'].append({'href': href, 'text': text})
            
        except Exception as error:
            logger.warning(f"Error parsing storage format: {error}")
            parsed['text_content'] = storage_content
        
        return parsed
    
    def _parse_html_content(self, html_content: str) -> Dict[str, Any]:
        """
        Parse HTML view content.
        
        Args:
            html_content: HTML content from view format
            
        Returns:
            Parsed content dictionary
        """
        parsed = {
            'text_content': '',
            'headings': [],
            'paragraphs': [],
            'lists': [],
            'tables': []
        }
        
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Extract text content
            parsed['text_content'] = soup.get_text(strip=True)
            
            # Extract headings
            for i in range(1, 7):  # h1 to h6
                headings = soup.find_all(f'h{i}')
                for heading in headings:
                    parsed['headings'].append({
                        'level': i,
                        'text': heading.get_text(strip=True)
                    })
            
            # Extract paragraphs
            paragraphs = soup.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                if text:  # Skip empty paragraphs
                    parsed['paragraphs'].append(text)
            
            # Extract lists
            lists = soup.find_all(['ul', 'ol'])
            for list_elem in lists:
                list_items = list_elem.find_all('li')
                list_data = [li.get_text(strip=True) for li in list_items]
                parsed['lists'].append({
                    'type': list_elem.name,
                    'items': list_data
                })
            
            # Extract tables
            tables = soup.find_all('table')
            for table in tables:
                table_data = []
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    row_data = [cell.get_text(strip=True) for cell in cells]
                    table_data.append(row_data)
                parsed['tables'].append(table_data)
            
        except Exception as error:
            logger.warning(f"Error parsing HTML content: {error}")
            parsed['text_content'] = html_content
        
        return parsed
    
    def get_page_properties(self, page_id: str) -> Dict[str, Any]:
        """
        Get custom properties for a page.
        
        Args:
            page_id: Confluence page ID
            
        Returns:
            Page properties dictionary
        """
        try:
            response = self._make_request('GET', f'/content/{page_id}/property')
            properties = response.json()
            
            property_dict = {}
            for prop in properties.get('results', []):
                key = prop.get('key')
                value = prop.get('value')
                property_dict[key] = value
            
            logger.info(f"Retrieved {len(property_dict)} properties for page {page_id}")
            return property_dict
            
        except Exception as error:
            logger.error(f"Error getting page properties for {page_id}: {error}")
            return {}
    
    def test_connection(self) -> bool:
        """
        Test the connection to Confluence API.
        
        Returns:
            True if connection is successful, False otherwise
        """
        try:
            response = self._make_request('GET', '/space')
            return response.status_code == 200
        except Exception as error:
            logger.error(f"Confluence connection test failed: {error}")
            return False

