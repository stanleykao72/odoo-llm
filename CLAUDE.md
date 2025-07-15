# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Methodology

This project follows a **strict Test-Driven Development (TDD) methodology** combined with **Tidy First principles** for disciplined, high-quality Odoo module development.

### Core TDD Cycle: Red → Green → Refactor

**Always follow the TDD cycle rigorously:**

1. **Red Phase**: Write a failing test that describes the desired behavior
2. **Green Phase**: Write the minimal code to make the test pass
3. **Refactor Phase**: Improve code structure while maintaining functionality

### Fundamental Principles

#### **Tidy First Integration**
- **Separate structural changes from behavioral changes**
- **Never mix structural and behavioral changes in the same commit**
- **Structural changes must precede behavioral changes**
- **Each commit represents a single logical unit of work**

#### **Quality Standards**
- **Eliminate duplication ruthlessly**
- **Express intent clearly through naming and structure**
- **Keep methods small and focused**
- **Minimize state and side effects**
- **Use the simplest solution that works**

### Commit Discipline

**Commit ONLY when:**
- ✅ All tests are passing
- ✅ All compiler/linter warnings are resolved
- ✅ Changes represent a single logical work unit
- ✅ Commit message clearly indicates change type (structural vs behavioral)

**Commit Requirements:**
- Small, frequent commits preferred
- Clear, descriptive commit messages
- Separate commits for structural vs behavioral changes
- Never commit broken or incomplete functionality

### TDD Workflow for Odoo Development

This section adapts the strict TDD methodology to Odoo's testing framework and module architecture using **Docker**.

#### **Red Phase: Writing Failing Odoo Tests**

**1. Test Structure and Organization**
```python
from odoo.tests.common import TransactionCase
from odoo.tests import tagged
from odoo.exceptions import UserError

@tagged('post_install', '-at_install')
class TestLLMProvider(TransactionCase):
    """Test LLM Provider functionality following TDD principles"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Create test data efficiently at class level
        cls.provider = cls.env['llm.provider'].create({
            'name': 'Test Provider',
            'provider_type': 'openai',
            'api_key': False,  # Intentionally empty for testing
        })
    
    def test_generate_completion_requires_api_key(self):
        """Test that completion generation fails without API key"""
        with self.assertRaises(UserError, msg="Should raise UserError when API key is missing"):
            self.provider.generate_completion("test prompt")
    
    def test_completion_with_valid_configuration(self):
        """Test successful completion generation with valid configuration"""
        self.provider.api_key = "test-key-123"
        result = self.provider.generate_completion("Hello")
        self.assertIsInstance(result, str, "Should return string response")
        self.assertTrue(len(result) > 0, "Response should not be empty")
```

**2. Test Execution Commands (Docker)**
```bash
# Run specific test during Red phase
docker compose exec odoo odoo-bin --test-tags=/llm:TestLLMProvider.test_generate_completion_requires_api_key

# Run all tests for a module
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable

# Run tests with detailed output
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable --log-level=test
```

#### **Green Phase: Minimal Odoo Implementation**

**1. Implement Only What Makes Tests Pass**
```python
class LLMProvider(models.Model):
    _name = 'llm.provider'
    _description = 'LLM Provider Configuration'
    
    name = fields.Char(required=True)
    provider_type = fields.Selection([('openai', 'OpenAI')], required=True)
    api_key = fields.Char()
    
    def generate_completion(self, prompt):
        """Generate completion - minimal implementation for Green phase"""
        if not self.api_key:
            raise UserError("API key is required for completion generation")
        
        # Minimal implementation that passes the test
        return f"Generated response for: {prompt}"
```

**2. Verify Green State (Docker)**
```bash
# Ensure all tests pass
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable --stop-after-init

# Verify module installation
docker compose exec odoo odoo-bin -i llm_provider --stop-after-init
```

#### **Refactor Phase: Odoo Code Optimization**

