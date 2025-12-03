"""Tests for agent prompts."""

from langchain_core.messages import SystemMessage

from src.agent.prompts.system import SYSTEM_PROMPT, get_system_message


class TestSystemPrompt:
    """Tests for system prompt content."""

    def test_system_prompt_contains_role(self) -> None:
        """Test system prompt contains role definition."""
        assert "PrismIQ" in SYSTEM_PROMPT
        assert "pricing copilot" in SYSTEM_PROMPT

    def test_system_prompt_contains_all_tools(self) -> None:
        """Test system prompt lists all available tools."""
        expected_tools = [
            "optimize_price",
            "explain_decision",
            "sensitivity_analysis",
            "get_segment",
            "get_eda_summary",
            "get_external_context",
            "get_evidence",
            "get_honeywell_mapping",
        ]

        for tool in expected_tools:
            assert tool in SYSTEM_PROMPT, f"Tool {tool} not found in system prompt"

    def test_system_prompt_contains_guidelines(self) -> None:
        """Test system prompt contains usage guidelines."""
        assert "Guidelines" in SYSTEM_PROMPT
        assert "Response Format" in SYSTEM_PROMPT

    def test_get_system_message_returns_system_message(self) -> None:
        """Test get_system_message returns a valid SystemMessage for LangGraph."""
        message = get_system_message()

        assert isinstance(message, SystemMessage)
        assert message.content == SYSTEM_PROMPT
        assert "PrismIQ" in message.content

    def test_system_prompt_has_tool_selection_guide(self) -> None:
        """Test system prompt has tool selection guide."""
        assert "Tool Selection Guide" in SYSTEM_PROMPT
        assert 'Questions about "what price"' in SYSTEM_PROMPT
        assert 'Questions about "why"' in SYSTEM_PROMPT
