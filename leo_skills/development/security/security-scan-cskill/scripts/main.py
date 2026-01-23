"""
安全扫描技能 Skill
=================
代码安全检查和漏洞扫描
"""

from pathlib import Path
from typing import Dict, Optional, List
import re


class SecurityScanSkill:
    """安全扫描技能"""

    # 常见安全问题模式
    SECURITY_PATTERNS = {
        'hardcoded_secret': {
            'patterns': [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
            ],
            'severity': 'high',
            'description': '硬编码的密钥或密码'
        },
        'sql_injection': {
            'patterns': [
                r'execute\s*\(\s*["\'].*%s.*["\']',
                r'cursor\.execute\s*\(\s*f["\']',
                r'\.format\s*\(.*\).*execute',
            ],
            'severity': 'critical',
            'description': '可能的SQL注入漏洞'
        },
        'xss': {
            'patterns': [
                r'innerHTML\s*=',
                r'document\.write\s*\(',
                r'v-html\s*=',
                r'dangerouslySetInnerHTML',
            ],
            'severity': 'high',
            'description': '可能的XSS漏洞'
        },
        'command_injection': {
            'patterns': [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(\s*[^,\]]+\s*,\s*shell\s*=\s*True',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            'severity': 'critical',
            'description': '可能的命令注入漏洞'
        },
        'insecure_random': {
            'patterns': [
                r'random\.random\s*\(',
                r'Math\.random\s*\(',
            ],
            'severity': 'medium',
            'description': '使用不安全的随机数生成器'
        },
        'debug_enabled': {
            'patterns': [
                r'DEBUG\s*=\s*True',
                r'debug\s*:\s*true',
                r'console\.log\s*\(',
            ],
            'severity': 'low',
            'description': '调试模式可能已启用'
        },
        'insecure_http': {
            'patterns': [
                r'http://',
            ],
            'severity': 'medium',
            'description': '使用不安全的HTTP协议'
        }
    }

    def __init__(self, output_dir: str = "."):
        self.output_dir = Path(output_dir)

    def scan_code(self, code: str, language: str = "python") -> Dict:
        """
        扫描代码中的安全问题

        Args:
            code: 源代码
            language: 编程语言

        Returns:
            扫描结果
        """
        findings = []

        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            for issue_type, config in self.SECURITY_PATTERNS.items():
                for pattern in config['patterns']:
                    if re.search(pattern, line, re.IGNORECASE):
                        findings.append({
                            'type': issue_type,
                            'severity': config['severity'],
                            'description': config['description'],
                            'line': line_num,
                            'code': line.strip()[:100]
                        })

        return {
            'total_issues': len(findings),
            'critical': len([f for f in findings if f['severity'] == 'critical']),
            'high': len([f for f in findings if f['severity'] == 'high']),
            'medium': len([f for f in findings if f['severity'] == 'medium']),
            'low': len([f for f in findings if f['severity'] == 'low']),
            'findings': findings
        }

    def scan_directory(self, directory: str, extensions: List[str] = None) -> Dict:
        """
        扫描目录中的所有文件

        Args:
            directory: 目录路径
            extensions: 文件扩展名列表

        Returns:
            扫描结果
        """
        extensions = extensions or ['.py', '.js', '.ts', '.jsx', '.tsx', '.vue']
        dir_path = Path(directory)

        all_findings = []
        scanned_files = 0

        for ext in extensions:
            for file_path in dir_path.rglob(f'*{ext}'):
                if 'node_modules' in str(file_path) or '.git' in str(file_path):
                    continue

                try:
                    code = file_path.read_text(encoding='utf-8')
                    result = self.scan_code(code)

                    for finding in result['findings']:
                        finding['file'] = str(file_path.relative_to(dir_path))
                        all_findings.append(finding)

                    scanned_files += 1
                except Exception:
                    pass

        return {
            'scanned_files': scanned_files,
            'total_issues': len(all_findings),
            'critical': len([f for f in all_findings if f['severity'] == 'critical']),
            'high': len([f for f in all_findings if f['severity'] == 'high']),
            'medium': len([f for f in all_findings if f['severity'] == 'medium']),
            'low': len([f for f in all_findings if f['severity'] == 'low']),
            'findings': all_findings
        }

    def generate_report(self, scan_result: Dict, format: str = "markdown") -> str:
        """
        生成扫描报告

        Args:
            scan_result: 扫描结果
            format: 报告格式

        Returns:
            报告内容
        """
        if format == "markdown":
            return self._generate_markdown_report(scan_result)
        else:
            return self._generate_text_report(scan_result)

    def _generate_markdown_report(self, result: Dict) -> str:
        """生成Markdown报告"""
        report = f"""# 安全扫描报告

Generated by Leo Security Scan Skill

## 概览

| 指标 | 数量 |
|------|------|
| 扫描文件数 | {result.get('scanned_files', 'N/A')} |
| 总问题数 | {result['total_issues']} |
| 严重 (Critical) | {result['critical']} |
| 高危 (High) | {result['high']} |
| 中危 (Medium) | {result['medium']} |
| 低危 (Low) | {result['low']} |

## 详细发现

"""
        # 按严重程度排序
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3}
        sorted_findings = sorted(
            result['findings'],
            key=lambda x: severity_order.get(x['severity'], 4)
        )

        for finding in sorted_findings:
            severity_emoji = {
                'critical': '🔴',
                'high': '🟠',
                'medium': '🟡',
                'low': '🟢'
            }.get(finding['severity'], '⚪')

            report += f"""### {severity_emoji} {finding['description']}

- **严重程度**: {finding['severity'].upper()}
- **类型**: {finding['type']}
- **位置**: {finding.get('file', 'N/A')}:{finding['line']}
- **代码**: `{finding['code']}`

---

"""

        report += """## 修复建议

1. **硬编码密钥**: 使用环境变量或密钥管理服务
2. **SQL注入**: 使用参数化查询
3. **XSS**: 对用户输入进行转义
4. **命令注入**: 避免使用shell=True，使用参数列表
5. **不安全随机数**: 使用secrets模块生成安全随机数
"""

        return report

    def _generate_text_report(self, result: Dict) -> str:
        """生成文本报告"""
        lines = [
            "=" * 50,
            "安全扫描报告",
            "=" * 50,
            f"总问题数: {result['total_issues']}",
            f"严重: {result['critical']}",
            f"高危: {result['high']}",
            f"中危: {result['medium']}",
            f"低危: {result['low']}",
            "-" * 50
        ]

        for finding in result['findings']:
            lines.append(f"[{finding['severity'].upper()}] {finding['description']}")
            lines.append(f"  位置: {finding.get('file', 'N/A')}:{finding['line']}")
            lines.append(f"  代码: {finding['code']}")
            lines.append("")

        return "\n".join(lines)

    def save_report(self, report: str, filename: str = "security_report.md") -> Path:
        """保存报告"""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        report_path = self.output_dir / filename
        report_path.write_text(report, encoding='utf-8')
        return report_path


def main():
    """示例用法"""
    scanner = SecurityScanSkill(output_dir="./output")

    # 示例代码
    sample_code = '''
import os

# 硬编码密码 - 不安全
password = "admin123"
api_key = "sk-1234567890"

def get_user(user_id):
    # SQL注入风险
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")

def render_html(content):
    # XSS风险
    document.innerHTML = content

def run_command(cmd):
    # 命令注入风险
    os.system(cmd)

# 不安全的随机数
import random
token = random.random()

# 调试模式
DEBUG = True
'''

    result = scanner.scan_code(sample_code)
    report = scanner.generate_report(result)
    saved_path = scanner.save_report(report)

    print(f"扫描完成！发现 {result['total_issues']} 个问题")
    print(f"报告已保存到: {saved_path}")


if __name__ == '__main__':
    main()
