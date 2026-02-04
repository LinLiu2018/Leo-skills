"""
Leo Web UI 主程序 v2.1
======================
Leo AI 智能工作台 - 中文优化版
基于 2026 UX 最佳实践重构
"""

import sys
import os

# 先设置路径，确保模块可以被找到
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
src_path = os.path.join(project_root, "src")
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# 导入依赖
try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
    import pandas as pd
    from leo_subagents.skills_bridge.enhanced_skill_loader import get_enhanced_loader
except ImportError as e:
    print(f"[ERROR] 无法加载核心组件: {e}")
    sys.exit(1)

# ==================== 中文描述映射 ====================

# 分类中文名称
CATEGORY_CN = {
    "backend": "后端开发",
    "frontend": "前端开发",
    "tools": "开发工具",
    "utilities": "实用工具",
    "automation": "自动化",
    "content_creation": "内容创作",
    "business": "商业应用",
    "devops": "运维部署",
    "scaffold": "项目脚手架",
    "testing": "测试工具",
    "security": "安全工具",
    "intelligence": "智能分析",
    "development": "开发辅助",
    "core": "核心功能",
    "general": "通用技能",
}

# 技能中文描述
SKILL_CN = {
    # 后端技能
    "flask_api_generator_skill": ("Flask API 生成器", "自动生成 Flask RESTful API 代码，包含路由、模型和蓝图"),
    "database_migration_skill": ("数据库迁移工具", "管理数据库版本迁移，支持 SQLAlchemy 和 Alembic"),
    "database_model_generator_skill": ("数据库模型生成器", "根据需求自动生成 SQLAlchemy ORM 模型"),
    "flask_auth_generator_skill": ("Flask 认证生成器", "生成用户认证模块，支持 JWT 和 Session"),
    "fastapi_endpoint_generator_skill": ("FastAPI 端点生成器", "快速创建 FastAPI 异步 API 端点"),

    # 前端技能
    "miniprogram_page_generator_skill": ("小程序页面生成器", "生成微信小程序页面，包含 WXML/WXSS/JS"),
    "react_component_generator_skill": ("React 组件生成器", "创建 React 函数组件，支持 Hooks"),
    "vue_component_generator_skill": ("Vue 组件生成器", "生成 Vue 3 组合式 API 组件"),
    "css_layout_generator_skill": ("CSS 布局生成器", "生成响应式 CSS 布局代码"),
    "vant_weapp_skill": ("Vant Weapp 组件", "使用 Vant UI 库创建小程序组件"),
    "weui_miniprogram_skill": ("WeUI 小程序组件", "使用 WeUI 样式库开发小程序"),
    "miniprogram_component_generator_skill": ("小程序组件生成器", "创建可复用的小程序自定义组件"),
    "vue_page_generator_skill": ("Vue 页面生成器", "生成完整的 Vue 页面模板"),

    # 内容创作
    "content_layout_leo_skill": ("内容排版工具", "自动排版公众号文章，支持多种样式模板"),
    "project_marketing_doc_generator_skill": ("营销文档生成器", "生成项目营销文案、宣传材料"),
    "realestate_news_publisher_skill": ("房产资讯发布器", "采集和发布房产行业新闻资讯"),
    "text_generator_skill": ("文本生成器", "AI 驱动的文本内容生成工具"),
    "image_generator_skill": ("图片生成器", "AI 图片生成，支持多种风格"),

    # 开发工具
    "agent_skill_creator_skill": ("技能创建器", "元技能：自动创建新的 Agent 技能"),
    "subagent_creator_skill": ("子代理创建器", "创建和配置新的 AI 子代理"),
    "article_to_prototype_skill": ("文章转原型", "将技术文章转换为可执行的代码原型"),
    "skill_code_generator_skill": ("技能代码生成器", "自动生成技能的核心代码逻辑"),

    # DevOps
    "dockerfile_generator_skill": ("Dockerfile 生成器", "自动生成 Docker 容器配置文件"),
    "docker_compose_generator_skill": ("Docker Compose 生成器", "生成多容器编排配置"),
    "github_actions_generator_skill": ("GitHub Actions 生成器", "创建 CI/CD 工作流配置"),
    "nginx_config_generator_skill": ("Nginx 配置生成器", "生成 Nginx 反向代理配置"),

    # 脚手架
    "flask_api_scaffold_skill": ("Flask 项目脚手架", "快速搭建 Flask 项目结构"),
    "fullstack_project_scaffold_skill": ("全栈项目脚手架", "一键生成前后端分离项目"),
    "t3_stack_scaffold_skill": ("T3 Stack 脚手架", "创建 Next.js + tRPC + Prisma 项目"),

    # 商业应用
    "fission_miniprogram": ("裂变小程序", "微信裂变营销小程序解决方案"),
    "realestate": ("房产业务模块", "房产项目管理和营销工具集"),
    "ecommerce": ("电商模块", "电商业务相关功能集合"),

    # 实用工具
    "research_assistant_skill": ("研究助手", "辅助市场调研和信息收集"),
    "business_research_skill": ("商业研究工具", "企业和行业分析研究"),
    "tech_extractor_skill": ("技术提取器", "从文档中提取技术栈信息"),
    "obsidian_sync_skill": ("Obsidian 同步", "与 Obsidian 笔记同步集成"),

    # 测试
    "unit_test_generator_skill": ("单元测试生成器", "自动生成 Python 单元测试代码"),
    "api_test_generator_skill": ("API 测试生成器", "生成 API 接口测试用例"),

    # 安全
    "security_scan_skill": ("安全扫描工具", "代码安全漏洞检测和审计"),

    # 智能分析
    "twitter_monitor_skill": ("Twitter 监控", "监控 Twitter 关键词和趋势"),
    "data_analyzer_skill": ("数据分析器", "数据可视化和统计分析"),

    # 其他
    "automation": ("自动化工具", "通用自动化任务处理"),
    "evolution": ("进化模块", "技能自我优化和进化"),
}

