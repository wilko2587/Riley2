# 🚦 Riley2 Protocols

This file defines how autonomous agents and humans interact with the Riley2 framework. It governs task execution, logging, testing, committing, and releasing.

---

## 🔁 Task Execution Flow

### 1. On Startup
- Read `README.md` to understand system architecture
- Read `ROADMAP.md` and locate next actionable `[ ] TASK-###`
- Cross-reference `GPTLOG.md` to avoid duplicate or blocked work
- Begin tracking in `copilot_status.md`

### 2. While Working
- Log substep activity in real-time to `copilot_status.md`
- Leave `#TODO`, `#FIXME`, `#NOTE` in code as needed
- Use VSCode **Testing Explorer** to run all tests
- Fix failures until all pass — do **not** rollback unless explicitly told

### 3. On Completion (`✅ PASS`)
- Mark `[x]` in `ROADMAP.md` next to the task
- Append a `GPTLOG.md` entry
- Generate a release note in `releases/TASK-###.md`
- Commit using format: `TASK-###: <summary>`
- Push

### 4. On Failure (`❌ FAIL` or `⚠ RETRY`)
- Do not commit code
- Mark task as `[!]` in `ROADMAP.md`
- Log what was attempted and what failed in `GPTLOG.md`
- Optionally save test output as `test_results/TASK-###.log`

---

## 🧪 Testing Protocol

1. **Use Only the VSCode Testing Explorer**  
   You must run tests using the built-in Testing Explorer panel in VSCode.  
   Do **not** invoke `pytest`, `unittest`, or test scripts via terminal commands like `python -m`.

2. **Detect All Tests**
   Tests are located under the `tests/` directory.  
   Ensure they are discovered automatically. Do **not** hardcode file paths.

3. **Run Full Suite**
   Always run **all tests** in the suite, not just the current file or module.

4. **Evaluate Results**
   - If all tests pass → continue
   - If any test fails → debug, fix the issue, and re-run until all tests pass
   - Never rollback unless explicitly instructed in the task or roadmap

5. **Recording Failures**
   - If you encounter persistent failures or reach a blocked state:
     - Mark the task as `[!]` in `ROADMAP.md`
     - Log full reasoning in `GPTLOG.md`
     - Save test output as `test_results/TASK-###.log`

6. **Do Not Bypass**
   - Do not skip or ignore failing tests
   - Do not alter test assertions unless explicitly told to
   - Do not assume success without verification from the Testing Explorer UI

---

## 🧾 File Format Standards

### ✅ `ROADMAP.md`
```markdown
# Roadmap

- [x] TASK-001: Set up base project scaffold
- [~] TASK-002: Design scheduler class interface
- [ ] TASK-003: Implement scheduler logic
- [!] TASK-004: Timezone sync issue (blocked by merge logic)
```

### 🧠 `GPTLOG.md`
```markdown
## TASK-004
⚠ RETRY  
**Timestamp:** 2025-05-03 16:02  
**Summary:**
- Attempted to sync calendar with merge logic
- Failing test: `test_event_merge_conflict`
- Possibly blocked by fallback rule design
```

### 📟 `copilot_status.md`
```text
TASK-005
├── 🟡 Reading ROADMAP.md
├── ✅ Located TASK-005
├── 🛠️ Editing scheduler.py
├── ✅ Saved tests/test_conflicts.py
├── ✅ Ran tests (PASS)
└── ✅ Committed TASK-005: Handle conflict overlap
```

### 📦 `releases/TASK-###.md`
```markdown
# TASK-005

**Commit:** `TASK-005: Handle conflict overlap`  
**Status:** ✅ PASS  
**Timestamp:** 2025-05-03 16:37

## Summary
- Added conflict resolution to scheduler
- Tests written for overlapping time scenarios
- Validated in VSCode Testing Explorer
```

---

## 📓 Logging Conventions

- One active task at a time
- `copilot_status.md` is reset on each task
- Logs are append-only — never overwrite old entries
- Log files must be Markdown-compatible
- `TASK-###` must match across all files
- `test_results/*.log` only created if tests fail
