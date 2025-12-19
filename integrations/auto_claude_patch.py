"""
Auto Claude Integration Patch
==============================

Adds enhanced tools (Morph + Augment) to Auto Claude agents.

Instructions:
1. Copy this file to: auto-claude/integrations/
2. Update auto-claude/agents/coder.py to import and use enhanced tools
3. Restart Auto Claude

This patch adds:
- edit_file_fast (Morph Fast Apply) - 10,500 tok/s editing
- warpgrep_search (Morph Warp Grep) - AI-powered search
- augment_get_context (Augment) - Smart context retrieval
- augment_generate (Augment) - Context-aware generation
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


def patch_auto_claude_tools(
    existing_tools: List[str],
    project_dir: Path
) -> List[str]:
    """
    Add enhanced tools to Auto Claude's tool list.
    
    Args:
        existing_tools: Current tool list
        project_dir: Project root directory
        
    Returns:
        Enhanced tool list with Morph and Augment tools
    """
    enhanced_tools = list(existing_tools)
    
    # Check if enhanced tools are available
    has_morph = bool(os.getenv("MORPH_API_KEY"))
    has_augment = bool(os.getenv("AUGMENT_API_KEY"))
    
    if has_morph:
        # Add Morph tools
        if "edit_file_fast" not in enhanced_tools:
            enhanced_tools.append("edit_file_fast")
            logger.info("✓ Added Morph Fast Apply tool")
        
        if "warpgrep_search" not in enhanced_tools:
            enhanced_tools.append("warpgrep_search")
            logger.info("✓ Added Morph Warp Grep tool")
    
    if has_augment:
        # Add Augment tools
        if "augment_get_context" not in enhanced_tools:
            enhanced_tools.append("augment_get_context")
            logger.info("✓ Added Augment Context tool")
        
        if "augment_generate" not in enhanced_tools:
            enhanced_tools.append("augment_generate")
            logger.info("✓ Added Augment Generate tool")
    
    return enhanced_tools


# Example integration for Auto Claude's coder agent
CODER_SYSTEM_PROMPT_ADDITION = """
ENHANCED TOOLS AVAILABLE:

You have access to powerful enhanced tools that make coding faster and more accurate:

1. edit_file_fast (Morph Fast Apply)
   - Use this instead of str_replace or rewriting full files
   - 60x faster, 98% accurate
   - Use // ... existing code ... markers
   - Example: edit_file_fast("src/auth.ts", "Add null check", "// ... existing code ...\\nif (!user) throw Error();\\n// ... existing code ...")

2. warpgrep_search (Morph Warp Grep)
   - Use this FIRST before manually reading files
   - AI-powered semantic search
   - 4x faster than regular grep
   - Example: warpgrep_search("Find authentication middleware")

3. augment_get_context (Augment Context)
   - Get smart context about the codebase
   - Better than manual file exploration
   - Example: augment_get_context("How do we handle user sessions?")

4. augment_generate (Augment Code Generation)
   - Generate code with full project context
   - Follows project patterns and conventions
   - Example: augment_generate("Add rate limiting to API endpoints")

WORKFLOW BEST PRACTICES:

When starting a new task:
1. Use warpgrep_search or augment_get_context to understand the codebase
2. Use edit_file_fast for all file edits (it's much faster and more accurate)
3. Use augment_generate for complex new features that need project context

Remember: These tools are optimized for speed and accuracy. Use them instead of manual approaches.
"""


# Configuration for Auto Claude's ClaudeAgentOptions
def get_enhanced_agent_config(project_dir: Path) -> Dict:
    """
    Get enhanced configuration for ClaudeAgentOptions.
    
    Args:
        project_dir: Project root directory
        
    Returns:
        Configuration dict with enhanced tools
    """
    from integrations.enhanced_tools import get_enhanced_tools
    
    # Get all enhanced tool definitions
    enhanced_tools = get_enhanced_tools(project_dir)
    
    # Convert to tool names list for allowed_tools
    tool_names = [tool["name"] for tool in enhanced_tools]
    
    return {
        "enhanced_tools": enhanced_tools,
        "tool_names": tool_names,
        "system_prompt_addition": CODER_SYSTEM_PROMPT_ADDITION
    }


# Example: How to modify Auto Claude's coder agent
"""
In auto-claude/agents/coder.py, add this at the top:

from integrations.auto_claude_patch import get_enhanced_agent_config

Then in create_coder_agent():

# Get enhanced tools
enhanced_config = get_enhanced_agent_config(project_dir)

# Update allowed_tools
allowed_tools = [
    "Read", "Write", "Bash",  # Standard tools
    *enhanced_config["tool_names"]  # Add enhanced tools
]

# Update system prompt
system_prompt = f'''
{ORIGINAL_CODER_PROMPT}

{enhanced_config["system_prompt_addition"]}
'''

# Create agent with enhanced tools
client = ClaudeSDKClient(
    options=ClaudeAgentOptions(
        model="claude-opus-4-5",
        system_prompt=system_prompt,
        allowed_tools=allowed_tools,
        custom_tools=enhanced_config["enhanced_tools"]
    )
)
"""


__all__ = [
    "patch_auto_claude_tools",
    "get_enhanced_agent_config",
    "CODER_SYSTEM_PROMPT_ADDITION"
]
