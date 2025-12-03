"""Tests for agent tools."""

import pytest
from langchain_core.tools import Tool

from src.agent.tools.data_tools import (
    create_get_eda_summary_tool,
    create_get_external_context_tool,
    create_get_segment_tool,
)
from src.agent.tools.doc_tools import (
    create_get_evidence_tool,
    create_get_honeywell_mapping_tool,
)
from src.agent.tools.pricing_tools import (
    create_explain_decision_tool,
    create_optimize_price_tool,
    create_sensitivity_tool,
)


class TestPricingTools:
    """Tests for pricing-related tools."""

    def test_optimize_price_tool_creation(self) -> None:
        """Test optimize_price tool is created correctly."""
        tool = create_optimize_price_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "optimize_price"
        assert "optimal price" in tool.description.lower()
        assert callable(tool.func)

    def test_explain_decision_tool_creation(self) -> None:
        """Test explain_decision tool is created correctly."""
        tool = create_explain_decision_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "explain_decision"
        assert "explanation" in tool.description.lower()
        assert callable(tool.func)

    def test_sensitivity_tool_creation(self) -> None:
        """Test sensitivity_analysis tool is created correctly."""
        tool = create_sensitivity_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "sensitivity_analysis"
        assert "sensitivity" in tool.description.lower()
        assert callable(tool.func)


class TestDataTools:
    """Tests for data-related tools."""

    def test_get_segment_tool_creation(self) -> None:
        """Test get_segment tool is created correctly."""
        tool = create_get_segment_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "get_segment"
        assert "segment" in tool.description.lower()
        assert callable(tool.func)

    def test_get_eda_summary_tool_creation(self) -> None:
        """Test get_eda_summary tool is created correctly."""
        tool = create_get_eda_summary_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "get_eda_summary"
        assert "statistics" in tool.description.lower() or "dataset" in tool.description.lower()
        assert callable(tool.func)

    def test_get_external_context_tool_creation(self) -> None:
        """Test get_external_context tool is created correctly."""
        tool = create_get_external_context_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "get_external_context"
        assert "external" in tool.description.lower()
        assert callable(tool.func)

    def test_get_external_context_returns_simulated_data(self) -> None:
        """Test get_external_context returns simulated data."""
        tool = create_get_external_context_tool()
        result = tool.func("")

        assert "Weather" in result
        assert "Events" in result
        assert "Fuel Prices" in result
        assert "Simulated" in result


class TestDocTools:
    """Tests for documentation-related tools."""

    def test_get_evidence_tool_creation(self) -> None:
        """Test get_evidence tool is created correctly."""
        tool = create_get_evidence_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "get_evidence"
        assert "model" in tool.description.lower() or "documentation" in tool.description.lower()
        assert callable(tool.func)

    def test_get_honeywell_mapping_tool_creation(self) -> None:
        """Test get_honeywell_mapping tool is created correctly."""
        tool = create_get_honeywell_mapping_tool()

        assert isinstance(tool, Tool)
        assert tool.name == "get_honeywell_mapping"
        assert "honeywell" in tool.description.lower()
        assert callable(tool.func)


class TestToolDescriptions:
    """Tests for tool description quality."""

    @pytest.fixture
    def all_tools(self) -> list[Tool]:
        """Create all tools for testing."""
        return [
            create_optimize_price_tool(),
            create_explain_decision_tool(),
            create_sensitivity_tool(),
            create_get_segment_tool(),
            create_get_eda_summary_tool(),
            create_get_external_context_tool(),
            create_get_evidence_tool(),
            create_get_honeywell_mapping_tool(),
        ]

    def test_all_tools_have_unique_names(self, all_tools: list[Tool]) -> None:
        """Test all tools have unique names."""
        names = [tool.name for tool in all_tools]
        assert len(names) == len(set(names)), "Tool names must be unique"

    def test_all_tools_have_descriptions(self, all_tools: list[Tool]) -> None:
        """Test all tools have non-empty descriptions."""
        for tool in all_tools:
            assert tool.description, f"Tool {tool.name} has no description"
            assert len(tool.description) > 20, f"Tool {tool.name} description too short"

    def test_tool_count_matches_story(self, all_tools: list[Tool]) -> None:
        """Test we have all 8 tools as specified in the story."""
        expected_count = 8
        assert len(all_tools) == expected_count, (
            f"Expected {expected_count} tools, got {len(all_tools)}"
        )

