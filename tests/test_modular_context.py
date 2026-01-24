
import sys
from pathlib import Path
import os

# Add project root and src to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from leo_subagents.agents import ProductManagerAgent, AgentConfig, AgentFactory

def test_prd_template_loading():
    print("Testing Modular Context Loading for Product Manager Agent...")
    
    # Configure Agent
    config = AgentConfig(
        name="pm-test",
        type="product_manager",
        priority=1,
        skills=["research_assistant_skill"],
        description="Test Agent"
    )
    
    # Create Agent
    agent = ProductManagerAgent(config)
    
    # Mock context_cache check to ensure it's empty initially
    print(f"Initial Cache: {agent.context_cache}")
    
    # Run execute aimed at PRD
    # Note: We won't actually run the full skill execution because we might lack API keys or environment
    # But we can check if _plan_product_work loads the context.
    
    # We'll spy on the internal method since we just want to verify loading
    # Or we can just run it and check if the print statement appears or cache is populated.
    
    try:
        # Generate plan directly to test loading logic
        steps = agent._plan_product_work("Write a PRD for Login", "prd")
        
        # Check cache
        cache_key = "templates/prd_template.md"
        if cache_key in agent.context_cache:
            print("[SUCCESS] Success: PRD Template loaded in context_cache")
            print(f"Template size: {len(agent.context_cache[cache_key])} chars")
            return True
        else:
            print("[ERROR] Failure: PRD Template NOT found in context_cache")
            return False
            
    except Exception as e:
        print(f"[ERROR] Error during test: {e}")
        return False

if __name__ == "__main__":
    if test_prd_template_loading():
        sys.exit(0)
    else:
        sys.exit(1)
