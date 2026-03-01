# -*- coding: utf-8 -*-
"""测试 Browser 技能"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from leo_skills.tools.browser_skill.browser_skill import BrowserSkill

s = BrowserSkill()
print('Browser Skill loaded OK')

result = s.execute({'action': 'snapshot', 'url': 'https://example.com'})
print(f"Status: {result['status']}")
print(f"Message: {result['message']}")
