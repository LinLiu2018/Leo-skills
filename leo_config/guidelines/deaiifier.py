"""
去AI化内容处理器 (双模式版本)
========================
根据场景自动将AI生成的内容转换为合适的表达
支持创意模式(creative)和严谨模式(formal)
"""

import yaml
import re
import random
from pathlib import Path
from typing import Dict, List, Optional, Literal


class DeAIifier:
    """
    去AI化处理器 (双模式)
    ===================

    根据配置规则自动将AI生成的内容转换为合适的表达：
    - creative_mode: 创意模式，口语化、接地气、真人口吻
    - formal_mode: 严谨模式，客观、准确、拒绝AI幻想
    """

    def __init__(
        self,
        config_path: Optional[str] = None,
        mode: Literal["creative", "formal", "auto"] = "auto"
    ):
        """
        初始化处理器

        Args:
            config_path: 配置文件路径，默认使用项目内置配置
            mode: 去AI化模式
                - "creative": 创意模式，营销文案、短视频、直播
                - "formal": 严谨模式，技术文档、数据分析、正式报告
                - "auto": 自动根据技能名称选择模式
        """
        if config_path is None:
            current_file = Path(__file__)
            config_path = current_file.parent / "deaiification_guide.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.mode = mode
        self.creative_config = self.config.get('creative_mode', {})
        self.formal_config = self.config.get('formal_mode', {})
        self.skill_modes = self.config.get('skill_default_modes', {})

    def process(
        self,
        text: str,
        mode: Optional[Literal["creative", "formal"]] = None
    ) -> str:
        """
        处理文本，应用去AI化规则

        Args:
            text: 待处理的文本
            mode: 指定模式，如不指定则使用初始化时的模式

        Returns:
            处理后的文本
        """
        # 确定使用的模式
        effective_mode = mode or self._determine_mode()

        if effective_mode == "creative":
            return self._process_creative(text)
        else:
            return self._process_formal(text)

    def _determine_mode(self) -> str:
        """确定当前使用的模式"""
        if self.mode == "auto":
            # 默认使用创意模式
            return "creative"
        return self.mode

    def _process_creative(self, text: str) -> str:
        """
        创意模式处理
        让内容更像真人说话，口语化、接地气
        """
        # 1. 替换营销黑话
        text = self._replace_marketing_jargon(text)

        # 2. 替换过度绝对化表达
        text = self._replace_absolutes(text)

        # 3. 添加口语化元素
        text = self._add_colloquial_elements(text)

        # 4. 调整句式
        text = self._adjust_sentence_patterns(text)

        return text

    def _process_formal(self, text: str) -> str:
        """
        严谨模式处理
        拒绝AI幻想，确保内容客观准确
        """
        # 1. 替换夸大表达
        text = self._replace_exaggeration(text)

        # 2. 添加数据来源标注
        text = self._add_data_sources(text)

        # 3. 添加风险提示
        text = self._add_risk_disclaimers(text)

        return text

    # ==================== 创意模式方法 ====================

    def _replace_marketing_jargon(self, text: str) -> str:
        """替换营销黑话为更自然的表达"""
        jargon_replacements = self.creative_config.get(
            'marketing_jargon_replacements', {}
        )

        for jargon, natural in jargon_replacements.items():
            text = text.replace(jargon, natural)

        return text

    def _replace_absolutes(self, text: str) -> str:
        """替换绝对化表达为相对化表达"""
        avoid_absolutes = self.creative_config.get('avoid_absolutes', {})

        for absolute, relative in avoid_absolutes.items():
            text = text.replace(absolute, relative)

        return text

    def _add_colloquial_elements(self, text: str) -> str:
        """添加口语化元素"""
        colloquial = self.creative_config.get('colloquial_style', {})

        # 获取口语化短语
        openings = colloquial.get('opening', ['我跟你说'])
        personal = colloquial.get('personal_touch', ['我觉得'])
        uncertainty = colloquial.get('uncertainty', ['差不多'])

        lines = text.split('\n')
        result = []

        for i, line in enumerate(lines):
            # 跳过标题和空行
            if not line.strip() or line.startswith('#') or line.startswith('|'):
                result.append(line)
                continue

            # 在某些段落开头添加口语化表达（约15%的段落）
            if i > 0 and i % 5 == 0 and random.random() < 0.15:
                phrase = random.choice(openings + personal)
                result.append(f"{phrase}，{line}")
            else:
                # 偶尔在句中添加不确定性表达
                if random.random() < 0.1:
                    phrase = random.choice(uncertainty)
                    # 在句中适当位置插入
                    if '，' in line:
                        parts = line.split('，', 1)
                        line = f"{parts[0]}，{phrase}，{parts[1]}"
                result.append(line)

        return '\n'.join(result)

    def _adjust_sentence_patterns(self, text: str) -> str:
        """调整句式，让表达更自然"""
        # 调整数字表达
        text = re.sub(r'(\d+)%', r'\1%左右', text)

        # 调整时间表达
        text = text.replace('6个月', '差不多半年')
        text = text.replace('12个月', '差不多一年')

        return text

    # ==================== 严谨模式方法 ====================

    def _replace_exaggeration(self, text: str) -> str:
        """替换夸大表达"""
        avoid = self.formal_config.get('avoid_exaggeration', {})

        for exaggerated, accurate in avoid.items():
            text = text.replace(exaggerated, accurate)

        # 额外的严谨化处理
        text = text.replace('高达', '约')
        text = text.replace('轻松', '')
        text = text.replace('！', '。')

        return text

    def _add_data_sources(self, text: str) -> str:
        """为数据添加来源标注"""
        # 检测数字和百分比，添加"约"或"左右"
        text = re.sub(r'(\d+)([％%])(?![左右约约])', r'\1\2左右', text)
        text = re.sub(r'(\d+)万(?![左右约约])', r'\1万左右', text)

        return text

    def _add_risk_disclaimers(self, text: str) -> str:
        """添加风险提示"""
        disclaimers = self.formal_config.get('risk_disclaimers', [])

        # 如果文本中包含收益数据，添加风险提示
        if any(keyword in text for keyword in ['收益', '回报', '赚', '%', '％']):
            # 选择合适的风险提示
            disclaimer = random.choice(disclaimers) if disclaimers else ""

            # 在文档末尾添加（如果还没有）
            if disclaimer and disclaimer not in text:
                text = text.rstrip() + f"\n\n**风险提示**: {disclaimer}"

        return text

    # ==================== 质量检查方法 ====================

    def check_quality(
        self,
        text: str,
        mode: Optional[Literal["creative", "formal"]] = None
    ) -> Dict[str, any]:
        """
        检查内容质量

        Args:
            text: 待检查的文本
            mode: 检查模式

        Returns:
            检查结果字典
        """
        effective_mode = mode or self._determine_mode()
        issues = []
        score = 100

        if effective_mode == "creative":
            # 创意模式质量检查
            # 检查营销黑话
            jargon = self.creative_config.get('marketing_jargon_replacements', {})
            found_jargon = [k for k in jargon if k in text]
            if found_jargon:
                issues.append(f"发现营销黑话: {', '.join(found_jargon)}")
                score -= 5

            # 检查绝对化表达
            absolutes = self.creative_config.get('avoid_absolutes', {})
            found_absolute = [k for k in absolutes if k in text]
            if found_absolute:
                issues.append(f"发现绝对化表达: {', '.join(found_absolute)}")
                score -= 3

            # 检查口语化程度
            colloquial = self.creative_config.get('colloquial_style', {})
            colloquial_phrases = (
                colloquial.get('opening', []) +
                colloquial.get('personal_touch', []) +
                colloquial.get('uncertainty', [])
            )
            has_colloquial = any(p in text for p in colloquial_phrases)
            if not has_colloquial:
                issues.append("缺少口语化表达")
                score -= 10

        else:
            # 严谨模式质量检查
            # 检查夸大表达
            avoid = self.formal_config.get('avoid_exaggeration', {})
            found_exaggerated = [k for k in avoid if k in text]
            if found_exaggerated:
                issues.append(f"发现夸大表达: {', '.join(found_exaggerated)}")
                score -= 10

            # 检查数据是否标注来源
            has_data = bool(re.search(r'\d+[％%]', text) or re.search(r'\d+万', text))
            if has_data and '约' not in text and '左右' not in text:
                issues.append("数据缺少不确定性标注")
                score -= 5

            # 检查是否有风险提示
            if '收益' in text or '回报' in text:
                if '风险' not in text:
                    issues.append("缺少风险提示")
                    score -= 15

        return {
            'score': max(0, score),
            'issues': issues,
            'passed': score >= 70,
            'mode': effective_mode
        }

    def suggest_improvements(
        self,
        text: str,
        mode: Optional[Literal["creative", "formal"]] = None
    ) -> List[str]:
        """
        建议改进措施

        Args:
            text: 待改进的文本
            mode: 改进模式

        Returns:
            改进建议列表
        """
        effective_mode = mode or self._determine_mode()
        suggestions = []
        quality = self.check_quality(text, effective_mode)

        if not quality['passed']:
            for issue in quality['issues']:
                if '营销黑话' in issue or '绝对化' in issue:
                    suggestions.append("替换为更自然的口语化表达")
                if '缺少口语化' in issue:
                    suggestions.append("加入个人感受表达，如'我觉得''说实话'")
                if '夸大表达' in issue:
                    suggestions.append("使用更准确客观的表述，避免夸大")
                if '缺少不确定性' in issue:
                    suggestions.append("为数据添加'约''左右'等不确定性标注")
                if '缺少风险提示' in issue:
                    suggestions.append("添加风险提示说明")

        return suggestions


