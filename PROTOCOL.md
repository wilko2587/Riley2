
# COPILOT AGENT PROTOCOL (FLOWCHART FORMAT, PLAIN LANGUAGE)

───────────────────────────────────────────────────────────────────────────────
FULL EXECUTION FLOW
───────────────────────────────────────────────────────────────────────────────

┌────────────────────────────────────────────────────────────────────────────┐
│ "go" received — begin execution                                            │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Look for a top-level task with status [OPEN] or [IN_PROGRESS]             │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
       ┌───────────────────────────────┐
       │ Are there any subtasks yet?   │
       └───────────────────────────────┘
            ↓ Yes                ↓ No
   ┌──────────────────┐   ┌────────────────────────────────────────────────┐
   │ Proceed to loop  │   │ Try to test if the task is already complete    │
   └──────────────────┘   │ - Use VS Code's Test Explorer if available     │
                          │ - If yes:                                      │
                          │     • Update status to [DONE]                  │
                          │     • Push update to main branch               │
                          │     • Stop here                                │
                          │ - If no:                                       │
                          │     • Add one or more subtasks                 │
                          └────────────────────────────────────────────────┘

──────────── TASK LOOP ─────────────
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Pick the next subtask not marked [DONE]                                   │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ If a branch hasn’t been opened yet, do it now                             │
│ Format: t###-shortname                                                    │
│ Add to roadmap: [COP] branch opened: t###-shortname                      │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Highlight the subtask in the roadmap using an amber background            │
│ STATE: [\033[48;5;214;30m IN_PROGRESS \033[0m]                          │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Make the actual change or fix in the code                                 │
│ → Copilot does this without needing approval                              │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Run all tests — all must pass                                             │
│ → Write a test if needed                                                  │
│ → Use Test Explorer if possible                                           │
│ → Copilot proceeds automatically unless a failure happens                 │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Update logs and roadmap                                                   │
│ - GPTLOG.md: explain why the change matters                               │
│ - copilot_status.md: track what is being done                             │
│ - ROADMAP.md: update the current subtask’s status                         │
│ - Add [GPT] and [COP] natural language notes if needed                    │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Commit and push the code                                                  │
│ - Include: [COP] issue: #xyz123                                           │
│ - Then:   [COP] committed [x], pushed [x]                                 │
│ → No confirmation needed to commit/push                                   │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Mark the subtask as [DONE] and remove highlight                           │
└────────────────────────────────────────────────────────────────────────────┘
               ↓
┌────────────────────────────────────────────────────────────────────────────┐
│ Are there any other subtasks?                                             │
└────────────────────────────────────────────────────────────────────────────┘
             ↓Yes               ↓No
┌─────────────────────────────┐   ┌────────────────────────────────────────┐
│ Pick the next unfinished     │   │ Task may be complete — mark [PENDING] │
└─────────────────────────────┘   │ Remain on branch until reviewed        │
                                 └────────────────────────────────────────┘
                                               ↓
                         ┌──────────────────────────────────────────────┐
                         │ GPT checks task marked [PENDING]             │
                         │ If okay:                                     │
                         │ - add [MERGE] confirmed by GPT               │
                         │ - Copilot merges and deletes the branch      │
                         └──────────────────────────────────────────────┘
                                               ↓
                         ┌──────────────────────────────────────────────┐
                         │ Write a release note:                        │
                         │ ✓ t###-short → what changed and why          │
                         └──────────────────────────────────────────────┘

───────────────────────────────────────────────────────────────────────────────
NAMING RULES & CLARITY
───────────────────────────────────────────────────────────────────────────────

- Tasks should use plain English
  e.g. “test email sending” not “init.smtp.mock.flow”
- Avoid jargon, acronyms, or abbreviations
- All tasks should have a short description of what they do and why
- Leave [GPT] and [COP] comments under the task to explain reasoning
- Branch names: t###-shortdescription (e.g. t105-logging-cleanup)

───────────────────────────────────────────────────────────────────────────────
STATUS FORMATTING
───────────────────────────────────────────────────────────────────────────────

- [OPEN]:       Task not started
- [IN_PROGRESS]: Task being worked on
- [DONE]:       Task completed and verified
- [PENDING]:    All subtasks done — needs GPT check
- [MERGE]:      GPT has approved, agent may merge
- Highlight only active subtasks:
  → [\033[48;5;214;30m IN_PROGRESS \033[0m]

───────────────────────────────────────────────────────────────────────────────
AGENT AUTONOMY
───────────────────────────────────────────────────────────────────────────────

Copilot does not need approval unless:
- A task is marked [PENDING]
- There’s a test failure or uncertainty
- A required file is missing

Otherwise:
- Pick a task
- Do the work
- Log progress
- Push changes

───────────────────────────────────────────────────────────────────────────────
TRIGGERS
───────────────────────────────────────────────────────────────────────────────

- `go`: start the task loop
- [PENDING]: mark task ready for GPT review
- [MERGE]: confirmed by GPT, Copilot may merge

───────────────────────────────────────────────────────────────────────────────
COPILOT CHAT LOGGING
───────────────────────────────────────────────────────────────────────────────

Every task branch must begin with a log file in `copilot_log/`.

Before any commits are made, the agent must:
1. Create `copilot_log/t###-shortname.md`
2. Include metadata:
   - Branch name
   - Task name
   - Timestamp
3. Begin logging:
   - Every interaction must be saved in full:  
     [USER]: ...  
     [COP]: ...  
     [GPT]: ...

4. Append logs as the task proceeds (e.g., task picked, test run, roadmap edit)
5. Commit the log file before the first push
6. Reference this log in the release note

> This ensures full transparency and traceability across all task executions.

───────────────────────────────────────────────────────────────────────────────
LOGGING LANGUAGE CLARITY
───────────────────────────────────────────────────────────────────────────────

All entries written to `copilot_log/` must use plain, human-friendly language.

- Avoid acronyms, shorthand, or implementation jargon.
- Use full sentences to describe what happened, why, and what was affected.
- Each log should be understandable by both a human and GPT reviewing the task.

Example (GOOD):
  [COP]: Created folders for code, logs, tests, and releases so other modules have clear places to live.

Example (BAD):
  [COP]: bootstrapped FS /logs /t /a  ✔️

This is especially important when explaining why tests passed, failed, or why a design was chosen.
