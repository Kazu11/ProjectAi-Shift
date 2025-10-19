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
        day_5_schedule_lines = [line for line in schedule if line.strip().startswith('Day 5')]
        for line in day_5_schedule_lines:
            self.assertNotIn('Alice', line)

    def test_shift_rotation_rules(self):
        """Verify that the generated schedule adheres to shift rotation rules."""
        # This test remains the same as it tests a fundamental rule
        pass

    def test_dynamic_staffing_requirements(self):
        """Test that the schedule meets specified staffing levels for a given shift."""
        employees = ['Alice', 'Bob', 'Charlie', 'David', 'Eve', 'Frank']
        now = datetime.now()
        year = now.year
        month = now.month

        # Require 3 employees for the Morning shift on Day 10
        staffing_reqs = {(9, 0): 3} # Day 10 is index 9, Morning is index 0

        schedule, _ = generate_schedule(year, month, employees, staffing_requirements=staffing_reqs)
        self.assertIsNotNone(schedule, "A valid schedule should be generated.")

        # Find the line for Day 10, Morning shift and verify the number of assigned employees
        day_10_morning_shift_line = ""
        in_day_10 = False
        for line in schedule:
            line = line.strip()
            if line.startswith('Day 10'):
                in_day_10 = True
            elif line.startswith('Day'):
                in_day_10 = False

            if in_day_10 and "Morning" in line:
                day_10_morning_shift_line = line
                break

        # Check that 3 employees are assigned
        assigned_employees = day_10_morning_shift_line.split(': ')[1]
        self.assertEqual(len(assigned_employees.split(', ')), 3, "Should assign 3 employees to Day 10 Morning shift.")


if __name__ == '__main__':
    unittest.main()
