"""
Subagent Creator Skill - 元技能

自动创建 Claude Subagent 的完整解决方案。
"""

import re
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# 添加leo_system路径
leo_system_path = Path(__file__).parent.parent.parent.parent / "leo_system"
if str(leo_system_path) not in sys.path:
    sys.path.insert(0, str(leo_system_path))

try:
    from leo_skills.core.evolution import EvolvableSkill
except ImportError:
    # 如果进化框架不可用，使用简化版本
    class EvolvableSkill:
        def __init__(self, skill_name, evolution_path=None):
            self.skill_name = skill_name

        def learn(self, tip, context=""):
            print(f"[Evolution] {self.skill_name}: {tip}")


class SubagentCreatorSkill(EvolvableSkill):
    """
    Subagent 创建器 - 元技能

    自动创建 Claude Subagent 的完整解决方案。
    """

    # Agent 类型模板
    AGENT_TEMPLATES = {
        "executor": {
            "description": "任务执行代理",
            "base_class": "BaseAgent",
            "methods": ["can_handle", "execute"],
            "config": {"batch_size": 10, "async_execution": True}
        },
        "researcher": {
            "description": "研究代理 - 信息收集和分析",
            "base_class": "BaseAgent",
            "methods": ["can_handle", "execute"],
            "config": {"max_sources": 20, "research_depth": 3}
        },
        "analyzer": {
            "description": "分析代理 - 数据分析和趋势",
            "base_class": "BaseAgent",
            "methods": ["can_handle", "execute"],
            "config": {"analysis_method": "statistical", "visualization": True}
        },
        "creator": {
            "description": "创作代理 - 内容和文案生成",
            "base_class": "BaseAgent",
            "methods": ["can_handle", "execute"],
            "config": {"creativity_level": "balanced", "output_formats": ["markdown", "html"]}
        },
        "custom": {
            "description": "自定义代理",
            "base_class": "BaseAgent",
            "methods": ["can_handle", "execute"],
            "config": {}
        }
    }

    def __init__(self, skill_name: str = "subagent_creator"):
        super().__init__(skill_name, Path(__file__).parent / "evolution.json")

        # 路径配置 - 从 subagent_creator_skill/ 向上两级到项目根目录
        # subagent_creator_skill -> tools -> leo_skills -> src -> 项目根
        self.project_root = Path(__file__).parent.parent.parent.parent.parent
        self.agents_dir = self.project_root / "src" / "leo_subagents" / "agents"
        self.config_path = self.project_root / "src" / "leo_subagents" / "config" / "agents.yaml"

    def execute(self, action: str = "create", **kwargs) -> Dict[str, Any]:
        """
        执行创建操作

        Args:
            action: 操作类型
                - create: 从零创建 Agent
                - create_from_template: 从模板创建
                - analyze_and_recommend: 分析需求并推荐
                - list_templates: 列出可用模板
                - generate_code: 仅生成代码
                - update_config: 更新配置
            agent_name: Agent 名称
            description: Agent 描述
            agent_type: Agent 类型
            skills: 技能列表
            template: 模板名称
            task_description: 任务描述

        Returns:
            执行结果
        """
        actions = {
            "create": self._create_agent,
            "create_from_template": self._create_from_template,
            "analyze_and_recommend": self._analyze_and_recommend,
            "list_templates": self._list_templates,
            "generate_code": self._generate_code,
            "update_config": self._update_config,
        }

        if action not in actions:
            return {"success": False, "error": f"Unknown action: {action}"}

        return actions[action](**kwargs)

    def _create_agent(self, agent_name: str, description: str = "",
                      agent_type: str = "custom", skills: List[str] = None,
                      **kwargs) -> Dict[str, Any]:
        """创建完整的 Agent"""
        try:
            # 1. 分析和验证
            if not agent_name:
                return {"success": False, "error": "agent_name is required"}

            agent_name = self._normalize_name(agent_name)
            agent_dir = self.agents_dir / f"{agent_name}_agent"

            if agent_dir.exists():
                return {"success": False, "error": f"Agent already exists: {agent_name}"}

            # 2. 确定技能列表
            if not skills:
                skills = self._recommend_skills(agent_type, description)

            # 3. 生成代码
            code = self._generate_agent_code(agent_name, description, agent_type, skills)

            # 4. 生成配置
            config = self._generate_agent_config(agent_name, description, agent_type, skills)

            # 5. 创建目录和文件
            agent_dir.mkdir(parents=True, exist_ok=True)

            # 创建 Python 文件
            py_file = agent_dir / f"{agent_name}_agent.py"
            py_file.write_text(code, encoding="utf-8")

            # 创建 __init__.py
            init_file = agent_dir / "__init__.py"
            init_content = self._generate_init_file(agent_name)
            init_file.write_text(init_content, encoding="utf-8")

            # 6. 更新 agents.yaml
            self._update_agents_yaml(config)

            # 7. 更新 agents/__init__.py
            self._update_agents_init(agent_name)

            self.learn(f"Created agent: {agent_name} with {len(skills)} skills")

            return {
                "success": True,
                "agent_name": agent_name,
                "agent_dir": str(agent_dir),
                "skills": skills,
                "files_created": ["__init__.py", f"{agent_name}_agent.py"],
                "config_updated": True
            }

        except Exception as e:
            self.learn(f"Failed to create agent {agent_name}: {str(e)}", "error")
            return {"success": False, "error": str(e)}

    def _create_from_template(self, template: str, agent_name: str, **kwargs) -> Dict[str, Any]:
        """从模板创建 Agent"""
        if template not in self.AGENT_TEMPLATES:
            return {"success": False, "error": f"Unknown template: {template}"}

        template_info = self.AGENT_TEMPLATES[template]
        agent_type = template

        return self._create_agent(
            agent_name=agent_name,
            description=template_info["description"],
            agent_type=agent_type,
            skills=[],
            **kwargs
        )

    def _analyze_and_recommend(self, task_description: str, **kwargs) -> Dict[str, Any]:
        """分析需求并推荐 Agent 配置"""
        # 分析任务描述，推断类型和技能
        task_lower = task_description.lower()

        # 推断 Agent 类型
        agent_type = "custom"
        type_keywords = {
            "research": ["研究", "调研", "搜索", "收集", "调查", "research", "search", "investigate"],
            "analyzer": ["分析", "数据", "统计", "趋势", "analyze", "data", "statistics"],
            "creator": ["创作", "写", "生成", "文案", "内容", "create", "write", "generate"],
            "executor": ["执行", "处理", "自动化", "执行", "execute", "process", "automate"],
        }

        for type_name, keywords in type_keywords.items():
            if any(kw in task_lower for kw in keywords):
                agent_type = type_name
                break

        # 推荐技能
        recommended_skills = self._recommend_skills(agent_type, task_description)

        # 推荐激活词
        activation_keywords = self._generate_activation_keywords(task_description)

        return {
            "success": True,
            "task_description": task_description,
            "recommended_type": agent_type,
            "recommended_skills": recommended_skills,
            "activation_keywords": activation_keywords,
            "template": agent_type,
            "suggested_name": self._generate_name_from_task(task_description)
        }

    def _list_templates(self, **kwargs) -> Dict[str, Any]:
        """列出可用模板"""
        templates = []
        for name, info in self.AGENT_TEMPLATES.items():
            templates.append({
                "name": name,
                "description": info["description"],
                "methods": info["methods"],
                "config_keys": list(info["config"].keys()) if info["config"] else []
            })

        return {
            "success": True,
            "templates": templates,
            "total": len(templates)
        }

    def _generate_code(self, agent_name: str, description: str = "",
                       agent_type: str = "custom", skills: List[str] = None,
                       **kwargs) -> Dict[str, Any]:
        """仅生成代码，不创建文件"""
        agent_name = self._normalize_name(agent_name)
        if not skills:
            skills = []

        code = self._generate_agent_code(agent_name, description, agent_type, skills)

        return {
            "success": True,
            "agent_name": agent_name,
            "code": code
        }

    def _update_config(self, config_yaml: str, **kwargs) -> Dict[str, Any]:
        """更新 agents.yaml"""
        try:
            current_content = self.config_path.read_text(encoding="utf-8")

            # 检查是否已存在同名 agent
            agent_match = re.search(r'(\w+)-agent:', config_yaml)
            if agent_match:
                agent_name = agent_match.group(1)
                if re.search(rf'{agent_name}-agent:', current_content):
                    return {"success": False, "error": f"Agent {agent_name} already exists in config"}

            # 追加配置
            # 找到 workflows: 之前的位置
            insert_pos = current_content.find('# Workflows')
            if insert_pos == -1:
                insert_pos = len(current_content)

            new_content = current_content[:insert_pos] + config_yaml + "\n" + current_content[insert_pos:]

            self.config_path.write_text(new_content, encoding="utf-8")

            return {"success": True, "message": "Config updated"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    # ==================== 辅助方法 ====================

    def _normalize_name(self, name: str) -> str:
        """标准化 Agent 名称"""
        # 移除 -agent 后缀
        name = name.replace("-agent", "")
        # 转换为 snake_case
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1_\2', name)
        name = re.sub(r'([a-z\d])([A-Z])', r'\1_\2', name)
        name = name.replace('-', '_')
        return name.lower()

    def _generate_name_from_task(self, task: str) -> str:
        """从任务描述生成 Agent 名称"""
        # 提取关键词
        keywords = re.findall(r'\b[a-zA-Z]+\b', task)
        if len(keywords) >= 2:
            return f"{keywords[0]}_{keywords[1]}_agent"
        elif keywords:
            return f"{keywords[0]}_agent"
        else:
            return "custom_agent"

    def _recommend_skills(self, agent_type: str, description: str) -> List[str]:
        """推荐技能组合"""
        # 根据类型推荐默认技能
        type_skills = {
            "researcher": ["research_assistant_skill", "web_search_skill"],
            "analyzer": ["data_analyzer_skill"],
            "creator": ["content_layout_leo_skill", "article_to_prototype_skill"],
            "executor": [],
        }

        skills = type_skills.get(agent_type, [])

        # 根据描述添加关键词
        desc_lower = description.lower()
        if "电商" in desc_lower or "电商" in desc_lower:
            skills.extend(["content_layout_leo_skill", "article_to_prototype_skill"])
        if "房地产" in desc_lower or "realestate" in desc_lower:
            skills.extend(["project_marketing_doc_generator_skill", "realestate_news_publisher_skill"])

        # 去重
        return list(dict.fromkeys(skills))

    def _generate_activation_keywords(self, task: str) -> List[str]:
        """生成激活词"""
        keywords = []

        # 从任务描述提取动词
        verbs = re.findall(r'\b(创建|生成|分析|研究|执行|处理|搜索|写|制作)\b', task)
        keywords.extend(verbs)

        # 如果没有提取到，添加默认
        if not keywords:
            keywords = ["帮我", "请", "需要"]

        return keywords[:5]

    def _generate_agent_code(self, agent_name: str, description: str,
                             agent_type: str, skills: List[str]) -> str:
        """生成 Agent Python 代码"""
        class_name = ''.join(word.title() for word in agent_name.split('_')) + 'Agent'

        skills_str = ',\n            '.join([f'"{s}"' for s in skills]) if skills else ""

        code = f'''"""
{class_name}

{description}
"""

import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List

# 添加父目录到路径
parent_path = Path(__file__).parent.parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

if TYPE_CHECKING:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig
else:
    from leo_subagents.agents.base_agent import BaseAgent, AgentConfig

from leo_subagents.agents.base_agent import logger


class {class_name}(BaseAgent):
    """
    {class_name}

    {description}
    """

    def __init__(self, config: AgentConfig):
        """初始化 Agent"""
        super().__init__(config)
        self.agent_name = "{agent_name}"

    def can_handle(self, task: str) -> float:
        """
        判断是否能处理此任务

        Args:
            task: 任务描述

        Returns:
            置信度 (0.0 - 1.0)
        """
        task_lower = task.lower()

        # 定义关键词匹配
        keywords = [
            "{agent_name}",
            "{description[:20] if description else 'task'}"
        ]

        for keyword in keywords:
            if keyword.lower() in task_lower:
                return 0.9

        # 检查是否需要使用的技能
        for skill in self.config.skills:
            if skill.lower() in task_lower:
                return 0.7

        return 0.3

    @BaseAgent.track_time
    def execute(self, task: str, **kwargs) -> Dict[str, Any]:
        """
        执行任务

        Args:
            task: 任务描述
            **kwargs: 任务参数

        Returns:
            执行结果
        """
        try:
            # 记录任务
            self.log_task(task, {{"status": "started"}})

            # 规划执行步骤
            plan = self.plan_execution(task, **kwargs)

            # 执行计划
            results = []
            for step in plan:
                step_result = {{
                    "step": step["step"],
                    "skill": step.get("skill", ""),
                    "status": "pending"
                }}

                # 如果有技能，使用技能执行
                if step.get("skill"):
                    try:
                        skill_result = self.use_skill(
                            step["skill"],
                            step.get("action", "execute"),
                            **step.get("params", {{}})
                        )
                        step_result["result"] = skill_result
                        step_result["status"] = "completed"
                    except Exception as e:
                        step_result["error"] = str(e)
                        step_result["status"] = "failed"

                results.append(step_result)

            # 汇总结果
            success_count = sum(1 for r in results if r["status"] == "completed")
            total_count = len(results)

            final_result = {{
                "task": task,
                "status": "completed" if success_count == total_count else "partial",
                "total_steps": total_count,
                "completed_steps": success_count,
                "results": results,
                "agent": self.agent_name
            }}

            # 记录完成
            self.log_task(task, final_result)

            return final_result

        except Exception as e:
            error_result = {{
                "task": task,
                "status": "failed",
                "error": str(e),
                "agent": self.agent_name
            }}
            self.log_task(task, error_result)
            logger.error(f"Agent execution failed: {{e}}")
            return error_result


# ==================== 注册 ====================

# 在 AgentFactory 中注册此 Agent
# AGENT_TYPE = "{agent_type}"
'''

        return code

    def _generate_agent_config(self, agent_name: str, description: str,
                                agent_type: str, skills: List[str]) -> str:
        """生成 agents.yaml 配置片段"""
        skills_config = ""
        for skill in skills:
            skills_config += f'''      - name: "{skill}"
        path: "../leo_skills/tools/{skill}"
        enabled: true
'''

        config = f'''
  # {description}
  {agent_name}-agent:
    name: "{agent_name.title().replace('_', ' ')}"
    description: "{description}"
    type: "{agent_type}"
    priority: 10

    skills:
{skills_config}
    config:
      output_format: "json"

    activation_keywords:
      - "{agent_name}"
'''

        return config

    def _generate_init_file(self, agent_name: str) -> str:
        """生成 __init__.py"""
        class_name = ''.join(word.title() for word in agent_name.split('_')) + 'Agent'

        return f'''from .{agent_name}_agent import {class_name}

__all__ = ["{class_name}"]
'''

    def _update_agents_yaml(self, config: str) -> None:
        """更新 agents.yaml"""
        if not self.config_path.exists():
            return

        content = self.config_path.read_text(encoding="utf-8")

        # 找到 workflows: 之前的位置
        insert_pos = content.find('# Workflows')
        if insert_pos == -1:
            insert_pos = len(content)

        new_content = content[:insert_pos] + config + content[insert_pos:]
        self.config_path.write_text(new_content, encoding="utf-8")

    def _update_agents_init(self, agent_name: str) -> None:
        """更新 agents/__init__.py"""
        init_path = self.agents_dir / "__init__.py"

        if not init_path.exists():
            init_path.write_text('"""Agents Package"""', encoding="utf-8")
            return

        content = init_path.read_text(encoding="utf-8")

        # 检查是否已存在
        if agent_name in content:
            return

        # 添加导入
        class_name = ''.join(word.title() for word in agent_name.split('_')) + 'Agent'
        import_line = f'from .{agent_name}_agent import {class_name}\n'

        # 添加到文件末尾
        content += import_line
        init_path.write_text(content, encoding="utf-8")
