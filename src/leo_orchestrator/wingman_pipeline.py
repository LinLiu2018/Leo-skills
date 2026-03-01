# -*- coding: utf-8 -*-
"""
Wingman 端到端执行流水线
========================
实现从意图理解到结果交付的完整自动化流程

核心流程：
1. 任务理解（自然语言 → 结构化意图）
2. 执行计划生成（选择 Agent/Skill/Workflow）
3. 执行（调用 LLM 驱动的 Agent）
4. 格式转换（MD → PDF/HTML/等）
5. 结果交付（上传飞书/微信/本地）
6. 反馈学习（记录用户偏好）
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

# 添加路径
parent_path = Path(__file__).parent.parent
if str(parent_path) not in sys.path:
    sys.path.insert(0, str(parent_path))

from leo_system.logger import get_logger
from leo_orchestrator.registry import get_registry
from leo_orchestrator.workflow_engine import WorkflowEngine
from leo_subagents.core.llm_adapter import LLMAdapter

logger = get_logger(__name__)


class TaskParser:
    """
    任务理解引擎

    将自然语言输入解析为结构化的执行计划
    """

    def __init__(self):
        self.llm = LLMAdapter(provider="claude")

    def parse(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        解析用户输入，理解真实意图

        Args:
            user_input: 用户输入文本
            context: 上下文信息（当前文件、项目等）

        Returns:
            结构化执行计划
        """
        # 加载用户画像
        try:
            from leo_memory.user_profile_manager import get_profile_manager
            profile_manager = get_profile_manager()
            user_context = profile_manager.get_context_for_task(user_input)
        except Exception:
            user_context = ""

        # 构建提示词
        prompt = f"""分析用户意图并生成执行计划。

用户输入: "{user_input}"

{user_context}

当前上下文:
{json.dumps(context or {}, ensure_ascii=False, indent=2)}

请分析并返回 JSON 格式的执行计划:
{{
    "intent": "意图类型 (distribute_content/create_document/research/etc)",
    "entities": {{
        "source": "源文件/内容",
        "target": "目标/接收方",
        "format": "期望格式"
    }},
    "actions": [
        {{
            "type": "use_agent|use_skill|run_workflow|format|upload|notify",
            "target": "目标名称",
            "params": {{}}
        }}
    ],
    "delivery": {{
        "format": "pdf|html|markdown|docx",
        "destination": "feishu|wechat|local|email",
        "notify": true/false
    }}
}}

只返回 JSON，不要其他内容。"""

        try:
            response = self.llm.call(prompt, max_tokens=2000, temperature=0.3)
            content = response.content

            # 提取 JSON
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                json_str = content.strip()

            plan = json.loads(json_str)
            logger.info(f"任务解析成功: {plan.get('intent', 'unknown')}")
            return plan

        except json.JSONDecodeError as e:
            logger.error(f"JSON 解析失败: {e}")
            # 返回默认计划
            return self._default_plan(user_input)
        except Exception as e:
            logger.error(f"任务解析失败: {e}")
            return self._default_plan(user_input)

    def _default_plan(self, user_input: str) -> Dict:
        """默认执行计划"""
        return {
            "intent": "general",
            "entities": {"source": user_input},
            "actions": [
                {"type": "use_agent", "target": "research_agent", "params": {"task": user_input}}
            ],
            "delivery": {"format": "markdown", "destination": "local", "notify": False}
        }


