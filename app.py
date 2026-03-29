"""
app.py — PawPal+ Streamlit UI
Connects the backend logic layer (pawpal_system.py) to an interactive web interface.
Run: streamlit run app.py
"""

import streamlit as st
from datetime import date
from pawpal_system import Task, Pet, Owner, Scheduler

# ── Page config ───────────────────────────────────────────────
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session state: initialise Owner and Scheduler once ────────
if "owner" not in st.session_state:
    st.session_state.owner = None

if "scheduler" not in st.session_state:
    st.session_state.scheduler = None


# ── Helper to rebuild scheduler from current owner ───────────
def get_scheduler() -> Scheduler:
    """Return (or create) a Scheduler for the current owner."""
    return Scheduler(st.session_state.owner)


# ═══════════════════════════════════════════════════════════════
# SIDEBAR — Owner & Pet Setup
# ═══════════════════════════════════════════════════════════════
with st.sidebar:
    st.header("🏠 Owner Setup")

    with st.form("owner_form"):
        owner_name = st.text_input("Your name", value="Alex")
        owner_email = st.text_input("Email (optional)", value="")
        submitted_owner = st.form_submit_button("Set Owner")

    if submitted_owner and owner_name.strip():
        st.session_state.owner = Owner(owner_name.strip(), owner_email.strip())
        st.session_state.scheduler = get_scheduler()
        st.success(f"Owner set: {owner_name}")

    st.divider()

    # ── Add a Pet ──────────────────────────────────────────────
    st.header("🐾 Add a Pet")
    if st.session_state.owner is None:
        st.info("Set your name above first.")
    else:
        with st.form("pet_form"):
            pet_name = st.text_input("Pet name", value="Buddy")
            species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
            breed = st.text_input("Breed (optional)", value="")
            submitted_pet = st.form_submit_button("Add Pet")

        if submitted_pet and pet_name.strip():
            new_pet = Pet(pet_name.strip(), species, breed.strip())
            st.session_state.owner.add_pet(new_pet)
            st.success(f"Added {pet_name} the {species}!")

        # Show current pets
        if st.session_state.owner.pets:
            st.subheader("Your Pets")
            for pet in st.session_state.owner.pets:
                st.write(f"- **{pet.name}** ({pet.species})"
                         + (f" — {pet.breed}" if pet.breed else ""))


# ═══════════════════════════════════════════════════════════════
# MAIN AREA
# ═══════════════════════════════════════════════════════════════
st.title("🐾 PawPal+ — Smart Pet Care Scheduler")
st.caption("Design, schedule, and track your pet's daily care tasks.")

