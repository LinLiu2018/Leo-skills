# -*- coding: utf-8 -*-
"""
AI 学习网站生成器 - 四级进阶体系 (修复版 - 英文文件名)
"""

import json
from pathlib import Path
from datetime import datetime

# 输出目录
OUTPUT_DIR = Path("D:/桌面/leo_ai_system/output/ai_learning_site")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 四级进阶课程体系
CURRICULUM = {
    "title": "AI 学习网站 - 四级进阶体系",
    "description": "从小学到大学，系统化学习人工智能",
    "levels": [
        {
            "id": "elementary",
            "name": "小学级",
            "subtitle": "AI 启蒙阶段",
            "description": "培养对 AI 的兴趣和基础认知",
            "target": "小学生/零基础初学者",
            "duration": "3-6 个月",
            "modules": [
                {"name": "什么是 AI", "topics": ["AI 是什么", "AI 能做什么", "AI 在哪里"], "activities": ["AI 应用体验", "AI 小游戏"], "outcome": "了解 AI 基本概念"},
                {"name": "AI 好朋友", "topics": ["语音助手", "智能推荐", "图像识别"], "activities": ["和 Siri 对话", "体验人脸识别"], "outcome": "认识常见的 AI 应用"},
                {"name": "AI 小创客", "topics": ["简单编程", "图形化编程", "AI 绘画"], "activities": ["Scratch 编程", "AI 画画体验"], "outcome": "初步体验 AI 创作"}
            ],
            "resources": [{"type": "视频", "name": "AI 是什么", "url": "待添加"}, {"type": "游戏", "name": "AI 体验小游戏", "url": "待添加"}, {"type": "绘本", "name": "AI 启蒙绘本", "url": "待添加"}],
            "assessment": "完成 3 个 AI 体验活动"
        },
        {
            "id": "intermediate",
            "name": "初中级",
            "subtitle": "AI 入门阶段",
            "description": "学习 AI 基础原理和简单应用",
            "target": "初中生/有编程基础",
            "duration": "6-12 个月",
            "modules": [
                {"name": "Python 编程基础", "topics": ["Python 语法", "数据结构", "函数"], "activities": ["编写小程序", "数据处理练习"], "outcome": "掌握 Python 基础"},
                {"name": "机器学习入门", "topics": ["什么是机器学习", "监督学习", "分类与回归"], "activities": ["训练简单模型", "数据可视化"], "outcome": "理解机器学习原理"},
                {"name": "AI 项目实战", "topics": ["情感分析", "图像分类", "智能对话"], "activities": ["制作聊天机器人", "图片识别项目"], "outcome": "完成 2-3 个 AI 项目"}
            ],
            "resources": [{"type": "教程", "name": "Python 入门教程", "url": "待添加"}, {"type": "课程", "name": "机器学习入门", "url": "待添加"}, {"type": "项目", "name": "AI 实战项目集", "url": "待添加"}],
            "assessment": "完成 3 个 Python 项目和 2 个 ML 项目"
        },
        {
            "id": "advanced",
            "name": "高中级",
            "subtitle": "AI 进阶阶段",
            "description": "深入学习深度学习和专业应用",
            "target": "高中生/有 ML 基础",
            "duration": "12-18 个月",
            "modules": [
                {"name": "深度学习基础", "topics": ["神经网络", "反向传播", "优化算法"], "activities": ["搭建神经网络", "调参实验"], "outcome": "掌握深度学习原理"},
                {"name": "计算机视觉", "topics": ["CNN", "目标检测", "图像分割"], "activities": ["图像分类项目", "目标检测实战"], "outcome": "掌握 CV 核心技术"},
                {"name": "自然语言处理", "topics": ["RNN", "Transformer", "语言模型"], "activities": ["文本分类", "情感分析项目"], "outcome": "掌握 NLP 核心技术"},
                {"name": "AI 工程化", "topics": ["模型部署", "API 开发", "性能优化"], "activities": ["部署模型到云端", "开发 AI 应用"], "outcome": "具备工程落地能力"}
            ],
            "resources": [{"type": "课程", "name": "深度学习专项课程", "url": "待添加"}, {"type": "书籍", "name": "深度学习花书", "url": "待添加"}, {"type": "框架", "name": "PyTorch/TensorFlow", "url": "待添加"}],
            "assessment": "完成 4 个深度学习项目和 1 个综合项目"
        },
        {
            "id": "professional",
            "name": "大学级",
            "subtitle": "AI 专业阶段",
            "description": "前沿技术研究和专业能力培养",
            "target": "大学生/从业者",
            "duration": "18-24 个月",
            "modules": [
                {"name": "大模型技术", "topics": ["LLM 架构", "Prompt Engineering", "RAG"], "activities": ["微调大模型", "构建 AI 应用"], "outcome": "掌握大模型技术栈"},
                {"name": "AI 系统架构", "topics": ["分布式训练", "模型压缩", "推理优化"], "activities": ["大规模训练实验", "模型优化实战"], "outcome": "具备系统设计能力"},
                {"name": "AI 伦理与安全", "topics": ["AI 伦理", "模型安全", "隐私保护"], "activities": ["伦理案例分析", "安全审计实践"], "outcome": "具备 AI 伦理意识"},
                {"name": "研究能力培养", "topics": ["论文阅读", "实验设计", "学术写作"], "activities": ["复现顶会论文", "撰写技术博客"], "outcome": "具备独立研究能力"}
            ],
            "resources": [{"type": "论文", "name": "顶会论文精选", "url": "待添加"}, {"type": "开源", "name": "GitHub 优质项目", "url": "待添加"}, {"type": "社区", "name": "AI 技术社区", "url": "待添加"}],
            "assessment": "完成 1 个研究项目和 2 篇技术文章"
        }
    ]
}

