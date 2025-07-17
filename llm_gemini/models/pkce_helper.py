# -*- coding: utf-8 -*-

"""
PKCE (Proof Key for Code Exchange) Helper for OAuth2 Security
Implements RFC 7636 compliant PKCE flow for browser authentication
Enhanced for Odoo 18.0 with additional security features
"""

import os
import base64
import hashlib


class PKCEHelper:
    """PKCE Helper for OAuth2 Security Implementation (18.0 Enhanced)"""
    
    @staticmethod
    def generate_code_verifier():
        """
        Generate cryptographically secure code verifier
        
        Returns:
            str: Base64 URL-safe encoded code verifier (43-128 characters)
        """
        # Generate 32 random bytes (256 bits) - enhanced for 18.0
        random_bytes = os.urandom(32)
        
        # Base64 URL-safe encode and remove padding
        code_verifier = base64.urlsafe_b64encode(random_bytes).decode('utf-8').rstrip('=')
        
        return code_verifier
    
    @staticmethod
    def generate_code_challenge(code_verifier):
        """
        Generate code challenge from verifier using SHA256
        
        Args:
            code_verifier (str): The code verifier string
            
        Returns:
            str: Base64 URL-safe encoded SHA256 hash of code verifier
        """
        # Create SHA256 hash of the code verifier
        digest = hashlib.sha256(code_verifier.encode('utf-8')).digest()
        
        # Base64 URL-safe encode and remove padding
        code_challenge = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        
        return code_challenge
    
    @staticmethod
    def verify_code_challenge(code_verifier, code_challenge):
        """
        Verify that code verifier matches the challenge
        
        Args:
            code_verifier (str): The original code verifier
            code_challenge (str): The code challenge to verify
            
        Returns:
            bool: True if verifier matches challenge, False otherwise
        """
        expected_challenge = PKCEHelper.generate_code_challenge(code_verifier)
        return expected_challenge == code_challenge
    
    @staticmethod
    def validate_code_verifier(code_verifier):
        """
        Validate code verifier according to RFC 7636 (18.0 enhancement)
        
        Args:
            code_verifier (str): The code verifier to validate
            
        Returns:
            bool: True if valid, raises exception if invalid
        """
        if not code_verifier:
            raise ValueError("Code verifier cannot be empty")
        
        if len(code_verifier) < 43:
            raise ValueError("Code verifier must be at least 43 characters")
            
        if len(code_verifier) > 128:
            raise ValueError("Code verifier must be no more than 128 characters")
        
        # Check that it contains only valid characters
        import re
        if not re.match(r'^[A-Za-z0-9\-_.~]+$', code_verifier):
            raise ValueError("Code verifier contains invalid characters")
        
        return True