**1. Structural Improvements (Separate Commit)**
```python
class LLMProvider(models.Model):
    _name = 'llm.provider'
    _description = 'LLM Provider Configuration'
    
    name = fields.Char(required=True)
    provider_type = fields.Selection([('openai', 'OpenAI')], required=True)
    api_key = fields.Char()
    
    def generate_completion(self, prompt):
        """Generate completion with improved structure"""
        self._validate_configuration()
        return self._call_provider_api(prompt)
    
    def _validate_configuration(self):
        """Validate provider configuration"""
        if not self.api_key:
            raise UserError("API key is required for completion generation")
    
    def _call_provider_api(self, prompt):
        """Call the provider API - extracted for clarity"""
        return f"Generated response for: {prompt}"
```

**2. Refactoring Verification (Docker)**
```bash
# Run tests after each refactoring step
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable

# Verify no regressions
docker compose exec odoo odoo-bin --test-tags=standard --test-enable
```

### Module Task Management

Since this project uses **28 independent Odoo modules** instead of a central `plan.md`, we implement a **distributed task management system** using module-level CLAUDE.md files.

#### **Module-Level CLAUDE.md Structure**

Each module maintains its own CLAUDE.md file with the following structure:

```markdown
# {module_name}/CLAUDE.md

## Current Development Tasks
- [ ] Task 1: Description with acceptance criteria
- [ ] Task 2: Description with acceptance criteria
- [x] Completed Task: Description

## Module Dependencies
- **Depends on**: module1, module2 (must be implemented first)
- **Required by**: module3, module4 (blocking these modules)
- **Optional integration**: module5, module6

## Test Strategy
- **Unit Tests**: Core functionality validation
- **Integration Tests**: Cross-module interaction
- **Performance Tests**: Query count and response time
- **Security Tests**: Access control and validation

## Development Notes
- Architecture decisions
- Known limitations
- Future considerations
```

#### **Cross-Module Coordination**

**1. Dependency Management (Docker)**
```bash
# Check module dependencies before development
grep -r "depends.*llm_" */CLAUDE.md

# Verify installation order
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d test_db --init=llm,llm_provider,llm_thread --dry-run
```

**2. Integration Testing (Docker)**
```bash
# Test module interactions
docker compose exec odoo odoo-bin --test-tags=/llm,/llm_provider --test-enable

# Full integration test
docker compose exec odoo odoo-bin --test-tags=post_install --test-enable
```

### Quick Start Guide

For immediate TDD development, follow these steps:

1. **Setup Docker Environment**: 
   ```bash
   # Start Docker services
   docker compose up -d
   ```

2. **Start TDD Cycle**:
   ```bash
   # Run complete automated TDD cycle in Docker
   docker compose exec odoo odoo-bin --test-tags=/your_module_name --test-enable
   ```

3. **Quality Check Before Commit**:
   ```bash
   # Docker-based quality checks
   docker compose exec odoo python -m py_compile /mnt/extra-addons/your_module_name/models/*.py
   ```

### Quality Gates and Standards

#### **Pre-Commit Checklist (Docker)**
```bash
# 1. All tests pass
docker compose exec odoo odoo-bin --test-tags=/current_module --test-enable

# 2. Module installation succeeds
docker compose exec odoo odoo-bin -i current_module --stop-after-init

# 3. No Python syntax errors
docker compose exec odoo python -m py_compile /mnt/extra-addons/current_module/models/*.py

# 4. XML syntax validation
docker compose exec odoo xmllint --noout /mnt/extra-addons/current_module/views/*.xml

# 5. Security rules validation
docker compose exec odoo odoo-bin --test-tags=access_rights --test-enable
```

#### **Performance Standards**
```python
# Use assertQueryCount for performance testing
class TestLLMPerformance(TransactionCase):
    
    def test_message_query_performance(self):
        """Ensure indexed llm_role field provides 10x performance"""
        with self.assertQueryCount(5):  # Maximum 5 queries allowed
            messages = self.env['llm.thread.message'].search([
                ('llm_role', '=', 'user')
            ], limit=100)
            self.assertTrue(len(messages) >= 0)
```

