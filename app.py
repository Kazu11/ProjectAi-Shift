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

def parse_staffing_requirements(staffing_reqs_str):
    staffing_reqs = {}
    shift_map = {'morning': 0, 'evening': 1, 'night': 2}
    for line in staffing_reqs_str.strip().splitlines():
        parts = [p.strip() for p in line.split(',')]
        if len(parts) == 3:
            day_str, shift_name, count_str = parts
            try:
                day = int(day_str) - 1 # Convert to 0-indexed
                shift_id = shift_map.get(shift_name.lower())
                count = int(count_str)
                if shift_id is not None and day >= 0:
                    staffing_reqs[(day, shift_id)] = count
            except ValueError:
                pass
    return staffing_reqs

@app.route('/', methods=['GET', 'POST'])
def index():
    now = datetime.now()
    year, month = now.year, now.month
    employees_str, absences_str, staffing_reqs_str = "", "", ""
    schedule, stats, error = None, None, None

    if request.method == 'POST':
        year = int(request.form['year'])
        month = int(request.form['month'])
        employees_str = request.form['employees']
        absences_str = request.form['absences']
        staffing_reqs_str = request.form['staffing_reqs']

        employees = [e.strip() for e in employees_str.split(',') if e.strip()]

        if not employees:
            error = "Please provide a list of employees."
        else:
            absences = parse_absences(absences_str)
            staffing_reqs = parse_staffing_requirements(staffing_reqs_str)
            schedule, stats = generate_schedule(year, month, employees, absences, staffing_reqs)
            if not schedule:
                error = "No solution could be found. Try adding more employees, reducing absences, or adjusting staffing requirements."

    return render_template('index.html',
                           year=year, month=month,
                           employees_str=employees_str,
                           absences_str=absences_str,
                           staffing_reqs_str=staffing_reqs_str,
                           schedule=schedule, stats=stats,
                           error=error, calendar=calendar)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
