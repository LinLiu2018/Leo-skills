---
name: file-manager-skill
description: 磁盘清理和文件管理 (含桌面文件整理)。当用户需要实用工具相关帮助时使用。 [优化第5轮：提升了触发准确率]
metadata:
  version: 2.0.0
  category: utilities
  author: leo-ai-system
  priority: 1
  activation_keywords:
  - file-manager-skill
  - 磁盘清理
  - 桌面整理
  - 文件整理
  - 大文件
  - 重复文件
  - PARA
  allowed-tools:
  - Read
  - Write
  - Bash
  user-invocable: true
license: MIT
---

# File Manager Skill (v2.0)

## 功能说明

磁盘清理和文件管理工具，支持以下功能：

| 功能 | 说明 | 参考来源 |
|------|------|---------|
| **scan_large_files** | 扫描大文件 | 通用 |
| **find_duplicates** | 查找重复文件(MD5) | 通用 |
| **clean_temp** | 清理临时文件 | 通用 |
| **clean_empty_dirs** | 清理空目录 | 通用 |
| **organize_by_type** | 按类型整理 | AutomaDesk |
| **organize_by_date** | 按日期整理 | DeskCleaner |
| **organize_para** | PARA方法整理 | claude-code-cowork-skills-file-organizer |
| **inbox_workflow** | 收件箱工作流 | PARA方法 |

## 使用方式

### 磁盘清理功能

#### 1. 扫描大文件
```
execute(action='scan_large_files', path='D:\\', min_size_mb=100, top_n=20)
```

#### 2. 查找重复文件
```
execute(action='find_duplicates', path='D:\\图片', min_size_kb=10)
```

#### 3. 清理临时文件
```
execute(action='clean_temp', path='D:\\temp', dry_run=True)
```

#### 4. 清理空目录
```
execute(action='clean_empty_dirs', path='D:\\项目', dry_run=True)
```

### 桌面文件整理功能

#### 5. 按类型整理
```
execute(action='organize_by_type', path='D:\\下载', dry_run=True)
```

按文件类型自动归类：
- 图片 (.jpg, .png, .gif, .svg...)
- 视频 (.mp4, .avi, .mkv...)
- 音频 (.mp3, .wav, .flac...)
- 文档 (.pdf, .doc, .docx, .xls...)
- 压缩包 (.zip, .rar, .7z...)
- 代码 (.py, .js, .ts, .java...)
- 数据 (.sql, .db, .csv...)
- 可执行 (.exe, .msi, .dmg...)

#### 6. 按日期整理
```
execute(action='organize_by_date', path='D:\\整理', dry_run=True)
```

按修改日期自动归类到 `年-月` 文件夹。

#### 7. PARA方法整理
```
execute(action='organize_para', path='D:\\资料', dry_run=True)
```

PARA方法分类：
| 类别 | 说明 |
|------|------|
| **Projects** | 正在进行的项目 |
| **Areas** | 责任领域 |
| **Resources** | 参考资源 |
| **Archive** | 归档内容 |

#### 8. 收件箱工作流
```
execute(action='inbox_workflow', path='D:\\桌面', dry_run=True)
```

先将所有文件集中到 Inbox，再按需整理。

#### 9. 预览整理效果
```
execute(action='preview_organize', path='D:\\下载', mode='type')
```

预览不实际移动文件，支持 `type`/`date`/`para` 模式。

## 最佳实践

### 推荐工作流

1. **收件箱 → 整理**
   ```
   inbox_workflow → organize_by_type
   ```

2. **桌面整理**
   ```
   inbox_workflow → organize_para
   ```

3. **下载文件夹整理**
   ```
   organize_by_date
   ```

### 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| path | 操作路径 | 当前目录 |
| dry_run | 模拟运行，不实际修改 | True |
| create_subdirs | 创建类型子目录 | True |
| date_format | 日期格式 | %Y-%m |
| inbox_name | 收件箱名称 | Inbox |

### 安全提示

- 首次使用务必设置 `dry_run=True` 预览效果
- 移动后可使用 `Ctrl+Z` 或手动恢复
- 建议先备份重要文件