# 工作流中文描述
WORKFLOW_CN = {
    "content-pipeline": ("内容创作流水线", "从选题到发布的完整内容创作流程"),
    "research-pipeline": ("研究分析流水线", "市场调研和竞品分析工作流"),
    "analysis-pipeline": ("数据分析流水线", "数据收集、处理和可视化流程"),
    "fullstack-dev-pipeline": ("全栈开发流水线", "前后端一体化开发工作流"),
    "miniprogram-dev-pipeline": ("小程序开发流水线", "微信小程序完整开发流程"),
    "api-pipeline": ("API 开发流水线", "RESTful API 设计和实现流程"),
    "realestate-pipeline": ("房产业务流水线", "房产项目营销和管理流程"),
    "ecommerce-pipeline": ("电商业务流水线", "电商运营和管理工作流"),
}


def get_skill_cn(name):
    """获取技能的中文名称和描述"""
    if name in SKILL_CN:
        return SKILL_CN[name]
    # 尝试模糊匹配
    for key, value in SKILL_CN.items():
        if key in name or name in key:
            return value
    return (name, "暂无中文描述")


def get_category_cn(name):
    """获取分类的中文名称"""
    return CATEGORY_CN.get(name, name)


def get_workflow_cn(name):
    """获取工作流的中文名称和描述"""
    return WORKFLOW_CN.get(name, (name, "暂无中文描述"))

# ==================== 页面配置 ====================

st.set_page_config(
    page_title="Leo AI 工作台",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"  # 默认收起侧边栏，更简洁
)

# ==================== 简洁样式 ====================

