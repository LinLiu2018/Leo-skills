"""
Leo Web UI 主程序
=================
Leo AI 智能工作台的 Streamlit 入口。
路径: leo_interface/web/app.py
"""

import sys
import time
from datetime import datetime

# 标准库导入成功前提：已执行 pip install -e .
try:
    import streamlit as st
    from streamlit_autorefresh import st_autorefresh
    
    # 核心包导入
    from leo_system import get_system
    from leo_subagents.core.meta_skills import get_meta_manager
    from leo_subagents.core.task_executor import get_executor
    from leo_subagents.skills_bridge.enhanced_skill_loader import get_enhanced_loader
except ImportError as e:
    import os
    # 如果标准导入失败（开发环境下可能发生），尝试回退到路径追加模式
    # 这确保了在未完全安装环境下的鲁棒性
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        import streamlit as st
        from streamlit_autorefresh import st_autorefresh
        from leo_system import get_system
        from leo_subagents.core.meta_skills import get_meta_manager
        from leo_subagents.core.task_executor import get_executor
        from leo_subagents.skills_bridge.enhanced_skill_loader import get_enhanced_loader
    except ImportError as final_e:
        print(f"❌ 严重错误: 无法加载核心组件。请确保在项目根目录运行了 `pip install -e .`\n详情: {final_e}")
        sys.exit(1)

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="Leo AI 实战工作台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自动刷新（用于实时日志）
count = st_autorefresh(interval=2000, limit=None, key="log_refresh")

