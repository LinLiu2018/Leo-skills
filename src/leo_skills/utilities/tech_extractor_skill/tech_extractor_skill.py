"""
tech_extractor_skill - 技术信息提取技能

从文本、文档、代码中提取技术栈信息、识别技术趋势。
"""

import re
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

from leo_skills.core.base_executor import BaseExecutor


@dataclass
class Technology:
    """技术/工具数据"""
    name: str
    category: str  # language, framework, library, tool, platform, database, concept
    confidence: float = 1.0
    version: str = ""
    related: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class TechExtractor(BaseExecutor):
    """
    技术信息提取技能

    支持操作：
    - extract: 从文本中提取技术栈
    - analyze_stack: 分析项目技术栈（通过 package.json / requirements.txt / 文件列表）
    - detect_patterns: 检测代码中的技术模式（API端点、环境变量、导入等）
    - compare: 对比两组技术栈的异同
    """

    # 技术关键词库
    TECH_DB = {
        "language": {
            "python": "Python", "javascript": "JavaScript", "typescript": "TypeScript",
            "java": "Java", "go": "Go", "rust": "Rust", "c++": "C++", "c#": "C#",
            "ruby": "Ruby", "php": "PHP", "swift": "Swift", "kotlin": "Kotlin",
            "dart": "Dart", "scala": "Scala", "r": "R", "julia": "Julia",
            "lua": "Lua", "perl": "Perl", "shell": "Shell/Bash",
        },
        "framework": {
            "react": "React", "vue": "Vue.js", "angular": "Angular",
            "next.js": "Next.js", "nextjs": "Next.js", "nuxt": "Nuxt.js",
            "svelte": "Svelte", "django": "Django", "flask": "Flask",
            "fastapi": "FastAPI", "express": "Express.js", "spring": "Spring",
            "rails": "Ruby on Rails", "laravel": "Laravel", "gin": "Gin",
            "nest.js": "NestJS", "nestjs": "NestJS",
            "flutter": "Flutter", "react native": "React Native",
            "electron": "Electron", "tauri": "Tauri",
        },
        "library": {
            "pandas": "Pandas", "numpy": "NumPy", "scipy": "SciPy",
            "tensorflow": "TensorFlow", "pytorch": "PyTorch", "keras": "Keras",
            "scikit-learn": "scikit-learn", "sklearn": "scikit-learn",
            "transformers": "HuggingFace Transformers",
            "langchain": "LangChain", "llamaindex": "LlamaIndex",
            "opencv": "OpenCV", "sqlalchemy": "SQLAlchemy", "prisma": "Prisma",
            "tailwindcss": "Tailwind CSS", "tailwind": "Tailwind CSS",
            "bootstrap": "Bootstrap", "material-ui": "Material UI",
            "antd": "Ant Design", "ant design": "Ant Design",
            "vant": "Vant", "element-ui": "Element UI",
            "axios": "Axios", "redux": "Redux", "zustand": "Zustand",
            "pinia": "Pinia", "vuex": "Vuex",
            "jest": "Jest", "vitest": "Vitest", "pytest": "pytest",
            "playwright": "Playwright", "cypress": "Cypress",
        },
        "database": {
            "postgresql": "PostgreSQL", "postgres": "PostgreSQL",
            "mysql": "MySQL", "mongodb": "MongoDB", "redis": "Redis",
            "elasticsearch": "Elasticsearch", "sqlite": "SQLite",
            "supabase": "Supabase", "firebase": "Firebase",
            "pinecone": "Pinecone", "qdrant": "Qdrant", "weaviate": "Weaviate",
        },
        "tool": {
            "docker": "Docker", "kubernetes": "Kubernetes", "k8s": "Kubernetes",
            "nginx": "Nginx", "webpack": "Webpack", "vite": "Vite",
            "esbuild": "esbuild", "git": "Git", "github": "GitHub",
            "jenkins": "Jenkins", "github actions": "GitHub Actions",
            "terraform": "Terraform", "ansible": "Ansible",
            "grafana": "Grafana", "prometheus": "Prometheus", "sentry": "Sentry",
        },
        "platform": {
            "aws": "AWS", "azure": "Azure", "gcp": "Google Cloud",
            "vercel": "Vercel", "netlify": "Netlify", "heroku": "Heroku",
            "cloudflare": "Cloudflare", "vultr": "Vultr",
            "阿里云": "阿里云", "腾讯云": "腾讯云", "华为云": "华为云",
        },
        "concept": {
            "微服务": "微服务架构", "serverless": "Serverless",
            "restful": "RESTful API", "graphql": "GraphQL", "grpc": "gRPC",
            "websocket": "WebSocket", "ci/cd": "CI/CD", "devops": "DevOps",
            "mlops": "MLOps", "消息队列": "消息队列",
            "kafka": "Kafka", "rabbitmq": "RabbitMQ",
            "oauth": "OAuth", "jwt": "JWT",
            "rag": "RAG", "向量数据库": "向量数据库",
            "agent": "AI Agent", "function calling": "Function Calling",
        },
    }

    def __init__(self) -> None:
        self.name = "tech_extractor_skill"

    def execute(
        self,
        action: str = "extract",
        context: Optional[Dict[str, Any]] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """统一执行入口"""
        params = dict(context or {})
        params.update(kwargs)

        actions = {
            "extract": self._extract,
            "analyze_stack": self._analyze_stack,
            "detect_patterns": self._detect_patterns,
            "compare": self._compare,
        }

        handler = actions.get(action)
        if not handler:
            return {"status": "error", "message": f"不支持的操作: {action}，可用: {list(actions.keys())}"}
        return handler(**params)

    def _extract(self, text: str = "", **_) -> Dict[str, Any]:
        """从文本中提取技术栈"""
        if not text:
            return {"status": "error", "message": "请提供 text（文本内容）"}

        text_lower = text.lower()
        found: Dict[str, List[Technology]] = {}

        for category, tech_map in self.TECH_DB.items():
            for keyword, display_name in tech_map.items():
                pattern = r'(?:^|[\s,;.!?()（）\[\]{}"\'/])' + re.escape(keyword) + r'(?:$|[\s,;.!?()（）\[\]{}"\'/])'
                matches = re.findall(pattern, text_lower)
                if matches:
                    confidence = min(1.0, len(matches) * 0.3 + 0.4)
                    tech = Technology(name=display_name, category=category, confidence=round(confidence, 2))
                    if category not in found:
                        found[category] = []
                    if not any(t.name == display_name for t in found[category]):
                        found[category].append(tech)

        for cat in found:
            found[cat].sort(key=lambda t: t.confidence, reverse=True)

        total = sum(len(techs) for techs in found.values())
        return {
            "status": "success",
            "total_found": total,
            "by_category": {cat: [t.to_dict() for t in techs] for cat, techs in found.items()},
            "flat_list": [t.name for techs in found.values() for t in techs],
            "summary": self._generate_summary(found),
        }

    def _analyze_stack(self, files: Optional[List[str]] = None,
                       package_json: Optional[Dict] = None,
                       requirements: Optional[List[str]] = None, **_) -> Dict[str, Any]:
        """分析项目技术栈"""
        techs: List[Technology] = []

        if package_json:
            deps = {}
            deps.update(package_json.get("dependencies", {}))
            deps.update(package_json.get("devDependencies", {}))
            for pkg_name in deps:
                pkg_lower = pkg_name.lower()
                for category, tech_map in self.TECH_DB.items():
                    for keyword, display_name in tech_map.items():
                        if keyword in pkg_lower or pkg_lower in keyword:
                            techs.append(Technology(name=display_name, category=category))
                            break

        if requirements:
            for req in requirements:
                pkg_name = re.split(r'[>=<!\[\]]', req.strip())[0].lower().replace("-", "_")
                for category, tech_map in self.TECH_DB.items():
                    for keyword, display_name in tech_map.items():
                        if keyword.replace("-", "_") == pkg_name:
                            techs.append(Technology(name=display_name, category=category))
                            break

        if files:
            ext_map = {
                ".py": ("Python", "language"), ".js": ("JavaScript", "language"),
                ".ts": ("TypeScript", "language"), ".tsx": ("React + TypeScript", "framework"),
                ".vue": ("Vue.js", "framework"), ".java": ("Java", "language"),
                ".go": ("Go", "language"), ".rs": ("Rust", "language"),
                ".wxml": ("微信小程序", "framework"),
            }
            for filepath in files:
                ext = "." + filepath.rsplit(".", 1)[-1] if "." in filepath else ""
                if ext in ext_map:
                    name, cat = ext_map[ext]
                    if not any(t.name == name for t in techs):
                        techs.append(Technology(name=name, category=cat))

        # 去重
        unique = []
        seen = set()
        for t in techs:
            if t.name not in seen:
                seen.add(t.name)
                unique.append(t)

        return {
            "status": "success",
            "stack": [t.to_dict() for t in unique],
            "categories": sorted(set(t.category for t in unique)),
            "total": len(unique),
        }

    def _detect_patterns(self, text: str = "", **_) -> Dict[str, Any]:
        """检测代码/文档中的技术模式"""
        if not text:
            return {"status": "error", "message": "请提供 text（代码或文档内容）"}

        patterns = {
            "api_endpoints": re.findall(r'(?:GET|POST|PUT|DELETE|PATCH)\s+[/\w{}:-]+', text),
            "env_vars": re.findall(r'[A-Z][A-Z_]{2,}(?:_KEY|_SECRET|_TOKEN|_URL|_HOST|_PORT|_DB)', text),
            "imports": re.findall(r'(?:import|from|require|use)\s+[\w./@-]+', text),
            "urls": re.findall(r'https?://[^\s<>"\')\]]+', text),
            "docker_images": re.findall(r'(?:FROM|image:)\s+[\w./-]+(?::[\w.-]+)?', text),
            "ports": re.findall(r'(?:port|PORT)[:\s=]+(\d{2,5})', text),
            "versions": re.findall(r'v?\d+\.\d+(?:\.\d+)?', text),
        }
        patterns = {k: v for k, v in patterns.items() if v}

        return {
            "status": "success",
            "patterns_found": sum(len(v) for v in patterns.values()),
            "patterns": patterns,
        }

    def _compare(self, stack_a: Optional[List[str]] = None,
                 stack_b: Optional[List[str]] = None, **_) -> Dict[str, Any]:
        """对比两组技术栈"""
        if not stack_a or not stack_b:
            return {"status": "error", "message": "请提供 stack_a 和 stack_b（两组技术栈列表）"}

        set_a = set(s.lower() for s in stack_a)
        set_b = set(s.lower() for s in stack_b)
        common = set_a & set_b

        return {
            "status": "success",
            "common": sorted(common),
            "only_in_a": sorted(set_a - set_b),
            "only_in_b": sorted(set_b - set_a),
            "similarity": round(len(common) / max(len(set_a | set_b), 1), 2),
        }

    @staticmethod
    def _generate_summary(found: Dict[str, List[Technology]]) -> str:
        """生成技术栈摘要"""
        labels = {
            "language": "编程语言", "framework": "框架", "library": "库",
            "database": "数据库", "tool": "工具", "platform": "平台", "concept": "技术概念",
        }
        parts = []
        for category, techs in found.items():
            names = [t.name for t in techs[:5]]
            parts.append(f"{labels.get(category, category)}: {', '.join(names)}")
        return " | ".join(parts) if parts else "未识别到技术栈"


__all__ = ["TechExtractor"]
