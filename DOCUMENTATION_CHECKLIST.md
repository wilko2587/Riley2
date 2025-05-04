# Documentation Checklist for Riley2

This file serves as a quick reference for the mandatory documentation updates required with every task.

## 📝 Required Documentation Updates

With **EVERY** task or code change, all of these files MUST be updated:

### 1. Update `copilot_status.md`
- [ ] Add current date and task being worked on
- [ ] List all actions taken in chronological order
- [ ] Include status updates (starting, in progress, completed)
- [ ] Document any issues encountered and their resolution
- [ ] Add next steps if the task is ongoing

### 2. Update `GPTLOG.md`
- [ ] Add new entry with timestamp for significant changes
- [ ] Include summary of what was accomplished
- [ ] Document any issues encountered and resolutions
- [ ] Reference relevant files that were modified
- [ ] Link to any related tasks or dependencies

### 3. Update `releases/TASK-###.md`
- [ ] Create file if it doesn't exist
- [ ] Document specific changes implemented
- [ ] List the benefits of these changes
- [ ] Note any impact on other parts of the system
- [ ] Include test results or validation steps

### 4. Update `ROADMAP.md`
- [ ] Mark current task with appropriate status
- [ ] Update completed items with proper formatting
- [ ] Add any new tasks identified during work
- [ ] Ensure relationships between tasks are clear

## 🔄 Automation Note

These documentation updates should be performed **automatically** with every task, without requiring explicit instruction from the user. Documentation is NOT optional - it is a mandatory part of every change to the system.

## 📊 Documentation Status Template

Use this template as a starting point for updates:

```markdown
## Documentation Status

### copilot_status.md
- ✅ Added current date and task
- ✅ Listed all actions taken
- ✅ Included status updates
- ✅ Documented issues and resolutions
- ✅ Added next steps

### GPTLOG.md
- ✅ Added timestamped entry
- ✅ Included summary of accomplishments
- ✅ Documented issues and resolutions
- ✅ Referenced modified files
- ✅ Linked related tasks

### releases/TASK-###.md
- ✅ Created/updated file
- ✅ Documented specific changes
- ✅ Listed benefits
- ✅ Noted system impact
- ✅ Included validation steps

### ROADMAP.md
- ✅ Marked task status
- ✅ Updated completed items
- ✅ Added new tasks
- ✅ Clarified task relationships
```