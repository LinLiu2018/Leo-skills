# -*- coding: utf-8 -*-
"""
Message Router - 消息路由器

基于 OpenClaw Routing + Claude Code Agent 选择
"""

import logging
import re
from typing import Dict, List, Optional, Any, Callable, Awaitable
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class RouteStrategy(str, Enum):
    """路由策略"""
    KEYWORD = "keyword"       # 关键词匹配
    LLM = "llm"              # LLM 智能路由
    FALLBACK = "fallback"    # 兜底路由


@dataclass
class Route:
    """路由结果"""
    target: str              # 目标 (agent/skill/workflow)
    strategy: RouteStrategy  # 路由策略
    confidence: float        # 置信度 0-1
    params: Dict[str, Any]  # 额外参数
    response: str = ""       # 响应内容

    def to_dict(self) -> Dict[str, Any]:
        return {
            "target": self.target,
            "strategy": self.strategy.value,
            "confidence": self.confidence,
            "params": self.params,
            "response": self.response,
        }


class MessageRouter:
    """
    消息路由器

    支持多种路由策略:
    - 关键词匹配
    - 正则表达式
    - LLM 智能路由 (可选)
    """

    def __init__(self, strategy: RouteStrategy = RouteStrategy.KEYWORD):
        self.strategy = strategy

        # 关键词路由表
        self._keyword_rules: Dict[str, str] = {
            # Agent 路由
            "research": "research_agent",
            "分析": "analysis_agent",
            "创意": "creative_agent",
            "房地产": "realestate_agent",

            # Skill 路由
            "brainstorm": "brainstorming_skill",
            "头脑风暴": "brainstorming_skill",
            "写测试": "test_driven_development_skill",
            "tdd": "test_driven_development_skill",
            "debug": "systematic_debugging_skill",
            "调试": "systematic_debugging_skill",
            "计划": "writing_plans_skill",
            "review": "requesting_code_review_skill",

            # Workflow 路由
            "workflow": "default_workflow",
        }

        # 正则路由表
        self._regex_rules: List[tuple] = []

        # 自定义路由器
        self._custom_routers: List[Callable] = []

        # 兜底目标
        self._fallback = "general_agent"

        logger.info(f"MessageRouter initialized with strategy: {strategy}")

    def add_keyword_rule(self, keyword: str, target: str) -> None:
        """添加关键词路由规则"""
        self._keyword_rules[keyword.lower()] = target

    def add_regex_rule(self, pattern: str, target: str) -> None:
        """添加正则路由规则"""
        self._regex_rules.append((re.compile(pattern, re.IGNORECASE), target))

    def add_custom_router(self, router: Callable) -> None:
        """添加自定义路由器"""
        self._custom_routers.append(router)

    def set_fallback(self, target: str) -> None:
        """设置兜底目标"""
        self._fallback = target

    async def route(
        self,
        message,
        session: Any,
        context: Dict[str, Any]
    ) -> Route:
        """
        路由消息

        Args:
            message: 消息对象
            session: 会话对象
            context: 额外上下文

        Returns:
            Route 对象
        """
        content = message.content
        user_id = message.user_id

        # 1. 尝试自定义路由器
        for router in self._custom_routers:
            try:
                result = await router(message, session, context)
                if result:
                    return result
            except Exception as e:
                logger.debug(f"Custom router error: {e}")

        # 2. 关键词匹配
        target = self._match_keyword(content)
        if target:
            logger.debug(f"Keyword route: {content[:50]} -> {target}")
            return Route(
                target=target,
                strategy=RouteStrategy.KEYWORD,
                confidence=0.9,
                params={"method": "keyword"}
            )

        # 3. 正则匹配
        target = self._match_regex(content)
        if target:
            logger.debug(f"Regex route: {content[:50]} -> {target}")
            return Route(
                target=target,
                strategy=RouteStrategy.KEYWORD,
                confidence=0.8,
                params={"method": "regex"}
            )

        # 4. LLM 路由 (如果启用)
        if self.strategy == RouteStrategy.LLM:
            target = await self._route_with_llm(content, context)
            if target:
                return Route(
                    target=target,
                    strategy=RouteStrategy.LLM,
                    confidence=0.7,
                    params={"method": "llm"}
                )

        # 5. 兜底
        logger.debug(f"Fallback route: {content[:50]} -> {self._fallback}")
        return Route(
            target=self._fallback,
            strategy=RouteStrategy.FALLBACK,
            confidence=0.5,
            params={"method": "fallback"}
        )

    def _match_keyword(self, content: str) -> Optional[str]:
        """关键词匹配"""
        content_lower = content.lower()

        # 精确匹配
        if content_lower in self._keyword_rules:
            return self._keyword_rules[content_lower]

        # 包含匹配
        for keyword, target in self._keyword_rules.items():
            if keyword in content_lower:
                return target

        return None

    def _match_regex(self, content: str) -> Optional[str]:
        """正则匹配"""
        for pattern, target in self._regex_rules:
            if pattern.search(content):
                return target
        return None

    async def _route_with_llm(
        self,
        content: str,
        context: Dict[str, Any]
    ) -> Optional[str]:
        """使用 LLM 进行智能路由"""
        # TODO: 实现 LLM 路由
        # 可以调用现有的 leo_orchestrator 进行意图识别
        return None

    def get_stats(self) -> Dict[str, Any]:
        """获取路由统计"""
        return {
            "strategy": self.strategy.value,
            "keyword_rules": len(self._keyword_rules),
            "regex_rules": len(self._regex_rules),
            "custom_routers": len(self._custom_routers),
            "fallback": self._fallback,
        }

    def get_routes_for_context(self, context: Dict[str, Any]) -> List[str]:
        """根据上下文获取可用路由"""
        routes = []

        # 添加基于会话历史的路由
        if context.get("recent_agents"):
            routes.extend(context["recent_agents"])

        # 添加基于用户偏好的路由
        if context.get("user_preferences"):
            routes.extend(context["user_preferences"].get("preferred_agents", []))

        return routes


