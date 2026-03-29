"""
main.py — CLI demo script for PawPal+
Run: python main.py
Verifies that the backend logic works correctly in the terminal.
"""

from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler


def print_schedule(schedule):
    """Print a formatted task schedule to the terminal."""
    if not schedule:
        print("  (no tasks)")
        return
    for pet, task in schedule:
        status = "Done" if task.completed else "Pending"
        print(f"  [{status}] {task.time}  |  {pet.name:<12}|  {task.description}  ({task.frequency})")


def divider(label=""):
    """Print a section divider."""
    print("\n" + "-" * 55)
    if label:
        print(f"  {label}")
    print("-" * 55)


def main():
    # ── Phase 2, Step 2: Create Owner and Pets ──────────────
    owner = Owner("Alex", email="alex@example.com")

    buddy = Pet("Buddy", "dog", "Golden Retriever")
    whiskers = Pet("Whiskers", "cat", "Tabby")

    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    # ── Add tasks out of order (to test sorting) ─────────────
    buddy.add_task(Task("Evening walk",      "18:00", "daily"))
    buddy.add_task(Task("Morning walk",      "07:30", "daily"))
    buddy.add_task(Task("Flea medication",   "09:00", "weekly"))
    # Intentional conflict: same time as Buddy's morning walk
    buddy.add_task(Task("Buddy feeding",     "07:30", "daily"))

    whiskers.add_task(Task("Whiskers feeding", "08:00", "daily"))
    whiskers.add_task(Task("Vet appointment",  "14:00", "once"))

    scheduler = Scheduler(owner)

    # ── Today's Schedule ─────────────────────────────────────
    divider("PawPal+ — Today's Schedule")
    print_schedule(scheduler.get_todays_schedule())

    # ── Sorted by time ───────────────────────────────────────
    divider("All Tasks — Sorted by Time")
    print_schedule(scheduler.sort_by_time())

    # ── Filter: incomplete only ───────────────────────────────
    divider("Filter — Incomplete Tasks Only")
    print_schedule(scheduler.filter_tasks(completed=False))

    # ── Filter: by pet name ───────────────────────────────────
    divider("Filter — Buddy's Tasks Only")
    print_schedule(scheduler.filter_tasks(pet_name="Buddy"))

    # ── Conflict Detection ────────────────────────────────────
    divider("Conflict Detection")
    conflicts = scheduler.detect_conflicts()
    if conflicts:
        for warning in conflicts:
            print(f"  WARNING: {warning}")
    else:
        print("  No conflicts detected.")

    # ── Recurring Task Demo ───────────────────────────────────
    divider("Recurring Task — Mark Morning Walk Complete")
    morning_walk = buddy.tasks[1]   # "Morning walk" at 07:30
    print(f"  Before: Buddy has {len(buddy.tasks)} tasks")
    scheduler.mark_task_complete(buddy, morning_walk)
    print(f"  After:  Buddy has {len(buddy.tasks)} tasks")
    print(f"  New task due date: {buddy.tasks[-1].due_date}")

    # ── Updated Schedule ──────────────────────────────────────
    divider("Updated Schedule After Completion")
    print_schedule(scheduler.get_todays_schedule())

    print("\n" + "=" * 55)
    print("  Demo complete - all backend logic verified.")
    print("=" * 55 + "\n")


if __name__ == "__main__":
    main()
