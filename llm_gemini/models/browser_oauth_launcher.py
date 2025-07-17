# -*- coding: utf-8 -*-

"""
Browser OAuth Launcher for Browser Authentication
Handles cross-platform browser launching for OAuth flows
"""

import webbrowser
import platform
from odoo.exceptions import UserError


class BrowserOAuthLauncher:
    """Browser Launch and URL Management for OAuth2 Flow"""
    
    def __init__(self, provider):
        """
        Initialize browser OAuth launcher
        
        Args:
            provider: LLM provider instance
        """
        self.provider = provider
        
    def launch_browser_auth(self, auth_url):
        """
        Launch browser with OAuth URL
        
        Args:
            auth_url (str): OAuth2 authorization URL
            
        Returns:
            bool: True if browser launched successfully
            
        Raises:
            UserError: If browser launch fails
        """
        try:
            # Attempt to open browser automatically
            success = webbrowser.open(auth_url)
            
            if not success:
                # Browser launch failed, provide manual URL
                raise Exception("Failed to open browser automatically")
            
            return True
            
        except Exception as e:
            # Handle browser launch failures gracefully
            return self._handle_browser_failure(auth_url, e)
    
    def _handle_browser_failure(self, auth_url, error):
        """
        Handle browser launch failures gracefully
        
        Args:
            auth_url (str): OAuth2 authorization URL
            error (Exception): Original error that occurred
            
        Raises:
            UserError: With manual URL instructions
        """
        # Get platform-specific instructions
        platform_instructions = self._get_platform_instructions()
        
        error_message = f"""
        Browser Authentication Setup Required
        
        We couldn't open your browser automatically. Please follow these steps:
        
        1. Copy this URL: {auth_url}
        
        2. Open your web browser manually
        
        3. Paste the URL into your browser's address bar
        
        4. Complete the Google authentication process
        
        Platform: {platform.system()}
        {platform_instructions}
        
        Technical Error: {str(error)}
        """.strip()
        
        raise UserError(error_message)
    
    def _get_platform_instructions(self):
        """
        Get platform-specific browser instructions
        
        Returns:
            str: Platform-specific instructions
        """
        current_os = platform.system()
        
        if current_os == "Windows":
            return """
            Windows Instructions:
            - Press Ctrl+L in your browser to focus the address bar
            - Or use Edge, Chrome, Firefox, or your preferred browser
            """.strip()
            
        elif current_os == "Darwin":  # macOS
            return """
            macOS Instructions:
            - Press Cmd+L in your browser to focus the address bar
            - Or use Safari, Chrome, Firefox, or your preferred browser
            """.strip()
            
        else:  # Linux and others
            return """
            Linux Instructions:
            - Press Ctrl+L in your browser to focus the address bar
            - Or use Firefox, Chrome, or your preferred browser
            - You may need to install a browser if none is available
            """.strip()
    
    def get_supported_browsers(self):
        """
        Get list of supported browsers for current platform
        
        Returns:
            list: List of browser names
        """
        current_os = platform.system()
        
        if current_os == "Windows":
            return ["edge", "chrome", "firefox", "opera", "internet explorer"]
        elif current_os == "Darwin":  # macOS
            return ["safari", "chrome", "firefox", "opera"]
        else:  # Linux
            return ["firefox", "chrome", "chromium", "opera"]
    
    def test_browser_availability(self):
        """
        Test if browser is available on the system
        
        Returns:
            bool: True if browser is available
        """
        try:
            # Try to get the default browser
            browser = webbrowser.get()
            return browser is not None
        except Exception:
            return False