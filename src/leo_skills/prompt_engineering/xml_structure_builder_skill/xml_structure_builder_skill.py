# -*- coding: utf-8 -*-
"""
xml_structure_builder - XML结构构建技能

使用XML标签结构化复杂提示，提高模型输出的组织性和一致性。
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class XMLTag:
    """XML标签"""
    name: str
    content: str
    attributes: Dict[str, str] = field(default_factory=dict)
    children: List["XMLTag"] = field(default_factory=list)


@dataclass
class XMLStructure:
    """XML结构"""
    root: XMLTag
    template: str = ""


class XmlStructureBuilderSkill:
    """
    XML结构构建技能

    使用XML标签结构化复杂提示：
    - <task> 任务定义
    - <context> 上下文信息
    - <constraints> 约束条件
    - <output_format> 输出格式
    - <examples> 示例
    """

    def __init__(self):
        self.name = "xml_structure_builder_skill"
        self.version = "1.0.0"
        self.description = "使用XML结构化提示"
        self.category = "prompt_engineering"

    def execute(
        self,
        task: str,
        context: str = "",
        constraints: List[str] = None,
        output_format: str = "",
        examples: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        执行XML结构构建

        Args:
            task: 任务描述
            context: 上下文信息
            constraints: 约束条件
            output_format: 输出格式
            examples: 示例

        Returns:
            结构化提示
        """
        try:
            # 构建XML结构
            root = XMLTag(
                name="prompt",
                content="",
                children=[
                    XMLTag(name="task", content=task),
                ]
            )

            if context:
                root.children.append(XMLTag(name="context", content=context))

            if constraints:
                constraints_tag = XMLTag(name="constraints", content="")
                for c in constraints:
                    constraints_tag.children.append(XMLTag(name="rule", content=c))
                root.children.append(constraints_tag)

            if output_format:
                root.children.append(XMLTag(name="output_format", content=output_format))

            if examples:
                examples_tag = XMLTag(name="examples", content="")
                for i, ex in enumerate(examples, 1):
                    examples_tag.children.append(XMLTag(name="example", content=ex, attributes={"id": str(i)}))
                root.children.append(examples_tag)

            # 生成XML字符串
            xml_output = self._to_xml(root)

            return {
                "status": "success",
                "xml_structure": xml_output,
                "tags_used": ["prompt", "task", "context", "constraints", "output_format", "examples"]
            }

        except Exception as e:
            return {
                "status": "error",
                "error": str(e),
                "skill": self.name
            }

    def _to_xml(self, tag: XMLTag, indent: int = 0) -> str:
        """转换为XML字符串"""
        spaces = "  " * indent
        attrs = "".join(f' {k}="{v}"' for k, v in tag.attributes.items())

        if tag.children:
            lines = [f"{spaces}<{tag.name}{attrs}>"]
            for child in tag.children:
                lines.append(self._to_xml(child, indent + 1))
            lines.append(f"{spaces}</{tag.name}>")
            return "\n".join(lines)
        else:
            return f"{spaces}<{tag.name}{attrs}>{tag.content}</{tag.name}>"

    def create_analysis_prompt(self, data: str, analysis_type: str) -> str:
        """创建分析提示"""
        return f"""
<prompt>
  <task>分析以下{analysis_type}数据</task>
  <context>{data}</context>
  <constraints>
    <rule>提供详细的分析结果</rule>
    <rule>包含具体的数据支持</rule>
    <rule>给出可操作的建议</rule>
  </constraints>
  <output_format>
    <section name="summary">分析摘要</section>
    <section name="findings">关键发现</section>
    <section name="recommendations">建议</section>
  </output_format>
</prompt>
        """.strip()


def main():
    """入口函数"""
    return XmlStructureBuilderSkill()


if __name__ == "__main__":
    skill = main()

