#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Leo Data Fetcher - 宁波商业租赁市场数据获取
尝试从多个官方数据源获取最新数据
"""

import sys
import os
import json
import re
import urllib.request
import urllib.parse
import ssl
import time
from datetime import datetime

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

os.environ['PYTHONIOENCODING'] = 'utf-8'

try:
    import requests
    HAS_REQUESTS = True
except:
    HAS_REQUESTS = False


class NingboDataFetcher:
    """宁波数据获取器"""
    
    def __init__(self):
        self.timeout = 15
        self.user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        self.session = requests.Session() if HAS_REQUESTS else None
    
    def fetch_url(self, url: str, headers: dict = None) -> dict:
        """获取 URL 内容"""
        result = {"url": url, "success": False, "content": "", "error": ""}
        
        try:
            # 优先使用 requests
            if self.session:
                resp = self.session.get(url, timeout=self.timeout, headers={'User-Agent': self.user_agent}, verify=False)
                resp.raise_for_status()
                result["content"] = resp.text[:50000]
            else:
                # 使用 urllib
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE
                req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
                with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                    result["content"] = response.read().decode('utf-8', errors='replace')[:50000]
            
            result["success"] = True
            print(f"[OK] Fetched: {url[:60]}...")
            
        except Exception as e:
            result["error"] = str(e)
            print(f"[FAIL] {url[:40]}... : {str(e)[:50]}")
        
        return result
    
    def fetch_ningbo_stats(self) -> dict:
        """获取宁波统计数据"""
        urls = [
            "https://www.ningbo.gov.cn/",
            "https://tjj.ningbo.gov.cn/",
        ]
        
        data = {"source": "宁波市统计局", "data": {}}
        for url in urls:
            content = self.fetch_url(url)
            if content["success"]:
                # 提取可能的统计数据
                numbers = re.findall(r'[\d,.]+%?|[\d,.]+亿元|[\d,.]+万平方米', content["content"])
                data["data"]["extracted_numbers"] = list(set(numbers))[:20]
                break
        
        return data
    
    def fetch_real_estate_data(self) -> dict:
        """获取房地产相关数据"""
        urls = [
            "https://www.nbfcjs.com/",
            "https://fang.tianyancha.com/330200/ningbo",
        ]
        
        data = {"source": "房地产数据", "data": {}}
        for url in urls:
            content = self.fetch_url(url)
            if content["success"]:
                # 提取房产相关数据
                prices = re.findall(r'[\d,.]+元/平方米|[\d,.]+元/㎡|[\d,.]+万', content["content"])
                areas = re.findall(r'[\d,.]+平方米|[\d,.]+㎡|[\d,.]+万㎡', content["content"])
                data["data"]["prices"] = list(set(prices))[:10]
                data["data"]["areas"] = list(set(areas))[:10]
                break
        
        return data
    
    def fetch_government_reports(self) -> dict:
        """获取政府报告中的数据"""
        urls = [
            "https://www.ningbo.gov.cn/xxgk/zwgk/zfgb/",
            "https://www.ningbo.gov.cn/xxgk/zwgk/zwxx/",
        ]
        
        data = {"source": "政府公开数据", "reports": []}
        for url in urls:
            content = self.fetch_url(url)
            if content["success"]:
                # 提取报告标题
                titles = re.findall(r'>([^<]{10,50})</a>', content["content"])
                data["reports"] = titles[:10]
                break
        
        return data
    
    def search_with_api(self, query: str) -> dict:
        """尝试使用免费 API 搜索"""
        # 尝试使用 DuckDuckGo Instant Answer API (免费)
        try:
            url = f"https://api.duckduckgo.com/?q={urllib.parse.quote(query)}&format=json&no_html=1"
            
            ctx = ssl.create_default_context()
            ctx.check_hostname = False
            ctx.verify_mode = ssl.CERT_NONE
            
            req = urllib.request.Request(url, headers={'User-Agent': self.user_agent})
            with urllib.request.urlopen(req, timeout=self.timeout, context=ctx) as response:
                data = json.loads(response.read().decode('utf-8'))
            
            return {
                "query": query,
                "related_topics": [t.get("Text", "") for t in data.get("RelatedTopics", [])[:5]],
                "abstract": data.get("Abstract", ""),
                "source": "DuckDuckGo Instant Answer API"
            }
        except Exception as e:
            return {"query": query, "error": str(e)}
    
    def comprehensive_search(self, query: str) -> dict:
        """综合搜索"""
        print("\n" + "=" * 60)
        print(f"Searching for: {query}")
        print("=" * 60)
        
        results = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "sources": []
        }
        
        # 1. 搜索 API
        print("\n[1/3] DuckDuckGo Instant Answer API...")
        api_result = self.search_with_api(query)
        if "error" not in api_result:
            results["sources"].append({
                "type": "instant_answer",
                "data": api_result
            })
            print(f"      Found {len(api_result.get('related_topics', []))} related topics")
        
        # 2. 尝试获取政府数据
        print("\n[2/3] Government data sources...")
        gov_data = self.fetch_ningbo_stats()
        results["sources"].append({
            "type": "government",
            "data": gov_data
        })
        
        # 3. 尝试获取房产数据
        print("\n[3/3] Real estate data sources...")
        estate_data = self.fetch_real_estate_data()
        results["sources"].append({
            "type": "real_estate",
            "data": estate_data
        })
        
        return results
    
    def generate_market_report(self) -> str:
        """生成宁波商业租赁市场报告"""
        query = "宁波商业租赁市场 2025 租金 空置率"
        results = self.comprehensive_search(query)
        
        report = f"""# 宁波商业租赁市场调研报告

