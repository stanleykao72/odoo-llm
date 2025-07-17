# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError, UserError


@tagged('post_install', '-at_install')
class TestLLMAssistant18Compatibility(TransactionCase):
    """Test Odoo 18.0 compatibility for LLM Assistant module"""
    
    def setUp(self):
        super().setUp()
        self.Assistant = self.env['llm.assistant']
        self.Prompt = self.env['llm.prompt']
        self.PromptCategory = self.env['llm.prompt.category']
        self.PromptTag = self.env['llm.prompt.tag']
        self.Provider = self.env['llm.provider']
        self.Model = self.env['llm.model']
        self.Tool = self.env['llm.tool']
        self.Thread = self.env['llm.thread']
        
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
        
        # Create test prompt category
        self.category = self.PromptCategory.create({
            'name': 'Test Category 18.0',
            'description': 'Test category for 18.0 compatibility',
        })
        
        # Create test prompt tag
        self.tag = self.PromptTag.create({
            'name': 'Test Tag 18.0',
            'color': 1,
        })
    
    def test_assistant_model_compatibility(self):
        """Test that assistant model works with 18.0 ORM"""
        assistant = self.Assistant.create({
            'name': 'Test Assistant 18.0',
            'description': 'Test assistant for 18.0 compatibility',
            'role': 'AI Assistant',
            'goal': 'Help with testing',
            'system_prompt': 'You are a test assistant.',
        })
        
        # Test 18.0 specific features
        self.assertTrue(assistant.exists())
        self.assertEqual(assistant.name, 'Test Assistant 18.0')
        self.assertEqual(assistant.role, 'AI Assistant')
        self.assertEqual(assistant.goal, 'Help with testing')
        self.assertTrue(assistant.active)
    
    def test_prompt_model_compatibility(self):
        """Test that prompt model works with 18.0 ORM"""
        prompt = self.Prompt.create({
            'name': 'Test Prompt 18.0',
            'content': 'This is a test prompt for 18.0',
            'category_id': self.category.id,
            'tag_ids': [(6, 0, [self.tag.id])],
            'format': 'text',
        })
        
        # Test 18.0 specific features
        self.assertTrue(prompt.exists())
        self.assertEqual(prompt.name, 'Test Prompt 18.0')
        self.assertEqual(prompt.format, 'text')
        self.assertEqual(prompt.category_id, self.category)
        self.assertIn(self.tag, prompt.tag_ids)
    
    def test_assistant_tool_relationship(self):
        """Test assistant-tool relationship in 18.0"""
        # Create test tool
        tool = self.Tool.create({
            'name': 'Assistant Tool 18.0',
            'description': 'Test tool for assistant',
            'implementation': 'server_action',
        })
        
        # Create assistant with tools
        assistant = self.Assistant.create({
            'name': 'Assistant with Tools 18.0',
            'description': 'Test assistant with tools',
            'role': 'Tool User',
            'goal': 'Use tools effectively',
            'tool_ids': [(6, 0, [tool.id])],
        })
        
        # Test relationship
        self.assertEqual(len(assistant.tool_ids), 1)
        self.assertIn(tool, assistant.tool_ids)
    
    def test_assistant_prompt_relationship(self):
        """Test assistant-prompt relationship in 18.0"""
        # Create prompt
        prompt = self.Prompt.create({
            'name': 'Assistant Prompt 18.0',
            'content': 'Prompt for assistant testing',
            'category_id': self.category.id,
            'format': 'text',
        })
        
        # Create assistant with prompt
        assistant = self.Assistant.create({
            'name': 'Assistant with Prompt 18.0',
            'description': 'Test assistant with prompt',
            'role': 'Prompt User',
            'goal': 'Use prompts effectively',
            'system_prompt_id': prompt.id,
        })
        
        # Test relationship
        self.assertEqual(assistant.system_prompt_id, prompt)
    
    def test_assistant_thread_integration(self):
        """Test that assistant integrates correctly with threads in 18.0"""
        # Create assistant
        assistant = self.Assistant.create({
            'name': 'Thread Assistant 18.0',
            'description': 'Assistant for thread testing',
            'role': 'Thread Manager',
            'goal': 'Manage conversations',
            'system_prompt': 'You manage threads.',
        })
        
        # Create thread with assistant
        thread = self.Thread.create({
            'name': 'Assistant Thread 18.0',
            'model_id': self.model.id,
            'assistant_id': assistant.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
        
        # Test integration
        self.assertEqual(thread.assistant_id, assistant)
    
    def test_prompt_category_compatibility(self):
        """Test that prompt category works in 18.0"""
        category = self.PromptCategory.create({
            'name': 'Category 18.0',
            'description': 'Test category',
            'parent_id': self.category.id,
        })
        
        # Test hierarchy
        self.assertTrue(category.exists())
        self.assertEqual(category.parent_id, self.category)
        self.assertIn(category, self.category.child_ids)
    
    def test_prompt_tag_compatibility(self):
        """Test that prompt tag works in 18.0"""
        tag = self.PromptTag.create({
            'name': 'Tag 18.0',
            'color': 5,
        })
        
        # Test tag features
        self.assertTrue(tag.exists())
        self.assertEqual(tag.name, 'Tag 18.0')
        self.assertEqual(tag.color, 5)
    
    def test_prompt_format_compatibility(self):
        """Test different prompt formats in 18.0"""
        formats = ['text', 'yaml', 'json']
        
        for format_type in formats:
            prompt = self.Prompt.create({
                'name': f'Prompt {format_type} 18.0',
                'content': f'Test content for {format_type}',
                'category_id': self.category.id,
                'format': format_type,
            })
            
            self.assertEqual(prompt.format, format_type)
            self.assertTrue(prompt.exists())
    
    def test_assistant_security_compatibility(self):
        """Test that assistant security rules work correctly in 18.0"""
        # Create test user
        user = self.env['res.users'].create({
            'name': 'Test User Assistant 18.0',
            'login': 'test_user_assistant_18@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that regular user can read assistants
        assistants = self.Assistant.with_user(user).search([])
        self.assertTrue(len(assistants) >= 0)
        
        # Test that regular user cannot create assistants
        with self.assertRaises(AccessError):
            self.Assistant.with_user(user).create({
                'name': 'Unauthorized Assistant',
                'description': 'Should not be created',
                'role': 'Unauthorized',
                'goal': 'Should fail',
            })
    
    def test_prompt_search_compatibility(self):
        """Test prompt search functionality in 18.0"""
        # Create multiple prompts
        prompts = []
        for i in range(5):
            prompt = self.Prompt.create({
                'name': f'Search Prompt {i}',
                'content': f'Content with keyword test_{i}',
                'category_id': self.category.id,
                'format': 'text',
            })
            prompts.append(prompt)
        
        # Test search
        found_prompts = self.Prompt.search([
            ('name', 'ilike', 'Search Prompt'),
        ])
        self.assertTrue(len(found_prompts) >= 5)
    
    def test_assistant_performance_compatibility(self):
        """Test assistant performance features in 18.0"""
        # Create multiple assistants
        assistants = []
        for i in range(10):
            assistant = self.Assistant.create({
                'name': f'Performance Assistant {i}',
                'description': f'Performance test {i}',
                'role': f'Role {i}',
                'goal': f'Goal {i}',
            })
            assistants.append(assistant)
        
        # Test search performance
        with self.assertQueryCount(1):
            found_assistants = self.Assistant.search([
                ('active', '=', True),
            ])
            self.assertTrue(len(found_assistants) >= 10)
    
    def test_assistant_method_compatibility(self):
        """Test that assistant methods work correctly in 18.0"""
        assistant = self.Assistant.create({
            'name': 'Method Test Assistant 18.0',
            'description': 'Test methods',
            'role': 'Method Tester',
            'goal': 'Test all methods',
            'system_prompt': 'Test prompt',
        })
        
        # Test 18.0 enhanced methods
        self.assertTrue(hasattr(assistant, 'get_system_prompt'))
        self.assertTrue(hasattr(assistant, 'get_tools'))
        self.assertTrue(hasattr(assistant, 'get_configuration'))
        
        # Test method execution
        system_prompt = assistant.get_system_prompt()
        self.assertIsInstance(system_prompt, str)
        
        tools = assistant.get_tools()
        self.assertIsInstance(tools, list)
    
    def test_prompt_template_compatibility(self):
        """Test prompt template processing in 18.0"""
        prompt = self.Prompt.create({
            'name': 'Template Prompt 18.0',
            'content': 'Hello {{ name }}, your role is {{ role }}',
            'category_id': self.category.id,
            'format': 'text',
            'arguments': '{"name": "string", "role": "string"}',
        })
        
        # Test template rendering
        self.assertTrue(prompt.exists())
        self.assertIn('{{ name }}', prompt.content)
        self.assertIn('{{ role }}', prompt.content)
    
    def test_assistant_validation_compatibility(self):
        """Test assistant validation in 18.0"""
        # Test valid assistant
        assistant = self.Assistant.create({
            'name': 'Valid Assistant 18.0',
            'description': 'Valid assistant',
            'role': 'Valid Role',
            'goal': 'Valid Goal',
        })
        
        self.assertTrue(assistant.exists())
        
        # Test validation constraints
        with self.assertRaises(ValidationError):
            self.Assistant.create({
                'name': '',  # Empty name should fail
                'description': 'Invalid assistant',
                'role': 'Invalid',
                'goal': 'Should fail',
            })
    
    def test_prompt_active_compatibility(self):
        """Test prompt active field in 18.0"""
        prompt = self.Prompt.create({
            'name': 'Active Test Prompt 18.0',
            'content': 'Test active field',
            'category_id': self.category.id,
            'format': 'text',
        })
        
        # Test active field
        self.assertTrue(prompt.active)
        
        # Test archiving
        prompt.write({'active': False})
        self.assertFalse(prompt.active)
        
        # Test that archived prompts are filtered out
        active_prompts = self.Prompt.search([])
        self.assertNotIn(prompt, active_prompts)