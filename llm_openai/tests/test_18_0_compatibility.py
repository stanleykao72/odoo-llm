# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError, UserError


@tagged('post_install', '-at_install')
class TestLLMOpenAI18Compatibility(TransactionCase):
    """Test Odoo 18.0 compatibility for LLM OpenAI module"""
    
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
            'name': 'OpenAI Test',
            'code': 'openai_test',
        })
    
    def test_openai_provider_compatibility(self):
        """Test that OpenAI provider works with 18.0 ORM"""
        provider = self.Provider.create({
            'name': 'OpenAI Test 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key_18.0',
            'base_url': 'https://api.openai.com/v1/',
        })
        
        # Test 18.0 specific features
        self.assertTrue(provider.exists())
        self.assertEqual(provider.name, 'OpenAI Test 18.0')
        self.assertEqual(provider.service, 'openai')
        self.assertEqual(provider.base_url, 'https://api.openai.com/v1/')
        self.assertTrue(provider.active)
    
    def test_openai_model_compatibility(self):
        """Test that OpenAI models work with 18.0 ORM"""
        provider = self.Provider.create({
            'name': 'OpenAI Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        model = self.Model.create({
            'name': 'gpt-4',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
        })
        
        # Test 18.0 specific features
        self.assertTrue(model.exists())
        self.assertEqual(model.name, 'gpt-4')
        self.assertEqual(model.provider_id, provider)
        self.assertEqual(model.publisher_id, self.publisher)
    
    def test_openai_configuration_fields_compatibility(self):
        """Test that OpenAI configuration fields work in 18.0"""
        provider = self.Provider.create({
            'name': 'OpenAI Config Test 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
            'base_url': 'https://api.openai.com/v1/',
            'organization_id': 'org-test123',
            'project_id': 'proj-test456',
        })
        
        # Test 18.0 specific features
        self.assertTrue(provider.exists())
        self.assertEqual(provider.base_url, 'https://api.openai.com/v1/')
        self.assertEqual(provider.organization_id, 'org-test123')
        self.assertEqual(provider.project_id, 'proj-test456')
    
    def test_openai_security_compatibility(self):
        """Test that OpenAI security rules work correctly in 18.0"""
        # Create test user
        user = self.User.create({
            'name': 'Test User OpenAI 18.0',
            'login': 'test_user_openai_18@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that regular user cannot access API key
        provider = self.Provider.create({
            'name': 'Secure Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-secret_key',
        })
        
        with self.assertRaises(AccessError):
            provider.with_user(user).read(['api_key'])
    
    def test_openai_thread_integration_compatibility(self):
        """Test OpenAI integration with threads in 18.0"""
        provider = self.Provider.create({
            'name': 'Thread Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        model = self.Model.create({
            'name': 'gpt-4',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
        })
        
        thread = self.Thread.create({
            'name': 'OpenAI Thread 18.0',
            'model_id': model.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
        
        # Test thread integration
        self.assertTrue(thread.exists())
        self.assertEqual(thread.model_id.provider_id.service, 'openai')
    
    def test_openai_performance_compatibility(self):
        """Test OpenAI performance features in 18.0"""
        # Create multiple providers
        providers = []
        for i in range(5):
            provider = self.Provider.create({
                'name': f'OpenAI Provider {i}',
                'service': 'openai',
                'api_key': f'sk-key_{i}',
            })
            providers.append(provider)
        
        # Test search performance with indexed fields
        with self.assertQueryCount(1):
            openai_providers = self.Provider.search([
                ('service', '=', 'openai'),
                ('active', '=', True),
            ])
            self.assertTrue(len(openai_providers) >= 5)
    
    def test_openai_method_compatibility(self):
        """Test that OpenAI-specific methods work in 18.0"""
        provider = self.Provider.create({
            'name': 'Method Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        # Test 18.0 enhanced methods
        self.assertTrue(hasattr(provider, '_openai_get_client'))
        self.assertTrue(hasattr(provider, '_openai_generate_completion'))
        self.assertTrue(hasattr(provider, '_openai_generate_embedding'))
    
    def test_openai_validation_compatibility(self):
        """Test OpenAI validation in 18.0"""
        # Test that OpenAI provider requires API key
        with self.assertRaises(ValidationError):
            self.Provider.create({
                'name': 'Invalid Provider 18.0',
                'service': 'openai',
                # Missing API key
            })
    
    def test_openai_url_validation_compatibility(self):
        """Test OpenAI URL validation in 18.0"""
        provider = self.Provider.create({
            'name': 'URL Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
            'base_url': 'https://api.openai.com/v1/',
        })
        
        # Test URL validation
        self.assertTrue(provider.base_url.startswith('https://'))
        self.assertTrue(provider.base_url.endswith('/'))
    
    def test_openai_model_types_compatibility(self):
        """Test OpenAI model types in 18.0"""
        provider = self.Provider.create({
            'name': 'Model Type Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        # Test different model types
        chat_model = self.Model.create({
            'name': 'gpt-4',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
        })
        
        embedding_model = self.Model.create({
            'name': 'text-embedding-3-large',
            'provider_id': provider.id,
            'model_type': 'embedding',
            'publisher_id': self.publisher.id,
        })
        
        # Test model types
        self.assertEqual(chat_model.model_type, 'chat')
        self.assertEqual(embedding_model.model_type, 'embedding')
    
    def test_openai_streaming_compatibility(self):
        """Test OpenAI streaming support in 18.0"""
        provider = self.Provider.create({
            'name': 'Streaming Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        model = self.Model.create({
            'name': 'gpt-4',
            'provider_id': provider.id,
            'model_type': 'chat',
            'publisher_id': self.publisher.id,
            'supports_streaming': True,
        })
        
        # Test streaming support
        self.assertTrue(model.supports_streaming)
    
    def test_openai_organization_project_compatibility(self):
        """Test OpenAI organization and project fields in 18.0"""
        provider = self.Provider.create({
            'name': 'Org Project Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
            'organization_id': 'org-123456789',
            'project_id': 'proj-abcdef123',
        })
        
        # Test organization and project fields
        self.assertEqual(provider.organization_id, 'org-123456789')
        self.assertEqual(provider.project_id, 'proj-abcdef123')
    
    def test_openai_18_0_features(self):
        """Test OpenAI with 18.0 specific features"""
        # Test field indexing and tracking
        provider = self.Provider.create({
            'name': 'Feature Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
            'base_url': 'https://api.openai.com/v1/',
        })
        
        # Verify that provider benefits from 18.0 indexed fields
        self.assertTrue(provider.active)
        
        # Test that name field benefits from indexing
        providers = self.Provider.search([
            ('name', 'ilike', 'Feature Test'),
            ('service', '=', 'openai'),
        ])
        self.assertIn(provider, providers)
    
    def test_openai_error_handling_compatibility(self):
        """Test OpenAI error handling in 18.0"""
        provider = self.Provider.create({
            'name': 'Error Test Provider 18.0',
            'service': 'openai',
            'api_key': 'sk-test_key',
        })
        
        # Test that provider has proper error handling methods
        self.assertTrue(hasattr(provider, '_handle_openai_error'))
        self.assertTrue(hasattr(provider, '_validate_openai_response'))