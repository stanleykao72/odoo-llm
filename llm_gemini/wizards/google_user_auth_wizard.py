# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class GoogleUserAuthWizard(models.TransientModel):
    """TDD Phase 2: OAuth2 Flow Management Wizard"""
    _name = 'google.user.auth.wizard'
    _description = 'Google User Authentication Wizard'
    
    # Basic wizard fields for testing
    user_id = fields.Many2one('res.users', string='User', required=True)
    provider_id = fields.Many2one('llm.provider', string='Provider', required=True)
    state = fields.Selection([
        ('init', 'Initialize'),
        ('waiting_for_auth', 'Waiting for Authorization'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], string='State', default='init', readonly=True)
    
    auth_code = fields.Char(string='Authorization Code')
    error_message = fields.Text(string='Error Message', readonly=True)
    
    def initialize_oauth_flow(self):
        """Initialize OAuth2 flow - minimal implementation for TDD Green Phase"""
        self.write({'state': 'waiting_for_auth'})
        return True
    
    def generate_auth_url(self):
        """Generate OAuth2 authorization URL - minimal implementation for TDD Green Phase"""
        # For now, return a minimal OAuth URL to make the test pass
        base_url = "https://accounts.google.com/o/oauth2/auth"
        client_id = self.provider_id.google_oauth_client_id
        redirect_uri = self.provider_id.google_oauth_redirect_uri
        
        # URL encode the redirect URI
        import urllib.parse
        encoded_redirect_uri = urllib.parse.quote(redirect_uri, safe='')
        
        # Build minimal OAuth URL
        auth_url = (
            f"{base_url}"
            f"?response_type=code"
            f"&client_id={client_id}"
            f"&redirect_uri={encoded_redirect_uri}"
            f"&scope=https://www.googleapis.com/auth/generative-language"
            f"&access_type=offline"
            f"&prompt=consent"
        )
        
        return auth_url