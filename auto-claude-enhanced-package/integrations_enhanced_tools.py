"""
Enhanced Tools Integration for Auto Claude
===========================================

Combines Morph Fast Apply, Warp Grep, and Augment Context into a single interface.

Usage in Auto Claude:
    from integrations.enhanced_tools import get_enhanced_tools
    
    tools = get_enhanced_tools(project_dir=Path("/path/to/project"))
    
    # Tools are now available:
    # - edit_file_fast (Morph Fast Apply)
    # - warpgrep_search (Morph Warp Grep)
    # - augment_get_context (Augment Context)
    # - augment_generate (Augment Generation)
"""

import os
import logging
from typing import List, Dict, Optional
from pathlib import Path

from .morph.client import MorphClient, create_morph_tools
from .augment.client import AugmentClient, create_augment_tools

logger = logging.getLogger(__name__)


def get_enhanced_tools(
    project_dir: Path,
    enable_morph: bool = True,
    enable_augment: bool = True
) -> List[Dict]:
    """
    Get all enhanced tools for Auto Claude.
    
    Args:
        project_dir: Project root directory
        enable_morph: Enable Morph Fast Apply and Warp Grep (default: True)
        enable_augment: Enable Augment Context (default: True)
        
    Returns:
        List of tool definitions ready for Claude Agent SDK
        
    Example:
        tools = get_enhanced_tools(Path("/path/to/project"))
        # Use with ClaudeSDKClient(options=ClaudeAgentOptions(tools=tools))
    """
    all_tools = []
    
    # Check environment variables
    morph_enabled = enable_morph and bool(os.getenv("MORPH_API_KEY"))
    augment_enabled = enable_augment and bool(os.getenv("AUGMENT_API_KEY"))
    
    # Morph Tools
    if morph_enabled:
        try:
            morph_tools = create_morph_tools(project_dir)
            all_tools.extend(morph_tools)
            logger.info(f"✓ Morph tools loaded: {len(morph_tools)} tools")
        except Exception as e:
            logger.warning(f"Failed to load Morph tools: {e}")
    else:
        if enable_morph:
            logger.warning(
                "MORPH_API_KEY not set. Get one at https://morphllm.com/dashboard"
            )
    
    # Augment Tools
    if augment_enabled:
        try:
            augment_tools = create_augment_tools(project_dir)
            all_tools.extend(augment_tools)
            logger.info(f"✓ Augment tools loaded: {len(augment_tools)} tools")
        except Exception as e:
            logger.warning(f"Failed to load Augment tools: {e}")
    else:
        if enable_augment:
            logger.warning(
                "AUGMENT_API_KEY not set. Get one at https://augmentcode.com"
            )
    
    if not all_tools:
        logger.error(
            "No enhanced tools loaded. Set MORPH_API_KEY and/or AUGMENT_API_KEY"
        )
    else:
        logger.info(f"✓ Total enhanced tools loaded: {len(all_tools)}")
    
    return all_tools


def print_tools_summary():
    """Print summary of available enhanced tools."""
    print("\n" + "="*60)
    print("Enhanced Tools for Auto Claude")
    print("="*60)
    
    morph_key = os.getenv("MORPH_API_KEY")
    augment_key = os.getenv("AUGMENT_API_KEY")
    
    print("\nMorph LLM:")
    if morph_key:
        print("  ✓ API Key configured")
        print("  • edit_file_fast - 10,500 tok/s code editing")
        print("  • warpgrep_search - AI-powered code search")
    else:
        print("  ✗ API Key not set (MORPH_API_KEY)")
        print("    Get one at: https://morphllm.com/dashboard")
    
    print("\nAugment Code:")
    if augment_key:
        print("  ✓ API Key configured")
        print("  • augment_get_context - Smart context retrieval")
        print("  • augment_generate - Context-aware generation")
    else:
        print("  ✗ API Key not set (AUGMENT_API_KEY)")
        print("    Get one at: https://augmentcode.com")
    
    print("\n" + "="*60)
    
    if not morph_key and not augment_key:
        print("\n⚠️  No API keys configured. Enhanced tools disabled.")
        print("Add them to your .env file to enable.")
    
    print()


# Test function
async def test_enhanced_tools(project_dir: Path):
    """
    Test all enhanced tools.
    
    Args:
        project_dir: Project directory to test with
    """
    print("\n🧪 Testing Enhanced Tools...\n")
    
    # Test Morph
    if os.getenv("MORPH_API_KEY"):
        print("Testing Morph LLM...")
        try:
            from .morph.client import MorphClient
            morph = MorphClient()
            
            # Test Warp Grep
            print("  → Warp Grep: Searching for 'main function'")
            result = await morph.warp_grep(
                "Find the main function",
                repo_root=str(project_dir)
            )
            if result.get("success"):
                print(f"  ✓ Found {len(result.get('contexts', []))} results")
            else:
                print(f"  ✗ Failed: {result.get('error')}")
            
            print()
        except Exception as e:
            print(f"  ✗ Morph test failed: {e}\n")
    
    # Test Augment
    if os.getenv("AUGMENT_API_KEY"):
        print("Testing Augment Code...")
        try:
            from .augment.client import AugmentClient
            augment = AugmentClient(workspace_root=project_dir)
            
            # Test Context
            print("  → Context: Getting project overview")
            result = await augment.get_context(
                "What is the main purpose of this project?",
                max_files=3
            )
            if result.get("success"):
                print(f"  ✓ Retrieved {len(result.get('contexts', []))} context files")
            else:
                print(f"  ✗ Failed: {result.get('error')}")
            
            print()
        except Exception as e:
            print(f"  ✗ Augment test failed: {e}\n")
    
    print("✅ Testing complete!\n")


__all__ = [
    "get_enhanced_tools",
    "print_tools_summary",
    "test_enhanced_tools",
    "MorphClient",
    "AugmentClient"
]
