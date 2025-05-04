# PULL REQUEST REVIEW PROTOCOL

───────────────────────────────────────────────────────────────────────────────
SECTION P1: INITIATE REVIEW CONTEXT
───────────────────────────────────────────────────────────────────────────────

[P1.1] Assume the currently active Git branch is the feature branch under review  
[P1.2] Extract the branch name (e.g. `t123-feature`)  
[P1.3] Confirm the branch maps to a valid `TASK-XXX` entry in `ROADMAP.md`  
→ proceed to [P2.1]

───────────────────────────────────────────────────────────────────────────────
SECTION P2: CHECK FOR ROADMAP ALIGNMENT
───────────────────────────────────────────────────────────────────────────────

[P2.1] Locate the associated `TASK-XXX` entry in `ROADMAP.md`  
[P2.2] Confirm that the task’s stated goal aligns with the feature branch purpose  
→ proceed to [P3.1]

───────────────────────────────────────────────────────────────────────────────
SECTION P3: PERFORM CODE REVIEW
───────────────────────────────────────────────────────────────────────────────

[P3.1] Fetch the full diff between `branch` and `main`  
[P3.2] Review for:
  • Modularity  
  • Logging discipline  
  • Error and edge-case handling  
[P3.3] Confirm the implementation matches roadmap intent  
[P3.4] Flag and reject any unrelated or bundled changes  
[P3.5] Check for LLM-generated bloat:
  • Identify redundant logic, duplicate conditionals, unnecessary helper methods  
  • Detect verbose or over-engineered code that could be simplified  
  • Reject if the same outcome can be achieved more directly  
→ proceed to [P4.1]

───────────────────────────────────────────────────────────────────────────────
SECTION P4: VERIFY TEST COVERAGE
───────────────────────────────────────────────────────────────────────────────

[P4.1] Confirm presence of both unit and integration tests  
[P4.2] Check for edge cases:  
  • DST boundaries  
  • Null/missing values  
  • Leap years  
[P4.3] If any critical tests are missing or weak:  
  • ❌ REJECT  
→ If coverage is sufficient → proceed to [P5.1]

───────────────────────────────────────────────────────────────────────────────
SECTION P5: FINAL DECISION
───────────────────────────────────────────────────────────────────────────────

[P5.1] If code is clean, aligned, and test-covered → ✅ APPROVE  
[P5.2] If brittle, partial, or non-modular → ❌ REJECT  
[P5.3] Provide precise fix instructions to Copilot  
→ END

───────────────────────────────────────────────────────────────────────────────
SECTION P6: OUTPUT TEMPLATE
───────────────────────────────────────────────────────────────────────────────

## ✅ PR REVIEW: [branch-name]  
- Task: [TASK-### – summary]  
- Roadmap Match: ✔ / ✘ (reason)  
- Code Quality: ✔ / ✘ (reason)  
- Test Coverage: ✔ / ✘ (reason)  
- Merge Status: ✅ APPROVED / ❌ REJECTED  
- Feedback: [If rejected — explain exactly what to improve]  

───────────────────────────────────────────────────────────────────────────────
