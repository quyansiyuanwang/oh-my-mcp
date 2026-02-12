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
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
from typing import Any, Dict, List, Optional

import requests

from mcp_server.tools.registry import tool_handler
from mcp_server.tools.subagent_config import get_config
from mcp_server.utils import NetworkError, ValidationError, logger, retry

# 工具类别信息
CATEGORY_NAME = "Subagent AI Orchestration"
CATEGORY_DESCRIPTION = (
    "Delegate subtasks to external AI models with parallel execution and custom model support"
)
TOOLS = [
    "subagent_call",
    "subagent_parallel",
    "subagent_conditional",
    "subagent_config_set",
    "subagent_config_get",
    "subagent_config_list",
]


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

        payload: Dict[str, Any] = {"model": model, "messages": messages, "temperature": temperature}

        if max_tokens:
            payload["max_tokens"] = max_tokens

        try:
            logger.info(f"Calling OpenAI API: model={model}, messages={len(messages)}")
            response = requests.post(url, headers=headers, json=payload, timeout=timeout)
            response.raise_for_status()

            data: Dict[str, Any] = response.json()
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
        headers: dict[str, Any] = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }

        # 转换消息格式: 提取 system 消息
        system_message: Optional[str] = None
        user_messages: list[dict[str, str]] = []

        for msg in messages:
            if msg["role"] == "system":
                system_message = msg["content"]
            else:
                user_messages.append(msg)

        payload: dict[str, Any] = {
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
            converted: dict[str, Any] = {
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


class SubagentManager:
    """子代理管理器 - 单例模式"""

    _instance: Optional["SubagentManager"] = None
    _lock = Lock()
    _initialized: bool = False

    def __new__(cls) -> "SubagentManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self.openai_client: Optional[OpenAIClient] = None
        self.anthropic_client: Optional[AnthropicClient] = None
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
            provider: "openai" 或 "anthropic"
            model: 模型名称
            messages: 消息列表
            max_tokens: 最大生成 token 数
            temperature: 温度参数
            timeout: 超时时间

        Returns:
            标准化的响应 {"result", "usage", "model", "provider"}
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
                openai_client = self.get_openai_client()
                response = openai_client.call(model, messages, max_tokens, temperature, timeout)
            elif provider.lower() == "anthropic":
                anthropic_client = self.get_anthropic_client()
                # Anthropic 要求 max_tokens，如果未提供则使用默认值
                if max_tokens is None:
                    max_tokens = 4096
                response = anthropic_client.call(model, messages, max_tokens, temperature, timeout)
            else:
                raise ValidationError(
                    f"Unsupported provider: {provider}. Use 'openai' or 'anthropic'"
                )

            # 提取结果
            result_text = response["choices"][0]["message"]["content"]
            usage = response["usage"]

            elapsed_time = time.time() - start_time

            return {
                "result": result_text,
                "usage": {
                    "prompt_tokens": usage["prompt_tokens"],
                    "completion_tokens": usage["completion_tokens"],
                    "total_tokens": usage["total_tokens"],
                },
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
                "total_input_tokens": total_input_tokens,
                "total_output_tokens": total_output_tokens,
                "total_tokens": total_input_tokens + total_output_tokens,
                "elapsed_time": round(elapsed_time, 2),
            },
        }


# 全局单例
_manager: Optional[SubagentManager] = None
_manager_lock = Lock()


def get_subagent_manager() -> SubagentManager:
    """获取全局 SubagentManager 实例"""
    global _manager
    if _manager is None:
        with _manager_lock:
            if _manager is None:
                _manager = SubagentManager()
    return _manager


@tool_handler
def subagent_call(
    provider: str,
    model: str,
    messages: str,
    max_tokens: Optional[int] = None,
    temperature: float = 0.7,
) -> str:
    """
    Call an external AI model to handle a subtask.

    Supports OpenAI and Anthropic APIs with custom endpoint configuration.
    Returns response with token usage statistics.

    Args:
        provider: AI provider - "openai" or "anthropic"
        model: Model name (e.g., "gpt-4", "claude-3-5-sonnet-20241022", or any custom model)
        messages: JSON string of message list [{"role": "user", "content": "..."}]
        max_tokens: Maximum tokens to generate (optional, max 32000)
        temperature: Temperature parameter 0.0-2.0 (default: 0.7)

    Returns:
        JSON string with {result, usage, model, provider, status}

    Example:
        messages = '[{"role": "user", "content": "Explain quantum computing"}]'
        result = subagent_call("openai", "gpt-4", messages)
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


@tool_handler
def subagent_parallel(tasks: str, max_workers: int = 3) -> str:
    """
    Execute multiple AI subtasks in parallel with result aggregation.

    Coordinates concurrent calls to different AI models and aggregates results.
    Useful for breaking complex problems into independent subtasks.

    Args:
        tasks: JSON string of task list. Each task: {provider, model, messages, max_tokens?, temperature?, name?}
        max_workers: Maximum concurrent tasks (default: 3, max: 10)

    Returns:
        JSON string with {results: [...], summary: {total_tasks, successful, failed, total_tokens, ...}}

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


@tool_handler
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
        JSON string with {condition_result, branch_taken, final_result, total_usage}

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
        total_input_tokens = 0
        total_output_tokens = 0

        if condition_result["status"] == "success":
            total_input_tokens += condition_result["usage"]["prompt_tokens"]
            total_output_tokens += condition_result["usage"]["completion_tokens"]

        if branch_result["status"] == "success":
            total_input_tokens += branch_result["usage"]["prompt_tokens"]
            total_output_tokens += branch_result["usage"]["completion_tokens"]

        return json.dumps(
            {
                "condition_result": {
                    "text": condition_result["result"],
                    "evaluated_as": is_true,
                    "usage": condition_result.get("usage"),
                },
                "branch_taken": branch_taken,
                "final_result": branch_result,
                "total_usage": {
                    "prompt_tokens": total_input_tokens,
                    "completion_tokens": total_output_tokens,
                    "total_tokens": total_input_tokens + total_output_tokens,
                },
                "status": "success",
            },
            ensure_ascii=False,
            indent=2,
        )

    except Exception as e:
        logger.error(f"subagent_conditional error: {e}")
        return json.dumps({"error": str(e), "status": "failed"})


@tool_handler
def subagent_config_set(provider: str, api_key: str, api_base: Optional[str] = None) -> str:
    """
    设置 Subagent 提供商的 API 配置（持久化保存）

    此工具将 API 密钥和基础 URL 保存到配置文件中，下次启动时自动加载。
    配置文件位置：~/.subagent_config.json

    Args:
        provider: 提供商名称，支持: "openai", "anthropic"
        api_key: API 密钥
        api_base: API 基础 URL（可选）

    Returns:
        JSON 格式的配置设置结果

    Example:
        # 设置 OpenAI API
        subagent_config_set("openai", "sk-xxxxxxxxxxxx")

        # 设置自定义端点
        subagent_config_set("openai", "sk-xxx", "https://api.openai-proxy.com/v1")
    """
    try:
        config = get_config()

        # 验证 provider
        valid_providers = ["openai", "anthropic"]
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
            "api_key_preview": (api_key[:8] + "..." + api_key[-4:] if len(api_key) > 12 else "***"),
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


@tool_handler
def subagent_config_get(provider: str) -> str:
    """
    获取指定提供商的 API 配置信息

    Args:
        provider: 提供商名称，支持: "openai", "anthropic"

    Returns:
        JSON 格式的配置信息（密钥已脱敏）

    Example:
        config = subagent_config_get("openai")
    """
    try:
        config = get_config()

        # 验证 provider
        valid_providers = ["openai", "anthropic"]
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


@tool_handler
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
