#!/usr/bin/env python3
"""Test Subagent AI orchestration tools"""

import json
import os
import sys
from collections.abc import Callable
from pathlib import Path
from typing import Any
from unittest.mock import Mock, patch

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from mcp_server.tools import subagent
from mcp_server.tools.subagent import (
    AnthropicClient,
    OpenAIClient,
    SubagentManager,
    SubagentOrchestrator,
    get_subagent_manager,
)


class MockMCP:
    """Mock MCP server for testing"""

    def __init__(self) -> None:
        self.tools: dict[str, Callable[..., Any]] = {}

    def tool(self) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
        def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
            self.tools[func.__name__] = func
            return func

        return decorator


def test_openai_client_mock() -> None:
    """测试 OpenAI 客户端 (Mock)"""
    print("\n3. Testing OpenAIClient (Mock):")

    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "Hello! How can I help you?"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
    }
    mock_response.raise_for_status = Mock()

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            client = OpenAIClient()
            messages = [{"role": "user", "content": "Hello"}]
            result = client.call("gpt-3.5-turbo", messages)

            print("   Model: gpt-3.5-turbo")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            print(f"   Usage: {result['usage']}")

            assert "choices" in result
            assert result["usage"]["total_tokens"] == 18

    print("   [OK] OpenAIClient mock tests passed")


def test_anthropic_client_mock() -> None:
    """测试 Anthropic 客户端 (Mock)"""
    print("\n4. Testing AnthropicClient (Mock):")

    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "content": [{"text": "Hello! I'm Claude. How can I help?"}],
        "usage": {"input_tokens": 12, "output_tokens": 9},
        "stop_reason": "end_turn",
    }
    mock_response.raise_for_status = Mock()

    with patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            client = AnthropicClient()
            messages = [{"role": "user", "content": "Hello"}]
            result = client.call("claude-3-haiku-20240307", messages)

            print("   Model: claude-3-haiku-20240307")
            print(f"   Response: {result['choices'][0]['message']['content']}")
            print(f"   Usage: {result['usage']}")

            assert "choices" in result
            assert result["usage"]["total_tokens"] == 21

    print("   [OK] AnthropicClient mock tests passed")


def test_subagent_manager() -> None:
    """测试 SubagentManager"""
    print("\n5. Testing SubagentManager:")

    # 测试单例模式
    manager1 = SubagentManager()
    manager2 = SubagentManager()
    assert manager1 is manager2
    print("   Singleton pattern works")

    # 测试全局获取
    manager3 = get_subagent_manager()
    assert manager1 is manager3
    print("   Global getter works")

    print("   [OK] SubagentManager tests passed")


def test_subagent_manager_call_ai_mock() -> None:
    """测试 SubagentManager.call_ai (Mock)"""
    print("\n6. Testing SubagentManager.call_ai (Mock):")

    # Mock OpenAI 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {
                    "role": "assistant",
                    "content": "The capital of France is Paris.",
                },
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23},
    }
    mock_response.raise_for_status = Mock()

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            manager = SubagentManager()
            messages = [{"role": "user", "content": "What is the capital of France?"}]

            result = manager.call_ai(
                provider="openai", model="gpt-3.5-turbo", messages=messages, max_tokens=100
            )

            print(f"   Provider: {result['provider']}")
            print(f"   Model: {result['model']}")
            print(f"   Result: {result['result']}")
            print(f"   Usage: {result['usage']}")
            print(f"   Status: {result['status']}")

            assert result["status"] == "success"
            assert result["usage"]["total_tokens"] == 23

    print("   [OK] SubagentManager.call_ai mock tests passed")


def test_subagent_orchestrator_mock() -> None:
    """测试 SubagentOrchestrator (Mock)"""
    print("\n7. Testing SubagentOrchestrator (Mock):")

    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"role": "assistant", "content": "Task completed"}, "finish_reason": "stop"}
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_response.raise_for_status = Mock()

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            manager = SubagentManager()
            orchestrator = SubagentOrchestrator(manager)

            tasks = [
                {
                    "name": "task1",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Task 1"}],
                },
                {
                    "name": "task2",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Task 2"}],
                },
            ]

            result = orchestrator.execute_parallel(tasks, max_workers=2)

            print(f"   Total tasks: {result['summary']['total_tasks']}")
            print(f"   Successful: {result['summary']['successful']}")
            print(f"   Failed: {result['summary']['failed']}")
            print(f"   Total tokens: {result['summary']['total_tokens']}")

            assert result["summary"]["total_tasks"] == 2
            assert len(result["results"]) == 2

    print("   [OK] SubagentOrchestrator mock tests passed")


def test_subagent_tools_registration() -> None:
    """测试工具注册"""
    print("\n8. Testing tool registration:")

    mcp = MockMCP()
    subagent.register_tools(mcp)

    print(f"   Registered tools: {list(mcp.tools.keys())}")

    assert "subagent_call" in mcp.tools
    assert "subagent_parallel" in mcp.tools
    assert "subagent_conditional" in mcp.tools

    print("   [OK] Tool registration tests passed")


