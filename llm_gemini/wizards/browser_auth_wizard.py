# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import UserError


class BrowserAuthWizard(models.TransientModel):
    _name = 'llm.gemini.browser.auth.wizard'
    _description = 'Gemini Browser Authentication Wizard'
    
    provider_id = fields.Many2one('llm.provider', required=True)
    state = fields.Selection([
        ('init', 'Initialize'),
        ('waiting', 'Waiting for Browser'),
        ('processing', 'Processing Tokens'),
        ('completed', 'Completed'),
        ('error', 'Error'),
    ], default='init')
    
    status_message = fields.Text(readonly=True)
    auth_url = fields.Char(readonly=True)
    
    def start_browser_authentication(self):
        """Start the browser authentication process"""
        self.ensure_one()
        
        try:
            # Update status
            self.write({
                'state': 'waiting',
                'status_message': 'Starting browser authentication...'
            })
            
            # Delegate to provider
            result = self.provider_id.browser_authenticate()
            
            self.write({
                'state': 'waiting',
                'status_message': 'Browser opened. Please complete authentication in your browser window.'
            })
            
            return {
                'type': 'ir.actions.act_window',
                'res_model': self._name,
                'res_id': self.id,
                'view_mode': 'form',
                'target': 'new',
                'context': {'browser_auth_in_progress': True}
            }
            
        except Exception as e:
            self.write({
                'state': 'error',
                'status_message': f'Authentication failed: {str(e)}'
            })
            raise
    
    def check_authentication_status(self):
        """Check the current authentication status"""
        self.ensure_one()
        
        # Check user's authentication status
        user_status = self.env.user.google_auth_status
        
        if user_status == 'connected':
            self.write({
                'state': 'completed',
                'status_message': 'Authentication completed successfully!'
            })
            return True
        elif user_status == 'error':
            self.write({
                'state': 'error',
                'status_message': 'Authentication failed. Please try again.'
            })
            return False
        
        return None  # Still processing
    
    def refresh_status(self):
        """Refresh the authentication status"""
        self.check_authentication_status()
        return {
            'type': 'ir.actions.act_window',
            'res_model': self._name,
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'browser_auth_in_progress': True}
        }