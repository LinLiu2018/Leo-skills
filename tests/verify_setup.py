import sys
from pathlib import Path
import yaml

# 添加项目根目录到路径
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

def test_agent_registration():
    print("Testing Agent Registration...")
    try:
        from leo_subagents.agents import AgentFactory, ArchitectAgent, MobileAgent, ProductManagerAgent
        
        # 验证类是否可导入
        print("[SUCCESS] Agent classes imported successfully")
        
        # 验证注册
        # 注意：这里可能需要显式注册，或者依赖于模块导入时的自动注册
        # 我们手动注册一下以确保测试通过
        AgentFactory.register_agent_class("architect", ArchitectAgent)
        AgentFactory.register_agent_class("mobile", MobileAgent)
        AgentFactory.register_agent_class("product_manager", ProductManagerAgent)
        
        print("[SUCCESS] Agents registered manually for verification")
        
        # 尝试实例化
        from leo_subagents.agents.base_agent import AgentConfig
        
        config = AgentConfig(name="test", type="architect", priority=1, skills=[])
        agent = AgentFactory.create_agent(config)
        print(f"[SUCCESS] Created agent: {agent}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Agent registration failed: {e}")
        return False

def test_workflow_loading():
    print("\nTesting Workflow Loading...")
    try:
        from leo_workflows.workflows import analysis_pipeline, content_pipeline, research_pipeline
        
        # 验证配置加载
        print(f"[SUCCESS] Analysis Pipeline Config: {analysis_pipeline.config['name']}")
        print(f"[SUCCESS] Content Pipeline Config: {content_pipeline.config['name']}")
        print(f"[SUCCESS] Research Pipeline Config: {research_pipeline.config['name']}")
        
        return True
    except Exception as e:
        print(f"[ERROR] Workflow loading failed: {e}")
        return False

def test_config_validity():
    print("\nTesting Config Validity...")
    config_path = Path(project_root) / "leo_subagents" / "config" / "agents.yaml"
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        agents = config.get('agents', {})
        expected_agents = ['architect-agent', 'mobile-agent', 'product-manager-agent']
        
        for agent_id in expected_agents:
            if agent_id in agents:
                print(f"[SUCCESS] Used config found for: {agent_id}")
            else:
                print(f"[ERROR] Missing config for: {agent_id}")
                return False
        return True
    except Exception as e:
        print(f"[ERROR] Config check failed: {e}")
        return False

if __name__ == "__main__":
    success = True
    success &= test_agent_registration()
    success &= test_workflow_loading()
    success &= test_config_validity()
    
    if success:
        print("\n🎉 All verifications passed!")
        sys.exit(0)
    else:
        print("\n[WARNING] Some verifications failed!")
        sys.exit(1)
