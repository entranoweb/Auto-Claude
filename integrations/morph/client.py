"""
Morph LLM Integration for Auto Claude
======================================

Fast Apply: 10,500 tokens/second code editing
Warp Grep: AI-powered semantic code search

Usage:
    from integrations.morph import MorphClient, create_morph_tools
    
    morph = MorphClient()
    
    # Fast Apply
    result = await morph.fast_apply(
        target_filepath="src/auth.ts",
        instructions="Add null check",
        code_edit='// ... existing code ...\\nif (!user) throw Error();\\n// ... existing code ...'
    )
    
    # Warp Grep
    result = await morph.warp_grep(
        query="Find authentication middleware",
        repo_root="."
    )
"""

import os
import asyncio
import subprocess
import json
import logging
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class MorphClient:
    """Client for Morph Fast Apply and Warp Grep."""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Morph client.
        
        Args:
            api_key: Morph API key (defaults to MORPH_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("MORPH_API_KEY")
        if not self.api_key:
            raise ValueError(
                "MORPH_API_KEY required. Get one at https://morphllm.com/dashboard"
            )
        
        self.bridge_dir = Path(__file__).parent
        self._ensure_bridge_script()
    
    async def fast_apply(
        self,
        target_filepath: str,
        instructions: str,
        code_edit: str,
        base_dir: str = "."
    ) -> Dict[str, Any]:
        """
        Apply code edits using Morph Fast Apply (10,500 tok/s).
        
        Args:
            target_filepath: Path to file to edit
            instructions: What you're changing and why
            code_edit: Code with // ... existing code ... markers
            base_dir: Base directory for file paths
            
        Returns:
            {
                "success": bool,
                "filepath": str,
                "changes": {"linesAdded": int, "linesRemoved": int, "linesModified": int},
                "udiff": str (optional),
                "error": str (optional)
            }
            
        Example:
            result = await morph.fast_apply(
                "src/auth.ts",
                "Add null check for user",
                '// ... existing code ...\\nif (!user) throw new Error("Not found");\\n// ... existing code ...'
            )
        """
        logger.info(f"Fast Apply: {target_filepath}")
        
        result = await self._call_morph_node(
            "fastApply",
            {
                "target_filepath": target_filepath,
                "instructions": instructions,
                "code_edit": code_edit,
                "base_dir": base_dir
            }
        )
        
        if result.get("success"):
            changes = result.get("changes", {})
            logger.info(
                f"✓ Applied: +{changes.get('linesAdded', 0)} "
                f"-{changes.get('linesRemoved', 0)} lines"
            )
        else:
            logger.error(f"✗ Fast Apply failed: {result.get('error')}")
        
        return result
    
    async def warp_grep(
        self,
        query: str,
        repo_root: str = ".",
        excludes: Optional[List[str]] = None,
        includes: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Search codebase using AI-powered Warp Grep.
        
        4x faster than regular grep, understands semantic meaning.
        
        Args:
            query: Natural language search query
            repo_root: Root directory to search
            excludes: Glob patterns to exclude
            includes: Glob patterns to include (optional)
            
        Returns:
            {
                "success": bool,
                "contexts": [{"file": str, "content": str}],
                "summary": str,
                "error": str (optional)
            }
            
        Example:
            result = await morph.warp_grep(
                "Find where we handle authentication",
                repo_root=".",
                excludes=["node_modules", ".git"]
            )
        """
        logger.info(f"Warp Grep: {query}")
        
        result = await self._call_morph_node(
            "warpGrep",
            {
                "query": query,
                "repoRoot": repo_root,
                "excludes": excludes or ["node_modules", ".git", "dist", "build"],
                "includes": includes
            }
        )
        
        if result.get("success"):
            contexts = result.get("contexts", [])
            logger.info(f"✓ Found {len(contexts)} relevant code sections")
        else:
            logger.error(f"✗ Warp Grep failed: {result.get('error')}")
        
        return result
    
    async def _call_morph_node(self, method: str, params: Dict) -> Dict:
        """Call Morph via Node.js bridge script."""
        bridge_script = self.bridge_dir / "morph_bridge.js"
        
        try:
            proc = await asyncio.create_subprocess_exec(
                "node",
                str(bridge_script),
                method,
                json.dumps(params),
                env={**os.environ, "MORPH_API_KEY": self.api_key},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=str(self.bridge_dir)
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Morph bridge error: {error_msg}")
                return {"success": False, "error": error_msg}
            
            return json.loads(stdout.decode())
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": "Node.js not found. Install from https://nodejs.org"
            }
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            logger.exception("Morph call failed")
            return {"success": False, "error": str(e)}
    
    def _ensure_bridge_script(self):
        """Create Node.js bridge script if it doesn't exist."""
        bridge_script = self.bridge_dir / "morph_bridge.js"
        
        if bridge_script.exists():
            return
        
        logger.info("Creating Morph bridge script...")
        
        bridge_code = '''#!/usr/bin/env node
/**
 * Morph Bridge for Auto Claude
 * Allows Python to call Morph SDK
 */

const { MorphClient } = require('@morphllm/morphsdk');

const method = process.argv[2];
const params = JSON.parse(process.argv[3]);

const morph = new MorphClient({ apiKey: process.env.MORPH_API_KEY });

(async () => {
  try {
    let result;
    
    if (method === 'fastApply') {
      result = await morph.fastApply.execute({
        target_filepath: params.target_filepath,
        instructions: params.instructions,
        code_edit: params.code_edit,
        baseDir: params.base_dir || '.'
      });
    } else if (method === 'warpGrep') {
      result = await morph.warpGrep.execute({
        query: params.query,
        repoRoot: params.repoRoot || '.',
        excludes: params.excludes,
        includes: params.includes
      });
    } else {
      throw new Error(`Unknown method: ${method}`);
    }
    
    console.log(JSON.stringify(result));
    process.exit(0);
    
  } catch (error) {
    console.error(JSON.stringify({ 
      success: false, 
      error: error.message,
      stack: error.stack
    }));
    process.exit(1);
  }
})();
'''
        bridge_script.write_text(bridge_code)
        bridge_script.chmod(0o755)
        
        logger.info(f"✓ Bridge script created: {bridge_script}")


def create_morph_tools(project_dir: Path) -> List[Dict]:
    """
    Create Morph tool definitions for Claude Agent SDK.
    
    Args:
        project_dir: Project root directory
        
    Returns:
        List of tool definitions with execute functions
    """
    morph = MorphClient()
    
    def execute_fast_apply(params: Dict) -> Dict:
        """Execute Fast Apply tool."""
        return asyncio.run(
            morph.fast_apply(
                target_filepath=params["target_filepath"],
                instructions=params["instructions"],
                code_edit=params["code_edit"],
                base_dir=str(project_dir)
            )
        )
    
    def execute_warp_grep(params: Dict) -> Dict:
        """Execute Warp Grep tool."""
        return asyncio.run(
            morph.warp_grep(
                query=params["query"],
                repo_root=str(project_dir),
                excludes=params.get("excludes"),
                includes=params.get("includes")
            )
        )
    
    return [
        {
            "name": "edit_file_fast",
            "description": (
                "FAST CODE EDITING (10,500 tok/s) - Use this instead of str_replace or full file writes.\n\n"
                "Edit code files using Morph Fast Apply with 98% accuracy. "
                "Use // ... existing code ... markers to show where changes go.\n\n"
                "Benefits:\n"
                "• 60x faster than rewriting full files\n"
                "• Automatic indentation correction\n"
                "• Fuzzy matching for code blocks\n"
                "• Works with partial snippets\n\n"
                "Example:\n"
                "// ... existing code ...\n"
                "if (!user) throw new Error('Not found');\n"
                "// ... existing code ..."
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "target_filepath": {
                        "type": "string",
                        "description": "Path to file to edit (relative to project root)"
                    },
                    "instructions": {
                        "type": "string",
                        "description": "Clear explanation of what you're changing and why"
                    },
                    "code_edit": {
                        "type": "string",
                        "description": (
                            "Code with // ... existing code ... markers showing where changes go. "
                            "Don't include the full file, just the changed section."
                        )
                    }
                },
                "required": ["target_filepath", "instructions", "code_edit"]
            },
            "execute": execute_fast_apply
        },
        {
            "name": "warpgrep_search",
            "description": (
                "FAST CODE SEARCH - Use this FIRST before reading files.\n\n"
                "AI-powered semantic code search with 4x faster results. "
                "Understands natural language queries and returns relevant code sections.\n\n"
                "Benefits:\n"
                "• 70% less context rot on long tasks\n"
                "• Parallel grep + file read operations\n"
                "• Semantic understanding of code intent\n"
                "• Returns exact line ranges\n\n"
                "Example queries:\n"
                "• 'Find authentication middleware'\n"
                "• 'Where do we handle rate limiting?'\n"
                "• 'Show me database connection setup'"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language search query (be specific about what you're looking for)"
                    },
                    "excludes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Glob patterns to exclude (default: node_modules, .git, dist)"
                    },
                    "includes": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Glob patterns to include (optional, includes all by default)"
                    }
                },
                "required": ["query"]
            },
            "execute": execute_warp_grep
        }
    ]


__all__ = ["MorphClient", "create_morph_tools"]