#### **Security Validation**
```python
def test_api_key_security(self):
    """Ensure API keys are properly protected"""
    provider = self.env['llm.provider'].create({
        'name': 'Test Provider',
        'api_key': 'secret-key-123'
    })
    
    # API key should not appear in string representation
    self.assertNotIn('secret-key-123', str(provider))
    
    # API key should not appear in read() without proper access
    with self.assertRaises(AccessError):
        provider.with_user(self.demo_user).read(['api_key'])
```

## Project Overview

This is the **Odoo LLM Integration** project - a comprehensive framework for integrating Large Language Models (LLMs) into Odoo. The project provides a unified API for various AI providers (OpenAI, Anthropic, Ollama, Replicate, etc.) with features like chat completions, embeddings, RAG (Retrieval-Augmented Generation), and AI assistants.

## Architecture

### Modular Structure
The project is organized into **28 independent Odoo modules**, each with specific functionality:

- **Core Modules**:
  - `llm` - Base framework with providers, models, and core functionality
  - `llm_thread` - Chat thread management with PostgreSQL locking
  - `llm_assistant` - AI assistants with integrated prompt templates
  - `llm_tool` - Framework for LLM tool execution and Odoo data interaction

- **Provider Modules**:
  - `llm_openai`, `llm_anthropic`, `llm_ollama`, `llm_mistral`, `llm_replicate`, `llm_fal_ai`, `llm_litellm`

- **Knowledge Base (RAG)**:
  - `llm_knowledge` - Core RAG functionality
  - `llm_store` - Vector store abstraction
  - `llm_pgvector`, `llm_chroma`, `llm_qdrant` - Vector database integrations

- **Generation & Tools**:
  - `llm_generate` - Unified content generation API
  - `llm_generate_job` - Background job processing
  - `llm_tool_knowledge` - Knowledge base tools for LLMs

### Key Architectural Patterns
- **Odoo Model Architecture**: Each module follows standard Odoo patterns with `__manifest__.py`, `models/`, `views/`, `security/`
- **Provider Pattern**: Standardized provider interface for different LLM APIs
- **Tool Framework**: Structured tool execution with JSON schema validation
- **Performance Optimization**: Indexed `llm_role` field for 10x faster message queries

## TDD Development Commands

This section provides the essential commands for following the strict TDD workflow in Odoo development.

> **🐳 Docker Required**: All development is done using Docker. Ensure you have `docker` and `docker-compose` installed on your system.

### Initial Setup and Environment

#### **1. Docker Project Setup**
```bash
# Start Docker services
docker compose up -d

# Create test database for TDD development
docker compose exec db createdb -U odoo odoo_tdd_test

# Initial module installation (base framework)
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -i llm --stop-after-init
```

#### **2. Development Database Management (Docker)**
```bash
# Reset test database for clean TDD cycle
docker compose exec db dropdb -U odoo odoo_tdd_test && docker compose exec db createdb -U odoo odoo_tdd_test

# Install specific module set for development
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -i llm,llm_provider,llm_assistant --stop-after-init

# Check module dependencies before development
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test --init=llm_assistant --dry-run
```

### TDD Cycle Commands

#### **Red Phase: Failing Test Execution (Docker)**
```bash
# Run single failing test (Red Phase)
docker compose exec odoo odoo-bin --test-tags=/llm_provider:TestLLMProvider.test_generate_completion_requires_api_key

# Run all tests for current module to establish baseline
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable --stop-after-init

# Verify test failure with detailed output
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable --log-level=test
```

#### **Green Phase: Minimal Implementation Verification (Docker)**
```bash
# Run specific test to verify it passes
docker compose exec odoo odoo-bin --test-tags=/llm_provider:TestLLMProvider.test_generate_completion_requires_api_key

# Run all module tests to ensure no regressions
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable --stop-after-init

# Install/update module after minimal implementation
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -u llm_provider --stop-after-init
```