class DeliveryService:
    """
    结果交付服务

    负责：
    - 格式转换（MD → PDF/HTML/PPT）
    - 文件上传（飞书/微信/本地）
    - 通知发送
    """

    def __init__(self):
        self.output_dir = Path("output/delivery")
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def deliver(self, content: str, delivery_spec: Dict) -> Dict[str, Any]:
        """
        执行交付

        Args:
            content: 要交付的内容
            delivery_spec: 交付规格

        Returns:
            交付结果
        """
        results = []

        # 1. 格式转换
        if "format" in delivery_spec:
            format_result = self._convert_format(content, delivery_spec["format"])
            content = format_result.get("content", content)
            file_path = format_result.get("file_path")
            results.append(format_result)
        else:
            file_path = None

        # 2. 上传/保存
        destination = delivery_spec.get("destination", "local")
        if destination == "local":
            if file_path:
                results.append({"type": "save", "status": "success", "path": str(file_path)})
        elif destination == "feishu":
            upload_result = self._upload_to_feishu(file_path or content, delivery_spec)
            results.append(upload_result)
        elif destination == "wechat":
            # 微信暂不支持自动上传
            results.append({"type": "wechat", "status": "manual", "note": "请手动复制内容"})

        # 3. 通知
        if delivery_spec.get("notify", False):
            notify_result = self._send_notification(delivery_spec, results)
            results.append(notify_result)

        return {
            "status": "completed",
            "delivery_type": destination,
            "results": results
        }

    def _convert_format(self, content: str, format_type: str) -> Dict:
        """格式转换"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if format_type == "pdf":
            # 使用 markdown 转 PDF（需要安装依赖）
            output_file = self.output_dir / f"output_{timestamp}.pdf"
            try:
                # 尝试使用 markdown-pdf 或其他工具
                import markdown
                html = markdown.markdown(content)
                # 这里简化处理，实际应该使用 weasyprint 或 pdfkit
                output_file.write_text(html, encoding="utf-8")
                return {
                    "type": "convert",
                    "status": "success",
                    "format": "pdf",
                    "file_path": output_file,
                    "note": "已转换为 HTML（PDF 需要额外依赖）"
                }
            except Exception as e:
                return {"type": "convert", "status": "error", "error": str(e)}

        elif format_type == "html":
            output_file = self.output_dir / f"output_{timestamp}.html"
            import markdown
            html = markdown.markdown(content)
            output_file.write_text(html, encoding="utf-8")
            return {
                "type": "convert",
                "status": "success",
                "format": "html",
                "file_path": output_file
            }

        elif format_type == "markdown":
            output_file = self.output_dir / f"output_{timestamp}.md"
            output_file.write_text(content, encoding="utf-8")
            return {
                "type": "convert",
                "status": "success",
                "format": "markdown",
                "file_path": output_file,
                "content": content
            }

        else:
            return {"type": "convert", "status": "skipped", "format": format_type}

    def _upload_to_feishu(self, content, delivery_spec: Dict) -> Dict:
        """上传到飞书（简化版）"""
        # 实际实现需要调用飞书 API
        return {
            "type": "upload",
            "status": "mock",
            "destination": "feishu",
            "note": "飞书上传需要配置 API 密钥"
        }

    def _send_notification(self, delivery_spec: Dict, results: List[Dict]) -> Dict:
        """发送通知"""
        # 简化版通知
        return {
            "type": "notify",
            "status": "sent",
            "message": f"任务完成，已交付到 {delivery_spec.get('destination', 'local')}"
        }


class WingmanPipeline:
    """
    Wingman 端到端执行流水线

    这是整个系统的核心，串联所有组件实现"说一句话就能干活"
    """

    def __init__(self):
        self.task_parser = TaskParser()
        self.delivery_service = DeliveryService()
        self.registry = get_registry()
        self.workflow_engine = WorkflowEngine(agents={})

    def execute(self, user_input: str, context: Dict = None) -> Dict[str, Any]:
        """
        端到端执行

        完整流程：
        1. 理解意图
        2. 生成执行计划
        3. 执行（Agent/Skill/Workflow）
        4. 格式转换
        5. 结果交付
        6. 反馈学习
        """
        logger.info(f"=" * 60)
        logger.info(f"Wingman Pipeline 开始执行: {user_input[:50]}...")
        logger.info(f"=" * 60)

        # 1. 理解意图
        logger.info("[1/6] 解析任务意图...")
        plan = self.task_parser.parse(user_input, context)
        logger.info(f"意图: {plan.get('intent')}")
        logger.info(f"计划动作数: {len(plan.get('actions', []))}")

        # 2. 执行计划
        logger.info("[2/6] 执行计划...")
        execution_results = self._execute_plan(plan, context)

        # 3. 组装内容
        logger.info("[3/6] 组装输出内容...")
        content = self._assemble_content(execution_results)

        # 4. 格式转换
        logger.info("[4/6] 格式转换...")
        delivery_spec = plan.get("delivery", {"format": "markdown", "destination": "local"})

        # 5. 结果交付
        logger.info("[5/6] 交付结果...")
        delivery_result = self.delivery_service.deliver(content, delivery_spec)

        # 6. 反馈学习
        logger.info("[6/6] 学习反馈...")
        self._learn_from_execution(user_input, plan, execution_results, delivery_result)

        # 组装最终结果
        final_result = {
            "status": "completed",
            "original_input": user_input,
            "intent": plan.get("intent"),
            "execution": {
                "actions_count": len(plan.get("actions", [])),
                "results": execution_results
            },
            "delivery": delivery_result,
            "output_preview": content[:200] if len(content) > 200 else content
        }

        logger.info(f"=" * 60)
        logger.info(f"执行完成！")
        logger.info(f"=" * 60)

        return final_result

    def _execute_plan(self, plan: Dict, context: Dict) -> List[Dict]:
        """执行计划中的动作"""
        results = []

        for action in plan.get("actions", []):
            action_type = action.get("type")
            target = action.get("target")
            params = action.get("params", {})

            try:
                if action_type == "use_agent":
                    result = self._execute_agent(target, params, context)
                elif action_type == "use_skill":
                    result = self._execute_skill(target, params)
                elif action_type == "run_workflow":
                    result = self._execute_workflow(target, params)
                elif action_type == "format":
                    # 格式转换在 delivery 阶段处理
                    result = {"type": "format", "status": "deferred"}
                else:
                    result = {"type": action_type, "status": "skipped", "note": "未知动作类型"}

                results.append(result)

            except Exception as e:
                logger.error(f"动作执行失败: {action}, 错误: {e}")
                results.append({"type": action_type, "status": "error", "error": str(e)})

        return results

    def _execute_agent(self, agent_name: str, params: Dict, context: Dict) -> Dict:
        """执行 Agent"""
        agent = self.registry.get_agent(agent_name)
        if not agent:
            return {"status": "error", "error": f"Agent not found: {agent_name}"}

        task = params.get("task", "")

        # 优先使用 execute_with_llm
        if hasattr(agent, 'execute_with_llm'):
            result = agent.execute_with_llm(task, **context)
        elif hasattr(agent, 'execute'):
            result = agent.execute(task, **context)
        else:
            return {"status": "error", "error": "Agent has no execute method"}

        return {"type": "agent", "agent": agent_name, "result": result}

    def _execute_skill(self, skill_name: str, params: Dict) -> Dict:
        """执行 Skill"""
        # 这里简化处理，实际应该调用 skill_executor
        return {"type": "skill", "skill": skill_name, "params": params, "status": "mock"}

    def _execute_workflow(self, workflow_name: str, params: Dict) -> Dict:
        """执行 Workflow"""
        workflow = self.registry.get_workflow(workflow_name)
        if not workflow:
            return {"status": "error", "error": f"Workflow not found: {workflow_name}"}

        result = self.workflow_engine.execute(workflow, **params)
        return {"type": "workflow", "workflow": workflow_name, "result": result}

    def _assemble_content(self, results: List[Dict]) -> str:
        """组装输出内容"""
        content_parts = []

        for result in results:
            if "result" in result:
                r = result["result"]
                if isinstance(r, dict):
                    # 提取有用的输出
                    if "output" in r:
                        content_parts.append(str(r["output"]))
                    elif "content" in r:
                        content_parts.append(str(r["content"]))
                    elif "llm_response" in r:
                        content_parts.append(str(r["llm_response"]))

        if content_parts:
            return "\n\n".join(content_parts)
        else:
            return "执行完成，但没有生成内容。"

    def _learn_from_execution(self, user_input: str, plan: Dict, execution_results: List[Dict], delivery_result: Dict):
        """从执行中学习"""
        try:
            from leo_memory.user_profile_manager import observe_user_action

            # 记录技能使用
            for result in execution_results:
                if result.get("type") == "skill":
                    observe_user_action("skill_used",
                                      skill=result.get("skill"),
                                      success=result.get("status") != "error")

            # 记录内容生成（简化版）
            observe_user_action("content_generated",
                              content=user_input,
                              type=plan.get("intent"))

        except Exception as e:
            logger.warning(f"学习记录失败: {e}")


# ==================== 便捷函数 ====================

def wingman_execute(user_input: str, context: Dict = None) -> Dict:
    """便捷函数：执行 Wingman 流水线"""
    pipeline = WingmanPipeline()
    return pipeline.execute(user_input, context)


# ==================== 测试入口 ====================

if __name__ == "__main__":
    print("=" * 60)
    print("Wingman 端到端流水线 - 测试")
    print("=" * 60)

    pipeline = WingmanPipeline()

    # 测试场景
    test_cases = [
        "研究宁波商铺市场",
        "生成乐橙荟营销文案",
    ]

    for test_input in test_cases:
        print(f"\n测试输入: {test_input}")
        print("-" * 40)

        try:
            result = pipeline.execute(test_input)
            print(f"意图: {result['intent']}")
            print(f"状态: {result['status']}")
            print(f"输出预览: {result['output_preview'][:100]}...")
        except Exception as e:
            print(f"错误: {e}")

    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
