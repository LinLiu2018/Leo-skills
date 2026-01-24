"""
Leo System Web UI v4.0 - 实战进化版
=====================================
集成元技能引擎和真实执行器，系统真正可用

功能特点:
- ⚡ 元技能引擎：专门的技能工坊和进化实验室
- [LAUNCH] 真实执行：连接后台执行器，实时日志流
- 📂 工作区：文件预览和管理
- [BUILD] 完整业务场景支持

运行: streamlit run leo_web_ui_v4.py
"""

import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.absolute()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import streamlit as st
    from streamlit_autorefresh import st_autorefresh
except ImportError:
    print("[ERROR] 请先安装依赖: pip install streamlit streamlit-autorefresh")
    sys.exit(1)

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="Leo AI 实战工作台 v4.0",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# 自动刷新（用于实时日志）
count = st_autorefresh(interval=2000, limit=None, key="fizzbuzz")

# ==================== 样式 ====================

st.markdown(
    """
<style>
    /* 引入字体 */
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500&family=Inter:wght@400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    code {
        font-family: 'JetBrains Mono', monospace;
    }

    /* 顶部导航栏 */
    .top-nav {
        background: white;
        padding: 1rem;
        border-bottom: 1px solid #e2e8f0;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    /* 元技能卡片 */
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

    /* 执行日志终端风 */
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

    /* 状态指示器 */
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .running { background-color: #fbbf24; box-shadow: 0 0 5px #fbbf24; }
    .completed { background-color: #10b981; box-shadow: 0 0 5px #10b981; }
    .failed { background-color: #ef4444; box-shadow: 0 0 5px #ef4444; }

</style>
""",
    unsafe_allow_html=True,
)


# ==================== 数据加载 ====================


