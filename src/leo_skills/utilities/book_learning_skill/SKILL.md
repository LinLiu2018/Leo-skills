# Book Learning Skill（书籍学习助手）

从 PDF/EPUB 书籍中提取知识点，生成 Obsidian 学习笔记。

## 核心能力

- 搜索书籍（LibGen 数据库）
- 提取 PDF/EPUB 文本和章节结构
- AI 逐章分析，提取核心知识点
- 输出到 Obsidian（MOC + 章节笔记 + 学习大纲）

## 完整流程

```
搜索书籍 → 下载 PDF → 提取章节 → AI 分析知识点 → Obsidian 笔记
```

## 使用方法

### Python API

```python
from leo_skills.utilities.book_learning_skill import BookLearning

bl = BookLearning(vault_path="D:/Obsidian/MyVault")

# 处理本地 PDF
result = bl.process_local_pdf("深度学习.pdf")

# 搜索书籍
print(bl.search_books("Python编程"))

# 完整流程：搜索 → 下载 → 分析 → 导出
result = bl.search_and_process("机器学习", book_index=0)
```

### CLI

```bash
# 搜索书籍
python -m leo_skills.utilities.book_learning_skill.scripts.main search "深度学习"

# 处理本地 PDF
python -m leo_skills.utilities.book_learning_skill.scripts.main process "book.pdf" -o ./output

# 完整流程
python -m leo_skills.utilities.book_learning_skill.scripts.main full "Python编程" -i 0
```

## 依赖

```
libgen-api-enhanced    # LibGen 搜索
PyMuPDF                # PDF 提取（推荐）
pdfplumber             # PDF 提取（备选）
ebooklib               # EPUB 支持
beautifulsoup4         # HTML 解析
anthropic              # Claude API（或 openai）
```

## 输出示例

```
output/book_notes/深度学习/
├── 深度学习.md              # MOC 主页
├── 深度学习-学习大纲.md      # 学习大纲
├── 深度学习-第1章.md         # 章节知识点
├── 深度学习-第2章.md
└── ...
```

---
**Version:** 1.0.0
