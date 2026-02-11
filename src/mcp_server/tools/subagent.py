"""
Subagent AI 编排工具模块

提供功能:
- 支持 OpenAI 和 Anthropic API (兼容自定义端点)
- 无状态 AI 子任务委派
- 并行子任务执行
- Token 使用量统计和成本追踪
- 条件分支决策
- 状态跟踪和进度报告
"""

import json
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Any, Dict, List, Optional

import requests

from ..utils import logger, NetworkError, ValidationError, retry
from .subagent_config import get_config

# 工具类别信息
CATEGORY_NAME = "Subagent AI Orchestration"
CATEGORY_DESCRIPTION = (
    "Delegate subtasks to external AI models with parallel execution and cost tracking"
)
TOOLS = [
    "subagent_call",
    "subagent_parallel",
    "subagent_conditional",
    "subagent_config_set",
    "subagent_config_get",
    "subagent_config_list",
]

# 模型价格表 (USD per 1K tokens)
MODEL_PRICING = {
    # OpenAI
    "gpt-3.5-turbo": {"input": 0.0015, "output": 0.002},
    "gpt-3.5-turbo-16k": {"input": 0.003, "output": 0.004},
    "gpt-4": {"input": 0.03, "output": 0.06},
    "gpt-4-32k": {"input": 0.06, "output": 0.12},
    "gpt-4-turbo": {"input": 0.01, "output": 0.03},
    "gpt-4-turbo-preview": {"input": 0.01, "output": 0.03},
    "gpt-4o": {"input": 0.005, "output": 0.015},
    "gpt-4o-mini": {"input": 0.00015, "output": 0.0006},
    # Anthropic Claude
    "claude-3-opus-20240229": {"input": 0.015, "output": 0.075},
    "claude-3-sonnet-20240229": {"input": 0.003, "output": 0.015},
    "claude-3-haiku-20240307": {"input": 0.00025, "output": 0.00125},
    "claude-3-5-sonnet-20241022": {"input": 0.003, "output": 0.015},
    "claude-3-5-haiku-20241022": {"input": 0.001, "output": 0.005},
    # ZhipuAI GLM (估算价格，以人民币计，按 1 USD = 7 CNY 换算)
    "glm-4": {"input": 0.0143, "output": 0.0143},  # ¥0.1/1K tokens
    "glm-4-plus": {"input": 0.0714, "output": 0.0714},  # ¥0.5/1K tokens
    "glm-4-air": {"input": 0.00143, "output": 0.00143},  # ¥0.01/1K tokens
    "glm-4-airx": {"input": 0.0143, "output": 0.0143},  # ¥0.1/1K tokens
    "glm-4-flash": {"input": 0.0, "output": 0.0},  # 免费
}


class TokenCounter:
    """Token 计数器 - 使用字符近似算法"""

    @staticmethod
    def count_tokens(text: str) -> int:
        """
        估算文本的 token 数量
        使用简单的字符近似: 1 token ≈ 4 characters
        对于 CJK 字符: 1 token ≈ 2 characters

        Args:
            text: 要计数的文本

        Returns:
            估算的 token 数量
        """
        if not text:
            return 0

        # 检测 CJK 字符
        cjk_pattern = re.compile(r"[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff]")
        cjk_chars = len(cjk_pattern.findall(text))
        other_chars = len(text) - cjk_chars

        # CJK: ~2 chars per token, Other: ~4 chars per token
        estimated_tokens = (cjk_chars / 2.0) + (other_chars / 4.0)
        return int(estimated_tokens)

    @staticmethod
    def count_messages_tokens(messages: List[Dict[str, str]]) -> int:
        """
        计算消息列表的 token 数量

        Args:
            messages: 消息列表 [{"role": "user", "content": "..."}]

        Returns:
            总 token 数量
        """
        total = 0
        for msg in messages:
            # 每条消息有少量开销（role + 分隔符）
            total += 4  # 消息开销
            total += TokenCounter.count_tokens(msg.get("content", ""))
        return total


