#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Content Layout Leo CSkill - 智能内容排版技能
Author: Leo Liu
Version: 1.0.0
"""

import argparse
import sys
import os
import yaml
from pathlib import Path

# 技能根目录
SKILL_ROOT = Path(__file__).parent.parent
CONFIG_DIR = SKILL_ROOT / "config"

def load_config():
    """加载配置"""
    config_path = CONFIG_DIR / "style_profiles.yaml"
    if config_path.exists():
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    return {}

# 导入 WeChatFormatter
sys.path.insert(0, str(Path(__file__).parent))
from formatters.wechat_formatter import WeChatFormatter
from image_matchers.intelligent_matcher import ImageMatcher


def format_for_wechat(content: str, style: str = "data_driven",
                      title: str = None, author: str = "Leo") -> str:
    """格式化为微信公众号格式"""
    config = load_config()
    formatter = WeChatFormatter(config)
    html_content = formatter.format(
        content=content,
        style_name=style,
        title=title,
        author=author
    )
    return html_content


def format_for_xiaohongshu(content: str, style: str = "vibrant_attention",
                           title: str = None) -> str:
    """格式化为小红书格式"""
    formatted = []
    if title:
        formatted.append(f"📌 {title}\n")
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if line.startswith('#'):
            heading = line.lstrip('#').strip()
            formatted.append(f"\n{'='*30}\n  {heading}\n{'='*30}\n")
        else:
            formatted.append(line + "\n")
    
    formatted.append("\n" + "─"*30)
    formatted.append("\n🏷️  #房产 #楼市 #宁波 #购房指南")
    
    return '\n'.join(formatted)


def generate_image_prompts(content: str, style: str = "professional") -> list:
    """生成AI图片提示词"""
    config = load_config()
    image_rules = config.get("image_matching_rules", {})
    matcher = ImageMatcher(image_rules)
    prompts = matcher.generate_image_prompts(content, style)
    return prompts


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
