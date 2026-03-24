# /kernel/complete

Final gate before marking work done.

## Instructions

1. **Check state:**

   | Gate | Required |
   |------|----------|
   | Protocol created | `protocol_created: true` |
   | Anchored | `anchored: true` |

2. **Verify deliverables (MANDATORY):**

   Before marking complete, actually look at what the task produced. Tool call success is not verification.

   | Deliverable type | How to verify |
   |-----------------|---------------|
   | Files created | Read them — confirm content matches requirements |
   | Files modified | Read the changed sections — confirm the edit is correct |
   | State changed | Read state files — confirm values are what you expect |
   | Tests ran | Read results — confirm pass/fail matches expectations |
   | Repo changes | List files, read key ones — confirm nothing unexpected |
   | Decisions/docs | Read them — confirm they address the requirements |
   | Nothing tangible | State what you verified and why it's sufficient |

   **Report verification in the completion output.** List what you checked and the result.

3. **Save final conversation context:**
   - Update `context` key in `.claude/state/session_state.json` with:
     - Summary of what was accomplished this session
     - Key decisions made
     - Any open items or next steps for future sessions
   - MERGE into existing state, don't overwrite other keys

4. **Update state:**
   ```json
   {
     "complete": true,
     "complete_timestamp": "..."
   }
   ```

5. **Report:**
   ```
   COMPLETE

   Domain: [domain]
   Task: [what was done]
   Files created/modified: [count]
   Lessons learned: [count]

   Verified:
   - [what I checked] → [result]
   - [what I checked] → [result]

   Done.
   ```

## When to Invoke

- ALWAYS before saying "done"
- NEVER skip this gate
