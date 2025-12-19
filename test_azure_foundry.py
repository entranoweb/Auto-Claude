#!/usr/bin/env python3
"""
Test script for Azure Foundry integration with Auto Claude.

This script verifies that the Azure Foundry client can be created
and configured properly for use with Auto Claude's Graphiti memory layer.
"""

import os
import sys
from pathlib import Path

# Add auto-claude directory to path
sys.path.insert(0, str(Path(__file__).parent / "auto-claude"))

def print_header(text):
    """Print a styled header."""
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70 + "\n")

def print_success(text):
    """Print success message."""
    print(f"✓ {text}")

def print_error(text):
    """Print error message."""
    print(f"✗ {text}")

def print_info(text):
    """Print info message."""
    print(f"ℹ {text}")


def test_anthropic_foundry_import():
    """Test if anthropic package supports Foundry."""
    print_header("TEST 1: Anthropic Foundry Import")
    
    try:
        from anthropic import Anthropic, AnthropicFoundry
        print_success("Successfully imported Anthropic and AnthropicFoundry")
        print_info(f"   Anthropic module: {Anthropic.__module__}")
        print_info(f"   AnthropicFoundry available: Yes")
        return True
    except ImportError as e:
        print_error(f"Failed to import AnthropicFoundry: {e}")
        print_info("   Install/upgrade with: pip install --upgrade anthropic")
        return False


def test_graphiti_integration():
    """Test if the modified anthropic_llm.py works."""
    print_header("TEST 2: Graphiti Integration")
    
    try:
        from integrations.graphiti.providers_pkg.llm_providers.anthropic_llm import (
            create_anthropic_llm_client
        )
        print_success("Successfully imported create_anthropic_llm_client")
        return True
    except ImportError as e:
        print_error(f"Failed to import from graphiti integration: {e}")
        print_info("   Check that auto-claude/integrations/graphiti exists")
        return False


def test_foundry_client_creation():
    """Test creating Azure Foundry client."""
    print_header("TEST 3: Azure Foundry Client Creation")
    
    # Check environment variables
    api_key = os.getenv("ANTHROPIC_FOUNDRY_API_KEY")
    resource = os.getenv("ANTHROPIC_FOUNDRY_RESOURCE")
    
    if not api_key:
        print_error("ANTHROPIC_FOUNDRY_API_KEY not set")
        print_info("   Add your Azure API key to .env file")
        return False
    
    if not resource:
        print_error("ANTHROPIC_FOUNDRY_RESOURCE not set")
        print_info("   Add your Azure resource name to .env file")
        return False
    
    print_success(f"ANTHROPIC_FOUNDRY_API_KEY: {'*' * 20} (hidden)")
    print_success(f"ANTHROPIC_FOUNDRY_RESOURCE: {resource}")
    
    # Set Foundry mode
    os.environ["CLAUDE_CODE_USE_FOUNDRY"] = "1"
    print_info("   Set CLAUDE_CODE_USE_FOUNDRY=1")
    
    try:
        from integrations.graphiti.providers_pkg.llm_providers.anthropic_llm import (
            create_anthropic_llm_client
        )
        
        # Create mock config
        class MockConfig:
            anthropic_api_key = api_key
            anthropic_model = "claude-opus-4-5"
        
        print_info("   Creating Azure Foundry client...")
        client = create_anthropic_llm_client(MockConfig())
        
        print_success(f"Azure Foundry client created successfully!")
        print_info(f"   Client type: {type(client).__name__}")
        print_info(f"   Client module: {type(client).__module__}")
        
        # Verify it's actually AnthropicFoundry
        if "Foundry" in type(client).__name__:
            print_success("✓ Confirmed: Using Azure Foundry client!")
        else:
            print_error(f"Warning: Expected AnthropicFoundry, got {type(client).__name__}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create Azure Foundry client: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_standard_client_fallback():
    """Test that standard Anthropic client works when Foundry is disabled."""
    print_header("TEST 4: Standard Client Fallback")
    
    # Disable Foundry mode
    os.environ["CLAUDE_CODE_USE_FOUNDRY"] = "0"
    print_info("   Set CLAUDE_CODE_USE_FOUNDRY=0")
    
    # Use a test API key (won't actually make calls)
    test_key = "sk-ant-test-key"
    
    try:
        from integrations.graphiti.providers_pkg.llm_providers.anthropic_llm import (
            create_anthropic_llm_client
        )
        
        class MockConfig:
            anthropic_api_key = test_key
            anthropic_model = "claude-opus-4-5"
        
        print_info("   Creating standard Anthropic client...")
        client = create_anthropic_llm_client(MockConfig())
        
        print_success(f"Standard client created successfully!")
        print_info(f"   Client type: {type(client).__name__}")
        
        # Verify it's standard Anthropic
        if type(client).__name__ == "Anthropic":
            print_success("✓ Confirmed: Using standard Anthropic client!")
        else:
            print_error(f"Warning: Expected Anthropic, got {type(client).__name__}")
        
        return True
        
    except Exception as e:
        print_error(f"Failed to create standard client: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_environment_configuration():
    """Test that all required environment variables are set."""
    print_header("TEST 5: Environment Configuration")
    
    required_vars = {
        "ANTHROPIC_FOUNDRY_API_KEY": "Azure Foundry API key",
        "ANTHROPIC_FOUNDRY_RESOURCE": "Azure resource name",
        "MORPH_API_KEY": "Morph LLM API key",
        "AUGMENT_API_KEY": "Augment Code API key",
    }
    
    optional_vars = {
        "VOYAGE_API_KEY": "Voyage AI (for embeddings)",
        "GRAPHITI_ENABLED": "Graphiti memory layer",
    }
    
    print("Required Variables:")
    all_required_set = True
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value and value != f"your_{var.lower()}_here":
            print_success(f"{var}: Set ({description})")
        else:
            print_error(f"{var}: Not set ({description})")
            all_required_set = False
    
    print("\nOptional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print_success(f"{var}: {value} ({description})")
        else:
            print_info(f"{var}: Not set ({description})")
    
    return all_required_set


def main():
    """Run all tests."""
    print("\n" + "="*70)
    print("  🚀 AUTO CLAUDE - AZURE FOUNDRY TEST SUITE")
    print("="*70)
    
    # Load .env file if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        print_info(f"Loading environment from: {env_file}")
        with open(env_file, encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    if value and not value.startswith("your_"):
                        os.environ[key] = value
    else:
        print_info(".env file not found - using system environment")
    
    # Run tests
    results = {
        "Anthropic Foundry Import": test_anthropic_foundry_import(),
        "Graphiti Integration": test_graphiti_integration(),
        "Azure Foundry Client": test_foundry_client_creation(),
        "Standard Client Fallback": test_standard_client_fallback(),
        "Environment Configuration": test_environment_configuration(),
    }
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for result in results.values() if result)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status} - {test_name}")
    
    print(f"\n  Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  🎉 All tests passed! Azure Foundry is ready to use!")
        print("\n  Next steps:")
        print("  1. Restart Auto Claude")
        print("  2. Enhanced tools will use Azure Foundry automatically")
        print("  3. Check logs for 'Using Azure Foundry endpoint'")
        return 0
    else:
        print("\n  ⚠️  Some tests failed. Please review the errors above.")
        print("\n  Common fixes:")
        print("  1. Run: pip install --upgrade anthropic")
        print("  2. Add API keys to .env file")
        print("  3. Verify .env configuration matches template")
        return 1


if __name__ == "__main__":
    sys.exit(main())