st.markdown("""
<style>
    /* 简洁现代风格 */
    .main > div { padding-top: 1rem; }

    /* 统计卡片 */
    .stat-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 12px;
        padding: 1.2rem;
        color: white;
        text-align: center;
    }
    .stat-value { font-size: 2rem; font-weight: 700; }
    .stat-label { font-size: 0.85rem; opacity: 0.9; }

    /* 快捷操作按钮 */
    .action-btn {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        text-align: center;
        transition: all 0.2s;
        cursor: pointer;
    }
    .action-btn:hover {
        border-color: #667eea;
        transform: translateY(-2px);
    }

    /* 隐藏默认元素 */
    #MainMenu, footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ==================== 数据加载 ====================

@st.cache_resource
def load_data():
    """加载系统数据"""
    try:
        loader = get_enhanced_loader()
        return {
            "loader": loader,
            "skills": loader.skills,
            "workflows": loader.workflows,
            "categories": loader.categories,
        }
    except Exception as e:
        return {"error": str(e)}


data = load_data()


# ==================== 组件函数 ====================

def render_stats_row():
    """渲染统计指标行"""
    skills_count = len(data.get("skills", {}))
    workflows_count = len(data.get("workflows", {}))
    categories_count = len(data.get("categories", {}))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("📦 技能总数", skills_count, help="已加载的技能数量")
    with col2:
        st.metric("⚡ 工作流", workflows_count, help="可用的工作流数量")
    with col3:
        st.metric("📁 分类数", categories_count, help="技能分类数量")
    with col4:
        st.metric("🟢 系统状态", "正常", help="系统运行状态")


def render_skills_chart():
    """渲染 Skills 分布图表 (Plotly 交互式)"""
    categories = data.get("categories", {})

    if not categories:
        st.info("暂无技能数据")
        return

    # 准备数据 - 使用中文分类名
    chart_data = pd.DataFrame([
        {"分类": get_category_cn(cat), "数量": len(skills)}
        for cat, skills in categories.items()
    ])

    # 创建交互式柱状图
    fig = px.bar(
        chart_data,
        x="分类",
        y="数量",
        color="数量",
        color_continuous_scale="Viridis",
        title="技能分类分布"
    )
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20),
        showlegend=False
    )
    st.plotly_chart(fig, use_container_width=True)


def render_skills_pie():
    """渲染 Skills 饼图"""
    categories = data.get("categories", {})

    if not categories:
        return

    # 使用中文分类名
    chart_data = pd.DataFrame([
        {"分类": get_category_cn(cat), "数量": len(skills)}
        for cat, skills in categories.items()
    ])

    fig = px.pie(
        chart_data,
        values="数量",
        names="分类",
        title="技能占比分布",
        hole=0.4  # 环形图
    )
    fig.update_layout(
        height=300,
        margin=dict(l=20, r=20, t=40, b=20)
    )
    st.plotly_chart(fig, use_container_width=True)


def render_quick_actions():
    """渲染快捷操作区"""
    st.subheader("⚡ 快捷操作")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("🔨 创建新技能", use_container_width=True, type="primary"):
            st.session_state.view = "create_skill"
            st.rerun()

    with col2:
        if st.button("📚 浏览资源库", use_container_width=True):
            st.session_state.view = "resources"
            st.rerun()

    with col3:
        if st.button("🔍 搜索技能", use_container_width=True):
            st.session_state.view = "search"
            st.rerun()


def render_skills_list():
    """渲染技能列表"""
    skills = data.get("skills", {})
    categories = data.get("categories", {})

    if not skills:
        st.info("暂无技能")
        return

    # 搜索框
    search = st.text_input("🔍 搜索技能", placeholder="输入关键词...")

    # 分类选择 - 使用中文名称
    cat_options = ["全部"] + [f"{get_category_cn(c)} ({c})" for c in sorted(categories.keys())]
    selected_option = st.selectbox("选择分类", cat_options)

    # 解析选择的分类
    if selected_option == "全部":
        filtered = list(skills.keys())
    else:
        # 从选项中提取英文分类名
        selected_cat = selected_option.split("(")[-1].rstrip(")")
        filtered = categories.get(selected_cat, [])

    if search:
        # 搜索时同时匹配英文名和中文名
        filtered = [s for s in filtered if search.lower() in s.lower() or search in get_skill_cn(s)[0]]

    # 显示技能
    st.caption(f"共 {len(filtered)} 个技能")

    for name in filtered[:20]:  # 限制显示数量
        skill = skills.get(name)
        if skill:
            cn_name, cn_desc = get_skill_cn(name)
            with st.expander(f"📦 {cn_name} ({name})"):
                st.markdown(f"**中文说明**: {cn_desc}")
                if skill.description and skill.description != cn_desc:
                    st.markdown(f"**原始描述**: {skill.description}")
                st.caption(f"📁 路径: {skill.path}")
                st.caption(f"路径: {skill.path}")


def render_workflows_list():
    """渲染工作流列表"""
    workflows = data.get("workflows", {})

    if not workflows:
        st.info("暂无工作流")
        return

    for name, wf in workflows.items():
        cn_name, cn_desc = get_workflow_cn(name)
        with st.expander(f"⚡ {cn_name} ({name})"):
            st.markdown(f"**中文说明**: {cn_desc}")
            if wf.description and wf.description != cn_desc:
                st.markdown(f"**原始描述**: {wf.description}")
            if wf.steps:
                st.markdown("**执行步骤:**")
                for i, step in enumerate(wf.steps, 1):
                    step_name = step.get("name", str(step)) if isinstance(step, dict) else str(step)
                    step_desc = step.get("description", "") if isinstance(step, dict) else ""
                    if step_desc:
                        st.markdown(f"{i}. **{step_name}** - {step_desc}")
                    else:
                        st.markdown(f"{i}. {step_name}")


def render_create_skill():
    """渲染创建技能表单"""
    st.subheader("🔨 创建新技能")

    if st.button("← 返回"):
        st.session_state.view = "dashboard"
        st.rerun()

    with st.form("create_skill"):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("技能名称", placeholder="my_new_skill")
            category = st.selectbox("分类", ["backend", "frontend", "tools", "automation", "content_creation"])
        with col2:
            desc = st.text_input("简短描述", placeholder="这个技能用于...")

        requirements = st.text_area("详细需求", height=150, placeholder="描述技能的具体功能...")

        if st.form_submit_button("创建技能", type="primary"):
            st.success(f"✅ 技能 '{name}' 创建请求已提交！")
            st.info("提示: 实际创建需要通过 Claude Code 执行")


# ==================== 主程序 ====================

def main():
    # 初始化视图状态
    if "view" not in st.session_state:
        st.session_state.view = "dashboard"

    # 页面标题
    st.title("⚡ Leo AI 工作台")

    # 检查错误
    if "error" in data:
        st.error(f"系统错误: {data['error']}")
        return

    # 路由
    view = st.session_state.view

    if view == "dashboard":
        # 统计指标
        render_stats_row()
        st.markdown("---")

        # 图表区
        col1, col2 = st.columns(2)
        with col1:
            render_skills_chart()
        with col2:
            render_skills_pie()

        st.markdown("---")

        # 快捷操作
        render_quick_actions()

        st.markdown("---")

        # 最近技能
        st.subheader("📦 技能概览")
        render_skills_list()

    elif view == "resources":
        st.subheader("📚 资源库")
        if st.button("← 返回"):
            st.session_state.view = "dashboard"
            st.rerun()

        tab1, tab2 = st.tabs(["📦 技能库", "⚡ 工作流"])
        with tab1:
            render_skills_list()
        with tab2:
            render_workflows_list()

    elif view == "create_skill":
        render_create_skill()

    elif view == "search":
        st.subheader("🔍 搜索技能")
        if st.button("← 返回"):
            st.session_state.view = "dashboard"
            st.rerun()
        render_skills_list()

    # 页脚
    st.markdown("---")
    st.caption("Leo AI 智能工作台 v2.1 | 简体中文版 | Powered by Streamlit & Plotly")


if __name__ == "__main__":
    main()
