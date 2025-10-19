import unittest
import subprocess

class TestScheduler(unittest.TestCase):
    def test_sufficient_employees(self):
        """Test that a schedule is found when there are enough employees."""
        employees = ['Alice', 'Bob', 'Charlie', 'David', 'Eve']
        result = subprocess.run(
            ['python', 'scheduler.py', '--employees'] + employees,
            capture_output=True, text=True)
        self.assertIn('Solution:', result.stdout)

    def test_insufficient_employees(self):
        """Test that no schedule is found when there are not enough employees."""
        employees = ['Alice', 'Bob', 'Charlie', 'David']
        result = subprocess.run(
            ['python', 'scheduler.py', '--employees'] + employees,
            capture_output=True, text=True)
        self.assertIn('No solution found.', result.stdout)

if __name__ == '__main__':
    unittest.main()
