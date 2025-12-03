"""Unit tests for orchestrator worker nodes."""

from unittest.mock import MagicMock, patch


class TestOptimizerNode:
    """Tests for the optimizer worker node."""

    def test_optimizer_node_returns_output(self) -> None:
        """Optimizer node invokes tool and stores result in outputs."""
        from src.orchestrator.nodes.optimizer import optimizer_node

        state = {
            "user_message": "What is the optimal price?",
            "context": {
                "unit_cost": 50.0,
                "competitor_price": 75.0,
                "customer_segment": "Premium",
            },
            "outputs": {},
        }

        with patch(
            "src.agent.tools.pricing_tools.optimize_price"
        ) as mock_tool:
            mock_tool.invoke.return_value = "Optimal Price: $94.50"
            result = optimizer_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "optimizer" in result["outputs"]
        assert "94.50" in result["outputs"]["optimizer"]
        mock_tool.invoke.assert_called_once_with("current")

    def test_optimizer_node_handles_error(self) -> None:
        """Optimizer node handles tool invocation errors gracefully."""
        from src.orchestrator.nodes.optimizer import optimizer_node

        state = {"context": {}, "outputs": {}}

        with patch(
            "src.agent.tools.pricing_tools.optimize_price"
        ) as mock_tool:
            mock_tool.invoke.side_effect = RuntimeError("Service unavailable")
            result = optimizer_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "optimizer" in result["outputs"]
        assert "Error" in result["outputs"]["optimizer"]

    def test_optimizer_node_preserves_existing_outputs(self) -> None:
        """Optimizer node preserves any existing outputs in state."""
        from src.orchestrator.nodes.optimizer import optimizer_node

        state = {
            "context": {},
            "outputs": {"previous": "some data"},
        }

        with patch(
            "src.agent.tools.pricing_tools.optimize_price"
        ) as mock_tool:
            mock_tool.invoke.return_value = "Optimal Price: $50.00"
            result = optimizer_node(state)  # type: ignore[arg-type]

        assert result["outputs"]["previous"] == "some data"
        assert "optimizer" in result["outputs"]


class TestExplainerNode:
    """Tests for the explainer worker node."""

    def test_explainer_node_returns_output(self) -> None:
        """Explainer node invokes tool and stores result in outputs."""
        from src.orchestrator.nodes.explainer import explainer_node

        state = {
            "user_message": "Why this price?",
            "context": {"customer_segment": "Premium"},
            "outputs": {},
        }

        with patch(
            "src.agent.tools.pricing_tools.explain_decision"
        ) as mock_tool:
            mock_tool.invoke.return_value = (
                "The price is driven by high competitor pricing and premium segment."
            )
            result = explainer_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "explainer" in result["outputs"]
        assert "premium" in result["outputs"]["explainer"].lower()

    def test_explainer_node_handles_error(self) -> None:
        """Explainer node handles tool invocation errors gracefully."""
        from src.orchestrator.nodes.explainer import explainer_node

        state = {"context": {}, "outputs": {}}

        with patch(
            "src.agent.tools.pricing_tools.explain_decision"
        ) as mock_tool:
            mock_tool.invoke.side_effect = ValueError("Invalid context")
            result = explainer_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "explainer" in result["outputs"]
        assert "Error" in result["outputs"]["explainer"]


class TestSensitivityNode:
    """Tests for the sensitivity worker node."""

    def test_sensitivity_node_returns_output(self) -> None:
        """Sensitivity node invokes tool and stores result in outputs."""
        from src.orchestrator.nodes.sensitivity import sensitivity_node

        state = {
            "user_message": "How robust is this price?",
            "context": {"unit_cost": 50.0},
            "outputs": {},
        }

        with patch(
            "src.agent.tools.pricing_tools.sensitivity_analysis"
        ) as mock_tool:
            mock_tool.invoke.return_value = (
                "Confidence band: $90-$98. Worst case: $85. Best case: $102."
            )
            result = sensitivity_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "sensitivity" in result["outputs"]
        assert "Confidence" in result["outputs"]["sensitivity"]

    def test_sensitivity_node_handles_error(self) -> None:
        """Sensitivity node handles tool invocation errors gracefully."""
        from src.orchestrator.nodes.sensitivity import sensitivity_node

        state = {"context": {}, "outputs": {}}

        with patch(
            "src.agent.tools.pricing_tools.sensitivity_analysis"
        ) as mock_tool:
            mock_tool.invoke.side_effect = Exception("Analysis failed")
            result = sensitivity_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "sensitivity" in result["outputs"]
        assert "Error" in result["outputs"]["sensitivity"]


