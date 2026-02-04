"""
Leo Web UI 简化版
================
用于测试基本功能
"""

import sys
from pathlib import Path

# 先设置路径，再导入其他模块
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))

import streamlit as st

st.set_page_config(
    page_title="Leo AI 工作台",
    page_icon="⚡",
    layout="wide"
)

st.title("⚡ Leo AI 实战工作台")
st.markdown("---")

# 简单的系统状态
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Skills", "加载中...")
with col2:
    st.metric("Agents", "加载中...")
with col3:
    st.metric("Workflows", "加载中...")

st.markdown("---")

# 尝试加载系统
with st.spinner("正在加载系统组件..."):
    try:

        # 尝试加载 skill loader
        from leo_subagents.skills_bridge.enhanced_skill_loader import get_enhanced_loader
        loader = get_enhanced_loader()

        skills_count = len(loader.skills) if loader.skills else 0
        workflows_count = len(loader.workflows) if loader.workflows else 0

        st.success(f"✅ 系统加载成功！Skills: {skills_count}, Workflows: {workflows_count}")

        # 显示 Skills 列表
        if loader.skills:
            st.subheader("📦 Skills 列表")
            for name in list(loader.skills.keys())[:10]:
                st.write(f"- {name}")
            if len(loader.skills) > 10:
                st.caption(f"... 还有 {len(loader.skills) - 10} 个")

    except Exception as e:
        st.error(f"❌ 加载失败: {e}")
        import traceback
        st.code(traceback.format_exc())

st.markdown("---")
st.caption("Leo AI System - 简化测试版")