#### **Refactor Phase: Comprehensive Validation (Docker)**
```bash
# Run module tests during refactoring
docker compose exec odoo odoo-bin --test-tags=/llm_provider --test-enable

# Run cross-module integration tests
docker compose exec odoo odoo-bin --test-tags=/llm,/llm_provider --test-enable

# Run performance tests to validate optimizations
docker compose exec odoo odoo-bin --test-tags=/llm_provider:TestLLMPerformance --test-enable

# Full regression test suite
docker compose exec odoo odoo-bin --test-tags=standard,post_install --test-enable
```

### Pre-Commit Validation Commands

#### **Quality Gate Checklist (Docker)**
```bash
# 1. All tests pass
docker compose exec odoo odoo-bin --test-tags=/current_module --test-enable --stop-after-init

# 2. Module installation/upgrade succeeds
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -u current_module --stop-after-init

# 3. Python syntax validation
docker compose exec odoo find /mnt/extra-addons/current_module -name "*.py" -exec python -m py_compile {} \;

# 4. XML syntax validation
docker compose exec odoo find /mnt/extra-addons/current_module -name "*.xml" -exec xmllint --noout {} \;

# 5. Security rules validation
docker compose exec odoo odoo-bin --test-tags=access_rights,/current_module --test-enable
```

#### **Performance Validation (Docker)**
```bash
# Query performance validation
docker compose exec odoo odoo-bin --test-tags=/current_module:TestPerformance --test-enable

# Memory usage profiling (if available)
docker compose exec odoo odoo-bin --test-tags=/current_module --test-enable --profile

# Database query analysis
docker compose exec odoo odoo-bin --test-tags=/current_module --test-enable --log-level=debug
```

### Advanced TDD Commands

#### **Test Discovery and Execution (Docker)**
```bash
# List all available tests for a module
docker compose exec odoo odoo-bin --test-tags=/llm_assistant --dry-run

# Run tests by specific pattern
docker compose exec odoo odoo-bin --test-tags='*.test_*_security'

# Run only fast tests (exclude slow/integration)
docker compose exec odoo odoo-bin --test-tags='standard,-slow,-post_install'

# Run comprehensive test suite
docker compose exec odoo odoo-bin --test-tags='*' --test-enable
```

#### **Debugging and Analysis (Docker)**
```bash
# Run single test with debugging
docker compose exec odoo odoo-bin --test-tags=/module:TestClass.test_method --test-enable --log-level=debug

# Run tests with profiling
docker compose exec odoo odoo-bin --test-tags=/module --test-enable --profile

# Check test coverage (if coverage.py is installed)
docker compose exec odoo coverage run --source=. odoo-bin --test-tags=/module --test-enable
docker compose exec odoo coverage report -m
```

#### **Multi-Module Development (Docker)**
```bash
# Test module dependencies
docker compose exec odoo odoo-bin --test-tags=/llm,/llm_provider,/llm_assistant --test-enable

# Install and test multiple modules
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -i llm_provider,llm_assistant --test-enable --stop-after-init

# Update multiple modules with testing
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -u llm_provider,llm_assistant --test-enable --stop-after-init
```

### Continuous Integration Commands

#### **CI/CD Pipeline Commands (Docker)**
```bash
# Full CI test suite (for automation)
docker compose exec odoo odoo-bin --test-tags=standard,post_install --test-enable --stop-after-init

# Security and compliance testing
docker compose exec odoo odoo-bin --test-tags=security,access_rights --test-enable

# Performance regression testing
docker compose exec odoo odoo-bin --test-tags=performance --test-enable

# Integration testing
docker compose exec odoo odoo-bin --test-tags=integration,post_install --test-enable
```

#### **Development Environment Management (Docker)**
```bash
# Clean development environment setup
docker compose exec db dropdb -U odoo odoo_tdd_test && docker compose exec db createdb -U odoo odoo_tdd_test
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -i base --stop-after-init

# Module development cycle
docker compose exec odoo odoo-bin -c /etc/odoo/odoo.conf -d odoo_tdd_test -i target_module --test-enable --stop-after-init

# Production readiness validation
docker compose exec odoo odoo-bin --test-tags=post_install,security,performance --test-enable
```

