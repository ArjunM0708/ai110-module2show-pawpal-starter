# PawPal+ UML Class Diagram

```mermaid
classDiagram
    class scheduler_module {
        <<module>>
        +dict PRIORITY_ORDER
        +int DAY_START_HOUR
        +_minutes_to_time(minutes_offset) str
    }

    class PetTask {
        +str title
        +int duration_minutes
        +str priority
        +str notes
        +is_schedulable() bool
    }

    class Pet {
        +str name
        +str species
        +int age
        +list~str~ special_needs
    }

    class Owner {
        +str name
        +int available_minutes
        +list~str~ preferences
        +Pet pet
        +list~PetTask~ tasks
        +add_task(task: PetTask)
        +remove_task(title: str)
    }

    class ScheduledTask {
        +PetTask task
        +int start_minute
        +str reason
    }

    class DailyPlan {
        +list~ScheduledTask~ scheduled_tasks
        +int total_duration
        +list~str~ skipped_titles
        +explain() str
    }

    class Scheduler {
        +Owner owner
        +generate_plan() DailyPlan
        -_rank_tasks(tasks: list) list
        -_fits_in_time(task: PetTask, remaining_minutes: int) bool
    }

    Owner "1" --> "1" Pet : owns
    Owner "1" --> "0..*" PetTask : manages
    Scheduler "1" --> "1" Owner : uses
    Scheduler ..> DailyPlan : creates
    DailyPlan "1" --> "0..*" ScheduledTask : contains
    ScheduledTask "1" --> "1" PetTask : wraps
    PetTask ..> scheduler_module : references PRIORITY_ORDER
    DailyPlan ..> scheduler_module : uses _minutes_to_time
```

## Changes from original draft

- `scheduler_module` added — captures the module-level `PRIORITY_ORDER` dict, `DAY_START_HOUR` constant, and `_minutes_to_time()` helper that live outside any class
- `DailyPlan.total_duration` is computed in `__init__` from `scheduled_tasks`, not set externally
- `PetTask` and `DailyPlan` both carry a dashed dependency to `scheduler_module` reflecting their runtime use of its contents
