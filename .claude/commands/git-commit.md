# Git Commit Message Convention

# 🚨🚨🚨 CRITICAL RULE #1 🚨🚨🚨
## **TYPE MUST BE LOWERCASE - NO CAPITAL LETTERS**

### ❌ WRONG ❌ WRONG ❌ WRONG ❌
- `Docs(main): add feature` ❌
- `Feat(story-1): update code` ❌  
- `Fix(BUG-123): resolve issue` ❌

### ✅ CORRECT ✅ CORRECT ✅ CORRECT ✅
- `docs(main): add feature` ✅
- `feat(story-1): update code` ✅
- `fix(BUG-123): resolve issue` ✅

**REMEMBER: `docs` NOT `Docs` | `feat` NOT `Feat` | `fix` NOT `Fix`**

---

## Task
Write standardized Git commit messages using conventional commit format.

## Format
```
<type>(<scope>): <description>

<detailed message>
```

### **⚠️ TYPE CASE COMPARISON ⚠️**
| ❌ WRONG (Capital) | ✅ CORRECT (lowercase) |
|-------------------|------------------------|
| `Docs(main):` | `docs(main):` |
| `Feat(M-123):` | `feat(M-123):` |
| `Fix(BUG-456):` | `fix(BUG-456):` |
| `Chore(develop):` | `chore(develop):` |
| `Style(main):` | `style(main):` |
| `Refactor(story-1):` | `refactor(story-1):` |
| `Test(feature/xyz):` | `test(feature/xyz):` |
| `Perf(PERF-789):` | `perf(PERF-789):` |
| `Ci(main):` | `ci(main):` |

**⚠️ IMPORTANT: `<type>` MUST ALWAYS BE LOWERCASE**

**Where `<scope>` is (in order of priority):**
1. Ticket number if available (e.g., `M-324`, `JIRA-123`, `BUG-456`)
2. Story identifier if no ticket (e.g., `story-1`, `story-auth`)
3. Branch name if no ticket/story (e.g., `main`, `develop`, `feature/user-auth`)

## Scope Priority (ALWAYS use in this order)
```
Ticket Number → Story ID → Branch Name
```
**Never leave scope empty. Always fall back to branch name.**

## Types Reference

**ALL TYPES MUST BE LOWERCASE - NO EXCEPTIONS**

| Type (lowercase!) | When to Use | Example |
|------|-------------|---------|
| `feat` | New feature/functionality | `feat(M-123): add user authentication` |
| `fix` | Bug fixes | `fix(BUG-456): resolve login timeout issue` |
| `chore` | Maintenance, dependencies, configs | `chore(main): update npm dependencies` |
| `style` | Code formatting (no logic change) | `style(feature/ui-refresh): fix indentation` |
| `refactor` | Code restructuring (no behavior change) | `refactor(TECH-789): extract helper functions` |
| `docs` | Documentation only | `docs(story-docs): update API reference` |
| `perf` | Performance improvements | `perf(PERF-111): optimize database queries` |
| `test` | Adding/updating tests | `test(develop): add unit tests for auth` |
| `ci` | CI/CD changes | `ci(main): add deployment workflow` |

❌ Never: `Feat`, `Fix`, `Docs`, `Chore`, `Style`, `Refactor`, `Perf`, `Test`, `Ci`
✅ Always: `feat`, `fix`, `docs`, `chore`, `style`, `refactor`, `perf`, `test`, `ci`

## Rules
1. **TYPE MUST BE LOWERCASE** (never `Feat`, `Docs`, `Fix` - always `feat`, `docs`, `fix`)
2. **Always include scope in parentheses** - use ticket > story > branch name (never leave empty)
3. Use imperative mood: "add" not "added" or "adds"
4. No period at end of description
5. Max 72 characters first line
6. Be specific and clear
7. Add detailed message on new lines when needed

## Examples

### Scenario 1: With ticket number
```bash
git commit -m "feat(M-324): add password reset functionality"

git commit -m "fix(BUG-456): prevent duplicate user registration" \
  -m "Added validation check before creating new user account" \
  -m "Resolves issue where users could register multiple times with same email"

git commit -m "docs(DOC-789): update README file" \
  -m "Added installation instructions and troubleshooting section"
```

### Scenario 2: No ticket, but have story
```bash
git commit -m "feat(story-1): implement checkout process"

git commit -m "refactor(story-auth): optimize authentication flow" \
  -m "Reduced API calls from 5 to 2 during login" \
  -m "Implemented token caching strategy"
```

