# COPILOT AGENT PROTOCOL (STEP-BY-STEP FLOW FORMAT)

───────────────────────────────────────────────────────────────────────────────
SECTION F0: STARTUP
───────────────────────────────────────────────────────────────────────────────

[F0.1] Wait for the command: `go`  
→ proceed to [F0.2]

[F0.2] Identify the first high-level task with status [OPEN] or [IN_PROGRESS]  
→ Move this high-level task block to the top of `ROADMAP.ansi`  
→ proceed to [F0.3]

[F0.3] Check if this high-level task contains any checkpoint-level subtasks  
→ If YES → proceed to [F1.1]  
→ If NO  → proceed to [F0.4]

[F0.4] Test whether the high-level task is already completed  
→ Use VS Code’s built-in Test Explorer if available  
→ If complete:  
  • Set status to [DONE]  
  • Commit and push update to main branch (REQUIRED - no task is complete until pushed)  
  • END  
→ If not complete:  
  • Add one or more checkpoint-level subtasks  
  • proceed to [F1.1]

───────────────────────────────────────────────────────────────────────────────
SECTION F1: CHECKPOINT TASK LOOP
───────────────────────────────────────────────────────────────────────────────

[F1.1] Select the next `checkpoint.*` task that is [OPEN] or [IN_PROGRESS]  
→ proceed to [F1.2]

[F1.2] Does this checkpoint contain any `lowlevel.*` subtasks?  
→ If YES → proceed to [F2.1]  
→ If NO  → proceed to [F1.3]

[F1.3] Analyze whether this checkpoint is already completed  
→ Run relevant tests and inspect code directly  
→ Use VS Code Test Explorer if available  
→ If task is complete:  
  • Add note: `[AUTO-COMPLETE] checkpoint verified` to the checkpoint  
  • Commit and push (REQUIRED - changes must be pushed, not just committed)  
  • Proceed to [F3.1]  
→ If not complete:  
  • Add one or more `lowlevel.*` roadmap items  
  • proceed to [F2.1]

───────────────────────────────────────────────────────────────────────────────
SECTION F2: LOW-LEVEL TASK EXECUTION
───────────────────────────────────────────────────────────────────────────────

[F2.1] Pick the first `lowlevel.*` subtask with status [OPEN] or [IN_PROGRESS]  
→ proceed to [F2.2]

[F2.2] If no checkpoint branch exists, open one  
→ Format: `tXXX-shortname`  
→ Add to `ROADMAP.ansi`: `[90m[COP] branch opened: [38;5;164mtXXX-shortname[0m`  
  (only the branch name should be in deep magenta color)  
→ proceed to [F2.3]

[F2.3] Visually highlight the active `lowlevel.*` task line  
→ In `ROADMAP.ansi`, apply amber background to the **entire line** beginning with:

  `> STATE: [IN_PROGRESS] ...`

→ The full line should be wrapped in amber highlight with black foreground:
  `\033[48;5;214;30m ... \033[0m`

→ Move the full parent `highlevel.*` block (including checkpoint + subtasks) to
  the **top of the file**

→ Only one `lowlevel.*` task may be highlighted at a time

→ proceed to [F2.4]

[F2.4] Create `copilot_log/tXXX-shortname.md`  
→ Include full log from the beginning:  
  [USER]: go  
  [COP]: ...  
  [GPT]: ...  
→ Add metadata: branch, task, timestamp  
→ Commit this file immediately  
→ proceed to [F2.5]

[F2.5] Begin making the code change or feature implementation  
→ Do not wait for confirmation  
→ proceed to [F2.6]

[F2.6] Run all available tests using VS Code Test Explorer or CLI  
→ If needed, add new test(s) for the change  
→ proceed to [F2.7]

[F2.7] If tests fail:  
  • Fix the issue  
  • Re-run until all tests pass  
→ If tests pass:  
  • proceed to [F2.8]

[F2.8] Update documentation files:  
  • `copilot_status.md` — describe steps taken  
  • `ROADMAP.ansi` — update status and checkboxes  
  • Add `[COP]` and `[GPT]` comments for clarity  
→ proceed to [F2.8.1]

[F2.8.1] Request human confirmation of changes:  
  • Pause and explicitly ask the human to review and accept all changes  
  • Wait for explicit confirmation before proceeding  
  • Ensure all file edits are properly accepted in the editor  
→ proceed to [F2.9]

