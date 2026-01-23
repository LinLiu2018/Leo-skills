"""
Leo System Web UI v3.0 - 完整业务版
====================================
针对 Leo 业务场景优化的完整 Web 界面

功能特点:
- 完整展示所有 Skills (39+)、Agents (14+)、Workflows (6+)
- 业务场景快捷入口（房产、菜场、小程序开发）
- 项目管理面板
- 优化的 UI/UX 设计

运行: streamlit run leo_web_ui_v3.py
"""

import sys
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
except ImportError:
    print("❌ 请先安装 Streamlit: pip install streamlit")
    sys.exit(1)

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="Leo AI Agent System | 智能工作台",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'About': "Leo AI Agent System v3.0 - 您的智能工作伙伴"
    }
)


# ==================== 高级样式 ====================

st.markdown("""
<style>
    /* 全局样式 */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* 隐藏默认元素 */
    #MainMenu, footer, header {visibility: hidden;}
    
    /* 主标题 */
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #d946ef 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0.5rem;
        animation: glow 2s ease-in-out infinite alternate;
    }
    
    @keyframes glow {
        from { filter: drop-shadow(0 0 5px rgba(99, 102, 241, 0.3)); }
        to { filter: drop-shadow(0 0 15px rgba(139, 92, 246, 0.5)); }
    }
    
    .hero-subtitle {
        text-align: center;
        color: #64748b;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    
    /* 玻璃态卡片 */
    .glass-card {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 16px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 1.5rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
        transition: transform 0.3s, box-shadow 0.3s;
    }
    
    .glass-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
    }
    
    /* 指标卡片 */
    .metric-card {
        background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
        border-radius: 16px;
        padding: 1.5rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 40px rgba(99, 102, 241, 0.3);
    }
    
    .metric-card.green { background: linear-gradient(135deg, #10b981 0%, #059669 100%); box-shadow: 0 10px 40px rgba(16, 185, 129, 0.3); }
    .metric-card.orange { background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); box-shadow: 0 10px 40px rgba(245, 158, 11, 0.3); }
    .metric-card.pink { background: linear-gradient(135deg, #ec4899 0%, #db2777 100%); box-shadow: 0 10px 40px rgba(236, 72, 153, 0.3); }
    .metric-card.cyan { background: linear-gradient(135deg, #06b6d4 0%, #0891b2 100%); box-shadow: 0 10px 40px rgba(6, 182, 212, 0.3); }
    
    .metric-value { font-size: 2.5rem; font-weight: 700; }
    .metric-label { font-size: 0.9rem; opacity: 0.9; margin-top: 0.5rem; }
    
    /* 业务场景卡片 */
    .scenario-card {
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.1) 100%);
        border: 2px solid transparent;
        border-radius: 16px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s;
        text-align: center;
    }
    
    .scenario-card:hover {
        border-color: #6366f1;
        background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.2) 100%);
        transform: translateY(-3px);
    }
    
    .scenario-icon { font-size: 2.5rem; margin-bottom: 0.5rem; }
    .scenario-title { font-weight: 600; color: #1e293b; font-size: 1.1rem; }
    .scenario-desc { font-size: 0.85rem; color: #64748b; margin-top: 0.5rem; }
    
    /* Skill 卡片 */
    .skill-item {
        background: #f8fafc;
        border-left: 4px solid #6366f1;
        border-radius: 8px;
        padding: 0.8rem 1rem;
        margin-bottom: 0.5rem;
        transition: all 0.2s;
    }
    
    .skill-item:hover {
        background: #f1f5f9;
        transform: translateX(5px);
    }
    
    .skill-name { font-weight: 600; color: #1e293b; }
    .skill-desc { font-size: 0.8rem; color: #64748b; }
    
    /* Agent 徽章 */
    .agent-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 100px;
        font-weight: 500;
        font-size: 0.9rem;
        margin: 0.25rem;
    }
    
    /* Workflow 时间线 */
    .workflow-step {
        position: relative;
        padding-left: 2rem;
        padding-bottom: 1rem;
        border-left: 2px solid #e2e8f0;
    }
    
    .workflow-step::before {
        content: '';
        position: absolute;
        left: -6px;
        top: 0;
        width: 10px;
        height: 10px;
        background: #6366f1;
        border-radius: 50%;
    }
    
    /* 渐变分隔线 */
    .gradient-divider {
        height: 3px;
        background: linear-gradient(90deg, #6366f1, #8b5cf6, #d946ef, #f59e0b);
        border-radius: 3px;
        margin: 2rem 0;
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%);
    }
    
    /* 项目卡片 */
    .project-card {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.75rem;
    }
    
    .project-name { font-weight: 600; color: #1e293b; }
    .project-type { font-size: 0.75rem; color: #6366f1; background: #eef2ff; padding: 0.2rem 0.5rem; border-radius: 4px; }
    
    /* 任务执行器 */
    .executor-box {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 20px;
        padding: 2rem;
        border: 1px solid #e2e8f0;
    }
    
    /* 动画 */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in { animation: fadeIn 0.5s ease-out; }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载 ====================

@st.cache_resource(ttl=300)
def load_all_data():
    """加载所有数据"""
    data = {
        "skills": {},
        "agents": {},
        "workflows": {},
        "projects": [],
        "categories": {},
        "stats": {}
    }
    
    try:
        # 加载增强版 Skill Loader
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "skills_bridge"))
        from enhanced_skill_loader import EnhancedSkillLoader
        
        loader = EnhancedSkillLoader(
            skills_path=PROJECT_ROOT / "leo_skills",
            workflows_path=PROJECT_ROOT / "leo_workflows" / "workflows"
        )
        loader.discover_all()
        
        data["skills"] = loader.skills
        data["workflows"] = loader.workflows
        data["categories"] = loader.categories
        data["stats"]["skills_count"] = len(loader.skills)
        data["stats"]["workflows_count"] = len(loader.workflows)
        data["stats"]["categories_count"] = len(loader.categories)
    except Exception as e:
        st.error(f"Skills 加载错误: {e}")
    
    try:
        # 加载 Agents
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "agents"))
        from agent_discovery import AgentDiscovery
        
        discovery = AgentDiscovery(PROJECT_ROOT / "leo_subagents" / "agents")
        data["agents"] = discovery.discover_all()
        data["stats"]["agents_count"] = len(data["agents"])
    except Exception as e:
        data["stats"]["agents_count"] = 0
    
    # 加载项目
    projects_dir = PROJECT_ROOT / "projects"
    if projects_dir.exists():
        for item in projects_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                data["projects"].append({
                    "name": item.name,
                    "path": str(item),
                    "type": "miniprogram" if "miniprogram" in item.name else "business"
                })
    
    return data


# ==================== 业务场景定义 ====================

BUSINESS_SCENARIOS = [
    {
        "icon": "🏠",
        "title": "房产项目营销",
        "desc": "营销文档、项目分析、资讯发布",
        "agents": ["realestate-agent", "creative-agent"],
        "workflows": ["content-pipeline"],
        "skills": ["project-marketing-doc-generator-cskill", "realestate-news-publisher-cskill"]
    },
    {
        "icon": "🥬",
        "title": "菜场项目管理",
        "desc": "摊位销售、项目资料、客户管理",
        "agents": ["task-agent", "research-agent"],
        "workflows": ["research-pipeline"],
        "skills": ["project-marketing-doc-generator-cskill", "data-analyzer-cskill"]
    },
    {
        "icon": "📱",
        "title": "小程序开发",
        "desc": "裂变小程序、前后端开发、部署",
        "agents": ["frontend-agent", "backend-agent", "devops-agent"],
        "workflows": ["miniprogram-dev-pipeline", "fullstack-dev-pipeline"],
        "skills": ["miniprogram-page-generator-cskill", "flask-api-generator-cskill"]
    },
    {
        "icon": "🔬",
        "title": "市场研究",
        "desc": "行业分析、竞品调研、数据报告",
        "agents": ["research-agent", "analysis-agent"],
        "workflows": ["research-pipeline", "analysis-pipeline"],
        "skills": ["research-assistant-cskill", "data-analyzer-cskill"]
    },
    {
        "icon": "📝",
        "title": "内容创作",
        "desc": "公众号文章、排版、多平台发布",
        "agents": ["creative-agent", "task-agent"],
        "workflows": ["content-pipeline"],
        "skills": ["content-layout-leo-cskill"]
    },
    {
        "icon": "🛡️",
        "title": "代码安全",
        "desc": "安全扫描、漏洞检测、代码审计",
        "agents": ["security-agent", "test-agent"],
        "workflows": ["api-pipeline"],
        "skills": ["security-scan-cskill", "unit-test-generator-cskill"]
    }
]


# ==================== 页面组件 ====================

def render_header():
    """渲染页头"""
    st.markdown('<h1 class="hero-title animate-in">🚀 Leo AI 智能工作台</h1>', unsafe_allow_html=True)
    st.markdown(f'''
    <p class="hero-subtitle animate-in">
        Skills + Agents + Workflows 协同工作 | 
        {datetime.now().strftime("%Y年%m月%d日 %H:%M")}
    </p>
    ''', unsafe_allow_html=True)


def render_metrics(data):
    """渲染统计指标"""
    col1, col2, col3, col4, col5 = st.columns(5)
    
    stats = data.get("stats", {})
    
    with col1:
        st.markdown(f'''
        <div class="metric-card">
            <div class="metric-value">{stats.get("skills_count", 0)}</div>
            <div class="metric-label">🎯 Skills 技能</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col2:
        st.markdown(f'''
        <div class="metric-card green">
            <div class="metric-value">{stats.get("agents_count", 0)}</div>
            <div class="metric-label">🤖 Agents 代理</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col3:
        st.markdown(f'''
        <div class="metric-card orange">
            <div class="metric-value">{stats.get("workflows_count", 0)}</div>
            <div class="metric-label">⚡ Workflows</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col4:
        st.markdown(f'''
        <div class="metric-card pink">
            <div class="metric-value">{stats.get("categories_count", 0)}</div>
            <div class="metric-label">📁 分类</div>
        </div>
        ''', unsafe_allow_html=True)
    
    with col5:
        st.markdown(f'''
        <div class="metric-card cyan">
            <div class="metric-value">{len(data.get("projects", []))}</div>
            <div class="metric-label">📂 项目</div>
        </div>
        ''', unsafe_allow_html=True)


def render_business_scenarios():
    """渲染业务场景快捷入口"""
    st.markdown("### 🎯 业务场景快捷入口")
    
    cols = st.columns(3)
    for i, scenario in enumerate(BUSINESS_SCENARIOS):
        with cols[i % 3]:
            if st.button(
                f"{scenario['icon']} {scenario['title']}", 
                key=f"scenario_{i}",
                use_container_width=True
            ):
                st.session_state.selected_scenario = scenario
            st.caption(scenario['desc'])


def render_selected_scenario():
    """渲染选中的业务场景详情"""
    if 'selected_scenario' not in st.session_state:
        return
    
    scenario = st.session_state.selected_scenario
    
    st.markdown(f"### {scenario['icon']} {scenario['title']} - 推荐配置")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**推荐 Agents:**")
        for agent in scenario['agents']:
            st.markdown(f'<span class="agent-badge">🤖 {agent}</span>', unsafe_allow_html=True)
        
        st.markdown("**推荐 Workflows:**")
        for wf in scenario['workflows']:
            st.markdown(f"- ⚡ {wf}")
    
    with col2:
        st.markdown("**推荐 Skills:**")
        for skill in scenario['skills']:
            st.markdown(f"- 📦 {skill}")
    
    if st.button("🚀 使用此配置执行任务", type="primary"):
        st.success("已加载推荐配置，请在下方任务执行器中输入具体任务")


def render_skills_panel(data):
    """渲染 Skills 面板"""
    st.markdown("### 📚 Skills 技能库")
    
    categories = data.get("categories", {})
    skills = data.get("skills", {})
    
    if not categories:
        st.info("暂无 Skills")
        return
    
    # 分类标签
    sorted_cats = sorted(categories.keys())
    
    tabs = st.tabs([f"{cat} ({len(categories[cat])})" for cat in sorted_cats])
    
    for tab, cat in zip(tabs, sorted_cats):
        with tab:
            skill_names = categories[cat]
            
            # 搜索
            search = st.text_input("🔍 搜索", key=f"search_{cat}", placeholder="输入关键词...")
            
            if search:
                skill_names = [s for s in skill_names if search.lower() in s.lower()]
            
            # 分页
            page_size = 8
            total = len(skill_names)
            pages = max(1, (total + page_size - 1) // page_size)
            
            if total > page_size:
                page = st.slider("页码", 1, pages, 1, key=f"page_{cat}") - 1
            else:
                page = 0
            
            start, end = page * page_size, (page + 1) * page_size
            
            for skill_name in skill_names[start:end]:
                skill = skills.get(skill_name)
                desc = skill.description[:80] if skill and skill.description else "暂无描述"
                st.markdown(f'''
                <div class="skill-item">
                    <div class="skill-name">📦 {skill_name}</div>
                    <div class="skill-desc">{desc}...</div>
                </div>
                ''', unsafe_allow_html=True)
            
            st.caption(f"显示 {start+1}-{min(end, total)} / 共 {total} 个")


def render_agents_panel(data):
    """渲染 Agents 面板"""
    st.markdown("### 🤖 Agents 代理库")
    
    agents = data.get("agents", {})
    
    if not agents:
        st.info("暂无 Agents")
        return
    
    for name, meta in agents.items():
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**🤖 {name}**")
                st.caption(f"类型: {meta.type} | {meta.description[:50] if meta.description else '智能代理'}...")
            with col2:
                st.markdown("🟢 就绪")


def render_workflows_panel(data):
    """渲染 Workflows 面板"""
    st.markdown("### ⚡ Workflows 工作流")
    
    workflows = data.get("workflows", {})
    
    if not workflows:
        st.info("暂无 Workflows")
        return
    
    for name, wf in workflows.items():
        with st.expander(f"⚡ {name}", expanded=False):
            st.markdown(f"**{wf.description}**")
            if wf.steps:
                for i, step in enumerate(wf.steps, 1):
                    step_name = step.get('name', str(step)) if isinstance(step, dict) else str(step)
                    st.markdown(f"{i}. {step_name}")


def render_projects_panel(data):
    """渲染项目面板"""
    st.markdown("### 📂 我的项目")
    
    projects = data.get("projects", [])
    
    if not projects:
        st.info("暂无项目")
        return
    
    for proj in projects:
        st.markdown(f'''
        <div class="project-card">
            <span class="project-name">📁 {proj["name"]}</span>
            <span class="project-type">{proj["type"]}</span>
        </div>
        ''', unsafe_allow_html=True)


def render_task_executor(data):
    """渲染任务执行器"""
    st.markdown("### 🚀 任务执行器")
    
    st.markdown('<div class="executor-box">', unsafe_allow_html=True)
    
    with st.form("task_form"):
        task = st.text_area(
            "📝 任务描述",
            placeholder="例如：为建华观园项目生成营销文档...",
            height=100
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            agents = ["🔮 自动选择"] + [f"🤖 {a}" for a in data.get("agents", {}).keys()]
            agent = st.selectbox("选择 Agent", agents)
        
        with col2:
            workflows = ["不使用"] + [f"⚡ {w}" for w in data.get("workflows", {}).keys()]
            workflow = st.selectbox("选择 Workflow", workflows)
        
        with col3:
            projects = ["无"] + [f"📁 {p['name']}" for p in data.get("projects", [])]
            project = st.selectbox("关联项目", projects)
        
        submitted = st.form_submit_button("🚀 执行任务", type="primary", use_container_width=True)
        
        if submitted and task:
            with st.spinner("执行中..."):
                st.success("✅ 任务已提交！")
                st.json({
                    "task": task[:100],
                    "agent": agent,
                    "workflow": workflow,
                    "project": project,
                    "status": "queued",
                    "timestamp": datetime.now().isoformat()
                })
    
    st.markdown('</div>', unsafe_allow_html=True)


def render_sidebar(data):
    """渲染侧边栏"""
    with st.sidebar:
        st.markdown("## 🚀 Leo AI System")
        st.markdown("**v3.0** | 智能工作台")
        
        st.markdown("---")
        
        # 快速统计
        stats = data.get("stats", {})
        st.markdown("### 📊 系统概览")
        st.markdown(f"- Skills: **{stats.get('skills_count', 0)}** 个")
        st.markdown(f"- Agents: **{stats.get('agents_count', 0)}** 个")
        st.markdown(f"- Workflows: **{stats.get('workflows_count', 0)}** 个")
        st.markdown(f"- 项目: **{len(data.get('projects', []))}** 个")
        
        st.markdown("---")
        
        # 快捷操作
        st.markdown("### ⚡ 快捷操作")
        
        if st.button("🔄 刷新数据", use_container_width=True):
            st.cache_resource.clear()
            st.rerun()
        
        if st.button("📊 系统状态", use_container_width=True):
            st.info(f"运行正常 | {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # 文档链接
        st.markdown("### 📚 文档")
        st.markdown("- [📖 系统文档](LEO_SYSTEM_README.md)")
        st.markdown("- [📋 技能清单](SKILLS_MANIFEST.md)")
        
        st.markdown("---")
        
        # 用户信息
        st.markdown("### 👤 Leo Liu")
        st.markdown("*房产 | AI眼镜 | 菜场*")
        st.caption("© 2026 Leo AI System")


# ==================== 主程序 ====================

def main():
    """主程序"""
    # 加载数据
    data = load_all_data()
    
    # 侧边栏
    render_sidebar(data)
    
    # 页头
    render_header()
    
    # 指标
    render_metrics(data)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # 业务场景
    render_business_scenarios()
    render_selected_scenario()
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # 主内容区
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        render_skills_panel(data)
    
    with col_right:
        render_agents_panel(data)
        st.markdown("---")
        render_workflows_panel(data)
        st.markdown("---")
        render_projects_panel(data)
    
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    
    # 任务执行器
    render_task_executor(data)
    
    # 页脚
    st.markdown('<div class="gradient-divider"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; color: #64748b; padding: 1rem;">
        🚀 Leo AI Agent System v3.0 | Built with ❤️ by Leo Liu | Powered by Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
