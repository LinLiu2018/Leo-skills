# 硬盘清理技能 - Disk Cleanup Skill

> 安全、高效的 Windows 磁盘空间管理工具

[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://github.com/LinLiu2018/Leo-skills)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)
[![Python](https://img.shields.io/badge/python-3.9+-green.svg)](https://www.python.org/)

## 📋 功能特性

### 核心功能
- ✅ **硬盘空间分析** - 实时监控各分区使用情况
- ✅ **临时文件清理** - 清理 Windows Temp、浏览器缓存等
- ✅ **大文件扫描** - 快速找出占用空间大的文件
- ⏳ **重复文件检测** - 使用哈希算法识别重复文件（开发中）
- ⏳ **回收站清理** - 安全清空回收站（开发中）
- ⏳ **系统日志清理** - 清理旧的系统日志（开发中）
- ✅ **智能建议** - 根据磁盘使用情况提供清理建议

### 安全机制
- 🛡️ **Dry-run 模式**（默认启用）：仅模拟，不实际删除
- 🛡️ **send2trash**：移到回收站而非永久删除
- 🛡️ **白名单/黑名单**：保护系统关键文件
- 🛡️ **用户确认**：所有删除操作需要确认
- 🛡️ **多层保护**：系统目录黑名单 + 文件扩展名保护

### 性能优化
- ⚡ 多线程并行扫描
- ⚡ 缓存机制（24小时）
- ⚡ 进度条显示
- ⚡ 智能排除系统目录

## 🚀 快速开始

### 安装依赖

```bash
cd leo-skills/utilities/disk-cleanup-cskill
pip install -r requirements.txt
```

### 基本使用

```bash
# 1. 分析磁盘空间
python scripts/main.py --action analyze_space

# 2. 查看临时文件大小
python scripts/main.py --action get_temp_size

# 3. 获取清理建议
python scripts/main.py --action get_recommendations

# 4. 清理临时文件（dry-run 模式）
python scripts/main.py --action clean_temp --dry-run

# 5. 完整清理流程（标准模式，dry-run）
python scripts/main.py --action full_cleanup --profile standard --dry-run
```

### 实际执行清理

⚠️ **警告**: 实际执行清理操作前，请先使用 `--dry-run` 模式查看将要删除的文件！

```bash
# 实际清理临时文件
python scripts/main.py --action clean_temp --no-dry-run

# 实际执行完整清理（标准模式）
python scripts/main.py --action full_cleanup --profile standard --no-dry-run
```

## 📖 详细使用

### 命令行参数

```
--action ACTION       要执行的操作
                      可选: analyze_space, clean_temp, full_cleanup,
                           get_recommendations, get_temp_size

--profile PROFILE     清理配置（用于 full_cleanup）
                      可选: conservative, standard, aggressive
                      默认: standard

--dry-run            仅模拟，不实际删除文件（默认启用）

--no-dry-run         实际执行删除操作（谨慎使用）

--drives DRIVE [...]  要分析的驱动器列表，如: C: D:

--verbose            显示详细输出

--json               以 JSON 格式输出结果
```

### 清理配置说明

#### Conservative（保守模式）
- 只清理明确安全的文件
- 清理临时文件
- 不清理回收站
- 不清理浏览器缓存
- 需要用户确认

#### Standard（标准模式）⭐ 推荐
- 平衡安全和效果
- 清理临时文件
- 清理回收站
- 清理浏览器缓存
- 需要用户确认

#### Aggressive（激进模式）
- 最大化清理空间
- 清理所有可清理项
- 包括系统日志
- 需要用户确认

## 🔧 配置文件

### config.yaml（主配置）

```yaml
settings:
  default_profile: "standard"
  enable_cache: true
  max_threads: 4

cleanup_profiles:
  standard:
    clean_temp: true
    clean_recycle_bin: true
    clean_browser_cache: true
    require_confirmation: true

safety:
  dry_run_by_default: true
  use_send2trash: true
  confirm_before_delete: true
```

### safety_rules.yaml（安全规则）

```yaml
whitelist:
  - "C:\\Windows\\Temp"
  - "C:\\Users\\*\\AppData\\Local\\Temp"

blacklist:
  - "C:\\Windows\\System32"
  - "C:\\Program Files"
  - "C:\\Users\\*\\Documents"
```

## 📊 使用示例

### 示例 1: 分析磁盘空间

```bash
$ python scripts/main.py --action analyze_space

============================================================
  硬盘清理技能 - Disk Cleanup Skill
  Version: 1.0.0
  安全、高效的 Windows 磁盘空间管理工具
============================================================

✅ 操作成功: analyze_space
------------------------------------------------------------

📊 磁盘空间分析:

  🟡 C:
     总容量: 200.0 GB
     已使用: 150.0 GB (75.0%)
     剩余空间: 50.0 GB

  🟢 D:
     总容量: 275.0 GB
     已使用: 83.0 GB (30.0%)
     剩余空间: 192.0 GB

总体状态: WARNING
⚠️  警告驱动器: C:

💡 清理建议:
  🟡 C: 使用率 75.0%，剩余空间 50.0GB，建议定期清理
```

### 示例 2: 查看临时文件大小

```bash
$ python scripts/main.py --action get_temp_size

📦 临时文件统计:
  总大小: 3.45 GB (3532.18 MB)
  文件数: 12847

  各位置详情:
    C:\Users\用户名\AppData\Local\Temp
      大小: 2.15 GB, 文件: 8234
    C:\Windows\Temp
      大小: 1.30 GB, 文件: 4613
```

### 示例 3: 清理临时文件（dry-run）

```bash
$ python scripts/main.py --action clean_temp --dry-run

🧹 清理结果:
  模式: Dry-run (模拟)
  发现文件: 12847
  已删除: 0
  跳过: 3421
  释放空间: 3.45 GB (3532.18 MB)

  清理位置:
    - C:\Users\用户名\AppData\Local\Temp
      文件: 0, 空间: 2201.45 MB
    - C:\Windows\Temp
      文件: 0, 空间: 1330.73 MB
```

## 🔒 安全保障

### 多层保护机制

1. **Dry-run 模式**
   - 默认启用，仅模拟不实际删除
   - 可以安全预览将要删除的文件

2. **send2trash 集成**
   - 文件移到回收站而非永久删除
   - 可以从回收站恢复误删的文件

3. **白名单/黑名单**
   - 系统关键目录受保护
   - 用户重要文件夹受保护
   - 可自定义配置

4. **文件年龄检查**
   - 默认只删除 30 天以前的文件
   - 保护最近使用的文件

5. **用户确认**
   - 所有删除操作需要用户确认
   - 显示详细的操作信息

### 受保护的位置

以下位置**绝对不会**被清理：
- `C:\Windows\System32`
- `C:\Program Files`
- `C:\Users\*\Documents`
- `C:\Users\*\Desktop`
- `C:\Users\*\Downloads`
- `C:\Users\*\Pictures`
- `C:\Users\*\Videos`

## 🐛 故障排除

### 问题 1: 权限不足

**症状**: 提示"权限被拒绝"

**解决方案**:
```bash
# 以管理员身份运行命令提示符
# 然后执行清理命令
```

### 问题 2: 依赖包安装失败

**症状**: `pip install` 失败

**解决方案**:
```bash
# 升级 pip
python -m pip install --upgrade pip

# 重新安装依赖
pip install -r requirements.txt
```

### 问题 3: 找不到模块

**症状**: `ModuleNotFoundError`

**解决方案**:
```bash
# 确保在正确的目录
cd leo-skills/utilities/disk-cleanup-cskill

# 确保依赖已安装
pip install -r requirements.txt
```

## 📝 开发计划

### v1.0.0（当前版本）✅
- [x] 硬盘空间分析
- [x] 临时文件清理
- [x] 安全机制
- [x] 配置系统

### v1.1.0（计划中）
- [ ] 重复文件检测
- [ ] 回收站清理
- [ ] 系统日志清理
- [ ] 大文件扫描优化

### v2.0.0（未来）
- [ ] 磁盘碎片整理
- [ ] 启动项管理
- [ ] 定时任务
- [ ] GUI 界面

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 👤 作者

**Leo Liu** (@LinLiu2018)

- GitHub: [https://github.com/LinLiu2018/Leo-skills](https://github.com/LinLiu2018/Leo-skills)

## 🙏 致谢

感谢以下开源项目：
- [psutil](https://github.com/giampaolo/psutil) - 系统信息获取
- [send2trash](https://github.com/arsenetar/send2trash) - 安全删除
- [PyYAML](https://github.com/yaml/pyyaml) - YAML 解析

---

**⚠️ 重要提示**: 使用本工具前请务必备份重要数据！虽然本工具有多重安全保护机制，但仍建议谨慎使用。
