{
    "name": "Google Gemini LLM Integration",
    "summary": "Google Gemini provider integration for LLM module with dual authentication",
    "description": """
        Implements Google Gemini provider service for the LLM integration module.
        
        Features:
        - Dual Authentication Architecture (System API Key + User OAuth2)
        - Google OAuth2 personal authentication support
        - User quota management with monthly limits
        - Fernet encryption for secure token storage
        - Gemini 2.5 Pro, Flash, and Flash-lite models
        - Enterprise-grade security and audit logging
        - Test-Driven Development (TDD) methodology
        
        This module allows users to utilize their own Google account and 
        free quota allocation through personal OAuth2 authentication.
    """,
    "author": "Apexive Solutions LLC",
    "website": "https://github.com/apexive/odoo-llm",
    "category": "Technical",
    "version": "16.0.1.0.0",
    "depends": ["llm", "llm_tool"],
    "external_dependencies": {
        "python": ["google-generativeai", "cryptography"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/llm_publisher.xml",
        "data/llm_provider.xml", 
        "data/llm_model.xml",
        "views/llm_provider_views.xml",
        "views/res_users_views.xml",
        "wizards/google_user_auth_wizard_views.xml",
    ],
    "images": [
        "static/description/banner.jpeg",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}