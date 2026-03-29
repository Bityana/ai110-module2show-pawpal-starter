# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

I designed four classes to represent the system:

- **Task** — represents a single care activity. It holds a `description`, `time` (in HH:MM format), `frequency` (once/daily/weekly), a `completed` flag, and a `due_date`. Its key responsibility is `mark_complete()`, which returns the next occurrence of a recurring task automatically.

- **Pet** — stores a pet's `name`, `species`, and `breed`, plus a list of `Task` objects. Its responsibility is to own and expose its tasks via `add_task()` and `get_tasks()`.

- **Owner** — manages a list of `Pet` objects and provides `get_all_tasks()`, which flattens all tasks across all pets into `(Pet, Task)` tuples. This design lets the Scheduler always know *which pet* a task belongs to.

- **Scheduler** — the "brain." It takes an `Owner` at init time and provides all algorithmic operations: `sort_by_time()`, `filter_tasks()`, `detect_conflicts()`, `mark_task_complete()`, and `get_todays_schedule()`. The Scheduler holds *no data itself* — it operates entirely through the Owner.

Three core user actions I identified:
1. **Add a pet** — create a `Pet` object and register it with the `Owner`.
2. **Schedule a task** — create a `Task` and add it to a pet's task list via `Pet.add_task()`.
3. **See today's tasks** — call `Scheduler.get_todays_schedule()` to get sorted, pending tasks due today.

**b. Design changes**

During implementation I made one significant change: I initially planned for `mark_complete()` to live only in the `Scheduler`, but moved the recurrence logic *into the `Task` class* instead. When a task is marked complete, the `Task` itself decides whether to generate a next occurrence based on its `frequency` attribute and returns a new `Task` — or `None` for one-time tasks. The `Scheduler.mark_task_complete()` method then handles appending that new task to the pet.

This separation was cleaner: Task encapsulates what it *knows about itself* (its own recurrence), while Scheduler handles *where the new task goes*. It also made unit-testing recurrence logic on `Task` directly simpler.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers:
- **Time** — tasks are sorted chronologically by HH:MM string using Python's `sorted()` with a lambda key. Since times are zero-padded strings in HH:MM format, lexicographic sorting is equivalent to chronological sorting.
- **Due date** — `get_todays_schedule()` only surfaces tasks whose `due_date <= today`, filtering out future-dated tasks.
- **Completion status** — completed tasks are excluded from the "today's schedule" view and from conflict detection, to avoid false warnings.

I prioritized time-ordering as the primary constraint because a pet owner's main need is knowing *what to do and when*. Priority levels (high/medium/low) were considered but left out to avoid over-engineering the MVP.

**b. Tradeoffs**

**Tradeoff: Exact-time conflict detection only.**

The conflict detector checks whether two incomplete tasks share the *exact same* HH:MM time string. It does not account for task *duration* or overlapping time windows. For example, a 30-minute walk starting at 07:00 and a 20-minute feeding starting at 07:15 would not be flagged, even though they truly overlap.

This tradeoff is reasonable for an MVP because: (1) pet owners typically think in terms of scheduled start times, not time windows; (2) adding duration-based overlap detection would require tasks to carry a duration field and would significantly increase algorithm complexity; (3) for the use cases in this app (walks, feedings, medications), tasks are short enough that exact-time matching catches the most common mistake — accidentally double-booking the same slot.

---

## 3. AI Collaboration

**a. How you used AI**

I used Claude Code (Claude Sonnet 4.6) throughout this project as my AI assistant, playing the role that VS Code Copilot plays in the instructions.

Most effective uses:
- **System design brainstorming** — I described the scenario and asked the AI to suggest class responsibilities and relationships. The `(Pet, Task)` tuple pattern for `get_all_tasks()` came from this conversation and was a clean solution to the problem of "how does the Scheduler know which pet owns a task?"
- **Algorithm implementation** — I asked the AI to implement `sort_by_time()` using a lambda key, `detect_conflicts()` using a dictionary scan, and the recurrence logic using `timedelta`.
- **Test generation** — I described the behaviors to verify (sorting, recurrence, conflict detection, edge cases) and the AI scaffolded 15 test functions covering happy paths and edge cases.

The most helpful prompt pattern was: *"Given these class skeletons, implement [specific method] and explain the approach."* This kept me in control of the design while the AI filled in the implementation detail.

