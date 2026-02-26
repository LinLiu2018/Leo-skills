"""
Demo: Skill Evolution in Action
==============================
演示如何使用 `EvolvableSkill` 让电商代理具备自我进化能力。
"""

import sys
from pathlib import Path

# 添加路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from leo_skills.core.evolution.base import EvolvableSkill

class EvolvableCompetitorScraper(EvolvableSkill):
    def __init__(self):
        # 模拟存档路径
        save_path = Path("demo_ecommerce_evolution.json")
        super().__init__("competitor_scraper", save_path)
        
    def scrape(self, url: str):
        # 1. 读取经验
        experience = self.get_experience_context()
        print(f"\n[System] Current Experience: \n{experience if experience else '(None)'}")
        
        # 2. 模拟执行
        print(f"[Action] Scraping {url}...")
        
        # 3. 模拟失败与学习
        if "wechat" in url and "Use custom fetcher" not in experience:
            print("[Error] Failed to scrape WeChat (Anti-bot detected).")
            print("[Evolution] Analyzing failure... -> Found solution.")
            self.learn("Use custom fetcher for WeChat URLs to bypass anti-bot")
        else:
            print("[Success] Scraped successfully using optimized strategy!")

def main():
    print("🚀 Skill Evolution Demo Request\n")
    
    skill = EvolvableCompetitorScraper()
    
    # 第一次运行：失败并学习
    print("--- Run 1: First Encounter ---")
    skill.scrape("https://mp.weixin.qq.com/s/sample")
    
    print("\n" + "="*30 + "\n")
    
    # 第二次运行：应用经验
    print("--- Run 2: Learned Response ---")
    skill.scrape("https://mp.weixin.qq.com/s/sample")

if __name__ == "__main__":
    main()
