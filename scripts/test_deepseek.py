
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(env_path)

# Verify key
key = os.environ.get("DEEPSEEK_API_KEY")
print(f"DeepSeek Key: {key[:5]}..." if key else "DeepSeek Key NOT FOUND")

# Add skill path
sys.path.append(str(project_root / "leo_skills/core/text-generator-cskill/scripts"))

try:
    from main import TextGeneratorSkill
    print("[SUCCESS] Skill imported")
    
    skill = TextGeneratorSkill()
    print("[SUCCESS] Skill instantiated")
    
    print("Testing generation (Chinese)...")
    result = skill.generate("你好，请自我介绍", provider="deepseek")
    
    print("-" * 20)
    print("RESULT:", result)
    print("-" * 20)
    
except Exception as e:
    print(f"[ERROR] Error: {e}")
    import traceback
    traceback.print_exc()
