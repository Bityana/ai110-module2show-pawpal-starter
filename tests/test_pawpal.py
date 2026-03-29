"""
tests/test_pawpal.py — Automated test suite for PawPal+
Run: python -m pytest
Covers: task completion, task addition, sorting, recurrence, conflict detection, edge cases.
"""

import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


# ── Fixtures ─────────────────────────────────────────────────

@pytest.fixture
def simple_owner():
    """Return an Owner with two pets and several tasks."""
    owner = Owner("Test Owner")
    buddy = Pet("Buddy", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    buddy.add_task(Task("Evening walk",       "18:00", "daily"))
    buddy.add_task(Task("Morning walk",       "07:30", "daily"))
    buddy.add_task(Task("Flea medication",    "09:00", "weekly"))

    whiskers.add_task(Task("Whiskers feeding", "08:00", "daily"))
    whiskers.add_task(Task("Vet appointment",  "14:00", "once"))
    return owner


# ── Phase 2: Basic Tests ──────────────────────────────────────

def test_task_completion_changes_status():
    """Task Completion: mark_complete() must set completed to True."""
    task = Task("Morning walk", "07:30", "once")
    assert task.completed is False
    task.mark_complete()
    assert task.completed is True


def test_task_addition_increases_pet_task_count():
    """Task Addition: adding a task to a Pet increases its task list length."""
    pet = Pet("Buddy", "dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task("Walk", "08:00", "daily"))
    assert len(pet.tasks) == 1
    pet.add_task(Task("Feed", "07:00", "daily"))
    assert len(pet.tasks) == 2


# ── Phase 5: Sorting Tests ────────────────────────────────────

def test_sort_by_time_returns_chronological_order(simple_owner):
    """Sorting Correctness: tasks must come back in ascending HH:MM order."""
    scheduler = Scheduler(simple_owner)
    sorted_tasks = scheduler.sort_by_time()
    times = [task.time for _, task in sorted_tasks]
    assert times == sorted(times), "Tasks are not in chronological order"


def test_sort_by_time_with_single_pet():
    """Sorting works correctly when there is only one pet."""
    owner = Owner("Solo")
    pet = Pet("Rex", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Night feed",    "21:00", "daily"))
    pet.add_task(Task("Morning feed",  "06:00", "daily"))
    pet.add_task(Task("Noon walk",     "12:30", "daily"))

    scheduler = Scheduler(owner)
    times = [t.time for _, t in scheduler.sort_by_time()]
    assert times == ["06:00", "12:30", "21:00"]


# ── Phase 5: Recurrence Tests ────────────────────────────────

def test_daily_task_creates_next_day_occurrence():
    """Recurrence Logic: marking a daily task complete auto-creates tomorrow's task."""
    today = date.today()
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    task = Task("Morning walk", "07:30", "daily", due_date=today)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    initial_count = len(pet.tasks)
    scheduler.mark_task_complete(pet, task)

    assert task.completed is True
    assert len(pet.tasks) == initial_count + 1
    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(days=1)
    assert new_task.completed is False
    assert new_task.description == task.description


def test_weekly_task_creates_next_week_occurrence():
    """Recurrence Logic: marking a weekly task complete creates next week's task."""
    today = date.today()
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    task = Task("Flea treatment", "09:00", "weekly", due_date=today)
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(pet, task)

    new_task = pet.tasks[-1]
    assert new_task.due_date == today + timedelta(weeks=1)
    assert new_task.frequency == "weekly"


def test_once_task_does_not_create_recurrence():
    """Recurrence Logic: a 'once' task must NOT add any new task after completion."""
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    task = Task("Vet visit", "10:00", "once")
    pet.add_task(task)

    scheduler = Scheduler(owner)
    scheduler.mark_task_complete(pet, task)

    assert task.completed is True
    assert len(pet.tasks) == 1   # no new task was appended


# ── Phase 5: Conflict Detection Tests ────────────────────────

def test_conflict_detected_for_same_time_different_pets():
    """Conflict Detection: tasks at the same time across pets must be flagged."""
    owner = Owner("Test Owner")
    buddy = Pet("Buddy", "dog")
    whiskers = Pet("Whiskers", "cat")
    owner.add_pet(buddy)
    owner.add_pet(whiskers)

    buddy.add_task(Task("Morning walk", "07:30", "daily"))
    whiskers.add_task(Task("Feeding",   "07:30", "daily"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 1
    assert "07:30" in conflicts[0]


def test_conflict_detected_same_pet_same_time():
    """Conflict Detection: two tasks for the same pet at the same time must be flagged."""
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Walk",     "08:00", "daily"))
    pet.add_task(Task("Feeding",  "08:00", "daily"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) >= 1


def test_no_conflict_with_different_times():
    """No warnings should fire when all tasks are at distinct times."""
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    pet.add_task(Task("Morning walk",  "07:30", "daily"))
    pet.add_task(Task("Midday feed",   "12:00", "daily"))
    pet.add_task(Task("Evening walk",  "18:00", "daily"))

    scheduler = Scheduler(owner)
    assert scheduler.detect_conflicts() == []


def test_completed_tasks_do_not_trigger_conflicts():
    """Completed tasks must be ignored by conflict detection."""
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    done_task = Task("Walk", "07:30", "daily")
    done_task.completed = True
    pet.add_task(done_task)
    pet.add_task(Task("Feeding", "07:30", "daily"))

    scheduler = Scheduler(owner)
    conflicts = scheduler.detect_conflicts()
    assert len(conflicts) == 0   # completed task should be skipped


# ── Edge Case Tests ───────────────────────────────────────────

def test_owner_with_no_pets_returns_empty_schedule():
    """Edge case: an owner with zero pets must return an empty schedule."""
    owner = Owner("Empty Owner")
    scheduler = Scheduler(owner)
    assert scheduler.get_all_tasks() == []
    assert scheduler.get_todays_schedule() == []
    assert scheduler.detect_conflicts() == []


def test_pet_with_no_tasks_returns_empty():
    """Edge case: a pet registered but with no tasks should return empty lists."""
    owner = Owner("Test Owner")
    pet = Pet("Ghost", "cat")
    owner.add_pet(pet)
    scheduler = Scheduler(owner)
    assert scheduler.get_all_tasks() == []


def test_filter_by_pet_name(simple_owner):
    """Filtering by pet name returns only that pet's tasks."""
    scheduler = Scheduler(simple_owner)
    buddy_tasks = scheduler.filter_tasks(pet_name="Buddy")
    assert all(pet.name == "Buddy" for pet, _ in buddy_tasks)
    assert len(buddy_tasks) == 3   # 3 tasks were added to Buddy


def test_filter_by_completed_status():
    """Filtering by completed=True returns only completed tasks."""
    owner = Owner("Test Owner")
    pet = Pet("Buddy", "dog")
    owner.add_pet(pet)
    done = Task("Old walk", "06:00", "once")
    done.completed = True
    pet.add_task(done)
    pet.add_task(Task("New walk", "07:00", "daily"))

    scheduler = Scheduler(owner)
    completed = scheduler.filter_tasks(completed=True)
    pending = scheduler.filter_tasks(completed=False)
    assert len(completed) == 1
    assert len(pending) == 1
