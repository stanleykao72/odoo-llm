# -*- coding: utf-8 -*-

import base64
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from cryptography.fernet import Fernet
from odoo import models, fields, api
from odoo.exceptions import AccessError, UserError


class ResUsers(models.Model):
    _inherit = 'res.users'
    
    # TDD: Green Phase - Minimal fields to make test pass
    google_access_token = fields.Char(string='Google Access Token')
    google_refresh_token = fields.Char(string='Google Refresh Token')
    
    # TDD: Phase 5 - Token rotation security fields
    google_token_rotation_date = fields.Datetime(string='Last Token Rotation Date')
    
    # TDD: Phase 3 - Quota management fields
    google_quota_used = fields.Integer(string='Google Quota Used This Month', default=0)
    google_quota_limit = fields.Integer(string='Google Quota Limit', default=15)
    google_quota_reset_date = fields.Date(string='Quota Reset Date', default=lambda self: self._default_quota_reset_date())
    google_quota_status = fields.Selection([
        ('available', 'Available'),
        ('warning', 'Warning'),
        ('exhausted', 'Exhausted')
    ], string='Quota Status', default='available')
    
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