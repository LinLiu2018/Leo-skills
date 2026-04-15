# -*- coding: utf-8 -*-
"""
TDD Workflow Skill
==================

测试驱动开发工作流
参考 ECC TDD Workflow

Author: Leo AI System
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from base import BaseSkill, SkillResult


class TDDPhase(Enum):
    """TDD阶段"""
    RED = "red"      # 写失败测试
    GREEN = "green"  # 写代码通过
    REFACTOR = "refactor"  # 重构


@dataclass
class TDDRecord:
    """TDD记录"""
    feature: str
    phase: str
    test_code: str = ""
    impl_code: str = ""
    passed: bool = False
    timestamp: str = ""


class TDDWorkflowSkill(BaseSkill):
    """
    TDD Workflow Skill

    测试驱动开发工作流
    """

    def __init__(self):
        super().__init__()
        self.current_phase = TDDPhase.RED
        self.current_feature = ""
        self.records: List[TDDRecord] = []

    @property
    def name(self) -> str:
        return "tdd_workflow"

    @property
    def description(self) -> str:
        return "测试驱动开发工作流 - Red/Green/Refactor循环"

    def execute(self, action: str = "default", **kwargs) -> SkillResult:
        """
        执行TDD操作

        Actions:
            start: 开始TDD会话
            red: 进入Red阶段(写测试)
            green: 进入Green阶段(写实现)
            refactor: 进入Refactor阶段
            status: 查看当前状态
            report: 生成TDD报告
        """
        if action == "start":
            return self._start_tdd(kwargs.get("feature", ""))
        elif action == "red":
            return self._phase_red(kwargs.get("test_code", ""), kwargs.get("description", ""))
        elif action == "green":
            return self._phase_green(kwargs.get("impl_code", ""))
        elif action == "refactor":
            return self._phase_refactor(kwargs.get("refactor_type", ""))
        elif action == "status":
            return self._status()
        elif action == "report":
            return self._generate_report()
        else:
            return self._status()

    def _start_tdd(self, feature: str) -> SkillResult:
        """开始TDD会话"""
        if not feature:
            return SkillResult.fail("请指定要开发的功能")

        self.current_feature = feature
        self.current_phase = TDDPhase.RED
        self.records = []

        guide = """
## TDD工作流启动: {feature}

### 当前阶段: RED (写失败的测试)

### 步骤:
1. 先写测试，只调用待实现的方法
2. 测试应该失败（因为方法不存在）
3. 运行测试确认失败

### 示例:
```python
def test_calculate_sum():
    # Arrange
    calculator = Calculator()

    # Act
    result = calculator.add(2, 3)

    # Assert
    assert result == 5  # 这会失败，因为方法未实现
```
""".format(feature=feature)

        return SkillResult.ok(
            data={
                "feature": feature,
                "phase": "RED",
                "guide": guide,
                "next_action": "使用 /tdd red <test_code> 提交测试代码"
            },
            message=f"TDD会话开始: {feature}"
        )

    def _phase_red(self, test_code: str, description: str) -> SkillResult:
        """Red阶段"""
        if not self.current_feature:
            return SkillResult.fail("请先使用 /tdd start <功能名> 开始TDD")

        if not test_code:
            return SkillResult.fail("请提供测试代码")

        # 记录
        record = TDDRecord(
            feature=self.current_feature,
            phase="RED",
            test_code=test_code,
            timestamp=datetime.now().isoformat()
        )
        self.records.append(record)

        self.current_phase = TDDPhase.GREEN

        guide = """
## RED阶段完成

### 测试代码:
```python
{test_code}
```

### 下一步: GREEN阶段

使用 `/tdd green <impl_code>` 提交实现代码

### GREEN阶段指南:
1. 写最小代码让测试通过
2. 不要过度设计
3. 通过测试即可停止
""".format(test_code=test_code)

        return SkillResult.ok(
            data={
                "phase": "GREEN",
                "guide": guide,
                "test_recorded": True
            },
            message="Red阶段完成，准备Green阶段"
        )

    def _phase_green(self, impl_code: str) -> SkillResult:
        """Green阶段"""
        if self.current_phase != TDDPhase.GREEN:
            return SkillResult.fail("当前不在Green阶段")

        if not impl_code:
            return SkillResult.fail("请提供实现代码")

        # 更新最后一条记录
        if self.records:
            self.records[-1].impl_code = impl_code

        self.current_phase = TDDPhase.REFACTOR

        guide = """
## GREEN阶段完成

### 实现代码:
```python
{impl_code}
```

### 下一步: REFACTOR阶段

使用 `/tdd refactor <type>` 进行重构

### 重构类型:
- extract: 提取重复代码
- rename: 重命名变量/函数
- optimize: 性能优化
- clarity: 提高可读性
""".format(impl_code=impl_code)

        return SkillResult.ok(
            data={
                "phase": "REFACTOR",
                "guide": guide
            },
            message="Green阶段完成，准备Refactor阶段"
        )

    def _phase_refactor(self, refactor_type: str) -> SkillResult:
        """Refactor阶段"""
        if self.current_phase != TDDPhase.REFACTOR:
            return SkillResult.fail("当前不在Refactor阶段")

        self.current_phase = TDDPhase.RED  # 重构完后回到Red

        guide = """
## REFACTOR阶段

### 重构类型: {refactor_type}

### 重构检查清单:
- [ ] 没有重复代码
- [ ] 命名清晰
- [ ] 函数单一职责
- [ ] 测试覆盖充分

### 重构后:
回到RED阶段，写下一个测试
使用 `/tdd red <test_code>` 继续
""".format(refactor_type=refactor_type)

        return SkillResult.ok(
            data={
                "phase": "RED",
                "guide": guide,
                "cycles_completed": len([r for r in self.records if r.phase == "REFACTOR"])
            },
            message=f"Refactor完成，返回RED阶段"
        )

    def _status(self) -> SkillResult:
        """查看当前状态"""
        return SkillResult.ok(
            data={
                "feature": self.current_feature,
                "phase": self.current_phase.value.upper(),
                "cycles": len(self.records),
                "records": [
                    {"phase": r.phase, "feature": r.feature, "timestamp": r.timestamp}
                    for r in self.records
                ]
            },
            message=f"当前: {self.current_feature or '无'} | 阶段: {self.current_phase.value.upper()}"
        )

    def _generate_report(self) -> SkillResult:
        """生成TDD报告"""
        if not self.records:
            return SkillResult.ok(
                data={"cycles": 0, "report": "暂无TDD记录"},
                message="无TDD记录"
            )

        phases = [r.phase for r in self.records]
        red_count = phases.count("RED")
        green_count = phases.count("GREEN")
        refactor_count = phases.count("REFACTOR")

        report = {
            "feature": self.current_feature,
            "total_cycles": len(self.records),
            "phases": {"red": red_count, "green": green_count, "refactor": refactor_count},
            "timeline": [
                {"phase": r.phase, "timestamp": r.timestamp}
                for r in self.records
            ]
        }

        return SkillResult.ok(
            data=report,
            message=f"TDD报告: {len(self.records)} 个阶段完成"
        )

    def get_actions(self) -> List[str]:
        return ["default", "start", "red", "green", "refactor", "status", "report"]


# 快捷函数
def start_tdd(feature: str) -> SkillResult:
    """快速开始TDD"""
    skill = TDDWorkflowSkill()
    return skill.execute(action="start", feature=feature)


if __name__ == "__main__":
    skill = TDDWorkflowSkill()
    print(skill.execute("status"))