**b. Judgment and verification**

One AI suggestion I modified: the initial `detect_conflicts()` draft used a nested loop (O(n²)) comparing every task pair. I kept the logic the same but rewrote it using a dictionary keyed by time string (O(n)), which is simpler to read and more efficient. The AI's suggestion was correct but unnecessarily complex for a small dataset. I verified the rewrite by running `test_conflict_detected_for_same_time_different_pets` and `test_no_conflict_with_different_times`.

---

## 4. Testing and Verification

**a. What you tested**

15 automated tests covering:
1. **Task completion** — `mark_complete()` flips `completed` to True.
2. **Task addition** — `Pet.add_task()` increases the pet's task count.
3. **Sorting correctness** — `sort_by_time()` returns tasks in ascending HH:MM order.
4. **Daily recurrence** — marking a daily task complete adds a task for tomorrow.
5. **Weekly recurrence** — marking a weekly task complete adds a task for next week.
6. **No recurrence for "once"** — one-time tasks do not spawn a new task.
7. **Conflict detection** — same-time tasks across two pets are flagged.
8. **Conflict detection (same pet)** — same-time tasks on one pet are flagged.
9. **No false conflicts** — different-time tasks produce no warnings.
10. **Completed tasks skipped in conflict detection** — done tasks are not double-counted.
11. **Empty owner** — owner with no pets returns empty lists without crashing.
12. **Empty pet** — pet with no tasks returns empty lists.
13. **Filter by pet name** — only the requested pet's tasks are returned.
14. **Filter by completed status** — completed/pending split works correctly.
15. **Single-pet sorting** — sorting works when there is only one pet.

These tests were important because they cover the three core algorithmic behaviors (sorting, recurrence, conflict detection) plus edge cases that could silently produce wrong output (empty data, already-completed tasks).

**b. Confidence**

Confidence: ⭐⭐⭐⭐ (4 / 5)

All 15 tests pass. The system handles the expected happy paths and the main edge cases.

I would test next, given more time:
- Duration-based overlap detection (tasks that overlap in time window, not just start time)
- What happens with invalid time strings (e.g., "25:00")
- Persistence between Streamlit sessions (session_state resets on refresh)
- Multiple conflicts at the same time slot (three-way conflicts)

---

## 5. Reflection

**a. What went well**

The "CLI-first" workflow worked very well. Writing and running `main.py` before touching `app.py` meant I could verify all the sorting, filtering, recurrence, and conflict logic in isolation. By the time I wired up the Streamlit UI, the backend had no bugs — every `st.warning` and `st.table` call just worked.

**b. What you would improve**

If I had another iteration I would add task duration as an attribute and upgrade the conflict detector to flag overlapping time windows rather than just exact-time matches. I would also add a persistent storage layer (JSON or SQLite) so pet and task data survives a Streamlit page refresh.

**c. Key takeaway**

The most important thing I learned: **the AI is a powerful implementer, but a poor architect.** When I let it freely generate code, it sometimes created unnecessary complexity (nested loops, extra classes). When I stayed in the "lead architect" role — defining what each class was responsible for, what the method signatures should be, and what the test cases needed to prove — and then asked the AI to *implement* those specs, the code came out clean and correct. The human's job is to hold the design vision; the AI's job is to execute it precisely.

---

## AI Strategy Summary (VS Code Copilot / Claude Code)

**Which features were most effective:**
- **Agent Mode / full-file generation** for scaffolding pawpal_system.py and tests/test_pawpal.py from a clear spec
- **Inline Chat equivalent** for refining individual methods (e.g., rewriting detect_conflicts to use a dict instead of nested loops)
- **Chat for algorithm brainstorming** — asking "what is a lightweight conflict detection strategy?" and comparing options

**One AI suggestion I rejected:**
The AI initially suggested adding a `priority` field to Task and sorting by priority before time. I rejected this because the project spec prioritizes time-based scheduling, and adding priority sorting would have required defining priority ordering rules and complicating the scheduler significantly. Simpler is better for an MVP.

**How separate sessions helped:**
Using separate planning conversations for each phase kept context clean — the algorithmic design session didn't get polluted with UI questions, and the test-writing session started fresh without implementation assumptions. It mirrors the discipline of writing a spec before coding.