## Code Architecture Details

### Database Schema
- **Performance Focus**: Recent architectural improvements include indexed `llm_role` field for 10x faster message queries
- **Locking Mechanism**: PostgreSQL advisory locking prevents concurrent generation issues
- **Migration Support**: Comprehensive migration scripts in `migrations/16.0.x.x.x/` directories

### Core Models
- **LLM Provider** (`llm.provider`): API configuration and authentication
- **LLM Model** (`llm.model`): Model definitions and capabilities
- **LLM Thread** (`llm.thread`): Conversation management
- **LLM Assistant** (`llm.assistant`): AI assistant configuration with prompt templates
- **LLM Tool** (`llm.tool`): Tool definitions and execution framework

### Frontend Components
- **JavaScript Architecture**: Located in `static/src/` directories
- **Owl Framework**: Uses Odoo's Owl framework for reactive components
- **Chat Interface**: Real-time streaming with WebSocket support
- **Form Generation**: Dynamic form creation based on model schemas

### API Patterns
- **Unified Generation**: `generate()` method provides consistent interface for all content types
- **Tool Execution**: Structured JSON schema validation for tool calls
- **Provider Abstraction**: Standardized methods across all LLM providers

## Testing Framework

The project uses **Odoo's built-in testing framework** following **strict TDD methodology**:

### Test Architecture and Standards

**Base Test Classes:**
- **TransactionCase**: Primary test class for unit and integration tests
- **HttpCase**: For testing HTTP endpoints and JavaScript components
- **SingleTransactionCase**: For tests requiring single transaction isolation

**Test Organization:**
```
module_name/
├── tests/
│   ├── __init__.py          # Import all test modules
│   ├── test_models.py       # Model functionality tests
│   ├── test_api.py          # API and integration tests
│   ├── test_security.py     # Access control tests
│   └── test_performance.py  # Performance and query optimization tests
```

### TDD Testing Standards

#### **1. Test Naming and Structure**
```python
from odoo.tests.common import TransactionCase
from odoo.tests import tagged

@tagged('post_install', '-at_install')
class TestLLMAssistant(TransactionCase):
    """
    Test LLM Assistant functionality following TDD principles.
    Tests run after all modules are installed for integration testing.
    """
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Efficient test data creation at class level
        cls.assistant = cls.env['llm.assistant'].create({
            'name': 'Test Assistant',
            'prompt_template': 'You are a helpful assistant.',
        })
    
    def test_prompt_generation_fails_without_template(self):
        """Red Phase: Test that prompt generation requires template"""
        assistant = self.env['llm.assistant'].create({'name': 'Empty Assistant'})
        with self.assertRaises(UserError, msg="Should require prompt template"):
            assistant.generate_prompt({})
    
    def test_prompt_generation_with_valid_template(self):
        """Green Phase: Test successful prompt generation"""
        result = self.assistant.generate_prompt({'user_input': 'Hello'})
        self.assertIsInstance(result, str)
        self.assertIn('helpful assistant', result.lower())
```

#### **2. Test Execution Commands (TDD Cycle with Docker)**
```bash
# Red Phase: Run failing test
docker compose exec odoo odoo-bin --test-tags=/llm_assistant:TestLLMAssistant.test_prompt_generation_fails_without_template

# Green Phase: Run all tests for module after minimal implementation
docker compose exec odoo odoo-bin --test-tags=/llm_assistant --test-enable --stop-after-init

# Refactor Phase: Run comprehensive test suite
docker compose exec odoo odoo-bin --test-tags=standard,post_install --test-enable

# Performance validation during refactor
docker compose exec odoo odoo-bin --test-tags=/llm_assistant:TestLLMPerformance --test-enable
```

#### **3. Advanced Test Patterns**

