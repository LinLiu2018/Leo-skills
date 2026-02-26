
import sys
from pathlib import Path
import json
import os

# Add project root to sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from leo_orchestrator.api import leo
from leo_subagents.agents import AgentConfig, AgentFactory

from dotenv import load_dotenv

def load_env():
    """Load .env file using python-dotenv"""
    env_path = project_root / ".env"
    if env_path.exists():
        print(f"📄 Loading .env file from {env_path}")
        load_dotenv(env_path, override=True)
        # Verify API Keys
        zhipu = os.environ.get("ZHIPUAI_API_KEY")
        deepseek = os.environ.get("DEEPSEEK_API_KEY")
        
        if zhipu:
             masked = zhipu[:3] + "..." + zhipu[-3:] if len(zhipu) > 6 else "***"
             print(f"   [SUCCESS] Loaded ZHIPUAI_API_KEY={masked}")
        if deepseek:
             masked = deepseek[:3] + "..." + deepseek[-3:] if len(deepseek) > 6 else "***"
             print(f"   [SUCCESS] Loaded DEEPSEEK_API_KEY={masked}")
        
        if not (zhipu or deepseek):
             print("   [WARNING]  No supported API Key found (DeepSeek/ZhipuAI)")
    else:
        print("[WARNING]  .env file not found")

def implement_web_ui():
    load_env()
    print("[LAUNCH] Starting Web UI Implementation Pipeline...")
    print("   Goal: Research Best Practices -> Design System -> Generate Code")
    print("-" * 60)

    # 1. Research Phase
    print("\n📍 Phase 1: Research (Web UI Trends)")
    # We use a Task Agent disguised as Researcher because ResearchAgent's skills are currently academic-focused
    # or we can just use the Text Generator directly via API for this script to emulate a smart agent.
    # Let's use the API to run a "Research Agent" capability directly.
    
    # Ensure Text Generator Skill is enabled
    leo.enable("skill", "text_generator_skill")
    
    trends = leo.call(
        "text_generator_skill", 
        "generate", 
        prompt="What are the top Web UI design trends for 2026? Focus on Enterprise AI Dashboards. List 5 key points.",
        format="text"
    )
    
    print(f"DEBUG: trends type: {type(trends)}")
    print(f"DEBUG: trends success: {getattr(trends, 'success', 'N/A')}")
    if hasattr(trends, 'result'):
         print(f"DEBUG: trends.result: {trends.result}")
    
    # leo.call returns ExecutionResult object, not dict
    
    if trends and trends.success and trends.result.get("success"):
        # trends.result is the dict returned by text_generator_skill
        content = trends.result['result']
        print(f"[SUCCESS] Research Complete:\n{content[:200]}...")
        
        # Save to Knowledge Base
        kb_path = project_root / "leo_knowledge/frameworks/web_design_trends.md"
        with open(kb_path, "w", encoding="utf-8") as f:
            f.write(f"# Web Design Trends 2026\n\n{content}")
        print(f"   Saved to {kb_path}")
        research_context = content
    else:
        error_msg = trends.result.get('error') if trends and trends.result else (trends.error if trends else "Unknown error")
        print(f"[ERROR] Research Failed: {error_msg}. Using default context.")
        research_context = "Clean, Minimalist, Bento Grid, Dark Mode, Glassmorphism."

    # 2. Design Phase
    print("\n📍 Phase 2: System Design")
    design_spec = leo.call(
        "text_generator_skill",
        "generate",
        prompt="Create a Design System Specification for an AI Agent Dashboard based on these trends.",
        context=research_context,
        format="markdown"
    )
    
    if design_spec and design_spec.success and design_spec.result.get("success"):
        content = design_spec.result['result']
        print(f"[SUCCESS] Design Complete:\n{content[:200]}...")
        design_context = content
        
        # Save to Knowledge Base
        kb_path = project_root / "leo_knowledge/frameworks/web_design_system.md"
        with open(kb_path, "w", encoding="utf-8") as f:
            f.write(f"# Web Design System\n\n{design_context}")
        print(f"   Saved to {kb_path}")
    else:
        print("[ERROR] Design Failed. Using default context.")
        design_context = "Primary Color: Blue-500. Font: Inter."

    # 3. Implementation Phase
    print("\n📍 Phase 3: Frontend Implementation")
    components = ["DashboardLayout", "AgentStatusCard", "TrendChart"]
    
    output_dir = project_root / "leo_skills/development/frontend/web-ui"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    for comp in components:
        print(f"   Generating {comp}...")
        code_result = leo.call(
            "text_generator_skill",
            "generate",
            prompt=f"Write a React/Next.js component for {comp}. Use Tailwind CSS.",
            context=design_context,
            format="code"
        )
        
        if code_result and code_result.success and code_result.result.get("success"):
            code = code_result.result['result']
            # Simple extraction of code block if needed, or just save raw
            file_path = output_dir / f"{comp}.tsx"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(code)
            print(f"   [SUCCESS] Generated: {file_path}")
        else:
            print(f"   [ERROR] Failed to generate {comp}")

    print("-" * 60)
    print("[SPARKLE] Pipeline Complete. Web UI implemented.")

if __name__ == "__main__":
    implement_web_ui()
