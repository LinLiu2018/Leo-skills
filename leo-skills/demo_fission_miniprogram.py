"""
裂变小程序完整代码生成演示
===========================
使用4个开发Skills生成完整的裂变小程序项目
"""

import sys
from pathlib import Path

# 输出目录
OUTPUT_DIR = Path(__file__).parent / "demo_output" / "fission_miniprogram"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# 添加Skills路径
SKILLS_BASE = Path(__file__).parent / "development"
sys.path.insert(0, str(SKILLS_BASE / "backend/database-model-generator-cskill/scripts"))

print("=" * 60)
print("裂变小程序完整代码生成")
print("=" * 60)

# ==================== 1. 生成数据库模型 ====================
print("\n[1/5] 生成数据库模型...")

from main import DatabaseModelGenerator

db_gen = DatabaseModelGenerator(output_dir=str(OUTPUT_DIR / "backend"), orm="sqlalchemy")

# Lead模型（线索/客户）
lead_fields = [
    {'name': 'name', 'type': 'string', 'required': True, 'max_length': 50, 'description': '客户姓名'},
    {'name': 'phone', 'type': 'string', 'required': True, 'max_length': 20, 'description': '手机号'},
    {'name': 'parent_id', 'type': 'integer', 'foreign_key': 'leads.id', 'description': '推荐人ID'},
    {'name': 'status', 'type': 'string', 'default': 'new', 'max_length': 20, 'description': '状态(new/contacted/converted)'},
    {'name': 'depth', 'type': 'integer', 'default': 0, 'description': '裂变层级'},
    {'name': 'source', 'type': 'string', 'max_length': 50, 'description': '来源渠道'},
    {'name': 'openid', 'type': 'string', 'max_length': 100, 'description': '微信OpenID'},
]

lead_results = db_gen.generate(
    entity_name='Lead',
    fields=lead_fields,
    relationships=[{'name': 'parent', 'type': 'self_referential', 'back_ref': 'children'}],
    indexes=['phone', 'status', 'parent_id', 'openid']
)
db_gen.save_files('Lead', lead_results)
print("  [OK] Lead模型生成完成")

# Reward模型（奖励记录）
reward_fields = [
    {'name': 'lead_id', 'type': 'integer', 'required': True, 'foreign_key': 'leads.id', 'description': '线索ID'},
    {'name': 'reward_type', 'type': 'string', 'required': True, 'max_length': 20, 'description': '奖励类型(coupon/cash/points)'},
    {'name': 'amount', 'type': 'float', 'required': True, 'description': '奖励金额'},
    {'name': 'status', 'type': 'string', 'default': 'pending', 'max_length': 20, 'description': '状态(pending/issued/used)'},
    {'name': 'issued_at', 'type': 'datetime', 'description': '发放时间'},
]

reward_results = db_gen.generate(
    entity_name='Reward',
    fields=reward_fields,
    indexes=['lead_id', 'status']
)
db_gen.save_files('Reward', reward_results)
print("  [OK] Reward模型生成完成")

# ==================== 2. 生成Flask API ====================
print("\n[2/5] 生成Flask API...")

# 重新加载模块
sys.path.insert(0, str(SKILLS_BASE / "backend/flask-api-generator-cskill/scripts"))
import importlib
import main
importlib.reload(main)
from main import FlaskAPIGenerator

api_gen = FlaskAPIGenerator(output_dir=str(OUTPUT_DIR / "backend"))

# Lead API
lead_api_fields = [
    {'name': 'name', 'type': 'string', 'required': True},
    {'name': 'phone', 'type': 'string', 'required': True},
    {'name': 'parent_id', 'type': 'integer'},
    {'name': 'status', 'type': 'string'},
    {'name': 'depth', 'type': 'integer'},
    {'name': 'source', 'type': 'string'},
    {'name': 'openid', 'type': 'string'},
]

lead_api_results = api_gen.generate(
    resource_name='lead',
    fields=lead_api_fields,
    auth_required=False  # 小程序端不需要JWT
)
api_gen.save_files('lead', lead_api_results)
print("  [OK] Lead API生成完成")

# Reward API
reward_api_fields = [
    {'name': 'lead_id', 'type': 'integer', 'required': True},
    {'name': 'reward_type', 'type': 'string', 'required': True},
    {'name': 'amount', 'type': 'float', 'required': True},
    {'name': 'status', 'type': 'string'},
]

reward_api_results = api_gen.generate(
    resource_name='reward',
    fields=reward_api_fields,
    auth_required=False
)
api_gen.save_files('reward', reward_api_results)
print("  [OK] Reward API生成完成")

