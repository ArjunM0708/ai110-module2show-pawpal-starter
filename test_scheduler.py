import pytest
from scheduler import PetTask, Pet, Owner, Scheduler, DailyPlan


# --- Helpers ---

def make_owner(minutes=120):
    owner = Owner(name="Jordan", available_minutes=minutes)
    owner.pet = Pet(name="Mochi", species="dog")
    return owner


# --- PetTask ---

def test_task_is_schedulable_valid():
    task = PetTask("Walk", 20, "high")
    assert task.is_schedulable() is True


def test_task_is_schedulable_zero_duration():
    task = PetTask("Walk", 0, "high")
    assert task.is_schedulable() is False


def test_task_is_schedulable_invalid_priority():
    task = PetTask("Walk", 20, "urgent")
    assert task.is_schedulable() is False


# --- Owner ---

def test_owner_add_task():
    owner = make_owner()
    task = PetTask("Feed", 10, "high")
    owner.add_task(task)
    assert len(owner.tasks) == 1
    assert owner.tasks[0].title == "Feed"


def test_owner_remove_task():
    owner = make_owner()
    owner.add_task(PetTask("Feed", 10, "high"))
    owner.add_task(PetTask("Walk", 20, "medium"))
    owner.remove_task("Feed")
    assert len(owner.tasks) == 1
    assert owner.tasks[0].title == "Walk"


def test_owner_remove_task_not_found():
    owner = make_owner()
    owner.add_task(PetTask("Feed", 10, "high"))
    owner.remove_task("Groom")  # should not raise
    assert len(owner.tasks) == 1


# --- Scheduler: ranking ---

def test_rank_puts_high_before_low():
    owner = make_owner()
    owner.add_task(PetTask("Low task", 10, "low"))
    owner.add_task(PetTask("High task", 10, "high"))
    owner.add_task(PetTask("Medium task", 10, "medium"))
    scheduler = Scheduler(owner)
    ranked = scheduler._rank_tasks(owner.tasks)
    assert ranked[0].priority == "high"
    assert ranked[1].priority == "medium"
    assert ranked[2].priority == "low"


# --- Scheduler: fits in time ---

def test_fits_in_time_true():
    scheduler = Scheduler(make_owner())
    task = PetTask("Walk", 20, "high")
    assert scheduler._fits_in_time(task, 30) is True


def test_fits_in_time_exact():
    scheduler = Scheduler(make_owner())
    task = PetTask("Walk", 30, "high")
    assert scheduler._fits_in_time(task, 30) is True


def test_fits_in_time_false():
    scheduler = Scheduler(make_owner())
    task = PetTask("Walk", 40, "high")
    assert scheduler._fits_in_time(task, 30) is False


# --- Scheduler: generate_plan ---

def test_plan_respects_time_budget():
    owner = make_owner(minutes=30)
    owner.add_task(PetTask("Walk", 20, "high"))
    owner.add_task(PetTask("Groom", 60, "medium"))
    plan = Scheduler(owner).generate_plan()
    assert plan.total_duration <= 30


def test_plan_schedules_high_priority_first():
    owner = make_owner(minutes=30)
    owner.add_task(PetTask("Low task", 10, "low"))
    owner.add_task(PetTask("High task", 10, "high"))
    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks[0].task.title == "High task"


def test_plan_skips_tasks_that_dont_fit():
    owner = make_owner(minutes=25)
    owner.add_task(PetTask("Walk", 20, "high"))
    owner.add_task(PetTask("Groom", 60, "medium"))
    plan = Scheduler(owner).generate_plan()
    assert "Groom" in plan.skipped_titles


def test_plan_fits_multiple_small_tasks():
    owner = make_owner(minutes=60)
    owner.add_task(PetTask("Feed", 10, "high"))
    owner.add_task(PetTask("Walk", 20, "high"))
    owner.add_task(PetTask("Play", 15, "medium"))
    plan = Scheduler(owner).generate_plan()
    assert len(plan.scheduled_tasks) == 3
    assert plan.total_duration == 45


def test_plan_skips_unschedulable_task():
    owner = make_owner(minutes=60)
    owner.add_task(PetTask("Bad task", 0, "high"))
    owner.add_task(PetTask("Walk", 20, "medium"))
    plan = Scheduler(owner).generate_plan()
    scheduled_titles = [st.task.title for st in plan.scheduled_tasks]
    assert "Bad task" not in scheduled_titles
    assert "Walk" in scheduled_titles


def test_plan_empty_tasks():
    owner = make_owner(minutes=60)
    plan = Scheduler(owner).generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.total_duration == 0


# --- DailyPlan ---

def test_plan_total_duration_is_sum_of_scheduled():
    owner = make_owner(minutes=120)
    owner.add_task(PetTask("Feed", 10, "high"))
    owner.add_task(PetTask("Walk", 30, "high"))
    plan = Scheduler(owner).generate_plan()
    assert plan.total_duration == 40


def test_explain_contains_task_titles():
    owner = make_owner(minutes=60)
    owner.add_task(PetTask("Walk", 20, "high"))
    plan = Scheduler(owner).generate_plan()
    output = plan.explain()
    assert "Walk" in output


def test_explain_mentions_skipped_tasks():
    owner = make_owner(minutes=10)
    owner.add_task(PetTask("Walk", 20, "high"))
    plan = Scheduler(owner).generate_plan()
    output = plan.explain()
    assert "Walk" in output
    assert "Skipped" in output
