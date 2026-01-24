
import os
import sys
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TextGeneratorSkill:
    """
    Core Text Generation Skill
    """
    
    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        self.zhipuai_key = os.environ.get("ZHIPUAI_API_KEY")
        self.deepseek_key = os.environ.get("DEEPSEEK_API_KEY")
        
    def generate(self, 
                prompt: str, 
                context: Optional[str] = None, 
                template: Optional[str] = None,
                format: str = "text",
                **kwargs) -> Dict[str, Any]:
        """
        Generate text based on inputs.
        """
        logger.info(f"Generating content for prompt: {prompt[:50]}...")
        
        # DEBUG: Print keys (masked)
        print(f"DEBUG: TextGenerator Keys - OpenAI: {bool(self.openai_key)}, Anthropic: {bool(self.anthropic_key)}, Zhipu: {bool(self.zhipuai_key)}, DeepSeek: {bool(self.deepseek_key)}")
        if self.deepseek_key:
             print(f"DEBUG: DeepSeek Key first chars: {self.deepseek_key[:5]}")
        
        # 1. Construct Full Prompt
        full_prompt = self._construct_prompt(prompt, context, template)
        
        # 2. Call LLM
        output = ""
        provider = ""
        success = False
        error = ""
        
        try:
            if self.openai_key:
                output = self._call_openai(full_prompt)
                provider = "openai"
                success = True
            elif self.deepseek_key:
                output = self._call_deepseek(full_prompt)
                provider = "deepseek"
                success = True
            elif self.anthropic_key:
                output = self._call_anthropic(full_prompt)
                provider = "anthropic"
                success = True
            elif self.zhipuai_key:
                output = self._call_zhipuai(full_prompt)
                provider = "zhipuai"
                success = True
            else:
                # 真实模式下的 Fallback: 明确告知缺 Key，而不是假装成功
                error = "Missing API Key: Please set ONE of the keys in .env"
                output = f"[SYSTEM ERROR] {error}\n\nProcessed Context Size: {len(full_prompt)} chars."
                success = False
        except Exception as e:
            error = str(e)
            output = f"[GENERATION ERROR] {error}"
            success = False
            
        return {
            "result": output,
            "success": success,
            "provider": provider,
            "error": error
        }

    def _call_deepseek(self, prompt: str) -> str:
        try:
            from openai import OpenAI
            
            client = OpenAI(api_key=self.deepseek_key, base_url="https://api.deepseek.com")
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. You must output in Simplified Chinese (简体中文)."},
                    {"role": "user", "content": prompt}
                ],
                stream=False
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("Please install 'openai' package: pip install openai")

    def _call_zhipuai(self, prompt: str) -> str:
        try:
            from zhipuai import ZhipuAI
            
            client = ZhipuAI(api_key=self.zhipuai_key)
            response = client.chat.completions.create(
                model="glm-4",
                messages=[ 
                    {"role": "system", "content": "You are a helpful AI assistant. You must output in Simplified Chinese (简体中文)."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("Please install 'zhipuai' package: pip install zhipuai")

    def _construct_prompt(self, prompt: str, context: Optional[str], template: Optional[str]) -> str:
        parts = []
        if context:
            parts.append(f"=== CONTEXT ===\n{context}\n")
        if template:
            parts.append(f"=== TEMPLATE ===\n{template}\n")
        
        # Enforce Chinese Output globally
        prompt_with_lang = f"请用简体中文回答。\n{prompt}\n\n(IMPORTANT: Please output in Simplified Chinese/简体中文)"
        parts.append(f"=== INSTRUCTION ===\n{prompt_with_lang}")
        
        return "\n\n".join(parts)

    def _call_openai(self, prompt: str) -> str:
        try:
            import openai
            from openai import OpenAI
            
            client = OpenAI(api_key=self.openai_key)
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a helpful AI assistant. You must output in Simplified Chinese."},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("Please install 'openai' package: pip install openai")

    def _call_anthropic(self, prompt: str) -> str:
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.anthropic_key)
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4096,
                system="You are a helpful AI assistant. You must output in Simplified Chinese (简体中文).",
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("Please install 'anthropic' package: pip install anthropic")

if __name__ == "__main__":
    # Test CLI
    generator = TextGeneratorSkill()
    print(generator.generate("Test prompt", context="Test context"))
