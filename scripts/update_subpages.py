# -*- coding: utf-8 -*-
"""更新子页面为科技风"""

import shutil
from pathlib import Path

SITE_DIR = Path("D:/桌面/leo_ai_system/output/ai_learning_site")

# 高级页面内容
advanced_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>高中级 - AI 学习网站</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
        .grid-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px); background-size: 50px 50px; pointer-events: none; z-index: -1; }
        .header { background: linear-gradient(135deg, rgba(0, 255, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%); backdrop-filter: blur(10px); padding: 3rem 2rem; text-align: center; border-bottom: 1px solid rgba(0, 255, 255, 0.2); }
        .header h1 { font-size: 2.5rem; background: linear-gradient(135deg, #00ffff 0%, #8a2be2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem; }
        .header .subtitle { color: #8a2be2; font-size: 1rem; text-transform: uppercase; letter-spacing: 3px; }
        .container { max-width: 1000px; margin: 0 auto; padding: 3rem 2rem; }
        .info-card { background: linear-gradient(135deg, rgba(20, 20, 30, 0.9) 0%, rgba(10, 10, 20, 0.9) 100%); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; }
        .info-card .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
        .info-card .meta-item { background: rgba(0, 255, 255, 0.05); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 12px; padding: 1rem; text-align: center; }
        .info-card .meta-item .label { color: #8a2be2; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; }
        .info-card .meta-item .value { color: #00ffff; font-size: 1.1rem; font-weight: 600; }
        .section-title { color: #00ffff; font-size: 1.8rem; margin: 2.5rem 0 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid rgba(0, 255, 255, 0.2); }
        .module-card { background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease; }
        .module-card:hover { transform: translateX(8px); box-shadow: 0 0 30px rgba(138, 43, 226, 0.3); }
        .module-card h3 { color: #8a2be2; font-size: 1.3rem; margin-bottom: 1rem; }
        .module-card .item { margin: 0.5rem 0; color: #b0b0b0; line-height: 1.6; }
        .module-card .item strong { color: #00ffff; }
        .resources-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
        .resource-card { background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 12px; padding: 1.25rem; transition: all 0.3s ease; }
        .resource-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0, 255, 255, 0.2); }
        .resource-card .type { display: inline-block; background: linear-gradient(135deg, rgba(0, 255, 255, 0.2) 0%, rgba(138, 43, 226, 0.2) 100%); color: #00ffff; padding: 0.35rem 0.85rem; border-radius: 15px; font-size: 0.75rem; margin-bottom: 0.75rem; }
        .resource-card h4 { color: #e0e0e0; font-size: 1rem; margin-bottom: 0.5rem; }
        .resource-card a { color: #00ffff; text-decoration: none; font-weight: 600; }
        .back-btn { display: inline-block; margin-top: 2rem; color: #00ffff; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 25px; transition: all 0.3s; }
        .back-btn:hover { background: rgba(0, 255, 255, 0.1); box-shadow: 0 0 20px rgba(0, 255, 255, 0.3); }
        .footer { text-align: center; padding: 2rem; color: #606060; border-top: 1px solid rgba(0, 255, 255, 0.1); margin-top: 3rem; }
    </style>
</head>
<body>
    <div class="grid-bg"></div>
    <div class="header">
        <h1>🎓 高中级</h1>
        <p class="subtitle">AI 进阶阶段</p>
    </div>
    <div class="container">
        <div class="info-card">
            <h2 style="color: #00ffff; margin-bottom: 1rem;">阶段信息</h2>
            <p style="color: #b0b0b0; line-height: 1.8;">深入学习深度学习和专业应用，掌握 CV 和 NLP 核心技术。</p>
            <div class="meta-grid">
                <div class="meta-item"><div class="label">📅 时长</div><div class="value">12-18 个月</div></div>
                <div class="meta-item"><div class="label">👥 目标</div><div class="value">高中生/有 ML 基础</div></div>
                <div class="meta-item"><div class="label">📚 模块</div><div class="value">4 个模块</div></div>
                <div class="meta-item"><div class="label">✅ 考核</div><div class="value">4 个深度学习项目</div></div>
            </div>
        </div>
        <h2 class="section-title">📚 课程模块</h2>
        <div class="module-card"><h3>1. 深度学习基础</h3><div class="item"><strong>主题:</strong> 神经网络、反向传播、优化算法</div><div class="item"><strong>活动:</strong> 搭建神经网络、调参实验</div><div class="item"><strong>目标:</strong> 掌握深度学习原理</div></div>
        <div class="module-card"><h3>2. 计算机视觉</h3><div class="item"><strong>主题:</strong> CNN、目标检测、图像分割</div><div class="item"><strong>活动:</strong> 图像分类项目、目标检测实战</div><div class="item"><strong>目标:</strong> 掌握 CV 核心技术</div></div>
        <div class="module-card"><h3>3. 自然语言处理</h3><div class="item"><strong>主题:</strong> RNN、Transformer、语言模型</div><div class="item"><strong>活动:</strong> 文本分类、情感分析项目</div><div class="item"><strong>目标:</strong> 掌握 NLP 核心技术</div></div>
        <div class="module-card"><h3>4. AI 工程化</h3><div class="item"><strong>主题:</strong> 模型部署、API 开发、性能优化</div><div class="item"><strong>活动:</strong> 部署模型到云端、开发 AI 应用</div><div class="item"><strong>目标:</strong> 具备工程落地能力</div></div>
        <h2 class="section-title">📖 学习资源</h2>
        <div class="resources-grid">
            <div class="resource-card"><span class="type">课程</span><h4>吴恩达深度学习</h4><a href="https://www.coursera.org/specializations/deep-learning" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">书籍</span><h4>深度学习花书</h4><a href="https://github.com/exacity/deeplearningbook-chinese" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">框架</span><h4>PyTorch 教程</h4><a href="https://pytorch.org/tutorials/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">课程</span><h4>Fast.ai 实战</h4><a href="https://course.fast.ai/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">书籍</span><h4>动手学深度学习</h4><a href="https://zh.d2l.ai/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">项目</span><h4>Hugging Face</h4><a href="https://huggingface.co/learn" target="_blank">访问 →</a></div>
        </div>
        <a href="index.html" class="back-btn">← 返回首页</a>
    </div>
    <div class="footer"><p>Powered by Leo AI System | 2026</p></div>
</body>
</html>
"""

# 大学级页面内容
professional_content = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>大学级 - AI 学习网站</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Segoe UI', -apple-system, BlinkMacSystemFont, Roboto, sans-serif; background: #0a0a0f; color: #e0e0e0; min-height: 100vh; }
        .grid-bg { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-image: linear-gradient(rgba(0, 255, 255, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(0, 255, 255, 0.03) 1px, transparent 1px); background-size: 50px 50px; pointer-events: none; z-index: -1; }
        .header { background: linear-gradient(135deg, rgba(0, 255, 255, 0.15) 0%, rgba(138, 43, 226, 0.15) 100%); backdrop-filter: blur(10px); padding: 3rem 2rem; text-align: center; border-bottom: 1px solid rgba(0, 255, 255, 0.2); }
        .header h1 { font-size: 2.5rem; background: linear-gradient(135deg, #00ffff 0%, #8a2be2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 0.5rem; }
        .header .subtitle { color: #8a2be2; font-size: 1rem; text-transform: uppercase; letter-spacing: 3px; }
        .container { max-width: 1000px; margin: 0 auto; padding: 3rem 2rem; }
        .info-card { background: linear-gradient(135deg, rgba(20, 20, 30, 0.9) 0%, rgba(10, 10, 20, 0.9) 100%); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 16px; padding: 2rem; margin-bottom: 2rem; }
        .info-card .meta-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
        .info-card .meta-item { background: rgba(0, 255, 255, 0.05); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 12px; padding: 1rem; text-align: center; }
        .info-card .meta-item .label { color: #8a2be2; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 0.5rem; }
        .info-card .meta-item .value { color: #00ffff; font-size: 1.1rem; font-weight: 600; }
        .section-title { color: #00ffff; font-size: 1.8rem; margin: 2.5rem 0 1.5rem; padding-bottom: 0.75rem; border-bottom: 2px solid rgba(0, 255, 255, 0.2); }
        .module-card { background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(138, 43, 226, 0.3); border-radius: 12px; padding: 1.5rem; margin-bottom: 1rem; transition: all 0.3s ease; }
        .module-card:hover { transform: translateX(8px); box-shadow: 0 0 30px rgba(138, 43, 226, 0.3); }
        .module-card h3 { color: #8a2be2; font-size: 1.3rem; margin-bottom: 1rem; }
        .module-card .item { margin: 0.5rem 0; color: #b0b0b0; line-height: 1.6; }
        .module-card .item strong { color: #00ffff; }
        .resources-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-top: 1.5rem; }
        .resource-card { background: rgba(0, 0, 0, 0.3); border: 1px solid rgba(0, 255, 255, 0.2); border-radius: 12px; padding: 1.25rem; transition: all 0.3s ease; }
        .resource-card:hover { transform: translateY(-4px); box-shadow: 0 10px 30px rgba(0, 255, 255, 0.2); }
        .resource-card .type { display: inline-block; background: linear-gradient(135deg, rgba(0, 255, 255, 0.2) 0%, rgba(138, 43, 226, 0.2) 100%); color: #00ffff; padding: 0.35rem 0.85rem; border-radius: 15px; font-size: 0.75rem; margin-bottom: 0.75rem; }
        .resource-card h4 { color: #e0e0e0; font-size: 1rem; margin-bottom: 0.5rem; }
        .resource-card a { color: #00ffff; text-decoration: none; font-weight: 600; }
        .back-btn { display: inline-block; margin-top: 2rem; color: #00ffff; text-decoration: none; font-weight: 600; padding: 0.75rem 1.5rem; border: 1px solid rgba(0, 255, 255, 0.3); border-radius: 25px; transition: all 0.3s; }
        .back-btn:hover { background: rgba(0, 255, 255, 0.1); box-shadow: 0 0 20px rgba(0, 255, 255, 0.3); }
        .footer { text-align: center; padding: 2rem; color: #606060; border-top: 1px solid rgba(0, 255, 255, 0.1); margin-top: 3rem; }
    </style>
</head>
<body>
    <div class="grid-bg"></div>
    <div class="header">
        <h1>🎓 大学级</h1>
        <p class="subtitle">AI 专业阶段</p>
    </div>
    <div class="container">
        <div class="info-card">
            <h2 style="color: #00ffff; margin-bottom: 1rem;">阶段信息</h2>
            <p style="color: #b0b0b0; line-height: 1.8;">前沿技术研究和专业能力培养，掌握大模型技术和 AI 系统架构。</p>
            <div class="meta-grid">
                <div class="meta-item"><div class="label">📅 时长</div><div class="value">18-24 个月</div></div>
                <div class="meta-item"><div class="label">👥 目标</div><div class="value">大学生/从业者</div></div>
                <div class="meta-item"><div class="label">📚 模块</div><div class="value">4 个模块</div></div>
                <div class="meta-item"><div class="label">✅ 考核</div><div class="value">1 个研究项目 + 2 篇技术文章</div></div>
            </div>
        </div>
        <h2 class="section-title">📚 课程模块</h2>
        <div class="module-card"><h3>1. 大模型技术</h3><div class="item"><strong>主题:</strong> LLM 架构、Prompt Engineering、RAG</div><div class="item"><strong>活动:</strong> 微调大模型、构建 AI 应用</div><div class="item"><strong>目标:</strong> 掌握大模型技术栈</div></div>
        <div class="module-card"><h3>2. AI 系统架构</h3><div class="item"><strong>主题:</strong> 分布式训练、模型压缩、推理优化</div><div class="item"><strong>活动:</strong> 大规模训练实验、模型优化实战</div><div class="item"><strong>目标:</strong> 具备系统设计能力</div></div>
        <div class="module-card"><h3>3. AI 伦理与安全</h3><div class="item"><strong>主题:</strong> AI 伦理、模型安全、隐私保护</div><div class="item"><strong>活动:</strong> 伦理案例分析、安全审计实践</div><div class="item"><strong>目标:</strong> 具备 AI 伦理意识</div></div>
        <div class="module-card"><h3>4. 研究能力培养</h3><div class="item"><strong>主题:</strong> 论文阅读、实验设计、学术写作</div><div class="item"><strong>活动:</strong> 复现顶会论文、撰写技术博客</div><div class="item"><strong>目标:</strong> 具备独立研究能力</div></div>
        <h2 class="section-title">📖 学习资源</h2>
        <div class="resources-grid">
            <div class="resource-card"><span class="type">论文</span><h4>Papers With Code</h4><a href="https://paperswithcode.com/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">课程</span><h4>李宏毅机器学习</h4><a href="https://speech.ee.ntu.edu.tw/~hylee/ml/2022-spring.php" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">课程</span><h4>Stanford CS224N</h4><a href="http://web.stanford.edu/class/cs224n/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">课程</span><h4>Stanford CS231n</h4><a href="http://cs231n.stanford.edu/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">社区</span><h4>Hugging Face</h4><a href="https://huggingface.co/" target="_blank">访问 →</a></div>
            <div class="resource-card"><span class="type">博客</span><h4>Jay Alammar</h4><a href="https://jalammar.github.io/" target="_blank">访问 →</a></div>
        </div>
        <a href="index.html" class="back-btn">← 返回首页</a>
    </div>
    <div class="footer"><p>Powered by Leo AI System | 2026</p></div>
</body>
</html>
"""

# 写入文件
with open(SITE_DIR / "advanced.html", "w", encoding="utf-8") as f:
    f.write(advanced_content)
print("[OK] advanced.html")

with open(SITE_DIR / "professional.html", "w", encoding="utf-8") as f:
    f.write(professional_content)
print("[OK] professional.html")

print("\nAll subpages updated!")
