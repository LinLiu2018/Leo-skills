
import sys
import os
from pathlib import Path
import importlib.util
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

print(f"ZHIPUAI_API_KEY: {os.environ.get('ZHIPUAI_API_KEY')[:5]}...")

try:
    import zhipuai
    print("[SUCCESS] zhipuai imported successfully")
except ImportError as e:
    print(f"[ERROR] zhipuai import failed: {e}")

# Load Skill Main
skill_path = project_root / "leo_skills/core/text-generator-cskill/scripts/main.py"
print(f"Loading skill from {skill_path}")

try:
    spec = importlib.util.spec_from_file_location("text_gen_main", skill_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    print("[SUCCESS] Skill module execution successful")
    
    # Instantiate
    instance = mod.TextGenerator()
    print("[SUCCESS] TextGenerator instantiated")
    
    # Test Generate
    print("Testing generate...")
    res = instance.generate("Hello")
    print(f"Generate Result: {res}")
    
except Exception as e:
    print(f"[ERROR] Skill load/run failed: {e}")
    import traceback
    traceback.print_exc()