def generate_index():
    """生成网站首页"""
    html = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI 学习网站 - 四级进阶体系</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; }
        .header { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); padding: 2rem; text-align: center; color: white; }
        .header h1 { font-size: 2.5rem; margin-bottom: 0.5rem; }
        .header p { font-size: 1.2rem; opacity: 0.9; }
        .container { max-width: 1200px; margin: 0 auto; padding: 2rem; }
        .levels { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1.5rem; margin-top: 2rem; }
        .level-card { background: white; border-radius: 16px; padding: 2rem; box-shadow: 0 10px 40px rgba(0,0,0,0.2); transition: transform 0.3s; }
        .level-card:hover { transform: translateY(-5px); }
        .level-card h2 { color: #667eea; margin-bottom: 0.5rem; }
        .level-card .subtitle { color: #666; font-size: 0.9rem; margin-bottom: 1rem; }
        .level-card .description { color: #333; line-height: 1.6; margin-bottom: 1rem; }
        .level-card .meta { display: flex; gap: 1rem; margin-top: 1rem; font-size: 0.85rem; color: #666; }
        .level-card .meta span { background: #f0f0f0; padding: 0.25rem 0.75rem; border-radius: 20px; }
        .level-card a { display: block; margin-top: 1rem; color: #667eea; text-decoration: none; font-weight: 500; }
        .path { background: white; border-radius: 16px; padding: 2rem; margin-top: 2rem; }
        .path h2 { color: #667eea; margin-bottom: 1rem; }
        .career { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }
        .career span { background: #667eea; color: white; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; }
        .footer { text-align: center; padding: 2rem; color: white; opacity: 0.8; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI 学习网站</h1>
        <p>从小学到大学，系统化学习人工智能</p>
    </div>
    <div class="container">
        <div class="levels">
            <div class="level-card">
                <h2>🎒 小学级</h2>
                <p class="subtitle">AI 启蒙阶段</p>
                <p class="description">培养对 AI 的兴趣和基础认知，通过游戏和体验了解 AI 是什么、能做什么。</p>
                <div class="meta">
                    <span>📅 3-6 个月</span>
                    <span>👶 零基础</span>
                    <span>📚 3 个模块</span>
                </div>
                <a href="elementary.html">查看详情 →</a>
            </div>
            <div class="level-card">
                <h2>🎓 初中级</h2>
                <p class="subtitle">AI 入门阶段</p>
                <p class="description">学习 Python 编程和机器学习基础，完成简单的 AI 项目实战。</p>
                <div class="meta">
                    <span>📅 6-12 个月</span>
                    <span>💻 需编程基础</span>
                    <span>📚 3 个模块</span>
                </div>
                <a href="intermediate.html">查看详情 →</a>
            </div>
            <div class="level-card">
                <h2>🎓 高中级</h2>
                <p class="subtitle">AI 进阶阶段</p>
                <p class="description">深入学习深度学习和专业应用，掌握 CV 和 NLP 核心技术。</p>
                <div class="meta">
                    <span>📅 12-18 个月</span>
                    <span>🧠 需 ML 基础</span>
                    <span>📚 4 个模块</span>
                </div>
                <a href="advanced.html">查看详情 →</a>
            </div>
            <div class="level-card">
                <h2>🎓 大学级</h2>
                <p class="subtitle">AI 专业阶段</p>
                <p class="description">前沿技术研究和专业能力培养，掌握大模型技术和 AI 系统架构。</p>
                <div class="meta">
                    <span>📅 18-24 个月</span>
                    <span>🔬 需 DL 基础</span>
                    <span>📚 4 个模块</span>
                </div>
                <a href="professional.html">查看详情 →</a>
            </div>
        </div>
        <div class="path">
            <h2>📍 学习路径</h2>
            <p><strong>总时长:</strong> 39-60 个月</p>
            <p><strong>前置要求:</strong> 无（小学级从零开始）</p>
            <p><strong>证书:</strong> 每级完成后获得相应证书</p>
            <h3 style="margin-top:1.5rem; margin-bottom:0.5rem;">🎯 职业方向</h3>
            <div class="career">
                <span>AI 工程师</span>
                <span>机器学习工程师</span>
                <span>数据科学家</span>
                <span>AI 产品经理</span>
                <span>AI 研究员</span>
            </div>
        </div>
    </div>
    <div class="footer">
        <p>Generated by Leo AI System | """ + datetime.now().strftime('%Y-%m-%d') + """</p>
    </div>
</body>
</html>"""
    return html

def generate_level_page(level):
    """生成等级页面"""
    modules_html = ""
    for i, module in enumerate(level["modules"], 1):
        modules_html += f"""
        <div class="module">
            <h3>{i}. {module["name"]}</h3>
            <div class="topics"><strong>主题:</strong> {", ".join(module["topics"])}</div>
            <div class="activities"><strong>活动:</strong> {", ".join(module["activities"])}</div>
            <div class="outcome"><strong>目标:</strong> {module["outcome"]}</div>
        </div>
        """
    
    resources_html = ""
    for res in level["resources"]:
        resources_html += f'<span class="resource">{res["type"]}: {res["name"]}</span>'
    
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{level["name"]} - AI 学习网站</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; min-height: 100vh; }}
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 2rem; text-align: center; color: white; }}
        .header h1 {{ font-size: 2rem; margin-bottom: 0.5rem; }}
        .container {{ max-width: 900px; margin: 0 auto; padding: 2rem; }}
        .info {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; }}
        .info p {{ margin: 0.5rem 0; }}
        .module {{ background: white; border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; }}
        .module h3 {{ color: #667eea; margin-bottom: 0.75rem; }}
        .module .topics, .module .activities, .module .outcome {{ margin: 0.5rem 0; font-size: 0.9rem; }}
        .resources {{ display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 1rem; }}
        .resource {{ background: #f0f0f0; padding: 0.5rem 1rem; border-radius: 20px; font-size: 0.85rem; }}
        .back {{ display: inline-block; margin-top: 1rem; color: #667eea; text-decoration: none; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{level["name"]}</h1>
        <p>{level["subtitle"]}</p>
    </div>
    <div class="container">
        <div class="info">
            <p><strong>📅 时长:</strong> {level["duration"]}</p>
            <p><strong>👥 目标:</strong> {level["target"]}</p>
            <p><strong>📖 描述:</strong> {level["description"]}</p>
            <p><strong>✅ 考核:</strong> {level["assessment"]}</p>
        </div>
        <h2 style="margin: 1.5rem 0 1rem;">📚 课程模块</h2>
        {modules_html}
        <h2 style="margin: 1.5rem 0 1rem;">📖 学习资源</h2>
        <div class="resources">{resources_html}</div>
        <a href="index.html" class="back">← 返回首页</a>
    </div>
</body>
</html>"""
    return f"{level['id']}.html", html

# 生成网站
print("=" * 60)
print("AI 学习网站生成器 - 修复版 (英文文件名)")
print("=" * 60)

# 生成首页
with open(OUTPUT_DIR / "index.html", "w", encoding="utf-8") as f:
    f.write(generate_index())
print("[OK] 生成首页：index.html")

# 生成各级页面
for level in CURRICULUM["levels"]:
    filename, html = generate_level_page(level)
    with open(OUTPUT_DIR / filename, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"[OK] 生成页面：{filename}")

# 生成课程数据 JSON
with open(OUTPUT_DIR / "curriculum.json", "w", encoding="utf-8") as f:
    json.dump(CURRICULUM, f, ensure_ascii=False, indent=2)
print(f"[OK] 生成数据：curriculum.json")

print()
print("=" * 60)
print(f"网站已生成到：{OUTPUT_DIR}")
print("=" * 60)
print()
print("文件列表:")
for f in OUTPUT_DIR.iterdir():
    if f.is_file():
        print(f"  - {f.name}")
print()
print("访问方式:")
print(f"  本地打开：{OUTPUT_DIR / 'index.html'}")
print()
