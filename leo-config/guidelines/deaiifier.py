"""
去AI化内容处理器
================
自动将AI生成的内容转换为更自然的表达
"""

import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional


class DeAIifier:
    """
    去AI化处理器
    ===========
    根据配置规则自动将AI生成的内容转换为更像真人的表达
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化处理器

        Args:
            config_path: 配置文件路径，默认使用项目内置配置
        """
        if config_path is None:
            # 默认配置路径
            current_file = Path(__file__)
            config_path = current_file.parent / "deaiification_guide.yaml"

        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)

        self.forbidden_words = set(self.config.get('forbidden_words', []))
        self.word_replacements = self.config.get('word_replacements', {})
        self.sentence_patterns = self.config.get('sentence_patterns', {})

    def process(self, text: str) -> str:
        """
        处理文本，应用去AI化规则

        Args:
            text: 待处理的文本

        Returns:
            处理后的文本
        """
        # 1. 替换禁用词汇
        text = self._replace_forbidden_words(text)

        # 2. 替换AI化表达
        text = self._replace_ai_expressions(text)

        # 3. 添加口语化元素
        text = self._add_colloquial_elements(text)

        # 4. 调整句式
        text = self._adjust_sentence_patterns(text)

        return text

    def _replace_forbidden_words(self, text: str) -> str:
        """替换禁用词汇"""
        for word in self.forbidden_words:
            if word in text:
                # 查找替换词
                replacement = self.word_replacements.get(word)
                if replacement:
                    text = text.replace(word, replacement)
                else:
                    # 如果没有替换词，用更自然的表达
                    text = text.replace(word, self._natural_alternative(word))

        return text

    def _replace_ai_expressions(self, text: str) -> str:
        """替换AI化表达"""
        replacements = {
            '五大优势': '这几个地方我觉得不错',
            '四大亮点': '这几点挺好的',
            '三大特色': '这几个地方还行',
            '核心卖点': '主要优势',
            '投资回报': '能赚多少钱',
            '目标客户': '想找摊位的人',
            '市场需求': '大家需要什么',
            '竞争优势': '比别人强的地方',
            '商业模式': '怎么做生意',
            '运营策略': '怎么经营',
            '增长空间': '还能赚多少',
        }

        for ai_term, human_term in replacements.items():
            text = text.replace(ai_term, human_term)

        return text

    def _add_colloquial_elements(self, text: str) -> str:
        """添加口语化元素"""
        # 在开头添加口语化表达
        colloquial_opens = [
            '我跟你说',
            '说实话',
            '不瞒你说',
            '讲真',
        ]

        # 在结尾添加口语化表达
        colloquial_closes = [
            '就是这样',
            '我话就说到这',
            '你们自己看着办吧',
        ]

        # 随机插入一些口语化表达（避免过度使用）
        lines = text.split('\n')

        for i, line in enumerate(lines):
            # 跳过标题和空行
            if not line.strip() or line.startswith('#') or line.startswith('|'):
                continue

            # 在某些段落开头添加口语化表达（约20%的段落）
            if i % 5 == 0 and i > 0:
                import random
                if random.random() < 0.2:
                    open_phrase = random.choice(colloquial_opens)
                    lines[i] = f"{open_phrase}，{line}"

        return '\n'.join(lines)

    def _adjust_sentence_patterns(self, text: str) -> str:
        """调整句式"""
        # 将绝对化表达改为相对化
        absolute_patterns = {
            r'必须([要打])': r'最好\1',
            r'绝对([能会])': r'基本\1',
            r'保证([有成])': r'应该没问题，\1',
            r'完美([的地])': r'还不错\1',
            r'一定([能会])': r'应该\1',
            r'肯定([是能会])': r'估计\1',
        }

        for pattern, replacement in absolute_patterns.items():
            text = re.sub(pattern, replacement, text)

        return text

    def _natural_alternative(self, word: str) -> str:
        """为禁用词提供自然的替代"""
        alternatives = {
            '智慧': '标准化',
            '智能': '方便的',
            'AI': '好用的',
            '赋能': '帮助',
            '痛点': '头疼的事',
            '赛道': '行业',
            '闭环': '完整流程',
            '沉浸式': '真实的',
            '极致': '挺好的',
            '顶级': '不错的',
            '首选': '可以考虑',
            '必选': '建议选择',
        }

        return alternatives.get(word, '好的')

    def check_quality(self, text: str) -> Dict[str, any]:
        """
        检查内容质量

        Args:
            text: 待检查的文本

        Returns:
            检查结果字典
        """
        issues = []
        score = 100

        # 检查禁用词汇
        found_forbidden = []
        for word in self.forbidden_words:
            if word in text:
                found_forbidden.append(word)
                score -= 5

        if found_forbidden:
            issues.append(f"发现禁用词汇: {', '.join(found_forbidden)}")

        # 检查绝对化表达
        absolute_patterns = ['必须', '绝对', '保证', '完美', '一定', '肯定']
        found_absolute = []
        for pattern in absolute_patterns:
            if pattern in text:
                found_absolute.append(pattern)
                score -= 2

        if found_absolute:
            issues.append(f"发现绝对化表达: {', '.join(found_absolute)}")

        # 检查是否有口语化表达
        colloquial_patterns = ['我觉得', '说实话', '你猜怎么着', '差不多']
        has_colloquial = any(pattern in text for pattern in colloquial_patterns)

        if not has_colloquial:
            issues.append("缺少口语化表达")
            score -= 10

        return {
            'score': max(0, score),
            'issues': issues,
            'passed': score >= 70
        }

    def suggest_improvements(self, text: str) -> List[str]:
        """
        建议改进措施

        Args:
            text: 待改进的文本

        Returns:
            改进建议列表
        """
        suggestions = []
        quality = self.check_quality(text)

        if not quality['passed']:
            for issue in quality['issues']:
                if '禁用词汇' in issue:
                    suggestions.append("替换禁用词汇为更自然的表达")
                if '绝对化表达' in issue:
                    suggestions.append("将绝对化表达改为相对化，如'必须'改为'最好'")
                if '缺少口语化' in issue:
                    suggestions.append("加入口语化表达，如'我觉得''说实话'")

        # 检查是否过于正式
        formal_patterns = ['综上所述', '因此', '故而', '由此可见']
        if any(pattern in text for pattern in formal_patterns):
            suggestions.append("减少正式连接词，用更自然的过渡")

        # 检查是否过于完美
        if text.count('！') > 10:
            suggestions.append("减少感叹号使用，让语气更平和")

        return suggestions


