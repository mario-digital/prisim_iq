# Appendix A: Architecture Decision Records

## ADR-001: Monolithic over Microservices

**Status:** Accepted

**Context:** PrismIQ is a hackathon project with a 2-week development timeline.

**Decision:** Use a monolithic architecture with clear module boundaries instead of microservices.

**Consequences:**
- (+) Faster development and deployment
- (+) Simpler debugging and testing
- (+) No network overhead between services
- (-) All components scale together
- (-) Harder to migrate to microservices later

## ADR-002: Bun over npm/pnpm

**Status:** Accepted

**Context:** Need fast development iteration and modern JavaScript runtime.

**Decision:** Use Bun as the JavaScript runtime and package manager.

**Consequences:**
- (+) Fastest install times (10-100x faster than npm)
- (+) Built-in bundler reduces tooling
- (+) Native TypeScript execution
- (-) Newer ecosystem, fewer edge cases handled
- (-) Team must learn new tool

## ADR-003: uv over pip/poetry

**Status:** Accepted

**Context:** Python package management is slow and lockfiles are inconsistent.

**Decision:** Use uv for Python package management with venv.

**Consequences:**
- (+) 10-100x faster installs
- (+) Reliable lockfile format
- (+) Compatible with pip requirements
- (-) Newer tool, may have edge cases
- (-) Team must learn new commands

## ADR-004: File-based Storage

**Status:** Accepted

**Context:** Hackathon demo doesn't require persistent multi-user data.

**Decision:** Use Excel for source data, JSON files for scenarios, and joblib for models.

**Consequences:**
- (+) No database setup or management
- (+) Easy to inspect and debug data
- (+) Portable across environments
- (-) No concurrent write safety
- (-) Manual migration for production

---
