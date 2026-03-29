"""
PawPal+ — Logic Layer
Core classes for the pet care management system.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple


@dataclass
class Task:
    """Represents a single pet care activity."""

    description: str
    time: str          # "HH:MM" 24-hour format
    frequency: str     # "once", "daily", or "weekly"
    completed: bool = False
    due_date: date = field(default_factory=date.today)

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete and return the next occurrence for recurring tasks."""
        self.completed = True
        if self.frequency == "daily":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(days=1),
            )
        elif self.frequency == "weekly":
            return Task(
                description=self.description,
                time=self.time,
                frequency=self.frequency,
                due_date=self.due_date + timedelta(weeks=1),
            )
        return None

    def __str__(self) -> str:
        """Return a readable string representation of the task."""
        status = "Done" if self.completed else "Pending"
        return f"[{status}] {self.time} — {self.description} ({self.frequency})"


@dataclass
class Pet:
    """Stores pet details and a list of care tasks."""

    name: str
    species: str
    breed: str = ""
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a care task to this pet's task list."""
        self.tasks.append(task)

    def get_tasks(self) -> List[Task]:
        """Return all tasks assigned to this pet."""
        return self.tasks

    def __str__(self) -> str:
        """Return a readable string representation of the pet."""
        return f"{self.name} ({self.species})"


class Owner:
    """Manages multiple pets and provides access to all their tasks."""

    def __init__(self, name: str, email: str = "") -> None:
        """Initialize an Owner with a name and optional email address."""
        self.name = name
        self.email = email
        self.pets: List[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to this owner's list of pets."""
        self.pets.append(pet)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Return all (pet, task) tuples across every pet this owner has."""
        result = []
        for pet in self.pets:
            for task in pet.tasks:
                result.append((pet, task))
        return result

    def __str__(self) -> str:
        """Return a readable string representation of the owner."""
        return f"Owner: {self.name} ({len(self.pets)} pet(s))"


class Scheduler:
    """The 'Brain' — retrieves, organizes, and manages tasks across all pets."""

    def __init__(self, owner: Owner) -> None:
        """Initialize the Scheduler with an Owner instance."""
        self.owner = owner

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        """Retrieve every (pet, task) pair from the owner's pets."""
        return self.owner.get_all_tasks()

    def sort_by_time(self) -> List[Tuple[Pet, Task]]:
        """Return all tasks sorted chronologically using their HH:MM time attribute."""
        all_tasks = self.get_all_tasks()
        return sorted(all_tasks, key=lambda pt: pt[1].time)

    def filter_tasks(
        self,
        completed: Optional[bool] = None,
        pet_name: Optional[str] = None,
    ) -> List[Tuple[Pet, Task]]:
        """Filter tasks by completion status and/or pet name; None means no filter."""
        result = self.get_all_tasks()
        if completed is not None:
            result = [(pet, task) for pet, task in result if task.completed == completed]
        if pet_name is not None:
            result = [(pet, task) for pet, task in result if pet.name.lower() == pet_name.lower()]
        return result

    def detect_conflicts(self) -> List[str]:
        """Detect incomplete tasks scheduled at the same time; returns warning strings."""
        time_map: dict = {}
        warnings: List[str] = []
        for pet, task in self.get_all_tasks():
            if task.completed:
                continue
            if task.time in time_map:
                existing_pet, existing_task = time_map[task.time]
                warnings.append(
                    f"CONFLICT at {task.time}: '{existing_task.description}' "
                    f"({existing_pet.name}) clashes with '{task.description}' ({pet.name})"
                )
            else:
                time_map[task.time] = (pet, task)
        return warnings

    def mark_task_complete(self, pet: Pet, task: Task) -> None:
        """Mark a task done and automatically add the next occurrence for recurring tasks."""
        next_task = task.mark_complete()
        if next_task is not None:
            pet.add_task(next_task)

    def get_todays_schedule(self) -> List[Tuple[Pet, Task]]:
        """Return sorted incomplete tasks whose due_date is today or earlier."""
        today = date.today()
        return [
            (pet, task)
            for pet, task in self.sort_by_time()
            if not task.completed and task.due_date <= today
        ]
