import unittest
import subprocess
from scheduler import generate_schedule
from datetime import datetime
import calendar

class TestScheduler(unittest.TestCase):
    def test_cli_sufficient_employees(self):
        """Test the CLI finds a schedule with enough employees."""
        employees = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']
        result = subprocess.run(
            ['python', 'scheduler.py', '--employees'] + employees,
            capture_output=True, text=True)
        self.assertIn('Solution', result.stdout)

    def test_cli_insufficient_employees(self):
        """Test the CLI finds no schedule with too few employees."""
        employees = ['Alice', 'Bob']
        result = subprocess.run(
            ['python', 'scheduler.py', '--employees'] + employees,
            capture_output=True, text=True)
        self.assertIn('No solution found', result.stdout)

    def test_monthly_schedule_logic_with_absences(self):
        """Test the core monthly scheduling logic with an absence."""
        employees = ['Alice', 'Bob', 'Charlie', 'David']
        absences = [{'employee_name': 'Alice', 'day': 5}]
        now = datetime.now()
        schedule, _ = generate_schedule(now.year, now.month, employees, absences)
        self.assertIsNotNone(schedule, "Schedule should be generated even with absences.")
        day_5_schedule = [line for line in schedule if line.strip().startswith('Day 5')]
        for line in day_5_schedule:
            self.assertNotIn('Alice', line)

    def test_shift_rotation_rules(self):
        """Verify that the generated schedule adheres to shift rotation rules."""
        employees = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']
        now = datetime.now()
        year = now.year
        month = now.month
        _, num_days = calendar.monthrange(year, month)

        schedule, _ = generate_schedule(year, month, employees)
        self.assertIsNotNone(schedule, "A valid schedule should be generated.")

        # Helper to parse the schedule into a more usable format
        # schedule_map[employee][day] = shift_id (0:M, 1:E, 2:N)
        schedule_map = {emp: {} for emp in employees}
        current_day = -1
        for line in schedule:
            line = line.strip()
            if line.startswith('Day'):
                current_day = int(line.split(' ')[1]) - 1
                continue

            parts = line.split(' ')
            emp_name = parts[-1]
            if "(Overtime)" in emp_name:
                emp_name = parts[-2] # Adjust for overtime marker

            is_regular = "(Overtime)" not in line
            shift_type = parts[1] # Morning, Evening, Night
            shift_id = {'Morning': 0, 'Evening': 1, 'Night': 2}[shift_type]

            if emp_name in employees:
                if current_day not in schedule_map[emp_name]:
                    schedule_map[emp_name][current_day] = []
                schedule_map[emp_name][current_day].append({'id': shift_id, 'regular': is_regular})

        # Check the rotation rules for each employee
        for emp in employees:
            for day in range(num_days - 1):
                today_shifts = schedule_map[emp].get(day, [])
                tomorrow_shifts = schedule_map[emp].get(day + 1, [])

                if not today_shifts or not tomorrow_shifts:
                    continue

                # Hard Rule: No Night -> Morning
                if any(s['id'] == 2 for s in today_shifts):
                    self.assertFalse(any(s['id'] == 0 for s in tomorrow_shifts),
                                     f"Invalid rotation for {emp}: Night on day {day} to Morning on day {day + 1}")

                # Flexible Rule for Regular Shifts
                today_regular_shifts = [s['id'] for s in today_shifts if s['regular']]
                tomorrow_regular_shifts = [s['id'] for s in tomorrow_shifts if s['regular']]

                if not today_regular_shifts or not tomorrow_regular_shifts:
                    continue

                today_reg_id = today_regular_shifts[0]
                tomorrow_reg_id = tomorrow_regular_shifts[0]

                # Evening -> Morning (Regular only)
                if today_reg_id == 1:
                    self.assertNotEqual(tomorrow_reg_id, 0,
                                       f"Invalid regular rotation for {emp}: Evening on day {day} to Morning on day {day + 1}")
                # Night -> Evening (Regular only)
                if today_reg_id == 2:
                    self.assertNotEqual(tomorrow_reg_id, 1,
                                       f"Invalid regular rotation for {emp}: Night on day {day} to Evening on day {day + 1}")

if __name__ == '__main__':
    unittest.main()
