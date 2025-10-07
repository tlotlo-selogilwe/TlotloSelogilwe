#Import necesary libraries
import os
import datetime

"""
task_manager.py
Refactored and completed to meet HyperionDev practical task requirements.
"""

from pathlib import Path
import datetime
import sys

# Files
USER_FILE = Path("user.txt")
TASK_FILE = Path("tasks.txt")
TASK_OVERVIEW = Path("task_overview.txt")
USER_OVERVIEW = Path("user_overview.txt")

# In-memory users dict: username -> password
users = {}

# ---------------------------
# Utility / I/O / Validation
# ---------------------------

def load_users():
    """Load users from user.txt into the users dict.
    Expected format per line: username, password   (note the comma and space is allowed)
    """
    users.clear()
    if not USER_FILE.exists():
        # If no file exists, create an empty one so later appends succeed
        USER_FILE.touch()
        return

    with USER_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            if ',' in line:
                username, password = line.split(',', 1)
                users[username.strip().lower()] = password.strip()
            else:
                # skip malformed line
                continue


def save_new_user(username: str, password: str):
    """Append a new user to user.txt in the required format: username, password"""
    # ensure file exists
    USER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USER_FILE.open("a", encoding="utf-8") as f:
        f.write(f"\n{username}, {password}")


def validate_date(date_str: str) -> bool:
    """Return True if string is YYYY-MM-DD and a real date."""
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def read_tasks():
    """Return list of tasks (each a list of parts). Handles descriptions containing commas by:
       splitting into parts and rejoining middle parts as description.
       Each task expected fields after parsing: [username, title, description, assigned_date, due_date, completed]
    """
    tasks = []
    if not TASK_FILE.exists():
        TASK_FILE.touch()
        return tasks

    with TASK_FILE.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 6:
                # malformed - skip
                continue
            # username = parts[0], title = parts[1], description = parts[2..-4], assigned = -3, due=-2, complete=-1
            username = parts[0]
            title = parts[1]
            # description might have commas, so join parts[2:len(parts)-3]
            description = ','.join(parts[2:-3]) if len(parts) > 6 else parts[2]
            assigned_date = parts[-3]
            due_date = parts[-2]
            completed = parts[-1]
            tasks.append([username, title, description, assigned_date, due_date, completed])
    return tasks


def write_tasks(tasks):
    """Overwrite tasks.txt with the provided tasks list (each element is a list of 6 fields)."""
    TASK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with TASK_FILE.open("w", encoding="utf-8") as f:
        for t in tasks:
            # Ensure we write in the specified format with comma and single space after comma in user file,
            # but tasks file uses comma separators (no enforced extra space needed).
            f.write(f"{t[0]},{t[1]},{t[2]},{t[3]},{t[4]},{t[5]}\n")


# ---------------------------
# Required functionality
# ---------------------------

def reg_user(current_user: str):
    """Register a new user. Only admin can call this (enforced by caller)."""
    print("\n=== Register User ===")
    while True:
        new_username = input("New username: ").strip().lower()
        if not new_username:
            print("Username cannot be empty. Try again.")
            continue
        if new_username in users:
            print("This username already exists. Please choose another.")
            # allow retry
            continue
        new_password = input("New password: ").strip()
        confirm = input("Confirm password: ").strip()
        if new_password != confirm:
            print("Passwords do not match. Try again.")
            continue
        # save
        save_new_user(new_username, new_password)
        # reload users to update in-memory dict
        load_users()
        print(f"User '{new_username}' registered successfully.")
        break


def add_task():
    """Add a task and write it to tasks.txt in the specified format."""
    print("\n=== Add Task ===")
    assigned_to = input("Username of person assigned to: ").strip().lower()
    if assigned_to not in users:
        print("Error: That user does not exist. Please register the user first or assign to an existing user.")
        return
    title = input("Title of task: ").strip()
    description = input("Description of task: ").strip()
    # assigned date is today
    assigned_date = datetime.date.today().strftime("%Y-%m-%d")
    while True:
        due_date = input("Due date (YYYY-MM-DD): ").strip()
        if validate_date(due_date):
            break
        print("Invalid date format. Please use YYYY-MM-DD.")
    completed = "No"
    tasks = read_tasks()
    tasks.append([assigned_to, title, description, assigned_date, due_date, completed])
    write_tasks(tasks)
    print(f"Task '{title}' assigned to {assigned_to}.")


def view_all():
    """Display all tasks in an easy-to-read format."""
    print("\n=== View All Tasks ===")
    tasks = read_tasks()
    if not tasks:
        print("No tasks to show.")
        return
    for i, t in enumerate(tasks, 1):
        username, title, description, assigned_date, due_date, completed = t
        print(f"\nTask {i}:")
        print(f"Assigned to: {username}")
        print(f"Title      : {title}")
        print(f"Description: {description}")
        print(f"Assigned on: {assigned_date}")
        print(f"Due date   : {due_date}")
        print(f"Completed  : {completed}")
        print("-" * 40)


