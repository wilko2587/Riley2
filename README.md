
# Riley2

**Riley2** is an intelligent scheduling engine built to manage time, tasks, and constraints with agent support.  
It merges calendar blocks, resolves conflicts, and adapts to custom scheduling rules.

---

## ✨ Features

- Constraint-based time block merging
- Email, calendar, and location integration
- Rule-driven scheduling and resolution
- Extensible agent hooks

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- `pip`, `venv`, and `pytest`

### Install & Run

```bash
git clone https://github.com/wilko2587/Riley2.git
cd Riley2
python -m venv venv
source venv/bin/activate  # or .\venv\Scripts\activate on Windows
pip install -r requirements.txt
python main.py
```

### Run Tests

```bash
pytest
```

---

## 📁 Structure

```
agents/           # Core automation agents (calendar, email, etc.)
interfaces/       # External APIs and services
logs/             # Runtime output
tests/            # Unit and integration tests
releases/         # Release notes (one per checkpoint)
copilot_log/      # Task-specific chat logs
ROADMAP.ansi      # Visual project roadmap
```

---

## 🧠 Philosophy

Riley2 aims to be understandable, extensible, and auditable.  
All changes are tracked clearly with logs and rationale in natural language.
