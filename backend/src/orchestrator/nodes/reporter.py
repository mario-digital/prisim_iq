"""Reporter worker node: composes a concise analyst summary using LLM."""

from __future__ import annotations

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from src.config import get_settings
from src.orchestrator.state import OrchState


def reporter_chain(model: str | None = None):
    settings = get_settings()
    llm = ChatOpenAI(
        model=model or "gpt-4o",
        temperature=0,
        api_key=settings.openai_api_key,
        streaming=True,
    )

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a pricing analyst assistant. Summarize the results for a business audience. Be concise.",
            ),
            (
                "human",
                "Context: {ctx}\n\nOutputs (may include optimizer/explainer/sensitivity):\n{outputs}\n\nCompose a brief summary with key numbers and any rule implications.",
            ),
        ]
    )
    return prompt | llm | StrOutputParser()


def reporter_node(state: OrchState, model: str | None = None) -> dict:
    """Summarize accumulated outputs with an LLM; returns text in outputs.report."""
    outputs = state.get("outputs") or {}
    ctx = state.get("context") or {}

    chain = reporter_chain(model)
    text = chain.invoke({"outputs": outputs, "ctx": ctx})

    new_outputs = dict(outputs)
    new_outputs["report"] = text
    return {"outputs": new_outputs}

