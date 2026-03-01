#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
意图识别引擎 (Intent Recognition Engine)

基于关键词匹配、语义相似度和上下文推断的用户意图识别系统。
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class IntentMatch:
    """意图匹配结果"""
    intent_type: str  # 'skill', 'agent', 'workflow', 'general'
    target: str  # 目标名称
    confidence: float  # 置信度 0-1
    params: Dict[str, Any]  # 提取的参数
    reason: str  # 匹配原因


@dataclass
class IntentPattern:
    """意图模式定义"""
    name: str
    intent_type: str
    triggers: List[str]  # 触发关键词
    regex_patterns: List[str]  # 正则模式
    priority: int = 1


class IntentRecognizer:
    """
    意图识别器

    支持三种识别方式：
    1. 关键词匹配 - 快速、精确
    2. 正则模式 - 灵活、可扩展
    3. 语义相似度 - 智能、容错
    """

    def __init__(self, registry=None):
        self.registry = registry
        self.patterns: List[IntentPattern] = []
        self.intent_cache: Dict[str, IntentMatch] = {}
        self._load_default_patterns()

    def _load_default_patterns(self):
        """加载默认意图模式"""
        # 技能相关意图
        self.patterns.extend([
            IntentPattern(
                name="skill_execution",
                intent_type="skill",
                triggers=["执行技能", "运行技能", "使用技能", "调用技能", "skill", "run skill"],
                regex_patterns=[
                    r"(?:执行|运行|使用|调用)\s*(.+?)\s*技能",
                    r"(?:use|run|execute)\s+(.+?)\s+skill",
                ],
                priority=2
            ),
            IntentPattern(
                name="agent_delegation",
                intent_type="agent",
                triggers=["委托给", "让", "帮我", "研究", "分析", "生成", "创建", "调查"],
                regex_patterns=[
                    r"(?:让|请|帮|委托)\s*(.+?)(?:agent|代理|帮我)?",
                    r"(?:research|analyze|generate|create)\s+(.+?)",
                ],
                priority=2
            ),
            IntentPattern(
                name="workflow_trigger",
                intent_type="workflow",
                triggers=["启动工作流", "运行流程", "执行流程", "workflow", "pipeline"],
                regex_patterns=[
                    r"(?:启动|运行|执行)\s*(.+?)\s*(?:工作流|流程|pipeline)",
                ],
                priority=1
            ),
            IntentPattern(
                name="practice_accumulation",
                intent_type="workflow",
                triggers=["沉淀", "保存prompt", "保存提示词", "积累经验",
                          "沉淀实操", "提示词库", "prompt vault"],
                regex_patterns=[
                    r"(?:沉淀|保存|积累|记录).*(?:实操|经验|提示词|prompt)",
                    r"(?:save|store|accumulate).*(?:prompt|skill|experience)",
                ],
                priority=2
            ),
            IntentPattern(
                name="use_prompt",
                intent_type="skill",
                triggers=["用提示词", "用prompt", "用框架", "使用提示词",
                          "使用框架", "use prompt", "apply prompt",
                          "用CRISPE", "用CO-STAR", "用RISEN"],
                regex_patterns=[
                    r"(?:用|使用|应用|套用)\s*(.+?)\s*(?:框架|提示词|prompt|模板)",
                    r"(?:用|使用|应用|套用)\s*([\w\-]+)\s*$",
                    r"(?:use|apply)\s+(.+?)\s*(?:framework|prompt|template)?$",
                ],
                priority=3
            ),
        ])
        # 按优先级排序，高优先级先匹配
        self.patterns.sort(key=lambda p: p.priority, reverse=True)

    def register_pattern(self, pattern: IntentPattern):
        """注册自定义意图模式"""
        self.patterns.append(pattern)
        # 按优先级排序
        self.patterns.sort(key=lambda p: p.priority, reverse=True)

    def recognize(self, user_input: str, context: Optional[Dict] = None) -> IntentMatch:
        """
        识别用户意图

        Args:
            user_input: 用户输入文本
            context: 可选的上下文信息

        Returns:
            IntentMatch: 意图匹配结果
        """
        user_input = user_input.strip().lower()
        context = context or {}

        # 1. 检查缓存
        cache_key = f"{user_input}:{hash(str(context))}"
        if cache_key in self.intent_cache:
            return self.intent_cache[cache_key]

        # 2. 关键词匹配
        match = self._match_by_keywords(user_input)
        if match and match.confidence >= 0.8:
            self.intent_cache[cache_key] = match
            return match

        # 3. 正则匹配
        match = self._match_by_regex(user_input)
        if match and match.confidence >= 0.7:
            self.intent_cache[cache_key] = match
            return match

        # 4. 上下文推断
        if context.get('last_intent'):
            match = self._infer_from_context(user_input, context)
            if match and match.confidence >= 0.6:
                self.intent_cache[cache_key] = match
                return match

        # 5. 默认返回 general 意图
        default_match = IntentMatch(
            intent_type="general",
            target="",
            confidence=0.5,
            params={"original_input": user_input},
            reason="no specific intent matched"
        )
        self.intent_cache[cache_key] = default_match
        return default_match

    def _match_by_keywords(self, user_input: str) -> Optional[IntentMatch]:
        """基于关键词匹配意图"""
        if not self.registry:
            return None

        # 检查技能触发词
        for skill_name, skill in (self.registry.skills or {}).items():
            triggers = getattr(skill, 'triggers', [])
            for trigger in triggers:
                if trigger.lower() in user_input:
                    return IntentMatch(
                        intent_type="skill",
                        target=skill_name,
                        confidence=0.9,
                        params={"trigger": trigger},
                        reason=f"matched skill trigger: {trigger}"
                    )

        # 检查 Agent 触发词
        for agent_name, agent in (self.registry.agents or {}).items():
            triggers = getattr(agent, 'triggers', [])
            for trigger in triggers:
                if trigger.lower() in user_input:
                    return IntentMatch(
                        intent_type="agent",
                        target=agent_name,
                        confidence=0.85,
                        params={"trigger": trigger},
                        reason=f"matched agent trigger: {trigger}"
                    )

        return None

    def _match_by_regex(self, user_input: str) -> Optional[IntentMatch]:
        """基于正则模式匹配意图"""
        for pattern in self.patterns:
            for regex in pattern.regex_patterns:
                match = re.search(regex, user_input, re.IGNORECASE)
                if match:
                    extracted = match.group(1) if match.groups() else ""
                    return IntentMatch(
                        intent_type=pattern.intent_type,
                        target=extracted,
                        confidence=0.7 + (0.1 * pattern.priority),
                        params={"extracted": extracted, "pattern": pattern.name},
                        reason=f"matched regex pattern: {pattern.name}"
                    )
        return None

    def _infer_from_context(self, user_input: str, context: Dict) -> Optional[IntentMatch]:
        """基于上下文推断意图"""
        last_intent = context.get('last_intent')
        conversation_history = context.get('history', [])

        # 如果是简短回复，延续上一个意图
        if len(user_input) < 20 and last_intent:
            # 检查是否是确认/否定
            confirm_words = ['是', '对', '好', 'yes', 'ok', '确认', '执行']
            deny_words = ['不', '否', 'no', 'cancel', '取消']

            if any(w in user_input for w in confirm_words):
                return IntentMatch(
                    intent_type=last_intent.get('type', 'general'),
                    target=last_intent.get('target', ''),
                    confidence=0.7,
                    params={"confirmation": True},
                    reason="context: user confirmed previous intent"
                )

        return None

    def route(self, user_input: str, context: Optional[Dict] = None) -> Dict:
        """
        路由决策：根据意图选择执行路径

        Returns:
            Dict with routing decision
        """
        intent = self.recognize(user_input, context)

        routing_decision = {
            "intent": intent,
            "action": None,
            "target": None,
            "params": intent.params
        }

        # 特殊处理：use_prompt 意图 → 自动调取提示词并组装任务
        if intent.params.get("pattern") == "use_prompt":
            routing_decision["action"] = "use_prompt"
            routing_decision["target"] = "prompt_vault_skill"
            routing_decision["params"]["query"] = intent.target
            routing_decision["params"]["original_input"] = user_input
            return routing_decision

        if intent.intent_type == "skill":
            routing_decision["action"] = "execute_skill"
            routing_decision["target"] = intent.target

        elif intent.intent_type == "agent":
            routing_decision["action"] = "delegate_to_agent"
            routing_decision["target"] = intent.target

        elif intent.intent_type == "workflow":
            routing_decision["action"] = "trigger_workflow"
            routing_decision["target"] = intent.target

        else:
            # 默认使用 orchestrator 处理
            routing_decision["action"] = "general_chat"

        return routing_decision


# 全局意图识别器实例
_intent_recognizer: Optional[IntentRecognizer] = None


def get_intent_recognizer(registry=None) -> IntentRecognizer:
    """获取全局意图识别器实例（线程安全）"""
    global _intent_recognizer
    if _intent_recognizer is None:
        from leo_system.singleton import thread_safe_singleton
        _intent_recognizer = thread_safe_singleton(
            "intent_recognizer", _intent_recognizer,
            lambda: IntentRecognizer(registry)
        )
    return _intent_recognizer
