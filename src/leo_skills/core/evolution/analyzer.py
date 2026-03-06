# -*- coding: utf-8 -*-
"""
LLM 分析引擎

使用 LLM 进行深度经验分析
"""

import json
import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ...base import BaseSkill, SkillResult

# Prompt 模板
ANALYSIS_PROMPT = """
你是一个专业的代码进化分析师。请分析以下技能的经验数据：

## 经验数据
{experiences}

## 性能指标
{metrics}

## 执行日志
{logs}

请输出一个 JSON 对象，包含：
1. patterns: 发现的模式列表
2. root_cause: 根因分析
3. suggestions: 优化建议列表
4. priority: 优先级 (high/medium/low)
5. confidence: 分析置信度 (0-1)

输出格式：纯 JSON，不要其他内容
"""

FAILURE_ANALYSIS_PROMPT = """
你是一个专业的故障分析专家。请分析以下失败案例：

## 错误信息
{error_message}

## 错误堆栈
{stack_trace}

## 上下文
{context}

请输出一个 JSON 对象，包含：
1. error_type: 错误类型
2. root_cause: 根本原因
3. fix_suggestion: 修复建议
4. prevention: 预防措施

输出格式：纯 JSON，不要其他内容
"""

OPTIMIZATION_PROMPT = """
你是一个性能优化专家。请分析以下代码和性能数据：

## 技能代码路径
{skill_path}

## 性能指标
{metrics}

## 执行日志
{logs}

请输出一个 JSON 对象，包含：
1. bottlenecks: 性能瓶颈列表
2. optimization_suggestions: 优化建议列表
3. expected_improvement: 预期改进效果
4. risk_level: 风险等级 (low/medium/high)

输出格式：纯 JSON，不要其他内容
"""

CODE_IMPROVEMENT_PROMPT = """
你是一个代码改进专家。请根据以下分析结果生成代码改进方案：

## 当前代码
```python
{code}
```

## 需要改进的点
{improvements}

请输出一个 JSON 对象，包含：
1. new_code: 改进后的代码
2. changes: 变更说明列表
3. backward_compatible: 是否向后兼容 (true/false)
4. test_suggestions: 测试建议

输出格式：纯 JSON，不要其他内容
"""


@dataclass
class AnalysisResult:
    """分析结果"""
    patterns: List[str] = field(default_factory=list)
    root_cause: str = ""
    suggestions: List[str] = field(default_factory=list)
    priority: str = "medium"
    confidence: float = 0.5
    raw_response: str = ""

    def to_dict(self) -> Dict:
        return {
            "patterns": self.patterns,
            "root_cause": self.root_cause,
            "suggestions": self.suggestions,
            "priority": self.priority,
            "confidence": self.confidence,
        }


@dataclass
class FailureAnalysis:
    """失败分析结果"""
    error_type: str = ""
    root_cause: str = ""
    fix_suggestion: str = ""
    prevention: str = ""

    def to_dict(self) -> Dict:
        return {
            "error_type": self.error_type,
            "root_cause": self.root_cause,
            "fix_suggestion": self.fix_suggestion,
            "prevention": self.prevention,
        }


@dataclass
class OptimizationPlan:
    """优化方案"""
    bottlenecks: List[str] = field(default_factory=list)
    optimization_suggestions: List[str] = field(default_factory=list)
    expected_improvement: str = ""
    risk_level: str = "medium"

    def to_dict(self) -> Dict:
        return {
            "bottlenecks": self.bottlenecks,
            "optimization_suggestions": self.optimization_suggestions,
            "expected_improvement": self.expected_improvement,
            "risk_level": self.risk_level,
        }