**Performance Testing with Query Count Assertions:**
```python
class TestLLMPerformance(TransactionCase):
    
    def test_thread_message_query_optimization(self):
        """Ensure indexed llm_role field provides optimal performance"""
        # Create test data
        thread = self.env['llm.thread'].create({'name': 'Test Thread'})
        for i in range(100):
            self.env['llm.thread.message'].create({
                'thread_id': thread.id,
                'content': f'Message {i}',
                'llm_role': 'user' if i % 2 else 'assistant',
            })
        
        # Test optimized query performance
        with self.assertQueryCount(2):  # Maximum 2 queries for indexed search
            user_messages = self.env['llm.thread.message'].search([
                ('thread_id', '=', thread.id),
                ('llm_role', '=', 'user')
            ])
            self.assertEqual(len(user_messages), 50)
```

**Security and Access Control Testing:**
```python
def test_api_key_access_security(self):
    """Ensure API keys are protected from unauthorized access"""
    provider = self.env['llm.provider'].create({
        'name': 'Secure Provider',
        'api_key': 'secret-key-123'
    })
    
    # Create demo user
    demo_user = self.env['res.users'].create({
        'name': 'Demo User',
        'login': 'demo@test.com',
        'groups_id': [(6, 0, [self.env.ref('base.group_user').id])],
    })
    
    # Test access restrictions
    with self.assertRaises(AccessError):
        provider.with_user(demo_user).read(['api_key'])
    
    # Test field visibility in forms
    provider_form = self.env['llm.provider'].with_user(demo_user).create({
        'name': 'Demo Provider'
    })
    self.assertFalse(hasattr(provider_form, 'api_key'))
```

**Integration Testing Across Modules:**
```python
@tagged('post_install')  # Run after all modules are installed
class TestLLMIntegration(TransactionCase):
    
    def test_end_to_end_conversation_flow(self):
        """Test complete conversation flow across multiple modules"""
        # Setup: Create provider, assistant, and thread
        provider = self.env['llm.provider'].create({
            'name': 'Integration Test Provider',
            'provider_type': 'openai',
            'api_key': 'test-key',
        })
        
        assistant = self.env['llm.assistant'].create({
            'name': 'Integration Assistant',
            'provider_id': provider.id,
            'prompt_template': 'You are a helpful assistant.',
        })
        
        thread = self.env['llm.thread'].create({
            'name': 'Integration Test Thread',
            'assistant_id': assistant.id,
        })
        
        # Test: Complete conversation cycle
        response = thread.send_message('Hello, how are you?')
        
        # Verify: All components work together
        self.assertIsInstance(response, str)
        self.assertTrue(len(response) > 0)
        
        # Verify message history
        messages = thread.message_ids
        self.assertEqual(len(messages), 2)  # User + Assistant message
        self.assertEqual(messages[0].llm_role, 'user')
        self.assertEqual(messages[1].llm_role, 'assistant')
```

### Current Test Coverage

**Modules with Comprehensive Test Coverage:**
- `llm`: Core provider and model functionality
- `llm_assistant`: Prompt template and assistant logic
- `llm_thread`: Conversation management and PostgreSQL locking
- `llm_tool`: Tool execution framework and JSON schema validation

**Test Categories:**
- **Unit Tests**: Individual method and function testing
- **Integration Tests**: Cross-module functionality
- **Performance Tests**: Query optimization and response time
- **Security Tests**: Access control and data protection
- **API Tests**: HTTP endpoints and JSON-RPC interfaces

**Interactive Testing Tools:**
- Test wizard: `llm_assistant/wizards/llm_prompt_test.py`
- Performance profiling: Built-in `assertQueryCount` integration
- Security validation: Access control test patterns

## Development Notes

### Recent Architectural Changes (16.0-pr)
- **Consolidated Architecture**: Merged `llm_prompt` into `llm_assistant` for streamlined management
- **Performance Optimization**: Added indexed `llm_role` field for faster queries
- **Unified Generation API**: New `generate()` method for consistent content generation
- **Enhanced Tool System**: Improved error handling and structured data storage

