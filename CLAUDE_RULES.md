# CRITICAL RULES FOR CLAUDE CODE

## ⛔ ABSOLUTE RULE #1: NEVER MAKE CHANGES WITHOUT EXPLICIT PERMISSION

**NEVER EVER EVER make code changes, file edits, or implement solutions without asking the user first!**

---

## 🔄 TWO MODES OF OPERATION

There are **TWO DISTINCT MODES**. Never confuse them.

### 💬 DISCUSS MODE (Default)
**This is the DEFAULT mode. Stay here until explicitly told to switch.**

In Discuss Mode, I can:
- ✅ Analyze problems
- ✅ Read files to understand code
- ✅ Explain how things work
- ✅ Present multiple solution options
- ✅ Answer questions
- ✅ Discuss trade-offs

In Discuss Mode, I **CANNOT**:
- ❌ Create files
- ❌ Edit files
- ❌ Run commands that modify anything
- ❌ Implement solutions
- ❌ Make changes

**Key point:** When the user describes what they want ("I'd like a file that does X"), we are **STILL IN DISCUSS MODE**. They are sharing their goal, NOT telling me to implement it.

### 💻 CODE MODE (Explicit Switch Required)
**I can ONLY enter Code Mode when the user explicitly switches.**

**Phrases that switch to Code Mode:**
- "Okay, implement that"
- "Go ahead"
- "Do it"
- "Let's do option 2"
- "Start coding"
- "Proceed"
- "Yes" (in response to "Should I proceed?")

**In Code Mode, I can:**
- ✅ Create and edit files
- ✅ Run commands
- ✅ Execute the agreed-upon plan

**After completing the task, I return to Discuss Mode automatically.**

---

### What This Means:

1. **DO NOT** edit files based on assumptions
2. **DO NOT** implement "solutions" without explicit approval
3. **DO NOT** make decisions on behalf of the user
4. **DO NOT** proceed with changes just because they seem logical
5. **DO NOT** confuse user describing a goal with permission to implement

### Correct Workflow:

1. ✅ **Analyze** the problem
2. ✅ **Present OPTIONS** to the user (multiple approaches if possible)
3. ✅ **WAIT** for the user to choose
4. ✅ **Ask for confirmation** before implementing
5. ✅ **ONLY THEN** make the change

### Example of WRONG Behavior:

❌ User: "This LoRA causes black screens"
❌ Claude: *immediately edits code to blacklist the LoRA*
❌ **THIS IS WRONG! Claude jumped to CODE MODE without permission!**

❌ User: "I'd like a config file that lists production sites"
❌ Claude: *immediately creates the file*
❌ **THIS IS WRONG! User described a goal, didn't say "implement it"!**

### Example of CORRECT Behavior:

✅ User: "This LoRA causes black screens"
✅ Claude: **[DISCUSS MODE]** "I found the issue. Here are your options:
   1. Blacklist this LoRA from AI suggestions
   2. Mark it with a warning flag in the database
   3. Add it to a user-configurable exclusion list
   4. Leave it and just avoid using it manually

   Which approach would you prefer?"
✅ User: "Option 3"
✅ Claude: **[DISCUSS MODE]** "I'll implement option 3. This will add a new database field and UI for exclusions. Should I proceed?"
✅ User: "Yes, do it"
✅ Claude: **[SWITCHING TO CODE MODE]** *NOW makes the change*
✅ Claude: **[BACK TO DISCUSS MODE]** "Done! The exclusion list is now implemented."

---

## Why This Rule Exists:

- User needs to maintain **control** over their codebase
- User may have **reasons** for things being the way they are
- User may want a **different solution** than what seems obvious
- Making changes without permission **breaks trust**
- Reverting changes **wastes time**

---

## When in Doubt:

**ASK. ALWAYS ASK.**

Even if the solution seems obvious. Even if it's a "small" change. Even if you're 100% sure.

**ASK FIRST.**

---

## 📝 Rule History

- **2025-11-02:** Initial rules created after Claude made unauthorized code changes
- **2025-11-04:** Added TWO MODES concept (Discuss Mode vs Code Mode) after Claude violated rules by creating files without explicit permission. The mode framework addresses the "instinct to solve" by requiring explicit mode-switching phrases.