# ==================== 样式 ====================

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    code {
        font-family: 'JetBrains Mono', monospace;
    }

    .meta-card {
        background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
        color: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #334155;
        height: 100%;
        transition: transform 0.2s;
    }
    
    .meta-card:hover { transform: translateY(-3px); }
    .meta-title { font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; color: #38bdf8; }
    .meta-desc { font-size: 0.9rem; color: #94a3b8; }
    
    .terminal-box {
        background: #0f172a;
        color: #38bdf8;
        font-family: 'JetBrains Mono', monospace;
        padding: 1rem;
        border-radius: 8px;
        height: 300px;
        overflow-y: auto;
        border: 1px solid #1e293b;
        font-size: 0.85rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载 ====================

@st.cache_resource
def load_core_modules():
    """加载核心模块"""
    try:
        system = get_system()
        # 确保元技能管理器持有系统引用
        meta_manager = get_meta_manager()
        if not meta_manager.system:
            meta_manager.system = system
            
        executor = get_executor()
        if not executor.system:
            executor.system = system
            
        return {
            "system": system,
            "meta": meta_manager,
            "executor": executor,
            "loader": get_enhanced_loader(),
            # 获取 Agents 列表（通过系统实例）
            "agents": system.agents
        }
    except Exception as e:
        return {"error": str(e)}

core = load_core_modules()


# ==================== 功能模块 ====================

def render_meta_skills_engine():
    """渲染元技能引擎面板"""
    st.markdown("### ⚡ 元技能引擎 (Meta-Skills Engine)")
    st.markdown("系统的自我进化中心，用于创建新能力和优化现有能力。")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="meta-card">
            <div class="meta-title">🔨 技能工坊</div>
            <div class="meta-desc">创建新的 Agent 技能。描述你的需求，自动生成代码、配置和文档。</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("启动技能工坊", key="btn_workshop", use_container_width=True):
            st.session_state.current_view = "workshop"
            st.rerun()
            
    with col2:
        st.markdown("""
        <div class="meta-card">
            <div class="meta-title">🧬 进化实验室</div>
            <div class="meta-desc">优化现有技能。提供反馈，自动重构代码和改进逻辑。</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("启动进化实验", key="btn_evolution", use_container_width=True):
            st.session_state.current_view = "evolution"
            st.rerun()
            
    with col3:
        st.markdown("""
        <div class="meta-card">
            <div class="meta-title">🧠 提示词优化</div>
            <div class="meta-desc">优化 Claude 提示词。提升准确性、鲁棒性和创造力。</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("优化提示词", key="btn_optimizer", use_container_width=True):
            st.session_state.current_view = "optimizer"
            st.rerun()


def render_skill_workshop():
    """技能工坊界面"""
    st.markdown("#### 🔨 技能工坊 (Skill Workshop)")
    
    with st.expander("ℹ️ 帮助与说明", expanded=True):
        st.info("基于 `agent-skill-creator` 元技能。此工具将为您自动生成完整的 Skill 目录结构、代码和配置。")
    
    with st.form("create_skill_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("技能名称 (英文)", placeholder="e.g. video-transcriber-cskill")
            domain = st.selectbox("领域", ["backend", "frontend", "data-analysis", "automation", "tools"])
        with col2:
            desc = st.text_input("简短描述", placeholder="e.g. Transcribe videos using Whisper API")
            interactive = st.checkbox("交互式创建 mode", value=False)
            
        requirements = st.text_area("详细需求描述", height=150, placeholder="描述该技能具体需要做什么、输入输出是什么、使用什么库或API...")
        
        submitted = st.form_submit_button("🚀 开始创建技能", type="primary")
        
        if submitted and name and requirements:
            with st.spinner(f"正在调用元技能创建 {name}..."):
                result = core["meta"].create_skill(name, desc, domain, requirements, interactive)
                if result.get("success"):
                    st.success("✅ 技能创建指令已发送！")
                    st.json(result)
                else:
                    st.error(f"❌ 创建失败: {result.get('error')}")


def render_task_monitor():
    """任务监控与日志"""
    st.markdown("### 📡 任务监控 (Real-time Monitor)")
    
    executor = core.get("executor")
    if not executor:
        st.warning("任务执行器未就绪")
        return
    
    tasks = executor.tasks
    if not tasks:
        st.info("暂无活动任务")
    else:
        sorted_tasks = sorted(tasks.values(), key=lambda x: x['created_at'], reverse=True)[:5]
        
        for task in sorted_tasks:
            status = task.get("status", "unknown")
            with st.expander(f"[{status.upper()}] {task['description'][:50]}...", expanded=(status == 'running')):
                st.caption(f"ID: {task['id']} | Agent: {task['agent']} | Time: {task['created_at'].strftime('%H:%M:%S')}")
                
                logs = task.get("logs", [])
                log_text = "\n".join(logs)
                st.code(log_text, language="bash")
                
                if task.get("result"):
                    st.json(task["result"])


def render_execution_panel():
    """主执行面板"""
    st.markdown("### 🚀 任务执行 (Task Execution)")
    
    with st.form("execution_form"):
        task_input = st.text_area("输入任务指令", height=100, placeholder="描述要做什么...")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            agent_list = list(core["agents"].keys()) if "agents" in core else []
            agents = ["🔮 自动选择"] + [f"🤖 {name}" for name in agent_list]
            agent = st.selectbox("选择 Agent", agents)
        with col2:
            workflow_list = list(core["loader"].workflows.keys()) if "loader" in core else []
            workflows = ["不使用 Workflow"] + [f"⚡ {name}" for name in workflow_list]
            workflow = st.selectbox("选择 Workflow", workflows)
        with col3:
            # TODO: 实现真实的项目加载
            projects = ["无关联项目", "演示项目A"] 
            project = st.selectbox("上下文项目", projects)
            
        submitted = st.form_submit_button("🚀 立即执行", type="primary", use_container_width=True)
        
        if submitted and task_input:
            executor = core["executor"]
            task_id = executor.submit_task(
                task_description=task_input,
                agent_name=agent,
                workflow_name=workflow,
                project_context=project
            )
            st.success(f"✅ 任务已提交 (ID: {task_id})")
            time.sleep(0.5)
            st.rerun()



# ==================== 资源库视图 (Resource Library) ====================

def render_resource_library():
    """渲染资源库主视图"""
    st.markdown("### 📚 资源库 (Resource Library)")
    st.markdown("查看和管理系统中的所有能力资产。")
    
    tab1, tab2, tab3 = st.tabs(["📦 技能库 (Skills)", "🤖 代理库 (Agents)", "⚡ 工作流 (Workflows)"])
    
    # --- Tab 1: 技能库 ---
    with tab1:
        skills = core["loader"].skills if "loader" in core else {}
        categories = core["loader"].categories if "loader" in core else {}
        
        if not skills:
            st.info("暂无技能数据")
        else:
            # 搜索框
            search_query = st.text_input("🔍 搜索技能", placeholder="输入关键词...", key="skill_search")
            
            # 1. 整理分类
            # 如果有搜索，暂不按分类折叠，直接展示列表
            if search_query:
                filtered_skills = {k: v for k, v in skills.items() if search_query.lower() in k.lower()}
                st.write(f"找到 {len(filtered_skills)} 个匹配的技能:")
                for name, skill in filtered_skills.items():
                    with st.expander(f"📦 {name}", expanded=True):
                        st.write(f"**描述**: {skill.description}")
                        st.caption(f"路径: {skill.path}")
            else:
                # 按分类展示 (Tabs inside Tab)
                # 使用 Streamlit 的 Tabs 来做顶层分类
                sorted_cats = sorted(categories.keys())
                cat_tabs = st.tabs([f"{c} ({len(categories[c])})" for c in sorted_cats])
                
                for idx, cat in enumerate(sorted_cats):
                    with cat_tabs[idx]:
                        skill_names = categories[cat]
                        for name in skill_names:
                            skill = skills.get(name)
                            if skill:
                                with st.expander(f"📦 {name}"):
                                    st.write(f"**描述**: {skill.description}")
                                    # SkillInfo 对象没有 metadata 属性，我们改用 to_dict() 展示完整信息
                                    # 排除一些不必要的字段以保持整洁
                                    info = skill.to_dict()
                                    display_info = {k: v for k, v in info.items() if k not in ['name', 'description', 'path']}
                                    st.json(display_info, expanded=False)
                                    st.caption(f"路径: {skill.path}")

    # --- Tab 2: 代理库 ---
    with tab2:
        agents = core.get("agents", {})
        if not agents:
            st.info("暂无代理数据")
        else:
            # 1. 按类型/职能分类 Agents
            agent_types = {}
            for name, agent in agents.items():
                a_type = agent.config.type if hasattr(agent, 'config') else 'unknown'
                if a_type not in agent_types:
                    agent_types[a_type] = []
                agent_types[a_type].append(agent)
            
            for a_type, agent_list in agent_types.items():
                st.markdown(f"#### 🏷️ 类型: {a_type.capitalize()}")
                cols = st.columns(2)
                for i, agent in enumerate(agent_list):
                    with cols[i % 2]:
                        with st.container():
                            st.markdown(f"""
                            <div class="meta-card" style="padding: 1rem; margin-bottom: 1rem;">
                                <div class="meta-title">🤖 {agent.config.name}</div>
                                <div class="meta-desc">{agent.config.description or '暂无描述'}</div>
                                <div style="margin-top:0.5rem; font-size: 0.8rem; color:#64748b;">
                                    Skills: {len(agent.config.skills)} | Priority: {agent.config.priority}
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

    # --- Tab 3: 工作流 ---
    with tab3:
        workflows = core["loader"].workflows if "loader" in core else {}
        if not workflows:
            st.info("暂无工作流数据")
        else:
            # 可以按名称前缀简单归类，或者直接列表
            # 这里尝试简单归类：Content, Research, Dev 等
            for name, wf in workflows.items():
                with st.expander(f"⚡ {name}", expanded=False):
                     st.write(f"**描述**: {wf.description}")
                     st.markdown("**步骤流程:**")
                     for i, step in enumerate(wf.steps, 1):
                         # 兼容不同的 step 格式
                         step_name = step.get('name', '未命名步骤') if isinstance(step, dict) else str(step)
                         step_desc = step.get('description', '') if isinstance(step, dict) else ''
                         st.markdown(f"{i}. **{step_name}** - {step_desc}")


# ==================== 主程序 ====================

def main():
    if "current_view" not in st.session_state:
        st.session_state.current_view = "dashboard"
        
    # 侧边栏导航
    with st.sidebar:
        st.title("⚡ Leo工作台")
        
        if st.button("📊 仪表盘", use_container_width=True):
            st.session_state.current_view = "dashboard"
            st.rerun()
        if st.button("🔨 技能工坊", use_container_width=True):
            st.session_state.current_view = "workshop"
            st.rerun()
        if st.button("📚 资源库", use_container_width=True):
            st.session_state.current_view = "resources"
            st.rerun()
        if st.button("🧬 进化实验室", use_container_width=True):
            st.session_state.current_view = "evolution"
            st.rerun()
            
        st.markdown("---")
        st.markdown("### 系统状态")
        if "error" in core:
            st.error(f"系统错误: {core['error']}")
        else:
            agent_count = len(core.get('agents', []))
            skill_count = len(core['loader'].skills) if 'loader' in core else 0
            st.success("🟢 系统运行正常")
            st.caption(f"Skills: {skill_count}")
            st.caption(f"Agents: {agent_count}")

    # 主视图路由
    view = st.session_state.current_view
    
    if view == "dashboard":
        render_meta_skills_engine()
        st.markdown("---")
        render_execution_panel()
        st.markdown("---")
        render_task_monitor()
        
    elif view == "workshop":
        if st.button("← 返回仪表盘"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        render_skill_workshop()

    elif view == "resources":
        render_resource_library()
        
    elif view == "evolution":
        if st.button("← 返回仪表盘"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        st.info("进化实验室功能正在开发中...")



if __name__ == "__main__":
    main()