class SmartRouter(MessageRouter):
    """
    智能路由器 - 与 UnifiedRegistry 联动

    特性:
    - 自动从 Registry 同步路由表
    - 支持热更新
    - 技能优先级排序
    - Agent 冲突检测
    """

    def __init__(
        self,
        registry=None,
        strategy: RouteStrategy = RouteStrategy.KEYWORD,
        auto_sync: bool = True
    ):
        super().__init__(strategy)
        self._registry = registry
        self._auto_sync = auto_sync
        self._last_sync_time = 0
        self._sync_interval = 60  # 同步间隔(秒)
        self._skill_triggers: Dict[str, List[str]] = {}
        self._agent_triggers: Dict[str, List[str]] = {}

        # 注册 Registry 变更监听器，实现实时推送
        if registry and hasattr(registry, 'register_change_listener'):
            registry.register_change_listener(self._on_registry_change)
            logger.info("SmartRouter registered as Registry change listener")

        if auto_sync and registry:
            self._sync_from_registry()

    def _sync_from_registry(self) -> int:
        """
        从 Registry 同步路由表

        Returns:
            同步的规则数量
        """
        import time

        if not self._registry:
            return 0

        self._last_sync_time = time.time()
        synced_count = 0

        # 1. 同步 Skills
        try:
            for skill_name, skill in (self._registry.skills or {}).items():
                if not getattr(skill, 'enabled', True):
                    continue

                # 获取触发词
                triggers = getattr(skill, 'triggers', [])
                metadata_triggers = getattr(skill, 'metadata', {}).get('triggers', [])

                all_triggers = list(set(triggers + metadata_triggers))
                if not all_triggers:
                    # 默认触发词: skill_name 去掉后缀
                    default_trigger = skill_name.replace('_skill', '').replace('-', ' ')
                    all_triggers = [default_trigger]

                self._skill_triggers[skill_name] = all_triggers

                # 添加到关键词路由表
                for trigger in all_triggers:
                    self._keyword_rules[trigger.lower()] = skill_name
                    synced_count += 1

            logger.info(f"Synced {len(self._registry.skills or {})} skills with {synced_count} triggers")

        except Exception as e:
            logger.error(f"Failed to sync skills: {e}")

        # 2. 同步 Agents
        try:
            agent_count = 0
            for agent_name, agent in (self._registry.agents or {}).items():
                if not getattr(agent, 'enabled', True):
                    continue

                triggers = getattr(agent, 'triggers', [])
                metadata_triggers = getattr(agent, 'metadata', {}).get('triggers', [])

                all_triggers = list(set(triggers + metadata_triggers))
                if not all_triggers:
                    # 默认触发词
                    default_trigger = agent_name.replace('_agent', '').replace('-', ' ')
                    all_triggers = [default_trigger]

                self._agent_triggers[agent_name] = all_triggers

                for trigger in all_triggers:
                    self._keyword_rules[trigger.lower()] = agent_name
                    synced_count += 1

                agent_count += 1

            logger.info(f"Synced {agent_count} agents")

        except Exception as e:
            logger.error(f"Failed to sync agents: {e}")

        return synced_count

    def check_sync(self) -> bool:
        """检查是否需要同步，如需要则执行"""
        import time

        if not self._auto_sync or not self._registry:
            return False

        elapsed = time.time() - self._last_sync_time
        if elapsed > self._sync_interval:
            self._sync_from_registry()
            return True
        return False

    def _on_registry_change(self, change_type: str, item_name: str, version: int):
        """
        Registry 变更回调 - 实现实时推送

        Args:
            change_type: 变更类型
            item_name: 变更项名称
            version: 注册表版本
        """
        logger.info(f"Registry change detected: {change_type} - {item_name} (version: {version})")

        if change_type == "skill_added":
            self._sync_single_skill(item_name)
        elif change_type == "agent_added":
            self._sync_single_agent(item_name)
        elif change_type in ("skill_removed", "agent_removed"):
            self._remove_item_routes(item_name)
        elif change_type in ("skill_disabled", "agent_disabled"):
            self._remove_item_routes(item_name)
        elif change_type in ("skill_enabled", "agent_enabled"):
            # 重新同步启用的项目
            if change_type == "skill_enabled":
                self._sync_single_skill(item_name)
            else:
                self._sync_single_agent(item_name)
        else:
            # 其他变更，全量同步
            self._sync_from_registry()

    def _sync_single_skill(self, skill_name: str):
        """增量同步单个 Skill"""
        if not self._registry:
            return

        skill = self._registry.get_skill(skill_name)
        if not skill or not skill.enabled:
            return

        triggers = skill.get_all_triggers()
        if not triggers:
            triggers = [skill_name.replace('_skill', '').replace('-', ' ')]

        self._skill_triggers[skill_name] = triggers
        for trigger in triggers:
            self._keyword_rules[trigger.lower()] = skill_name

        logger.debug(f"Incremental sync: skill '{skill_name}' with {len(triggers)} triggers")

    def _sync_single_agent(self, agent_name: str):
        """增量同步单个 Agent"""
        if not self._registry:
            return

        agent = self._registry.get_agent(agent_name)
        if not agent or not agent.enabled:
            return

        triggers = agent.get_all_triggers()
        if not triggers:
            triggers = [agent_name.replace('_agent', '').replace('-', ' ')]

        self._agent_triggers[agent_name] = triggers
        for trigger in triggers:
            self._keyword_rules[trigger.lower()] = agent_name

        logger.debug(f"Incremental sync: agent '{agent_name}' with {len(triggers)} triggers")

    def _remove_item_routes(self, item_name: str):
        """移除项目的所有路由"""
        # 清理关键词路由表
        keys_to_remove = [k for k, v in self._keyword_rules.items() if v == item_name]
        for key in keys_to_remove:
            del self._keyword_rules[key]

        # 清理触发词记录
        if item_name in self._skill_triggers:
            del self._skill_triggers[item_name]
        if item_name in self._agent_triggers:
            del self._agent_triggers[item_name]

        logger.debug(f"Removed routes for '{item_name}'")

    async def route(
        self,
        message,
        session: Any,
        context: Dict[str, Any]
    ) -> Route:
        """
        路由消息 (自动同步检查)
        """
        # 检查是否需要同步
        self.check_sync()

        # 调用父类路由逻辑
        route = await super().route(message, session, context)

        # 增强: 检测 Agent 冲突
        if route.strategy == RouteStrategy.KEYWORD:
            conflicts = self._detect_conflicts(message.content, route.target)
            if conflicts:
                route.params['conflicts'] = conflicts
                route.params['conflict_resolution'] = self._resolve_conflicts(conflicts)

        return route

    def _detect_conflicts(self, content: str, selected_target: str) -> List[Dict[str, Any]]:
        """
        检测路由冲突

        Returns:
            冲突列表，每个冲突包含 target 和 confidence
        """
        conflicts = []
        content_lower = content.lower()

        # 检查是否有多个目标匹配
        matched_targets = set()

        for keyword, target in self._keyword_rules.items():
            if keyword in content_lower:
                matched_targets.add(target)

        if len(matched_targets) > 1:
            for target in matched_targets:
                if target != selected_target:
                    # 计算置信度 (简单启发式)
                    confidence = 0.7  # 基础置信度

                    # 如果关键词完全匹配，提高置信度
                    for trigger in self._get_triggers_for_target(target):
                        if trigger.lower() == content_lower:
                            confidence = 0.95
                            break

                    conflicts.append({
                        'target': target,
                        'confidence': confidence,
                        'type': 'skill' if 'skill' in target else 'agent'
                    })

        return conflicts

    def _get_triggers_for_target(self, target: str) -> List[str]:
        """获取目标的触发词"""
        if target in self._skill_triggers:
            return self._skill_triggers[target]
        if target in self._agent_triggers:
            return self._agent_triggers[target]
        return []

    def _resolve_conflicts(self, conflicts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        冲突解决策略

        Returns:
            解决决策
        """
        if not conflicts:
            return {'action': 'none'}

        # 策略 1: 选择置信度最高的
        best_match = max(conflicts, key=lambda x: x['confidence'])

        # 策略 2: Agent 优先于 Skill (如果置信度相近)
        agent_conflicts = [c for c in conflicts if c['type'] == 'agent']
        if agent_conflicts:
            best_agent = max(agent_conflicts, key=lambda x: x['confidence'])
            if best_agent['confidence'] >= best_match['confidence'] - 0.1:
                best_match = best_agent

        return {
            'action': 'select_highest_confidence',
            'selected': best_match['target'],
            'alternatives': [c['target'] for c in conflicts if c != best_match],
            'reason': f"Selected {best_match['target']} with confidence {best_match['confidence']}"
        }

    def force_sync(self) -> int:
        """强制同步 Registry"""
        return self._sync_from_registry()

    def get_registry_stats(self) -> Dict[str, Any]:
        """获取 Registry 同步统计"""
        return {
            'last_sync_time': self._last_sync_time,
            'skills_loaded': len(self._skill_triggers),
            'agents_loaded': len(self._agent_triggers),
            'total_triggers': len(self._keyword_rules),
            'auto_sync': self._auto_sync,
            'sync_interval': self._sync_interval,
        }

    def set_sync_interval(self, seconds: int) -> None:
        """设置同步间隔"""
        self._sync_interval = max(10, seconds)  # 最少10秒


def create_smart_router(registry=None, strategy: RouteStrategy = RouteStrategy.KEYWORD) -> SmartRouter:
    """创建智能路由器工厂函数"""
    # 如果未提供 registry，尝试从全局获取
    if registry is None:
        try:
            from leo_orchestrator.registry import get_registry
            registry = get_registry()
        except ImportError:
            logger.warning("Could not import registry, creating SmartRouter without registry")

    return SmartRouter(registry=registry, strategy=strategy)
