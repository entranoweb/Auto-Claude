"""
Anthropic LLM Provider
======================

Anthropic LLM client implementation for Graphiti.
"""

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from graphiti_config import GraphitiConfig

from ..exceptions import ProviderError, ProviderNotInstalled


def create_anthropic_llm_client(config: "GraphitiConfig") -> Any:
    """
    Create Anthropic LLM client with optional Azure Foundry support.

    Args:
        config: GraphitiConfig with Anthropic settings

    Returns:
        Anthropic LLM client instance (standard or Azure Foundry)

    Raises:
        ProviderNotInstalled: If anthropic package is not installed
        ProviderError: If API key is missing or Foundry config incomplete
    """
    import os
    
    if not config.anthropic_api_key:
        raise ProviderError("ANTHROPIC_API_KEY required")
    
    # Check if Azure Foundry should be used
    use_foundry = os.environ.get("CLAUDE_CODE_USE_FOUNDRY") == "1"
    
    if use_foundry:
        try:
            from anthropic import AnthropicFoundry
        except ImportError as e:
            raise ProviderNotInstalled(
                f"Azure Foundry requires anthropic package. "
                f"Install with: pip install anthropic\n"
                f"Error: {e}"
            )
        
        resource = os.environ.get("ANTHROPIC_FOUNDRY_RESOURCE")
        base_url = os.environ.get("ANTHROPIC_FOUNDRY_BASE_URL")
        
        if resource:
            return AnthropicFoundry(api_key=config.anthropic_api_key, resource=resource)
        elif base_url:
            return AnthropicFoundry(api_key=config.anthropic_api_key, base_url=base_url)
        else:
            raise ProviderError("ANTHROPIC_FOUNDRY_RESOURCE or ANTHROPIC_FOUNDRY_BASE_URL required when CLAUDE_CODE_USE_FOUNDRY=1")
    else:
        # Standard Anthropic client
        try:
            from anthropic import Anthropic
        except ImportError as e:
            raise ProviderNotInstalled(
                f"Anthropic provider requires anthropic package. "
                f"Install with: pip install anthropic\n"
                f"Error: {e}"
            )
        
        return Anthropic(api_key=config.anthropic_api_key)
