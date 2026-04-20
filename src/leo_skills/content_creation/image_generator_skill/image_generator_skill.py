"""
AI 图片生成技能

基于 OpenAI DALL-E 3 / GPT-Image-1 API 的图片生成技能。
"""

import base64
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

from leo_skills.core.evolution import EvolvableSkill


class ImageGeneratorSkill(EvolvableSkill):
    """
    AI 图片生成技能

    支持文本生成图片、图片编辑、风格变换等功能。
    """

    # 预设的 UI 风格 prompt 模板
    STYLE_TEMPLATES = {
        "miniprogram-ui": "微信小程序UI界面设计，现代简约风格，圆角卡片，清晰的图标，{prompt}",
        "app-ui": "移动应用UI界面设计，Material Design风格，{prompt}",
        "web-ui": "网页UI设计，响应式布局，现代扁平化风格，{prompt}",
        "marketing": "营销海报设计，吸引眼球，专业商业风格，{prompt}",
        "icon": "图标设计，简洁清晰，矢量风格，{prompt}",
        "illustration": "插画风格，扁平化设计，柔和配色，{prompt}",
    }

    def __init__(self, config_path: Optional[str] = None):
        super().__init__("image_generator", Path(__file__).parent / "evolution.json")
        self.config_path = Path(config_path) if config_path else Path(__file__).parent / "config" / "config.yaml"
        self.config = self._load_config()
        self.client = self._init_client()
        self.output_dir = Path(__file__).parent / "output"
        self.output_dir.mkdir(exist_ok=True)

    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        if self.config_path.exists():
            try:
                import yaml
                with open(self.config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f) or {}
            except Exception:
                pass
        return {
            "openai": {
                "api_key": os.getenv("OPENAI_API_KEY", ""),
                "model": "dall-e-3",
                "default_size": "1024x1024",
                "default_quality": "standard"
            }
        }

    def _init_client(self) -> Optional["OpenAI"]:
        """初始化 OpenAI 客户端"""
        if OpenAI is None:
            return None

        api_key = self.config.get("openai", {}).get("api_key") or os.getenv("OPENAI_API_KEY")
        if api_key:
            return OpenAI(api_key=api_key)
        return None

    def execute(self, action: str = "generate", **kwargs) -> Dict[str, Any]:
        """
        执行图片生成任务

        Args:
            action: 操作类型
                - generate: 生成单张图片
                - batch_generate: 批量生成
                - edit: 编辑图片
                - variation: 生成变体
            prompt: 图片描述
            prompts: 批量描述列表
            size: 图片尺寸 (1024x1024, 1792x1024, 1024x1792)
            quality: 质量 (standard, hd)
            style: 预设风格
            n: 生成数量

        Returns:
            执行结果
        """
        # Handle health_check and execute before client check (for scheduled tasks)
        if action in ("health_check", "execute"):
            return {
                "success": True,
                "status": "ok",
                "skill": "image_generator",
                "client_ready": self.client is not None,
                "timestamp": datetime.now().isoformat()
            }

        if not self.client:
            return {
                "success": False,
                "error": "OpenAI client not initialized. Please install openai package and set API key.",
                "hint": "pip install openai && export OPENAI_API_KEY=your-key"
            }

        if action == "generate":
            return self._generate_image(**kwargs)
        elif action == "batch_generate":
            return self._batch_generate(**kwargs)
        elif action == "edit":
            return self._edit_image(**kwargs)
        elif action == "variation":
            return self._create_variation(**kwargs)
        elif action == "list_styles":
            return {"success": True, "styles": list(self.STYLE_TEMPLATES.keys())}
        else:
            return {"success": False, "error": f"Unknown action: {action}"}

    def _generate_image(
        self,
        prompt: str,
        size: str = None,
        quality: str = None,
        style: str = None,
        save: bool = True,
        **kwargs
    ) -> Dict[str, Any]:
        """生成单张图片"""
        try:
            # 应用风格模板
            final_prompt = self._apply_style(prompt, style)

            # 获取配置
            model = self.config.get("openai", {}).get("model", "dall-e-3")
            size = size or self.config.get("openai", {}).get("default_size", "1024x1024")
            quality = quality or self.config.get("openai", {}).get("default_quality", "standard")

            # 调用 API
            response = self.client.images.generate(
                model=model,
                prompt=final_prompt,
                size=size,
                quality=quality,
                n=1,
                response_format="url"
            )

            image_url = response.data[0].url
            revised_prompt = getattr(response.data[0], 'revised_prompt', final_prompt)

            result = {
                "success": True,
                "url": image_url,
                "prompt": final_prompt,
                "revised_prompt": revised_prompt,
                "model": model,
                "size": size,
                "quality": quality
            }

            # 保存图片
            if save:
                saved_path = self._save_image_from_url(image_url, prompt)
                if saved_path:
                    result["saved_path"] = str(saved_path)

            # 学习成功经验
            self.learn(f"Generated image for: {prompt[:50]}...")

            return result

        except Exception as e:
            self.learn(f"Failed to generate: {str(e)}", "error_context")
            return {"success": False, "error": str(e)}

    def _batch_generate(
        self,
        prompts: List[str],
        style: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """批量生成图片"""
        results = []
        for prompt in prompts:
            result = self._generate_image(prompt=prompt, style=style, **kwargs)
            results.append(result)

        success_count = sum(1 for r in results if r.get("success"))

        return {
            "success": success_count > 0,
            "total": len(prompts),
            "success_count": success_count,
            "results": results
        }

    def _edit_image(
        self,
        image_path: str,
        prompt: str,
        mask_path: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """编辑图片"""
        try:
            with open(image_path, "rb") as image_file:
                image_data = image_file.read()

            mask_data = None
            if mask_path:
                with open(mask_path, "rb") as mask_file:
                    mask_data = mask_file.read()

            response = self.client.images.edit(
                image=image_data,
                mask=mask_data,
                prompt=prompt,
                n=1,
                size="1024x1024"
            )

            return {
                "success": True,
                "url": response.data[0].url,
                "prompt": prompt
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _create_variation(self, image_path: str, n: int = 1, **kwargs) -> Dict[str, Any]:
        """创建图片变体"""
        try:
            with open(image_path, "rb") as image_file:
                response = self.client.images.create_variation(
                    image=image_file,
                    n=n,
                    size="1024x1024"
                )

            urls = [data.url for data in response.data]

            return {
                "success": True,
                "urls": urls,
                "count": len(urls)
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def _apply_style(self, prompt: str, style: str = None) -> str:
        """应用风格模板"""
        if style and style in self.STYLE_TEMPLATES:
            return self.STYLE_TEMPLATES[style].format(prompt=prompt)
        return prompt

    def _save_image_from_url(self, url: str, prompt: str) -> Optional[Path]:
        """从 URL 下载并保存图片"""
        try:
            import urllib.request

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() else "_" for c in prompt[:30])
            filename = f"{timestamp}_{safe_name}.png"
            filepath = self.output_dir / filename

            urllib.request.urlretrieve(url, filepath)
            return filepath

        except Exception as e:
            print(f"Failed to save image: {e}")
            return None


# 便捷函数
def generate_image(prompt: str, style: str = None, **kwargs) -> Dict[str, Any]:
    """快速生成图片"""
    skill = ImageGeneratorSkill()
    return skill.execute(action="generate", prompt=prompt, style=style, **kwargs)


def generate_ui_mockup(description: str, ui_type: str = "miniprogram-ui") -> Dict[str, Any]:
    """生成 UI 效果图"""
    skill = ImageGeneratorSkill()
    return skill.execute(action="generate", prompt=description, style=ui_type)
