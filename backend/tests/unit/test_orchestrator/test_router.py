from src.orchestrator.nodes.router import router_node


def test_router_selects_optimizer_by_default() -> None:
    state = {"user_message": "What is the optimal price?"}
    out = router_node(state)  # type: ignore[arg-type]
    assert out["route"] == "optimizer"


def test_router_selects_explainer() -> None:
    state = {"user_message": "Why was that price recommended? Please explain."}
    out = router_node(state)  # type: ignore[arg-type]
    assert out["route"] == "explainer"


def test_router_selects_sensitivity() -> None:
    state = {"user_message": "Run a sensitivity check with worst and best cases."}
    out = router_node(state)  # type: ignore[arg-type]
    assert out["route"] == "sensitivity"


def test_router_selects_policy() -> None:
    state = {"user_message": "Check policy compliance and hierarchy violations."}
    out = router_node(state)  # type: ignore[arg-type]
    assert out["route"] == "policy"

