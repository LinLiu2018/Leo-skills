
import sys
from pathlib import Path
import json

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_subagents.agents import ProductManagerAgent, AgentConfig, AgentFactory

def run_prd_task():
    print("[LAUNCH] Starting Product Manager Agent for PRD Task...")
    
    # Configure Agent
    config = AgentConfig(
        name="pm-runner",
        type="product_manager",
        priority=1,
        skills=["research_assistant_skill", "web_search_skill", "text_generator_skill"],
        description="Runner Agent"
    )
    
    # Create Agent
    agent = ProductManagerAgent(config)
    
    task = "编写 AI 眼镜电商小程序 PRD"
    print(f"📋 Task: {task}")
    
    # Execute
    try:
        result = agent.execute(task, task_type="prd", project_name="AI Glasses E-com")
        
        print("\n[SUCCESS] Task Completed!")
        print("=" * 50)
        
        # Check if template was loaded (we can infer from logs or result structure if skill used it)
        # For now, let's print the summary
        print(f"Summary:\n{result.get('summary', 'No summary')}")
        
        print("-" * 50)
        # If we had a mechanism where the skill returns the generated text based on template, 
        # it would be in detailed_results. 
        # Since the skill implementation details regarding template usage weren't fully verified,
        # we focus on the Agent passing the template in kwargs.
        
        # Let's verify context loading from cache directly
        if "templates/prd_template.md" in agent.context_cache:
            print(f"\n[SPARKLE] Verified: PRD Template was loaded into context ({len(agent.context_cache['templates/prd_template.md'])} chars).")
        else:
            print("\n[WARNING] Warning: PRD Template was NOT loaded.")
            
    except Exception as e:
        print(f"\n[ERROR] Prediction failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_prd_task()
