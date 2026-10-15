
import json
from datetime import datetime, date
from pathlib import Path


class Task:
    """Represents a task in the virtual assistant."""

    def __init__(
        self,
        task_id,
        title,
        description="",
        priority="Medium",
        due_date="",
        completed=False
    ):
        self.task_id = task_id
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.completed = completed
        self.created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    def to_dict(self):
        """Convert a task into a dictionary for JSON storage."""
        return {
            "task_id": self.task_id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "completed": self.completed,
            "created_at": self.created_at
        }

    @classmethod
    def from_dict(cls, data):
        """Create a task from saved JSON data."""
        task = cls(
            task_id=data["task_id"],
            title=data["title"],
            description=data.get("description", ""),
            priority=data.get("priority", "Medium"),
            due_date=data.get("due_date", ""),
            completed=data.get("completed", False)
        )
        task.created_at = data.get("created_at", "")
        return task


class PersonalizedVirtualAssistant:
    """Manages tasks and saves them in a JSON file."""

    DATA_FILE = Path(__file__).with_name("tasks.json")
    PRIORITIES = ("High", "Medium", "Low")

    def __init__(self):
        self.tasks = []
        self.load_tasks()

    def load_tasks(self):
        """Load saved tasks when the program starts."""
        if not self.DATA_FILE.exists():
            return

        try:
            with self.DATA_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)

            self.tasks = [
                Task.from_dict(item) for item in data
            ]

        except (json.JSONDecodeError, OSError, KeyError, TypeError) as error:
            print(f"Could not load saved tasks: {error}")
            print("Starting with an empty task list.")

    def save_tasks(self):
        """Save all tasks to JSON storage."""
        try:
            with self.DATA_FILE.open("w", encoding="utf-8") as file:
                json.dump(
                    [task.to_dict() for task in self.tasks],
                    file,
                    indent=4
                )
            return True

        except OSError as error:
            print(f"Error saving tasks: {error}")
            return False

    def next_task_id(self):
        """Generate a unique task ID."""
        return max(
            (task.task_id for task in self.tasks),
            default=0
        ) + 1

    @staticmethod
    def read_due_date():
        """Accept a date in YYYY-MM-DD format or no date."""
        while True:
            value = input(
                "Due date (YYYY-MM-DD, or press Enter to skip): "
            ).strip()

            if not value:
                return ""

            try:
                date.fromisoformat(value)
                return value
            except ValueError:
                print("Invalid date. Example: 2026-12-31")

    def add_task(self):
        """Create and save a new task."""
        print("\n--- Create New Task ---")
        title = input("Task title: ").strip()

        if not title:
            print("Task title cannot be empty.")
            return

        description = input("Description: ").strip()

        print("Priority options: High, Medium, Low")
        while True:
            priority = input("Choose priority: ").strip().capitalize()
            if priority in self.PRIORITIES:
                break
            print("Please enter High, Medium, or Low.")

        due_date = self.read_due_date()

        task = Task(
            task_id=self.next_task_id(),
            title=title,
            description=description,
            priority=priority,
            due_date=due_date
        )

        self.tasks.append(task)

        if self.save_tasks():
            print(f"Task #{task.task_id} created successfully!")

    @staticmethod
    def display_task(task):
        """Display a task and its current status."""
        status = "Completed" if task.completed else "Pending"
        due = task.due_date or "Not set"

        if task.due_date and not task.completed:
            if date.fromisoformat(task.due_date) < date.today():
                status += " - OVERDUE"

        print("-" * 45)
        print(f"ID: {task.task_id}")
        print(f"Title: {task.title}")
        print(f"Description: {task.description or 'None'}")
        print(f"Priority: {task.priority}")
        print(f"Due date: {due}")
        print(f"Status: {status}")
        print(f"Created: {task.created_at}")

    def list_tasks(self):
        """Display all tasks."""
        print("\n--- All Tasks ---")

        if not self.tasks:
            print("No tasks found. Create your first task!")
            return

        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        ordered_tasks = sorted(
            self.tasks,
            key=lambda task: (
                task.completed,
                priority_order.get(task.priority, 1),
                task.due_date or "9999-12-31"
            )
        )

        for task in ordered_tasks:
            self.display_task(task)

        print("-" * 45)

    def search_tasks(self):
        """Search tasks by title or description."""
        keyword = input(
            "\nEnter a title or description keyword: "
        ).strip().lower()

        if not keyword:
            print("Please enter a search keyword.")
            return

        matches = [
            task for task in self.tasks
            if keyword in task.title.lower()
            or keyword in task.description.lower()
        ]

        if not matches:
            print("No matching tasks found.")
            return

        print(f"\nFound {len(matches)} matching task(s):")
        for task in matches:
            self.display_task(task)

    def complete_task(self):
        """Mark a pending task as completed."""
        try:
            task_id = int(input("\nEnter task ID to complete: "))
        except ValueError:
            print("Please enter a valid numeric task ID.")
            return

        for task in self.tasks:
            if task.task_id == task_id:
                if task.completed:
                    print("This task is already completed.")
                    return

                task.completed = True

                if self.save_tasks():
                    print(f"Task #{task_id} marked as completed!")
                return

        print("Task ID not found.")

    def delete_task(self):
        """Delete a task by its ID."""
        try:
            task_id = int(input("\nEnter task ID to delete: "))
        except ValueError:
            print("Please enter a valid numeric task ID.")
            return

        for task in self.tasks:
            if task.task_id == task_id:
                confirm = input(
                    f"Delete '{task.title}'? (yes/no): "
                ).strip().lower()

                if confirm != "yes":
                    print("Deletion cancelled.")
                    return

                self.tasks.remove(task)

                if self.save_tasks():
                    print("Task deleted successfully.")
                return

        print("Task ID not found.")

    def show_summary(self):
        """Show task completion statistics."""
        total = len(self.tasks)
        completed = sum(task.completed for task in self.tasks)
        pending = total - completed
        overdue = sum(
            not task.completed
            and bool(task.due_date)
            and date.fromisoformat(task.due_date) < date.today()
            for task in self.tasks
        )

        percentage = (completed / total * 100) if total else 0

        print("\n--- Task Summary ---")
        print(f"Total tasks: {total}")
        print(f"Completed: {completed}")
        print(f"Pending: {pending}")
        print(f"Overdue: {overdue}")
        print(f"Completion rate: {percentage:.1f}%")

    def run(self):
        """Display the menu and handle user choices."""
        print("=" * 45)
        print(" PERSONALIZED VIRTUAL ASSISTANT")
        print(" Task Management System")
        print("=" * 45)

        while True:
            print("\n1. Create a task")
            print("2. View all tasks")
            print("3. Search tasks")
            print("4. Mark task as completed")
            print("5. Delete a task")
            print("6. View task summary")
            print("7. Exit")

            choice = input("\nEnter your choice (1-7): ").strip()

            if choice == "1":
                self.add_task()
            elif choice == "2":
                self.list_tasks()
            elif choice == "3":
                self.search_tasks()
            elif choice == "4":
                self.complete_task()
            elif choice == "5":
                self.delete_task()
            elif choice == "6":
                self.show_summary()
            elif choice == "7":
                print("Thank you for using the assistant. Goodbye!")
                break
            else:
                print("Invalid choice. Please select a number from 1 to 7.")


if __name__ == "__main__":
    assistant = PersonalizedVirtualAssistant()
    try:
        assistant.run()
    except (KeyboardInterrupt, EOFError):
        print("\nAssistant closed. Your saved tasks remain available.")
