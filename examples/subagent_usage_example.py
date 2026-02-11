#!/usr/bin/env python3
"""
Subagent AI Orchestration - Usage Examples

This file demonstrates how to use the subagent tools for AI task delegation.

Requirements:
- Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables
- MCP server running with subagent tools registered
"""

import json
import os


def example_single_call():
    """Example 1: Simple single AI call"""
    print("\n" + "=" * 60)
    print("Example 1: Single AI Call")
    print("=" * 60)

    # Prepare messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "Explain quantum computing in 2 sentences."},
    ]

    # In your MCP client (Claude Desktop, etc.), you would call:
    print("\nMCP Tool Call:")
    print("""
    subagent_call(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=json.dumps([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain quantum computing in 2 sentences."}
        ]),
        max_tokens=200,
        temperature=0.7
    )
    """)

    print("\nExpected Response Structure:")
    print(
        json.dumps(
            {
                "result": "Quantum computing uses quantum bits...",
                "usage": {"prompt_tokens": 25, "completion_tokens": 45, "total_tokens": 70},
                "cost": {"input_cost": 0.0000375, "output_cost": 0.00009, "total_cost": 0.0001275},
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "elapsed_time": 1.23,
                "status": "success",
            },
            indent=2,
        )
    )


def example_parallel_tasks():
    """Example 2: Parallel task execution"""
    print("\n" + "=" * 60)
    print("Example 2: Parallel Tasks - Document Analysis")
    print("=" * 60)

    document_text = """
    Artificial Intelligence is transforming industries worldwide.
    Machine learning algorithms enable computers to learn from data.
    Deep learning, a subset of ML, uses neural networks with multiple layers.
    """

    tasks = [
        {
            "name": "extract_entities",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": f"Extract key terms from: {document_text}"}],
            "max_tokens": 200,
        },
        {
            "name": "summarize",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "messages": [
                {"role": "user", "content": f"Summarize in one sentence: {document_text}"}
            ],
            "max_tokens": 100,
        },
        {
            "name": "sentiment",
            "provider": "openai",
            "model": "gpt-3.5-turbo",
            "messages": [
                {
                    "role": "user",
                    "content": f"Analyze sentiment (positive/neutral/negative): {document_text}",
                }
            ],
            "max_tokens": 50,
        },
    ]

    print("\nMCP Tool Call:")
    print(f"""
    subagent_parallel(
        tasks=json.dumps({json.dumps(tasks, indent=8)}),
        max_workers=3
    )
    """)

    print("\nExpected Response Structure:")
    print(
        json.dumps(
            {
                "results": [
                    {
                        "task_name": "extract_entities",
                        "task_index": 0,
                        "result": "AI, Machine Learning, Deep Learning...",
                        "usage": {"prompt_tokens": 50, "completion_tokens": 30, "total_tokens": 80},
                        "cost": {"total_cost": 0.000195},
                        "status": "success",
                    },
                    {
                        "task_name": "summarize",
                        "task_index": 1,
                        "result": "AI and ML are transforming industries...",
                        "usage": {"prompt_tokens": 45, "completion_tokens": 20, "total_tokens": 65},
                        "cost": {"total_cost": 0.0001475},
                        "status": "success",
                    },
                    {
                        "task_name": "sentiment",
                        "task_index": 2,
                        "result": "Positive",
                        "usage": {"prompt_tokens": 40, "completion_tokens": 5, "total_tokens": 45},
                        "cost": {"total_cost": 0.00007},
                        "status": "success",
                    },
                ],
                "summary": {
                    "total_tasks": 3,
                    "successful": 3,
                    "failed": 0,
                    "total_cost": 0.0004125,
                    "total_tokens": 190,
                    "elapsed_time": 2.5,
                },
            },
            indent=2,
        )
    )


def example_conditional_branching():
    """Example 3: Conditional branching based on AI decision"""
    print("\n" + "=" * 60)
    print("Example 3: Conditional Branching - Smart Routing")
    print("=" * 60)

    user_message = "What is the capital of France?"

    # Condition: Is this a complex question?
    condition_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"Is this question complex requiring deep reasoning? '{user_message}'. Reply only 'true' or 'false'",
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1,
    }

    # If complex, use GPT-4
    complex_task = {
        "provider": "openai",
        "model": "gpt-4",
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 1000,
    }

    # If simple, use GPT-3.5
    simple_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": user_message}],
        "max_tokens": 200,
    }

    print("\nMCP Tool Call:")
    print(f"""
    subagent_conditional(
        condition_task=json.dumps({json.dumps(condition_task, indent=8)}),
        true_task=json.dumps({json.dumps(complex_task, indent=8)}),
        false_task=json.dumps({json.dumps(simple_task, indent=8)})
    )
    """)

    print("\nExpected Response Structure:")
    print(
        json.dumps(
            {
                "condition_result": {
                    "text": "false",
                    "evaluated_as": False,
                    "usage": {"prompt_tokens": 30, "completion_tokens": 2, "total_tokens": 32},
                    "cost": {"total_cost": 0.000049},
                },
                "branch_taken": "false_branch",
                "final_result": {
                    "result": "The capital of France is Paris.",
                    "usage": {"prompt_tokens": 15, "completion_tokens": 8, "total_tokens": 23},
                    "cost": {"total_cost": 0.0000385},
                    "status": "success",
                },
                "total_usage": {"prompt_tokens": 45, "completion_tokens": 10, "total_tokens": 55},
                "total_cost": 0.0000875,
                "status": "success",
            },
            indent=2,
        )
    )