**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')}
**调研方式**: 多数据源自动获取

---

## 一、数据获取情况

### 获取的数据源

| 数据类型 | 状态 | 说明 |
|---------|------|------|
"""

        # 统计各数据源
        source_stats = {"instant_answer": "API数据", "government": "政府网站", "real_estate": "房产网站"}
        for source in results["sources"]:
            src_type = source["type"]
            status = "[OK]" if source.get("data") and not source.get("data", {}).get("error") else "[FAIL]"
            report += f"| {source_stats.get(src_type, src_type)} | {status} | 查看详情 |\n"

        report += """
### 搜索结果

"""

        # 添加 API 结果
        for source in results["sources"]:
            if source["type"] == "instant_answer":
                data = source.get("data", {})
                if data.get("abstract"):
                    report += f"**摘要**: {data['abstract'][:500]}\n\n"
                if data.get("related_topics"):
                    report += "**相关主题**:\n"
                    for topic in data["related_topics"][:5]:
                        report += f"- {topic}\n"
                    report += "\n"

        # 添加提取的数字
        for source in results["sources"]:
            if source["type"] in ["government", "real_estate"]:
                data = source.get("data", {}).get("data", {})
                if data:
                    report += f"**{source['type'].upper()} 数据提取**:\n"
                    if data.get("extracted_numbers"):
                        report += f"数字: {', '.join(data['extracted_numbers'][:10])}\n"
                    if data.get("prices"):
                        report += f"价格: {', '.join(data['prices'][:5])}\n"
                    report += "\n"

        report += """---

## 二、重要说明

### ⚠️ 数据限制

**问题**: 
- 大多数官方数据源需要登录或使用 JavaScript 渲染
- 简单的 HTTP 请求无法获取完整数据
- 实时成交数据通常不对外公开 API

### ✅ 解决方案

1. **访问官方数据源手动获取**:
   - 宁波市统计局: tjj.ningbo.gov.cn (统计数据)
   - 宁波住建局: nbjs.ningbo.gov.cn (房产数据)
   - 透明售房网: www.nbfcjs.com (成交数据)

2. **使用政府开放数据平台**:
   - 浙江政务服务网 data.zj.gov.cn
   - 宁波公共数据开放平台 data.ningbo.gov.cn

3. **付费数据源**:
   - 中国房地产指数系统 CREIS
   - 戴德梁行、高力国际等机构报告

---

## 三、建议的后续步骤

1. **手动获取数据**:
   - 访问上述官方数据源
   - 复制关键数据（租金、空置率、成交量等）
   - 发送给我

2. **我来做深度分析**:
   - 使用 Leo 的 `realestate_agent` 分析数据
   - 使用 `data_analyzer_skill` 处理数值
   - 生成完整的投资分析报告

---

**报告生成时间**: {timestamp}
**生成工具**: Leo Data Fetcher v1.0
""".format(timestamp=datetime.now().strftime('%Y-%m-%d %H:%M'))

        return report


def main():
    print("=" * 60)
    print("Leo Data Fetcher - 宁波商业租赁市场数据获取")
    print("=" * 60)
    
    fetcher = NingboDataFetcher()
    
    # 生成报告
    report = fetcher.generate_market_report()
    
    # 保存报告
    filename = f"宁波商业租赁市场调研_{datetime.now().strftime('%Y-%m-%d')}.md"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n[OK] 报告已保存: {filename}")
    print("\n" + "=" * 60)
    print(report)
    print("=" * 60)


if __name__ == "__main__":
    main()