if st.session_state.owner is None:
    st.info("👈 Start by entering your name in the sidebar.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler: Scheduler = get_scheduler()

st.markdown(f"**Welcome, {owner.name}!** You have **{len(owner.pets)}** pet(s) registered.")

# ── Warn if no pets yet ───────────────────────────────────────
if not owner.pets:
    st.warning("Add at least one pet in the sidebar to get started.")
    st.stop()

st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 1 — Add a Task
# ═══════════════════════════════════════════════════════════════
st.subheader("📋 Schedule a Task")

pet_names = [pet.name for pet in owner.pets]

with st.form("task_form"):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        selected_pet_name = st.selectbox("For which pet?", pet_names)
    with col2:
        task_description = st.text_input("Task description", value="Morning walk")
    with col3:
        task_time = st.text_input("Time (HH:MM)", value="07:30")
    with col4:
        frequency = st.selectbox("Frequency", ["daily", "weekly", "once"])

    task_date = st.date_input("Due date", value=date.today())
    submitted_task = st.form_submit_button("Add Task")

if submitted_task:
    # Validate time format
    try:
        h, m = task_time.strip().split(":")
        assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
        valid_time = True
    except Exception:
        valid_time = False

    if not task_description.strip():
        st.error("Task description cannot be empty.")
    elif not valid_time:
        st.error("Time must be in HH:MM format (e.g. 07:30).")
    else:
        target_pet = next(p for p in owner.pets if p.name == selected_pet_name)
        new_task = Task(
            description=task_description.strip(),
            time=task_time.strip(),
            frequency=frequency,
            due_date=task_date,
        )
        target_pet.add_task(new_task)
        st.success(f"Task '{task_description}' added for {selected_pet_name}!")

st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 2 — Conflict Warnings
# ═══════════════════════════════════════════════════════════════
conflicts = scheduler.detect_conflicts()
if conflicts:
    st.subheader("⚠️ Schedule Conflicts Detected")
    for conflict in conflicts:
        st.warning(conflict)
    st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 3 — Today's Schedule
# ═══════════════════════════════════════════════════════════════
st.subheader("📅 Today's Schedule (Sorted by Time)")

todays_tasks = scheduler.get_todays_schedule()

if not todays_tasks:
    st.info("No pending tasks for today. Add tasks above!")
else:
    rows = []
    for pet, task in todays_tasks:
        rows.append({
            "Time": task.time,
            "Pet": pet.name,
            "Task": task.description,
            "Frequency": task.frequency,
            "Due": str(task.due_date),
            "Status": "Done" if task.completed else "Pending",
        })
    st.table(rows)

st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 4 — Filter & View
# ═══════════════════════════════════════════════════════════════
st.subheader("🔍 Filter Tasks")

col_a, col_b = st.columns(2)
with col_a:
    filter_pet = st.selectbox("Filter by pet", ["All"] + pet_names)
with col_b:
    filter_status = st.selectbox("Filter by status", ["All", "Pending", "Done"])

# Build filters
pet_filter = None if filter_pet == "All" else filter_pet
completed_filter = None
if filter_status == "Pending":
    completed_filter = False
elif filter_status == "Done":
    completed_filter = True

filtered = scheduler.filter_tasks(completed=completed_filter, pet_name=pet_filter)

if not filtered:
    st.info("No tasks match your filter.")
else:
    filter_rows = []
    for pet, task in filtered:
        filter_rows.append({
            "Time": task.time,
            "Pet": pet.name,
            "Task": task.description,
            "Frequency": task.frequency,
            "Due": str(task.due_date),
            "Status": "Done" if task.completed else "Pending",
        })
    st.table(filter_rows)

st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 5 — Mark Tasks Complete
# ═══════════════════════════════════════════════════════════════
st.subheader("✅ Mark a Task Complete")

pending_tasks = scheduler.filter_tasks(completed=False)
if not pending_tasks:
    st.info("No pending tasks to mark complete.")
else:
    task_options = {
        f"{pet.name} — {task.description} @ {task.time} ({task.frequency})": (pet, task)
        for pet, task in pending_tasks
    }
    selected_label = st.selectbox("Choose a task to complete", list(task_options.keys()))

    if st.button("Mark as Complete"):
        target_pet, target_task = task_options[selected_label]
        scheduler.mark_task_complete(target_pet, target_task)
        if target_task.frequency in ("daily", "weekly"):
            st.success(
                f"'{target_task.description}' marked done! "
                f"Next occurrence auto-scheduled for {target_pet.tasks[-1].due_date}."
            )
        else:
            st.success(f"'{target_task.description}' marked complete!")
        st.rerun()

st.divider()

# ═══════════════════════════════════════════════════════════════
# SECTION 6 — Full Schedule (all pets, all tasks)
# ═══════════════════════════════════════════════════════════════
st.subheader("📊 Full Schedule — All Tasks")

all_sorted = scheduler.sort_by_time()
if not all_sorted:
    st.info("No tasks yet. Add some above!")
else:
    all_rows = []
    for pet, task in all_sorted:
        all_rows.append({
            "Time": task.time,
            "Pet": pet.name,
            "Task": task.description,
            "Frequency": task.frequency,
            "Due": str(task.due_date),
            "Status": "Done" if task.completed else "Pending",
        })
    st.table(all_rows)

st.caption("PawPal+ — Built with Python OOP + Streamlit | AI110 Module 2")