def view_completed():
    """Admin-only: view all completed tasks."""
    print("\n=== View Completed Tasks ===")
    tasks = read_tasks()
    found = False
    for i, t in enumerate(tasks, 1):
        if t[5].strip().lower() == "yes":
            found = True
            username, title, description, assigned_date, due_date, completed = t
            print(f"\nTask {i}:")
            print(f"Assigned to: {username}")
            print(f"Title      : {title}")
            print(f"Description: {description}")
            print(f"Assigned on: {assigned_date}")
            print(f"Due date   : {due_date}")
            print(f"Completed  : {completed}")
            print("-" * 40)
    if not found:
        print("There are no completed tasks.")


def delete_task():
    """Admin-only: delete a specific task by its number in the file listing."""
    print("\n=== Delete Task ===")
    tasks = read_tasks()
    if not tasks:
        print("No tasks to delete.")
        return
    # Display numbered list
    for i, t in enumerate(tasks, 1):
        print(f"{i}. {t[1]} (Assigned to {t[0]}) - Completed: {t[5]}")
    while True:
        sel = input("Enter task number to delete (or -1 to cancel): ").strip()
        if sel == "-1":
            print("Delete cancelled.")
            return
        if not sel.isdigit():
            print("Please enter a valid integer.")
            continue
        idx = int(sel) - 1
        if 0 <= idx < len(tasks):
            removed = tasks.pop(idx)
            write_tasks(tasks)
            print(f"Deleted task '{removed[1]}' assigned to {removed[0]}.")
            return
        else:
            print("That task number does not exist.")


# Optional recursive function as requested
def get_valid_task_number(prompt: str, max_number: int):
    """Recursive helper that returns a valid task number (1..max_number) or -1 to cancel."""
    entry = input(prompt).strip()
    if entry == "-1":
        return -1
    if not entry.isdigit():
        print("Invalid input. Enter a number or -1 to cancel.")
        return get_valid_task_number(prompt, max_number)
    value = int(entry)
    if value < 1 or value > max_number:
        print("Number out of range.")
        return get_valid_task_number(prompt, max_number)
    return value


def view_mine(current_user: str):
    """Allow a user to view and manage their tasks:
       - Display tasks with numbers
       - Allow selection (or -1 to return)
       - Mark as complete OR edit assigned user/due date (only if not completed)
    """
    print(f"\n=== View My Tasks ({current_user}) ===")
    tasks = read_tasks()
    my_indexes = [i for i, t in enumerate(tasks) if t[0].strip().lower() == current_user.lower()]

    if not my_indexes:
        print("You have no tasks assigned.")
        return

    # Show user's tasks numbered 1..N (local indexing)
    for local_idx, global_idx in enumerate(my_indexes, 1):
        t = tasks[global_idx]
        print(f"\nTask {local_idx}:")
        print(f"Title      : {t[1]}")
        print(f"Description: {t[2]}")
        print(f"Assigned on: {t[3]}")
        print(f"Due date   : {t[4]}")
        print(f"Completed  : {t[5]}")
        print("-" * 40)

    # Prompt user to select a task or -1 to return
    sel = get_valid_task_number("Enter the task number to select a task, or -1 to return: ", len(my_indexes))
    if sel == -1:
        return

    selected_global_idx = my_indexes[sel - 1]
    task = tasks[selected_global_idx]

    # If completed, cannot edit
    if task[5].strip().lower() == "yes":
        print("This task is already completed and cannot be edited.")
        # Still allow user to return
        return

    # Offer options
    print("\nWhat would you like to do?")
    print("1 - Mark as complete")
    print("2 - Edit task (username or due date)")
    choice = input("> ").strip()
    if choice == "1":
        tasks[selected_global_idx][5] = "Yes"
        write_tasks(tasks)
        print("Task marked as complete.")
        return
    elif choice == "2":
        # Edit assigned username and/or due date
        new_user = input("Enter new username to assign (leave blank to keep current): ").strip().lower()
        if new_user:
            if new_user not in users:
                print("That user does not exist. Edit cancelled.")
                return
            tasks[selected_global_idx][0] = new_user
        new_due = input("Enter new due date (YYYY-MM-DD) (leave blank to keep current): ").strip()
        if new_due:
            if not validate_date(new_due):
                print("Invalid date format. Edit cancelled.")
                return
            tasks[selected_global_idx][4] = new_due
        write_tasks(tasks)
        print("Task updated successfully.")
        return
    else:
        print("Invalid option selected.")


# ---------------------------
# Reports and statistics
# ---------------------------

