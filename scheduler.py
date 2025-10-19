from ortools.sat.python import cp_model
import argparse
import calendar
from datetime import datetime

def generate_schedule(year, month, employees, absences=None, staffing_requirements=None):
    """
    Generates a shift schedule with dynamic staffing requirements.
    """
    if absences is None: absences = []
    if staffing_requirements is None: staffing_requirements = {}

    num_employees = len(employees)
    num_shifts = 3
    _, num_days = calendar.monthrange(year, month)

    all_employees, all_shifts, all_days = range(num_employees), range(num_shifts), range(num_days)

    employee_map = {name: i for i, name in enumerate(employees)}
    absent_employees = set()
    for ab in absences:
        if ab['employee_name'] in employee_map:
            emp_idx = employee_map[ab['employee_name']]
            day_idx = ab['day'] - 1
            if 0 <= day_idx < num_days: absent_employees.add((emp_idx, day_idx))

    model = cp_model.CpModel()

    regular_shifts, overtime_shifts = {}, {}
    for e in all_employees:
        for d in all_days:
            for s in all_shifts:
                regular_shifts[(e, d, s)] = model.NewBoolVar(f'reg_e{e}d{d}s{s}')
                overtime_shifts[(e, d, s)] = model.NewBoolVar(f'ovr_e{e}d{d}s{s}')

    # --- Core Constraints ---
    # Each shift must meet its staffing requirement.
    for d in all_days:
        for s in all_shifts:
            required_staff = staffing_requirements.get((d, s), 1)
            model.Add(sum(regular_shifts[(e, d, s)] + overtime_shifts[(e, d, s)] for e in all_employees) == required_staff)

    # Absence constraints.
    for e, d in absent_employees:
        for s in all_shifts:
            model.Add(regular_shifts[(e, d, s)] == 0)
            model.Add(overtime_shifts[(e, d, s)] == 0)

    # --- Employee Workload & Rotation Constraints ---
    for e in all_employees:
        for d in all_days:
            model.Add(sum(regular_shifts[(e, d, s)] for s in all_shifts) <= 1)
            model.Add(sum(regular_shifts[(e, d, s)] + overtime_shifts[(e, d, s)] for s in all_shifts) <= 2)

        for d in range(num_days - 6):
            model.Add(sum(regular_shifts[(e, d_window, s)] for d_window in range(d, d + 7) for s in all_shifts) <= 6)

        for d in range(num_days - 1):
            works_night_d = model.NewBoolVar(f'e{e}d{d}_works_night')
            model.AddBoolOr([regular_shifts[(e, d, 2)], overtime_shifts[(e, d, 2)]]).OnlyEnforceIf(works_night_d)
            model.AddBoolAnd([regular_shifts[(e, d, 2)].Not(), overtime_shifts[(e, d, 2)].Not()]).OnlyEnforceIf(works_night_d.Not())
            works_morning_d1 = model.NewBoolVar(f'e{e}d{d+1}_works_morning')
            model.AddBoolOr([regular_shifts[(e, d + 1, 0)], overtime_shifts[(e, d + 1, 0)]]).OnlyEnforceIf(works_morning_d1)
            model.AddBoolAnd([regular_shifts[(e, d + 1, 0)].Not(), overtime_shifts[(e, d + 1, 0)].Not()]).OnlyEnforceIf(works_morning_d1.Not())
            model.AddImplication(works_night_d, works_morning_d1.Not())

    # --- Overtime Constraints ---
    for e in all_employees:
        model.Add(sum(overtime_shifts[(e, d, s)] for d in all_days for s in all_shifts) <= 3)
        for d in range(num_days - 7):
            model.Add(sum(overtime_shifts[(e, d_window, s)] for d_window in range(d, d + 8) for s in all_shifts) <= 1)
        for d in all_days:
            for s in all_shifts:
                adj_regular_shifts = []
                if s > 0: adj_regular_shifts.append(regular_shifts[(e, d, s - 1)])
                if s < num_shifts - 1: adj_regular_shifts.append(regular_shifts[(e, d, s + 1)])
                if adj_regular_shifts: model.AddBoolOr(adj_regular_shifts).OnlyEnforceIf(overtime_shifts[(e, d, s)])

    model.Minimize(sum(overtime_shifts.values()))

    solver = cp_model.CpSolver()
    status = solver.Solve(model)

    schedule_output, stats_output, structured_schedule = [], [], {}
    if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
        for d in all_days:
            schedule_output.append(f'Day {d + 1}')
            day_key = d + 1
            structured_schedule[day_key] = {}
            for s in all_shifts:
                assigned_employees = []
                shift_name_key = ["Morning", "Evening", "Night"][s]
                structured_schedule[day_key][shift_name_key] = []
                for e in all_employees:
                    is_overtime = solver.Value(overtime_shifts[(e, d, s)]) == 1
                    if is_overtime or solver.Value(regular_shifts[(e, d, s)]) == 1:
                        employee_name = employees[e]
                        ot_marker = " (Overtime)" if is_overtime else ""
                        assigned_employees.append(f'{employee_name}{ot_marker}')
                        structured_schedule[day_key][shift_name_key].append(employee_name)

                shift_name_display = ["Morning (7am-3pm)", "Evening (3pm-11pm)", "Night (11pm-7am)"][s]
                schedule_output.append(f'  Shift {shift_name_display}: {", ".join(assigned_employees)}')

        for e in all_employees:
            reg = sum(solver.Value(regular_shifts[(e, d, s)]) for d in all_days for s in all_shifts)
            ot = sum(solver.Value(overtime_shifts[(e, d, s)]) for d in all_days for s in all_shifts)
            stats_output.append(f'{employees[e]}: {reg} regular shifts, {ot} overtime shifts.')

        return schedule_output, stats_output, structured_schedule
    else:
        return None, None, None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--employees', nargs='+', default=['Alice', 'Bob', 'Charlie', 'David', 'Eve'], help='List of employee names')
    parser.add_argument('--year', type=int, default=datetime.now().year, help='Year for the schedule')
    parser.add_argument('--month', type=int, default=datetime.now().month, help='Month for the schedule')
    args = parser.parse_args()

    staffing_reqs = {(4, 0): 2, (4, 1): 2} # Day 5, Morning: 2 staff; Day 5, Evening: 2 staff

    schedule, stats, _ = generate_schedule(args.year, args.month, args.employees, staffing_requirements=staffing_reqs)

    if schedule and stats:
        print(f'Solution for {calendar.month_name[args.month]} {args.year}:')
        print(f"Staffing Requirements: {staffing_reqs}")
        for line in schedule:
            print(line)
        print("\nStatistics")
        for line in stats:
            print(line)
    else:
        print('No solution found.')

if __name__ == '__main__':
    main()
