#!/usr/bin/env python3
"""
Subagent AI Orchestration - Usage Examples (Updated v0.2.0)

This file demonstrates how to use the subagent tools for AI task delegation.

Changes in v0.2.0:
- Removed cost tracking (no more 'cost' field in返回值)
- Added custom model support (use any model name)
- Token usage statistics still available via 'usage' field

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
                "model": "gpt-3.5-turbo",
                "provider": "openai",
                "elapsed_time": 1.23,
                "status": "success",
            },
            indent=2,
        )
    )

    print("\n💡 Note: Token usage statistics help you monitor API consumption")
    print("   Check actual costs at: https://platform.openai.com/usage")


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
        tasks=json.dumps({json.dumps(tasks, indent=8)})
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
                        "result": "Key terms: AI, ML, neural networks",
                        "usage": {"prompt_tokens": 30, "completion_tokens": 40, "total_tokens": 70},
                        "status": "success",
                    },
                    {
                        "task_name": "summarize",
                        "task_index": 1,
                        "result": "AI and ML are transforming industries...",
                        "usage": {"prompt_tokens": 25, "completion_tokens": 35, "total_tokens": 60},
                        "status": "success",
                    },
                    {
                        "task_name": "sentiment",
                        "task_index": 2,
                        "result": "positive",
                        "usage": {"prompt_tokens": 20, "completion_tokens": 5, "total_tokens": 25},
                        "status": "success",
                    },
                ],
                "summary": {
                    "total_tasks": 3,
                    "successful": 3,
                    "failed": 0,
                    "total_input_tokens": 75,
                    "total_output_tokens": 80,
                    "total_tokens": 155,
                    "elapsed_time": 2.45,
                },
            },
            indent=2,
        )
    )

    print("\n💡 Parallel execution saves time! These 3 tasks run simultaneously.")
    print("   Total tokens used: 155 across all tasks")


def example_conditional_branching():
    """Example 3: Conditional branching"""
    print("\n" + "=" * 60)
    print("Example 3: Conditional Branching - Language Detection")
    print("=" * 60)

    user_input = "你好，世界！"

    condition_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [
            {
                "role": "user",
                "content": f"Is this text in Chinese? Reply only 'true' or 'false': {user_input}",
            }
        ],
        "max_tokens": 10,
        "temperature": 0.1,
    }

    true_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Respond in Chinese to: {user_input}"}],
        "max_tokens": 100,
    }

    false_task = {
        "provider": "openai",
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": f"Respond in English to: {user_input}"}],
        "max_tokens": 100,
    }

    print("\nMCP Tool Call:")
    print(f"""
    subagent_conditional(
        condition_task=json.dumps({json.dumps(condition_task, indent=8)}),
        true_task=json.dumps({json.dumps(true_task, indent=8)}),
        false_task=json.dumps({json.dumps(false_task, indent=8)})
    )
    """)

    print("\nExpected Response Structure:")
    print(
        json.dumps(
            {
                "condition_result": {
                    "text": "true",
                    "evaluated_as": True,
                    "usage": {"prompt_tokens": 15, "completion_tokens": 5, "total_tokens": 20},
                },
                "branch_taken": "true_branch",
                "final_result": {
                    "result": "你好！很高兴见到你...",
                    "usage": {"prompt_tokens": 18, "completion_tokens": 35, "total_tokens": 53},
                    "status": "success",
                },
                "total_usage": {
                    "prompt_tokens": 33,
                    "completion_tokens": 40,
                    "total_tokens": 73,
                },
                "status": "success",
            },
            indent=2,
        )
    )

    print("\n💡 Conditional branching: Only one branch executes based on the condition")
    print("   Total tokens: 73 (condition check + selected branch)")


def example_custom_models():
    """Example 4: Custom model support"""
    print("\n" + "=" * 60)
    print("Example 4: Custom Model Support (New in v0.2.0)")
    print("=" * 60)

    print("\nYou can now use ANY custom model name:")
    print("-" * 60)

    examples = [
        ("gpt-3.5-turbo", "openai", "Standard OpenAI model"),
        ("gpt-4", "openai", "GPT-4 standard"),
        ("gpt-4o-mini", "openai", "Budget-friendly option"),
        ("my-fine-tuned-gpt4", "openai", "🆕 Your custom fine-tuned model"),
        ("gpt-4-turbo-2024-04-09", "openai", "🆕 Newly released (no code update!)"),
        ("claude-3-5-sonnet-20241022", "anthropic", "Latest Claude"),
        ("custom-claude-model", "anthropic", "🆕 Custom deployment"),
    ]

    for model, provider, description in examples:
        print(f"  {model:35} ({provider:10}): {description}")

    print("\n📊 Token Usage Monitoring:")
    print("-" * 60)
    print("All tools return 'usage' field with detailed statistics:")
    print(
        json.dumps(
            {"usage": {"prompt_tokens": 50, "completion_tokens": 100, "total_tokens": 150}},
            indent=2,
        )
    )

    print("\n💰 Cost Tracking:")
    print("-" * 60)
    print("Check actual costs through provider dashboards:")
    print("  • OpenAI:    https://platform.openai.com/usage")
    print("  • Anthropic: https://console.anthropic.com/settings/usage")

    print("\n🎯 Model Selection Guide:")
    print("-" * 60)
    print("  Simple tasks:      gpt-3.5-turbo, claude-3-haiku")
    print("  Complex reasoning: gpt-4, claude-3-5-sonnet")
    print("  Budget-friendly:   gpt-4o-mini, claude-3-haiku")
    print("  Custom needs:      Your own fine-tuned models!")


def example_multi_turn_conversation():
    """Example 5: Multi-turn conversation simulation"""
    print("\n" + "=" * 60)
    print("Example 5: Multi-Turn Conversation")
    print("=" * 60)

    print("\nTurn 1: User asks a question")

    print("\nMCP Tool Call (Turn 1):")
    print("""
    result1 = subagent_call(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=json.dumps([
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "What is Python?"}
        ])
    )
    """)

    print("\nTurn 2: User asks follow-up (maintaining context)")
    print("\nMCP Tool Call (Turn 2):")
    print("""
    # Add AI's response from Turn 1 to maintain context
    messages_turn2 = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is Python?"},
        {"role": "assistant", "content": result1['result']},  # Previous response
        {"role": "user", "content": "What are its main use cases?"}  # Follow-up
    ]
    
    result2 = subagent_call(
        provider="openai",
        model="gpt-3.5-turbo",
        messages=json.dumps(messages_turn2)
    )
    """)

    print("\nNote: Subagent is stateless. You must maintain conversation history")
    print("      by including previous messages in the messages array.")


def example_error_handling():
    """Example 6: Error handling patterns"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)

    print("\nAlways check the 'status' field in responses:")
    print("-" * 60)

    print("\nCode Pattern:")
    print("""
    result = json.loads(subagent_call(...))
    
    if result['status'] == 'success':
        print(f"Result: {result['result']}")
        print(f"Tokens used: {result['usage']['total_tokens']}")
    else:
        print(f"Error: {result.get('error', 'Unknown error')}")
        # Handle error: retry, fallback model, or notify user
    """)

    print("\nCommon errors:")
    print("  • API key not configured")
    print("  • Rate limit exceeded")
    print("  • Invalid model name")
    print("  • Network timeout")
    print("  • Token limit exceeded")

    print("\nBest practices:")
    print("  1. Always set max_tokens to control costs")
    print("  2. Check status before processing results")
    print("  3. Monitor token usage via 'usage' field")
    print("  4. Use appropriate temperature (0.1 for factual, 0.7-1.0 for creative)")
    print("  5. Implement retry logic for transient failures")


