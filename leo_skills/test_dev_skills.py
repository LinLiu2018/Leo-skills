"""
开发Skills测试脚本
==================
测试4个第一阶段开发Skills
"""

import sys
from pathlib import Path

# 添加Skills路径
sys.path.insert(0, str(Path(__file__).parent / "development/backend/flask-api-generator-cskill/scripts"))
sys.path.insert(0, str(Path(__file__).parent / "development/backend/database-model-generator-cskill/scripts"))
sys.path.insert(0, str(Path(__file__).parent / "development/frontend/miniprogram-page-generator-cskill/scripts"))
sys.path.insert(0, str(Path(__file__).parent / "development/deployment/dockerfile-generator-cskill/scripts"))

# 测试输出目录
OUTPUT_DIR = Path(__file__).parent / "test_output"
OUTPUT_DIR.mkdir(exist_ok=True)


def test_database_model_generator():
    """测试数据库模型生成器"""
    print("\n" + "="*50)
    print("测试1: 数据库模型生成器 (Lead实体)")
    print("="*50)

    from main import DatabaseModelGenerator

    generator = DatabaseModelGenerator(output_dir=str(OUTPUT_DIR), orm="sqlalchemy")

    # Lead实体字段定义
    fields = [
        {'name': 'name', 'type': 'string', 'required': True, 'max_length': 100, 'description': '客户姓名'},
        {'name': 'phone', 'type': 'string', 'required': True, 'max_length': 20, 'description': '手机号'},
        {'name': 'parent_id', 'type': 'integer', 'foreign_key': 'leads.id', 'description': '推荐人ID'},
        {'name': 'status', 'type': 'string', 'default': 'new', 'description': '状态'},
        {'name': 'depth', 'type': 'integer', 'default': 0, 'description': '裂变层级'},
        {'name': 'source', 'type': 'string', 'max_length': 50, 'description': '来源渠道'}
    ]

    relationships = [
        {'name': 'parent', 'type': 'self_referential', 'back_ref': 'children'}
    ]

    results = generator.generate(
        entity_name='Lead',
        fields=fields,
        relationships=relationships,
        indexes=['status', 'phone', 'parent_id']
    )

    print(f"✓ 生成模型代码: {len(results['model'])} 字符")
    print(f"✓ 生成迁移脚本: {len(results['migration'])} 字符")

    # 保存文件
    saved = generator.save_files('Lead', results)
    for name, path in saved.items():
        print(f"  保存: {path}")

    return True


def test_flask_api_generator():
    """测试Flask API生成器"""
    print("\n" + "="*50)
    print("测试2: Flask API生成器 (Lead API)")
    print("="*50)

    # 重新导入（因为模块名相同）
    import importlib
    import main as flask_main
    importlib.reload(flask_main)

    # 需要先切换到正确的模块
    sys.path.insert(0, str(Path(__file__).parent / "development/backend/flask-api-generator-cskill/scripts"))

    from main import FlaskAPIGenerator

    generator = FlaskAPIGenerator(output_dir=str(OUTPUT_DIR))

    # Lead API字段定义
    fields = [
        {'name': 'name', 'type': 'string', 'required': True},
        {'name': 'phone', 'type': 'string', 'required': True},
        {'name': 'parent_id', 'type': 'integer'},
        {'name': 'status', 'type': 'string'},
        {'name': 'depth', 'type': 'integer'},
        {'name': 'source', 'type': 'string'}
    ]

    results = generator.generate(
        resource_name='lead',
        fields=fields,
        auth_required=True
    )

    print(f"✓ 生成Blueprint: {len(results['blueprint'])} 字符")
    print(f"✓ 生成Model: {len(results['model'])} 字符")
    print(f"✓ 生成Schema: {len(results['schema'])} 字符")
    print(f"✓ 生成Service: {len(results['service'])} 字符")

    saved = generator.save_files('lead', results)
    for name, path in saved.items():
        print(f"  保存: {path}")

    return True