# ==================== 便捷函数 ====================

def deaiify(
    text: str,
    mode: Literal["creative", "formal"] = "creative",
    config_path: Optional[str] = None
) -> str:
    """
    去AI化处理文本

    Args:
        text: 待处理的文本
        mode: 去AI化模式
        config_path: 配置文件路径（可选）

    Returns:
        处理后的文本

    Examples:
        >>> # 创意模式
        >>> text = "该项目采用核心卖点，保证6个月回本！"
        >>> deaiify(text, mode="creative")
        '我跟你说，这几个地方我觉得不错，差不多半年能回本，应该没问题'

        >>> # 严谨模式
        >>> deaiify(text, mode="formal")
        '该项目具有主要优势，预计6个月左右回本。\\n\\n**风险提示**: 以上数据为估算值...'
    """
    processor = DeAIifier(config_path, mode=mode)
    return processor.process(text)


def check_text_quality(
    text: str,
    mode: Literal["creative", "formal"] = "creative",
    config_path: Optional[str] = None
) -> Dict[str, any]:
    """
    检查文本质量

    Args:
        text: 待检查的文本
        mode: 检查模式
        config_path: 配置文件路径（可选）

    Returns:
        质量检查结果
    """
    processor = DeAIifier(config_path)
    return processor.check_quality(text, mode)


