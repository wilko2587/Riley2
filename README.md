# 🚀 Riley2 Assistant - Version 2.4

![Version](https://img.shields.io/badge/version-2.4-blue)
![Status](https://img.shields.io/badge/build-passing-brightgreen)
![Deployment](https://img.shields.io/badge/deploy-logging_enabled-success)

---

## 📈 Overview

**Riley2** is a modular, high-traceability AI agent framework designed for:

- ✅ Multi-step reasoning with full state visibility
- ✅ Calendar, email, and knowledge integrations
- ✅ Full logging (`copilot_status.md`, `GPTLOG.md`, `test_log.log`)
- ✅ Human + Copilot co-editing via `ROADMAP.md`
- ✅ Release notes for every task in `releases/`

---

## 🧠 Agent Workflow (Copilot)

1. Read `ROADMAP.md` to identify active or pending `TASK-###`
2. Execute the change
3. Track substeps live in `copilot_status.md`
4. Run tests (in VSCode UI or pytest)
5. If passing:
    - Update `ROADMAP.md` and `GPTLOG.md`
    - Commit and auto-generate `releases/TASK-###.md`
6. If failing:
    - Roll back
    - Log failure + notes in GPTLOG
    - Mark `ROADMAP.md` as `[!]`

---

## 📁 Directory Structure

```plaintext
Riley2/
├── src/                  # All core logic lives here
├── tests/                # All test cases
├── scripts/              # Deployment + launcher scripts
├── logs/                 # Runtime logs
├── secrets/              # Env keys (gitignored)
├── releases/             # One markdown file per task
├── dashboard.md          # High-level cockpit summary
├── copilot_status.md     # Live substep log from agent
├── ROADMAP.md            # Current task goals and states
├── GPTLOG.md             # Task execution history
├── README.md             # This file
```

---

## 🛠 Deployment

From root:
```bash
scripts/deploy_and_test_launcher.bat
```

Manually:
```bash
python scripts/main_launcher.py
```

---

## ✅ Tests

Run manually:
```bash
pytest -vvv -s
```

> Output logs go to `test_log.log` and/or VSCode test panel.

---

## 🧪 Copilot Instructions Summary

- Track task state in `ROADMAP.md`
- Log all reasoning in `GPTLOG.md`
- Live-update `copilot_status.md`
- Create release notes in `releases/TASK-###.md`
