# 📜 GPTLOG - Project Summary for Riley2 (v2.3e)

# Initial LLM Introduction

Hello,

You are now supporting an engineering project called **Riley2**.

✅ Please read the attached `GPTLOG.md` carefully.  
✅ Assume the system prioritizes:
- Modular architecture
- Full control over deployment
- Dynamic colorful logging
- LLM backend reasoning
- Professional-grade test coverage

Your role is to assist in expanding, refining, debugging, and maintaining this agent platform with a strong emphasis on:
- Smart reasoning
- Reliable tool execution
- Transparent planning
- Clean deploy workflows
- Live-testable logs

When proposing changes, always ensure:
- Full backwards compatibility unless explicitly authorized
- Clear testability (all major paths covered by tests)
- Explicit visibility of agent thinking (logs)
- Strict version control and checkpointing

You should maintain high skepticism of shortcuts or "magical" behavior.  
Every chain of reasoning must be **visible, traceable, and explainable**.

You must avoid introducing hidden complexity or opaque behavior.

---

# 🧠 Quick Core Principles:

- When extending tools or capabilities, **build modularly** (easy plug-and-play)
- When debugging LLM behavior, **prioritize colorful, clear logs**
- When running deployments, **treat code safety and backups as mandatory**
- Always strive for a "test-first" mindset — verify before claiming success
- Recognize when prior AI ideas didn’t work, and question novelty carefully

---

# 🚀 Current phase:

Riley2 v2.3e is deployed.  
We have colorful logging, full deploy validation, agent reasoning simulations, and test-backed workflows.

The next phases include smarter planner decisions, stronger calendar agent simulation, and knowledge base integrations.

---

# 🛠 Immediate Tasks:

You should assume the next goals could involve:
- Adding deeper calendar/event extraction capabilities
- Introducing a proper knowledge retrieval backend (KDB)
- Allowing more flexible tool planning chains
- Upgrading agent memory (short-term first)

Always discuss architectural choices **before implementation**.  
Treat control and explainability as more important than raw "magic" performance.

---

✅ Please confirm you understand.  
Then be ready to assist in further developing Riley2 in a clean, modular, production-grade way.


---
## 🎯 Project Purpose

**Riley2** is an evolving AI agent platform designed for:
- Multistep reasoning
- Conditional logic
- Tool selection and tool execution
- LLM interaction chaining
- Smart backend decision making
- Robust deployment workflows
- Full test coverage to ensure agent behavior is correct under various simulations

It aims to create a flexible, controllable AI assistant with modular backends for future plug-and-play components (calendar agents, email agents, knowledge bases, etc).

---
## 🛠 Current System Architecture (as of v2.3e)

| Layer | Key Components |
|:------|:---------------|
| Frontend (User Query) | Simulated user queries go into the system via tests |
| Backend LLM | `core/llm_backend.py` handles summarizing, interpreting tool results, and choosing actions |
| Planner | LLM model (ChatOllama Mistral 7B) generates plan on what tool to invoke |
| Tool Executor | Tools like calendar search, email search executed inside `core/tools/` |
| Test Framework | All tests inside `tests/`, dynamically log colorful execution |
| Deployment Workflow | `deployBounce.py` validates zip upgrades against local dev code |
| Automation Script | `deploy_and_test.ps1` automates deployment + test runs |

---
## 📦 Important Files Overview

| File | Purpose |
|:-----|:--------|
| `deployBounce.py` | Checks zip vs dev folder, manages backups, ensures safe deploy |
| `deploy_and_test.ps1` | Automates deploy and test execution |
| `core/llm_backend.py` | Summarize text, interpret tool output, backend planner decision logic |
| `tests/*.py` | Modular unit tests, color-coded and dynamically named |
| `logs/riley2_test.log` | Real-time live log of backend/LLM/test activity |
| `README.md`, `ROADMAP.md`, `GPTLOG.md` | Human-readable project information |

---
## 🔥 Design Priorities

- Full control over deployment and testing (human in the loop during upgrades)
- Modular and clean code
- Professional logging (Color-coded, tail-friendly for live debugging)
- Unit tests that check both surface behavior and deep reasoning
- Clear upgrade paths (e.g., adding new tools easily in `core/tools/`)

---
## 🧠 LLM Behavior Details

| Module | Behavior |
|:-------|:---------|
| `summarize_text` | Summarizes incoming text into concise readable form |
| `interpret_tool_command` | Converts tool raw output into human-like explanations |
| `backend_planner_llm` | Decides next action (e.g., calendar search, knowledge lookup) |
| `BackendLLM.choose_next_action` | Hardcoded fallback logic for action picking based on keywords |
| `BackendLLM.get_decision` | Currently simple yes/no turn management |

LLM used:  
- **ChatOllama**, Mistral 7B (local inference model)
- Temperature varies based on module (e.g., planner lower, interpretation higher)

---
## 📋 Testing Philosophy

Tests dynamically log:
- Start and finish of each test (colored 💠 and ✅)
- Summarize input/output shown in bright cyan
- Planner raw output and tool execution visibly separated in logs
- Fully live tailable via Powershell or shell `Get-Content -Wait`

Tests include reasoning validation:
- Example: Testing if the system can deduce "Italy trip" is on "15th May 2025" based on a dummy calendar entry and simulated time.

---
## 🚀 Deployment Workflow Summary

1. Download new Riley2 zip to `Downloads/`
2. Run `deployBounce.py`
   - Validates files and diffs
   - Asks for confirmation if diffs exist
   - Backs up `C:/dev/Riley2` before overwriting
3. If successful, run `tests`
4. Full success = new upgraded local dev state.

Optional full automation via `deploy_and_test.ps1`.

---
## 🔮 Future Expansion Plans (beyond v2.3e)

- Add multiple agent backend modules
- Refine planner tool selection using retrieval-augmented generation
- Add a Knowledge Base ("KDB") module
- More intelligent calendar interactions (time-based scanning)
- Self-healing deploy script (faster zip diffing)
- More powerful frontend prompts

---
## ⚡ Final Remarks

Riley2 is built carefully to **maximize control**, **visibility**, and **professional deploy-readiness**.  
The system is designed to evolve into a **production-grade assistant** capable of reasoning, tool use, and memory over time.

---

# 🧠 GPTs Reading This:

If you're a GPT agent or LLM system reading this GPTLOG:
- Assume the goal is **high control, full test coverage, and real engineering rigor**
- Always prefer **explicit logging**, **clear confirm steps**, and **visible reasoning chains**
- Support modular expansion of tools and agent types when designing next evolutions


---

# 📦 Packaging Rules

✅ When exchanging project ZIPs:
- User uploads: Outer folder wrapping (e.g., `Riley2/`) is **expected** and **correct**.
- Assistant sending ZIPs: Maintain same nested format internally.
- User manually unpacks outer folder after receiving.

This is a permanent project rule.
