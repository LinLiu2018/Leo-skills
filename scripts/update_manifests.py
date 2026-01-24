#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
from pathlib import Path
from datetime import datetime

# 确保文件操作使用UTF-8编码
def safe_print(text):
    """安全打印，避免编码错误"""
    try:
        print(text)
    except UnicodeEncodeError:
        # 如果编码失败，移除特殊字符后重试
        safe_text = text.encode('ascii', 'ignore').decode('ascii')
        print(safe_text)

# 配置路径
PROJECT_ROOT = Path(__file__).parent.parent
KNOWLEDGE_PATH = PROJECT_ROOT / "leo_knowledge" / "context"
SKILLS_PATH = PROJECT_ROOT / "leo_skills"
SUBAGENTS_PATH = PROJECT_ROOT / "leo_subagents" / "agents"
WORKFLOWS_PATH = PROJECT_ROOT / "leo_workflows" / "workflows"

def generate_project_structure():
    """生成项目结构树"""
    safe_print("Generating project structure...")
    
    structure = []
    structure.append(f"# Project Structure (Auto-Generated)\n")
    structure.append(f"> Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    structure.append("## Core Directory Tree\n")
    structure.append("```text")
    
    # 定义需要展示的目录深度和过滤规则
    ignore_dirs = {'.git', '__pycache__', '.idea', '.vscode', '.gemini', 'tmp', 'node_modules'}
    
    def add_to_tree(path, prefix=""):
        items = sorted([x for x in path.iterdir() if x.name not in ignore_dirs])
        # 限制显示数量，避免过长
        if len(items) > 20: 
            items = items[:20] + [Path("...")]
            
        for i, item in enumerate(items):
            is_last = i == len(items) - 1
            connector = "└── " if is_last else "├── "
            
            if isinstance(item, Path) and item.name == "...":
                structure.append(f"{prefix}{connector}...")
                continue
                
            structure.append(f"{prefix}{connector}{item.name}{'/' if item.is_dir() else ''}")
            
            if item.is_dir() and item.name not in ['assets', 'tests', 'logs']:
                # 递归深度限制
                if len(prefix) < 8: 
                    add_to_tree(item, prefix + ("    " if is_last else "│   "))
                    
    add_to_tree(PROJECT_ROOT)
    structure.append("```")
    
# 写入文件
    output_path = KNOWLEDGE_PATH / "project_structure.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(structure))
    safe_print(f"[SUCCESS] Updated: {output_path}")

def update_manifests():
    """更新 Skills/Agents/Workflows Manifest"""
    # 这里我们主要扫描并列出清单，暂不覆盖 SKILLS_MANIFEST.md 的核心描述，
    # 而是生成一个新的 summary index 供 Context 使用
    
    safe_print("Scanning Capabilities...")
    
    # 1. Scan Skills
    skills = []
    if SKILLS_PATH.exists():
        for item in SKILLS_PATH.rglob("SKILL.md"):
            skill_dir = item.parent
            skills.append(f"- **{skill_dir.name}**: {skill_dir.parent.name}/{skill_dir.name}")
            
    # 2. Scan Agents
    agents = []
    if SUBAGENTS_PATH.exists():
        for item in SUBAGENTS_PATH.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                # 简单读取 docstring 或 yaml (这里简化为目录名)
                agents.append(f"- **{item.name}**")
                
    # 3. Scan Workflows
    workflows = []
    if WORKFLOWS_PATH.exists():
        for item in WORKFLOWS_PATH.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                 workflows.append(f"- **{item.name}**")
    
    content = [
        "# System Capabilities Index (Auto-Generated)",
        f"> Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
        "## 🧩 Skills (能力库)",
        "\n".join(sorted(skills)) if skills else "- No skills found",
        "\n## 🤖 Subagents (代理库)",
        "\n".join(sorted(agents)) if agents else "- No agents found",
        "\n## 🌊 Workflows (工作流)",
        "\n".join(sorted(workflows)) if workflows else "- No workflows found"
    ]
    
    output_path = KNOWLEDGE_PATH / "capability_index.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(content))
    safe_print(f"[SUCCESS] Updated: {output_path}")

if __name__ == "__main__":
    generate_project_structure()
    update_manifests()
