# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError, UserError


@tagged('post_install', '-at_install')
class TestLLMGemini18Compatibility(TransactionCase):
    """Test Odoo 18.0 compatibility for LLM Gemini module"""
    
    def setUp(self):
        super().setUp()
        self.Provider = self.env['llm.provider']
        self.Model = self.env['llm.model']
        self.Publisher = self.env['llm.publisher']
        self.Thread = self.env['llm.thread']
        self.Tool = self.env['llm.tool']
        self.User = self.env['res.users']
        
        # Create test publisher
        self.publisher = self.Publisher.create({
            'name': 'Google Test',
            'code': 'google_test',
        })
    
    def test_gemini_provider_compatibility(self):
        """Test that Gemini provider works with 18.0 ORM"""
        provider = self.Provider.create({
            'name': 'Gemini Test 18.0',
            'service': 'gemini',
            'api_key': 'test_key_18.0',
            'auth_mode': 'system',
        })
        
        # Test 18.0 specific features
        self.assertTrue(provider.exists())
        self.assertEqual(provider.name, 'Gemini Test 18.0')
        self.assertEqual(provider.service, 'gemini')
        self.assertEqual(provider.auth_mode, 'system')
        self.assertTrue(provider.active)
    
    def test_gemini_model_compatibility(self):
        """Test that Gemini models work with 18.0 ORM"""
        provider = self.Provider.create({
            'name': 'Gemini Provider 18.0',
            'service': 'gemini',
            'api_key': 'test_key',
        })
        
        model = self.Model.create({
            'name': 'gemini-pro',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
        })
        
        # Test 18.0 specific features
        self.assertTrue(model.exists())
        self.assertEqual(model.name, 'gemini-pro')
        self.assertEqual(model.provider_id, provider)
        self.assertEqual(model.publisher_id, self.publisher)
    
    def test_user_google_fields_compatibility(self):
        """Test that user Google authentication fields work in 18.0"""
        user = self.User.create({
            'name': 'Gemini User 18.0',
            'login': 'gemini_user_18@example.com',
            'google_email': 'test@gmail.com',
            'google_auth_status': 'connected',
        })
        
        # Test 18.0 specific features
        self.assertTrue(user.exists())
        self.assertEqual(user.google_email, 'test@gmail.com')
        self.assertEqual(user.google_auth_status, 'connected')
    
    def test_gemini_auth_modes_compatibility(self):
        """Test that auth modes work correctly in 18.0"""
        # Test system mode
        system_provider = self.Provider.create({
            'name': 'System Auth Provider 18.0',
            'service': 'gemini',
            'api_key': 'system_key',
            'auth_mode': 'system',
        })
        
        self.assertEqual(system_provider.auth_mode, 'system')
        
        # Test user mode
        user_provider = self.Provider.create({
            'name': 'User Auth Provider 18.0',
            'service': 'gemini',
            'auth_mode': 'user',
            'google_oauth_client_id': 'test_client_id',
            'google_oauth_client_secret': 'test_client_secret',
        })
        
        self.assertEqual(user_provider.auth_mode, 'user')
        self.assertTrue(user_provider.google_oauth_client_id)
    
    def test_gemini_security_compatibility(self):
        """Test that Gemini security rules work correctly in 18.0"""
        # Create test user
        user = self.User.create({
            'name': 'Test User Gemini 18.0',
            'login': 'test_user_gemini_18@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that regular user cannot access API key
        provider = self.Provider.create({
            'name': 'Secure Provider 18.0',
            'service': 'gemini',
            'api_key': 'secret_key',
        })
        
        with self.assertRaises(AccessError):
            provider.with_user(user).read(['api_key'])
    
    def test_gemini_oauth_config_compatibility(self):
        """Test OAuth configuration fields in 18.0"""
        provider = self.Provider.create({
            'name': 'OAuth Provider 18.0',
            'service': 'gemini',
            'auth_mode': 'user',
            'google_oauth_client_id': 'client_id_18.0',
            'google_oauth_client_secret': 'client_secret_18.0',
            'google_oauth_redirect_uri': 'http://localhost:8069/auth/callback',
        })
        
        # Test OAuth fields
        self.assertEqual(provider.google_oauth_client_id, 'client_id_18.0')
        self.assertEqual(provider.google_oauth_client_secret, 'client_secret_18.0')
        self.assertEqual(provider.google_oauth_redirect_uri, 'http://localhost:8069/auth/callback')
    
    def test_user_quota_fields_compatibility(self):
        """Test user quota management fields in 18.0"""
        user = self.User.create({
            'name': 'Quota User 18.0',
            'login': 'quota_user_18@example.com',
            'google_quota_limit': 20,
            'google_quota_used': 5,
        })
        
        # Test quota fields
        self.assertEqual(user.google_quota_limit, 20)
        self.assertEqual(user.google_quota_used, 5)
        self.assertTrue(hasattr(user, 'google_quota_reset_date'))
    
    def test_gemini_thread_integration_compatibility(self):
        """Test Gemini integration with threads in 18.0"""
        provider = self.Provider.create({
            'name': 'Thread Provider 18.0',
            'service': 'gemini',
            'api_key': 'test_key',
        })
        
        model = self.Model.create({
            'name': 'gemini-pro',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
        })
        
        thread = self.Thread.create({
            'name': 'Gemini Thread 18.0',
            'model_id': model.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
        
        # Test thread integration
        self.assertTrue(thread.exists())
        self.assertEqual(thread.model_id.provider_id.service, 'gemini')
    
    def test_gemini_performance_compatibility(self):
        """Test Gemini performance features in 18.0"""
        # Create multiple providers
        providers = []
        for i in range(5):
            provider = self.Provider.create({
                'name': f'Gemini Provider {i}',
                'service': 'gemini',
                'api_key': f'key_{i}',
            })
            providers.append(provider)
        
        # Test search performance
        with self.assertQueryCount(1):
            gemini_providers = self.Provider.search([
                ('service', '=', 'gemini'),
                ('active', '=', True),
            ])
            self.assertTrue(len(gemini_providers) >= 5)
    
    def test_gemini_method_compatibility(self):
        """Test that Gemini-specific methods work in 18.0"""
        provider = self.Provider.create({
            'name': 'Method Test Provider 18.0',
            'service': 'gemini',
            'api_key': 'test_key',
        })
        
        # Test 18.0 enhanced methods
        self.assertTrue(hasattr(provider, '_gemini_get_client'))
        self.assertTrue(hasattr(provider, '_gemini_generate_completion'))
        self.assertTrue(hasattr(provider, '_format_messages_for_gemini'))
    
    def test_gemini_validation_compatibility(self):
        """Test Gemini validation in 18.0"""
        # Test that user mode requires OAuth config
        with self.assertRaises(ValidationError):
            self.Provider.create({
                'name': 'Invalid Provider 18.0',
                'service': 'gemini',
                'auth_mode': 'user',
                # Missing OAuth configuration
            })
    
    def test_gemini_token_encryption_compatibility(self):
        """Test token encryption methods in 18.0"""
        user = self.User.create({
            'name': 'Encryption User 18.0',
            'login': 'encryption_user_18@example.com',
        })
        
        # Test encryption methods exist
        self.assertTrue(hasattr(user, '_encrypt_token_fernet'))
        self.assertTrue(hasattr(user, '_decrypt_token_fernet'))
        
        # Test basic encryption/decryption
        test_token = 'test_token_18.0'
        encrypted = user._encrypt_token_fernet(test_token)
        decrypted = user._decrypt_token_fernet(encrypted)
        self.assertEqual(decrypted, test_token)
    
    def test_gemini_message_formatting_compatibility(self):
        """Test message formatting for Gemini API in 18.0"""
        provider = self.Provider.create({
            'name': 'Format Test Provider 18.0',
            'service': 'gemini',
            'api_key': 'test_key',
        })
        
        # Test message formatting
        messages = [
            {'role': 'system', 'content': 'You are a helpful assistant.'},
            {'role': 'user', 'content': 'Hello!'},
            {'role': 'assistant', 'content': 'Hi there!'},
        ]
        
        formatted = provider._format_messages_for_gemini(messages)
        self.assertIsInstance(formatted, list)
        
        # Check role conversion
        for msg in formatted:
            self.assertIn('role', msg)
            self.assertIn(msg['role'], ['user', 'model'])
    
    def test_gemini_wizard_compatibility(self):
        """Test Gemini authentication wizard in 18.0"""
        Wizard = self.env['google.user.auth.wizard']
        
        provider = self.Provider.create({
            'name': 'Wizard Provider 18.0',
            'service': 'gemini',
            'auth_mode': 'user',
            'google_oauth_client_id': 'client_id',
            'google_oauth_client_secret': 'client_secret',
            'google_oauth_redirect_uri': 'http://localhost/callback',
        })
        
        wizard = Wizard.create({
            'provider_id': provider.id,
            'state': 'init',
        })
        
        # Test wizard creation and methods
        self.assertTrue(wizard.exists())
        self.assertEqual(wizard.state, 'init')
        self.assertTrue(hasattr(wizard, 'generate_auth_url'))
    
    def test_gemini_18_0_features(self):
        """Test Gemini with 18.0 specific features"""
        # Test field indexing and tracking
        provider = self.Provider.create({
            'name': 'Feature Test Provider 18.0',
            'service': 'gemini',
            'api_key': 'test_key',
        })
        
        # Verify that provider benefits from 18.0 indexed fields
        self.assertTrue(provider.active)
        
        # Test that name field benefits from indexing
        providers = self.Provider.search([
            ('name', 'ilike', 'Feature Test'),
            ('service', '=', 'gemini'),
        ])
        self.assertIn(provider, providers)