class CostCalculator:
    """成本计算器"""

    @staticmethod
    def calculate_cost(model: str, input_tokens: int, output_tokens: int) -> Dict[str, float]:
        """
        计算 API 调用成本

        Args:
            model: 模型名称
            input_tokens: 输入 token 数量
            output_tokens: 输出 token 数量

        Returns:
            成本信息 {"input_cost", "output_cost", "total_cost"}
        """
        pricing = MODEL_PRICING.get(model, {"input": 0.0, "output": 0.0})

        input_cost = (input_tokens / 1000.0) * pricing["input"]
        output_cost = (output_tokens / 1000.0) * pricing["output"]

        return {
            "input_cost": round(input_cost, 6),
            "output_cost": round(output_cost, 6),
            "total_cost": round(input_cost + output_cost, 6),
        }


class OpenAIClient:
    """OpenAI API 客户端"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 OpenAI 客户端

        Args:
            api_key: API 密钥，默认从环境变量或配置文件读取
            api_base: API 基础 URL，默认从环境变量或配置文件读取
        """
        config = get_config()
        self.api_key = api_key or config.get_api_key("openai")
        self.api_base = api_base or config.get_api_base("openai")

        if not self.api_key:
            raise ValidationError("OPENAI_API_KEY not found in environment or config file")

    @retry(max_attempts=3, delay=2.0)
    def call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        调用 OpenAI Chat Completion API

        Args:
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            timeout: 超时时间（秒）

        Returns:
            响应数据

        Raises:
            NetworkError: API 调用失败
        """
        url = f"{self.api_base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {"model": model, "messages": messages, "temperature": temperature}

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            logger.info(f"Calling OpenAI API: model={model}, messages={len(messages)}")
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            logger.info(f"OpenAI API success: {data.get('usage', {})}")
            return data

        except requests.exceptions.Timeout:
            raise NetworkError(f"OpenAI API timeout after {timeout}s")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValidationError("Invalid OpenAI API key")
            elif e.response.status_code == 429:
                raise NetworkError("OpenAI API rate limit exceeded")
            else:
                raise NetworkError(
                    f"OpenAI API error: {e.response.status_code} - {e.response.text}"
                )
        except Exception as e:
            raise NetworkError(f"OpenAI API call failed: {str(e)}")


class AnthropicClient:
    """Anthropic Claude API 客户端"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 Anthropic 客户端

        Args:
            api_key: API 密钥，默认从环境变量或配置文件读取
            api_base: API 基础 URL，默认从环境变量或配置文件读取
        """
        config = get_config()
        self.api_key = api_key or config.get_api_key("anthropic")
        self.api_base = api_base or config.get_api_base("anthropic")

        if not self.api_key:
            raise ValidationError("ANTHROPIC_API_KEY not found in environment or config file")

    @retry(max_attempts=3, delay=2.0)
    def call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: int = 4096,
        temperature: float = 0.7,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        调用 Anthropic Messages API

        Args:
            model: 模型名称
            messages: 消息列表 (必须转换为 Anthropic 格式)
            max_tokens: 最大生成 token 数 (Anthropic 必需参数)
            temperature: 温度参数
            timeout: 超时时间（秒）

        Returns:
            响应数据 (转换为 OpenAI 兼容格式)

        Raises:
            NetworkError: API 调用失败
        """
        url = f"{self.api_base}/messages"
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # 转换消息格式: 提取 system 消息
        system_message = None
        user_messages = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        payload = {
            "model": model,
            "messages": user_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        if system_message:
            payload["system"] = system_message

        try:
            logger.info(f"Calling Anthropic API: model={model}, messages={len(messages)}")
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            data = response.json()

            # 转换为 OpenAI 兼容格式
            converted = {
                "choices": [
                    {
                        "message": {"role": "assistant", "content": data["content"][0]["text"]},
                        "finish_reason": data.get("stop_reason", "stop"),
                    }
                ],
                "usage": {
                    "prompt_tokens": data["usage"]["input_tokens"],
                    "completion_tokens": data["usage"]["output_tokens"],
                    "total_tokens": data["usage"]["input_tokens"] + data["usage"]["output_tokens"],
                },
            }

            logger.info(f"Anthropic API success: {converted['usage']}")
            return converted

        except requests.exceptions.Timeout:
            raise NetworkError(f"Anthropic API timeout after {timeout}s")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValidationError("Invalid Anthropic API key")
            elif e.response.status_code == 429:
                raise NetworkError("Anthropic API rate limit exceeded")
            else:
                raise NetworkError(
                    f"Anthropic API error: {e.response.status_code} - {e.response.text}"
                )
        except Exception as e:
            raise NetworkError(f"Anthropic API call failed: {str(e)}")


class ZhipuAIClient:
    """ZhipuAI (智谱AI) API 客户端"""

    def __init__(self, api_key: Optional[str] = None, api_base: Optional[str] = None):
        """
        初始化 ZhipuAI 客户端

        Args:
            api_key: API 密钥，默认从环境变量或配置文件读取
            api_base: API 基础 URL，默认从环境变量或配置文件读取
        """
        config = get_config()
        self.api_key = api_key or config.get_api_key("zhipuai")
        self.api_base = api_base or config.get_api_base("zhipuai")

        if not self.api_key:
            raise ValidationError("ZHIPUAI_API_KEY not found in environment or config file")

    @retry(max_attempts=3, delay=2.0)
    def call(
        self,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        调用 ZhipuAI Chat Completion API

        Args:
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            timeout: 超时时间（秒）

        Returns:
            响应数据 (OpenAI 兼容格式)

        Raises:
            NetworkError: API 调用失败
        """
        url = f"{self.api_base}/chat/completions"
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}

        payload = {"model": model, "messages": messages, "temperature": temperature}

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            logger.info(f"Calling ZhipuAI API: model={model}, messages={len(messages)}")
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            data = response.json()
            logger.info(f"ZhipuAI API success: {data.get('usage', {})}")
            return data

        except requests.exceptions.Timeout:
            raise NetworkError(f"ZhipuAI API timeout after {timeout}s")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise ValidationError("Invalid ZhipuAI API key")
            elif e.response.status_code == 429:
                raise NetworkError("ZhipuAI API rate limit exceeded")
            else:
                raise NetworkError(
                    f"ZhipuAI API error: {e.response.status_code} - {e.response.text}"
                )
        except Exception as e:
            raise NetworkError(f"ZhipuAI API call failed: {str(e)}")


class SubagentManager:
    """Subagent 管理器 - 单例模式"""

    _instance = None
    _lock = Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self.openai_client = None
        self.anthropic_client = None
        self.zhipuai_client = None
        self._initialized = True

        logger.info("SubagentManager initialized")

    def get_openai_client(self) -> OpenAIClient:
        """获取 OpenAI 客户端（懒加载）"""
        if self.openai_client is None:
            self.openai_client = OpenAIClient()
        return self.openai_client

    def get_anthropic_client(self) -> AnthropicClient:
        """获取 Anthropic 客户端（懒加载）"""
        if self.anthropic_client is None:
            self.anthropic_client = AnthropicClient()
        return self.anthropic_client

    def get_zhipuai_client(self) -> ZhipuAIClient:
        """获取 ZhipuAI 客户端（懒加载）"""
        if self.zhipuai_client is None:
            self.zhipuai_client = ZhipuAIClient()
        return self.zhipuai_client

    def call_ai(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        temperature: float = 0.7,
        timeout: int = 300,
    ) -> Dict[str, Any]:
        """
        统一的 AI 调用接口

        Args:
            provider: "openai", "anthropic", 或 "zhipuai"
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            timeout: 超时时间

        Returns:
            标准化的响应 {"result", "usage", "cost", "model", "provider"}
        """
        start_time = time.time()

        try:
            # 输入验证
            if not messages or not isinstance(messages, list):
                raise ValidationError("messages must be a non-empty list")

            for msg in messages:
                if "role" not in msg or "content" not in msg:
                    raise ValidationError("Each message must have 'role' and 'content' fields")

            # 验证 max_tokens 上限
            if max_tokens and max_tokens > 32000:
                raise ValidationError("max_tokens cannot exceed 32000")

            # 调用相应的 API
            if provider.lower() == "openai":
                client = self.get_openai_client()
                response = client.call(model, messages, max_tokens, temperature, timeout)
            elif provider.lower() == "anthropic":
                client = self.get_anthropic_client()
                # Anthropic 要求 max_tokens，如果未提供则使用默认值
                if max_tokens is None:
                    max_tokens = 4096
                response = client.call(model, messages, max_tokens, temperature, timeout)
            elif provider.lower() == "zhipuai":
                client = self.get_zhipuai_client()
                response = client.call(model, messages, max_tokens, temperature, timeout)
            else:
                raise ValidationError(
                    f"Unsupported provider: {provider}. Use 'openai', 'anthropic', or 'zhipuai'"
                )

            # 提取结果
            result_text = response["choices"][0]["message"]["content"]
            usage = response["usage"]

            # 计算成本
            cost = CostCalculator.calculate_cost(
                model, usage["prompt_tokens"], usage["completion_tokens"]
            )

            elapsed_time = time.time() - start_time

            return {
                "result": result_text,
                "usage": {
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"],
                },
                "cost": cost,
                "model": model,
                "provider": provider,
                "elapsed_time": round(elapsed_time, 2),
                "status": "success",
            }

        except (ValidationError, NetworkError) as e:
            logger.error(f"AI call failed: {e}")
            return {
                "result": None,
                "error": str(e),
                "status": "failed",
                "elapsed_time": round(time.time() - start_time, 2),
            }


class SubagentOrchestrator:
    """Subagent 并行任务协调器"""

    def __init__(self, manager: SubagentManager):
        self.manager = manager

    def execute_parallel(self, tasks: List[Dict[str, Any]], max_workers: int = 3) -> Dict[str, Any]:
        """
        并行执行多个 AI 任务

        Args:
            tasks: 任务列表，每个任务包含 {provider, model, messages, max_tokens?, temperature?, name?}
            max_workers: 最大并发数

        Returns:
            聚合结果 {"results": [...], "summary": {...}}
        """
        if not tasks:
            raise ValidationError("tasks list cannot be empty")

        if len(tasks) > 10:
            raise ValidationError("Maximum 10 parallel tasks allowed")

        results = []
        total_cost = 0.0
        total_input_tokens = 0
        total_output_tokens = 0
        successful = 0
        failed = 0

        start_time = time.time()

        # 使用线程池并行执行
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_task = {}
            for i, task in enumerate(tasks):
                task_name = task.get("name", f"task_{i + 1}")
                future = executor.submit(
                    self.manager.call_ai,
                    provider=task.get("provider", "openai"),
                    model=task.get("model", "gpt-3.5-turbo"),
                    messages=task["messages"],
                    max_tokens=task.get("max_tokens"),
                    temperature=task.get("temperature", 0.7),
                    timeout=task.get("timeout", 300),
                )
                future_to_task[future] = {"index": i, "name": task_name}

            # 收集结果
            for future in as_completed(future_to_task):
                task_info = future_to_task[future]
                try:
                    result = future.result()
                    result["task_name"] = task_info["name"]
                    result["task_index"] = task_info["index"]
                    results.append(result)

                    # 统计
                    if result["status"] == "success":
                        successful += 1
                        total_cost += result["cost"]["total_cost"]
                        total_input_tokens += result["usage"]["prompt_tokens"]
                        total_output_tokens += result["usage"]["completion_tokens"]
                    else:
                        failed += 1

                except Exception as e:
                    logger.error(f"Task {task_info['name']} failed: {e}")
                    results.append(
                        {
                            "task_name": task_info["name"],
                            "task_index": task_info["index"],
                            "status": "failed",
                            "error": str(e),
                        }
                    )
                    failed += 1

        # 按索引排序
        results.sort(key=lambda x: x["task_index"])

        elapsed_time = time.time() - start_time

        return {
            "results": results,
            "summary": {
                "total_tasks": len(tasks),
                "successful": successful,
                "failed": failed,
                "total_cost": round(total_cost, 6),
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "elapsed_time": round(elapsed_time, 2),
            },
        }


# 全局单例
_manager = None
_manager_lock = Lock()


def get_subagent_manager() -> SubagentManager:
    """获取全局 SubagentManager 实例"""
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = SubagentManager()
    return _manager


def register_tools(mcp: Any) -> None:
    """注册 Subagent 工具到 MCP 服务器"""

    @mcp.tool()
    def subagent_call(
        provider: str, model: str, messages: str, max_tokens: int = None, temperature: float = 0.7
    ) -> str:
        """
        Call an external AI model to handle a subtask.

        Supports OpenAI, Anthropic, and ZhipuAI APIs with custom endpoint configuration.
        Returns response with token usage and cost tracking.

        Args:
            provider: AI provider - "openai", "anthropic", or "zhipuai"
            model: Model name (e.g., "gpt-4", "claude-3-5-sonnet-20241022", "glm-4")
            messages: JSON string of message list [{"role": "user", "content": "..."}]
            max_tokens: Maximum tokens to generate (optional, max 32000)
            temperature: Temperature parameter 0.0-2.0 (default: 0.7)

        Returns:
            JSON string with {result, usage, cost, model, provider, status}

        Example:
            messages = '[{"role": "user", "content": "Explain quantum computing"}]'
            result = subagent_call("openai", "gpt-4", messages)
            result = subagent_call("zhipuai", "glm-4", messages)
        """
        try:
            # 解析 messages JSON
            try:
                messages_list = json.loads(messages)
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"error": f"Invalid JSON in messages parameter: {str(e)}", "status": "failed"}
                )

            manager = get_subagent_manager()
            result = manager.call_ai(
                provider=provider,
                model=model,
                messages=messages_list,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"subagent_call error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @mcp.tool()
    def subagent_parallel(tasks: str, max_workers: int = 3) -> str:
        """
        Execute multiple AI subtasks in parallel with result aggregation.

        Coordinates concurrent calls to different AI models and aggregates results.
        Useful for breaking complex problems into independent subtasks.

        Args:
            tasks: JSON string of task list. Each task: {provider, model, messages, max_tokens?, temperature?, name?}
            max_workers: Maximum concurrent tasks (default: 3, max: 10)

        Returns:
            JSON string with {results: [...], summary: {total_tasks, successful, failed, total_cost, ...}}

        Example:
            tasks = '[
                {"name": "task1", "provider": "openai", "model": "gpt-3.5-turbo",
                 "messages": [{"role": "user", "content": "Summarize AI"}]},
                {"name": "task2", "provider": "anthropic", "model": "claude-3-haiku-20240307",
                 "messages": [{"role": "user", "content": "List AI applications"}]}
            ]'
            result = subagent_parallel(tasks)
        """
        try:
            # 解析 tasks JSON
            try:
                tasks_list = json.loads(tasks)
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"error": f"Invalid JSON in tasks parameter: {str(e)}", "status": "failed"}
                )

            if not isinstance(tasks_list, list):
                return json.dumps({"error": "tasks must be a JSON array", "status": "failed"})

            manager = get_subagent_manager()
            orchestrator = SubagentOrchestrator(manager)

            result = orchestrator.execute_parallel(tasks_list, max_workers)

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"subagent_parallel error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @mcp.tool()
    def subagent_conditional(condition_task: str, true_task: str, false_task: str) -> str:
        """
        Execute conditional branching based on AI decision.

        First calls AI to evaluate a condition, then executes either true_task or false_task
        based on the decision. Useful for dynamic workflow control.

        Args:
            condition_task: JSON string of task to evaluate condition {provider, model, messages}
                           AI should return "true" or "false" in response
            true_task: JSON string of task to execute if condition is true
            false_task: JSON string of task to execute if condition is false

        Returns:
            JSON string with {condition_result, branch_taken, final_result, total_usage, total_cost}

        Example:
            condition_task = '{"provider": "openai", "model": "gpt-3.5-turbo",
                              "messages": [{"role": "user", "content": "Is 5 > 3? Reply only true or false"}]}'
            true_task = '{"provider": "openai", "model": "gpt-3.5-turbo",
                         "messages": [{"role": "user", "content": "Explain why 5 > 3"}]}'
            false_task = '{"provider": "openai", "model": "gpt-3.5-turbo",
                          "messages": [{"role": "user", "content": "Explain why 5 ≤ 3"}]}'
            result = subagent_conditional(condition_task, true_task, false_task)
        """
        try:
            # 解析所有任务
            try:
                cond_task = json.loads(condition_task)
                t_task = json.loads(true_task)
                f_task = json.loads(false_task)
            except json.JSONDecodeError as e:
                return json.dumps(
                    {"error": f"Invalid JSON in task parameters: {str(e)}", "status": "failed"}
                )

            manager = get_subagent_manager()

            # 执行条件判断
            logger.info("Executing condition task")
            condition_result = manager.call_ai(
                provider=cond_task.get("provider", "openai"),
                model=cond_task.get("model", "gpt-3.5-turbo"),
                messages=cond_task["messages"],
                max_tokens=cond_task.get("max_tokens", 100),
                temperature=cond_task.get("temperature", 0.1),
            )

            if condition_result["status"] != "success":
                return json.dumps(
                    {
                        "error": "Condition evaluation failed",
                        "condition_result": condition_result,
                        "status": "failed",
                    }
                )

            # 判断条件结果
            condition_text = condition_result["result"].strip().lower()
            is_true = "true" in condition_text or "yes" in condition_text or "是" in condition_text

            # 选择执行的任务
            branch_taken = "true_branch" if is_true else "false_branch"
            next_task = t_task if is_true else f_task

            logger.info(f"Condition evaluated to: {is_true}, executing {branch_taken}")

            # 执行选中的分支
            branch_result = manager.call_ai(
                provider=next_task.get("provider", "openai"),
                model=next_task.get("model", "gpt-3.5-turbo"),
                messages=next_task["messages"],
                max_tokens=next_task.get("max_tokens"),
                temperature=next_task.get("temperature", 0.7),
            )

            # 聚合结果
            total_cost = 0.0
            total_input_tokens = 0
            total_output_tokens = 0

            if condition_result["status"] == "success":
                total_cost += condition_result["cost"]["total_cost"]
                total_input_tokens += condition_result["usage"]["prompt_tokens"]
                total_output_tokens += condition_result["usage"]["completion_tokens"]

            if branch_result["status"] == "success":
                total_cost += branch_result["cost"]["total_cost"]
                total_input_tokens += branch_result["usage"]["prompt_tokens"]
                total_output_tokens += branch_result["usage"]["completion_tokens"]

            return json.dumps(
                {
                    "condition_result": {
                        "text": condition_result["result"],
                        "evaluated_as": is_true,
                        "usage": condition_result.get("usage"),
                        "cost": condition_result.get("cost"),
                    },
                    "branch_taken": branch_taken,
                    "final_result": branch_result,
                    "total_usage": {
                        "prompt_tokens": total_input_tokens,
                        "completion_tokens": total_output_tokens,
                        "total_tokens": total_input_tokens + total_output_tokens,
                    },
                    "total_cost": round(total_cost, 6),
                    "status": "success",
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"subagent_conditional error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @mcp.tool()
    def subagent_config_set(provider: str, api_key: str, api_base: Optional[str] = None) -> str:
        """
        设置 Subagent 提供商的 API 配置（持久化保存）

        此工具将 API 密钥和基础 URL 保存到配置文件中，下次启动时自动加载。
        配置文件位置：~/.subagent_config.json

        Args:
            provider: 提供商名称，支持: "openai", "anthropic", "zhipuai"
            api_key: API 密钥
            api_base: API 基础 URL（可选）

        Returns:
            JSON 格式的配置设置结果

        Example:
            # 设置 OpenAI API
            subagent_config_set("openai", "sk-xxxxxxxxxxxx")

            # 设置自定义端点
            subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")

            # 设置 ZhipuAI
            subagent_config_set("zhipuai", "your-api-key.xxxxxxxxx")
        """
        try:
            config = get_config()

            # 验证 provider
            valid_providers = ["openai", "anthropic", "zhipuai"]
            if provider.lower() not in valid_providers:
                return json.dumps(
                    {
                        "error": f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
                        "status": "failed",
                    }
                )

            # 保存 API 密钥
            config.set_api_key(provider, api_key)

            # 如果提供了 API 基础 URL，也保存它
            if api_base:
                config.set_api_base(provider, api_base)

            # 构建响应
            result = {
                "provider": provider,
                "api_key_set": True,
                "api_key_preview": (
                    api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"
                ),
                "config_file": config.get_config_path(),
                "status": "success",
            }

            if api_base:
                result["api_base"] = api_base

            logger.info(
                f"Configured {provider}: key={result['api_key_preview']}, base={api_base or 'default'}"
            )

            return json.dumps(result, ensure_ascii=False, indent=2)

        except Exception as e:
            logger.error(f"subagent_config_set error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @mcp.tool()
    def subagent_config_get(provider: str) -> str:
        """
        获取指定提供商的 API 配置信息

        Args:
            provider: 提供商名称，支持: "openai", "anthropic", "zhipuai"

        Returns:
            JSON 格式的配置信息（密钥已脱敏）

        Example:
            config = subagent_config_get("openai")
        """
        try:
            config = get_config()

            # 验证 provider
            valid_providers = ["openai", "anthropic", "zhipuai"]
            if provider.lower() not in valid_providers:
                return json.dumps(
                    {
                        "error": f"Invalid provider. Must be one of: {', '.join(valid_providers)}",
                        "status": "failed",
                    }
                )

            api_key = config.get_api_key(provider)
            api_base = config.get_api_base(provider)

            if not api_key:
                return json.dumps(
                    {
                        "provider": provider,
                        "configured": False,
                        "message": f"No API key found for {provider}",
                        "status": "not_found",
                    }
                )

            # 脱敏显示密钥
            masked_key = api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"

            # 检测密钥来源
            env_var = f"{provider.upper()}_API_KEY"
            source = "environment" if os.getenv(env_var) else "config_file"

            return json.dumps(
                {
                    "provider": provider,
                    "configured": True,
                    "api_key": masked_key,
                    "api_base": api_base,
                    "source": source,
                    "config_file": config.get_config_path(),
                    "status": "success",
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"subagent_config_get error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    @mcp.tool()
    def subagent_config_list() -> str:
        """
        列出所有已配置的 AI 提供商

        返回所有配置的提供商及其状态，包括密钥预览和配置来源。

        Returns:
            JSON 格式的提供商列表

        Example:
            providers = subagent_config_list()
        """
        try:
            config = get_config()
            providers_info = config.list_providers()

            if not providers_info:
                return json.dumps(
                    {
                        "providers": [],
                        "message": "No providers configured",
                        "config_file": config.get_config_path(),
                        "hint": "Use subagent_config_set to configure API keys",
                        "status": "success",
                    }
                )

            return json.dumps(
                {
                    "providers": providers_info,
                    "total_configured": len(providers_info),
                    "config_file": config.get_config_path(),
                    "status": "success",
                },
                ensure_ascii=False,
                indent=2,
            )

        except Exception as e:
            logger.error(f"subagent_config_list error: {e}")
            return json.dumps({"error": str(e), "status": "failed"})

    logger.info("Subagent tools registered successfully")