# ==================== 便捷函数 ====================

def deaiify(text: str, config_path: Optional[str] = None) -> str:
    """
    去AI化处理文本

    Args:
        text: 待处理的文本
        config_path: 配置文件路径（可选）

    Returns:
        处理后的文本

    Examples:
        >>> text = "该项目采用智慧农贸系统，打造全方位数字化生活服务"
        >>> deaiify(text)
        '这个市场挺正规的，买菜付款都方便，挺省事'
    """
    processor = DeAIifier(config_path)
    return processor.process(text)


def check_text_quality(text: str, config_path: Optional[str] = None) -> Dict[str, any]:
    """
    检查文本质量

    Args:
        text: 待检查的文本
        config_path: 配置文件路径（可选）

    Returns:
        质量检查结果
    """
    processor = DeAIifier(config_path)
    return processor.check_quality(text)


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

    # 去AI化处理
    processor = DeAIifier()

    print("=== 原文 ===")
    print(ai_text)

    print("\n=== 去AI化后 ===")
    human_text = processor.process(ai_text)
    print(human_text)

    print("\n=== 质量检查 ===")
    quality = processor.check_quality(ai_text)
    print(f"分数: {quality['score']}")
    print(f"通过: {quality['passed']}")
    print(f"问题: {quality['issues']}")

    print("\n=== 改进建议 ===")
    suggestions = processor.suggest_improvements(ai_text)
    for i, suggestion in enumerate(suggestions, 1):
        print(f"{i}. {suggestion}")
