from ortools.sat.python import cp_model
import argparse

def generate_schedule(employees):
    """
    Generates a shift schedule for the given list of employees.
    """
    num_employees = len(employees)
    num_shifts = 3  # Morning, Evening, Night
    num_days = 7
    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    # Creates the model.
    model = cp_model.CpModel()

    # Creates shift variables.
    shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                shifts[(e, d, s)] = model.NewBoolVar(f'shift_e{e}d{d}s{s}')

    # Each shift is assigned to exactly one employee.
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(shifts[(e, d, s)] for e in all_employees)

    # Each employee can only be assigned to one shift per day.
    for e in all_employees:
        for d in all_days:
            model.AddAtMostOne(shifts[(e, d, s)] for s in all_shifts)

    # Each employee works at most 5 days a week.
    for e in all_employees:
        model.Add(sum(shifts[(e, d, s)] for d in all_days for s in all_shifts) <= 5)

    # Creates a solver and solves the model.
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    schedule_output = []
    stats_output = []

    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for d in all_days:
            schedule_output.append(f'Day {d}')
            for s in all_shifts:
                for e in all_employees:
                    if solver.Value(shifts[(e, d, s)]) == 1:
                        if s == 0:
                            shift_name = "Morning ( 7am -  3pm)"
                        elif s == 1:
                            shift_name = "Evening ( 3pm - 11pm)"
                        else:
                            shift_name = "Night   (11pm -  7am)"
                        schedule_output.append(f'  Shift {shift_name} assigned to employee {employees[e]}')

        for e in all_employees:
            num_shifts_worked = 0
            for d in all_days:
                for s in all_shifts:
                    if solver.Value(shifts[(e, d, s)]) == 1:
                        num_shifts_worked += 1
            stats_output.append(f'Employee {employees[e]} worked {num_shifts_worked} shifts')

        return schedule_output, stats_output
    else:
        return None, None

def main(employees):
    """
    Main function to run from the command line.
    """
    schedule, stats = generate_schedule(employees)
    if schedule and stats:
        print('Solution:')
        for line in schedule:
            print(line)
        print()
        print('Statistics')
        for line in stats:
            print(line)
    else:
        print('No solution found.')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--employees', nargs='+', default=['Alice', 'Bob', 'Charlie', 'David', 'Eve'],
                        help='List of employee names')
    args = parser.parse_args()
    main(args.employees)