class LLMAnalyzer:
    """
    LLM 分析引擎

    使用 LLM 进行深度分析：
    - 经验模式识别
    - 根因分析
    - 优化建议生成
    - 代码改进方案
    """

    def __init__(self, model: str = "default"):
        self.model = model
        self.llm = None
        self._init_llm()

    def _init_llm(self):
        """初始化 LLM"""
        try:
            # 尝试导入 LLM 适配器
            from leo_subagents.core.llm_adapter import LLMAdapter
            self.llm = LLMAdapter()
        except ImportError:
            print("[LLMAnalyzer] Warning: LLM adapter not available, using fallback")

    def analyze_experience(
        self,
        experiences: List[Dict],
        metrics: Optional[Dict] = None,
        logs: Optional[List[Dict]] = None
    ) -> AnalysisResult:
        """
        分析经验数据

        Args:
            experiences: 经验列表
            metrics: 性能指标
            logs: 执行日志

        Returns:
            分析结果
        """
        if not experiences:
            return AnalysisResult(
                root_cause="No experiences to analyze",
                confidence=0.0
            )

        # 格式化数据
        exp_text = self._format_experiences(experiences)
        metrics_text = self._format_metrics(metrics or {})
        logs_text = self._format_logs(logs or [])

        # 构建 prompt
        prompt = ANALYSIS_PROMPT.format(
            experiences=exp_text,
            metrics=metrics_text,
            logs=logs_text
        )

        # 调用 LLM
        if self.llm:
            try:
                response = self.llm.chat(prompt)
                return self._parse_analysis_response(response)
            except Exception as e:
                print(f"[LLMAnalyzer] LLM call failed: {e}")
                return self._fallback_analysis(experiences)

        # 回退分析
        return self._fallback_analysis(experiences)

    def analyze_failure(
        self,
        error: Exception,
        context: Optional[Dict] = None
    ) -> FailureAnalysis:
        """
        分析失败原因

        Args:
            error: 异常对象
            context: 上下文信息

        Returns:
            失败分析结果
        """
        error_message = str(error)
        stack_trace = ""
        if hasattr(error, "__traceback__"):
            import traceback
            stack_trace = "".join(traceback.format_tb(error.__traceback__))

        context_text = json.dumps(context or {}, indent=2, ensure_ascii=False)

        prompt = FAILURE_ANALYSIS_PROMPT.format(
            error_message=error_message,
            stack_trace=stack_trace,
            context=context_text
        )

        if self.llm:
            try:
                response = self.llm.chat(prompt)
                return self._parse_failure_response(response)
            except Exception as e:
                print(f"[LLMAnalyzer] LLM call failed: {e}")

        # 回退分析
        return self._simple_failure_analysis(error)

    def generate_optimization(
        self,
        skill_path: str,
        metrics: Dict,
        logs: Optional[List[Dict]] = None
    ) -> OptimizationPlan:
        """
        生成优化方案

        Args:
            skill_path: 技能路径
            metrics: 性能指标
            logs: 执行日志

        Returns:
            优化方案
        """
        # 读取技能代码
        code = self._read_skill_code(skill_path)

        metrics_text = self._format_metrics(metrics)
        logs_text = self._format_logs(logs or [])

        prompt = OPTIMIZATION_PROMPT.format(
            skill_path=skill_path,
            metrics=metrics_text,
            logs=logs_text
        )

        if self.llm:
            try:
                response = self.llm.chat(prompt)
                return self._parse_optimization_response(response)
            except Exception as e:
                print(f"[LLMAnalyzer] LLM call failed: {e}")

        # 回退分析
        return self._simple_optimization_analysis(metrics)

    def generate_code_improvement(
        self,
        code: str,
        improvements: List[str]
    ) -> Dict[str, Any]:
        """
        生成代码改进

        Args:
            code: 当前代码
            improvements: 改进点列表

        Returns:
            改进结果
        """
        improvements_text = "\n".join(f"- {imp}" for imp in improvements)

        prompt = CODE_IMPROVEMENT_PROMPT.format(
            code=code,
            improvements=improvements_text
        )

        if self.llm:
            try:
                response = self.llm.chat(prompt)
                return self._parse_code_improvement_response(response)
            except Exception as e:
                print(f"[LLMAnalyzer] LLM call failed: {e}")

        return {
            "status": "error",
            "message": "LLM not available"
        }

    # ========== 格式化方法 ==========

    def _format_experiences(self, experiences: List[Dict]) -> str:
        """格式化经验数据"""
        lines = []
        for i, exp in enumerate(experiences[-10:], 1):  # 最多10条
            tip = exp.get("tip", "")
            context = exp.get("context", "")
            success_count = exp.get("success_count", 0)
            failure_count = exp.get("failure_count", 0)

            lines.append(
                f"{i}. [{'成功' if success_count > failure_count else '失败'}] {tip}\n"
                f"   上下文: {context}\n"
                f"   成功: {success_count}, 失败: {failure_count}"
            )

        return "\n\n".join(lines) if lines else "无经验数据"

    def _format_metrics(self, metrics: Dict) -> str:
        """格式化指标数据"""
        if not metrics:
            return "无指标数据"

        lines = []
        for name, value in metrics.items():
            if isinstance(value, dict):
                lines.append(f"- {name}:")
                for k, v in value.items():
                    lines.append(f"  - {k}: {v}")
            else:
                lines.append(f"- {name}: {value}")

        return "\n".join(lines)

    def _format_logs(self, logs: List[Dict]) -> str:
        """格式化日志数据"""
        if not logs:
            return "无日志数据"

        lines = []
        for log in logs[-5:]:  # 最多5条
            level = log.get("level", "info")
            message = log.get("message", "")
            timestamp = log.get("timestamp", "")

            lines.append(f"- [{level}] {timestamp}: {message[:100]}")

        return "\n".join(lines)

    def _read_skill_code(self, skill_path: str) -> str:
        """读取技能代码"""
        base_path = Path("src/leo_skills")
        skill_dir = base_path / skill_path

        # 查找 Python 文件
        for py_file in skill_dir.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            try:
                return py_file.read_text(encoding="utf-8")
            except:
                pass

        return ""

    # ========== 解析方法 ==========

    def _parse_analysis_response(self, response: str) -> AnalysisResult:
        """解析分析响应"""
        try:
            # 提取 JSON
            json_str = self._extract_json(response)
            data = json.loads(json_str)

            return AnalysisResult(
                patterns=data.get("patterns", []),
                root_cause=data.get("root_cause", ""),
                suggestions=data.get("suggestions", []),
                priority=data.get("priority", "medium"),
                confidence=data.get("confidence", 0.5),
                raw_response=response
            )
        except Exception as e:
            print(f"[LLMAnalyzer] Parse failed: {e}")
            return AnalysisResult(
                root_cause="解析失败",
                confidence=0.0
            )

    def _parse_failure_response(self, response: str) -> FailureAnalysis:
        """解析失败分析响应"""
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)

            return FailureAnalysis(
                error_type=data.get("error_type", ""),
                root_cause=data.get("root_cause", ""),
                fix_suggestion=data.get("fix_suggestion", ""),
                prevention=data.get("prevention", "")
            )
        except Exception as e:
            print(f"[LLMAnalyzer] Parse failed: {e}")
            return FailureAnalysis()

    def _parse_optimization_response(self, response: str) -> OptimizationPlan:
        """解析优化响应"""
        try:
            json_str = self._extract_json(response)
            data = json.loads(json_str)

            return OptimizationPlan(
                bottlenecks=data.get("bottlenecks", []),
                optimization_suggestions=data.get("optimization_suggestions", []),
                expected_improvement=data.get("expected_improvement", ""),
                risk_level=data.get("risk_level", "medium")
            )
        except Exception as e:
            print(f"[LLMAnalyzer] Parse failed: {e}")
            return OptimizationPlan()

    def _parse_code_improvement_response(self, response: str) -> Dict:
        """解析代码改进响应"""
        try:
            json_str = self._extract_json(response)
            return json.loads(json_str)
        except Exception as e:
            print(f"[LLMAnalyzer] Parse failed: {e}")
            return {"status": "error", "message": str(e)}

    def _extract_json(self, text: str) -> str:
        """提取 JSON 字符串"""
        # 尝试直接解析
        text = text.strip()

        # 去除 markdown 代码块
        if "```" in text:
            # 提取 ```json 或 ``` 之间的内容
            match = re.search(r'```(?:json)?\s*(.*?)\s*```', text, re.DOTALL)
            if match:
                return match.group(1)

        # 查找 { } 包围的内容
        start = text.find('{')
        end = text.rfind('}')

        if start != -1 and end != -1:
            return text[start:end+1]

        return text

    # ========== 回退分析 ==========

    def _fallback_analysis(self, experiences: List[Dict]) -> AnalysisResult:
        """回退分析（无 LLM 时）"""
        # 简单统计
        success_count = sum(1 for e in experiences if e.get("success_count", 0) > e.get("failure_count", 0))
        failure_count = len(experiences) - success_count

        suggestions = []
        if failure_count > success_count:
            suggestions.append("建议检查失败经验，优化错误处理逻辑")
        if len(experiences) < 5:
            suggestions.append("建议收集更多经验数据后再分析")

        return AnalysisResult(
            root_cause="基于统计的简单分析",
            suggestions=suggestions,
            priority="medium" if failure_count > 0 else "low",
            confidence=0.3
        )

    def _simple_failure_analysis(self, error: Exception) -> FailureAnalysis:
        """简单失败分析"""
        error_type = type(error).__name__

        return FailureAnalysis(
            error_type=error_type,
            root_cause=f"发生 {error_type} 异常",
            fix_suggestion="建议查看异常堆栈跟踪定位问题",
            prevention="添加异常处理和日志记录"
        )

    def _simple_optimization_analysis(self, metrics: Dict) -> OptimizationPlan:
        """简单优化分析"""
        bottlenecks = []
        suggestions = []

        # 基于指标简单判断
        if "avg_duration" in metrics:
            avg = metrics["avg_duration"]
            if avg > 30000:  # 30秒
                bottlenecks.append("执行时间过长")
                suggestions.append("考虑添加缓存或优化查询")

        return OptimizationPlan(
            bottlenecks=bottlenecks,
            optimization_suggestions=suggestions,
            risk_level="low"
        )


# 全局实例
_global_analyzer: Optional[LLMAnalyzer] = None


def get_llm_analyzer() -> LLMAnalyzer:
    """获取全局 LLM 分析器"""
    global _global_analyzer
    if _global_analyzer is None:
        _global_analyzer = LLMAnalyzer()
    return _global_analyzer
