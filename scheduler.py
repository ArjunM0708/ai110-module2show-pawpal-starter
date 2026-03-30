PRIORITY_ORDER = {"high": 3, "medium": 2, "low": 1}  # used for sorting tasks by urgency

DAY_START_HOUR = 8  # schedule begins at 8:00 AM


def _minutes_to_time(minutes_offset):
    # converts a minute offset from DAY_START_HOUR into a readable 12-hour time string
    total = DAY_START_HOUR * 60 + minutes_offset
    h, m = divmod(total, 60)
    period = "AM" if h < 12 else "PM"
    h12 = h % 12 or 12
    return f"{h12}:{m:02d} {period}"


class PetTask:
    def __init__(self, title, duration_minutes, priority, notes=""):
        self.title = title
        self.duration_minutes = duration_minutes
        self.priority = priority  # "low", "medium", "high"
        self.notes = notes

    def is_schedulable(self):
        # rejects tasks with no duration or an unrecognized priority value
        return self.duration_minutes > 0 and self.priority in PRIORITY_ORDER


class Pet:
    def __init__(self, name, species, age=None, special_needs=None):
        self.name = name
        self.species = species
        self.age = age
        self.special_needs = special_needs or []  # avoids mutable default argument pitfall


class Owner:
    def __init__(self, name, available_minutes, preferences=None):
        self.name = name
        self.available_minutes = available_minutes  # time budget for the scheduler
        self.preferences = preferences or []
        self.pet = None
        self.tasks = []

    def add_task(self, task):
        self.tasks.append(task)

    def remove_task(self, title):
        # rebuilds the list without the matching task — avoids index errors
        self.tasks = [t for t in self.tasks if t.title != title]


class ScheduledTask:
    def __init__(self, task, start_minute, reason):
        self.task = task
        self.start_minute = start_minute  # minutes elapsed since DAY_START_HOUR
        self.reason = reason              # human-readable explanation for why this task was chosen


class DailyPlan:
    def __init__(self, scheduled_tasks, skipped_titles):
        self.scheduled_tasks = scheduled_tasks
        self.total_duration = sum(st.task.duration_minutes for st in scheduled_tasks)  # computed from scheduled tasks
        self.skipped_titles = skipped_titles  # tasks that didn't fit in the time budget

    def explain(self):
        # formats each scheduled task with its start time and reason, then lists skipped tasks
        lines = []
        for st in self.scheduled_tasks:
            time_str = _minutes_to_time(st.start_minute)
            lines.append(
                f"{time_str} — {st.task.title} ({st.task.duration_minutes} min) | {st.reason}"
            )
        if self.skipped_titles:
            lines.append("\nSkipped tasks (not enough time):")
            for title in self.skipped_titles:
                lines.append(f"  • {title}")
        return "\n".join(lines)


class Scheduler:
    def __init__(self, owner):
        self.owner = owner

    def generate_plan(self):
        # greedy fit: rank by priority, schedule each task that fits, skip the rest
        ranked = self._rank_tasks(self.owner.tasks)
        remaining = self.owner.available_minutes
        start_minute = 0
        scheduled = []
        skipped = []

        for task in ranked:
            if not task.is_schedulable():
                skipped.append(task.title)
                continue
            if self._fits_in_time(task, remaining):
                reason = f"Priority: {task.priority}"
                scheduled.append(ScheduledTask(task, start_minute, reason))
                start_minute += task.duration_minutes  # advance the clock
                remaining -= task.duration_minutes     # reduce the time budget
            else:
                skipped.append(task.title)

        return DailyPlan(scheduled, skipped)

    def _rank_tasks(self, tasks):
        # sorts tasks highest to lowest priority using PRIORITY_ORDER weights
        return sorted(tasks, key=lambda t: PRIORITY_ORDER.get(t.priority, 0), reverse=True)

    def _fits_in_time(self, task, remaining_minutes):
        # true if the task duration fits within the remaining time budget
        return task.duration_minutes <= remaining_minutes