def test_miniprogram_page_generator():
    """测试小程序页面生成器"""
    print("\n" + "="*50)
    print("测试3: 小程序页面生成器 (注册表单页)")
    print("="*50)

    # 切换模块路径
    sys.path.insert(0, str(Path(__file__).parent / "development/frontend/miniprogram-page-generator-cskill/scripts"))

    import importlib
    import main as mp_main
    importlib.reload(mp_main)

    from main import MiniprogramPageGenerator

    generator = MiniprogramPageGenerator(output_dir=str(OUTPUT_DIR))

    # 注册表单数据绑定
    data_bindings = [
        {'name': 'name', 'type': 'input', 'label': '姓名', 'required': True, 'placeholder': '请输入您的姓名'},
        {'name': 'phone', 'type': 'input', 'label': '手机号', 'required': True, 'placeholder': '请输入手机号'},
        {'name': 'source', 'type': 'picker', 'label': '了解渠道', 'options': ['朋友推荐', '广告', '路过']}
    ]

    api_endpoints = [
        {'name': 'submit', 'url': '/api/leads', 'method': 'POST'}
    ]

    results = generator.generate(
        page_name='register',
        page_type='form',
        data_bindings=data_bindings,
        api_endpoints=api_endpoints,
        features=['validation', 'loading']
    )

    print(f"✓ 生成WXML: {len(results['wxml'])} 字符")
    print(f"✓ 生成WXSS: {len(results['wxss'])} 字符")
    print(f"✓ 生成JS: {len(results['js'])} 字符")
    print(f"✓ 生成JSON: {len(results['json'])} 字符")

    saved = generator.save_files('register', results)
    for name, path in saved.items():
        print(f"  保存: {path}")

    return True


def test_dockerfile_generator():
    """测试Dockerfile生成器"""
    print("\n" + "="*50)
    print("测试4: Dockerfile生成器 (Flask应用)")
    print("="*50)

    # 切换模块路径
    sys.path.insert(0, str(Path(__file__).parent / "development/deployment/dockerfile-generator-cskill/scripts"))

    import importlib
    import main as docker_main
    importlib.reload(docker_main)

    from main import DockerfileGenerator

    generator = DockerfileGenerator(output_dir=str(OUTPUT_DIR))

    results = generator.generate(
        app_type='flask',
        runtime='python:3.9-slim',
        port=5000,
        multi_stage=True,
        with_compose=True,
        services=['mysql', 'redis', 'nginx']
    )

    print(f"✓ 生成Dockerfile: {len(results['dockerfile'])} 字符")
    print(f"✓ 生成.dockerignore: {len(results['dockerignore'])} 字符")
    print(f"✓ 生成docker-compose.yml: {len(results['compose'])} 字符")
    print(f"✓ 生成docker-compose.prod.yml: {len(results['compose_prod'])} 字符")

    saved = generator.save_files(results)
    for name, path in saved.items():
        print(f"  保存: {path}")

    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("Leo开发Skills测试 - 裂变小程序场景")
    print("="*60)

    results = []

    # 测试数据库模型生成器
    try:
        results.append(("数据库模型生成器", test_database_model_generator()))
    except Exception as e:
        print(f"✗ 数据库模型生成器测试失败: {e}")
        results.append(("数据库模型生成器", False))

    # 测试Flask API生成器
    try:
        results.append(("Flask API生成器", test_flask_api_generator()))
    except Exception as e:
        print(f"✗ Flask API生成器测试失败: {e}")
        results.append(("Flask API生成器", False))

    # 测试小程序页面生成器
    try:
        results.append(("小程序页面生成器", test_miniprogram_page_generator()))
    except Exception as e:
        print(f"✗ 小程序页面生成器测试失败: {e}")
        results.append(("小程序页面生成器", False))

    # 测试Dockerfile生成器
    try:
        results.append(("Dockerfile生成器", test_dockerfile_generator()))
    except Exception as e:
        print(f"✗ Dockerfile生成器测试失败: {e}")
        results.append(("Dockerfile生成器", False))

    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"  {name}: {status}")

    print(f"\n总计: {passed}/{total} 通过")
    print(f"输出目录: {OUTPUT_DIR}")

    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
