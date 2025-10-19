from flask import Flask, render_template, request
from scheduler import generate_schedule
from datetime import datetime
import calendar

app = Flask(__name__)

def parse_absences(absences_str):
    absences = []
    for line in absences_str.strip().splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) == 2:
            employee_name, day_str = parts
            try:
                day = int(day_str)
                absences.append({'employee_name': employee_name, 'day': day})
            except ValueError:
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
            day = int(days[i]) - 1 # Convert to 0-indexed
            shift_name = shifts[i]
            count = int(counts[i])

            shift_id = shift_map.get(shift_name.lower())

            if shift_id is not None and day >= 0:
                staffing_reqs[(day, shift_id)] = count
        except (ValueError, IndexError):
            pass

    return staffing_reqs

@app.route('/', methods=['GET', 'POST'])
def index():
    now = datetime.now()
    year, month = now.year, now.month
    employees_str, absences_str = "", ""
    schedule, stats, error = None, None, None
    # We don't need to pass staffing_reqs_str anymore as it's not a single textarea

    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])
        employees_str = request.form['employees']
        absences_str = request.form['absences']

        employees = [e.strip() for e in employees_str.split(',') if e.strip()]

        if not employees:
            error = "Please provide a list of employees."
        else:
            absences = parse_absences(absences_str)
            staffing_reqs = parse_staffing_requirements(request.form)
            schedule, stats = generate_schedule(year, month, employees, absences, staffing_reqs)
            if not schedule:
                error = "No solution could be found. Try adding more employees, reducing absences, or adjusting staffing requirements."

    return render_template('index.html',
                           year=year, month=month,
                           employees_str=employees_str,
                           absences_str=absences_str,
                           schedule=schedule, stats=stats,
                           error=error, calendar=calendar)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
