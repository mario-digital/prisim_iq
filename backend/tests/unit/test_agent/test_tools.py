"""Tests for agent tools with @tool decorator pattern."""

import pytest
from langchain_core.tools import BaseTool

from src.agent.tools import (
    ALL_TOOLS,
    explain_decision,
    get_eda_summary,
    get_evidence,
    get_external_context,
    get_honeywell_mapping,
    get_segment,
    optimize_price,
    sensitivity_analysis,
)


class TestPricingTools:
    """Tests for pricing-related tools."""

    def test_optimize_price_tool_is_registered(self) -> None:
        """Test optimize_price is a valid LangChain tool."""
        assert isinstance(optimize_price, BaseTool)
        assert optimize_price.name == "optimize_price"
        assert "optimal price" in optimize_price.description.lower()

    def test_explain_decision_tool_is_registered(self) -> None:
        """Test explain_decision is a valid LangChain tool."""
        assert isinstance(explain_decision, BaseTool)
        assert explain_decision.name == "explain_decision"
        assert "explanation" in explain_decision.description.lower()

    def test_sensitivity_tool_is_registered(self) -> None:
        """Test sensitivity_analysis is a valid LangChain tool."""
        assert isinstance(sensitivity_analysis, BaseTool)
        assert sensitivity_analysis.name == "sensitivity_analysis"
        assert "sensitivity" in sensitivity_analysis.description.lower()


class TestDataTools:
    """Tests for data-related tools."""

    def test_get_segment_tool_is_registered(self) -> None:
        """Test get_segment is a valid LangChain tool."""
        assert isinstance(get_segment, BaseTool)
        assert get_segment.name == "get_segment"
        assert "segment" in get_segment.description.lower()

    def test_get_eda_summary_tool_is_registered(self) -> None:
        """Test get_eda_summary is a valid LangChain tool."""
        assert isinstance(get_eda_summary, BaseTool)
        assert get_eda_summary.name == "get_eda_summary"
        assert "statistics" in get_eda_summary.description.lower() or "dataset" in get_eda_summary.description.lower()

    def test_get_external_context_tool_is_registered(self) -> None:
        """Test get_external_context is a valid LangChain tool."""
        assert isinstance(get_external_context, BaseTool)
        assert get_external_context.name == "get_external_context"
        assert "external" in get_external_context.description.lower()

    def test_get_external_context_returns_simulated_data(self) -> None:
        """Test get_external_context returns simulated data."""
        result = get_external_context.invoke("")

        assert "Weather" in result
        assert "Events" in result
        assert "Fuel Prices" in result
        assert "SIMULATED" in result


class TestDocTools:
    """Tests for documentation-related tools."""

    def test_get_evidence_tool_is_registered(self) -> None:
        """Test get_evidence is a valid LangChain tool."""
        assert isinstance(get_evidence, BaseTool)
        assert get_evidence.name == "get_evidence"
        assert "model" in get_evidence.description.lower() or "documentation" in get_evidence.description.lower()

    def test_get_honeywell_mapping_tool_is_registered(self) -> None:
        """Test get_honeywell_mapping is a valid LangChain tool."""
        assert isinstance(get_honeywell_mapping, BaseTool)
        assert get_honeywell_mapping.name == "get_honeywell_mapping"
        assert "honeywell" in get_honeywell_mapping.description.lower()


class TestToolCollection:
    """Tests for tool collection and descriptions."""

    @pytest.fixture
    def all_tools(self) -> list[BaseTool]:
        """Get all tools from the ALL_TOOLS list."""
        return ALL_TOOLS

    def test_all_tools_have_unique_names(self, all_tools: list[BaseTool]) -> None:
        """Test all tools have unique names."""
        names = [tool.name for tool in all_tools]
        assert len(names) == len(set(names)), "Tool names must be unique"

    def test_all_tools_have_descriptions(self, all_tools: list[BaseTool]) -> None:
        """Test all tools have non-empty descriptions."""
        for tool in all_tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 20, f"Tool {tool.name} description too short"

    def test_tool_count_matches_story(self, all_tools: list[BaseTool]) -> None:
        """Test we have all 8 tools as specified in the story."""
        expected_count = 8
        assert len(all_tools) == expected_count, (
            f"Expected {expected_count} tools, got {len(all_tools)}"
        )

    def test_all_tools_list_contains_all_tools(self, all_tools: list[BaseTool]) -> None:
        """Test ALL_TOOLS contains all expected tools."""
        expected_names = {
            "optimize_price",
            "explain_decision",
            "sensitivity_analysis",
            "get_segment",
            "get_eda_summary",
            "get_external_context",
            "get_evidence",
            "get_honeywell_mapping",
        }
        actual_names = {tool.name for tool in all_tools}
        assert actual_names == expected_names
