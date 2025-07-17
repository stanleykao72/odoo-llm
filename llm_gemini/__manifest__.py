{
    "name": "Google Gemini LLM Integration",
    "summary": "Google Gemini provider integration for LLM module with dual authentication",
    "description": """
        Implements Google Gemini provider service for the LLM integration module.
        Enhanced for Odoo 18.0 with advanced authentication capabilities.
        
        Features:
        - Triple Authentication Architecture (System API Key + User OAuth2 + Browser Auth)
        - Browser-based authentication with PKCE security (similar to Gemini CLI)
        - Enhanced 18.0 features with tracking, indexing, and constraints
        - Cross-platform browser support (Windows, macOS, Linux)
        - User quota management with monthly limits and monitoring
        - Fernet encryption for secure token storage
        - Gemini 2.5 Pro, Flash, and Flash-lite models
        - Enterprise-grade security and audit logging
        - Enhanced OAuth session management
        - Test-Driven Development (TDD) methodology
        
        This module allows users to utilize their own Google account with one-click
        browser authentication or traditional OAuth2 flows.
    """,
    "author": "Apexive Solutions LLC",
    "website": "https://github.com/apexive/odoo-llm",
    "category": "Technical",
    "version": "18.0.1.1.0",
    "depends": ["llm", "llm_tool"],
    "external_dependencies": {
        "python": ["google-generativeai", "cryptography", "requests"],
    },
    "data": [
        "security/ir.model.access.csv",
        "data/llm_publisher.xml",
        "data/llm_provider.xml", 
        "data/llm_model.xml",
        "views/llm_provider_views.xml",
        "views/browser_auth_wizard_views.xml",
        # "views/res_users_views.xml",
        # "wizards/google_user_auth_wizard_views.xml",
    ],
    "images": [
        "static/description/banner.jpeg",
    ],
    "license": "LGPL-3",
    "installable": True,
    "auto_install": False,
}