# ==================== 3. 生成小程序页面 ====================
print("\n[3/5] 生成小程序页面...")

sys.path.insert(0, str(SKILLS_BASE / "frontend/miniprogram-page-generator-cskill/scripts"))
importlib.reload(main)
from main import MiniprogramPageGenerator

mp_gen = MiniprogramPageGenerator(output_dir=str(OUTPUT_DIR / "miniprogram"))

# 注册表单页
register_fields = [
    {'name': 'name', 'label': '姓名', 'type': 'text'},
    {'name': 'phone', 'label': '手机号', 'type': 'number'},
    {'name': 'source', 'label': '了解渠道', 'type': 'select', 'options': ['朋友推荐', '广告', '路过门店']},
]

register_results = mp_gen.generate(
    page_name='register',
    page_type='form',
    data_bindings=register_fields,
    api_endpoints=[{'url': '/api/leads', 'method': 'POST'}],
    features=['validation', 'loading']
)
mp_gen.save_files('register', register_results)
print("  [OK] 注册页面生成完成")

# 分享裂变页
share_results = mp_gen.generate(
    page_name='share',
    page_type='share',
    data_bindings=[],
    features=['share', 'poster']
)
mp_gen.save_files('share', share_results)
print("  [OK] 分享页面生成完成")

# 邀请列表页
invite_results = mp_gen.generate(
    page_name='invites',
    page_type='list',
    data_bindings=[{'name': 'name'}, {'name': 'phone'}],
    api_endpoints=[{'url': '/api/leads', 'method': 'GET'}],
    features=['pulldown']
)
mp_gen.save_files('invites', invite_results)
print("  [OK] 邀请列表页生成完成")

# ==================== 4. 生成Docker配置 ====================
print("\n[4/5] 生成Docker部署配置...")

sys.path.insert(0, str(SKILLS_BASE / "deployment/dockerfile-generator-cskill/scripts"))
importlib.reload(main)
from main import DockerfileGenerator

docker_gen = DockerfileGenerator(output_dir=str(OUTPUT_DIR / "deploy"))

docker_results = docker_gen.generate(
    app_type='flask',
    runtime='python:3.9-slim',
    port=5000,
    multi_stage=True,
    with_compose=True,
    services=['mysql', 'redis', 'nginx']
)
docker_gen.save_files(docker_results)
print("  [OK] Docker配置生成完成")

# ==================== 5. 生成项目说明 ====================
print("\n[5/5] 生成项目说明...")

readme = """# 裂变小程序项目

## 项目结构

```
fission_miniprogram/
├── backend/                    # 后端代码
│   ├── app/
│   │   ├── models/            # 数据模型
│   │   │   ├── lead.py        # 线索模型
│   │   │   └── reward.py      # 奖励模型
│   │   ├── schemas/           # 序列化Schema
│   │   ├── services/          # 业务逻辑
│   │   └── blueprints/        # API路由
│   └── migrations/            # 数据库迁移
├── miniprogram/               # 小程序代码
│   └── pages/
│       ├── register/          # 注册页面
│       ├── share/             # 分享裂变页
│       └── invites/           # 邀请列表页
└── deploy/                    # 部署配置
    ├── Dockerfile
    ├── docker-compose.yml
    └── docker-compose.prod.yml
```

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
flask db upgrade
flask run
```

### 小程序开发

1. 用微信开发者工具打开 `miniprogram` 目录
2. 配置 `app.js` 中的 `baseUrl`
3. 编译预览

### Docker部署

```bash
cd deploy
docker-compose up -d
```

## API接口

| 接口 | 方法 | 说明 |
|------|------|------|
| /api/leads | GET | 获取线索列表 |
| /api/leads | POST | 创建新线索 |
| /api/leads/:id | GET | 获取线索详情 |
| /api/rewards | GET | 获取奖励列表 |

## 裂变逻辑

1. 用户A分享小程序给用户B
2. 用户B通过分享链接注册（带parent_id参数）
3. 系统记录裂变关系，计算层级
4. 触发奖励发放逻辑

---
Generated by Leo AI Agent System
"""

readme_path = OUTPUT_DIR / "README.md"
readme_path.write_text(readme, encoding='utf-8')
print("  [OK] README生成完成")

# ==================== 完成 ====================
print("\n" + "=" * 60)
print("生成完成！")
print("=" * 60)
print(f"\n输出目录: {OUTPUT_DIR}")
print("\n生成的文件:")

for root, dirs, files in (OUTPUT_DIR).walk():
    level = len(root.relative_to(OUTPUT_DIR).parts)
    indent = "  " * level
    print(f"{indent}{root.name}/")
    for file in files:
        print(f"{indent}  {file}")