def test_subagent_call_tool_mock() -> None:
    """测试 subagent_call 工具 (Mock)"""
    print("\n9. Testing subagent_call tool (Mock):")

    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {"message": {"role": "assistant", "content": "AI response"}, "finish_reason": "stop"}
        ],
        "usage": {"prompt_tokens": 20, "completion_tokens": 10, "total_tokens": 30},
    }
    mock_response.raise_for_status = Mock()

    mcp = MockMCP()
    subagent.register_tools(mcp)

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            messages_json = json.dumps([{"role": "user", "content": "Test message"}])

            result_str = mcp.tools["subagent_call"](
                provider="openai",
                model="gpt-3.5-turbo",
                messages=messages_json,
                max_tokens=100,
                temperature=0.7,
            )

            result = json.loads(result_str)
            print(f"   Status: {result['status']}")
            print(f"   Result: {result['result']}")
            print(f"   Usage: {result['usage']}")

            assert result["status"] == "success"
            assert "result" in result
            assert "usage" in result

    print("   [OK] subagent_call tool mock tests passed")


def test_subagent_parallel_tool_mock() -> None:
    """测试 subagent_parallel 工具 (Mock)"""
    print("\n10. Testing subagent_parallel tool (Mock):")

    # Mock 响应
    mock_response = Mock()
    mock_response.json.return_value = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "Parallel task done"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_response.raise_for_status = Mock()

    mcp = MockMCP()
    subagent.register_tools(mcp)

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post", return_value=mock_response):
            tasks = [
                {
                    "name": "task1",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Task 1"}],
                },
                {
                    "name": "task2",
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Task 2"}],
                },
            ]

            tasks_json = json.dumps(tasks)
            result_str = mcp.tools["subagent_parallel"](tasks=tasks_json, max_workers=2)

            result = json.loads(result_str)
            print(f"   Total tasks: {result['summary']['total_tasks']}")
            print(f"   Successful: {result['summary']['successful']}")

            assert result["summary"]["total_tasks"] == 2
            assert len(result["results"]) == 2

    print("   [OK] subagent_parallel tool mock tests passed")


def test_subagent_conditional_tool_mock() -> None:
    """测试 subagent_conditional 工具 (Mock)"""
    print("\n11. Testing subagent_conditional tool (Mock):")

    # Mock 响应 - 条件返回 true
    mock_response_condition = Mock()
    mock_response_condition.json.return_value = {
        "choices": [{"message": {"role": "assistant", "content": "true"}, "finish_reason": "stop"}],
        "usage": {"prompt_tokens": 5, "completion_tokens": 2, "total_tokens": 7},
    }
    mock_response_condition.raise_for_status = Mock()

    # Mock 响应 - 分支执行
    mock_response_branch = Mock()
    mock_response_branch.json.return_value = {
        "choices": [
            {
                "message": {"role": "assistant", "content": "True branch executed"},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 5, "total_tokens": 15},
    }
    mock_response_branch.raise_for_status = Mock()

    mcp = MockMCP()
    subagent.register_tools(mcp)

    with patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"}):
        with patch("requests.post") as mock_post:
            # 设置两次调用的返回值
            mock_post.side_effect = [mock_response_condition, mock_response_branch]

            condition_task = json.dumps(
                {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Is 5 > 3? Reply true or false"}],
                }
            )

            true_task = json.dumps(
                {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Explain why 5 > 3"}],
                }
            )

            false_task = json.dumps(
                {
                    "provider": "openai",
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": "Explain why 5 <= 3"}],
                }
            )

            result_str = mcp.tools["subagent_conditional"](
                condition_task=condition_task, true_task=true_task, false_task=false_task
            )

            result = json.loads(result_str)
            print(f"   Condition evaluated as: {result['condition_result']['evaluated_as']}")
            print(f"   Branch taken: {result['branch_taken']}")
            print(f"   Final result: {result['final_result']['result']}")
            print(f"   Total usage: {result['total_usage']}")

            assert result["status"] == "success"
            assert result["branch_taken"] == "true_branch"
            assert "total_usage" in result

    print("   [OK] subagent_conditional tool mock tests passed")


def test_error_handling() -> None:
    """测试错误处理"""
    print("\n12. Testing error handling:")

    # 测试无效的 API 密钥
    with patch.dict(os.environ, {}, clear=True):
        try:
            OpenAIClient()  # Should raise ValidationError
            raise AssertionError("Should raise ValidationError")
        except Exception as e:
            print(f"   Missing API key error: {type(e).__name__}")
            assert "OPENAI_API_KEY" in str(e)

    # 测试无效的消息格式
    mcp = MockMCP()
    subagent.register_tools(mcp)

    result_str = mcp.tools["subagent_call"](
        provider="openai", model="gpt-3.5-turbo", messages="invalid json", max_tokens=100
    )

    result = json.loads(result_str)
    print(f"   Invalid JSON error: {result['status']}")
    assert result["status"] == "failed"
    assert "error" in result

    # 测试空任务列表
    result_str = mcp.tools["subagent_parallel"](tasks="[]", max_workers=3)
    result = json.loads(result_str)
    print(f"   Empty tasks error: {result['status']}")
    assert result["status"] == "failed"

    print("   [OK] Error handling tests passed")


def run_all_tests() -> None:
    """运行所有测试"""
    print("=" * 60)
    print("Testing Subagent AI Orchestration Tools")
    print("=" * 60)

    test_openai_client_mock()
    test_anthropic_client_mock()
    test_subagent_manager()
    test_subagent_manager_call_ai_mock()
    test_subagent_orchestrator_mock()
    test_subagent_tools_registration()
    test_subagent_call_tool_mock()
    test_subagent_parallel_tool_mock()
    test_subagent_conditional_tool_mock()
    test_error_handling()

    print("\n" + "=" * 60)
    print("[OK] All Subagent tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