### Security Considerations
- **API Key Management**: Secure storage of provider credentials
- **Role-Based Access**: Permission-based tool access control
- **Input Validation**: JSON schema validation for all inputs

### Dependencies
- Standard Odoo dependencies: `mail`, `web`
- External Python packages defined in `requirements.txt`
- Provider-specific SDKs: `openai`, `anthropic`, `ollama`, etc.

## Common Development Tasks

### Adding New Provider
1. Create new module following pattern: `llm_provider_name/`
2. Implement provider class inheriting from base provider
3. Add provider configuration in `data/llm_publisher.xml`
4. Implement required methods: `_generate_completion()`, `_generate_embeddings()`

### Creating New Tool
1. Define tool class in `llm_tool/models/`
2. Implement `_execute()` method with proper error handling
3. Define JSON schema for tool parameters
4. Add tool configuration in `data/llm_tool_data.xml`

### Extending Assistant Capabilities
1. Add prompt templates in `llm_assistant/data/llm_prompt_data.xml`
2. Configure assistant in `llm_assistant/data/llm_assistant_data.xml`
3. Test using wizard at `llm_assistant/wizards/llm_prompt_test.py`

## Odoo 16→18 Migration Standards

### Unified JavaScript and XML Upgrade Guidelines

This section provides comprehensive standards for upgrading JavaScript and XML files from Odoo 16 to Odoo 18, incorporating automated analysis using Context7 MCP and Playwright MCP tools.

#### Migration Methodology Framework

**Phase 1: Pre-Migration Analysis**
- [ ] Inventory all JavaScript and XML files requiring upgrade
- [ ] Extract import statements from each JavaScript file
- [ ] Use Context7 MCP to research Odoo 16→18 API changes for each import
- [ ] Use Playwright MCP to verify actual implementation differences
- [ ] Create migration mapping for each file

**Phase 2: Import-Based Analysis Protocol**

For each JavaScript file (`.js`):
1. **Extract Import Dependencies**:
   ```bash
   # Extract all import statements
   grep -n "^import\|from ['\"]@" file.js
   ```

2. **MCP-Powered Research**:
   ```bash
   # Context7 MCP analysis
   context7-mcp get-library-docs --library="/odoo/documentation" --topic="javascript-framework-16-vs-18"
   
   # Playwright MCP verification
   playwright-mcp navigate "https://github.com/odoo/odoo/compare/16.0...18.0" --filter="*.js"
   ```

3. **Component Analysis**:
   - Check component definition patterns
   - Verify service injection methods
   - Validate lifecycle hook usage
   - Confirm router service API changes

#### JavaScript Migration Standards

**1. Module Declaration Removal**
```javascript
// Odoo 16 (REMOVE)
/** @odoo-module **/

// Odoo 18 (KEEP EMPTY)
// No module declaration needed
```

**2. Component Definition Updates**
```javascript
// Odoo 16 Pattern
export class MyComponent extends Component {
    static template = "my.template";
    static components = { SubComponent };
}
MyComponent.template = "my.template";
MyComponent.components = { SubComponent };

// Odoo 18 Pattern (Preferred)
export class MyComponent extends Component {
    static template = "my.template";
    static components = { SubComponent };
    static props = ["*"];
}
```

**3. Service Injection Patterns**
```javascript
// Odoo 16
import { useService } from "@web/core/utils/hooks";

setup() {
    this.router = useService("router");
}

// Odoo 18 (Updated API)
import { useService } from "@web/core/utils/hooks";

setup() {
    this.router = useService("router");
    // Note: Router API may have changed - verify with MCP
}
```

**4. Router Service API Updates**
```javascript
// Odoo 16
this.router.current.hash

// Odoo 18 (Verify with MCP)
this.router.current  // API structure may differ
```

#### XML Migration Standards

**1. Template Inheritance Patterns**
```xml
<!-- Odoo 16 & 18 Compatible -->
<templates id="template" xml:space="preserve">
    <t t-name="my.template" t-inherit="parent.template" t-inherit-mode="extension">
        <xpath expr="//div[@class='content']" position="inside">
            <!-- Content -->
        </xpath>
    </t>
</templates>
```

