import sqlite3
from datetime import datetime

DATABASE_NAME = 'scheduler.db'

def get_db():
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # Employee table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')

    # Absences table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS absences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            absence_date DATE NOT NULL,
            reason TEXT NOT NULL, -- 'Leave', 'Sick', 'Permission'
            FOREIGN KEY (employee_id) REFERENCES employees (id)
        )
    ''')

    conn.commit()
    conn.close()

# --- Employee Functions ---
def add_employee(name):
    conn = get_db()
    try:
        conn.execute("INSERT INTO employees (name) VALUES (?)", (name,))
        conn.commit()
    except sqlite3.IntegrityError:
        # Employee name already exists
        pass
    finally:
        conn.close()

def get_all_employees():
    conn = get_db()
    employees = conn.execute("SELECT * FROM employees ORDER BY name").fetchall()
    conn.close()
    return employees

def update_employee(employee_id, new_name):
    conn = get_db()
    conn.execute("UPDATE employees SET name = ? WHERE id = ?", (new_name, employee_id))
    conn.commit()
    conn.close()

def delete_employee(employee_id):
    conn = get_db()
    conn.execute("DELETE FROM absences WHERE employee_id = ?", (employee_id,))
    conn.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
    conn.commit()
    conn.close()

# --- Absence Functions ---
def add_absence(employee_id, date, reason):
    conn = get_db()
    conn.execute("INSERT INTO absences (employee_id, absence_date, reason) VALUES (?, ?, ?)",
                 (employee_id, date, reason))
    conn.commit()
    conn.close()

def get_employee_absence_stats(employee_id, year):
    conn = get_db()
    start_of_year = f"{year}-01-01"
    end_of_year = f"{year}-12-31"

    leave_count = conn.execute(
        "SELECT COUNT(*) FROM absences WHERE employee_id = ? AND reason = 'Leave' AND absence_date BETWEEN ? AND ?",
        (employee_id, start_of_year, end_of_year)
    ).fetchone()[0]

    other_absences = conn.execute(
        "SELECT COUNT(*) FROM absences WHERE employee_id = ? AND reason IN ('Sick', 'Permission') AND absence_date BETWEEN ? AND ?",
        (employee_id, start_of_year, end_of_year)
    ).fetchone()[0]

    conn.close()
    return {'remaining_leave': 12 - leave_count, 'other_absences': other_absences}

if __name__ == '__main__':
    # Initialize the database if the script is run directly
    init_db()
    print("Database initialized.")