def example_best_practices():
    """Example 7: Best practices summary"""
    print("\n" + "=" * 60)
    print("Example 7: Best Practices")
    print("=" * 60)

    print("\n1️⃣  Model Selection")
    print("   • Start with cheaper models (gpt-3.5-turbo)")
    print("   • Upgrade to premium only when needed")
    print("   • Use custom fine-tuned models for specialized tasks")

    print("\n2️⃣  Token Management")
    print("   • Always set max_tokens parameter")
    print("   • Monitor usage via 'usage' field")
    print("   • Track cumulative usage over time")

    print("\n3️⃣  Parallel Processing")
    print("   • Use subagent_parallel for independent tasks")
    print("   • Max 10 tasks per batch")
    print("   • Speeds up workflows significantly")

    print("\n4️⃣  Error Handling")
    print("   • Check 'status' field in all responses")
    print("   • Implement retry logic with exponential backoff")
    print("   • Have fallback models ready")

    print("\n5️⃣  Security")
    print("   • Never hardcode API keys")
    print("   • Use environment variables or config files")
    print("   • Rotate keys regularly")

    print("\n6️⃣  Cost Control")
    print("   • Check provider dashboards regularly")
    print("   • Set up billing alerts")
    print("   • Monitor token usage trends")

    print("\n7️⃣  Custom Models")
    print("   • Fine-tune models for specific domains")
    print("   • Test with small datasets first")
    print("   • Version your custom models")


def main():
    """Run all examples"""
    print("=" * 60)
    print("SUBAGENT AI ORCHESTRATION - USAGE EXAMPLES (v0.2.0)")
    print("=" * 60)
    print("\n🆕 What's New in v0.2.0:")
    print("  • Removed cost tracking (simplified response structure)")
    print("  • Added support for custom model names")
    print("  • Token usage statistics still available")
    print("  • Check costs via provider dashboards")

    # Check API keys
    if not os.getenv("OPENAI_API_KEY") and not os.getenv("ANTHROPIC_API_KEY"):
        print("\n⚠️  Warning: No API keys found!")
        print("   Set OPENAI_API_KEY and/or ANTHROPIC_API_KEY environment variables")
        print("   Or use: subagent_config_set() to configure permanently")

    # Run examples
    example_single_call()
    example_parallel_tasks()
    example_conditional_branching()
    example_custom_models()
    example_multi_turn_conversation()
    example_error_handling()
    example_best_practices()

    print("\n" + "=" * 60)
    print("✨ Examples completed!")
    print("=" * 60)
    print("\nFor more information, see docs/SUBAGENT_GUIDE.md")
    print("For configuration help, see docs/SUBAGENT_CONFIG.md")
    print("\n📚 Documentation: https://github.com/your-repo/mcp-server")


if __name__ == "__main__":
    main()
