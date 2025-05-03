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

### 2.1. On Starting a Task
When beginning work on a task, checkpoint, or low-level item:
- Update status to `in-progress` in `ROADMAP.md` and change emoji to 🟧
- Begin tracking progress in `copilot_status.md`
- Make an initial entry in `GPTLOG.md` indicating the task has started
- Create a new branch named `task/TASK-###` if working on a new TASK
- Highlight the currently active item in `ROADMAP.md` with amber background and black text

### 3. On Completion (`✅ PASS`)
- Mark `[x]` in `ROADMAP.md` next to the task
- Append a `GPTLOG.md` entry
- Generate a release note in `releases/TASK-###.md`
- Commit using format: `TASK-###: <summary>`
- Push

### 3.1. On Low-Level Task Completion
When completing a low-level task (`lowlevel.*`) within a larger checkpoint or high-level goal:
- Update status to `completed` in `ROADMAP.md` and change emoji to 🟩
- Append the completion to the current task's entry in `GPTLOG.md`
- Create or update release notes in `releases/TASK-###.md` with completed work
- Add a commit identifier that references the task (e.g., "TASK-002: Completed lowlevel.compare_email_mock_vs_real")
- Commit and push the changes using the same identifier

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



---

## 🌱 Git Branching

For every task (`TASK-###`), Copilot must:

- Create and switch to a new branch named `task/TASK-###`
- Perform **all code, test, and logging work** on that branch
- Use the commit format `TASK-###: <summary>` as always
- Push the branch via `git push -u origin task/TASK-###`

Copilot must **not**:
- Push directly to `main`, `master`, or any protected branch
- Merge the task branch unless explicitly instructed in `ROADMAP.md` or by human override


---

## Structured Logging Protocol

This project uses a hierarchical, append-only roadmap log to manage agent goals, checkpoints, and low-level tasks.

### Syntax Overview

- `highlevel.<goal_id>` – Defines a high-level objective or integration.
- `checkpoint.<checkpoint_id>` – Marks a milestone under a high-level goal.
- `lowlevel.<task_id>` – Specifies an actionable step under a checkpoint.
- `status: open | in-progress | complete | abandoned` – Current state of the task.
- `note: <freeform natural language comment>` – Optional context or explanation.

### Example Entry

```
highlevel.wa_integration
status: open
note: Add WhatsApp messaging support using Twilio.

checkpoint.twilio_auth
status: open
note: Handle Twilio API key validation.

lowlevel.write_twilio_auth_function
status: complete
note: Function implemented and tested in test_twilio_auth.py.
```

### Agent Behavior

- The agent must only append entries.
- The agent must resolve each `checkpoint.*` before proceeding to dependent `lowlevel.*`.
- Tasks should be logged chronologically under their logical hierarchy.

---



### Status Color Legend
- 🟥 **Open** – Task identified but not yet started
- 🟧 **In Progress** – Actively being worked on
- 🟩 **Complete** – Finished and verified

Tasks are marked with their corresponding color emoji prefix in the roadmap entries.
