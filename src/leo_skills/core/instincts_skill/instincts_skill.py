# -*- coding: utf-8 -*-
"""
Instincts Skill - AI Agent本能系统
===================================

参考 everything-claude-code 的 Instincts 设计
提供模式匹配自动触发机制

核心概念：
- Instinct: 自动触发的行为规则
- Trigger: 触发条件
- Action: 执行行为
- Evidence: 支撑证据

Author: Leo AI System
"""

import json
import re
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult
import logging

logger = logging.getLogger(__name__)


class TriggerType(Enum):
    """触发类型"""
    KEYWORD = "keyword"
    REGEX = "regex"
    SEMANTIC = "semantic"
    COMBINED = "combined"


@dataclass
class InstinctEvidence:
    """本能证据"""
    description: str
    confidence: float  # 0.0 - 1.0
    source: str  # "builtin", "learned", "user"
    examples: List[str] = field(default_factory=list)


@dataclass
class Instinct:
    """本能定义"""
    id: str
    name: str
    description: str
    trigger_type: str  # keyword, regex, semantic, combined
    trigger_pattern: str  # 触发模式
    action_skill: str  # 触发的skill名称
    action_params: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 5  # 1-10, 越高越优先
    auto_execute: bool = False  # 是否自动执行
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    evidence: Optional[InstinctEvidence] = None  # 可以后续设置