class TestPolicyNode:
    """Tests for the policy checker worker node."""

    def test_policy_node_with_valid_tier_prices(self) -> None:
        """Policy node validates provided tier prices."""
        from src.orchestrator.nodes.policy import policy_node

        state = {
            "context": {
                "tier_prices": {
                    "new": 100.0,
                    "exchange": 95.0,
                    "repair": 90.0,
                    "usm": 85.0,
                }
            },
            "outputs": {},
        }

        result = policy_node(state)  # type: ignore[arg-type]

        assert "outputs" in result
        assert "policy" in result["outputs"]
        policy_output = result["outputs"]["policy"]
        assert policy_output["violations"] == []
        assert "No hierarchy violations" in policy_output["summary"]

    def test_policy_node_detects_hierarchy_violations(self) -> None:
        """Policy node detects when tier prices violate hierarchy."""
        from src.orchestrator.nodes.policy import policy_node

        state = {
            "context": {
                "tier_prices": {
                    "new": 100.0,
                    "exchange": 105.0,  # Violation: exchange > new
                    "repair": 90.0,
                    "usm": 85.0,
                }
            },
            "outputs": {},
        }

        result = policy_node(state)  # type: ignore[arg-type]

        policy_output = result["outputs"]["policy"]
        assert len(policy_output["violations"]) > 0
        assert policy_output["violations"][0]["type"] == "hierarchy_inversion"
        assert len(policy_output["suggestions"]) > 0

    def test_policy_node_derives_from_optimizer_output(self) -> None:
        """Policy node derives tier prices from optimizer output when not provided."""
        from src.orchestrator.nodes.policy import policy_node

        state = {
            "context": {},
            "outputs": {"optimizer": "Optimal Price: $100.00"},
        }

        result = policy_node(state)  # type: ignore[arg-type]

        policy_output = result["outputs"]["policy"]
        # Should derive prices based on 100.00 baseline
        assert policy_output["tier_prices"]["new"] == 100.0
        assert policy_output["tier_prices"]["exchange"] == 95.0  # 95%
        assert policy_output["tier_prices"]["repair"] == 90.0   # 90%
        assert policy_output["tier_prices"]["usm"] == 85.0      # 85%

    def test_policy_node_uses_defaults_when_no_input(self) -> None:
        """Policy node uses safe defaults when no prices available."""
        from src.orchestrator.nodes.policy import policy_node

        state = {"context": {}, "outputs": {}}

        result = policy_node(state)  # type: ignore[arg-type]

        policy_output = result["outputs"]["policy"]
        # Should use default prices
        assert "tier_prices" in policy_output
        assert policy_output["tier_prices"]["new"] == 100.0


class TestReporterNode:
    """Tests for the reporter worker node."""

    def test_reporter_chain_builds_correctly(self) -> None:
        """Reporter chain can be built with model parameter."""
        from src.orchestrator.nodes.reporter import reporter_chain

        with patch("src.orchestrator.nodes.reporter.get_settings") as mock_settings:
            mock_settings.return_value = MagicMock(openai_api_key="test-key")
            chain = reporter_chain(model="gpt-4o-mini")

        # Chain should be a runnable
        assert hasattr(chain, "invoke")

    def test_reporter_node_summarizes_outputs(self) -> None:
        """Reporter node invokes LLM to summarize accumulated outputs."""
        from src.orchestrator.nodes.reporter import reporter_node

        state = {
            "context": {"customer_segment": "Premium"},
            "outputs": {
                "optimizer": "Optimal Price: $94.50",
                "explainer": "Price driven by premium segment.",
            },
        }

        with patch(
            "src.orchestrator.nodes.reporter.reporter_chain"
        ) as mock_chain_fn:
            mock_chain = MagicMock()
            mock_chain.invoke.return_value = (
                "Summary: Recommended price is $94.50 for premium segment."
            )
            mock_chain_fn.return_value = mock_chain

            result = reporter_node(state, model="gpt-4o")  # type: ignore[arg-type]

        assert "outputs" in result
        assert "report" in result["outputs"]
        assert "94.50" in result["outputs"]["report"]
        # Original outputs should be preserved
        assert "optimizer" in result["outputs"]
        assert "explainer" in result["outputs"]

