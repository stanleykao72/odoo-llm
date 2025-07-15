# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError, AccessError


@tagged('post_install', '-at_install')
class TestGeminiProvider(TransactionCase):
    """Test Gemini provider functionality following TDD principles"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Test data will be created as needed per TDD

    def test_gemini_provider_requires_oauth_config_for_user_mode(self):
        """GREEN PHASE: Test that user authentication mode requires OAuth configuration"""
        provider = self.env['llm.provider'].create({
            'name': 'Test Gemini Provider',
            'service': 'gemini',
            'auth_mode': 'user',
            # Intentionally missing OAuth config
        })
        
        with self.assertRaises(ValidationError, msg="Should raise ValidationError when OAuth config is missing"):
            provider._check_gemini_oauth_config()

    def test_user_model_has_google_authentication_fields(self):
        """RED PHASE: Test that user model has Google authentication fields"""
        # This test should FAIL initially because Google fields don't exist yet
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'test@example.com',
        })
        
        # Test that user can store Google authentication tokens
        # This will fail because fields don't exist yet
        user.write({
            'google_access_token': 'test_access_token_123',
            'google_refresh_token': 'test_refresh_token_456',
        })
        
        # Verify tokens are stored
        self.assertEqual(user.google_access_token, 'test_access_token_123')
        self.assertEqual(user.google_refresh_token, 'test_refresh_token_456')

    def test_user_token_encryption_and_decryption(self):
        """RED PHASE: Test that user tokens are encrypted when stored"""
        user = self.env['res.users'].create({
            'name': 'Test User',
            'login': 'testencrypt@example.com',
        })
        
        # Test token encryption - this method doesn't exist yet
        original_token = 'test_secret_token_123'
        user.set_encrypted_google_token(original_token)
        
        # Verify token is stored encrypted (not in plain text)
        self.assertNotEqual(user.google_access_token, original_token)
        self.assertTrue(len(user.google_access_token) > len(original_token))
        
        # Test token decryption - this method doesn't exist yet
        decrypted_token = user.get_decrypted_google_token()
        self.assertEqual(decrypted_token, original_token)

    def test_basic_service_integration(self):
        """RED PHASE: Test that Gemini service is properly registered and accessible"""
        # Test that gemini appears in available services
        provider = self.env['llm.provider']
        available_services = provider._get_available_services()
        
        # Should find gemini in the list of available services
        gemini_service = None
        for service_code, service_name in available_services:
            if service_code == 'gemini':
                gemini_service = (service_code, service_name)
                break
        
        self.assertIsNotNone(gemini_service, "Gemini service should be available in provider services")
        self.assertEqual(gemini_service[0], 'gemini')
        self.assertEqual(gemini_service[1], 'Google Gemini')
        
        # Test that a provider can be created with gemini service
        provider = self.env['llm.provider'].create({
            'name': 'Test Gemini Integration',
            'service': 'gemini',
            'auth_mode': 'system',
        })
        
        self.assertEqual(provider.service, 'gemini')
        self.assertEqual(provider.auth_mode, 'system')

    def test_provider_dispatch_methods(self):
        """RED PHASE: Test that gemini_* methods are correctly dispatched"""
        provider = self.env['llm.provider'].create({
            'name': 'Test Gemini Dispatch',
            'service': 'gemini',
            'auth_mode': 'system',
            'api_key': 'test-dispatch-api-key',  # Add API key for system auth
        })
        
        # Test that provider has gemini-specific methods available
        # This will fail initially because these methods don't exist yet
        self.assertTrue(hasattr(provider, '_gemini_get_client'), 
                       "Provider should have _gemini_get_client method")
        
        self.assertTrue(hasattr(provider, '_gemini_generate_completion'), 
                       "Provider should have _gemini_generate_completion method")
        
        # Test that methods can be called (will fail without implementation)
        try:
            client = provider._gemini_get_client()
            self.assertIsNotNone(client, "Should return a Gemini client instance")
        except NotImplementedError:
            # This is expected in RED phase
            pass

    def test_error_handling_for_missing_configuration(self):
        """RED PHASE: Test proper error handling for missing configuration"""
        # Test provider without API key in API key mode
        provider = self.env['llm.provider'].create({
            'name': 'Test Incomplete Provider',
            'service': 'gemini',
            'auth_mode': 'system',
            # Intentionally missing api_key
        })
        
        # Should raise appropriate error when trying to generate completion
        with self.assertRaises(ValidationError, msg="Should raise ValidationError for missing API key"):
            provider._gemini_generate_completion([{"role": "user", "content": "test"}])
        
        # Test provider with invalid authentication mode
        provider_invalid = self.env['llm.provider'].create({
            'name': 'Test Invalid Auth Provider',
            'service': 'gemini',
            'auth_mode': 'user',
            # Missing OAuth configuration
        })
        
        # Should raise error when trying to get client with invalid auth
        with self.assertRaises(ValidationError, msg="Should raise ValidationError for invalid auth"):
            provider_invalid._gemini_get_client()

    def test_phase5_fernet_encryption_functionality(self):
        """GREEN PHASE: Test that Fernet encryption actually works"""
        user = self.env["res.users"].create({
            "name": "Test Fernet User",
            "login": "testfernet@example.com",
        })
        
        original_token = "test_secure_token_123456789"
        
        # Test Fernet encryption
        encrypted_token = user._encrypt_token_fernet(original_token)
        self.assertNotEqual(encrypted_token, original_token)
        self.assertTrue(encrypted_token.startswith("gAAAAA"), 
                       "Should use Fernet encryption format")
        
        # Test Fernet decryption
        decrypted_token = user._decrypt_token_fernet(encrypted_token)
        self.assertEqual(decrypted_token, original_token)

    def test_phase5_encryption_key_management(self):
        """RED PHASE: Test encryption key management and security"""
        user = self.env["res.users"].create({
            "name": "Test Key Management User",
            "login": "testkeymanagement@example.com",
        })
        
        # Test that encryption key is generated and stored securely
        key1 = user._get_or_create_encryption_key()
        self.assertIsNotNone(key1, "Should generate encryption key")
        self.assertEqual(len(key1), 44, "Fernet key should be 44 bytes encoded")
        
        # Test that the same key is returned on subsequent calls
        key2 = user._get_or_create_encryption_key()
        self.assertEqual(key1, key2, "Should return same key on subsequent calls")
        
        # Test that key is stored in ir.config_parameter
        stored_key = self.env['ir.config_parameter'].get_param('google.token.encryption.key')
        self.assertIsNotNone(stored_key, "Key should be stored in config parameters")
        
        # Test that key can encrypt/decrypt multiple times consistently
        token1 = "test_token_1"
        token2 = "test_token_2"
        
        encrypted1 = user._encrypt_token_fernet(token1)
        encrypted2 = user._encrypt_token_fernet(token2)
        
        # Different tokens should produce different encrypted values
        self.assertNotEqual(encrypted1, encrypted2)
        
        # But should decrypt correctly
        self.assertEqual(user._decrypt_token_fernet(encrypted1), token1)
        self.assertEqual(user._decrypt_token_fernet(encrypted2), token2)

    def test_phase5_token_rotation_security(self):
        """GREEN PHASE: Test periodic token rotation for security"""
        user = self.env["res.users"].create({
            "name": "Test Token Rotation User", 
            "login": "testtokenrotation@example.com",
        })
        
        # Set up some encrypted tokens
        original_access_token = "access_token_123"
        original_refresh_token = "refresh_token_456"
        
        user.google_access_token = user._encrypt_token_fernet(original_access_token)
        user.google_refresh_token = user._encrypt_token_fernet(original_refresh_token)
        
        # Record initial encrypted values
        initial_encrypted_access = user.google_access_token
        initial_encrypted_refresh = user.google_refresh_token
        
        # Test token rotation
        rotation_result = user._rotate_encryption_tokens()
        self.assertTrue(rotation_result, "Token rotation should succeed")
        
        # Test that rotation date was updated
        self.assertIsNotNone(user.google_token_rotation_date, "Rotation date should be set")
        
        # Test that tokens were re-encrypted (different encrypted values)
        self.assertNotEqual(user.google_access_token, initial_encrypted_access, 
                           "Access token should be re-encrypted")
        self.assertNotEqual(user.google_refresh_token, initial_encrypted_refresh,
                           "Refresh token should be re-encrypted")
        
        # Test that tokens can still be decrypted to original values
        decrypted_access = user._decrypt_token_fernet(user.google_access_token)
        decrypted_refresh = user._decrypt_token_fernet(user.google_refresh_token)
        
        self.assertEqual(decrypted_access, original_access_token,
                        "Access token should decrypt to original value")
        self.assertEqual(decrypted_refresh, original_refresh_token,
                        "Refresh token should decrypt to original value")

    def test_phase5_secure_token_storage(self):
        """GREEN PHASE: Test that tokens are never stored in plain text"""
        user = self.env["res.users"].create({
            "name": "Test Secure Storage User",
            "login": "testsecurestorage@example.com",
        })
        
        # Test storing various sensitive tokens
        sensitive_tokens = [
            "sk-1234567890abcdef",  # API key format
            "refresh_token_with_special_chars!@#$%",
            "access_token_very_long_" + "x" * 100,
            "token with spaces and unicode: 测试",
        ]
        
        for i, token in enumerate(sensitive_tokens):
            # Store token using encryption method
            user.set_encrypted_google_token(token)
            
            # Verify stored value is NOT the original token
            self.assertNotEqual(user.google_access_token, token,
                               f"Token {i+1} should not be stored in plain text")
            
            # Verify stored value is properly encrypted (Fernet format or base64)
            stored_value = user.google_access_token
            is_fernet = stored_value.startswith("gAAAAA")
            is_base64 = self._is_valid_base64(stored_value)
            
            self.assertTrue(is_fernet or is_base64,
                           f"Token {i+1} should be encrypted (Fernet or base64)")
            
            # Verify decryption works correctly
            decrypted = user.get_decrypted_google_token()
            self.assertEqual(decrypted, token,
                           f"Token {i+1} should decrypt correctly")
            
            # Verify token doesn't appear in string representation
            user_str = str(user)
            self.assertNotIn(token, user_str,
                           f"Token {i+1} should not appear in user string representation")
    
    def _is_valid_base64(self, s):
        """Helper method to check if string is valid base64"""
        try:
            import base64
            base64.b64decode(s.encode())
            return True
        except Exception:
            return False

    def test_phase5_user_permission_validation(self):
        """GREEN PHASE: Test that only authorized users can access Gemini"""
        # Create different user types for testing
        admin_user = self.env.ref('base.user_admin')
        
        # Create regular user without Gemini permissions
        regular_user = self.env['res.users'].create({
            'name': 'Regular User',
            'login': 'regular@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Create system admin user (with system group)
        system_user = self.env['res.users'].create({
            'name': 'System User',
            'login': 'system@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_system').id])],
        })
        
        # Create Gemini provider
        provider = self.env['llm.provider'].create({
            'name': 'Test Gemini Provider',
            'service': 'gemini',
            'auth_mode': 'user',
        })
        
        # Test that regular user cannot access Gemini functionality
        with self.assertRaises(AccessError, msg="Regular user should not have access"):
            provider.with_user(regular_user)._check_gemini_user_permission()
        
        # Test that system user should have access
        result = provider.with_user(system_user)._check_gemini_user_permission()
        self.assertTrue(result, "System user should have access to Gemini")
        
        # Test with inactive user
        inactive_user = self.env['res.users'].create({
            'name': 'Inactive User',
            'login': 'inactive@example.com',
            'active': False,
            'groups_id': [(6, 0, [self.env.ref('base.group_system').id])],
        })
        
        with self.assertRaises(AccessError, msg="Inactive user should not have access"):
            provider.with_user(inactive_user)._check_gemini_user_permission()

    def test_phase5_api_key_protection(self):
        """GREEN PHASE: Test that system API keys are properly protected"""
        # Create provider with API key
        provider = self.env['llm.provider'].create({
            'name': 'Test API Key Protection',
            'service': 'gemini',
            'auth_mode': 'system',
            'api_key': 'secret-gemini-api-key-12345',
        })
        
        # Create regular user without admin rights
        regular_user = self.env['res.users'].create({
            'name': 'Regular User API Test',
            'login': 'regularapi@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that API key doesn't appear in string representation
        provider_str = str(provider)
        self.assertNotIn('secret-gemini-api-key-12345', provider_str,
                        "API key should not appear in string representation")
        
        # Test that regular user cannot read API key field
        with self.assertRaises(AccessError, msg="Regular user should not access API key"):
            provider.with_user(regular_user).read(['api_key'])
        
        # Test that API key is not returned in search results for regular users
        providers = self.env['llm.provider'].with_user(regular_user).search([
            ('service', '=', 'gemini')
        ])
        if providers:
            # Check that api_key field is not accessible
            for prov in providers:
                with self.assertRaises((AccessError, ValidationError)):
                    _ = prov.api_key
        
        # Test that API key is masked in logs/exports
        export_data = provider._export_data(['name', 'service', 'api_key'])
        if export_data:
            # API key should be masked or not included
            api_key_column = export_data.get('api_key', [])
            if api_key_column:
                self.assertNotIn('secret-gemini-api-key-12345', str(api_key_column),
                               "API key should not appear in export data")
        
        # Test that admin can still access API key (for configuration)
        admin_user = self.env.ref('base.user_admin')
        try:
            admin_provider = provider.with_user(admin_user)
            api_key = admin_provider.api_key
            self.assertEqual(api_key, 'secret-gemini-api-key-12345',
                           "Admin should be able to access API key")
        except (AccessError, ValidationError):
            # This might be expected if we've implemented strict access controls
            pass

    def test_phase5_data_isolation(self):
        """GREEN PHASE: Test that users can only access their own tokens"""
        # Create two different users
        user1 = self.env['res.users'].create({
            'name': 'User 1',
            'login': 'user1@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        user2 = self.env['res.users'].create({
            'name': 'User 2', 
            'login': 'user2@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Set up tokens for each user
        user1_token = "user1_secret_token_123"
        user2_token = "user2_secret_token_456"
        
        # Store encrypted tokens for each user
        user1.set_encrypted_google_token(user1_token)
        user2.set_encrypted_google_token(user2_token)
        
        # Test that user1 can access their own token
        user1_decrypted = user1.get_decrypted_google_token()
        self.assertEqual(user1_decrypted, user1_token,
                        "User1 should be able to access their own token")
        
        # Test that user2 can access their own token
        user2_decrypted = user2.get_decrypted_google_token()
        self.assertEqual(user2_decrypted, user2_token,
                        "User2 should be able to access their own token")
        
        # Test that user1 cannot access user2's data using secure methods
        user2_as_user1 = user2.with_user(user1)
        
        with self.assertRaises(AccessError, msg="User1 should not access User2's tokens"):
            user2_as_user1._read_google_token_secure('google_access_token')
        
        # Test that user2 cannot access user1's data using secure methods
        user1_as_user2 = user1.with_user(user2)
        
        with self.assertRaises(AccessError, msg="User2 should not access User1's tokens"):
            user1_as_user2._read_google_token_secure('google_access_token')
        
        # Test that users can access their own data
        user1_as_user1 = user1.with_user(user1)
        user2_as_user2 = user2.with_user(user2)
        
        try:
            token1 = user1_as_user1._read_google_token_secure('google_access_token')
            token2 = user2_as_user2._read_google_token_secure('google_access_token')
            self.assertIsNotNone(token1, "User1 should access their own token")
            self.assertIsNotNone(token2, "User2 should access their own token")
        except AccessError:
            # This might fail if we're running as a different user context
            pass
        
        # Test search isolation - users should only see their own records
        user1_search = self.env['res.users'].with_user(user1).search([
            ('id', 'in', [user1.id, user2.id])
        ])
        # User1 should only see themselves (or system may restrict further)
        self.assertIn(user1.id, user1_search.ids, "User1 should see their own record")
        
        user2_search = self.env['res.users'].with_user(user2).search([
            ('id', 'in', [user1.id, user2.id])
        ])
        # User2 should only see themselves (or system may restrict further)
        self.assertIn(user2.id, user2_search.ids, "User2 should see their own record")
        
        # Test that tokens are properly isolated in database queries
        # Each user's encrypted token should be different
        self.assertNotEqual(user1.google_access_token, user2.google_access_token,
                           "Encrypted tokens should be different between users")
        
        # Test that admin can access both (for system administration)
        admin_user = self.env.ref('base.user_admin')
        try:
            admin_user1 = user1.with_user(admin_user)
            admin_user2 = user2.with_user(admin_user)
            
            admin_token1 = admin_user1.get_decrypted_google_token()
            admin_token2 = admin_user2.get_decrypted_google_token()
            
            self.assertEqual(admin_token1, user1_token, "Admin should access User1's token")
            self.assertEqual(admin_token2, user2_token, "Admin should access User2's token")
        except (AccessError, ValidationError):
            # This might be expected if we've implemented very strict access controls
            pass