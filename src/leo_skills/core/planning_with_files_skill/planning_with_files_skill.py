# -*- coding: utf-8 -*-
"""
planning_with_files_skill - 持久化规划核心技能

Manus风格的持久化规划技能。通过三个Markdown文件（task_plan.md、findings.md、progress.md）
实现任务规划、发现记录和进度跟踪。适用于复杂多步骤任务、研究项目或需要>5次工具调用的任务。

核心理念：Context Window = RAM（易失、有限），Filesystem = Disk（持久、无限）
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass, field


class PhaseStatus(Enum):
    """阶段状态"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETE = "complete"
    BLOCKED = "blocked"


@dataclass
class Phase:
    """任务阶段"""
    name: str
    description: str
    status: PhaseStatus = PhaseStatus.PENDING
    tasks: List[Dict[str, Any]] = field(default_factory=list)
    notes: str = ""


@dataclass
class PlanningResult:
    """规划结果"""
    status: str
    message: str
    files_created: List[str] = field(default_factory=list)
    files_updated: List[str] = field(default_factory=list)
    error: Optional[str] = None


class PlanningWithFilesSkill:
    """
    持久化规划技能 - 上下文工程基础设施

    功能：
    - 创建/管理 task_plan.md（任务计划）
    - 创建/管理 findings.md（研究发现）
    - 创建/管理 progress.md（进度日志）
    - 阶段跟踪和状态更新
    - 错误记录和知识积累
    """

    def __init__(self, base_path: str = "."):
        self.name = "planning_with_files_skill"
        self.version = "1.0.0"
        self.description = "持久化规划核心技能 - Context Engineering基础设施"
        self.base_path = Path(base_path)
        self.templates_dir = Path(__file__).parent / "templates"

    def execute(self, **kwargs) -> Dict[str, Any]:
        """
        执行技能主入口

        Args:
            action: 动作类型 (init/update_phase/add_finding/log_progress/complete)
            task_description: 任务描述
            phase_name: 阶段名称
            phase_status: 阶段状态
            finding: 研究发现
            progress_entry: 进度条目
            work_dir: 工作目录

        Returns:
            Dict 包含执行结果
        """
        action = kwargs.get("action", "init")
        work_dir = Path(kwargs.get("work_dir", self.base_path))

        try:
            if action == "init":
                result = self.initialize_planning(
                    task_description=kwargs.get("task_description", "未命名任务"),
                    work_dir=work_dir
                )
            elif action == "update_phase":
                result = self.update_phase(
                    phase_name=kwargs.get("phase_name", ""),
                    status=kwargs.get("phase_status", PhaseStatus.IN_PROGRESS.value),
                    notes=kwargs.get("notes", ""),
                    work_dir=work_dir
                )
            elif action == "add_finding":
                result = self.add_finding(
                    category=kwargs.get("category", "研究发现"),
                    content=kwargs.get("finding", ""),
                    work_dir=work_dir
                )
            elif action == "log_progress":
                result = self.log_progress(
                    entry=kwargs.get("progress_entry", ""),
                    work_dir=work_dir
                )
            elif action == "complete":
                result = self.mark_complete(
                    work_dir=work_dir,
                    summary=kwargs.get("summary", "")
                )
            else:
                return {
                    "status": "error",
                    "skill": self.name,
                    "error": f"Unknown action: {action}"
                }

            return {
                "status": result.status,
                "skill": self.name,
                "action": action,
                "result": result
            }

        except Exception as e:
            return {
                "status": "error",
                "skill": self.name,
                "action": action,
                "error": str(e)
            }

    def initialize_planning(
        self,
        task_description: str,
        work_dir: Optional[Path] = None
    ) -> PlanningResult:
        """
        初始化规划系统 - 创建三个核心文件

        Args:
            task_description: 任务描述
            work_dir: 工作目录

        Returns:
            PlanningResult 初始化结果
        """
        work_dir = work_dir or self.base_path
        work_dir = Path(work_dir)
        work_dir.mkdir(parents=True, exist_ok=True)

        files_created = []

        # 创建 task_plan.md
        task_plan_path = work_dir / "task_plan.md"
        if not task_plan_path.exists():
            task_plan_content = self._generate_task_plan(task_description)
            task_plan_path.write_text(task_plan_content, encoding="utf-8")
            files_created.append(str(task_plan_path))

        # 创建 findings.md
        findings_path = work_dir / "findings.md"
        if not findings_path.exists():
            findings_content = self._load_template("findings.md")
            findings_path.write_text(findings_content, encoding="utf-8")
            files_created.append(str(findings_path))

        # 创建 progress.md
        progress_path = work_dir / "progress.md"
        if not progress_path.exists():
            progress_content = self._generate_progress_log()
            progress_path.write_text(progress_content, encoding="utf-8")
            files_created.append(str(progress_path))

        return PlanningResult(
            status="success",
            message=f"规划系统初始化完成，创建了 {len(files_created)} 个文件",
            files_created=files_created
        )

    def update_phase(
        self,
        phase_name: str,
        status: str,
        notes: str = "",
        work_dir: Optional[Path] = None
    ) -> PlanningResult:
        """
        更新阶段状态

        Args:
            phase_name: 阶段名称
            status: 新状态
            notes: 备注
            work_dir: 工作目录

        Returns:
            PlanningResult 更新结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        task_plan_path = work_dir / "task_plan.md"

        if not task_plan_path.exists():
            return PlanningResult(
                status="error",
                message="task_plan.md 不存在，请先初始化规划系统",
                error="File not found"
            )

        content = task_plan_path.read_text(encoding="utf-8")

        # 更新当前阶段
        content = self._update_current_phase(content, phase_name)

        # 更新阶段状态
        content = self._update_phase_status(content, phase_name, status)

        # 添加备注
        if notes:
            content = self._add_phase_notes(content, phase_name, notes)

        task_plan_path.write_text(content, encoding="utf-8")

        return PlanningResult(
            status="success",
            message=f"阶段 '{phase_name}' 状态更新为 '{status}'",
            files_updated=[str(task_plan_path)]
        )

    def add_finding(
        self,
        category: str,
        content: str,
        work_dir: Optional[Path] = None
    ) -> PlanningResult:
        """
        添加研究发现

        Args:
            category: 发现类别
            content: 发现内容
            work_dir: 工作目录

        Returns:
            PlanningResult 添加结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        findings_path = work_dir / "findings.md"

        if not findings_path.exists():
            return PlanningResult(
                status="error",
                message="findings.md 不存在，请先初始化规划系统",
                error="File not found"
            )

        findings_content = findings_path.read_text(encoding="utf-8")

        # 添加新发现
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_finding = f"\n### {category} [{timestamp}]\n{content}\n"

        # 插入到研究发现部分
        if "## 研究发现" in findings_content:
            findings_content = findings_content.replace(
                "## 研究发现",
                f"## 研究发现\n{new_finding}"
            )
        else:
            findings_content += new_finding

        findings_path.write_text(findings_content, encoding="utf-8")

        return PlanningResult(
            status="success",
            message="研究发现已记录",
            files_updated=[str(findings_path)]
        )

    def log_progress(
        self,
        entry: str,
        work_dir: Optional[Path] = None
    ) -> PlanningResult:
        """
        记录进度日志

        Args:
            entry: 进度条目
            work_dir: 工作目录

        Returns:
            PlanningResult 记录结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path
        progress_path = work_dir / "progress.md"

        if not progress_path.exists():
            return PlanningResult(
                status="error",
                message="progress.md 不存在，请先初始化规划系统",
                error="File not found"
            )

        progress_content = progress_path.read_text(encoding="utf-8")

        # 添加新进度
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        new_entry = f"\n#### [{timestamp}]\n- {entry}\n"

        # 插入到第一个阶段的操作记录中
        if "- 执行的操作:" in progress_content:
            progress_content = progress_content.replace(
                "- 执行的操作:",
                f"- 执行的操作:{new_entry}",
                1
            )
        else:
            progress_content += new_entry

        progress_path.write_text(progress_content, encoding="utf-8")

        return PlanningResult(
            status="success",
            message="进度已记录",
            files_updated=[str(progress_path)]
        )

    def mark_complete(
        self,
        work_dir: Optional[Path] = None,
        summary: str = ""
    ) -> PlanningResult:
        """
        标记任务完成

        Args:
            work_dir: 工作目录
            summary: 完成总结

        Returns:
            PlanningResult 标记结果
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        # 更新所有阶段为完成
        task_plan_path = work_dir / "task_plan.md"
        if task_plan_path.exists():
            content = task_plan_path.read_text(encoding="utf-8")
            content = content.replace(
                "## 当前阶段\nPhase 1",
                "## 当前阶段\n✅ 已完成"
            )

            # 添加完成总结
            if summary:
                content += f"\n\n## 完成总结\n{summary}\n"

            task_plan_path.write_text(content, encoding="utf-8")

        return PlanningResult(
            status="success",
            message="任务已标记为完成",
            files_updated=[str(task_plan_path)] if task_plan_path.exists() else []
        )

    def _load_template(self, template_name: str) -> str:
        """加载模板文件"""
        template_path = self.templates_dir / template_name
        if template_path.exists():
            return template_path.read_text(encoding="utf-8")
        return ""

    def _generate_task_plan(self, task_description: str) -> str:
        """生成任务计划内容"""
        return f"""# 任务计划: {task_description}

## 目标
完成任务: {task_description}

## 当前阶段
Phase 1

## 阶段列表

### Phase 1: 需求与发现
- [ ] 理解用户意图
- [ ] 识别约束和需求
- [ ] 在 findings.md 中记录发现
- **状态:** in_progress

### Phase 2: 规划与结构
- [ ] 定义技术方案
- [ ] 创建项目结构（如需要）
- [ ] 记录决策及理由
- **状态:** pending

### Phase 3: 实施
- [ ] 按计划逐步执行
- [ ] 执行前先将代码写入文件
- [ ] 增量测试
- **状态:** pending

### Phase 4: 测试与验证
- [ ] 验证所有需求已满足
- [ ] 在 progress.md 中记录测试结果
- [ ] 修复发现的问题
- **状态:** pending

### Phase 5: 交付
- [ ] 审查所有输出文件
- [ ] 确保交付物完整
- [ ] 交付给用户
- **状态:** pending

## 关键问题
1. [待回答的问题]
2. [待回答的问题]

## 已做决策
| 决策 | 理由 |
|------|------|
|      |      |

## 遇到的错误
| 错误 | 尝试次数 | 解决方案 |
|------|----------|----------|
|      | 1        |          |

## 备注
- 进度更新：pending → in_progress → complete
- 重大决策前重读此计划（注意力操控）
- 记录所有错误 - 它们帮助避免重复

---
*创建时间: {datetime.now().strftime("%Y-%m-%d %H:%M")}*
"""

    def _generate_progress_log(self) -> str:
        """生成进度日志内容"""
        return f"""# 进度日志

## 会话: {datetime.now().strftime("%Y-%m-%d")}

### Phase 1: 需求与发现
- **状态:** in_progress
- **开始时间:** {datetime.now().strftime("%H:%M")}
- 执行的操作:
  -
- 创建/修改的文件:
  -

### Phase 2: 规划与结构
- **状态:** pending
- 执行的操作:
  -
- 创建/修改的文件:
  -

## 测试结果
| 测试 | 输入 | 预期 | 实际 | 状态 |
|------|------|------|------|------|
|      |      |      |      |      |

## 错误日志
<!-- 保留所有错误 - 它们帮助避免重复 -->
| 时间戳 | 错误 | 尝试次数 | 解决方案 |
|--------|------|----------|----------|
|        |      | 1        |          |

## 5问题重启检查
<!-- 如果你能回答这些，上下文是可靠的 -->
| 问题 | 答案 |
|------|------|
| 我在哪里？ | Phase 1 |
| 我要去哪里？ | 剩余阶段 |
| 目标是什么？ | 见 task_plan.md |
| 我学到了什么？ | 见 findings.md |
| 我做了什么？ | 见上文 |

---
*每完成一个阶段或遇到错误后更新*
"""

    def _update_current_phase(self, content: str, phase_name: str) -> str:
        """更新当前阶段"""
        # 更新 "## 当前阶段" 部分
        pattern = r"## 当前阶段\n.+?(?=\n## |\Z)"
        replacement = f"## 当前阶段\n{phase_name}\n"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return content

    def _update_phase_status(self, content: str, phase_name: str, status: str) -> str:
        """更新阶段状态"""
        # 查找阶段并更新状态
        pattern = rf"(### {re.escape(phase_name)}.*?- \*\*状态:\*\*) \w+"
        replacement = rf"\1 {status}"
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        return content

    def _add_phase_notes(self, content: str, phase_name: str, notes: str) -> str:
        """添加阶段备注"""
        timestamp = datetime.now().strftime("%H:%M")
        note_line = f"\n- [{timestamp}] {notes}"

        # 在阶段末尾添加备注
        pattern = rf"(### {re.escape(phase_name)}.*?)(?=\n### |\Z)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            section = match.group(1)
            updated_section = section.rstrip() + note_line + "\n"
            content = content.replace(section, updated_section)

        return content

    def read_planning_files(
        self,
        work_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """
        读取所有规划文件

        Args:
            work_dir: 工作目录

        Returns:
            Dict 包含所有文件内容
        """
        work_dir = Path(work_dir) if work_dir else self.base_path

        result = {}

        for filename in ["task_plan.md", "findings.md", "progress.md"]:
            filepath = work_dir / filename
            if filepath.exists():
                result[filename] = filepath.read_text(encoding="utf-8")
            else:
                result[filename] = None

        return result

    def get_capabilities(self) -> Dict[str, Any]:
        """获取技能能力信息"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "actions": ["init", "update_phase", "add_finding", "log_progress", "complete"],
            "files": ["task_plan.md", "findings.md", "progress.md"]
        }


# 向后兼容
PLANNING_Skill = PlanningWithFilesSkill


def main():
    """入口函数 - 演示用法"""
    import tempfile

    print("=" * 60)
    print("Planning With Files Skill - 演示")
    print("=" * 60)

    # 创建临时目录用于演示
    with tempfile.TemporaryDirectory() as tmpdir:
        skill = PlanningWithFilesSkill(base_path=tmpdir)

        # 演示1: 初始化规划系统
        print("\n1. 初始化规划系统")
        print("-" * 40)
        result = skill.initialize_planning(
            task_description="开发一个AI文本生成器"
        )
        print(f"状态: {result.status}")
        print(f"消息: {result.message}")
        print(f"创建的文件: {result.files_created}")

        # 演示2: 更新阶段状态
        print("\n2. 更新阶段状态")
        print("-" * 40)
        result = skill.update_phase(
            phase_name="Phase 1: 需求与发现",
            status="complete",
            notes="已完成需求分析"
        )
        print(f"状态: {result.status}")
        print(f"消息: {result.message}")

        # 演示3: 添加研究发现
        print("\n3. 添加研究发现")
        print("-" * 40)
        result = skill.add_finding(
            category="技术选型",
            content="选择 Claude API 作为文本生成引擎，因为质量和稳定性更好"
        )
        print(f"状态: {result.status}")
        print(f"消息: {result.message}")

        # 演示4: 记录进度
        print("\n4. 记录进度")
        print("-" * 40)
        result = skill.log_progress(
            entry="完成了需求分析和技术选型"
        )
        print(f"状态: {result.status}")
        print(f"消息: {result.message}")

        # 演示5: 读取规划文件
        print("\n5. 读取规划文件")
        print("-" * 40)
        files = skill.read_planning_files()
        for filename, content in files.items():
            if content:
                lines = content.split('\n')[:3]
                print(f"{filename}: {' | '.join(lines)}")

    print("\n" + "=" * 60)
    print("演示完成！")
    print("=" * 60)

    return skill


if __name__ == "__main__":
    main()
