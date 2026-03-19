"""
TaskMate AI - Database Layer
SQLite database for reminders, tasks, conversations, and users.
"""

import sqlite3
import json
from datetime import datetime
from typing import Optional
import os


class Database:
    """SQLite database manager for TaskMate AI."""

    def __init__(self, db_path: str = "taskmate.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        return conn

    def init_db(self):
        """Initialize all database tables."""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_number TEXT UNIQUE NOT NULL,
                name TEXT DEFAULT '',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                preferences TEXT DEFAULT '{}'
            )
        """)

        # Reminders table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                remind_at TIMESTAMP NOT NULL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_phone) REFERENCES users(phone_number)
            )
        """)

        # Tasks table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT DEFAULT '',
                priority TEXT DEFAULT 'medium',
                status TEXT DEFAULT 'pending',
                due_date TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                FOREIGN KEY (user_phone) REFERENCES users(phone_number)
            )
        """)

        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                intent TEXT DEFAULT '',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_phone) REFERENCES users(phone_number)
            )
        """)

        # Agent activity log
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_phone TEXT NOT NULL,
                action TEXT NOT NULL,
                details TEXT DEFAULT '',
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # ─── User Operations ─────────────────────────────────────────

    def get_all_users(self) -> list:
        """Get all users ordered by last active."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users ORDER BY last_active DESC")
        users = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return users

    def get_or_create_user(self, phone_number: str) -> dict:
        """Get existing user or create a new one."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
        user = cursor.fetchone()

        if not user:
            cursor.execute(
                "INSERT INTO users (phone_number) VALUES (?)",
                (phone_number,)
            )
            conn.commit()
            cursor.execute("SELECT * FROM users WHERE phone_number = ?", (phone_number,))
            user = cursor.fetchone()

        # Update last active
        cursor.execute(
            "UPDATE users SET last_active = ? WHERE phone_number = ?",
            (datetime.now().isoformat(), phone_number)
        )
        conn.commit()
        conn.close()
        return dict(user)

    # ─── Reminder Operations ─────────────────────────────────────

    def create_reminder(self, user_phone: str, title: str, remind_at: str, description: str = "") -> dict:
        """Create a new reminder."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO reminders (user_phone, title, description, remind_at)
               VALUES (?, ?, ?, ?)""",
            (user_phone, title, description, remind_at)
        )
        conn.commit()
        reminder_id = cursor.lastrowid

        cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        reminder = dict(cursor.fetchone())
        conn.close()

        self.log_action(user_phone, "reminder_created", f"Reminder: {title} at {remind_at}")
        return reminder

    def get_reminders(self, user_phone: str = None, status: str = None) -> list:
        """Get reminders, optionally filtered by user and status."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM reminders WHERE 1=1"
        params = []

        if user_phone:
            query += " AND user_phone = ?"
            params.append(user_phone)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY remind_at ASC"
        cursor.execute(query, params)
        reminders = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return reminders

    def update_reminder_status(self, reminder_id: int, status: str):
        """Update reminder status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE reminders SET status = ? WHERE id = ?",
            (status, reminder_id)
        )
        conn.commit()
        conn.close()

    # ─── Task Operations ─────────────────────────────────────────

    def create_task(self, user_phone: str, title: str, description: str = "",
                    priority: str = "medium", due_date: str = None) -> dict:
        """Create a new task."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """INSERT INTO tasks (user_phone, title, description, priority, due_date)
               VALUES (?, ?, ?, ?, ?)""",
            (user_phone, title, description, priority, due_date)
        )
        conn.commit()
        task_id = cursor.lastrowid

        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = dict(cursor.fetchone())
        conn.close()

        self.log_action(user_phone, "task_created", f"Task: {title} [{priority}]")
        return task

    def get_tasks(self, user_phone: str = None, status: str = None) -> list:
        """Get tasks, optionally filtered."""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM tasks WHERE 1=1"
        params = []

        if user_phone:
            query += " AND user_phone = ?"
            params.append(user_phone)
        if status:
            query += " AND status = ?"
            params.append(status)

        query += " ORDER BY created_at DESC"
        cursor.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return tasks

    def update_task_status(self, task_id: int, status: str):
        """Update task status."""
        conn = self.get_connection()
        cursor = conn.cursor()
        completed_at = datetime.now().isoformat() if status == "completed" else None
        cursor.execute(
            "UPDATE tasks SET status = ?, completed_at = ? WHERE id = ?",
            (status, completed_at, task_id)
        )
        conn.commit()
        conn.close()

    def complete_task(self, user_phone: str, task_identifier: str) -> Optional[dict]:
        """Complete a task by title search."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM tasks WHERE user_phone = ? AND status = 'pending'
               AND LOWER(title) LIKE ? ORDER BY created_at DESC LIMIT 1""",
            (user_phone, f"%{task_identifier.lower()}%")
        )
        task = cursor.fetchone()
        if task:
            task = dict(task)
            self.update_task_status(task["id"], "completed")
            self.log_action(user_phone, "task_completed", f"Task: {task['title']}")
            conn.close()
            return task
        conn.close()
        return None

    # ─── Conversation Operations ─────────────────────────────────

    def save_message(self, user_phone: str, role: str, content: str, intent: str = ""):
        """Save a conversation message."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """INSERT INTO conversations (user_phone, role, content, intent)
               VALUES (?, ?, ?, ?)""",
            (user_phone, role, content, intent)
        )
        conn.commit()
        conn.close()

    def get_conversation_history(self, user_phone: str, limit: int = 10) -> list:
        """Get recent conversation history for a user."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT role, content, timestamp FROM conversations
               WHERE user_phone = ? ORDER BY timestamp DESC LIMIT ?""",
            (user_phone, limit)
        )
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return list(reversed(messages))

    def get_all_conversations(self, limit: int = 50) -> list:
        """Get all recent conversations for dashboard."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM conversations ORDER BY timestamp DESC LIMIT ?""",
            (limit,)
        )
        conversations = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return conversations

    # ─── Agent Log Operations ────────────────────────────────────

    def log_action(self, user_phone: str, action: str, details: str = ""):
        """Log an agent action."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO agent_logs (user_phone, action, details) VALUES (?, ?, ?)",
            (user_phone, action, details)
        )
        conn.commit()
        conn.close()

    def get_agent_logs(self, limit: int = 50) -> list:
        """Get recent agent activity logs."""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM agent_logs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs

    # ─── Statistics ──────────────────────────────────────────────

    def get_stats(self) -> dict:
        """Get dashboard statistics."""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) as count FROM users")
        total_users = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM reminders WHERE status = 'pending'")
        active_reminders = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'pending'")
        pending_tasks = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'")
        completed_tasks = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM conversations")
        total_messages = cursor.fetchone()["count"]

        cursor.execute("SELECT COUNT(*) as count FROM agent_logs")
        total_actions = cursor.fetchone()["count"]

        conn.close()

        return {
            "total_users": total_users,
            "active_reminders": active_reminders,
            "pending_tasks": pending_tasks,
            "completed_tasks": completed_tasks,
            "total_messages": total_messages,
            "total_agent_actions": total_actions
        }
