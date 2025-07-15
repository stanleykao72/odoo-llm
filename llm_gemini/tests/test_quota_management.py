# -*- coding: utf-8 -*-

from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime
from dateutil.relativedelta import relativedelta


@tagged('post_install', '-at_install')
class TestGeminiQuotaManagement(TransactionCase):
    """Test Gemini quota management functionality following TDD principles"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test provider - minimal setup for quota testing
        cls.provider = cls.env['llm.provider'].create({
            'name': 'Test Gemini Quota Provider',
            'service': 'gemini',
            # Use basic fields that exist from Phase 1
        })

    def test_quota_initialization_for_new_user(self):
        """RED PHASE: Test that user quota is properly initialized with default values"""
        # Create new user
        user = self.env['res.users'].create({
            'name': 'Test Quota User',
            'login': 'quotauser@example.com',
        })
        
        # Test that quota fields are initialized with default values
        # This will FAIL because quota fields don't exist yet
        self.assertEqual(user.google_quota_used, 0, "New user should start with 0 quota used")
        self.assertEqual(user.google_quota_limit, 15, "New user should have default limit of 15")
        
        # Test that quota reset date is set to next month's first day
        expected_reset_date = date.today().replace(day=1) + relativedelta(months=1)
        self.assertEqual(user.google_quota_reset_date, expected_reset_date, 
                        "Quota reset date should be set to next month")
        
        # Test that quota status is properly initialized
        self.assertEqual(user.google_quota_status, 'available', 
                        "New user quota status should be 'available'")

    def test_usage_increment_functionality(self):
        """RED PHASE: Test that quota usage increments correctly"""
        # Create test user with some initial quota
        user = self.env['res.users'].create({
            'name': 'Test Increment User',
            'login': 'increment@example.com',
            'google_quota_used': 5,
            'google_quota_limit': 15,
        })
        
        # Test quota increment method - this doesn't exist yet
        initial_usage = user.google_quota_used
        user.increment_google_quota_usage()
        
        self.assertEqual(user.google_quota_used, initial_usage + 1, 
                        "Quota usage should increment by 1")
        
        # Test multiple increments
        user.increment_google_quota_usage(amount=3)
        self.assertEqual(user.google_quota_used, initial_usage + 4, 
                        "Quota usage should increment by specified amount")

    def test_quota_limit_enforcement(self):
        """RED PHASE: Test that requests are blocked when quota exceeded"""
        # Create user at quota limit
        user = self.env['res.users'].create({
            'name': 'Test Limit User',
            'login': 'limit@example.com',
            'google_quota_used': 15,
            'google_quota_limit': 15,
        })
        
        # Test that quota check fails when limit reached
        # This method doesn't exist yet - will fail
        with self.assertRaises(UserError, msg="Should raise UserError when quota exceeded"):
            user.check_google_quota_availability()
        
        # Test that quota check passes when under limit
        user.google_quota_used = 10
        result = user.check_google_quota_availability()
        self.assertTrue(result, "Quota check should pass when under limit")
        
        # Test that increment is blocked when at limit
        user.google_quota_used = 15
        with self.assertRaises(UserError, msg="Should block increment when at limit"):
            user.increment_google_quota_usage()

    def test_monthly_quota_reset_mechanism(self):
        """RED PHASE: Test automatic monthly quota reset"""
        # Create user with used quota and past reset date
        past_date = date.today() - relativedelta(months=1)
        user = self.env['res.users'].create({
            'name': 'Test Reset User',
            'login': 'reset@example.com',
            'google_quota_used': 10,
            'google_quota_limit': 15,
            'google_quota_reset_date': past_date,
        })
        
        # Test automatic reset when checking quota
        # This method doesn't exist yet - will fail
        user.check_and_reset_monthly_quota()
        
        # Verify quota was reset
        self.assertEqual(user.google_quota_used, 0, "Quota usage should be reset to 0")
        
        # Verify reset date was updated to next month
        expected_reset_date = date.today().replace(day=1) + relativedelta(months=1)
        self.assertEqual(user.google_quota_reset_date, expected_reset_date,
                        "Reset date should be updated to next month")

    def test_quota_availability_check_with_prerequest_validation(self):
        """RED PHASE: Test pre-request quota validation"""
        # Create user with available quota
        user = self.env['res.users'].create({
            'name': 'Test Availability User',
            'login': 'availability@example.com',
            'google_quota_used': 5,
            'google_quota_limit': 15,
        })
        
        # Test quota availability check before API call
        # This method doesn't exist yet - will fail
        availability_result = user.get_quota_availability_info()
        
        expected_result = {
            'available': True,
            'used': 5,
            'limit': 15,
            'remaining': 10,
            'usage_percentage': 33.33,
            'reset_date': user.google_quota_reset_date,
        }
        
        self.assertEqual(availability_result['available'], True, 
                        "Should indicate quota is available")
        self.assertEqual(availability_result['remaining'], 10, 
                        "Should calculate correct remaining quota")
        self.assertEqual(availability_result['usage_percentage'], 33.33, 
                        "Should calculate correct usage percentage")
        
        # Test when quota is exhausted
        user.google_quota_used = 15
        exhausted_result = user.get_quota_availability_info()
        self.assertEqual(exhausted_result['available'], False, 
                        "Should indicate quota is exhausted")
        self.assertEqual(exhausted_result['remaining'], 0, 
                        "Should show 0 remaining quota")