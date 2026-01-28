"""
Batch skill fixer script
批量修复不完整技能结构
"""

from pathlib import Path

# BACKEND 分类
BACKEND_SKILLS = [
    ("api_doc_generator_skill", "API文档生成技能", "ApiDocGenerator"),
    ("database_migration_skill", "数据库迁移技能", "DatabaseMigration"),
    ("database_model_generator_skill", "数据库模型生成技能", "DatabaseModelGenerator"),
    ("fastapi_endpoint_generator_skill", "FastAPI端点生成技能", "FastAPIEndpointGenerator"),
    ("flask_api_generator_skill", "Flask API生成技能", "FlaskAPIGenerator"),
    ("flask_auth_generator_skill", "Flask认证生成技能", "FlaskAuthGenerator"),
]

# BUSINESS 分类
BUSINESS_SKILLS = [
    ("ecommerce", "电商技能", "Ecommerce"),
    ("fission_miniprogram", "裂变小程序技能", "FissionMiniprogram"),
    ("realestate", "房地产技能", "RealEstate"),
]

# DEVOPS 分类
DEVOPS_SKILLS = [
    ("deployment_script_generator_skill", "部署脚本生成技能", "DeploymentScriptGenerator"),
    ("dockerfile_generator_skill", "Dockerfile生成技能", "DockerfileGenerator"),
    ("docker_compose_generator_skill", "Docker Compose生成技能", "DockerComposeGenerator"),
    ("github_actions_generator_skill", "GitHub Actions生成技能", "GitHubActionsGenerator"),
    ("nginx_config_generator_skill", "Nginx配置生成技能", "NginxConfigGenerator"),
]

# FRONTEND 分类
FRONTEND_SKILLS = [
    ("css_layout_generator_skill", "CSS布局生成技能", "CSSLayoutGenerator"),
    ("miniprogram_component_generator_skill", "小程序组件生成技能", "MiniprogramComponentGenerator"),
    ("miniprogram_page_generator_skill", "小程序页面生成技能", "MiniprogramPageGenerator"),
    ("react_component_generator_skill", "React组件生成技能", "ReactComponentGenerator"),
    ("vue_component_generator_skill", "Vue组件生成技能", "VueComponentGenerator"),
    ("vue_page_generator_skill", "Vue页面生成技能", "VuePageGenerator"),
    ("web-ui", "Web UI技能", "WebUI"),
]

# SCAFFOLD 分类
SCAFFOLD_SKILLS = [
    ("flask_api_scaffold_skill", "Flask API脚手架技能", "FlaskAPIScaffold"),
    ("fullstack_project_scaffold_skill", "全栈项目脚手架技能", "FullstackScaffold"),
    ("miniprogram_project_scaffold_skill", "小程序项目脚手架技能", "MiniprogramScaffold"),
    ("t3_stack_scaffold_skill", "T3 Stack脚手架技能", "T3StackScaffold"),
]

# TESTING 分类
TESTING_SKILLS = [
    ("api_test_generator_skill", "API测试生成技能", "APITestGenerator"),
    ("e2e_test_generator_skill", "E2E测试生成技能", "E2ETestGenerator"),
    ("unit_test_generator_skill", "单元测试生成技能", "UnitTestGenerator"),
]

# PROMPT-ENGINEERING 分类
PROMPT_SKILLS = [
    ("chain-of-thought-prompter", "思维链提示器", "ChainOfThoughtPrompter"),
    ("claude-prompt-engineering-skills", "Claude提示工程技能", "ClaudePromptEngineering"),
    ("long-context-handler", "长上下文处理器", "LongContextHandler"),
    ("prompt-chaining-orchestrator", "提示链编排器", "PromptChainingOrchestrator"),
    ("prompt-optimizer", "提示优化器", "PromptOptimizer"),
    ("xml-structure-builder", "XML结构构建器", "XMLStructureBuilder"),
]

# SECURITY 分类
SECURITY_SKILLS = [
    ("security_scan_skill", "安全扫描技能", "SecurityScan"),
]

SKILLS_ROOT = Path(__file__).parent.parent


def create_init_file(category_path: Path, skill_name: str, class_name: str):
    """创建 __init__.py 文件"""
    init_content = f'''from .{skill_name} import {class_name}

__all__ = ["{class_name}"]
'''
    init_path = category_path / skill_name / "__init__.py"
    init_path.write_text(init_content, encoding="utf-8")
    return init_path


def create_main_file(category_path: Path, skill_name: str, class_name: str, description: str):
    """创建主模块文件"""
    main_content = f'''"""
{skill_name}

{description}
"""

from .scripts.main import {class_name}

__all__ = ["{class_name}"]
'''
    main_path = category_path / skill_name / f"{skill_name}.py"
    main_path.write_text(main_content, encoding="utf-8")
    return main_path


def fix_category(category: str, skills_list):
    """修复一个分类的所有技能"""
    category_path = SKILLS_ROOT / category
    if not category_path.exists():
        print(f"[SKIP] Category {category} does not exist")
        return 0

    fixed = 0
    for skill_name, description, class_name in skills_list:
        skill_path = category_path / skill_name
        if not skill_path.exists():
            print(f"[SKIP] {category}/{skill_name} does not exist")
            continue

        # 检查是否已有 __init__.py
        init_path = skill_path / "__init__.py"
        if not init_path.exists():
            create_init_file(category_path, skill_name, class_name)
            print(f"[ADD] {category}/{skill_name}/__init__.py")
            fixed += 1

        # 检查是否有主模块文件
        main_path = skill_path / f"{skill_name}.py"
        if not main_path.exists():
            # 检查是否有 scripts/main.py
            scripts_main = skill_path / "scripts" / "main.py"
            if scripts_main.exists():
                create_main_file(category_path, skill_name, class_name, description)
                print(f"[ADD] {category}/{skill_name}/{skill_name}.py")
                fixed += 1
            else:
                # 没有 scripts/main.py，创建简单的主模块
                simple_content = f'''"""
{skill_name}

{description}
"""

import sys
from pathlib import Path

class {class_name}:
    \"\"\"
    {class_name}

    {description}
    \"\"\"

    def __init__(self):
        self.name = "{skill_name}"
        print(f"{{self.name}} initialized")

    def execute(self, task: str, **kwargs):
        \"\"\"执行任务\"\"\"
        return {{"status": "completed", "task": task}}


def main():
    skill = {class_name}()
    return skill


if __name__ == "__main__":
    skill = main()
'''
                main_path.write_text(simple_content, encoding="utf-8")
                create_init_file(category_path, skill_name, class_name)
                print(f"[ADD] {category}/{skill_name}/{skill_name}.py (simple)")
                fixed += 1

    return fixed


if __name__ == "__main__":
    print("="*60)
    print("BATCH SKILL FIXER")
    print("="*60)

    total_fixed = 0

    total_fixed += fix_category("backend", BACKEND_SKILLS)
    total_fixed += fix_category("business", BUSINESS_SKILLS)
    total_fixed += fix_category("devops", DEVOPS_SKILLS)
    total_fixed += fix_category("frontend", FRONTEND_SKILLS)
    total_fixed += fix_category("scaffold", SCAFFOLD_SKILLS)
    total_fixed += fix_category("testing", TESTING_SKILLS)
    total_fixed += fix_category("prompt-engineering", PROMPT_SKILLS)
    total_fixed += fix_category("security", SECURITY_SKILLS)

    print("="*60)
    print(f"Total files fixed: {total_fixed}")
    print("="*60)
