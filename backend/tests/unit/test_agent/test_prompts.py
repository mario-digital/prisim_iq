"""Tests for agent prompts."""

from src.agent.prompts.system import SYSTEM_PROMPT, create_prompt


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

    def test_create_prompt_returns_template(self) -> None:
        """Test create_prompt returns a valid ChatPromptTemplate."""
        from langchain_core.prompts import ChatPromptTemplate

        prompt = create_prompt()

        assert isinstance(prompt, ChatPromptTemplate)
        # Check that required variables are present
        assert "input" in prompt.input_variables or any(
            "input" in str(m) for m in prompt.messages
        )

