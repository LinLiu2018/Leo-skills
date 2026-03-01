# ClawHub 技能引入指南

**创建时间**: 2026-02-27  
**状态**: ✅ 配置框架完成

---

## 一、ClawHub 技能生态

### 官方数据

- **技能总数**: 2868+ 个
- **热门技能**: 100+ 个
- **分类**: 30+ 个类别

### 优先引入清单 (20 个)

| 类别 | 技能 | 优先级 |
|------|------|--------|
| **搜索** | tavily-search | P0 |
| **社交** | twitter-monitor | P0 |
| **媒体** | youtube-summarizer | P1 |
| **文档** | pdf-analyzer | P1 |
| **效率** | calendar-integration | P1 |
| **通讯** | email-automation | P2 |
| **协作** | slack-integration | P2 |
| **知识** | notion-connector | P2 |
| **数据** | airtable-connector | P3 |
| **自动化** | zapier-webhook | P3 |

---

## 二、引入流程

```
1. 从 ClawHub 下载技能
   ↓
2. 运行 skill_vetter 扫描
   ↓
3. 适配 Leo 系统规范
   ↓
4. 注册到 capability_index
   ↓
5. 测试验证
   ↓
6. 投入使用
```

---

## 三、安装命令

```bash
# 从 ClawHub 安装技能
clawhub install <skill-name>

# 或手动安装
git clone https://github.com/<repo>/skill-name
cp -r skill-name src/leo_skills/tools/
```

---

## 四、验收标准

- [x] ClawHub 技能引入文档已创建
- [ ] 引入 20+ 社区技能
- [ ] 所有技能通过安全扫描
- [ ] 技能正常使用

---

*配置完成时间：2026-02-27*
