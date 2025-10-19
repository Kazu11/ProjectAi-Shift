from flask import Flask, render_template, request, redirect, url_for
from scheduler import generate_schedule
from datetime import datetime
import calendar
import database as db

app = Flask(__name__)

def parse_dynamic_absences(form):
    absences = []
    employee_ids = form.getlist('absence_employee_id')
    days = form.getlist('absence_day')
    reasons = form.getlist('absence_reason')

    # Get all employees to map id back to name for the scheduler function
    all_employees = {str(e['id']): e['name'] for e in db.get_all_employees()}

    for i in range(len(employee_ids)):
        try:
            emp_id = int(employee_ids[i])
            day = int(days[i])
            reason = reasons[i]

            # Add to database
            date_str = f"{request.form['year']}-{request.form['month']}-{day}"
            db.add_absence(emp_id, date_str, reason)

            # Add to list for scheduler
            absences.append({
                'employee_name': all_employees.get(str(emp_id)),
                'day': day
            })
        except (ValueError, IndexError):
            pass
    return absences

def parse_staffing_requirements(form):
    staffing_reqs = {}
    shift_map = {'morning': 0, 'evening': 1, 'night': 2}
    days = form.getlist('staff_req_day')
    shifts = form.getlist('staff_req_shift')
    counts = form.getlist('staff_req_count')
    for i in range(len(days)):
        try:
            day = int(days[i]) - 1
            shift_id = shift_map.get(shifts[i].lower())
            count = int(counts[i])
            if shift_id is not None and day >= 0:
                staffing_reqs[(day, shift_id)] = count
        except (ValueError, IndexError):
            pass
    return staffing_reqs

@app.route('/', methods=['GET', 'POST'])
def index():
    now = datetime.now()
    year, month = now.year, now.month
    schedule, stats, error = None, None, None

    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])

        # Get selected employees from checkboxes
        employees = request.form.getlist('employees')

        if not employees:
            error = "Please select at least one employee for the schedule."
        else:
            absences = parse_dynamic_absences(request.form)
            staffing_reqs = parse_staffing_requirements(request.form)
            schedule, stats = generate_schedule(year, month, employees, absences, staffing_reqs)
            if not schedule:
                error = "No solution could be found. Try adding more employees, reducing absences, or adjusting staffing requirements."

    all_employees = db.get_all_employees()
    return render_template('index.html',
                           year=year, month=month,
                           all_employees=all_employees,
                           schedule=schedule, stats=stats,
                           error=error, calendar=calendar)


@app.route('/manage', methods=['GET', 'POST'])
def manage_employees():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            db.add_employee(request.form['name'])
        elif action == 'update':
            db.update_employee(request.form['id'], request.form['name'])
        elif action == 'delete':
            db.delete_employee(request.form['id'])
        return redirect(url_for('manage_employees'))

    employees_raw = db.get_all_employees()
    employees_with_stats = []
    current_year = datetime.now().year
    for emp in employees_raw:
        stats = db.get_employee_absence_stats(emp['id'], current_year)
        employees_with_stats.append({
            'id': emp['id'],
            'name': emp['name'],
            'remaining_leave': stats['remaining_leave'],
            'other_absences': stats['other_absences']
        })

    return render_template('manage.html', employees=employees_with_stats)

if __name__ == '__main__':
    db.init_db()
    app.run(debug=True, host='0.0.0.0', port=8080)