### Scenario 3: No ticket or story (use branch name)
```bash
git commit -m "chore(main): update npm dependencies"

git commit -m "style(develop): fix code formatting" \
  -m "Applied consistent indentation across all components"

git commit -m "feat(feature/shopping-cart): add item quantity controls"

git commit -m "fix(hotfix/login-error): resolve timeout on login page"
```

### Multi-line detailed message format
```bash
git commit -m "feat(M-234): add user notification system" \
  -m "" \
  -m "Detailed changes:" \
  -m "- Implemented email notifications for order updates" \
  -m "- Added SMS alerts for critical events" \
  -m "- Created notification preferences panel" \
  -m "" \
  -m "Breaking changes: None" \
  -m "Testing: Added unit and integration tests"
```

## Decision Flow
1. What did you change? → Select type from table
2. **⚠️ MAKE TYPE LOWERCASE** → `feat` not `Feat`, `docs` not `Docs`
3. Determine scope (in this order):
   - Have a ticket number? → Use it (e.g., `M-324`, `BUG-123`)
   - No ticket but have a story? → Use story ID (e.g., `story-1`, `story-auth`)
   - No ticket or story? → Use current branch name (e.g., `main`, `develop`, `feature/xyz`)
4. Write: `<type>(<scope>): <what you did>`
5. **VALIDATE: Is your type lowercase? If it starts with capital letter, FIX IT!**
6. Add detailed message if needed (new lines)
7. Commit

## Quick Reference
- New feature? → `feat`
- Fixing bug? → `fix`
- Cleaning up? → `chore`
- Documentation? → `docs`
- Tests? → `test`
- Performance? → `perf`
- Code structure? → `refactor`
- Formatting? → `style`
- CI/CD? → `ci`

## 📋 PRE-COMMIT CHECKLIST (CHECK EVERY TIME!)

Before you commit, verify:

☐ **Is your type lowercase?**
  - ❌ `Docs` → ✅ `docs`
  - ❌ `Feat` → ✅ `feat`
  - ❌ `Fix` → ✅ `fix`

☐ **Did you include scope in parentheses?**
  - Ticket? Story? Branch name?

☐ **Is your verb imperative?**
  - ❌ `adds` → ✅ `add`
  - ❌ `added` → ✅ `add`
  - ❌ `adding` → ✅ `add`

☐ **No capital letters after the colon?**
  - ❌ `: Adds` → ✅ `: add`

**FINAL CHECK: Does it look like this?**
```
docs(main): add a line to the README
```
NOT like this:
```
Docs(main): Adds a line to the README
```

## Common Mistakes to Avoid

### 🔴 ERROR #1: Capitalizing the type (MOST COMMON)

❌ **WRONG:** `Docs(main): adds a line to the README` 
- **TWO ERRORS HERE:**
  1. Type MUST be lowercase (`docs` not `Docs`)
  2. Use imperative mood (`add` not `adds`)

✅ **CORRECT:** `docs(main): add a line to the README`

**MORE EXAMPLES OF THIS ERROR:**

❌ `Feat(M-324): implement new feature` → ✅ `feat(M-324): implement new feature`
❌ `Fix(BUG-123): resolves the issue` → ✅ `fix(BUG-123): resolve the issue`
❌ `Chore(main): updates dependencies` → ✅ `chore(main): update dependencies`
❌ `Style(develop): fixes formatting` → ✅ `style(develop): fix formatting`
❌ `Docs(story-1): updates README` → ✅ `docs(story-1): update README`

### 🔴 ERROR #2: Wrong verb form

❌ **WRONG:** `docs(main): Adds a line to the README`
- Use imperative "add" not "adds" or "added" or "adding"

✅ **CORRECT:** `docs(main): add a line to the README`

### Other mistakes

❌ **WRONG:** `docs: update README`
- Missing scope (should include ticket, story, or branch)

✅ **CORRECT:** `docs(story-docs): update README` or `docs(develop): update README`

❌ **WRONG:** `feat(none): add new feature`
- Never use "none" - always use branch name if no ticket/story

✅ **CORRECT:** `feat(main): add new feature`

❌ **WRONG:** `feat(M-323) add new component`
- Missing colon after scope

✅ **CORRECT:** `feat(M-323): add new component`

❌ **WRONG:** `docs(main): Adds a line to the README`
- Wrong verb form (should be imperative "add" not "adds")

✅ **CORRECT:** `docs(main): add a line to the README`