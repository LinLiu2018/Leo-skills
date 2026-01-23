"""
Leo System Web UI
=================
基于 Streamlit 的轻量级 Web 界面
快速可视化展示 Skills 和 Agents 状态

运行方式: streamlit run leo_web_ui.py
"""

import sys
from pathlib import Path

# 确保项目路径在 sys.path 中
PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
except ImportError:
    print("❌ 请先安装 Streamlit: pip install streamlit")
    print("   或使用: pip install -e .[web]")
    sys.exit(1)

# 页面配置
st.set_page_config(
    page_title="Leo AI System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== 样式 ====================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
    }
    .skill-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #667eea;
        margin-bottom: 0.5rem;
    }
    .agent-card {
        background: #f0f7ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin-bottom: 0.5rem;
    }
    .status-active {
        color: #28a745;
        font-weight: bold;
    }
    .status-inactive {
        color: #dc3545;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载 ====================

@st.cache_resource
def load_system():
    """加载 Leo 系统（带缓存）"""
    try:
        # 尝试导入系统
        import importlib.util
        
        # 加载 leo-system.py
        spec = importlib.util.spec_from_file_location(
            "leo_system",
            str(PROJECT_ROOT / "leo-system.py")
        )
        leo_system = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(leo_system)
        
        system = leo_system.get_system()
        return system, None
    except Exception as e:
        return None, str(e)


@st.cache_data(ttl=60)
def get_system_stats(_system):
    """获取系统统计（带缓存）"""
    if _system is None:
        return None
    return _system.get_system_status()


# ==================== 页面组件 ====================

def render_header():
    """渲染页头"""
    st.markdown('<p class="main-header">🤖 Leo AI Agent System</p>', unsafe_allow_html=True)
    st.markdown("*Skills + Subagents 协同工作架构*")
    st.divider()


def render_metrics(system, stats):
    """渲染统计指标"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        skills_count = stats['skills']['total'] if stats else 0
        st.metric(
            label="🎯 Skills",
            value=skills_count,
            delta="已加载"
        )
    
    with col2:
        agents_count = stats['agents']['total'] if stats else 0
        st.metric(
            label="🤖 Agents",
            value=agents_count,
            delta="已创建"
        )
    
    with col3:
        exec_count = stats['statistics']['total_executions'] if stats else 0
        st.metric(
            label="📈 执行次数",
            value=exec_count
        )
    
    with col4:
        success_rate = stats['statistics'].get('success_rate', 0) if stats else 0
        st.metric(
            label="✅ 成功率",
            value=f"{success_rate:.1f}%"
        )


def render_skills_panel(system, stats):
    """渲染 Skills 面板"""
    st.subheader("🎯 Skills 技能库")
    
    if stats and 'skills' in stats:
        categories = stats['skills'].get('by_category', {})
        
        if categories:
            tabs = st.tabs(list(categories.keys()) or ["全部"])
            
            for tab, (category, skills) in zip(tabs, categories.items()):
                with tab:
                    if skills:
                        for skill_name in skills:
                            with st.container():
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"**📦 {skill_name}**")
                                with col2:
                                    st.markdown('<span class="status-active">🟢 活跃</span>', unsafe_allow_html=True)
                    else:
                        st.info("此分类暂无技能")
        else:
            st.info("暂无技能分类信息")
    else:
        st.warning("无法加载 Skills 信息")


def render_agents_panel(system, stats):
    """渲染 Agents 面板"""
    st.subheader("🤖 Agents 代理库")
    
    if stats and 'agents' in stats:
        agent_names = stats['agents'].get('names', [])
        
        if agent_names:
            for agent_name in agent_names:
                with st.container():
                    col1, col2, col3 = st.columns([2, 2, 1])
                    with col1:
                        st.markdown(f"**🤖 {agent_name}**")
                    with col2:
                        if system and agent_name in system.agents:
                            agent = system.agents[agent_name]
                            st.caption(f"类型: {agent.config.type}")
                    with col3:
                        st.markdown('<span class="status-active">🟢 就绪</span>', unsafe_allow_html=True)
        else:
            st.info("暂无 Agent")
    else:
        st.warning("无法加载 Agents 信息")


def render_task_executor(system):
    """渲染任务执行器"""
    st.subheader("🚀 任务执行器")
    
    with st.form("task_form"):
        task_input = st.text_area(
            "输入任务描述",
            placeholder="例如：生成营销文档、分析数据、创作内容...",
            height=100
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            agent_options = ["自动选择"] + (system.list_agents() if system else [])
            selected_agent = st.selectbox("选择 Agent", agent_options)
        
        with col2:
            submitted = st.form_submit_button("🚀 执行任务", type="primary")
        
        if submitted and task_input:
            with st.spinner("执行中..."):
                try:
                    agent_name = None if selected_agent == "自动选择" else selected_agent
                    result = system.execute_task(task_input, agent_name)
                    
                    if result.get('success', True):
                        st.success("✅ 任务执行成功")
                        st.json(result)
                    else:
                        st.error(f"❌ 执行失败: {result.get('error', '未知错误')}")
                except Exception as e:
                    st.error(f"❌ 执行出错: {str(e)}")


def render_sidebar():
    """渲染侧边栏"""
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=Leo+AI", width=150)
        st.markdown("---")
        
        st.markdown("### 📊 系统信息")
        st.markdown(f"**版本**: 1.0.0")
        st.markdown(f"**作者**: Leo Liu")
        
        st.markdown("---")
        
        st.markdown("### 🔧 快捷操作")
        
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_data.clear()
            st.cache_resource.clear()
            st.rerun()
        
        if st.button("📋 查看日志", use_container_width=True):
            st.info("日志功能开发中...")
        
        st.markdown("---")
        
        st.markdown("### 📚 文档链接")
        st.markdown("[📖 系统文档](LEO_SYSTEM_README.md)")
        st.markdown("[📋 Skills 清单](SKILLS_MANIFEST.md)")
        st.markdown("[🤝 协作指南](LEO_MULTI_AI_COLLABORATION_GUIDE.md)")


# ==================== 主程序 ====================

def main():
    """主程序入口"""
    render_sidebar()
    render_header()
    
    # 加载系统
    system, error = load_system()
    
    if error:
        st.error(f"⚠️ 系统加载失败: {error}")
        st.info("请确保所有依赖已安装: `pip install -e .[all]`")
        return
    
    # 获取统计数据
    stats = get_system_stats(system)
    
    # 渲染统计指标
    render_metrics(system, stats)
    
    st.divider()
    
    # 创建两列布局
    col_left, col_right = st.columns(2)
    
    with col_left:
        render_skills_panel(system, stats)
    
    with col_right:
        render_agents_panel(system, stats)
    
    st.divider()
    
    # 任务执行器
    render_task_executor(system)
    
    # 页脚
    st.divider()
    st.caption("© 2026 Leo AI System | Built with ❤️ by Leo Liu")


if __name__ == "__main__":
    main()
