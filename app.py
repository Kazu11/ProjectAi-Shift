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
                # Handle cases where day is not a valid number
                pass
    return absences

@app.route('/', methods=['GET', 'POST'])
def index():
    now = datetime.now()
    year = now.year
    month = now.month
    employees_str = ""
    absences_str = ""
    schedule = None
    stats = None
    error = None

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
            schedule, stats = generate_schedule(year, month, employees, absences)
            if not schedule:
                error = "No solution could be found with the given constraints. Try adding more employees or reducing absences."

    return render_template('index.html',
                           year=year,
                           month=month,
                           employees_str=employees_str,
                           absences_str=absences_str,
                           schedule=schedule,
                           stats=stats,
                           error=error,
                           calendar=calendar)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