**2. Component Integration**
```xml
<!-- Verify component names with MCP research -->
<t t-component="ComponentName" t-props="componentProps"/>
```

#### Automated MCP Analysis Workflow

**Step 1: File Inventory Script**
```python
import os
import re

def extract_js_imports(file_path):
    """Extract all import statements from JavaScript file"""
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Extract import statements
    import_pattern = r'^import\s+.*?from\s+[\'"]([^\'"]+)[\'"]'
    imports = re.findall(import_pattern, content, re.MULTILINE)
    
    return imports

def analyze_file_dependencies(file_path):
    """Analyze file dependencies for migration"""
    imports = extract_js_imports(file_path)
    
    # Categorize imports for MCP research
    odoo_imports = [imp for imp in imports if imp.startswith('@')]
    external_imports = [imp for imp in imports if not imp.startswith('@')]
    
    return {
        'file': file_path,
        'odoo_imports': odoo_imports,
        'external_imports': external_imports,
        'migration_priority': 'high' if odoo_imports else 'low'
    }
```

**Step 2: MCP Research Commands**
```bash
# For each Odoo import, research API changes
for import in odoo_imports:
    echo "Researching: $import"
    
    # Context7 MCP research
    context7-mcp get-library-docs \
        --library="/odoo/documentation" \
        --topic="$import-16-vs-18-changes"
    
    # Playwright MCP verification
    playwright-mcp navigate \
        "https://github.com/odoo/odoo/blob/16.0/addons/web/static/src/${import}" \
        --compare-with="https://github.com/odoo/odoo/blob/18.0/addons/web/static/src/${import}"
done
```

**Step 3: Migration Execution Template**
```python
def migrate_javascript_file(file_path, migration_rules):
    """Apply migration rules to JavaScript file"""
    
    # Read original file
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Apply migration rules
    for rule in migration_rules:
        if rule['type'] == 'remove_module_declaration':
            content = re.sub(r'/\*\* @odoo-module \*\*/\n?', '', content)
        
        elif rule['type'] == 'update_import':
            old_import = rule['old']
            new_import = rule['new']
            content = content.replace(old_import, new_import)
        
        elif rule['type'] == 'update_api_call':
            # Apply API-specific updates based on MCP research
            content = apply_api_updates(content, rule)
    
    # Write migrated file
    with open(file_path, 'w') as f:
        f.write(content)
    
    return True
```

#### Migration Validation Framework

**1. Syntax Validation**
```bash
# JavaScript syntax check
node -c migrated_file.js

# XML validation
xmllint --noout migrated_template.xml
```

**2. Component Integration Testing**
```python
def test_component_integration(component_path):
    """Test component integration after migration"""
    
    # Load component in test environment
    # Verify template rendering
    # Check service injection
    # Validate event handling
    
    return test_results
```

**3. MCP-Assisted Verification**
```bash
# Final verification using Playwright MCP
playwright-mcp test-component \
    --component="MyComponent" \
    --odoo-version="18.0" \
    --verify-functionality
```

#### File-by-File Migration Checklist

For each file requiring migration:

**JavaScript Files:**
- [ ] Remove `/** @odoo-module **/` declarations
- [ ] Research each `@web/*`, `@mail/*` import with Context7 MCP
- [ ] Verify API changes with Playwright MCP
- [ ] Update component definition patterns
- [ ] Migrate service injection calls
- [ ] Update router service usage
- [ ] Test component functionality
- [ ] Validate syntax and integration

**XML Files:**
- [ ] Verify template inheritance patterns
- [ ] Check component name changes with MCP
- [ ] Update XPath expressions if needed
- [ ] Validate XML syntax
- [ ] Test template rendering

**Documentation Updates:**
- [ ] Update component documentation
- [ ] Record migration decisions
- [ ] Update dependency lists
- [ ] Note any manual interventions required

This migration framework ensures systematic, MCP-assisted upgrades with comprehensive verification at each step.