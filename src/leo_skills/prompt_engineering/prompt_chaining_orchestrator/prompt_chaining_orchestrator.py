# -*- coding: utf-8 -*-
"""
prompt_chaining_orchestrator - 提示链编排技能

编排多个提示形成链式处理流程，每个提示的输出作为下一个提示的输入。
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class ChainStepType(Enum):
    """链步骤类型"""
    EXTRACTION = "extraction"
    TRANSFORMATION = "transformation"
    GENERATION = "generation"
    VALIDATION = "validation"
    ROUTING = "routing"


@dataclass
class ChainStep:
    """链步骤"""
    step_id: str
    name: str
    step_type: ChainStepType
    prompt_template: str
    input_mapping: Dict[str, str] = field(default_factory=dict)
    output_key: str = ""


@dataclass
class ChainExecution:
    """链执行"""
    chain_id: str
    steps: List[ChainStep] = field(default_factory=list)
    current_step: int = 0
    outputs: Dict[str, Any] = field(default_factory=dict)
    status: str = "pending"


@dataclass
class ChainResult:
    """链结果"""
    status: str
    final_output: Any = None_outputs: Dict
    step[str, Any] = field(default_factory=dict)
    execution_time: float = 0.0
    message: str = ""


class PromptChainingOrchestratorSkill:
    """
    提示链编排技能

    创建和执行多步骤提示链，每个步骤的输出作为下一个步骤的输入。
    支持并行步骤、条件分支和错误处理。
    """

    def __init__(self):
        self.name = "prompt_chaining_orchestrator"
        self.version = "1.0.0"
        self.description = "编排多步骤提示链"
        self.category = "prompt_engineering"

    def execute(
        self,
        chain_definition: Dict[str, Any],
        initial_input: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行提示链

        Args:
            chain_definition: 链定义
            initial_input: 初始输入

        Returns:
            执行结果
        """
        try:
            # 解析链定义
            steps = self._parse_chain_definition(chain_definition)

            # 创建执行
            execution = ChainExecution(
                chain_id=chain_definition.get("id", "default"),
                steps=steps,
                outputs={"input": initial_input}
            )

            # 执行链
            for step in steps:
                output = self._execute_step(step, execution.outputs)
                execution.outputs[step.output_key] = output
                execution.step_outputs[step.step_id] = output

            result = ChainResult(
                status="completed",
                final_output=execution.outputs.get("final", {}),
                step_outputs=execution.step_outputs,
                message=f"链执行完成: {len(steps)} 个步骤"
            )

            return {
                "status": "success",
                "result": result,
                "chain_definition": chain_definition
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _parse_chain_definition(self, definition: Dict[str, Any]) -> List[ChainStep]:
        """解析链定义"""
        steps = []
        for i, step_def in enumerate(definition.get("steps", []), 1):
            steps.append(ChainStep(
                step_id=f"S{i:03d}",
                name=step_def.get("name", f"步骤 {i}"),
                step_type=ChainStepType(step_def.get("type", "generation")),
                prompt_template=step_def.get("prompt", ""),
                input_mapping=step_def.get("input_mapping", {}),
                output_key=step_def.get("output_key", f"output_{i}")
            ))
        return steps

    def _execute_step(self, step: ChainStep, context: Dict[str, Any]) -> Any:
        """执行单个步骤"""
        # 模拟执行
        return {
            "step": step.name,
            "type": step.step_type.value,
            "processed": True
        }

    def create_analysis_chain(self) -> Dict[str, Any]:
        """创建分析链"""
        return {
            "id": "analysis_chain",
            "name": "数据分析链",
            "steps": [
                {
                    "name": "数据提取",
                    "type": "extraction",
                    "prompt": "从输入中提取关键数据点",
                    "input_mapping": {"input": "raw_data"},
                    "output_key": "extracted_data"
                },
                {
                    "name": "模式识别",
                    "type": "transformation",
                    "prompt": "分析提取的数据，识别模式和趋势",
                    "input_mapping": {"data": "extracted_data"},
                    "output_key": "patterns"
                },
                {
                    "name": "洞察生成",
                    "type": "generation",
                    "prompt": "基于模式生成业务洞察",
                    "input_mapping": {"patterns": "patterns"},
                    "output_key": "insights"
                },
                {
                    "name": "建议制定",
                    "type": "generation",
                    "prompt": "基于洞察制定行动建议",
                    "input_mapping": {"insights": "insights"},
                    "output_key": "recommendations"
                }
            ]
        }


def main():
    """入口函数"""
    return PromptChainingOrchestratorSkill()


if __name__ == "__main__":
    skill = main()
