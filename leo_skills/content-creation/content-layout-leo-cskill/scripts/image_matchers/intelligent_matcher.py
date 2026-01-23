# Intelligent Image Matcher Module
# 智能图片匹配模块

from typing import List, Dict, Any, Optional
import re
# logger imported elsewhere

# logger = get_logger(__name__)


class ImageMatcher:
    """智能图片匹配器 - 根据内容智能匹配合适的图片"""

    def __init__(self, style_config: Dict[str, Any]):
        """
        初始化图片匹配器

        Args:
            style_config: 样式配置
        """
        self.style_config = style_config
        self.keyword_to_image_type = style_config.get("keyword_to_image_type", {})
        self.section_colors = style_config.get("section_colors", {})
        self.image_library = style_config.get("image_library", {})

    def match_images_for_content(self, content: str,
                                 sections: List[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        为内容匹配图片

        Args:
            content: 文章内容
            sections: 章节列表

        Returns:
            图片匹配列表
        """
        matches = []

        # 如果有章节定义，按章节匹配
        if sections:
            for section in sections:
                image_suggestions = self._match_section_image(section)
                matches.extend(image_suggestions)
        else:
            # 基于段落分析匹配
            paragraphs = self._split_into_paragraphs(content)
            for i, para in enumerate(paragraphs):
                if self._should_have_image(para, i):
                    matches.append({
                        "paragraph_index": i,
                        "position": "after",
                        "image_types": self._detect_image_types(para),
                        "suggested_captions": self._generate_caption(para)
                    })

        return matches

    def _match_section_image(self, section: Dict[str, Any]) -> List[Dict[str, Any]]:
        """为章节匹配图片"""
        matches = []
        section_type = section.get("type", "body")
        content = section.get("content", "")

        # 根据章节类型决定图片策略
        if section_type == "introduction":
            # 开头用大图
            matches.append({
                "section": section.get("title", ""),
                "position": "after_title",
                "image_type": "hero_image",
                "size": "large",
                "suggestions": self._get_intro_images(content)
            })

        elif section_type == "data_analysis":
            # 数据分析用图表
            matches.append({
                "section": section.get("title", ""),
                "position": "after_heading",
                "image_type": "infographic",
                "size": "medium",
                "suggestions": ["数据图表", "趋势图", "对比柱状图"]
            })

        elif section_type == "regional_focus":
            # 区域聚焦用实景图
            matches.append({
                "section": section.get("title", ""),
                "position": "after_heading",
                "image_type": "location_photo",
                "size": "medium",
                "suggestions": self._get_region_images(content)
            })

        elif section_type == "project_showcase":
            # 项目展示用多图
            matches.append({
                "section": section.get("title", ""),
                "position": "within_content",
                "image_type": "gallery",
                "size": "mixed",
                "suggestions": ["项目鸟瞰图", "样板间实景", "配套景观"]
            })

        return matches

    def _detect_image_types(self, text: str) -> List[str]:
        """检测文本内容需要的图片类型"""
        types = []
        text_lower = text.lower()

        # 关键词匹配
        for keyword, image_type in self.keyword_to_image_type.items():
            if keyword in text_lower:
                types.append(image_type)

        # 数据相关
        if any(word in text for word in ["%", "涨", "跌", "同比", "环比", "数据"]):
            types.append("chart")

        # 项目相关
        if any(word in text for word in ["项目", "楼盘", "小区", "花园", "别墅"]):
            types.append("property_photo")

        # 区域相关
        if any(word in text for word in ["宁波", "余姚", "镇海", "奉化", "区域"]):
            types.append("location_image")

        return list(set(types))

    def _generate_caption(self, text: str) -> str:
        """生成图片说明文字"""
        # 提取关键信息
        sentences = re.split(r'[。！？；]', text)
        for sentence in sentences[:3]:
            if len(sentence) > 10 and len(sentence) < 50:
                return sentence.strip()

        return "示意图"

    def _get_intro_images(self, content: str) -> List[str]:
        """获取开头图片建议"""
        return ["城市天际线", "房产市场全景", "购房场景"]

    def _get_region_images(self, content: str) -> List[str]:
        """获取区域图片建议"""
        # 检测提到的区域
        regions = {
            "余姚": ["余姚城市风光", "牟山山景", "四明山景色"],
            "镇海": ["九龙湖景色", "镇海城区", "九龙湖别墅"],
            "奉化": ["溪口雪窦山", "奉化城市", "溪口古镇"],
            "鄞州": ["东部新城", "南部商务区", "鄞州中心"],
            "海曙": ["海曙老城", "三江口", "月湖"],
            "江北": ["湾头", "奥体中心", "老外滩"]
        }

        for region, images in regions.items():
            if region in content:
                return images

        return ["城市景观", "区域风光"]

    def _split_into_paragraphs(self, content: str) -> List[str]:
        """分割内容为段落"""
        # 按双换行分割
        paragraphs = re.split(r'\n\n+', content.strip())
        return [p.strip() for p in paragraphs if p.strip()]

    def _should_have_image(self, paragraph: str, index: int) -> bool:
        """判断段落是否需要配图"""
        # 规则1：每3-5段配一张图
        if index % 4 == 0:
            return True

        # 规则2：包含关键词的段落
        if any(word in paragraph for word in ["数据", "如图", "例如", "具体来说", "值得注意的是"]):
            return True

        # 规则3：段落长度适中（100-300字）
        length = len(paragraph)
        if 100 <= length <= 300:
            return True

        return False

    def generate_image_prompts(self, content: str,
                              style: str = "professional") -> List[Dict[str, Any]]:
        """
        生成AI图片生成提示词

        Args:
            content: 内容文本
            style: 图片风格

        Returns:
            图片提示词列表
        """
        prompts = []

        # 分析内容提取关键主题
        themes = self._extract_themes(content)

        for theme in themes:
            prompt = self._create_image_prompt(theme, style)
            prompts.append({
                "theme": theme,
                "prompt": prompt,
                "style": style,
                "aspect_ratio": "16:9"
            })

        return prompts

    def _extract_themes(self, content: str) -> List[str]:
        """从内容中提取主题"""
        themes = []

        # 房产相关主题
        real_estate_themes = {
            "modern_residential_complex": ["楼盘", "小区", "社区"],
            "luxury_villa": ["别墅", "豪宅", "度假"],
            "urban_skyline": ["城市", "天际线", "城区"],
            "interior_design": ["户型", "装修", "样板间"],
            "family_life": ["家庭", "生活", "社区"],
            "business_district": ["商务区", "写字楼", "商圈"],
            "green_landscape": ["花园", "景观", "环境"],
            "transportation": ["地铁", "交通", "配套"],
        }

        for theme, keywords in real_estate_themes.items():
            if any(keyword in content for keyword in keywords):
                themes.append(theme)

        return themes

    def _create_image_prompt(self, theme: str, style: str) -> str:
        """创建图片生成提示词"""
        style_prompts = {
            "professional": "professional architectural photography, high resolution, clean composition",
            "warm": "warm and inviting, natural lighting, lifestyle photography",
            "luxury": "luxury real estate photography, elegant, sophisticated, golden hour lighting",
            "modern": "modern minimalist, clean lines, bright and airy, architectural photography"
        }

        theme_prompts = {
            "modern_residential_complex": "modern residential apartment complex exterior, contemporary architecture",
            "luxury_villa": "luxury villa with swimming pool and garden, upscale residential",
            "urban_skyline": "city skyline with modern residential buildings, aerial view",
            "interior_design": "modern living room interior, elegant design, natural light",
            "family_life": "happy family in their new home, warm atmosphere, lifestyle",
            "business_district": "modern urban district with commercial and residential buildings",
            "green_landscape": "beautiful residential garden and landscaping, green spaces",
            "transportation": "modern residential area with convenient transportation, subway station nearby"
        }

        base_prompt = theme_prompts.get(theme, "residential architecture")
        style_desc = style_prompts.get(style, style_prompts["professional"])

        return f"{base_prompt}, {style_desc}, 8k, ultra detailed, photorealistic"


class ImagePromptGenerator:
    """AI图片提示词生成器"""

    def __init__(self, config: Dict[str, Any]):
        """
        初始化提示词生成器

        Args:
            config: 配置
        """
        self.config = config
        self.style_profiles = config.get("style_profiles", {})

    def generate_for_section(self, section_type: str,
                             content: str,
                             style_name: str) -> Dict[str, Any]:
        """
        为特定章节生成图片提示词

        Args:
            section_type: 章节类型
            content: 章节内容
            style_name: 风格名称

        Returns:
            图片提示词配置
        """
        # 提取关键词
        keywords = self._extract_keywords(content)

        # 根据章节类型生成提示词
        section_prompts = {
            "introduction": self._intro_prompt(keywords, style_name),
            "data_analysis": self._data_prompt(keywords, style_name),
            "regional_focus": self._regional_prompt(keywords, style_name),
            "project_showcase": self._project_prompt(keywords, style_name),
            "advice": self._advice_prompt(keywords, style_name),
            "conclusion": self._conclusion_prompt(keywords, style_name)
        }

        prompt_config = section_prompts.get(section_type, self._default_prompt(keywords, style_name))

        # 添加样式修饰
        prompt_config["style_modifiers"] = self._get_style_modifiers(style_name)

        return prompt_config

    def _extract_keywords(self, content: str) -> List[str]:
        """提取关键词"""
        # 简单的关键词提取
        keywords = []
        important_words = ["宁波", "余姚", "镇海", "奉化", "别墅", "楼盘",
                          "房价", "成交", "配套", "地铁", "学区", "湖景"]

        for word in important_words:
            if word in content:
                keywords.append(word)

        return keywords

    def _intro_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """开头图片提示词"""
        return {
            "prompt": f"Modern city skyline of Ningbo, aerial view, residential and commercial buildings, {style} photography",
            "type": "hero",
            "size": "large",
            "position": "top"
        }

    def _data_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """数据分析图片提示词"""
        return {
            "prompt": f"Real estate data visualization, infographic charts showing market trends, clean data design",
            "type": "infographic",
            "size": "medium",
            "position": "after_heading"
        }

    def _regional_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """区域聚焦图片提示词"""
        # 根据关键词选择区域
        region = "Ningbo urban area"
        if "余姚" in keywords:
            region = "Yuyao mountain area, scenic"
        elif "镇海" in keywords or "九龙湖" in keywords:
            region = "Jiulong Lake area, lake view"
        elif "奉化" in keywords or "溪口" in keywords:
            region = "Xikou scenic area, mountains"

        return {
            "prompt": f"Beautiful {region}, residential area, natural environment, high quality photography",
            "type": "location",
            "size": "medium",
            "position": "after_heading"
        }

    def _project_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """项目展示图片提示词"""
        return {
            "prompt": f"Luxury villa exterior, modern design, beautiful garden, high-end residential, {style} architectural photography",
            "type": "showcase",
            "size": "large",
            "position": "within_content"
        }

    def _advice_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """建议部分图片提示词"""
        return {
            "prompt": f"Happy family in their new home, warm atmosphere, lifestyle photography, {style}",
            "type": "lifestyle",
            "size": "medium",
            "position": "after_heading"
        }

    def _conclusion_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """结尾图片提示词"""
        return {
            "prompt": f"Modern residential community, peaceful atmosphere, hopeful mood, sunset lighting, {style}",
            "type": "mood",
            "size": "medium",
            "position": "end"
        }

    def _default_prompt(self, keywords: List[str], style: str) -> Dict[str, Any]:
        """默认图片提示词"""
        return {
            "prompt": f"Modern residential architecture, professional photography, {style}",
            "type": "general",
            "size": "medium",
            "position": "within_content"
        }

    def _get_style_modifiers(self, style_name: str) -> List[str]:
        """获取风格修饰词"""
        style_map = {
            "data_driven": ["clean", "professional", "high contrast"],
            "story_telling": ["warm", "emotional", "cinematic"],
            "minimalist_professional": ["clean", "minimal", "architectural"],
            "vibrant_attention": ["vibrant", "colorful", "high energy"],
            "emotional_resonance": ["warm", "soft", "inviting"],
            "magazine_premium": ["elegant", "sophisticated", "editorial"]
        }

        return style_map.get(style_name, ["professional", "high quality"])