def generate_reports():
    """Create task_overview.txt and user_overview.txt with the required statistics."""
    print("\n=== Generating Reports ===")
    tasks = read_tasks()
    total_tasks = len(tasks)
    completed_tasks = [t for t in tasks if t[5].strip().lower() == "yes"]
    incomplete_tasks = [t for t in tasks if t[5].strip().lower() != "yes"]

    # Overdue: incomplete and due_date < today
    today = datetime.date.today()
    overdue = []
    for t in incomplete_tasks:
        due = t[4].strip()
        if validate_date(due):
            due_date = datetime.datetime.strptime(due, "%Y-%m-%d").date()
            if due_date < today:
                overdue.append(t)

    # Task overview content
    percent_incomplete = (len(incomplete_tasks) / total_tasks * 100) if total_tasks else 0.0
    percent_overdue = (len(overdue) / total_tasks * 100) if total_tasks else 0.0

    TASK_OVERVIEW.parent.mkdir(parents=True, exist_ok=True)
    with TASK_OVERVIEW.open("w", encoding="utf-8") as f:
        f.write(f"Total tasks: {total_tasks}\n")
        f.write(f"Total completed tasks: {len(completed_tasks)}\n")
        f.write(f"Total uncompleted tasks: {len(incomplete_tasks)}\n")
        f.write(f"Total overdue tasks (uncompleted & past due date): {len(overdue)}\n")
        f.write(f"Percentage of tasks incomplete: {percent_incomplete:.2f}%\n")
        f.write(f"Percentage of tasks overdue: {percent_overdue:.2f}%\n")

    # User overview
    total_users = len(users)
    USER_OVERVIEW.parent.mkdir(parents=True, exist_ok=True)
    with USER_OVERVIEW.open("w", encoding="utf-8") as f:
        f.write(f"Total users: {total_users}\n")
        f.write(f"Total tasks: {total_tasks}\n\n")
        # For each user provide required breakdown
        for u in sorted(users.keys()):
            user_tasks = [t for t in tasks if t[0].strip().lower() == u.lower()]
            num_user_tasks = len(user_tasks)
            pct_of_total = (num_user_tasks / total_tasks * 100) if total_tasks else 0.0
            user_completed = [t for t in user_tasks if t[5].strip().lower() == "yes"]
            num_completed = len(user_completed)
            pct_completed_of_user = (num_completed / num_user_tasks * 100) if num_user_tasks else 0.0
            user_incomplete = [t for t in user_tasks if t[5].strip().lower() != "yes"]
            num_incomplete = len(user_incomplete)
            pct_incomplete_of_user = (num_incomplete / num_user_tasks * 100) if num_user_tasks else 0.0
            # overdue for this user
            user_overdue = 0
            for t in user_incomplete:
                due = t[4].strip()
                if validate_date(due) and datetime.datetime.strptime(due, "%Y-%m-%d").date() < today:
                    user_overdue += 1
            pct_overdue_of_user = (user_overdue / num_user_tasks * 100) if num_user_tasks else 0.0

            f.write(f"User: {u}\n")
            f.write(f"  Total tasks assigned: {num_user_tasks}\n")
            f.write(f"  Percentage of total tasks assigned to user: {pct_of_total:.2f}%\n")
            f.write(f"  Percentage of user's tasks completed: {pct_completed_of_user:.2f}%\n")
            f.write(f"  Percentage of user's tasks to be completed: {pct_incomplete_of_user:.2f}%\n")
            f.write(f"  Percentage of user's tasks overdue and not complete: {pct_overdue_of_user:.2f}%\n\n")

    print("Reports generated: task_overview.txt and user_overview.txt")


def display_statistics():
    """Display the contents of the overview reports. If they do not exist, generate them first."""
    if not TASK_OVERVIEW.exists() or not USER_OVERVIEW.exists():
        print("Reports not found. Generating now...")
        generate_reports()

    print("\n=== Task Overview ===")
    print(TASK_OVERVIEW.read_text())

    print("\n=== User Overview ===")
    print(USER_OVERVIEW.read_text())


# ---------------------------
# Main program loop
# ---------------------------

def main():
    load_users()
    print("Welcome to the Task Manager!\n")

    # Login
    current_user = None
    while True:
        username = input("Username: ").strip().lower()
        password = input("Password: ").strip()
        if username in users and users[username] == password:
            current_user = username
            print(f"\nLogin successful. Welcome, {current_user}!")
            break
        else:
            print("Invalid username or password. Please try again.")

    # Menu loop
    while True:
        is_admin = current_user == "admin"
        print("\nPlease select one of the following options:")
        if is_admin:
            print("r  - register user")
        print("a  - add task")
        print("va - view all tasks")
        print("vm - view my tasks")
        if is_admin:
            print("vc - view completed tasks")
            print("del - delete a task")
            print("ds - display statistics")
            print("gr - generate reports")
        print("e  - exit")

        choice = input("> ").strip().lower()

        if choice == "r" and is_admin:
            reg_user(current_user)
        elif choice == "a":
            add_task()
        elif choice == "va":
            view_all()
        elif choice == "vm":
            view_mine(current_user)
        elif choice == "vc" and is_admin:
            view_completed()
        elif choice == "del" and is_admin:
            delete_task()
        elif choice == "gr" and is_admin:
            generate_reports()
        elif choice == "ds" and is_admin:
            display_statistics()
        elif choice == "e":
            print("Goodbye!")
            sys.exit(0)
        else:
            print("Invalid option. Please select a valid menu item.")


if __name__ == "__main__":
    main()