@st.cache_resource
def load_core_modules():
    """加载核心模块"""
    try:
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "core"))
        from meta_skills import get_meta_manager
        from task_executor import get_executor

        # 加载 Skills/Agents 数据
        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "skills_bridge"))
        from enhanced_skill_loader import get_enhanced_loader

        sys.path.insert(0, str(PROJECT_ROOT / "leo_subagents" / "agents"))
        from agent_discovery import get_discovery

        return {
            "meta": get_meta_manager(),
            "executor": get_executor(),
            "loader": get_enhanced_loader(),
            "agents": get_discovery().discover_all(),
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

    # 技能工坊
    with col1:
        st.markdown(
            """
        <div class="meta-card">
            <div class="meta-title">🔨 技能工坊</div>
            <div class="meta-desc">创建新的 Agent 技能。描述你的需求，自动生成代码、配置和文档。</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("启动技能工坊", key="btn_workshop", use_container_width=True):
            st.session_state.current_view = "workshop"

    # 进化实验室
    with col2:
        st.markdown(
            """
        <div class="meta-card">
            <div class="meta-title">🧬 进化实验室</div>
            <div class="meta-desc">优化现有技能。提供反馈，自动重构代码和改进逻辑。</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("启动进化实验", key="btn_evolution", use_container_width=True):
            st.session_state.current_view = "evolution"

    # 提示词优化器
    with col3:
        st.markdown(
            """
        <div class="meta-card">
            <div class="meta-title">🧠 提示词优化</div>
            <div class="meta-desc">优化 Claude 提示词。提升准确性、鲁棒性和创造力。</div>
        </div>
        """,
            unsafe_allow_html=True,
        )
        if st.button("优化提示词", key="btn_optimizer", use_container_width=True):
            st.session_state.current_view = "optimizer"


def render_skill_workshop():
    """技能工坊界面"""
    st.markdown("#### 🔨 技能工坊 (Skill Workshop)")

    with st.expander("ℹ️ 帮助与说明", expanded=True):
        st.info(
            "基于 `agent_skill_creator_skill` 元技能。此工具将为您自动生成完整的 Skill 目录结构、代码和配置。"
        )

    with st.form("create_skill_form"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("技能名称 (英文)", placeholder="e.g. video-transcriber-cskill")
            domain = st.selectbox(
                "领域", ["backend", "frontend", "data-analysis", "automation", "tools"]
            )
        with col2:
            desc = st.text_input("简短描述", placeholder="e.g. Transcribe videos using Whisper API")
            interactive = st.checkbox("交互式创建 mode", value=False)

        requirements = st.text_area(
            "详细需求描述",
            height=150,
            placeholder="描述该技能具体需要做什么、输入输出是什么、使用什么库或API...",
        )

        submitted = st.form_submit_button("[LAUNCH] 开始创建技能", type="primary")

        if submitted and name and requirements:
            with st.spinner(f"正在调用元技能创建 {name}..."):
                # 调用元技能管理器
                result = core["meta"].create_skill(name, desc, domain, requirements, interactive)
                if result["success"]:
                    st.success("[SUCCESS] 技能创建指令已发送！")
                    st.json(result)
                else:
                    st.error(f"[ERROR] 创建失败: {result['error']}")


def render_task_monitor():
    """任务监控与日志"""
    st.markdown("### 📡 任务监控 (Real-time Monitor)")

    executor = core["executor"]

    # 任务列表
    tasks = executor.tasks
    if not tasks:
        st.info("暂无活动任务")
    else:
        # 只显示最近的 5 个任务
        sorted_tasks = sorted(tasks.values(), key=lambda x: x["created_at"], reverse=True)[:5]

        for task in sorted_tasks:
            status_color = {
                "queued": "gray",
                "running": "orange",
                "completed": "green",
                "failed": "red",
            }.get(task["status"], "gray")

            with st.expander(
                f"[{task['status'].upper()}] {task['description'][:50]}...",
                expanded=(task["status"] == "running"),
            ):
                st.caption(
                    f"ID: {task['id']} | Agent: {task['agent']} | Time: {task['created_at'].strftime('%H:%M:%S')}"
                )

                # 显示日志
                logs = task.get("logs", [])
                log_text = "\n".join(logs)
                st.code(log_text, language="bash")

                if task["result"]:
                    st.json(task["result"])


def render_execution_panel():
    """主执行面板"""
    st.markdown("### [LAUNCH] 任务执行 (Task Execution)")

    with st.form("execution_form"):
        task_input = st.text_area("输入任务指令", height=100, placeholder="描述要做什么...")

        col1, col2, col3 = st.columns(3)
        with col1:
            agents = ["🔮 自动选择"] + [f"🤖 {name}" for name in core["agents"].keys()]
            agent = st.selectbox("选择 Agent", agents)
        with col2:
            workflows = ["不使用 Workflow"] + [
                f"⚡ {name}" for name in core["loader"].workflows.keys()
            ]
            workflow = st.selectbox("选择 Workflow", workflows)
        with col3:
            projects = (
                ["无关联项目"] + [p["name"] for p in core.get("projects", [])]
                if "projects" in core
                else ["无关联项目"]
            )
            project = st.selectbox("上下文项目", projects)

        submitted = st.form_submit_button(
            "[LAUNCH] 立即执行", type="primary", use_container_width=True
        )

        if submitted and task_input:
            # 提交到真实执行器
            task_id = core["executor"].submit_task(
                task_description=task_input,
                agent_name=agent,
                workflow_name=workflow,
                project_context=project,
            )
            st.success(f"[SUCCESS] 任务已提交 (ID: {task_id})")
            time.sleep(0.5)
            st.rerun()


# ==================== 主程序 ====================


def main():
    if "current_view" not in st.session_state:
        st.session_state.current_view = "dashboard"

    # 侧边栏导航
    with st.sidebar:
        st.title("⚡ Leo工作台 v4.0")

        if st.button("[DATA] 仪表盘", use_container_width=True):
            st.session_state.current_view = "dashboard"
        if st.button("🔨 技能工坊", use_container_width=True):
            st.session_state.current_view = "workshop"
        if st.button("🧬 进化实验室", use_container_width=True):
            st.session_state.current_view = "evolution"

        st.markdown("---")
        st.markdown("### 系统状态")
        if "error" in core:
            st.error(f"系统错误: {core['error']}")
        else:
            st.success("🟢 系统运行正常")
            st.caption(f"Skills: {len(core['loader'].skills)}")
            st.caption(f"Agents: {len(core['agents'])}")

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

    elif view == "evolution":
        if st.button("← 返回仪表盘"):
            st.session_state.current_view = "dashboard"
            st.rerun()
        st.info("进化实验室功能开发中...")


if __name__ == "__main__":
    main()
