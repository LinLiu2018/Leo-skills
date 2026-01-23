#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Layout Leo CSkill - 智能内容排版技能
Author: Leo Liu
Version: 2.0.0 (可进化版本)
"""

import argparse
import sys
from pathlib import Path

# 添加leo-skills到路径以支持进化框架
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from core.evolution import EvolvableSkill

# 导入可进化技能类
sys.path.insert(0, str(Path(__file__).parent))
from content_layout_skill import ContentLayoutSkill

# 创建技能实例
skill = ContentLayoutSkill()


def format_for_wechat(content: str, style: str = "data_driven",
                      title: str = None, author: str = "Leo") -> str:
    """格式化为微信公众号格式（兼容旧接口）"""
    result = skill.execute(
        action="format_wechat",
        content=content,
        style=style,
        title=title,
        author=author
    )
    return result.data.get("result", "") if result.success else ""


def format_for_xiaohongshu(content: str, style: str = "vibrant_attention",
                           title: str = None) -> str:
    """格式化为小红书格式（兼容旧接口）"""
    result = skill.execute(
        action="format_xiaohongshu",
        content=content,
        style=style,
        title=title
    )
    return result.data.get("result", "") if result.success else ""


def generate_image_prompts(content: str, style: str = "professional") -> list:
    """生成AI图片提示词（兼容旧接口）"""
    result = skill.execute(
        action="generate_image_prompts",
        content=content,
        style=style
    )
    return result.data.get("prompts", []) if result.success else []


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="智能内容排版工具 by Leo")
    parser.add_argument("-p", "--platform", choices=["wechat", "xiaohongshu", "weibo", "blog"],
                       default="wechat", help="目标平台")
    parser.add_argument("-s", "--style", 
                       choices=["data_driven", "story_telling", "minimalist_professional",
                              "vibrant_attention", "emotional_resonance", "listicle_practical",
                              "comparison_analysis", "case_study_deep", "qa_interactive",
                              "magazine_premium"],
                       default="data_driven", help="排版风格")
    parser.add_argument("-i", "--input", help="输入文件路径")
    parser.add_argument("-o", "--output", help="输出文件路径")
    parser.add_argument("-t", "--title", help="文章标题")
    parser.add_argument("-a", "--author", default="Leo", help="作者名称")
    parser.add_argument("--images", action="store_true", help="生成图片提示词")
    parser.add_argument("--print", action="store_true", dest="print_output", help="打印输出")
    
    args = parser.parse_args()
    
    # 读取输入
    if args.input:
        with open(args.input, 'r', encoding='utf-8') as f:
            content = f.read()
    else:
        content = sys.stdin.read()
    
    if not content:
        print("错误: 没有输入内容")
        sys.exit(1)
    
    # 生成图片提示词
    if args.images:
        prompts = generate_image_prompts(content, args.style)
        print(f"\n📸 AI图片生成提示词 ({len(prompts)}个):\n")
        for i, prompt in enumerate(prompts, 1):
            print(f"{i}. {prompt['theme']}")
            print(f"   {prompt['prompt']}\n")
        sys.exit(0)
    
    # 格式化内容
    if args.platform == "wechat":
        result = format_for_wechat(content, args.style, args.title, args.author)
    elif args.platform == "xiaohongshu":
        result = format_for_xiaohongshu(content, args.style, args.title)
    else:
        result = content
    
    # 输出
    if args.print_output or not args.output:
        print(result)
    else:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(result)
        print(f"OK 已保存到: {args.output}")


if __name__ == "__main__":
    main()
