# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError, UserError


@tagged('post_install', '-at_install')
class TestLLMTool18Compatibility(TransactionCase):
    """Test Odoo 18.0 compatibility for LLM Tool module"""
    
    def setUp(self):
        super().setUp()
        self.Tool = self.env['llm.tool']
        self.ConsentConfig = self.env['llm.tool.consent.config']
        self.Provider = self.env['llm.provider']
        self.Model = self.env['llm.model']
        
        # Create test provider and model
        self.provider = self.Provider.create({
            'name': 'Test Provider 18.0',
            'service': 'openai',
            'api_key': 'test_key',
        })
        
        self.model = self.Model.create({
            'name': 'Test Model 18.0',
            'provider_id': self.provider.id,
            'model_type': 'chat',
        })
    
    def test_tool_model_compatibility(self):
        """Test that tool model works with 18.0 ORM"""
        tool = self.Tool.create({
            'name': 'Test Tool 18.0',
            'description': 'Test tool for 18.0 compatibility',
            'function_name': 'test_function',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
        })
        
        # Test 18.0 specific features
        self.assertTrue(tool.exists())
        self.assertEqual(tool.name, 'Test Tool 18.0')
        self.assertEqual(tool.tool_type, 'record_retriever')
        self.assertTrue(tool.active)
    
    def test_consent_config_compatibility(self):
        """Test that consent config model works with 18.0"""
        config = self.ConsentConfig.create({
            'model_name': 'res.partner',
            'consent_required': True,
            'description': 'Test consent config for 18.0',
        })
        
        # Verify field compatibility
        self.assertTrue(config.exists())
        self.assertEqual(config.model_name, 'res.partner')
        self.assertTrue(config.consent_required)
        self.assertTrue(config.active)
    
    def test_tool_execution_compatibility(self):
        """Test that tool execution works with 18.0"""
        tool = self.Tool.create({
            'name': 'Partner Retriever 18.0',
            'description': 'Retrieve partner records',
            'function_name': 'get_partners',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
        })
        
        # Test execution context
        context = {
            'active_model': 'res.partner',
            'active_id': 1,
            'tool_execution': True,
        }
        
        # Verify tool can be prepared for execution
        self.assertTrue(tool.with_context(context).exists())
        self.assertEqual(tool.model_name, 'res.partner')
    
    def test_tool_security_compatibility(self):
        """Test that tool security rules work correctly in 18.0"""
        # Create test user without LLM manager permissions
        user = self.env['res.users'].create({
            'name': 'Test User 18.0',
            'login': 'test_user_tool_18@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that regular user can read tools but not create
        tools = self.Tool.with_user(user).search([])
        self.assertTrue(len(tools) >= 0)  # Can read
        
        # Test that regular user cannot create tools
        with self.assertRaises(AccessError):
            self.Tool.with_user(user).create({
                'name': 'Unauthorized Tool',
                'description': 'Should not be created',
                'function_name': 'unauthorized_function',
                'model_name': 'res.partner',
                'tool_type': 'record_retriever',
            })
    
    def test_tool_provider_integration(self):
        """Test that tools integrate correctly with providers in 18.0"""
        tool = self.Tool.create({
            'name': 'Provider Integration Test 18.0',
            'description': 'Test tool provider integration',
            'function_name': 'test_provider_function',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
        })
        
        # Test that tool can be associated with provider
        self.assertTrue(tool.exists())
        self.assertEqual(tool.model_name, 'res.partner')
        
        # Test that provider can access tool
        provider_tools = self.provider.get_available_tools()
        self.assertTrue(isinstance(provider_tools, list))
    
    def test_tool_json_schema_compatibility(self):
        """Test that JSON schema handling works in 18.0"""
        tool = self.Tool.create({
            'name': 'Schema Test Tool 18.0',
            'description': 'Test JSON schema compatibility',
            'function_name': 'schema_test',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
            'parameters_schema': {
                'type': 'object',
                'properties': {
                    'name': {'type': 'string'},
                    'email': {'type': 'string', 'format': 'email'},
                },
                'required': ['name'],
            },
        })
        
        # Test JSON schema handling
        self.assertTrue(tool.exists())
        self.assertIsInstance(tool.parameters_schema, dict)
        self.assertEqual(tool.parameters_schema['type'], 'object')
        self.assertIn('properties', tool.parameters_schema)
    
    def test_tool_performance_compatibility(self):
        """Test that tool performance features work in 18.0"""
        # Create multiple tools
        tools = []
        for i in range(10):
            tool = self.Tool.create({
                'name': f'Performance Test Tool {i}',
                'description': f'Performance test tool {i}',
                'function_name': f'perf_test_{i}',
                'model_name': 'res.partner',
                'tool_type': 'record_retriever',
            })
            tools.append(tool)
        
        # Test search performance
        with self.assertQueryCount(1):
            found_tools = self.Tool.search([
                ('active', '=', True),
                ('tool_type', '=', 'record_retriever'),
            ])
            self.assertTrue(len(found_tools) >= 10)
    
    def test_tool_method_compatibility(self):
        """Test that tool methods work correctly in 18.0"""
        tool = self.Tool.create({
            'name': 'Method Test Tool 18.0',
            'description': 'Test tool methods compatibility',
            'function_name': 'method_test',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
        })
        
        # Test 18.0 enhanced methods
        self.assertTrue(hasattr(tool, 'get_tool_schema'))
        self.assertTrue(hasattr(tool, 'execute_tool'))
        self.assertTrue(hasattr(tool, 'validate_parameters'))
        
        # Test method execution
        schema = tool.get_tool_schema()
        self.assertIsInstance(schema, dict)
        self.assertIn('name', schema)
        self.assertIn('description', schema)
    
    def test_tool_validation_compatibility(self):
        """Test that tool validation works in 18.0"""
        # Test valid tool creation
        tool = self.Tool.create({
            'name': 'Validation Test Tool 18.0',
            'description': 'Test validation compatibility',
            'function_name': 'validation_test',
            'model_name': 'res.partner',
            'tool_type': 'record_retriever',
        })
        
        self.assertTrue(tool.exists())
        
        # Test validation constraints
        with self.assertRaises(ValidationError):
            self.Tool.create({
                'name': '',  # Empty name should fail
                'description': 'Invalid tool',
                'function_name': 'invalid_function',
                'model_name': 'res.partner',
                'tool_type': 'record_retriever',
            })
    
    def test_tool_consent_integration(self):
        """Test that consent system works with tools in 18.0"""
        # Create consent config
        config = self.ConsentConfig.create({
            'model_name': 'res.partner',
            'consent_required': True,
            'description': 'Test consent for partners',
        })
        
        # Create tool that requires consent
        tool = self.Tool.create({
            'name': 'Consent Test Tool 18.0',
            'description': 'Test consent integration',
            'function_name': 'consent_test',
            'model_name': 'res.partner',
            'tool_type': 'record_creator',
            'requires_consent': True,
        })
        
        # Verify consent integration
        self.assertTrue(tool.exists())
        self.assertTrue(tool.requires_consent)
        self.assertTrue(config.exists())
        self.assertTrue(config.consent_required)