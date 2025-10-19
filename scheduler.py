from ortools.sat.python import cp_model
import argparse
import calendar
from datetime import datetime

def generate_schedule(year, month, employees, absences=None):
    """
    Generates a shift schedule, handling absences and overtime.
    """
    if absences is None:
        absences = []

    num_employees = len(employees)
    num_shifts = 3
    _, num_days = calendar.monthrange(year, month)

    all_employees = range(num_employees)
    all_shifts = range(num_shifts)
    all_days = range(num_days)

    employee_map = {name: i for i, name in enumerate(employees)}
    absent_employees = set()
    for ab in absences:
        if ab['employee_name'] in employee_map:
            emp_idx = employee_map[ab['employee_name']]
            day_idx = ab['day'] - 1
            if 0 <= day_idx < num_days:
                absent_employees.add((emp_idx, day_idx))

    model = cp_model.CpModel()

    regular_shifts = {}
    overtime_shifts = {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                regular_shifts[(e, d, s)] = model.NewBoolVar(f'reg_e{e}d{d}s{s}')
                overtime_shifts[(e, d, s)] = model.NewBoolVar(f'ovr_e{e}d{d}s{s}')

    # --- Core Constraints ---
    # Each shift is covered by exactly one person (regular or overtime).
    for d in all_days:
        for s in all_shifts:
            model.AddExactlyOne(
                [regular_shifts[(e, d, s)] for e in all_employees] +
                [overtime_shifts[(e, d, s)] for e in all_employees]
            )

    # Absence constraints.
    for e, d in absent_employees:
        for s in all_shifts:
            model.Add(regular_shifts[(e, d, s)] == 0)
            model.Add(overtime_shifts[(e, d, s)] == 0)

    # --- Employee Workload Constraints ---
    for e in all_employees:
        for d in all_days:
            # At most one REGULAR shift per day.
            model.Add(sum(regular_shifts[(e, d, s)] for s in all_shifts) <= 1)
            # At most two TOTAL shifts per day (allows for one double shift).
            model.Add(sum(regular_shifts[(e, d, s)] + overtime_shifts[(e, d, s)] for s in all_shifts) <= 2)

    # --- Regular Shift Constraints ---
    # Max 6 regular shifts in a 7-day rolling window.
    for e in all_employees:
        for d in range(num_days - 6):
            model.Add(sum(regular_shifts[(e, d_window, s)] for d_window in range(d, d + 7) for s in all_shifts) <= 6)

    # --- Overtime Constraints ---
    # Max 3 overtime shifts per month.
    for e in all_employees:
        model.Add(sum(overtime_shifts[(e, d, s)] for d in all_days for s in all_shifts) <= 3)

    # At least 7-day gap between overtime shifts.
    for e in all_employees:
        for d in range(num_days - 7):
            model.Add(sum(overtime_shifts[(e, d_window, s)] for d_window in range(d, d + 8) for s in all_shifts) <= 1)

    # Overtime Eligibility: Must work an adjacent regular shift.
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                adj_regular_shifts = []
                # Shift before
                if s > 0:
                    adj_regular_shifts.append(regular_shifts[(e, d, s - 1)])
                # Shift after
                if s < num_shifts - 1:
                    adj_regular_shifts.append(regular_shifts[(e, d, s + 1)])

                # Enforce that if an overtime shift is taken, an adjacent regular shift must also be taken.
                if adj_regular_shifts:
                    model.AddBoolOr(adj_regular_shifts).OnlyEnforceIf(overtime_shifts[(e, d, s)])

    # --- Objective: Minimize Overtime ---
    model.Minimize(sum(overtime_shifts.values()))

    # --- Solve and Format Output ---
    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    schedule_output, stats_output = [], []
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for d in all_days:
            schedule_output.append(f'Day {d + 1}')
            for s in all_shifts:
                for e in all_employees:
                    is_overtime = solver.Value(overtime_shifts[(e, d, s)]) == 1
                    if is_overtime or solver.Value(regular_shifts[(e, d, s)]) == 1:
                        shift_name = ["Morning (7am-3pm)", "Evening (3pm-11pm)", "Night (11pm-7am)"][s]
                        ot_marker = " (Overtime)" if is_overtime else ""
                        schedule_output.append(f'  Shift {shift_name} assigned to {employees[e]}{ot_marker}')

        for e in all_employees:
            reg = sum(solver.Value(regular_shifts[(e, d, s)]) for d in all_days for s in all_shifts)
            ot = sum(solver.Value(overtime_shifts[(e, d, s)]) for d in all_days for s in all_shifts)
            stats_output.append(f'{employees[e]}: {reg} regular shifts, {ot} overtime shifts.')

        return schedule_output, stats_output
    else:
        return None, None

def main():
    parser = argparse.ArgumentParser()
    # Use a smaller, more constrained set of employees for testing the overtime logic
    parser.add_argument('--employees', nargs='+', default=['Alice', 'Bob', 'Charlie', 'David'], help='List of employee names')
    parser.add_argument('--year', type=int, default=datetime.now().year, help='Year for the schedule')
    parser.add_argument('--month', type=int, default=datetime.now().month, help='Month for the schedule')
    args = parser.parse_args()

    # Create a scenario where overtime is likely necessary
    absences = [{'employee_name': 'Alice', 'day': 5}, {'employee_name': 'Bob', 'day': 5}]

    schedule, stats = generate_schedule(args.year, args.month, args.employees, absences)

    if schedule and stats:
        print(f'Solution for {calendar.month_name[args.month]} {args.year}:')
        print(f"Absences: {absences}")
        for line in schedule:
            print(line)
        print("\nStatistics")
        for line in stats:
            print(line)
    else:
        print('No solution found.')

if __name__ == '__main__':
    main()
