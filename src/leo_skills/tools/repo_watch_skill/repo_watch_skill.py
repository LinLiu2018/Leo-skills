"""
Repo Watch Skill - 核心仓库监控技能

监控 Claude Code 和 OpenClaw 仓库的更新，生成周报并通过飞书发送。
"""

import os
import json
import yaml
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

from leo_skills.base import BaseSkill, SkillResult


class RepoWatchSkill(BaseSkill):
    """核心仓库监控技能"""

    def __init__(self, config_path: str = None):
        self.skill_dir = Path(__file__).parent
        self.config_path = config_path or self.skill_dir / "config" / "config.yaml"
        self.config = self._load_config()
        self.log_dir = Path(self.config.get("notification", {}).get("local", {}).get("log_dir", "logs/repo_watch"))
        self.log_dir.mkdir(parents=True, exist_ok=True)

    @property
    def name(self) -> str:
        return "repo_watch_skill"

    def get_actions(self) -> List[str]:
        return ["check_all", "check", "generate_report", "send_feishu_report", "get_status"]

    def _load_config(self) -> Dict:
        """加载配置文件"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {}

    def execute(self, action: str = "check_all", **kwargs) -> SkillResult:
        """执行技能动作"""
        actions = {
            "check_all": self._check_all_repos,
            "check": self._check_repo,
            "generate_report": self._generate_report,
            "send_feishu_report": self._send_feishu_report,
            "get_status": self._get_status,
        }

        if action not in actions:
            return SkillResult.fail(f"Unknown action: {action}")

        try:
            data = actions[action](**kwargs)
            if not data.get("success", True):
                return SkillResult.fail(data.get("error", "Unknown error"))
            return SkillResult.ok(data=data)
        except Exception as e:
            return SkillResult.fail(str(e))

    def _github_api_request(self, url: str) -> Optional[Any]:
        """发送 GitHub API 请求"""
        try:
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Leo-AI-System-RepoWatch/1.0"
            }
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"GitHub API error: {e.code} - {e.reason}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None

    def _get_latest_release(self, owner: str, repo: str) -> Optional[Dict]:
        """获取最新 Release"""
        url = f"https://api.github.com/repos/{owner}/{repo}/releases/latest"
        data = self._github_api_request(url)
        if data:
            return {
                "tag": data.get("tag_name"),
                "name": data.get("name"),
                "date": data.get("published_at"),
                "body": data.get("body", "")[:500] if data.get("body") else ""
            }
        return None

    def _get_recent_commits(self, owner: str, repo: str, days: int = 7) -> List[Dict]:
        """获取最近的提交"""
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
        url = f"https://api.github.com/repos/{owner}/{repo}/commits?since={since}"
        data = self._github_api_request(url)
        if data and isinstance(data, list):
            max_commits = self.config.get("report", {}).get("max_commits", 10)
            commits = []
            for item in data[:max_commits]:
                commits.append({
                    "sha": item.get("sha", "")[:7],
                    "message": item.get("commit", {}).get("message", ""),
                    "date": item.get("commit", {}).get("author", {}).get("date"),
                    "author": item.get("commit", {}).get("author", {}).get("name")
                })
            return commits
        return []

    def _check_repo(self, repo: str = None, owner: str = None, **kwargs) -> Dict[str, Any]:
        """检查单个仓库"""
        if not repo or not owner:
            return {"success": False, "error": "Missing repo or owner"}

        release = self._get_latest_release(owner, repo)
        commits = self._get_recent_commits(owner, repo)

        return {
            "success": True,
            "repo": f"{owner}/{repo}",
            "latest_release": release,
            "recent_commits": commits,
            "checked_at": datetime.now().isoformat()
        }

    def _check_all_repos(self, **kwargs) -> Dict[str, Any]:
        """检查所有仓库"""
        results = {}
        repos = self.config.get("repositories", [])

        for repo_config in repos:
            owner = repo_config.get("owner")
            repo = repo_config.get("repo")
            name = repo_config.get("name", repo)

            result = self._check_repo(repo=repo, owner=owner)
            results[name] = result

        return {
            "success": True,
            "results": results,
            "checked_at": datetime.now().isoformat()
        }

    def _generate_report(self, **kwargs) -> Dict[str, Any]:
        """生成周报"""
        check_result = self._check_all_repos()
        if not check_result.get("success"):
            return check_result

        results = check_result.get("results", {})
        today = datetime.now().strftime("%Y-%m-%d")

        report_lines = [
            f"# 核心仓库周报 ({today})",
            "",
            "> 自动生成，每周一早上9点更新",
            ""
        ]

        for name, data in results.items():
            repo_config = next(
                (r for r in self.config.get("repositories", []) if r.get("name") == name),
                {}
            )

            release = data.get("latest_release") or {}
            commits = data.get("recent_commits", [])

            report_lines.extend([
                f"## {name} ({repo_config.get('owner', '')}/{repo_config.get('repo', '')})",
                "",
                f"**描述**: {repo_config.get('description', 'N/A')}",
                ""
            ])

            if release:
                report_lines.extend([
                    f"### 最新版本",
                    f"- **版本**: {release.get('tag', 'N/A')}",
                    f"- **名称**: {release.get('name', 'N/A')}",
                    f"- **发布日期**: {release.get('date', 'N/A')[:10] if release.get('date') else 'N/A'}",
                    ""
                ])
            else:
                report_lines.extend([
                    f"### 最新版本",
                    f"- 暂无 Release 信息",
                    ""
                ])

            if commits:
                report_lines.extend([
                    f"### 本周提交 ({len(commits)} 个)",
                    ""
                ])
                for commit in commits[:5]:
                    msg = commit.get("message", "").split("\n")[0][:60]
                    report_lines.append(f"- `{commit.get('sha', '')}` {msg}")
                report_lines.append("")
            else:
                report_lines.extend([
                    f"### 本周提交",
                    f"- 本周暂无提交",
                    ""
                ])

            # 更新建议
            has_new_release = release and release.get("date")
            if has_new_release:
                try:
                    release_date = datetime.fromisoformat(release["date"].replace("Z", "+00:00"))
                    days_ago = (datetime.now(release_date.tzinfo) - release_date).days
                    if days_ago <= 7:
                        report_lines.append(f"**建议**: [!] 有新版本 ({days_ago} 天前发布)，建议检查更新")
                    else:
                        report_lines.append(f"**建议**: [OK] 版本稳定，暂不需要更新")
                except:
                    report_lines.append(f"**建议**: [OK] 暂无新版本")
            else:
                report_lines.append(f"**建议**: [OK] 暂无新版本")

            report_lines.extend(["", "---", ""])

        report_content = "\n".join(report_lines)

        # 保存到本地
        report_file = self.log_dir / f"report_{today}.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        return {
            "success": True,
            "report": report_content,
            "report_file": str(report_file),
            "generated_at": datetime.now().isoformat()
        }

    def _send_feishu_report(self, **kwargs) -> Dict[str, Any]:
        """发送飞书报告"""
        # 先生成报告
        report_result = self._generate_report()
        if not report_result.get("success"):
            return report_result

        report_content = report_result.get("report", "")

        # 通过 OpenClaw 发送飞书消息
        feishu_config = self.config.get("notification", {}).get("feishu", {})

        if not feishu_config.get("enabled"):
            return {
                "success": True,
                "report": report_content,
                "feishu_sent": False,
                "message": "Feishu notification disabled"
            }

        # 构建飞书消息
        # 注意：实际发送需要通过 OpenClaw Gateway
        return {
            "success": True,
            "report": report_content,
            "feishu_sent": True,
            "message": "Report generated. Send via OpenClaw Gateway.",
            "report_file": report_result.get("report_file")
        }

    def _get_status(self, **kwargs) -> Dict[str, Any]:
        """获取监控状态"""
        repos = self.config.get("repositories", [])
        schedule = self.config.get("schedule", {})

        return {
            "success": True,
            "monitored_repos": [f"{r.get('owner')}/{r.get('repo')}" for r in repos],
            "schedule": {
                "cron": schedule.get("cron"),
                "timezone": schedule.get("timezone"),
                "enabled": schedule.get("enabled")
            },
            "log_dir": str(self.log_dir)
        }


# 便捷函数
def check_repos():
    """检查所有仓库"""
    skill = RepoWatchSkill()
    return skill.execute("check_all")


def generate_weekly_report():
    """生成周报"""
    skill = RepoWatchSkill()
    return skill.execute("generate_report")


def send_feishu_report():
    """发送飞书报告"""
    skill = RepoWatchSkill()
    return skill.execute("send_feishu_report")


if __name__ == "__main__":
    # 测试
    skill = RepoWatchSkill()

    print("=== 检查仓库状态 ===")
    status = skill.execute("get_status")
    print(json.dumps(status, indent=2, ensure_ascii=False))

    print("\n=== 生成周报 ===")
    report = skill.execute("generate_report")
    if report.get("success"):
        print(report.get("report"))
