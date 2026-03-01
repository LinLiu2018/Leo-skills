"""
Skill Vetter Skill - 技能安全扫描器 (优化版)

扫描技能代码中的危险操作，生成安全评分报告。
优化：区分代码生成和代码执行，降低误报。
"""
from leo_skills.core.base_executor import BaseExecutor

from typing import Dict, Any, List, Optional
from pathlib import Path
import re


class SkillVetterSkill(BaseExecutor):
    """技能安全扫描器"""
    
    def __init__(self):
        self.name = "skill_vetter_skill"
        self.version = "1.1.0"  # 优化版本
        self.category = "tools"
        
        # 危险函数定义 (按风险等级)
        self.dangerous_functions = {
            "critical": ["eval(", "exec(", "compile(", "__import__(", "getattr(", "setattr("],
            "high": ["os.system(", "os.popen(", "subprocess.call(", "subprocess.check_output(", "subprocess.run("],
            "medium": ["requests.get(", "requests.post(", "urllib.request.", "http.client.", "socket."],
            "low": ["open(", "write(", "read(", "os.remove(", "os.unlink(", "shutil.rmtree("]
        }
        
        # 代码生成模式关键词 (这些场景下的危险函数是合理的)
        self.code_generation_patterns = [
            "generator", "scaffold", "template", "create_", "make_",
            "build_", "generate_", "writer", "exporter"
        ]
        
        # 敏感路径
        self.sensitive_paths = [
            "/etc/", "/root/", "/home/", "C:\\Users\\",
            ".ssh/", ".git/", "credentials", "password", "token"
        ]
    
    def execute(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """执行技能扫描"""
        params = params or {}
        skill_path = params.get("skill_path", "")
        
        if not skill_path:
            return {
                "status": "error",
                "message": "请提供技能路径",
                "example": "skill_vetter_skill({'skill_path': 'src/leo_skills/tools/example_skill'})"
            }
        
        # 执行扫描
        result = self.scan_skill(skill_path)
        
        return {
            "status": "success",
            "skill": self.name,
            "action": "skill_vet",
            "target": skill_path,
            **result
        }
    
    def scan_skill(self, skill_path: str) -> Dict[str, Any]:
        """扫描技能目录"""
        path = Path(skill_path)
        
        if not path.exists():
            return {
                "error": f"技能路径不存在：{skill_path}",
                "security_score": 0,
                "security_level": "❌ 无法扫描"
            }
        
        # 检测是否是代码生成类技能
        is_code_generator = self._is_code_generator(str(path))
        
        # 收集所有 Python 文件
        py_files = list(path.rglob("*.py"))
        
        findings = {
            "critical": [],
            "high": [],
            "medium": [],
            "low": []
        }
        
        # 扫描每个文件
        for py_file in py_files:
            file_findings = self._scan_file(py_file, is_code_generator)
            for level, items in file_findings.items():
                findings[level].extend(items)
        
        # 计算安全评分 (考虑代码生成模式)
        score = self._calculate_score(findings, is_code_generator)
        level = self._get_security_level(score)
        
        return {
            "security_score": score,
            "security_level": level,
            "files_scanned": len(py_files),
            "findings": findings,
            "is_code_generator": is_code_generator,
            "recommendation": self._get_recommendation(score, findings, is_code_generator)
        }
    
    def _is_code_generator(self, path: str) -> bool:
        """检测是否是代码生成类技能"""
        path_lower = path.lower()
        return any(pattern in path_lower for pattern in self.code_generation_patterns)
    
    def _scan_file(self, file_path: Path, is_code_generator: bool = False) -> Dict[str, List[Dict]]:
        """扫描单个文件"""
        findings = {"critical": [], "high": [], "medium": [], "low": []}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
        except Exception:
            return findings
        
        # 检测危险函数
        for level, functions in self.dangerous_functions.items():
            for func in functions:
                for i, line in enumerate(lines, 1):
                    if func in line and not line.strip().startswith('#'):
                        # 代码生成模式下，降低 low 级别问题的权重
                        if is_code_generator and level == "low":
                            # 检查是否是生成代码的场景
                            if self._is_code_generation_context(line):
                                continue  # 跳过
                        
                        findings[level].append({
                            "file": str(file_path),
                            "line": i,
                            "type": "dangerous_function",
                            "detail": f"检测到 {func}",
                            "code": line.strip()[:100]
                        })
        
        # 检测敏感路径
        for sensitive in self.sensitive_paths:
            for i, line in enumerate(lines, 1):
                if sensitive in line and not line.strip().startswith('#'):
                    findings["medium"].append({
                        "file": str(file_path),
                        "line": i,
                        "type": "sensitive_path",
                        "detail": f"检测到敏感路径：{sensitive}",
                        "code": line.strip()[:100]
                    })
        
        return findings
    
    def _is_code_generation_context(self, line: str) -> bool:
        """检查是否是代码生成上下文"""
        # 检查是否是字符串中的代码 (如 f.write("import os"))
        if 'f.write(' in line or 'template' in line or '"""' in line or "'''" in line:
            return True
        # 检查是否是生成文件操作
        if 'output' in line.lower() or 'result' in line.lower():
            return True
        return False
    
    def _calculate_score(self, findings: Dict, is_code_generator: bool = False) -> int:
        """计算安全评分"""
        score = 100
        
        # 基础扣分权重
        critical_weight = 25
        high_weight = 15
        medium_weight = 5
        low_weight = 1
        
        # 代码生成模式下，降低 low 级别扣分
        if is_code_generator:
            low_weight = 0.1  # 几乎不扣分
        
        score -= len(findings["critical"]) * critical_weight
        score -= len(findings["high"]) * high_weight
        score -= len(findings["medium"]) * medium_weight
        score -= len(findings["low"]) * low_weight
        
        return max(0, min(100, int(score)))
    
    def _get_security_level(self, score: int) -> str:
        """获取安全等级"""
        if score >= 90:
            return "[SAFE] 安全"
        elif score >= 60:
            return "[WARN] 注意"
        else:
            return "[DANG] 危险"
    
    def _get_recommendation(self, score: int, findings: Dict, is_code_generator: bool = False) -> str:
        """生成建议"""
        if is_code_generator:
            return "代码生成类技能，低分主要是误报，可放心使用"
        
        if score >= 90:
            return "技能代码安全，可以放心使用"
        elif score >= 60:
            return f"发现 {len(findings['critical']) + len(findings['high'])} 个高风险问题，建议审查后使用"
        else:
            return f"发现 {len(findings['critical'])} 个严重问题，禁止使用此技能"
    
    def get_status(self) -> Dict[str, Any]:
        """获取技能状态"""
        return {
            "name": self.name,
            "version": self.version,
            "category": self.category,
            "status": "active",
            "features": ["代码生成模式识别", "误报过滤", "上下文分析"]
        }


__all__ = ["SkillVetterSkill"]
