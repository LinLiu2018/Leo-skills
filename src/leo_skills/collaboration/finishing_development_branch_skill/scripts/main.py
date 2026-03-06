# -*- coding: utf-8 -*-
"""
finishing_development_branch_skill 脚本入口
"""


def execute(**kwargs):
    """执行技能主逻辑"""
    print("使用 finishing_development_branch_skill 完成开发分支")
    print("\n流程：验证测试 → 展示选项 → 执行选择 → 清理")


def get_info():
    """返回技能信息"""
    return {
        "name": "finishing_development_branch_skill",
        "description": "完成开发分支 - 在实现完成后展示合并/PR/清理选项",
        "category": "collaboration",
    }


if __name__ == "__main__":
    execute()