def example_cost_comparison():
    """Example 4: Model cost comparison"""
    print("\n" + "=" * 60)
    print("Example 4: Cost Comparison Across Models")
    print("=" * 60)

    prompt = "Explain machine learning in 3 sentences."
    estimated_tokens = {"input": 50, "output": 100}

    print("\nCost Estimates for 50 input + 100 output tokens:")
    print("-" * 60)

    models = [
        ("gpt-3.5-turbo", "openai", 0.0015, 0.002),
        ("gpt-4", "openai", 0.03, 0.06),
        ("gpt-4o-mini", "openai", 0.00015, 0.0006),
        ("claude-3-haiku-20240307", "anthropic", 0.00025, 0.00125),
        ("claude-3-5-sonnet-20241022", "anthropic", 0.003, 0.015),
    ]

    for model, provider, input_price, output_price in models:
        input_cost = (estimated_tokens["input"] / 1000) * input_price
        output_cost = (estimated_tokens["output"] / 1000) * output_price
        total_cost = input_cost + output_cost

        print(f"{model:30} ({provider:10}): ${total_cost:.6f}")

    print("\nRecommendation:")
    print("- For simple tasks: Use gpt-3.5-turbo or claude-3-haiku")
    print("- For complex reasoning: Use gpt-4 or claude-3-5-sonnet")
    print("- For budget constraints: Use gpt-4o-mini")


def example_multi_turn_conversation():
    """Example 5: Multi-turn conversation simulation"""
    print("\n" + "=" * 60)
    print("Example 5: Multi-Turn Conversation")
    print("=" * 60)

    print("\nTurn 1: User asks a question")
    messages_turn1 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
    ]

    print("\nMCP Tool Call (Turn 1):")
    print(f"""
    result1 = subagent_call(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=json.dumps({json.dumps(messages_turn1, indent=8)})
    )
    """)

    print("\nTurn 2: Follow-up question")
    # In practice, you would extract result1['result'] and add it to conversation
    messages_turn2 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": "Python is a high-level programming language..."},
        {"role": "user", "content": "What are its main uses?"},
    ]

    print("\nMCP Tool Call (Turn 2):")
    print(f"""
    result2 = subagent_call(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=json.dumps({json.dumps(messages_turn2, indent=8)})
    )
    """)

    print("\nNote: Subagent is stateless. You must maintain conversation history")
    print("      and pass it with each call.")


def example_error_handling():
    """Example 6: Error handling"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    print("\nCommon Errors and Solutions:")
    print("-" * 60)

    errors = [
        {
            "error": "OPENAI_API_KEY environment variable not set",
            "solution": "Set your API key: export OPENAI_API_KEY='sk-...'",
        },
        {
            "error": "Invalid OpenAI API key",
            "solution": "Check your API key is correct and not expired",
        },
        {
            "error": "API rate limit exceeded",
            "solution": "Reduce max_workers or add delays between calls",
        },
        {
            "error": "max_tokens cannot exceed 32000",
            "solution": "Reduce max_tokens parameter or split task",
        },
        {
            "error": "tasks list cannot be empty",
            "solution": "Provide at least one task in the tasks array",
        },
    ]

    for error_info in errors:
        print(f"\nError: {error_info['error']}")
        print(f"Solution: {error_info['solution']}")

    print("\n\nChecking Response Status:")
    print("""
    result = subagent_call(...)
    result_data = json.loads(result)
    
    if result_data['status'] == 'success':
        print(f"Result: {result_data['result']}")
        print(f"Cost: ${result_data['cost']['total_cost']}")
    else:
        print(f"Error: {result_data.get('error', 'Unknown error')}")
    """)


def main():
    """Run all examples"""
    print("=" * 60)
    print("SUBAGENT AI ORCHESTRATION - USAGE EXAMPLES")
    print("=" * 60)

    print("\nNote: These are demonstration examples showing the MCP tool call syntax.")
    print("      To run actual AI calls, you need:")
    print("      1. Valid API keys set in environment variables")
    print("      2. MCP server running")
    print("      3. MCP client (Claude Desktop, etc.) to invoke the tools")

    example_single_call()
    example_parallel_tasks()
    example_conditional_branching()
    example_cost_comparison()
    example_multi_turn_conversation()
    example_error_handling()

    print("\n" + "=" * 60)
    print("For more information, see docs/SUBAGENT_GUIDE.md")
    print("=" * 60)


if __name__ == "__main__":
    main()
