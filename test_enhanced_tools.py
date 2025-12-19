#!/usr/bin/env python3
"""
Test script for Auto Claude enhanced tools.

Tests Morph Fast Apply, Warp Grep, and Augment Context.
"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from integrations.enhanced_tools import (
    test_enhanced_tools,
    print_tools_summary,
    MorphClient,
    AugmentClient
)


async def quick_test():
    """Quick test of all enhanced tools."""
    print("\n" + "="*60)
    print("  Auto Claude Enhanced Tools Test")
    print("="*60)
    
    # Print configuration summary
    print_tools_summary()
    
    # Get current directory as test project
    project_dir = Path.cwd()
    print(f"Test Project: {project_dir}\n")
    
    # Run comprehensive tests
    await test_enhanced_tools(project_dir)
    
    print("="*60)
    print("\nIf all tests passed, you're ready to use Auto Claude!")
    print("\nNext steps:")
    print("1. Restart Auto Claude")
    print("2. Enhanced tools will be automatically available")
    print("3. Check the logs to see tools in action")
    print()


async def interactive_test():
    """Interactive test mode."""
    print("\n" + "="*60)
    print("  Interactive Enhanced Tools Test")
    print("="*60 + "\n")
    
    project_dir = Path.cwd()
    
    while True:
        print("\nChoose a test:")
        print("1. Test Morph Warp Grep (search)")
        print("2. Test Morph Fast Apply (edit)")
        print("3. Test Augment Context")
        print("4. Run all tests")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == "1":
            await test_warp_grep(project_dir)
        elif choice == "2":
            await test_fast_apply(project_dir)
        elif choice == "3":
            await test_augment_context(project_dir)
        elif choice == "4":
            await test_enhanced_tools(project_dir)
        elif choice == "5":
            print("\n👋 Goodbye!\n")
            break
        else:
            print("Invalid choice. Try again.")


async def test_warp_grep(project_dir: Path):
    """Test Warp Grep interactively."""
    try:
        morph = MorphClient()
        
        query = input("\nEnter search query: ").strip()
        if not query:
            print("Query cannot be empty")
            return
        
        print(f"\n🔍 Searching for: {query}")
        result = await morph.warp_grep(query, repo_root=str(project_dir))
        
        if result.get("success"):
            contexts = result.get("contexts", [])
            print(f"\n✓ Found {len(contexts)} relevant sections:\n")
            
            for i, ctx in enumerate(contexts, 1):
                print(f"{i}. {ctx['file']}")
                print(f"   {ctx['content'][:200]}...\n")
        else:
            print(f"\n✗ Search failed: {result.get('error')}")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def test_fast_apply(project_dir: Path):
    """Test Fast Apply interactively."""
    try:
        morph = MorphClient()
        
        # Create a test file
        test_file = project_dir / "test_fast_apply.js"
        test_file.write_text("""
function hello() {
  return "world";
}

module.exports = { hello };
""")
        
        print(f"\n📝 Created test file: {test_file.name}")
        print("Original content:")
        print(test_file.read_text())
        
        code_edit = """
// ... existing code ...
function hello() {
  console.log("Hello from Fast Apply!");
  return "world";
}
// ... existing code ...
"""
        
        print(f"\n⚡ Applying edit with Fast Apply...")
        result = await morph.fast_apply(
            target_filepath=test_file.name,
            instructions="Add console.log to hello function",
            code_edit=code_edit,
            base_dir=str(project_dir)
        )
        
        if result.get("success"):
            print("\n✓ Edit applied successfully!")
            print(f"\nNew content:")
            print(test_file.read_text())
            
            changes = result.get("changes", {})
            print(f"\nChanges: +{changes.get('linesAdded', 0)} lines added")
        else:
            print(f"\n✗ Edit failed: {result.get('error')}")
        
        # Clean up
        test_file.unlink()
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


async def test_augment_context(project_dir: Path):
    """Test Augment Context interactively."""
    try:
        augment = AugmentClient(workspace_root=project_dir)
        
        query = input("\nWhat do you want to know about the codebase? ").strip()
        if not query:
            print("Query cannot be empty")
            return
        
        print(f"\n🧠 Getting context for: {query}")
        result = await augment.get_context(query, max_files=5)
        
        if result.get("success"):
            contexts = result.get("contexts", [])
            print(f"\n✓ Found {len(contexts)} relevant files:\n")
            
            for i, ctx in enumerate(contexts, 1):
                print(f"{i}. {ctx['file']}")
                if 'summary' in ctx:
                    print(f"   Summary: {ctx['summary']}")
                if 'relevance' in ctx:
                    print(f"   Relevance: {ctx['relevance']:.2f}")
                print()
        else:
            print(f"\n✗ Context retrieval failed: {result.get('error')}")
    
    except Exception as e:
        print(f"\n✗ Error: {e}")


if __name__ == "__main__":
    import os
    
    # Check for required environment variables
    has_morph = bool(os.getenv("MORPH_API_KEY"))
    has_augment = bool(os.getenv("AUGMENT_API_KEY"))
    
    if not has_morph and not has_augment:
        print("\n⚠️  No API keys configured!")
        print("\nSet these environment variables:")
        print("  export MORPH_API_KEY=your_key")
        print("  export AUGMENT_API_KEY=your_key")
        print("\nOr add them to your .env file\n")
        sys.exit(1)
    
    # Run tests
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        asyncio.run(interactive_test())
    else:
        asyncio.run(quick_test())
