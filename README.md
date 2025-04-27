# 🚀 Riley2 Assistant - Version 2.3e

![Version](https://img.shields.io/badge/version-2.3e-blue)
![Status](https://img.shields.io/badge/build-passing-brightgreen)
![Deployment](https://img.shields.io/badge/deploy-logging_enabled-success)

---

## 📈 Project Overview

**Riley2** is a modular, professional-grade AI agent platform built for:
- Multi-step reasoning
- Intelligent tool selection and execution
- Calendar, email, and knowledge base integrations
- Full test coverage and deployment control

Architected for high explainability, visibility, and easy extensibility.

---

## 🛸 System Architecture

```plaintext
[User Input]
    ↓
[Frontend LLM Agent]
    ↓
[Backend Manager Agent]
    ↓
[Planner (LLM) -> Tool Executor]
    → [Calendar Agent]
    → [Email Agent]
    → [Knowledge Base]
    ↓
[Response Synthesizer]
    ↓
[Frontend LLM Agent]
    ↓
[User Output]
```

---

## 🏗️ Directory Structure

```plaintext
Riley2Container/
├── README.md
├── ROADMAP.md
├── scripts/
│   ├── deployBounce.py
│   ├── deploy_and_test.ps1
│   ├── deploy_and_test_launcher.bat
│   ├── main_launcher.py
├── Riley2/
│   ├── __init__.py
│   ├── core/
│   ├── agents/
│   ├── data/
│   ├── logs/
│   ├── secrets/
│   ├── tests/
│   └── twilio_sandbox/
```

---

## 🚀 Deployment Workflow

From the project root (`C:\dev\Riley2`):

```bash
scripts\deploy_and_test_launcher.bat
```

or run the main launcher manually:

```bash
python scripts/main_launcher.py
```

---

## 💪 Testing

Tests automatically run after deployment.  
You can manually trigger with:

```bash
cd Riley2
python -m tests.run_tests_and_package
```

Logs are stored under `/logs/riley2_test.log`.

---

> **Note:** Riley2 is designed for full traceability, modular evolution, and production-grade readiness.

---
