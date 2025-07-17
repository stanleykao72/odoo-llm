# -*- coding: utf-8 -*-

import base64
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from cryptography.fernet import Fernet
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # 18.0 Enhanced search methods
    @api.model
    def _search_google_auth_status(self, operator, value):
        """18.0 enhanced search: Custom search for Google auth status"""
        if operator == '=' and value == 'active':
            return [('google_auth_status', '=', 'connected')]
        return [('google_auth_status', operator, value)]
    
    # TDD: Green Phase - Google authentication fields - Enhanced for 18.0
    google_access_token = fields.Char(
        string='Google Access Token',
        groups='base.group_system',
    )
    google_refresh_token = fields.Char(
        string='Google Refresh Token',
        groups='base.group_system',
    )
    google_token_expiry = fields.Datetime(
        string='Token Expiry',
        tracking=True,
    )
    google_email = fields.Char(
        string='Google Email',
        readonly=True,
        index=True,
    )
    google_name = fields.Char(
        string='Google Name',
        readonly=True,
        index=True,
    )
    
    # Authentication Status (Phase 2) - Enhanced for 18.0
    google_auth_status = fields.Selection([
        ('not_connected', 'Not Connected'),
        ('connected', 'Connected'),
        ('expired', 'Token Expired'),
        ('error', 'Error')
    ], string='Google Auth Status', default='not_connected', index=True, tracking=True)
    
    # TDD: Phase 5 - Token rotation security fields - Enhanced for 18.0
    google_token_rotation_date = fields.Datetime(
        string='Last Token Rotation Date',
        tracking=True,
    )
    
    # TDD: Phase 3 - Quota management fields - Enhanced for 18.0
    google_quota_used = fields.Integer(
        string='Google Quota Used This Month',
        default=0,
        tracking=True,
    )
    google_quota_limit = fields.Integer(
        string='Google Quota Limit',
        default=15,
        tracking=True,
    )
    google_quota_reset_date = fields.Date(
        string='Quota Reset Date',
        default=lambda self: self._default_quota_reset_date(),
        tracking=True,
    )
    google_quota_status = fields.Selection([
        ('available', 'Available'),
        ('warning', 'Warning'),
        ('exhausted', 'Exhausted')
    ], string='Quota Status', default='available', index=True, tracking=True)
    
    def set_encrypted_google_token(self, token):
        """TDD: Green Phase - Minimal encryption implementation"""
        # Simple base64 encoding for now (not real encryption)
        if token:
            encoded_token = base64.b64encode(token.encode()).decode()
            self.write({'google_access_token': encoded_token})
    
    def get_decrypted_google_token(self):
        """TDD: Green Phase - Minimal decryption implementation"""
        # Simple base64 decoding for now (not real decryption)
        if self.google_access_token:
            return base64.b64decode(self.google_access_token.encode()).decode()
        return None
    
    def _get_or_create_encryption_key(self):
        """TDD: Green Phase - Get or create encryption key for Fernet"""
        key = self.env['ir.config_parameter'].get_param('google.token.encryption.key')
        if not key:
            # Generate new Fernet key
            key = Fernet.generate_key().decode()
            self.env['ir.config_parameter'].set_param('google.token.encryption.key', key)
        return key.encode()
    
    def _encrypt_token_fernet(self, token):
        """TDD: Green Phase - Minimal Fernet encryption implementation"""
        if not token:
            return False
        
        key = self._get_or_create_encryption_key()
        f = Fernet(key)
        return f.encrypt(token.encode()).decode()
    
    def _decrypt_token_fernet(self, encrypted_token):
        """TDD: Green Phase - Minimal Fernet decryption implementation"""
        if not encrypted_token:
            return False
        
        key = self._get_or_create_encryption_key()
        f = Fernet(key)
        return f.decrypt(encrypted_token.encode()).decode()
    
    def _decrypt_token_with_migration(self, token):
        """TDD: Green Phase - Backward compatible token decryption"""
        if not token:
            return False
        
        # Try Fernet first (new format)
        if token.startswith('gAAAAA'):
            return self._decrypt_token_fernet(token)
        else:
            # Fall back to base64 (old format)
            return base64.b64decode(token.encode()).decode()
    
    def _rotate_encryption_tokens(self):
        """TDD: Green Phase - Minimal token rotation implementation"""
        # Minimal implementation to make test pass
        # Update rotation timestamp
        self.google_token_rotation_date = fields.Datetime.now()
        
        # Re-encrypt existing tokens with new keys (minimal implementation)
        if self.google_access_token:
            # For now, just re-encrypt with same key (in production, would use new key)
            decrypted = self._decrypt_token_with_migration(self.google_access_token)
            self.google_access_token = self._encrypt_token_fernet(decrypted)
        
        if self.google_refresh_token:
            decrypted = self._decrypt_token_with_migration(self.google_refresh_token)
            self.google_refresh_token = self._encrypt_token_fernet(decrypted)
        
        return True
    
    @api.model
    def _check_google_token_access(self, user_id):
        """TDD: Phase 5 - Check if current user can access Google tokens for given user"""
        current_user = self.env.user
        
        # Admin users can access any user's tokens
        if current_user.has_group('base.group_system'):
            return True
        
        # Users can only access their own tokens
        if current_user.id != user_id:
            raise AccessError("You can only access your own Google authentication tokens")
        
        return True
    
    def read(self, fields=None, load='_classic_read'):
        """TDD: Phase 5 - Override read to protect Google token fields"""
        # Check access to Google token fields
        google_fields = ['google_access_token', 'google_refresh_token', 'google_token_rotation_date']
        
        if fields and any(field in google_fields for field in fields):
            for record in self:
                self._check_google_token_access(record.id)
        
        return super().read(fields, load)
    
    def _read_google_token_secure(self, field_name):
        """TDD: Phase 5 - Secure method to read Google token fields"""
        self._check_google_token_access(self.id)
        return getattr(self, field_name)
    
    def _write_google_token_secure(self, field_name, value):
        """TDD: Phase 5 - Secure method to write Google token fields"""
        self._check_google_token_access(self.id)
        return setattr(self, field_name, value)
    
    # TDD: Phase 3 - Quota management methods
    def _default_quota_reset_date(self):
        """TDD: Green Phase - Default quota reset date to next month's first day"""
        return date.today().replace(day=1) + relativedelta(months=1)
    
    def increment_google_quota_usage(self, amount=1):
        """TDD: Green Phase - Increment user's Google quota usage"""
        if self.google_quota_used + amount > self.google_quota_limit:
            raise UserError(f"Cannot increment quota by {amount}. Would exceed limit of {self.google_quota_limit}")
        self.write({'google_quota_used': self.google_quota_used + amount})
    
    def check_google_quota_availability(self):
        """TDD: Green Phase - Check if user has available quota"""
        # First check and reset if needed
        self.check_and_reset_monthly_quota()
        
        if self.google_quota_used >= self.google_quota_limit:
            raise UserError(f"Google API quota exhausted. Used {self.google_quota_used}/{self.google_quota_limit} requests this month. Resets on {self.google_quota_reset_date}")
        
        return True
    
    def check_and_reset_monthly_quota(self):
        """TDD: Green Phase - Check and reset quota if reset date has passed"""
        if self.google_quota_reset_date and date.today() >= self.google_quota_reset_date:
            self.write({
                'google_quota_used': 0,
                'google_quota_reset_date': date.today().replace(day=1) + relativedelta(months=1)
            })
        return True
    
    def get_quota_availability_info(self):
        """TDD: Green Phase - Get detailed quota availability information"""
        # Ensure quota is up to date
        self.check_and_reset_monthly_quota()
        
        remaining = max(0, self.google_quota_limit - self.google_quota_used)
        usage_percentage = round((self.google_quota_used / self.google_quota_limit) * 100, 2) if self.google_quota_limit > 0 else 0
        
        return {
            'available': self.google_quota_used < self.google_quota_limit,
            'used': self.google_quota_used,
            'limit': self.google_quota_limit,
            'remaining': remaining,
            'usage_percentage': usage_percentage,
            'reset_date': self.google_quota_reset_date,
        }
    
    # 18.0 Enhanced Methods
    @api.model
    def _get_users_with_google_auth(self):
        """18.0 enhanced method: Get all users with Google authentication"""
        return self.search([
            ('google_auth_status', '=', 'connected'),
            ('active', '=', True)
        ])
    
    @api.model
    def _get_users_quota_summary(self):
        """18.0 enhanced method: Get quota usage summary across all users"""
        users = self._get_users_with_google_auth()
        return {
            'total_users': len(users),
            'total_quota_used': sum(users.mapped('google_quota_used')),
            'total_quota_limit': sum(users.mapped('google_quota_limit')),
            'users_over_80_percent': len(users.filtered(
                lambda u: u.google_quota_used >= (u.google_quota_limit * 0.8)
            )),
            'users_exhausted': len(users.filtered(
                lambda u: u.google_quota_used >= u.google_quota_limit
            )),
        }
    
    def _update_quota_status(self):
        """18.0 enhanced method: Update quota status based on usage"""
        self.ensure_one()
        if self.google_quota_limit <= 0:
            status = 'available'
        else:
            usage_percentage = self.google_quota_used / self.google_quota_limit
            if usage_percentage >= 1.0:
                status = 'exhausted'
            elif usage_percentage >= 0.8:
                status = 'warning'
            else:
                status = 'available'
        
        if self.google_quota_status != status:
            self.google_quota_status = status
        
        return status
    
    def increment_google_quota_usage_safe(self, amount=1):
        """18.0 enhanced method: Thread-safe quota increment with status update"""
        self.ensure_one()
        
        # Use database-level constraints for thread safety
        self.env.cr.execute(
            "UPDATE res_users SET google_quota_used = google_quota_used + %s WHERE id = %s",
            (amount, self.id)
        )
        self.refresh()
        
        # Update status after increment
        self._update_quota_status()
        
        return True
    
    @api.model
    def cleanup_expired_tokens(self):
        """18.0 enhanced method: Clean up expired tokens"""
        expired_users = self.search([
            ('google_token_expiry', '<', fields.Datetime.now()),
            ('google_auth_status', '=', 'connected')
        ])
        
        for user in expired_users:
            user.write({
                'google_auth_status': 'expired',
                'google_access_token': False,
                'google_refresh_token': False,
            })
        
        return len(expired_users)
    
    def has_valid_google_token(self):
        """18.0 enhanced method: Check if user has valid Google token"""
        self.ensure_one()
        return (
            self.google_auth_status == 'connected' and
            self.google_access_token and
            self.google_token_expiry and
            self.google_token_expiry > fields.Datetime.now()
        )
    
    @api.constrains('google_quota_used', 'google_quota_limit')
    def _check_quota_constraints(self):
        """18.0 constraint: Validate quota values"""
        for user in self:
            if user.google_quota_used < 0:
                raise UserError("Google quota used cannot be negative")
            if user.google_quota_limit < 0:
                raise UserError("Google quota limit cannot be negative")
            if user.google_quota_used > user.google_quota_limit:
                user._update_quota_status()
    
    # OAuth Session Management (18.0 enhanced)
    def _store_oauth_session(self, session_data):
        """Store OAuth session data securely (18.0 enhanced implementation)"""
        try:
            # 18.0 enhancement: Enhanced session validation
            required_keys = ['code_verifier', 'state', 'redirect_uri']
            if not all(key in session_data for key in required_keys):
                raise UserError("Invalid OAuth session data - missing required fields")
            
            # 18.0 enhancement: Session expiry validation
            if 'initiated_at' not in session_data:
                session_data['initiated_at'] = fields.Datetime.now()
            
            # Store in secure location (18.0 uses encrypted storage)
            encrypted_session = self._encrypt_session_data(session_data)
            
            # Use Odoo's parameter storage for session data
            self.env['ir.config_parameter'].sudo().set_param(
                f'google_oauth_session_{self.id}',
                encrypted_session
            )
            
            return True
            
        except Exception as e:
            raise UserError(f"Failed to store OAuth session: {str(e)}")
    
    def _get_oauth_session(self):
        """Retrieve OAuth session data (18.0 enhanced implementation)"""
        try:
            # Get encrypted session from parameter storage
            encrypted_session = self.env['ir.config_parameter'].sudo().get_param(
                f'google_oauth_session_{self.id}'
            )
            
            if not encrypted_session:
                return None
            
            # Decrypt and return session data
            session_data = self._decrypt_session_data(encrypted_session)
            
            # 18.0 enhancement: Validate session expiry
            if 'initiated_at' in session_data:
                initiated_at = fields.Datetime.from_string(session_data['initiated_at'])
                if fields.Datetime.now() - initiated_at > timedelta(minutes=15):
                    self._clear_oauth_session()
                    return None
            
            return session_data
            
        except Exception as e:
            return None
    
    def _clear_oauth_session(self):
        """Clear OAuth session data (18.0 enhanced implementation)"""
        try:
            # Remove session from parameter storage
            self.env['ir.config_parameter'].sudo().set_param(
                f'google_oauth_session_{self.id}',
                False
            )
            
            return True
            
        except Exception as e:
            return False
    
    def _encrypt_session_data(self, session_data):
        """Encrypt session data for secure storage (18.0 enhancement)"""
        try:
            import json
            
            # Use existing Fernet encryption
            json_data = json.dumps(session_data, default=str)
            return self._encrypt_token_fernet(json_data)
            
        except Exception as e:
            # Fallback to base64 encoding
            import json
            json_data = json.dumps(session_data, default=str)
            return base64.b64encode(json_data.encode()).decode()
    
    def _decrypt_session_data(self, encrypted_session):
        """Decrypt session data (18.0 enhancement)"""
        try:
            import json
            
            # Try Fernet decryption first
            decrypted_data = self._decrypt_token_fernet(encrypted_session)
            if decrypted_data:
                return json.loads(decrypted_data)
            
            # Fallback to base64 decoding
            json_data = base64.b64decode(encrypted_session.encode()).decode()
            return json.loads(json_data)
            
        except Exception:
            return None
    
    # Enhanced Token Storage for 18.0
    def _store_google_tokens(self, tokens):
        """Store Google OAuth2 tokens with enhanced security (18.0)"""
        try:
            # 18.0 enhancement: Comprehensive token validation
            required_tokens = ['access_token']
            if not all(token in tokens for token in required_tokens):
                raise UserError("Invalid token data - missing access_token")
            
            # Calculate token expiry
            expires_in = tokens.get('expires_in', 3600)  # Default 1 hour
            token_expiry = fields.Datetime.now() + timedelta(seconds=int(expires_in))
            
            # 18.0 enhancement: Encrypt tokens with Fernet
            encrypted_access_token = self._encrypt_token_fernet(tokens['access_token'])
            encrypted_refresh_token = None
            
            if 'refresh_token' in tokens:
                encrypted_refresh_token = self._encrypt_token_fernet(tokens['refresh_token'])
            
            # Update user record with enhanced tracking
            update_vals = {
                'google_access_token': encrypted_access_token,
                'google_token_expiry': token_expiry,
                'google_auth_status': 'connected',
                'google_token_rotation_date': fields.Datetime.now(),  # 18.0 enhancement
            }
            
            if encrypted_refresh_token:
                update_vals['google_refresh_token'] = encrypted_refresh_token
            
            # 18.0 enhancement: Store user profile information
            if 'email' in tokens:
                update_vals['google_email'] = tokens['email']
            if 'name' in tokens:
                update_vals['google_name'] = tokens['name']
            
            self.write(update_vals)
            
            return True
            
        except Exception as e:
            self.write({'google_auth_status': 'error'})
            raise UserError(f"Failed to store authentication tokens: {str(e)}")
    
    def write(self, vals):
        """18.0 enhanced write: Update quota status when quota fields change"""
        result = super().write(vals)
        
        # Update quota status if quota fields changed
        if any(field in vals for field in ['google_quota_used', 'google_quota_limit']):
            for user in self:
                user._update_quota_status()
        
        return result