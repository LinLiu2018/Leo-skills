# Article Generator Module
# 文章生成模块

from typing import Dict, Any, List, Optional
from utils.logger import get_logger

logger = get_logger(__name__)


class ArticleGenerator:
    """文章生成器"""

    def __init__(self, ai_config: Dict[str, Any], content_config: Dict[str, Any],
                 keywords_config: Dict[str, Any], projects_config: List[Dict[str, Any]]):
        """
        初始化文章生成器

        Args:
            ai_config: AI 配置
            content_config: 内容配置
            keywords_config: 关键词配置
            projects_config: 项目配置
        """
        self.ai_config = ai_config
        self.content_config = content_config
        self.keywords_config = keywords_config
        self.projects_config = projects_config

        # 初始化 AI 客户端
        self._init_ai_client()

    def _init_ai_client(self):
        """初始化 AI 客户端"""
        provider = self.ai_config.get("provider", "zhipuai")

        if provider == "zhipuai":
            try:
                from zhipuai import ZhipuAI
                self.client = ZhipuAI(api_key=self.ai_config.get("api_key"))
                logger.info("使用智谱 AI GLM-4")
            except ImportError:
                logger.warning("zhipuai 未安装，将使用模板生成")
                self.client = None
        elif provider == "openai":
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.ai_config.get("api_key"))
                logger.info("使用 OpenAI")
            except ImportError:
                logger.warning("openai 未安装，将使用模板生成")
                self.client = None
        else:
            self.client = None

    def generate(self, item: Dict[str, Any], analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        生成文章

        Args:
            item: 原始信息项
            analysis: 分析结果

        Returns:
            生成的文章字典
        """
        category = item.get("category", "market")

        if category == "policy":
            return self.generate_policy_article(item, analysis)
        elif category == "market":
            return self.generate_market_article(item, analysis)
        else:
            return self.generate_regional_article(item, analysis)

    def generate_policy_article(self, item: Dict[str, Any],
                                 analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成政策解读类文章"""
        prompt = self._build_policy_prompt(item, analysis)

        if self.client:
            content = self._call_ai(prompt)
        else:
            content = self._generate_from_template("policy", item, analysis)

        title = self._generate_title(item, analysis, "policy")

        return {
            "title": title,
            "content": content,
            "category": "policy",
            "source_item_id": item.get("url", ""),
            "keywords": self._generate_tags(item, analysis),
            "summary": content[:200] + "..." if len(content) > 200 else content
        }

    def generate_market_article(self, item: Dict[str, Any],
                                analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成市场分析类文章"""
        prompt = self._build_market_prompt(item, analysis)

        if self.client:
            content = self._call_ai(prompt)
        else:
            content = self._generate_from_template("market", item, analysis)

        title = self._generate_title(item, analysis, "market")

        return {
            "title": title,
            "content": content,
            "category": "market",
            "source_item_id": item.get("url", ""),
            "keywords": self._generate_tags(item, analysis),
            "summary": content[:200] + "..." if len(content) > 200 else content
        }

    def generate_regional_article(self, item: Dict[str, Any],
                                  analysis: Dict[str, Any]) -> Dict[str, Any]:
        """生成区域聚焦类文章"""
        prompt = self._build_regional_prompt(item, analysis)

        if self.client:
            content = self._call_ai(prompt)
        else:
            content = self._generate_from_template("regional", item, analysis)

        title = self._generate_title(item, analysis, "regional")

        return {
            "title": title,
            "content": content,
            "category": "regional",
            "source_item_id": item.get("url", ""),
            "keywords": self._generate_tags(item, analysis),
            "summary": content[:200] + "..." if len(content) > 200 else content
        }

    def _build_policy_prompt(self, item: Dict[str, Any],
                             analysis: Dict[str, Any]) -> str:
        """构建政策文章的 AI 提示词"""
        project_info = self._get_relevant_project(analysis)

        prompt = f"""你是一位专业的房地产内容创作者。请基于以下信息撰写一篇微信公众号文章。

【原始信息】
标题：{item.get('title', '')}
内容：{item.get('content', '')[:1000]}

【分析要点】
政策要点：{', '.join(analysis.get('policy_points', [])[:3])}
市场影响：{analysis.get('market_impact', '')}
涉及区域：{', '.join(analysis.get('regions', []))}

【要求】
1. 标题要吸引人，包含政策关键词
2. 正文结构：引言 + 政策解读 + 市场影响 + 购房建议 + 结语
3. 自然融入项目信息（{project_info}）
4. 段落简短，适合手机阅读
5. 专业但不晦涩，贴近购房者
6. 字数800-1200字
7. 使用 Markdown 格式

请生成文章内容。"""

        return prompt

    def _build_market_prompt(self, item: Dict[str, Any],
                             analysis: Dict[str, Any]) -> str:
        """构建市场文章的 AI 提示词"""
        project_info = self._get_relevant_project(analysis)

        prompt = f"""你是一位专业的房地产内容创作者。请基于以下信息撰写一篇微信公众号文章。

【原始信息】
标题：{item.get('title', '')}
内容：{item.get('content', '')[:1000]}

【分析要点】
市场趋势：{', '.join(analysis.get('trends', []))}
情感倾向：{analysis.get('sentiment', '')}
涉及区域：{', '.join(analysis.get('regions', []))}

【要求】
1. 标题要吸引人，包含市场关键词
2. 正文结构：引言 + 市场现状 + 数据分析 + 购房建议 + 结语
3. 自然融入项目信息（{project_info}）
4. 段落简短，适合手机阅读
5. 数据支撑，观点明确
6. 字数800-1200字
7. 使用 Markdown 格式

请生成文章内容。"""

        return prompt

    def _build_regional_prompt(self, item: Dict[str, Any],
                               analysis: Dict[str, Any]) -> str:
        """构建区域文章的 AI 提示词"""
        regions = analysis.get("regions", [])
        region = regions[0] if regions else "宁波"

        prompt = f"""你是一位专业的房地产内容创作者。请基于以下信息撰写一篇微信公众号文章。

【原始信息】
标题：{item.get('title', '')}
内容：{item.get('content', '')[:1000]}

【分析要点】
涉及区域：{', '.join(regions)}
产品类型：{', '.join(analysis.get('products', []))}

【要求】
1. 标题包含区域名称，吸引目标读者
2. 正文结构：引言 + 区域优势 + 项目推荐 + 购房建议 + 结语
3. 重点介绍{region}的度假别墅/养老地产价值
4. 段落简短，适合手机阅读
5. 字数800-1200字
6. 使用 Markdown 格式

请生成文章内容。"""

        return prompt

    def _call_ai(self, prompt: str) -> str:
        """调用 AI 生成内容"""
        try:
            provider = self.ai_config.get("provider", "zhipuai")

            if provider == "zhipuai":
                response = self.client.chat.completions.create(
                    model=self.ai_config.get("model", "glm-4"),
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.ai_config.get("temperature", 0.7),
                    max_tokens=self.ai_config.get("max_tokens", 2000)
                )
                return response.choices[0].message.content

            elif provider == "openai":
                response = self.client.chat.completions.create(
                    model=self.ai_config.get("model", "gpt-4"),
                    messages=[
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.ai_config.get("temperature", 0.7),
                    max_tokens=self.ai_config.get("max_tokens", 2000)
                )
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"AI 生成失败: {e}")
            return ""

    def _generate_from_template(self, article_type: str,
                                 item: Dict[str, Any],
                                 analysis: Dict[str, Any]) -> str:
        """从模板生成文章"""
        # 这里提供简单的模板回退
        templates = {
            "policy": self._policy_template(item, analysis),
            "market": self._market_template(item, analysis),
            "regional": self._regional_template(item, analysis)
        }
        return templates.get(article_type, "")

    def _policy_template(self, item: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """政策文章模板"""
        title = item.get("title", "")
        policy_points = analysis.get("policy_points", [])
        regions = analysis.get("regions", ["宁波"])

        content = f"""# {title}

## 最新政策解读

近日，{'、'.join(regions)}发布新政策，对房地产市场产生重要影响。

## 核心政策要点

{chr(10).join(f'- {p}' for p in policy_points[:5])}

## 市场影响分析

这项政策对度假别墅市场将产生深远影响。对于计划在宁波周边购置度假房产的客户来说，这无疑是一个重要的参考信号。

## 购房建议

1. 关注政策细则，把握购房时机
2. 选择有实力的开发商
3. 优先考虑配套完善的区域

## 推荐项目

- **余姚牟山玫瑰园**：山水环抱，真山真水
- **九龙湖利时玖珑湾**：湖景别墅，品质生活

*本文仅供参考，具体以官方发布为准*
"""
        return content

    def _market_template(self, item: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """市场文章模板"""
        title = item.get("title", "")
        trends = analysis.get("trends", [])

        content = f"""# {title}

## 市场观察

宁波度假别墅市场近期呈现出新的变化。

## 趋势分析

{chr(10).join(f'- {t}' for t in trends)}

## 数据解读

根据最新市场数据，购房者在选择度假房产时更加注重品质和配套。

## 购房建议

建议有意向的客户：
1. 实地考察，了解项目详情
2. 对比不同区域的优势
3. 关注开发商的口碑和实力

*市场有风险，投资需谨慎*
"""
        return content

    def _regional_template(self, item: Dict[str, Any], analysis: Dict[str, Any]) -> str:
        """区域文章模板"""
        regions = analysis.get("regions", ["宁波"])
        region = regions[0] if regions else "宁波"

        content = f"""# {region}度假房产推荐

## 区域优势

{region}拥有得天独厚的自然环境和完善的配套设施，是度假置业的理想选择。

## 为什么选择{region}？

1. **自然环境**：山清水秀，空气清新
2. **交通便利**：快速路网，轻松通达
3. **配套齐全**：商业、医疗、教育一应俱全

## 推荐项目

- **余姚牟山玫瑰园**：真山真水，度假首选
- **九龙湖利时玖珑湾**：湖景美宅，品质生活

*欢迎实地考察品鉴*
"""
        return content

    def _generate_title(self, item: Dict[str, Any], analysis: Dict[str, Any],
                        article_type: str) -> str:
        """生成标题"""
        base_title = item.get("title", "")

        title_templates = {
            "policy": [
                f"重磅！{base_title}",
                f"买房必看：{base_title}",
                f"政策解读：{base_title}",
                f"最新！{base_title}，宁波购房者注意"
            ],
            "market": [
                f"{base_title}，市场风向变了？",
                f"最新数据：{base_title}",
                f"楼市观察：{base_title}",
                f"买房人必看：{base_title}"
            ],
            "regional": [
                f"{base_title}",
                f"为什么选择这里买房？{base_title}",
                f"{base_title}，度假置业的理想选择"
            ]
        }

        templates = title_templates.get(article_type, [base_title])
        return templates[0]  # 返回第一个模板，实际可以智能选择

    def _generate_tags(self, item: Dict[str, Any],
                       analysis: Dict[str, Any]) -> List[str]:
        """生成文章标签"""
        tags = []

        # 添加分类标签
        category = item.get("category", "")
        category_tags = {
            "policy": ["政策解读", "购房政策"],
            "market": ["市场分析", "房价走势"],
            "regional": ["区域推荐", "度假别墅"]
        }
        tags.extend(category_tags.get(category, []))

        # 添加区域标签
        regions = analysis.get("regions", [])
        for region in regions[:2]:
            tags.append(f"{region}房产")

        # 添加产品标签
        products = analysis.get("products", [])
        for product in products[:2]:
            tags.append(product)

        # 确保标签唯一
        return list(set(tags))

    def _get_relevant_project(self, analysis: Dict[str, Any]) -> str:
        """根据分析结果获取相关项目"""
        regions = analysis.get("regions", [])
        products = analysis.get("products", [])

        # 查找匹配的项目
        for project in self.projects_config:
            project_regions = project.get("keywords", [])
            project_name = project.get("name", "")

            # 如果区域匹配
            if any(region in project_regions for region in regions):
                return project_name

            # 如果产品类型匹配
            if any(product in project_regions for product in products):
                return project_name

        # 默认项目
        return "余姚牟山玫瑰园"