[F2.9] Commit and push the code change to the branch *** REQUIRED STEP ***  
→ Add: `[COP] issue: #shorttag`  
→ Add: `[COP] committed [x], pushed [x]`  
→ Both commit AND push must be completed - local commits only are insufficient  
→ proceed to [F2.10]

[F2.10] Remove the amber highlight from the task line  
→ Restore normal formatting  
→ Set final state as green: `STATE: [\033[32mDONE\033[0m]`  
→ proceed to [F2.11]

[F2.11] Are there more `lowlevel.*` subtasks for this checkpoint?  
→ If YES → proceed to [F2.1]  
→ If NO  → Add: `[AUTO-COMPLETE] checkpoint verified` to the checkpoint  
  • Commit and push (REQUIRED - never skip pushing after committing)  
  • Proceed to [F3.1]

───────────────────────────────────────────────────────────────────────────────
SECTION F3: CHECKPOINT FINALIZATION
───────────────────────────────────────────────────────────────────────────────

[F3.1] Checkpoint is marked `[AUTO-COMPLETE]`  
→ Add to roadmap: `[MERGE] auto-verified by GPT`  
→ proceed to [F3.2]

[F3.2] Write the release note  
→ File: `releases/TASK-XXX.md`  
→ Use format: `✓ tXXX-branchname → short summary`  
→ Reference copilot_log entry  
→ proceed to [F3.3]

[F3.3] Update the copilot_status.md file  
→ Add relevant information about the completed work  
→ Include specific changes and achievements  
→ Add to the "Completed Tasks" section  
→ Request human confirmation of changes  
→ Commit and push these updates to the feature branch  
→ proceed to [F3.4]

[F3.4] Update ROADMAP.ansi with merge notation  
→ Add to roadmap:  
  • `[COP] branch tXXX-shortname merged`  
  • `[COP] branch tXXX-shortname deleted`  
→ Request human confirmation of changes  
→ Commit and push these updates to the feature branch  
→ proceed to [F3.5]

[F3.5] Merge the checkpoint branch into main  
→ Switch to the main branch  
→ Perform the merge (--no-ff is recommended)  
→ Resolve any conflicts that arise  
→ Once merged, delete the feature branch  
→ proceed to [F0.1]

───────────────────────────────────────────────────────────────────────────────
ROADMAP VISUAL FORMATTING RULES
───────────────────────────────────────────────────────────────────────────────

• Only one `lowlevel.*` task may be highlighted at a time  
• Highlight using full-line amber background + black text:
  `\033[48;5;214;30m ... \033[0m`  
• Do NOT highlight `checkpoint.*` or `highlevel.*` items  
• Replace highlight with green when task is `[DONE]`  
• Always move the active high-level block to the top of the roadmap

───────────────────────────────────────────────────────────────────────────────
AUTONOMY & LOGGING RULES
───────────────────────────────────────────────────────────────────────────────

• Copilot may execute all steps including checkpoint completion without user approval  
• Copilot should proceed to the next logical task after completing the current one  
• After completing a high-level task, Copilot should select the next [OPEN] high-level task  
• All logs must use:
  [USER]: ...  
  [COP]: ...  
  [GPT]: ...  
• Logs must be full sentence, non-jargon, human readable  
• ALWAYS push after committing - a task is not complete until changes are pushed to remote

───────────────────────────────────────────────────────────────────────────────
CRITICAL REMINDERS
───────────────────────────────────────────────────────────────────────────────

1. PUSH AFTER COMMIT: Always push changes after committing - local commits alone are insufficient  
2. NEVER SKIP STEPS: All protocol steps must be followed in order  
3. RUN TESTS: Always run tests before marking a task as complete  
4. VERIFY CHANGES: Check that all changes properly address the task requirements  
5. REQUEST HUMAN CONFIRMATION: Always pause and request human confirmation before committing changes  

───────────────────────────────────────────────────────────────────────────────
FILE NAMING CONVENTIONS
───────────────────────────────────────────────────────────────────────────────

• Branches:       `tXXX-shortname`  
• Log files:      `copilot_log/tXXX-shortname.md`  
• Release notes:  `releases/TASK-XXX.md`  
• Tasks:          Plain English — avoid jargon or acronyms

───────────────────────────────────────────────────────────────────────────────
TRIGGERS
───────────────────────────────────────────────────────────────────────────────

• `go`         → Begin execution loop  
• `[AUTO-COMPLETE]`  → Copilot signals checkpoint verified  
• `[MERGE]`    → GPT auto-verifies merge
