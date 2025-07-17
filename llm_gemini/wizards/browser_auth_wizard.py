# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class BrowserAuthWizard(models.TransientModel):
    _name = 'llm.gemini.browser.auth.wizard'
    _description = 'Google Browser Authentication Wizard (18.0 Enhanced)'
    
    # Basic wizard state management (18.0 enhanced)
    state = fields.Selection([
        ('init', 'Initialize'),
        ('launching', 'Launching Browser'),
        ('waiting', 'Waiting for Authentication'),
        ('processing', 'Processing Response'),
        ('completed', 'Completed'),
        ('error', 'Error'),
        ('timeout', 'Timeout'),  # 18.0 enhancement
    ], default='init', string='Authentication State', tracking=True)
    
    # Provider reference (18.0 enhanced with index)
    provider_id = fields.Many2one(
        'llm.provider',
        string='Gemini Provider',
        required=True,
        domain=[('service', '=', 'gemini'), ('auth_mode', '=', 'browser')],
        index=True,  # 18.0 enhancement
    )
    
    # Authentication progress and feedback (18.0 enhanced)
    progress_message = fields.Text(
        string='Progress Message',
        readonly=True,
        help="Real-time progress updates for the authentication process"
    )
    error_message = fields.Text(
        string='Error Message',
        readonly=True,
        help="Detailed error information if authentication fails"
    )
    
    # Browser launch information (18.0 enhancement)
    browser_url = fields.Char(
        string='Authentication URL',
        readonly=True,
        help="OAuth2 URL for manual browser access if auto-launch fails"
    )
    platform_info = fields.Text(
        string='Platform Information',
        readonly=True,
        help="System platform information for troubleshooting"
    )
    
    # Authentication details (18.0 enhancement)
    auth_started_at = fields.Datetime(
        string='Authentication Started',
        readonly=True,
        help="When the authentication process was initiated"
    )
    auth_completed_at = fields.Datetime(
        string='Authentication Completed',
        readonly=True,
        help="When the authentication process was completed"
    )
    
    # Security and session tracking (18.0 enhancement)
    session_id = fields.Char(
        string='Session ID',
        readonly=True,
        help="Unique session identifier for this authentication attempt"
    )
    callback_port = fields.Integer(
        string='Callback Port',
        readonly=True,
        help="Port number used for OAuth callback"
    )
    
    def action_start_authentication(self):
        """Start the browser authentication process (18.0 enhanced implementation)"""
        self.ensure_one()
        
        try:
            # 18.0 enhancement: Validate provider configuration
            if not self.provider_id:
                raise ValidationError("No provider selected for authentication")
            
            if self.provider_id.service != 'gemini' or self.provider_id.auth_mode != 'browser':
                raise ValidationError("Provider must be configured for Gemini browser authentication")
            
            # Update state and start timing
            self.write({
                'state': 'launching',
                'progress_message': 'Initializing browser authentication...',
                'auth_started_at': fields.Datetime.now(),
                'session_id': self._generate_session_id(),
            })
            
            # Start the browser authentication process
            result = self.provider_id.browser_authenticate()
            
            if result.get('type') == 'ir.actions.client':
                # Browser launch was successful
                self._update_launch_success()
                return self._create_waiting_action()
            else:
                # Browser launch failed
                self._update_launch_error(result.get('params', {}).get('message', 'Unknown error'))
                return self._create_error_action()
                
        except Exception as e:
            _logger.error(f"Browser authentication start failed: {str(e)}")
            self._update_authentication_error(str(e))
            return self._create_error_action()
    
    def _generate_session_id(self):
        """Generate unique session ID for tracking (18.0 enhancement)"""
        import uuid
        return str(uuid.uuid4())
    
    def _update_launch_success(self):
        """Update wizard state after successful browser launch (18.0 enhancement)"""
        self.write({
            'state': 'waiting',
            'progress_message': 'Browser launched successfully. Please complete authentication in your browser window.',
        })
    
    def _update_launch_error(self, error_message):
        """Update wizard state after browser launch failure (18.0 enhancement)"""
        self.write({
            'state': 'error',
            'error_message': f"Browser launch failed: {error_message}",
            'progress_message': 'Authentication failed. Please try manual authentication.',
        })
    
    def _update_authentication_error(self, error_message):
        """Update wizard state for general authentication errors (18.0 enhancement)"""
        self.write({
            'state': 'error',
            'error_message': error_message,
            'progress_message': 'Authentication process encountered an error.',
        })
    
    def _create_waiting_action(self):
        """Create action for waiting state (18.0 enhancement)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Google Browser Authentication',
            'res_model': 'llm.gemini.browser.auth.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'dialog_size': 'medium'},
        }
    
    def _create_error_action(self):
        """Create action for error state (18.0 enhancement)"""
        return {
            'type': 'ir.actions.act_window',
            'name': 'Authentication Error',
            'res_model': 'llm.gemini.browser.auth.wizard',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
            'context': {'dialog_size': 'medium'},
        }
    
    def action_check_authentication_status(self):
        """Check if authentication has been completed (18.0 enhancement)"""
        self.ensure_one()
        
        try:
            # Check if user authentication status has been updated
            current_user = self.env.user
            
            if current_user.google_auth_status == 'connected':
                # Authentication successful
                self.write({
                    'state': 'completed',
                    'progress_message': 'Authentication completed successfully!',
                    'auth_completed_at': fields.Datetime.now(),
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Google authentication completed successfully!',
                        'type': 'success',
                        'sticky': False,
                        'fadeout': 3000,
                    }
                }
            
            elif current_user.google_auth_status == 'error':
                # Authentication failed
                self.write({
                    'state': 'error',
                    'error_message': 'Authentication failed. Please try again.',
                    'progress_message': 'Authentication process failed.',
                })
                
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Google authentication failed. Please try again.',
                        'type': 'danger',
                        'sticky': True,
                    }
                }
            
            else:\n                # Still waiting\n                return {\n                    'type': 'ir.actions.client',\n                    'tag': 'display_notification',\n                    'params': {\n                        'message': 'Still waiting for authentication completion...',\n                        'type': 'info',\n                        'sticky': False,\n                        'fadeout': 2000,\n                    }\n                }\n                \n        except Exception as e:\n            _logger.error(f\"Authentication status check failed: {str(e)}\")\n            self._update_authentication_error(f\"Status check failed: {str(e)}\")\n            return self._create_error_action()\n    \n    def action_retry_authentication(self):\n        \"\"\"Retry the authentication process (18.0 enhancement)\"\"\"\n        self.ensure_one()\n        \n        # Reset wizard state\n        self.write({\n            'state': 'init',\n            'progress_message': '',\n            'error_message': '',\n            'browser_url': '',\n            'auth_started_at': False,\n            'auth_completed_at': False,\n            'session_id': '',\n        })\n        \n        # Start authentication again\n        return self.action_start_authentication()\n    \n    def action_manual_authentication(self):\n        \"\"\"Provide manual authentication instructions (18.0 enhancement)\"\"\"\n        self.ensure_one()\n        \n        try:\n            # Generate manual authentication URL\n            # This would typically involve the same OAuth URL generation\n            # but without automatic browser launching\n            \n            # For now, provide general instructions\n            manual_instructions = {\n                'title': 'Manual Authentication Required',\n                'message': 'Automatic browser launch failed. Please authenticate manually.',\n                'steps': [\n                    '1. Open your web browser',\n                    '2. Navigate to Google OAuth2 consent screen',\n                    '3. Grant permissions to Odoo LLM',\n                    '4. Return to this wizard and check status',\n                ],\n            }\n            \n            self.write({\n                'progress_message': f\"Manual authentication required:\\n{chr(10).join(manual_instructions['steps'])}\",\n            })\n            \n            return {\n                'type': 'ir.actions.client',\n                'tag': 'display_notification',\n                'params': {\n                    'title': manual_instructions['title'],\n                    'message': manual_instructions['message'],\n                    'type': 'warning',\n                    'sticky': True,\n                }\n            }\n            \n        except Exception as e:\n            _logger.error(f\"Manual authentication setup failed: {str(e)}\")\n            return self._create_error_action()\n    \n    def action_close_wizard(self):\n        \"\"\"Close the authentication wizard (18.0 enhancement)\"\"\"\n        return {'type': 'ir.actions.act_window_close'}\n    \n    def get_authentication_summary(self):\n        \"\"\"Get summary of authentication attempt (18.0 enhancement)\"\"\"\n        self.ensure_one()\n        \n        duration = None\n        if self.auth_started_at:\n            end_time = self.auth_completed_at or fields.Datetime.now()\n            duration = (end_time - self.auth_started_at).total_seconds()\n        \n        return {\n            'session_id': self.session_id,\n            'state': self.state,\n            'provider': self.provider_id.name,\n            'started_at': self.auth_started_at,\n            'completed_at': self.auth_completed_at,\n            'duration_seconds': duration,\n            'success': self.state == 'completed',\n            'error_message': self.error_message,\n        }\n    \n    @api.model\n    def cleanup_old_wizards(self):\n        \"\"\"Clean up old wizard records (18.0 enhancement)\"\"\"\n        # Remove wizard records older than 24 hours\n        cutoff_time = fields.Datetime.now() - timedelta(hours=24)\n        \n        old_wizards = self.search([\n            ('create_date', '<', cutoff_time)\n        ])\n        \n        count = len(old_wizards)\n        old_wizards.unlink()\n        \n        _logger.info(f\"Cleaned up {count} old browser authentication wizard records\")\n        return count\n    \n    @api.model\n    def get_active_authentication_sessions(self):\n        \"\"\"Get count of active authentication sessions (18.0 enhancement)\"\"\"\n        active_sessions = self.search([\n            ('state', 'in', ['launching', 'waiting', 'processing']),\n            ('create_date', '>', fields.Datetime.now() - timedelta(hours=1))\n        ])\n        \n        return {\n            'total_active': len(active_sessions),\n            'by_state': {\n                'launching': len(active_sessions.filtered(lambda w: w.state == 'launching')),\n                'waiting': len(active_sessions.filtered(lambda w: w.state == 'waiting')),\n                'processing': len(active_sessions.filtered(lambda w: w.state == 'processing')),\n            },\n            'sessions': active_sessions.mapped('session_id'),\n        }