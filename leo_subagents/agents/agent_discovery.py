"""
Agent 自动发现机制
==================
自动扫描 agents 目录并注册所有有效的 Agent 类
"""

import os
import yaml
import importlib.util
from pathlib import Path
from typing import Dict, List, Any, Optional, Type
from dataclasses import dataclass


@dataclass
class AgentMetadata:
    """Agent 元数据"""
    name: str
    type: str
    description: str
    version: str
    author: str
    priority: int
    skills: List[str]
    capabilities: List[str]
    enabled: bool = True
    module_path: Optional[str] = None
    class_name: Optional[str] = None


class AgentDiscovery:
    """
    Agent 自动发现器
    ================
    扫描目录结构，发现并注册所有 Agent
    """
    
    AGENT_MANIFEST_FILE = "agent.yaml"
    AGENT_CLASS_SUFFIX = "Agent"
    
    def __init__(self, agents_dir: Optional[Path] = None):
        """
        初始化发现器
        
        Args:
            agents_dir: agents 目录路径
        """
        if agents_dir is None:
            agents_dir = Path(__file__).parent
        self.agents_dir = Path(agents_dir)
        self.discovered_agents: Dict[str, AgentMetadata] = {}
        self._agent_classes: Dict[str, Type] = {}
    
    def discover_all(self) -> Dict[str, AgentMetadata]:
        """
        发现所有 Agent
        
        Returns:
            发现的 Agent 元数据字典
        """
        print(f"🔍 扫描 Agent 目录: {self.agents_dir}")
        
        for item in self.agents_dir.iterdir():
            if item.is_dir() and not item.name.startswith(('_', '.')):
                agent_meta = self._discover_agent(item)
                if agent_meta:
                    self.discovered_agents[agent_meta.name] = agent_meta
                    print(f"  ✅ 发现 Agent: {agent_meta.name} ({agent_meta.type})")
        
        print(f"📊 共发现 {len(self.discovered_agents)} 个 Agent")
        return self.discovered_agents
    
    def _discover_agent(self, agent_dir: Path) -> Optional[AgentMetadata]:
        """
        发现单个 Agent
        
        Args:
            agent_dir: Agent 目录
            
        Returns:
            Agent 元数据或 None
        """
        manifest_path = agent_dir / self.AGENT_MANIFEST_FILE
        
        # 方式1：通过 agent.yaml 清单文件
        if manifest_path.exists():
            return self._load_from_manifest(manifest_path, agent_dir)
        
        # 方式2：通过目录名和 Python 文件推断
        return self._infer_from_directory(agent_dir)
    
    def _load_from_manifest(self, manifest_path: Path, agent_dir: Path) -> Optional[AgentMetadata]:
        """
        从清单文件加载 Agent 元数据
        
        Args:
            manifest_path: 清单文件路径
            agent_dir: Agent 目录
            
        Returns:
            Agent 元数据
        """
        try:
            with open(manifest_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            return AgentMetadata(
                name=data.get('name', agent_dir.name),
                type=data.get('type', 'generic'),
                description=data.get('description', ''),
                version=data.get('version', '1.0.0'),
                author=data.get('author', 'unknown'),
                priority=data.get('priority', 5),
                skills=data.get('skills', []),
                capabilities=data.get('capabilities', []),
                enabled=data.get('enabled', True),
                module_path=data.get('module', f"{agent_dir.name}.py"),
                class_name=data.get('class_name', self._infer_class_name(agent_dir.name))
            )
        except Exception as e:
            print(f"  ⚠️ 读取清单失败 {manifest_path}: {e}")
            return None
    
    def _infer_from_directory(self, agent_dir: Path) -> Optional[AgentMetadata]:
        """
        从目录结构推断 Agent 元数据
        
        Args:
            agent_dir: Agent 目录
            
        Returns:
            Agent 元数据或 None
        """
        # 查找 *_agent.py 文件
        agent_files = list(agent_dir.glob("*_agent.py"))
        if not agent_files:
            agent_files = list(agent_dir.glob("*.py"))
            agent_files = [f for f in agent_files if not f.name.startswith('_')]
        
        if not agent_files:
            return None
        
        agent_file = agent_files[0]
        dir_name = agent_dir.name.replace('-', '_').replace('_agent', '')
        
        return AgentMetadata(
            name=agent_dir.name.replace('_', '-'),
            type=self._infer_agent_type(dir_name),
            description=f"自动发现的 {dir_name} Agent",
            version="1.0.0",
            author="auto-discovered",
            priority=5,
            skills=[],
            capabilities=[],
            enabled=True,
            module_path=agent_file.name,
            class_name=self._infer_class_name(agent_file.stem)
        )
    
    def _infer_class_name(self, name: str) -> str:
        """
        推断类名
        
        Args:
            name: 文件名或目录名
            
        Returns:
            推断的类名
        """
        # snake_case -> PascalCase
        parts = name.replace('-', '_').split('_')
        class_name = ''.join(part.capitalize() for part in parts)
        
        if not class_name.endswith('Agent'):
            class_name += 'Agent'
        
        return class_name
    
    def _infer_agent_type(self, name: str) -> str:
        """
        推断 Agent 类型
        
        Args:
            name: 目录名
            
        Returns:
            Agent 类型
        """
        type_mapping = {
            'research': 'researcher',
            'analysis': 'analyzer',
            'creative': 'creator',
            'task': 'executor',
            'realestate': 'realestate',
            'architect': 'architect',
            'product': 'product_manager',
            'mobile': 'mobile',
        }
        
        for key, agent_type in type_mapping.items():
            if key in name.lower():
                return agent_type
        
        return 'generic'
    
    def load_agent_class(self, agent_meta: AgentMetadata) -> Optional[Type]:
        """
        加载 Agent 类
        
        Args:
            agent_meta: Agent 元数据
            
        Returns:
            Agent 类或 None
        """
        if agent_meta.name in self._agent_classes:
            return self._agent_classes[agent_meta.name]
        
        agent_dir = self.agents_dir / agent_meta.name.replace('-', '_')
        if not agent_dir.exists():
            agent_dir = self.agents_dir / agent_meta.name
        
        module_file = agent_dir / agent_meta.module_path
        
        if not module_file.exists():
            print(f"  ⚠️ 模块文件不存在: {module_file}")
            return None
        
        try:
            # 动态加载模块
            spec = importlib.util.spec_from_file_location(
                f"leo_subagents.agents.{agent_meta.name}",
                str(module_file)
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 获取 Agent 类
            agent_class = getattr(module, agent_meta.class_name, None)
            
            if agent_class:
                self._agent_classes[agent_meta.name] = agent_class
                return agent_class
            else:
                print(f"  ⚠️ 未找到类 {agent_meta.class_name} in {module_file}")
                return None
                
        except Exception as e:
            print(f"  ⚠️ 加载 Agent 类失败 {agent_meta.name}: {e}")
            return None
    
    def register_all_to_factory(self, factory_class) -> int:
        """
        将所有发现的 Agent 注册到工厂
        
        Args:
            factory_class: AgentFactory 类
            
        Returns:
            成功注册的数量
        """
        registered = 0
        
        for name, meta in self.discovered_agents.items():
            if not meta.enabled:
                continue
            
            agent_class = self.load_agent_class(meta)
            if agent_class:
                factory_class.register_agent_class(meta.type, agent_class)
                registered += 1
                print(f"  🔗 注册 {meta.name} -> {meta.type}")
        
        return registered


# ==================== 便捷函数 ====================

_discovery: Optional[AgentDiscovery] = None


def get_discovery() -> AgentDiscovery:
    """获取全局发现器实例"""
    global _discovery
    if _discovery is None:
        _discovery = AgentDiscovery()
    return _discovery


def discover_and_register(factory_class) -> int:
    """
    发现并注册所有 Agent
    
    Args:
        factory_class: AgentFactory 类
        
    Returns:
        注册的 Agent 数量
    """
    discovery = get_discovery()
    discovery.discover_all()
    return discovery.register_all_to_factory(factory_class)


# ==================== 命令行测试 ====================

if __name__ == "__main__":
    discovery = AgentDiscovery()
    agents = discovery.discover_all()
    
    print("\n📋 发现的 Agent 列表:")
    for name, meta in agents.items():
        print(f"  • {name}")
        print(f"    类型: {meta.type}")
        print(f"    描述: {meta.description}")
        print(f"    模块: {meta.module_path}")
        print(f"    类名: {meta.class_name}")
