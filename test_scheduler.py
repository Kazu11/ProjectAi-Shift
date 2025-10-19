import unittest
import subprocess
from scheduler import generate_schedule
from datetime import datetime

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
        # Request an absence for Alice on day 5.
        absences = [{'employee_name': 'Alice', 'day': 5}]
        now = datetime.now()

        schedule, _ = generate_schedule(now.year, now.month, employees, absences)

        # Check if a schedule was generated
        self.assertIsNotNone(schedule, "Schedule should be generated even with absences.")

        # Verify Alice is not scheduled on day 5
        day_5_schedule = [line for line in schedule if line.strip().startswith('Day 5')]

        # This is a bit of a simplification; a more robust test would parse the schedule more carefully.
        # For our purposes, we'll just check that Alice's name doesn't appear in the lines for day 5.
        for line in day_5_schedule:
            self.assertNotIn('Alice', line)

if __name__ == '__main__':
    unittest.main()