# ==================== 使用示例 ====================

if __name__ == "__main__":
    # 示例文本
    ai_text = """
    # 建华官园智慧农贸项目介绍

    本项目采用智慧农贸系统，打造全方位数字化生活服务。
    依托14万人口红利，构建核心商业护城河。

    五大核心优势：
    1. 独家经营：生态新城首个智慧农贸市场
    2. 租金洼地：比周边便宜3倍
    3. 人口红利：辐射14万人
    4. 政策支持：政府重点项目
    5. 稳定回报：保证20%收益

    投资回报率高达20%，保证6个月回本！
    """

    print("=" * 50)
    print("去AI化处理器 - 双模式演示")
    print("=" * 50)

    print("\n【原文】")
    print(ai_text)

    print("\n" + "=" * 50)
    print("【创意模式处理】")
    print("=" * 50)
    processor_creative = DeAIifier(mode="creative")
    creative_text = processor_creative.process(ai_text)
    print(creative_text)

    print("\n" + "=" * 50)
    print("【严谨模式处理】")
    print("=" * 50)
    processor_formal = DeAIifier(mode="formal")
    formal_text = processor_formal.process(ai_text)
    print(formal_text)

    print("\n" + "=" * 50)
    print("【创意模式质量检查】")
    print("=" * 50)
    quality_creative = processor_creative.check_quality(ai_text)
    print(f"分数: {quality_creative['score']}")
    print(f"通过: {quality_creative['passed']}")
    print(f"问题: {quality_creative['issues']}")

    print("\n" + "=" * 50)
    print("【严谨模式质量检查】")
    print("=" * 50)
    quality_formal = processor_formal.check_quality(ai_text, mode="formal")
    print(f"分数: {quality_formal['score']}")
    print(f"通过: {quality_formal['passed']}")
    print(f"问题: {quality_formal['issues']}")
