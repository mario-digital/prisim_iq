# 1. Introduction

## 1.1 Purpose

This document defines the complete technical architecture for PrismIQ, an agentic, chat-driven dynamic pricing copilot designed for hackathon demonstration. It serves as the authoritative reference for all development decisions.

## 1.2 Scope

- Full-stack monorepo architecture (Next.js frontend + FastAPI backend)
- LangChain-based agent with tool-calling capabilities
- ML pipeline for demand simulation and price optimization
- Local deployment without containerization

## 1.3 Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Architecture Style** | Monolithic fullstack | Simplicity for hackathon; clear boundaries |
| **Package Manager (JS)** | Bun | Fastest runtime, built-in bundler |
| **Package Manager (Python)** | uv | 10-100x faster than pip |
| **Containerization** | None | Simplicity; local development only |
| **Database** | File-based (Excel + JSON) | No external dependencies |
| **LLM Provider** | OpenAI GPT-4o | Best reasoning for agent tasks |

---
