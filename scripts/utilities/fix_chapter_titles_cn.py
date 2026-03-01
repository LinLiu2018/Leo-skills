#!/usr/bin/env python3
"""
批量修复存量 Obsidian 笔记：给英文章节标题补上中文翻译

针对 3 本英文教材的章节笔记，将英文标题翻译为中文。
"""

import re
from pathlib import Path

# 章节标题翻译映射（手工整理，确保准确）
CHAPTER_TRANSLATIONS = {
    # === 深度学习 (Deep Learning) ===
    "1 Introduction": "引言",
    "1.1 Who Should Read This Book?": "谁应该阅读本书？",
    "1.2 Historical Trends in 深度学习 (Deep Learning)": "深度学习的历史趋势",
    "I Applied Math and Machine Learning Basics": "第一部分 应用数学与机器学习基础",
    "2 Linear Algebra": "线性代数",
    "3 Probability and InformationTheory": "概率论与信息论",
    "4 Numerical Computation": "数值计算",
    "5 Machine Learning Basics": "机器学习基础",
    "II Deep Networks: Modern Practices": "第二部分 深度网络：现代实践",
    "6 Deep Feedforward Networks": "深度前馈网络",
    "7 Regularization for 深度学习 (Deep Learning)": "深度学习的正则化",
    "8 Optimization for Training Deep Models": "深度模型训练的优化",
    "9 Convolutional Networks": "卷积网络",
    "10 Sequence Modeling: Recurrent and Recursive Nets": "序列建模：循环与递归网络",
    "11 Practical Methodology": "实践方法论",
    "12 Applications": "应用",
    "III 深度学习 (Deep Learning) Research": "第三部分 深度学习研究",
    "13 Linear Factor Models": "线性因子模型",
    "14 Autoencoders": "自编码器",
    "15 Representation Learning": "表示学习",
    "16 Structured Probabilistic Models for 深度学习 (Deep Learning)": "深度学习的结构化概率模型",
    "17 Monte Carlo Methods": "蒙特卡洛方法",
    "18 Confronting the Partition Function": "面对配分函数",
    "19 Approximate Inference": "近似推断",
    "20 Deep Generative Models": "深度生成模型",

    # === 模式识别与机器学习 (PRML) ===
    "模式识别与机器学习 (PRML)": "前言与概述",
    "Mathematical notation": "数学符号",
    "1 Introduction": "引言",
    "2 Probability Distributions": "概率分布",
    "3 Linear Models for Regression": "回归的线性模型",
    "4 Linear Models for Classification": "分类的线性模型",
    "5 Neural Networks": "神经网络",
    "6 Kernel Methods": "核方法",
    "7 Sparse Kernel Machines": "稀疏核机器",
    "8 Graphical Models": "图模型",
    "9 Mixture Models and EM": "混合模型与EM算法",
    "10 Approximate Inference": "近似推断",
    "11 Sampling Methods": "采样方法",
    "12 Continuous Latent Variables": "连续潜变量",
    "13 Sequential Data": "序列数据",
    "14 Combining Models": "模型组合",
    "Appendix A. Data Sets": "附录A 数据集",
    "Appendix B. Probability Distributions": "附录B 概率分布",
    "Appendix C. Properties of Matrices": "附录C 矩阵性质",
    "Appendix D. Calculus of Variations": "附录D 变分法",
    "Appendix E. Lagrange Multipliers": "附录E 拉格朗日乘子",

    # === 人工智能：一种现代方法 (AIMA) ===
    # AIMA 的章节标题是 "Chapter N" 格式，需要特殊处理
}

# AIMA 章节名映射（Chapter N → 中文）
AIMA_CHAPTERS = {
    1: "引言",
    2: "智能体",
    3: "通过搜索求解问题",
    4: "超越经典搜索",
    5: "对抗搜索与博弈",
    6: "约束满足问题",
    7: "逻辑智能体",
    8: "一阶逻辑",
    9: "一阶逻辑中的推理",
    10: "知识表示",
    11: "自动规划",
    12: "不确定性量化",
    13: "概率推理",
    14: "随时间推理",
    15: "概率编程",
    16: "做出简单决策",
    17: "做出复杂决策",
    18: "多智能体决策",
    19: "从示例中学习",
    20: "学习概率模型",
    21: "深度学习",
    22: "强化学习",
    23: "自然语言处理",
    24: "深度学习在NLP中的应用",
    25: "计算机视觉",
}


def fix_file(filepath: Path) -> bool:
    """修复单个文件的章节标题，返回是否修改"""
    text = filepath.read_text(encoding="utf-8")
    original = text

    # 匹配 "# 第N章 英文标题" 格式
    match = re.search(r'^(# 第\d+章 )(.+)$', text, re.MULTILINE)
    if not match:
        return False

    prefix = match.group(1)  # "# 第N章 "
    en_title = match.group(2).strip()

    # 查找中文翻译
    cn_title = None

    # 先检查 AIMA "Chapter N" 格式
    ch_match = re.match(r'Chapter (\d+)', en_title)
    if ch_match:
        ch_num = int(ch_match.group(1))
        cn_title = AIMA_CHAPTERS.get(ch_num)
        if cn_title:
            cn_title = f"{cn_title} (Chapter {ch_num})"
    else:
        # 查通用映射表
        cn = CHAPTER_TRANSLATIONS.get(en_title)
        if cn:
            cn_title = f"{cn} ({en_title})"

    if not cn_title:
        return False

    # 替换标题行
    new_title_line = f"{prefix}{cn_title}"
    text = text.replace(match.group(0), new_title_line, 1)

    # 同时替换 frontmatter 中的 title
    fm_match = re.search(r'^title: "第(\d+)章 (.+)"$', text, re.MULTILINE)
    if fm_match:
        ch_num = fm_match.group(1)
        old_fm_title = fm_match.group(0)
        new_fm_title = f'title: "第{ch_num}章 {cn_title}"'
        text = text.replace(old_fm_title, new_fm_title, 1)

    if text != original:
        filepath.write_text(text, encoding="utf-8")
        return True
    return False


def main():
    books_dir = Path("d:/桌面/Leo-Outputs/30-Resources/Books")
    fixed = 0
    skipped = 0

    for md_file in sorted(books_dir.rglob("*-第*章.md")):
        if fix_file(md_file):
            print(f"  [OK] {md_file.name}")
            fixed += 1
        else:
            skipped += 1

    print(f"\n完成: 修复 {fixed} 个文件, 跳过 {skipped} 个")


if __name__ == "__main__":
    main()