class InstinctRegistry:
    """
    本能注册表

    管理所有本能规则
    """

    def __init__(self, storage_dir: Optional[Path] = None):
        if storage_dir is None:
            storage_dir = Path("leo_knowledge/instincts")

        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        self._instincts: Dict[str, Instinct] = {}
        self._load_builtins()
        self._load_learned()

    def _load_builtins(self):
        """加载内置本能"""
        builtins = [
            Instinct(
                id="bug_finder",
                name="Bug查找本能",
                description="当用户提到bug、错误、报错时自动触发调试流程",
                trigger_type="keyword",
                trigger_pattern="bug|错误|报错|exception|failed|error",
                action_skill="systematic_debugging",
                action_params={"deep": True},
                evidence=InstinctEvidence(
                    description="Bug报告应该触发系统性调试流程",
                    confidence=0.95,
                    source="builtin",
                    examples=["程序报错了", "有个bug", "执行失败"]
                ),
                priority=8
            ),
            Instinct(
                id="security_guard",
                name="安全守卫本能",
                description="当输入包含敏感信息时自动触发安全扫描",
                trigger_type="keyword",
                trigger_pattern="密码|token|api[_-]?key|secret|password|credential",
                action_skill="security_scan",
                action_params={"quick": True},
                evidence=InstinctEvidence(
                    description="敏感信息处理需要安全检查",
                    confidence=0.9,
                    source="builtin",
                    examples=["帮我写个登录函数", "使用token认证", "设置password"]
                ),
                priority=9,
                auto_execute=False
            ),
            Instinct(
                id="refactor_trigger",
                name="重构本能",
                description="当用户提到重构或优化时触发代码审查",
                trigger_type="keyword",
                trigger_pattern="重构|refactor|优化|optimize|improve|clean",
                action_skill="code_reviewer",
                evidence=InstinctEvidence(
                    description="重构前应先进行代码审查",
                    confidence=0.85,
                    source="builtin",
                    examples=["重构这段代码", "优化一下性能", "清理旧代码"]
                ),
                priority=6
            ),
            Instinct(
                id="doc_generator",
                name="文档生成本能",
                description="当需要生成文档时自动触发文档生成",
                trigger_type="keyword",
                trigger_pattern="文档|doc|注释|comment|readme|说明",
                action_skill="documentation",
                evidence=InstinctEvidence(
                    description="代码变更应伴随文档更新",
                    confidence=0.8,
                    source="builtin",
                    examples=["生成文档", "写readme", "添加注释"]
                ),
                priority=5
            ),
            Instinct(
                id="test_runner",
                name="测试运行本能",
                description="当提到测试时自动运行测试套件",
                trigger_type="keyword",
                trigger_pattern="测试|test|测一下|单元测试|pytest",
                action_skill="test_runner",
                evidence=InstinctEvidence(
                    description="代码变更后应运行测试",
                    confidence=0.9,
                    source="builtin",
                    examples=["运行测试", "test一下", "单元测试"]
                ),
                priority=7,
                auto_execute=True
            ),
            Instinct(
                id="harness_audit",
                name="系统检查本能",
                description="当提到系统检查或健康检查时触发审计",
                trigger_type="keyword",
                trigger_pattern="健康检查|系统检查|harness|audit|检查",
                action_skill="harness_audit",
                evidence=InstinctEvidence(
                    description="定期系统检查有助于维护",
                    confidence=0.95,
                    source="builtin",
                    examples=["系统检查", "健康检查", "跑一下审计"]
                ),
                priority=4
            ),
            Instinct(
                id="security_scan_trigger",
                name="安全扫描本能",
                description="当提到安全扫描或漏洞时触发安全检查",
                trigger_type="keyword",
                trigger_pattern="安全扫描|漏洞|vulnerability|security|scan",
                action_skill="security_scan",
                evidence=InstinctEvidence(
                    description="发现潜在漏洞时应进行安全扫描",
                    confidence=0.95,
                    source="builtin",
                    examples=["安全扫描", "检查漏洞", "扫一下安全"]
                ),
                priority=8
            ),
            Instinct(
                id="chinese_context",
                name="中文上下文本能",
                description="检测到中文输入时启用中文处理模式",
                trigger_type="regex",
                trigger_pattern="^[\u4e00-\u9fa5]",
                action_skill="context_manager",
                action_params={"language": "zh-CN", "style": "direct"},
                evidence=InstinctEvidence(
                    description="中文用户偏好直接简洁的回答",
                    confidence=0.9,
                    source="builtin",
                    examples=["帮我写个函数", "这个怎么实现", "给我看看"]
                ),
                priority=10,
                auto_execute=True
            )
        ]

        for instinct in builtins:
            self._instincts[instinct.id] = instinct

    def _load_learned(self):
        """加载学习到的本能"""
        learned_file = self.storage_dir / "learned_instincts.json"
        if learned_file.exists():
            try:
                with open(learned_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    for item in data:
                        instinct = self._dict_to_instinct(item)
                        self._instincts[instinct.id] = instinct
            except Exception as e:
                logger.warning(f"加载学习本能失败: {e}")

    def _save_learned(self):
        """保存学习到的本能"""
        learned_file = self.storage_dir / "learned_instincts.json"
        learned = [
            i.__dict__ for i in self._instincts.values()
            if i.evidence.source == "learned"
        ]
        try:
            with open(learned_file, "w", encoding="utf-8") as f:
                json.dump(learned, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"保存本能失败: {e}")

    def _dict_to_instinct(self, d: Dict) -> Instinct:
        """字典转Instinct"""
        evidence = d.get("evidence", {})
        if isinstance(evidence, dict):
            evidence = InstinctEvidence(**evidence)
        d["evidence"] = evidence
        return Instinct(**d)

    def list_instincts(self, enabled_only: bool = True) -> List[Instinct]:
        """列出所有本能"""
        instincts = list(self._instincts.values())
        if enabled_only:
            instincts = [i for i in instincts if i.enabled]
        return sorted(instincts, key=lambda x: x.priority, reverse=True)

    def get_instinct(self, instinct_id: str) -> Optional[Instinct]:
        """获取本能"""
        return self._instincts.get(instinct_id)

    def match(self, user_input: str) -> List[tuple[Instinct, float]]:
        """
        匹配本能

        Args:
            user_input: 用户输入

        Returns:
            匹配的本能列表，按置信度排序
        """
        matches = []

        for instinct in self._instincts.values():
            if not instinct.enabled:
                continue

            confidence = self._calculate_match(instinct, user_input)
            if confidence > 0:
                matches.append((instinct, confidence))

        # 按置信度排序
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches

    def _calculate_match(self, instinct: Instinct, user_input: str) -> float:
        """计算匹配度"""
        if instinct.trigger_type == "keyword":
            pattern = instinct.trigger_pattern.lower()
            input_lower = user_input.lower()
            if re.search(pattern, input_lower, re.IGNORECASE):
                # 关键词匹配
                return 0.5 + 0.3 * min(len(re.findall(pattern, input_lower, re.IGNORECASE)) / 2, 1)
            return 0.0

        elif instinct.trigger_type == "regex":
            try:
                if re.search(instinct.trigger_pattern, user_input):
                    return 0.9
            except:
                pass
            return 0.0

        elif instinct.trigger_type == "semantic":
            # 简化版语义匹配 - 基于关键词重叠
            keywords = instinct.trigger_pattern.split("|")
            matches = sum(1 for kw in keywords if kw.lower() in user_input.lower())
            if matches > 0:
                return min(0.5 + matches * 0.15, 0.95)
            return 0.0

        return 0.0

    def learn(
        self,
        name: str,
        trigger_pattern: str,
        action_skill: str,
        description: str = "",
        examples: Optional[List[str]] = None
    ) -> Instinct:
        """
        学习新本能

        从用户行为中学习新的本能规则
        """
        instinct_id = hashlib.md5(name.encode()).hexdigest()[:8]

        instinct = Instinct(
            id=instinct_id,
            name=name,
            description=description or f"自动学习的本能: {name}",
            trigger_type="keyword",
            trigger_pattern=trigger_pattern,
            action_skill=action_skill,
            evidence=InstinctEvidence(
                description=description,
                confidence=0.7,  # 学习的本能初始置信度较低
                source="learned",
                examples=examples or []
            )
        )

        self._instincts[instinct_id] = instinct
        self._save_learned()

        return instinct

    def enable(self, instinct_id: str):
        """启用本能"""
        if instinct_id in self._instincts:
            self._instincts[instinct_id].enabled = True
            self._save_learned()

    def disable(self, instinct_id: str):
        """禁用本能"""
        if instinct_id in self._instincts:
            self._instincts[instinct_id].enabled = False
            self._save_learned()


class InstinctsSkill(BaseSkill):
    """
    Instincts Skill

    提供本能系统的统一接口
    """

    _registry: Optional[InstinctRegistry] = None

    def __init__(self):
        if InstinctsSkill._registry is None:
            InstinctsSkill._registry = InstinctRegistry()

    @property
    def name(self) -> str:
        return "instincts"

    @property
    def description(self) -> str:
        return "AI Agent本能系统 - 模式匹配自动触发"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行本能操作

        Actions:
            list: 列出所有本能
            show: 显示本能详情
            match: 测试匹配
            learn: 学习新本能
            enable: 启用本能
            disable: 禁用本能
        """
        if action == "list":
            return self._list_instincts()
        elif action == "show":
            return self._show_instinct(kwargs.get("name"))
        elif action == "match":
            return self._match_instinct(kwargs.get("input", ""))
        elif action == "learn":
            return self._learn_instinct(**kwargs)
        elif action == "enable":
            self._registry.enable(kwargs.get("name", ""))
            return SkillResult.ok(message=f"本能已启用: {kwargs.get('name')}")
        elif action == "disable":
            self._registry.disable(kwargs.get("name", ""))
            return SkillResult.ok(message=f"本能已禁用: {kwargs.get('name')}")
        else:
            return self._list_instincts()

    def _list_instincts(self) -> SkillResult:
        """列出所有本能"""
        instincts = self._registry.list_instincts()

        return SkillResult.ok(
            data={
                "instincts": [
                    {
                        "id": i.id,
                        "name": i.name,
                        "description": i.description,
                        "trigger_type": i.trigger_type,
                        "trigger_pattern": i.trigger_pattern,
                        "action_skill": i.action_skill,
                        "priority": i.priority,
                        "enabled": i.enabled,
                        "auto_execute": i.auto_execute
                    }
                    for i in instincts
                ],
                "total": len(instincts)
            },
            message=f"共 {len(instincts)} 个本能"
        )

    def _show_instinct(self, instinct_id: str) -> SkillResult:
        """显示本能详情"""
        instinct = self._registry.get_instinct(instinct_id)
        if not instinct:
            return SkillResult.fail(f"本能不存在: {instinct_id}")

        return SkillResult.ok(
            data={
                "instinct": {
                    "id": instinct.id,
                    "name": instinct.name,
                    "description": instinct.description,
                    "trigger_type": instinct.trigger_type,
                    "trigger_pattern": instinct.trigger_pattern,
                    "action_skill": instinct.action_skill,
                    "action_params": instinct.action_params,
                    "evidence": instinct.evidence.__dict__,
                    "priority": instinct.priority,
                    "enabled": instinct.enabled,
                    "auto_execute": instinct.auto_execute,
                    "created_at": instinct.created_at
                }
            }
        )

    def _match_instinct(self, user_input: str) -> SkillResult:
        """测试匹配"""
        matches = self._registry.match(user_input)

        return SkillResult.ok(
            data={
                "input": user_input,
                "matches": [
                    {
                        "id": i.id,
                        "name": i.name,
                        "confidence": round(c, 3),
                        "action_skill": i.action_skill,
                        "auto_execute": i.auto_execute
                    }
                    for i, c in matches[:5]
                ],
                "matched_count": len(matches)
            },
            message=f"匹配到 {len(matches)} 个本能"
        )

    def _learn_instinct(self, **kwargs) -> SkillResult:
        """学习新本能"""
        try:
            instinct = self._registry.learn(
                name=kwargs.get("name", ""),
                trigger_pattern=kwargs.get("pattern", ""),
                action_skill=kwargs.get("skill", ""),
                description=kwargs.get("description", ""),
                examples=kwargs.get("examples", [])
            )
            return SkillResult.ok(
                data={"instinct_id": instinct.id},
                message=f"已学习新本能: {instinct.name}"
            )
        except Exception as e:
            return SkillResult.fail(f"学习失败: {e}")

    def get_actions(self) -> List[str]:
        return ["default", "list", "show", "match", "learn", "enable", "disable"]


# 全局注册表
_registry: Optional[InstinctRegistry] = None


def get_instinct_registry() -> InstinctRegistry:
    """获取本能注册表"""
    global _registry
    if _registry is None:
        _registry = InstinctRegistry()
    return _registry


def match_input(user_input: str) -> List[tuple[Instinct, float]]:
    """快速匹配输入"""
    return get_instinct_registry().match(user_input)


def get_triggered_skill(user_input: str) -> Optional[tuple[str, Dict]]:
    """获取应触发的技能"""
    matches = match_input(user_input)
    for instinct, confidence in matches:
        if confidence >= 0.5:
            return (instinct.action_skill, instinct.action_params, confidence)
    return None


__all__ = [
    "InstinctsSkill",
    "InstinctRegistry",
    "Instinct",
    "InstinctEvidence",
    "TriggerType",
    "get_instinct_registry",
    "match_input",
    "get_triggered_skill"
]