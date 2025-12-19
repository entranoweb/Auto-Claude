#!/usr/bin/env python3
"""
Live Azure Foundry API Test - Makes actual API call
"""

import os
import sys
from pathlib import Path

# Load .env
env_file = Path(__file__).parent / ".env"
if env_file.exists():
    with open(env_file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, value = line.split("=", 1)
                if value and not value.startswith("your_"):
                    os.environ[key] = value

print("\n" + "="*70)
print("  🔥 LIVE AZURE FOUNDRY API TEST")
print("="*70 + "\n")

# Get credentials
api_key = os.getenv("ANTHROPIC_FOUNDRY_API_KEY")
resource = os.getenv("ANTHROPIC_FOUNDRY_RESOURCE")

if not api_key:
    print("❌ ANTHROPIC_FOUNDRY_API_KEY not set!")
    sys.exit(1)

if not resource:
    print("❌ ANTHROPIC_FOUNDRY_RESOURCE not set!")
    sys.exit(1)

print(f"✓ API Key: {'*' * 20} (found)")
print(f"✓ Resource: {resource}")

# Set Foundry mode
os.environ["CLAUDE_CODE_USE_FOUNDRY"] = "1"

print("\n" + "="*70)
print("  🚀 MAKING LIVE API CALL TO AZURE FOUNDRY")
print("="*70 + "\n")

try:
    from anthropic import AnthropicFoundry
    
    print("✓ AnthropicFoundry imported successfully")
    
    # Create client
    client = AnthropicFoundry(
        api_key=api_key,
        resource=resource
    )
    
    print(f"✓ Client created: {type(client).__name__}")
    print(f"✓ Using resource: {resource}")
    
    # Make actual API call
    print("\n🔄 Making API request...")
    print("   Prompt: 'Hello! Please respond with: Azure Foundry is working!'")
    
    # Try with the model from .env
    model = os.getenv("AUTO_BUILD_MODEL", "claude-opus-4-5")
    print(f"   Using model: {model}")
    
    response = client.messages.create(
        model=model,
        max_tokens=100,
        messages=[
            {
                "role": "user",
                "content": "Hello! Please respond with exactly: 'Azure Foundry is working!'"
            }
        ]
    )
    
    print("\n" + "="*70)
    print("  🎉 API CALL SUCCESSFUL!")
    print("="*70 + "\n")
    
    print(f"Model: {response.model}")
    print(f"Response ID: {response.id}")
    print(f"Stop Reason: {response.stop_reason}")
    
    # Extract text content
    content = response.content[0].text if response.content else "No content"
    
    print(f"\n📝 Response from Claude:")
    print("─" * 70)
    print(content)
    print("─" * 70)
    
    print(f"\n📊 Token Usage:")
    print(f"   Input tokens: {response.usage.input_tokens}")
    print(f"   Output tokens: {response.usage.output_tokens}")
    
    print("\n" + "="*70)
    print("  ✅ AZURE FOUNDRY IS WORKING PERFECTLY!")
    print("="*70 + "\n")
    
    print("🎯 Integration Status: VERIFIED")
    print("🚀 Ready for Auto-Claude deployment!")
    
except Exception as e:
    print("\n" + "="*70)
    print("  ❌ API CALL FAILED")
    print("="*70 + "\n")
    print(f"Error: {e}")
    print("\nPossible issues:")
    print("  1. Check API key is correct")
    print("  2. Check resource name is correct")
    print("  3. Check Azure Foundry deployment is active")
    print("  4. Check network connectivity")
    import traceback
    traceback.print_exc()
    sys.exit(1)
