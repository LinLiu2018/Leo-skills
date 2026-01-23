"""
Leo System Web UI v2.0
======================
增强版 Web 界面 - 支持完整的 Skills/Agents/Workflows 展示

运行方式: streamlit run leo_web_ui_v2.py
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
    sys.exit(1)

# 页面配置
st.set_page_config(
    page_title="Leo AI Agent System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ==================== 自定义样式 ====================

st.markdown("""
<style>
    /* 主标题渐变 */
    .main-header {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        text-align: center;
    }
    
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    
    /* 指标卡片 */
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 1rem;
        color: white;
        text-align: center;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
    
    /* Skill 卡片 */
    .skill-card {
        background: linear-gradient(to right, #f8f9fa, #ffffff);
        padding: 1rem 1.2rem;
        border-radius: 0.75rem;
        border-left: 4px solid #667eea;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        transition: transform 0.2s, box-shadow 0.2s;
    }
    
    .skill-card:hover {
        transform: translateX(5px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .skill-name {
        font-weight: 600;
        color: #333;
        font-size: 1rem;
    }
    
    .skill-desc {
        color: #666;
        font-size: 0.85rem;
        margin-top: 0.3rem;
    }
    
    /* Agent 卡片 */
    .agent-card {
        background: linear-gradient(to right, #e8f5e9, #ffffff);
        padding: 1rem 1.2rem;
        border-radius: 0.75rem;
        border-left: 4px solid #28a745;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Workflow 卡片 */
    .workflow-card {
        background: linear-gradient(to right, #fff3e0, #ffffff);
        padding: 1rem 1.2rem;
        border-radius: 0.75rem;
        border-left: 4px solid #ff9800;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* 状态标签 */
    .status-active {
        background: #28a745;
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.75rem;
        font-weight: 500;
    }
    
    .status-pending {
        background: #ffc107;
        color: #333;
        padding: 0.2rem 0.6rem;
        border-radius: 1rem;
        font-size: 0.75rem;
    }
    
    /* 分类标签 */
    .category-tag {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 1rem;
        font-size: 0.8rem;
        margin-right: 0.5rem;
        display: inline-block;
    }
    
    /* 任务执行器 */
    .executor-container {
        background: linear-gradient(135deg, #f5f7fa 0%, #e4e8eb 100%);
        padding: 2rem;
        border-radius: 1rem;
        margin-top: 1rem;
    }
    
    /* 侧边栏美化 */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* 隐藏 Streamlit 默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* 分隔线 */
    .custom-divider {
        height: 2px;
        background: linear-gradient(to right, #667eea, #764ba2, #f093fb);
        margin: 2rem 0;
        border-radius: 1px;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载 ====================

@st.cache_resource(ttl=300)
def load_enhanced_data():
    """加载增强版数据"""
    try:
        # 加载增强版 Skill Loader
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "skills_bridge"))
        from enhanced_skill_loader import EnhancedSkillLoader
        
        loader = EnhancedSkillLoader(
            skills_path=PROJECT_ROOT / "leo-skills",
            workflows_path=PROJECT_ROOT / "leo_workflows" / "workflows"
        )
        loader.discover_all()
        
        return loader, None
    except Exception as e:
        return None, str(e)


@st.cache_resource(ttl=300)
def load_agents():
    """加载 Agents"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "agents"))
        from agent_discovery import AgentDiscovery
        
        discovery = AgentDiscovery(PROJECT_ROOT / "leo_subagents" / "agents")
        agents = discovery.discover_all()
        
        return agents, None
    except Exception as e:
        return {}, str(e)


# ==================== 页面组件 ====================

def render_header():
    """渲染页头"""
    st.markdown('<h1 class="main-header">🤖 Leo AI Agent System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Skills + Subagents + Workflows 协同工作架构 | v2.0</p>', unsafe_allow_html=True)
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)


def render_metrics(loader, agents):
    """渲染统计指标"""
    col1, col2, col3, col4 = st.columns(4)
    
    skills_count = len(loader.skills) if loader else 0
    agents_count = len(agents) if agents else 0
    workflows_count = len(loader.workflows) if loader else 0
    categories_count = len(loader.categories) if loader else 0
    
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <div class="metric-value">{skills_count}</div>
            <div class="metric-label">🎯 Skills 技能</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container" style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%);">
            <div class="metric-value">{agents_count}</div>
            <div class="metric-label">🤖 Agents 代理</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-container" style="background: linear-gradient(135deg, #ff9800 0%, #ffc107 100%);">
            <div class="metric-value">{workflows_count}</div>
            <div class="metric-label">⚡ Workflows 工作流</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-container" style="background: linear-gradient(135deg, #e91e63 0%, #ff5722 100%);">
            <div class="metric-value">{categories_count}</div>
            <div class="metric-label">📁 分类</div>
        </div>
        """, unsafe_allow_html=True)


def render_skills_panel(loader):
    """渲染 Skills 面板"""
    st.markdown("### 🎯 Skills 技能库")
    
    if not loader or not loader.categories:
        st.warning("暂无 Skills 数据")
        return
    
    # 分类标签
    categories = sorted(loader.categories.keys())
    
    # 创建标签页
    if categories:
        tabs = st.tabs([f"📁 {cat} ({len(loader.categories[cat])})" for cat in categories])
        
        for tab, category in zip(tabs, categories):
            with tab:
                skills = loader.categories[category]
                
                # 搜索框
                search = st.text_input(f"🔍 搜索 {category}", key=f"search_{category}", placeholder="输入关键词...")
                
                # 过滤
                if search:
                    skills = [s for s in skills if search.lower() in s.lower()]
                
                # 显示 Skills（分页）
                page_size = 10
                total_pages = max(1, (len(skills) + page_size - 1) // page_size)
                
                if len(skills) > page_size:
                    page = st.selectbox(f"页码", range(1, total_pages + 1), key=f"page_{category}") - 1
                else:
                    page = 0
                
                start = page * page_size
                end = start + page_size
                
                for skill_name in skills[start:end]:
                    skill = loader.skills.get(skill_name)
                    if skill:
                        with st.container():
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"""
                                <div class="skill-card">
                                    <div class="skill-name">📦 {skill.name}</div>
                                    <div class="skill-desc">{skill.description[:100] if skill.description else '暂无描述'}...</div>
                                </div>
                                """, unsafe_allow_html=True)
                            with col2:
                                if skill.has_skill_md:
                                    st.caption("📄 SKILL.md")
                                if skill.has_scripts:
                                    st.caption("📁 scripts/")
                
                st.caption(f"显示 {start+1}-{min(end, len(skills))} / 共 {len(skills)} 个")


def render_agents_panel(agents):
    """渲染 Agents 面板"""
    st.markdown("### 🤖 Agents 代理库")
    
    if not agents:
        st.info("暂无 Agents 数据")
        return
    
    for name, meta in agents.items():
        st.markdown(f"""
        <div class="agent-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <span class="skill-name">🤖 {name}</span>
                    <span class="category-tag">{meta.type}</span>
                </div>
                <span class="status-active">🟢 就绪</span>
            </div>
            <div class="skill-desc">{meta.description if meta.description else f'{meta.type} 类型代理'}</div>
        </div>
        """, unsafe_allow_html=True)


def render_workflows_panel(loader):
    """渲染 Workflows 面板"""
    st.markdown("### ⚡ Workflows 工作流")
    
    if not loader or not loader.workflows:
        st.info("暂无 Workflows 数据")
        return
    
    for name, workflow in loader.workflows.items():
        with st.expander(f"📋 {name}", expanded=False):
            st.markdown(f"""
            <div class="workflow-card">
                <div class="skill-name">⚡ {workflow.name}</div>
                <div class="skill-desc">{workflow.description}</div>
            </div>
            """, unsafe_allow_html=True)
            
            if workflow.steps:
                st.markdown("**执行步骤：**")
                for i, step in enumerate(workflow.steps, 1):
                    if isinstance(step, dict):
                        st.markdown(f"{i}. {step.get('name', step.get('action', str(step)))}")
                    else:
                        st.markdown(f"{i}. {step}")


def render_task_executor(loader, agents):
    """渲染任务执行器"""
    st.markdown("### 🚀 任务执行器")
    
    st.markdown('<div class="executor-container">', unsafe_allow_html=True)
    
    with st.form("task_form"):
        task_input = st.text_area(
            "📝 输入任务描述",
            placeholder="例如：生成营销文档、分析数据、创作内容、研究市场趋势...",
            height=120
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agent_options = ["🔮 自动选择最佳 Agent"]
            if agents:
                agent_options.extend([f"🤖 {name}" for name in agents.keys()])
            selected_agent = st.selectbox("选择 Agent", agent_options)
        
        with col2:
            workflow_options = ["不使用 Workflow"]
            if loader and loader.workflows:
                workflow_options.extend([f"⚡ {name}" for name in loader.workflows.keys()])
            selected_workflow = st.selectbox("选择 Workflow", workflow_options)
        
        with col3:
            priority = st.selectbox("优先级", ["🟢 普通", "🟡 较高", "🔴 紧急"])
        
        submitted = st.form_submit_button("🚀 执行任务", type="primary", use_container_width=True)
        
        if submitted and task_input:
            with st.spinner("⏳ 执行中..."):
                st.success("✅ 任务已提交！（演示模式）")
                st.json({
                    "task": task_input[:100],
                    "agent": selected_agent,
                    "workflow": selected_workflow,
                    "priority": priority,
                    "status": "queued"
                })
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar(loader, agents):
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🤖 Leo AI System")
        st.markdown("---")
        
        st.markdown("### 📊 系统概览")
        if loader:
            st.markdown(f"- **Skills**: {len(loader.skills)} 个")
            st.markdown(f"- **分类**: {len(loader.categories)} 个")
            st.markdown(f"- **Workflows**: {len(loader.workflows)} 个")
        if agents:
            st.markdown(f"- **Agents**: {len(agents)} 个")
        
        st.markdown("---")
        
        st.markdown("### 🔧 快捷操作")
        
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
        
        if st.button("📊 导出报告", use_container_width=True):
            if loader:
                summary = loader.get_summary()
                st.download_button(
                    "⬇️ 下载 JSON",
                    data=str(summary),
                    file_name="leo_system_report.json",
                    mime="application/json"
                )
        
        st.markdown("---")
        
        st.markdown("### 📚 文档")
        st.markdown("[📖 系统文档](LEO_SYSTEM_README.md)")
        st.markdown("[📋 Skills 清单](SKILLS_MANIFEST.md)")
        st.markdown("[🤝 协作指南](LEO_MULTI_AI_COLLABORATION_GUIDE.md)")
        
        st.markdown("---")
        
        st.markdown("### ℹ️ 关于")
        st.markdown("**版本**: 2.0.0")
        st.markdown("**作者**: Leo Liu")
        st.caption("© 2026 Leo AI System")


# ==================== 主程序 ====================

def main():
    """主程序入口"""
    # 加载数据
    loader, loader_error = load_enhanced_data()
    agents, agents_error = load_agents()
    
    # 渲染侧边栏
    render_sidebar(loader, agents)
    
    # 渲染页头
    render_header()
    
    # 错误提示
    if loader_error:
        st.error(f"⚠️ Skills 加载失败: {loader_error}")
    if agents_error:
        st.warning(f"⚠️ Agents 加载警告: {agents_error}")
    
    # 渲染统计指标
    render_metrics(loader, agents)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 三栏布局
    col_skills, col_agents = st.columns([2, 1])
    
    with col_skills:
        render_skills_panel(loader)
    
    with col_agents:
        render_agents_panel(agents)
        st.markdown("---")
        render_workflows_panel(loader)
    
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    
    # 任务执行器
    render_task_executor(loader, agents)
    
    # 页脚
    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 1rem;">
        © 2026 Leo AI Agent System | Built with ❤️ by Leo Liu | Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
