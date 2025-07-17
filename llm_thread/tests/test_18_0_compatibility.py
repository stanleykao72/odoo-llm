# -*- coding: utf-8 -*-
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import AccessError, ValidationError, UserError


@tagged('post_install', '-at_install')
class TestLLMThread18Compatibility(TransactionCase):
    """Test Odoo 18.0 compatibility for LLM Thread module"""
    
    def setUp(self):
        super().setUp()
        self.Thread = self.env['llm.thread']
        self.Message = self.env['llm.thread.message']
        self.Provider = self.env['llm.provider']
        self.Model = self.env['llm.model']
        self.Tool = self.env['llm.tool']
        
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
        
        # Create test thread
        self.thread = self.Thread.create({
            'name': 'Test Thread 18.0',
            'model_id': self.model.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
    
    def test_thread_model_compatibility(self):
        """Test that thread model works with 18.0 ORM"""
        thread = self.Thread.create({
            'name': 'Thread Compatibility Test 18.0',
            'model_id': self.model.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
        
        # Test 18.0 specific features
        self.assertTrue(thread.exists())
        self.assertEqual(thread.name, 'Thread Compatibility Test 18.0')
        self.assertEqual(thread.model_id, self.model)
        self.assertEqual(thread.res_model, 'res.partner')
        self.assertTrue(thread.active)
    
    def test_message_model_compatibility(self):
        """Test that message model works with 18.0 ORM"""
        message = self.Message.create({
            'thread_id': self.thread.id,
            'body': 'Test message for 18.0 compatibility',
            'llm_role': 'user',
        })
        
        # Test 18.0 specific features
        self.assertTrue(message.exists())
        self.assertEqual(message.thread_id, self.thread)
        self.assertEqual(message.body, 'Test message for 18.0 compatibility')
        self.assertEqual(message.llm_role, 'user')
    
    def test_thread_message_relationship(self):
        """Test thread-message relationship in 18.0"""
        # Create messages for the thread
        message1 = self.Message.create({
            'thread_id': self.thread.id,
            'body': 'First message',
            'llm_role': 'user',
        })
        
        message2 = self.Message.create({
            'thread_id': self.thread.id,
            'body': 'Second message',
            'llm_role': 'assistant',
        })
        
        # Test relationship
        self.assertEqual(len(self.thread.message_ids), 2)
        self.assertIn(message1, self.thread.message_ids)
        self.assertIn(message2, self.thread.message_ids)
    
    def test_thread_tool_relationship(self):
        """Test thread-tool relationship in 18.0"""
        # Create test tool
        tool = self.Tool.create({
            'name': 'Test Tool 18.0',
            'description': 'Test tool for 18.0 compatibility',
            'implementation': 'server_action',
        })
        
        # Associate tool with thread
        self.thread.write({
            'tool_ids': [(6, 0, [tool.id])],
        })
        
        # Test relationship
        self.assertEqual(len(self.thread.tool_ids), 1)
        self.assertIn(tool, self.thread.tool_ids)
    
    def test_thread_security_compatibility(self):
        """Test that thread security rules work correctly in 18.0"""
        # Create test user without LLM manager permissions
        user = self.env['res.users'].create({
            'name': 'Test User Thread 18.0',
            'login': 'test_user_thread_18@example.com',
            'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
        })
        
        # Test that regular user can read threads but not create system threads
        threads = self.Thread.with_user(user).search([])
        self.assertTrue(len(threads) >= 0)  # Can read
        
        # Test that regular user cannot create system threads
        with self.assertRaises(AccessError):
            self.Thread.with_user(user).create({
                'name': 'Unauthorized Thread',
                'model_id': self.model.id,
                'res_model': 'res.partner',
                'res_id': 1,
                'is_system': True,
            })
    
    def test_thread_performance_compatibility(self):
        """Test that thread performance features work in 18.0"""
        # Create multiple messages with different roles
        messages = []
        for i in range(20):
            role = 'user' if i % 2 == 0 else 'assistant'
            message = self.Message.create({
                'thread_id': self.thread.id,
                'body': f'Message {i}',
                'llm_role': role,
            })
            messages.append(message)
        
        # Test search performance with indexed llm_role field
        with self.assertQueryCount(1):
            user_messages = self.Message.search([
                ('thread_id', '=', self.thread.id),
                ('llm_role', '=', 'user'),
            ])
            self.assertEqual(len(user_messages), 10)
    
    def test_thread_context_compatibility(self):
        """Test that thread context handling works in 18.0"""
        # Create thread with context
        thread = self.Thread.create({
            'name': 'Context Test Thread 18.0',
            'model_id': self.model.id,
            'res_model': 'res.partner',
            'res_id': 1,
            'context': '{"test_key": "test_value"}',
        })
        
        # Test context handling
        self.assertTrue(thread.exists())
        self.assertEqual(thread.context, '{"test_key": "test_value"}')
    
    def test_thread_model_integration(self):
        """Test that thread integrates correctly with model in 18.0"""
        # Test model relationship
        self.assertEqual(self.thread.model_id, self.model)
        self.assertEqual(self.thread.model_id.provider_id, self.provider)
        
        # Test model access through thread
        self.assertEqual(self.thread.model_id.name, 'Test Model 18.0')
        self.assertEqual(self.thread.model_id.model_type, 'chat')
    
    def test_thread_record_relationship(self):
        """Test that thread relates to records correctly in 18.0"""
        # Create test partner
        partner = self.env['res.partner'].create({
            'name': 'Test Partner 18.0',
            'email': 'test@example.com',
        })
        
        # Create thread for partner
        thread = self.Thread.create({
            'name': 'Partner Thread 18.0',
            'model_id': self.model.id,
            'res_model': 'res.partner',
            'res_id': partner.id,
        })
        
        # Test relationship
        self.assertEqual(thread.res_model, 'res.partner')
        self.assertEqual(thread.res_id, partner.id)
    
    def test_thread_active_compatibility(self):
        """Test that thread active field works correctly in 18.0"""
        # Test active field
        self.assertTrue(self.thread.active)
        
        # Test archiving
        self.thread.write({'active': False})
        self.assertFalse(self.thread.active)
        
        # Test that archived threads are filtered out
        active_threads = self.Thread.search([])
        self.assertNotIn(self.thread, active_threads)
    
    def test_thread_method_compatibility(self):
        """Test that thread methods work correctly in 18.0"""
        # Test 18.0 enhanced methods
        self.assertTrue(hasattr(self.thread, 'get_thread_messages'))
        self.assertTrue(hasattr(self.thread, 'add_message'))
        self.assertTrue(hasattr(self.thread, 'get_context'))
        
        # Test method execution
        messages = self.thread.get_thread_messages()
        self.assertIsInstance(messages, list)
        
        context = self.thread.get_context()
        self.assertIsInstance(context, dict)
    
    def test_thread_validation_compatibility(self):
        """Test that thread validation works in 18.0"""
        # Test valid thread creation
        thread = self.Thread.create({
            'name': 'Validation Test Thread 18.0',
            'model_id': self.model.id,
            'res_model': 'res.partner',
            'res_id': 1,
        })
        
        self.assertTrue(thread.exists())
        
        # Test validation constraints
        with self.assertRaises(ValidationError):
            self.Thread.create({
                'name': '',  # Empty name should fail
                'model_id': self.model.id,
                'res_model': 'res.partner',
                'res_id': 1,
            })
    
    def test_message_llm_role_compatibility(self):
        """Test that message llm_role field works correctly in 18.0"""
        # Test different roles
        roles = ['user', 'assistant', 'system', 'tool']
        for role in roles:
            message = self.Message.create({
                'thread_id': self.thread.id,
                'body': f'Message with role {role}',
                'llm_role': role,
            })
            self.assertEqual(message.llm_role, role)
    
    def test_thread_streaming_compatibility(self):
        """Test that thread streaming features work in 18.0"""
        # Test streaming state
        self.assertFalse(self.thread.is_streaming)
        
        # Test streaming toggle
        self.thread.write({'is_streaming': True})
        self.assertTrue(self.thread.is_streaming)
        
        # Test streaming reset
        self.thread.write({'is_streaming': False})
        self.assertFalse(self.thread.is_streaming)