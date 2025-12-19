"""
Augment Code Integration for Auto Claude
=========================================

Better codebase context and understanding.

Usage:
    from integrations.augment import AugmentClient, create_augment_tools
    
    augment = AugmentClient(workspace_root="/path/to/project")
    
    # Get relevant context
    context = await augment.get_context(
        "How do we handle user authentication?"
    )
    
    # Generate code with context
    response = await augment.generate(
        "Add error handling to login function",
        model="sonnet4.5"
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


class AugmentClient:
    """Client for Augment Code context and generation."""
    
    def __init__(
        self,
        workspace_root: Optional[Path] = None,
        api_key: Optional[str] = None
    ):
        """
        Initialize Augment client.
        
        Args:
            workspace_root: Project root directory
            api_key: Augment API key (defaults to AUGMENT_API_KEY env var)
        """
        self.workspace_root = Path(workspace_root or os.getcwd())
        self.api_key = api_key or os.getenv("AUGMENT_API_KEY")
        
        if not self.api_key:
            raise ValueError(
                "AUGMENT_API_KEY required. Get one at https://augmentcode.com"
            )
        
        self._check_auggie_installed()
    
    async def get_context(
        self,
        query: str,
        max_files: int = 10,
        file_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get relevant codebase context using Augment's context engine.
        
        Args:
            query: What you're trying to understand or do
            max_files: Maximum files to return (default: 10)
            file_types: File extensions to focus on (e.g., [".ts", ".py"])
            
        Returns:
            {
                "success": bool,
                "contexts": [
                    {
                        "file": str,
                        "content": str,
                        "relevance": float,
                        "summary": str
                    }
                ],
                "error": str (optional)
            }
            
        Example:
            context = await augment.get_context(
                "How do we handle user authentication?",
                max_files=5
            )
        """
        logger.info(f"Augment Context: {query}")
        
        try:
            cmd = [
                "auggie",
                "context",
                "--query", query,
                "--max-files", str(max_files),
                "--format", "json"
            ]
            
            if file_types:
                cmd.extend(["--file-types", ",".join(file_types)])
            
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                cwd=str(self.workspace_root),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env={**os.environ, "AUGMENT_API_TOKEN": self.api_key}
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Augment context failed: {error_msg}")
                return {"success": False, "error": error_msg}
            
            result = json.loads(stdout.decode())
            logger.info(f"✓ Retrieved {len(result.get('contexts', []))} context files")
            
            return {"success": True, "contexts": result.get("contexts", [])}
            
        except FileNotFoundError:
            return {
                "success": False,
                "error": "auggie CLI not found. Run: npm install -g @augmentcode/auggie-cli"
            }
        except json.JSONDecodeError as e:
            return {"success": False, "error": f"Invalid JSON response: {e}"}
        except Exception as e:
            logger.exception("Augment context failed")
            return {"success": False, "error": str(e)}
    
    async def generate(
        self,
        prompt: str,
        model: str = "sonnet4.5",
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        Generate code using Augment with full codebase context.
        
        Args:
            prompt: What you want to create or modify
            model: Model to use (sonnet4.5, haiku4.5, gpt-5)
            stream: Whether to stream the response
            
        Returns:
            {
                "success": bool,
                "response": str,
                "files_modified": List[str],
                "error": str (optional)
            }
            
        Example:
            result = await augment.generate(
                "Add error handling to the login function",
                model="sonnet4.5"
            )
        """
        logger.info(f"Augment Generate: {prompt}")
        
        try:
            # Use Augment SDK via Node bridge
            bridge_script = Path(__file__).parent / "augment_bridge.js"
            self._ensure_bridge_script()
            
            proc = await asyncio.create_subprocess_exec(
                "node",
                str(bridge_script),
                "generate",
                json.dumps({
                    "prompt": prompt,
                    "model": model,
                    "workspaceRoot": str(self.workspace_root),
                    "stream": stream
                }),
                env={**os.environ, "AUGMENT_API_KEY": self.api_key},
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await proc.communicate()
            
            if proc.returncode != 0:
                error_msg = stderr.decode().strip()
                logger.error(f"Augment generate failed: {error_msg}")
                return {"success": False, "error": error_msg}
            
            result = json.loads(stdout.decode())
            logger.info("✓ Code generated successfully")
            
            return result
            
        except Exception as e:
            logger.exception("Augment generate failed")
            return {"success": False, "error": str(e)}
    
    def _check_auggie_installed(self):
        """Check if auggie CLI is installed."""
        try:
            result = subprocess.run(
                ["auggie", "--version"],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                logger.debug("✓ auggie CLI found")
                return True
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass
        
        logger.warning(
            "auggie CLI not found. Install with: npm install -g @augmentcode/auggie-cli"
        )
        return False
    
    def _ensure_bridge_script(self):
        """Create Node.js bridge script if it doesn't exist."""
        bridge_script = Path(__file__).parent / "augment_bridge.js"
        
        if bridge_script.exists():
            return
        
        logger.info("Creating Augment bridge script...")
        
        bridge_code = '''#!/usr/bin/env node
/**
 * Augment Bridge for Auto Claude
 * Allows Python to call Augment SDK
 */

const { Auggie } = require('@augmentcode/auggie-sdk');

const method = process.argv[2];
const params = JSON.parse(process.argv[3]);

(async () => {
  try {
    const client = await Auggie.create({
      apiKey: process.env.AUGMENT_API_KEY,
      workspaceRoot: params.workspaceRoot,
      model: params.model,
      allowIndexing: true
    });
    
    if (method === 'generate') {
      const response = await client.prompt(params.prompt, {
        isAnswerOnly: true
      });
      
      console.log(JSON.stringify({
        success: true,
        response: response
      }));
    }
    
    await client.close();
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


def create_augment_tools(project_dir: Path) -> List[Dict]:
    """
    Create Augment tool definitions for Claude Agent SDK.
    
    Args:
        project_dir: Project root directory
        
    Returns:
        List of tool definitions with execute functions
    """
    augment = AugmentClient(workspace_root=project_dir)
    
    def execute_get_context(params: Dict) -> Dict:
        """Execute Augment context retrieval."""
        return asyncio.run(
            augment.get_context(
                query=params["query"],
                max_files=params.get("max_files", 10),
                file_types=params.get("file_types")
            )
        )
    
    def execute_generate(params: Dict) -> Dict:
        """Execute Augment code generation."""
        return asyncio.run(
            augment.generate(
                prompt=params["prompt"],
                model=params.get("model", "sonnet4.5")
            )
        )
    
    return [
        {
            "name": "augment_get_context",
            "description": (
                "SMART CONTEXT RETRIEVAL - Get highly relevant codebase context.\n\n"
                "Augment analyzes your entire codebase to find the most relevant files "
                "and code sections for a given query. Better than manual file reading.\n\n"
                "Benefits:\n"
                "• Understands code relationships and dependencies\n"
                "• Ranks files by relevance\n"
                "• Provides summaries of each file\n"
                "• Faster than manual exploration\n\n"
                "Use this when you need to understand:\n"
                "• How a feature is implemented\n"
                "• Where to make changes\n"
                "• Code dependencies and relationships"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "What you're trying to understand (be specific)"
                    },
                    "max_files": {
                        "type": "integer",
                        "description": "Maximum files to return (default: 10)",
                        "default": 10
                    },
                    "file_types": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "File extensions to focus on (e.g., ['.ts', '.py'])"
                    }
                },
                "required": ["query"]
            },
            "execute": execute_get_context
        },
        {
            "name": "augment_generate",
            "description": (
                "CONTEXT-AWARE CODE GENERATION - Generate code with full project understanding.\n\n"
                "Uses Augment's deep codebase understanding to generate code that "
                "follows your project's patterns and conventions.\n\n"
                "Benefits:\n"
                "• Aware of entire codebase context\n"
                "• Follows existing patterns and style\n"
                "• Understands dependencies\n"
                "• Generates production-ready code\n\n"
                "Use this for:\n"
                "• Adding new features\n"
                "• Refactoring existing code\n"
                "• Fixing bugs with context"
            ),
            "input_schema": {
                "type": "object",
                "properties": {
                    "prompt": {
                        "type": "string",
                        "description": "What you want to create or modify"
                    },
                    "model": {
                        "type": "string",
                        "description": "Model to use (sonnet4.5, haiku4.5, gpt-5)",
                        "default": "sonnet4.5"
                    }
                },
                "required": ["prompt"]
            },
            "execute": execute_generate
        }
    ]


__all__ = ["AugmentClient", "create_augment_tools"]
