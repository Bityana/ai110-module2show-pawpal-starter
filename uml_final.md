# PawPal+ — Final UML Class Diagram (Mermaid.js)

Paste the code block below into https://mermaid.live to render and screenshot as `uml_final.png`.

```mermaid
classDiagram
    class Task {
        +str description
        +str time
        +str frequency
        +bool completed
        +date due_date
        +mark_complete() Task
        +__str__() str
    }

    class Pet {
        +str name
        +str species
        +str breed
        +List~Task~ tasks
        +add_task(task: Task) None
        +get_tasks() List~Task~
        +__str__() str
    }

    class Owner {
        +str name
        +str email
        +List~Pet~ pets
        +add_pet(pet: Pet) None
        +get_all_tasks() List~Tuple~
        +__str__() str
    }

    class Scheduler {
        +Owner owner
        +get_all_tasks() List~Tuple~
        +sort_by_time() List~Tuple~
        +filter_tasks(completed, pet_name) List~Tuple~
        +detect_conflicts() List~str~
        +mark_task_complete(pet, task) None
        +get_todays_schedule() List~Tuple~
    }

    Owner "1" --> "0..*" Pet : owns
    Pet   "1" --> "0..*" Task : has
    Scheduler "1" --> "1" Owner : manages
    Scheduler ..> Pet  : accesses via Owner
    Scheduler ..> Task : reads and updates
```

## Relationships Explained

| Relationship | Description |
|---|---|
| Owner → Pet | An owner can have zero or more pets (composition) |
| Pet → Task | A pet has zero or more tasks (composition) |
| Scheduler → Owner | Scheduler is initialized with one Owner (association) |
| Scheduler ⇢ Pet | Scheduler accesses pets indirectly through Owner |
| Scheduler ⇢ Task | Scheduler reads/updates tasks via the pet-task chain |

## Design Notes

- **Task** uses `mark_complete()` to return the next occurrence for recurring tasks (daily/weekly).
  This keeps recurrence logic self-contained in the Task class.
- **Scheduler** acts as a pure service layer — it holds no task data itself, only references Owner.
- **Owner.get_all_tasks()** returns `(Pet, Task)` tuples so the Scheduler always knows
  which pet a task belongs to (required for conflict detection and filtering).
