import streamlit as st
from scheduler import PetTask, Pet, Owner, Scheduler  # import backend classes

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Owner + Pet Info ---

st.subheader("Owner & Pet")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_minutes = st.number_input(
        "Time available today (minutes)", min_value=10, max_value=480, value=120, step=10
    )  # time budget passed to the scheduler
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])

st.divider()

# --- Task Management ---

st.subheader("Tasks")

if "tasks" not in st.session_state:
    st.session_state.tasks = []  # persists task list across Streamlit reruns

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

notes = st.text_input("Notes (optional)", value="")  # passed through to PetTask.notes

col_add, col_clear = st.columns([1, 5])
with col_add:
    if st.button("Add task"):
        st.session_state.tasks.append(
            {
                "title": task_title,
                "duration_minutes": int(duration),
                "priority": priority,
                "notes": notes,
            }
        )
with col_clear:
    if st.button("Clear all tasks"):
        st.session_state.tasks = []  # resets the task list without a page reload

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)

    remove_title = st.selectbox(
        "Remove a task", options=[t["title"] for t in st.session_state.tasks]
    )
    if st.button("Remove selected task"):
        st.session_state.tasks = [
            t for t in st.session_state.tasks if t["title"] != remove_title
        ]
        st.rerun()  # re-renders the page so the table reflects the removal immediately
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule Generation ---

st.subheader("Generate Schedule")

if st.button("Generate schedule", type="primary"):
    if not st.session_state.tasks:
        st.warning("Add at least one task before generating a schedule.")
    else:
        # build domain objects from UI inputs
        owner = Owner(name=owner_name, available_minutes=int(available_minutes))
        owner.pet = Pet(name=pet_name, species=species)

        # convert each UI task dict into a PetTask object
        for t in st.session_state.tasks:
            owner.add_task(
                PetTask(
                    title=t["title"],
                    duration_minutes=t["duration_minutes"],
                    priority=t["priority"],
                    notes=t.get("notes", ""),
                )
            )

        plan = Scheduler(owner).generate_plan()  # run the greedy scheduler

        # --- Results ---

        # summary banner: shows how much of the time budget was used
        st.success(
            f"Schedule generated for **{owner_name}** and **{pet_name}** "
            f"— {plan.total_duration} of {available_minutes} minutes used."
        )

        if plan.scheduled_tasks:
            st.markdown("### Scheduled Tasks")
            for st_task in plan.scheduled_tasks:
                with st.container(border=True):  # each task gets its own card
                    col_a, col_b = st.columns([3, 1])
                    with col_a:
                        st.markdown(f"**{st_task.task.title}**")
                        st.caption(st_task.reason)        # shows priority explanation
                        if st_task.task.notes:
                            st.caption(f"Note: {st_task.task.notes}")
                    with col_b:
                        st.metric("Duration", f"{st_task.task.duration_minutes} min")

        if plan.skipped_titles:
            st.markdown("### Skipped Tasks")
            st.caption("These tasks didn't fit within the available time.")
            for title in plan.skipped_titles:
                st.markdown(f"- {title}")

        st.divider()
        st.markdown("### Full Plan")
        st.code(plan.explain(), language=None)  # plain-text schedule with times and reasons
