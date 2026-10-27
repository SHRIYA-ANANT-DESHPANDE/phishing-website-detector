"""URL feature extraction for UCI Phishing Websites dataset."""

from urllib.parse import urlparse, urljoin
import re
from typing import List, Tuple
import socket
import requests
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


class URLFeatureExtractor:
    """
    Extract the 30 features used in the UCI Phishing Websites dataset.
    Fetches HTML content when possible to extract HTML-based features.
    All features return values in {-1, 0, 1} as per the original dataset.
    """
    
    def __init__(self, fetch_html: bool = True, timeout: int = 5):
        """
        Args:
            fetch_html: Whether to fetch HTML content (default True)
            timeout: Request timeout in seconds (default 5)
        """
        self.fetch_html = fetch_html
        self.timeout = timeout
    
    def extract_features(self, url: str) -> List[int]:
        """
        Extract 30 features from a URL matching UCI Phishing Websites dataset.
        Returns list of 30 integer values in range {-1, 0, 1}.
        """
        parsed = urlparse(url)
        domain = parsed.netloc
        path = parsed.path
        
        # Try to fetch HTML content
        html_content = None
        soup = None
        if self.fetch_html:
            html_content, soup = self._fetch_html(url)
        
        features = []
        
        # 1. having_IP_Address: Using IP address in domain (1) or not (-1)
        features.append(1 if self._has_ip_address(domain) else -1)
        
        # 2. URL_Length: Phishing (1), Suspicious (0), Legitimate (-1)
        url_len = len(url)
        if url_len < 54:
            features.append(-1)
        elif url_len <= 75:
            features.append(0)
        else:
            features.append(1)
        
        # 3. Shortining_Service: Using shortening service (1) or not (-1)
        features.append(1 if self._uses_shortening(domain) else -1)
        
        # 4. having_At_Symbol: Has @ symbol (1) or not (-1)
        features.append(1 if '@' in url else -1)
        
        # 5. double_slash_redirecting: Has // after protocol (1) or not (-1)
        url_after_protocol = url.split('://', 1)[-1]
        features.append(1 if '//' in url_after_protocol else -1)
        
        # 6. Prefix_Suffix: Has dash in domain (1) or not (-1)
        features.append(1 if '-' in domain else -1)
        
        # 7. having_Sub_Domain: Multiple subdomains
        dots_in_domain = domain.count('.')
        if dots_in_domain == 1:
            features.append(-1)
        elif dots_in_domain == 2:
            features.append(0)
        else:
            features.append(1)
        
        # 8. SSLfinal_State: Uses trusted SSL (-1), Suspicious (0), No SSL (1)
        if parsed.scheme == 'https':
            features.append(-1)  # Legitimate
        elif 'https' in domain.lower():
            features.append(0)  # Suspicious (https in domain but not in protocol)
        else:
            features.append(1)  # Phishing (no HTTPS)
        
        # 9. Domain_registeration_length: Cannot check without WHOIS
        features.append(-1)  # Default to legitimate
        
        # 10. Favicon: From different domain (1), same domain (-1), or can't tell (0)
        if soup:
            favicon_feature = self._check_favicon(soup, domain)
            features.append(favicon_feature)
        else:
            features.append(-1)  # Default to legitimate
        
        # 11. port: Using non-standard port (1) or standard (-1)
        if parsed.port:
            if parsed.port in [80, 443]:
                features.append(-1)
            else:
                features.append(1)
        else:
            features.append(-1)
        
        # 12. HTTPS_token: Has "https" in domain (1 = phishing) or not (-1)
        features.append(1 if 'https' in domain.lower() and parsed.scheme != 'https' else -1)
        
        # 13. Request_URL: % of external objects (images/videos/sounds)
        if soup:
            request_url_feature = self._check_request_url(soup, domain)
            features.append(request_url_feature)
        else:
            features.append(-1)  # Default to legitimate
        
        # 14. URL_of_Anchor: % of anchors to different domain
        if soup:
            anchor_feature = self._check_url_of_anchor(soup, domain)
            features.append(anchor_feature)
        else:
            features.append(-1)  # Default to legitimate
        
        # 15. Links_in_tags: % of meta/script/link tags to different domain
        if soup:
            links_in_tags_feature = self._check_links_in_tags(soup, domain)
            features.append(links_in_tags_feature)
        else:
            features.append(-1)  # Default to legitimate
        
        # 16. SFH: Server Form Handler
        if soup:
            sfh_feature = self._check_sfh(soup, domain)
            features.append(sfh_feature)
        else:
            features.append(-1)  # Default to legitimate
        
        # 17. Submitting_to_email: Has mailto (1) or not (-1)
        if soup:
            # Check in HTML
            has_mailto = 'mailto:' in str(soup).lower()
            features.append(1 if has_mailto else -1)
        else:
            # Check in URL
            features.append(1 if 'mailto:' in url.lower() else -1)
        
        # 18. Abnormal_URL: Domain has suspicious keywords (1) or not (-1)
        suspicious_keywords = ['verify', 'account', 'update', 'secure', 'banking', 
                               'signin', 'login', 'ebayisapi', 'webscr', 'confirm']
        is_suspicious = any(keyword in domain.lower() for keyword in suspicious_keywords)
        features.append(1 if is_suspicious else -1)
        
        # 19. Redirect: Path depth > 4 (1) or not (-1)
        path_depth = len([p for p in path.split('/') if p])
        features.append(1 if path_depth > 4 else -1)
        
        # 20. on_mouseover: Status bar customization (needs JS analysis)
        if soup:
            has_mouseover = bool(soup.find_all(attrs={'onmouseover': True}))
            features.append(1 if has_mouseover else -1)
        else:
            features.append(-1)
        
        # 21. RightClick: Right click disabled (needs JS analysis)
        if html_content:
            has_rightclick_disable = bool(
                'event.button==2' in html_content.lower() or
                'event.button == 2' in html_content.lower()
            )
            features.append(1 if has_rightclick_disable else -1)
        else:
            features.append(-1)
        
        # 22. popUpWidnow: Popup with text fields
        if html_content:
            has_popup = 'window.open' in html_content.lower() or 'popup' in html_content.lower()
            features.append(1 if has_popup else -1)
        else:
            features.append(-1)
        
        # 23. Iframe: Using iframe (1) or not (-1)
        if soup:
            has_iframe = bool(soup.find_all('iframe'))
            features.append(1 if has_iframe else -1)
        else:
            features.append(-1)
        
        # 24. age_of_domain: Cannot check without WHOIS
        features.append(-1)  # Default to old domain (legitimate)
        
        # 25. DNSRecord: No DNS record (1) or has record (-1)
        try:
            socket.gethostbyname(domain)
            features.append(-1)  # Has DNS record
        except:
            features.append(1)  # No DNS record (suspicious)
        
        # 26. web_traffic: Use TLD as proxy
        common_tlds = ['.com', '.org', '.net', '.edu', '.gov', '.mil']
        has_common_tld = any(domain.endswith(tld) for tld in common_tlds)
        features.append(-1 if has_common_tld else 0)
        
        # 27. Page_Rank: Use TLD as proxy
        features.append(-1 if has_common_tld else 1)
        
        # 28. Google_Index: Default to indexed
        features.append(-1)
        
        # 29. Links_pointing_to_page: Default to many
        features.append(-1)
        
        # 30. Statistical_report: Default to not blacklisted
        features.append(-1)
        
        return features
    
    def _fetch_html(self, url: str) -> Tuple[str, BeautifulSoup]:
        """Fetch HTML content from URL."""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, timeout=self.timeout, headers=headers, verify=False)
            html_content = response.text
            soup = BeautifulSoup(html_content, 'html.parser')
            logger.info(f"Successfully fetched HTML for {url}")
            return html_content, soup
        except Exception as e:
            logger.warning(f"Failed to fetch HTML for {url}: {e}")
            return None, None
    
    def _check_request_url(self, soup: BeautifulSoup, domain: str) -> int:
        """Check % of external objects. <22%=-1, 22-61%=0, >61%=1"""
        try:
            total = 0
            external = 0
            
            # Check images, videos, sounds
            for tag in soup.find_all(['img', 'video', 'audio']):
                src = tag.get('src', '')
                if src:
                    total += 1
                    if self._is_external(src, domain):
                        external += 1
            
            if total == 0:
                return -1  # No external resources
            
            percentage = (external / total) * 100
            if percentage < 22:
                return -1  # Legitimate
            elif percentage <= 61:
                return 0  # Suspicious
            else:
                return 1  # Phishing
        except:
            return -1
    
    def _check_url_of_anchor(self, soup: BeautifulSoup, domain: str) -> int:
        """Check % of anchors to external domains. <31%=-1, 31-67%=0, >67%=1"""
        try:
            anchors = soup.find_all('a', href=True)
            if not anchors:
                return -1
            
            external = sum(1 for a in anchors if self._is_external(a['href'], domain))
            percentage = (external / len(anchors)) * 100
            
            if percentage < 31:
                return -1
            elif percentage <= 67:
                return 0
            else:
                return 1
        except:
            return -1
    
    def _check_links_in_tags(self, soup: BeautifulSoup, domain: str) -> int:
        """Check % of meta/script/link tags from external domains. <17%=-1, 17-81%=0, >81%=1"""
        try:
            total = 0
            external = 0
            
            for tag in soup.find_all(['meta', 'script', 'link']):
                for attr in ['href', 'src', 'content']:
                    url = tag.get(attr, '')
                    if url and url.startswith('http'):
                        total += 1
                        if self._is_external(url, domain):
                            external += 1
            
            if total == 0:
                return -1
            
            percentage = (external / total) * 100
            if percentage < 17:
                return -1
            elif percentage <= 81:
                return 0
            else:
                return 1
        except:
            return -1
    
    def _check_sfh(self, soup: BeautifulSoup, domain: str) -> int:
        """Check Server Form Handler. Empty/about:blank=1, external=0, same=-1"""
        try:
            forms = soup.find_all('form')
            if not forms:
                return -1  # No forms
            
            for form in forms:
                action = form.get('action', '').lower()
                if not action or action == '' or 'about:blank' in action:
                    return 1  # Suspicious
                if self._is_external(action, domain):
                    return 0  # Suspicious
            
            return -1  # Same domain
        except:
            return -1
    
    def _check_favicon(self, soup: BeautifulSoup, domain: str) -> int:
        """Check if favicon is from external domain. External=1, same=-1"""
        try:
            icon = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
            if not icon:
                return -1
            
            href = icon.get('href', '')
            if self._is_external(href, domain):
                return 1  # External favicon
            return -1
        except:
            return -1
    
    def _is_external(self, url: str, domain: str) -> bool:
        """Check if URL points to a different domain."""
        if not url or url.startswith(('#', 'javascript:', 'mailto:')):
            return False
        
        try:
            # Relative URLs are not external
            if not url.startswith('http'):
                return False
            
            parsed = urlparse(url)
            url_domain = parsed.netloc
            
            # Remove www. for comparison
            url_domain = url_domain.replace('www.', '')
            domain = domain.replace('www.', '')
            
            return url_domain != domain and url_domain != ''
        except:
            return False
    
    @staticmethod
    def _has_ip_address(domain: str) -> bool:
        """Check if domain is an IP address (IPv4 or hex encoded)."""
        ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        hex_pattern = r'^0x[0-9a-fA-F]+(\.[0-9a-fA-F]+)*$'
        ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
        
        return bool(
            re.match(ipv4_pattern, domain) or
            re.match(hex_pattern, domain) or
            re.match(ipv6_pattern, domain)
        )
    
    @staticmethod
    def _uses_shortening(domain: str) -> bool:
        """Check if domain is a URL shortening service."""
        shortening_services = [
            'bit.ly', 'goo.gl', 'shorte.st', 'go2l.ink', 'x.co',
            'ow.ly', 't.co', 'tinyurl', 'tr.im', 'is.gd',
            'cli.gs', 'yfrog.com', 'migre.me', 'ff.im', 'tiny.cc',
            'url4.eu', 'twit.ac', 'su.pr', 'twurl.nl', 'snipurl.com',
            'short.to', 'budurl.com', 'ping.fm', 'post.ly', 'just.as',
            'bkite.com', 'snipr.com', 'fic.kr', 'loopt.us', 'doiop.com',
            'short.ie', 'kl.am', 'wp.me', 'rubyurl.com', 'om.ly',
            'to.ly', 'bit.do', 'lnkd.in', 'db.tt', 'qr.ae',
            'adf.ly', 'bitly.com', 'cur.lv', 'ity.im', 'q.gs',
            'po.st', 'bc.vc', 'u.to', 'j.mp', 'buzurl.com',
            'cutt.us', 'u.bb', 'yourls.org', 'prettylinkpro.com',
            'scrnch.me', 'vzturl.com', 'qr.net', '1url.com',
            'tweez.me', 'v.gd', 'link.zip.net', 'rb.gy', 'short.link',
            's.id', 'tiny.one', 'cutt.ly', 't.ly', '1pt.co'
        ]
        
        domain_lower = domain.lower()
        return any(service in domain_lower for service in shortening_services)
