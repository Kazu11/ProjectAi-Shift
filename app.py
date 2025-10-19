from flask import Flask, render_template, request
from scheduler import generate_schedule

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        employees_str = request.form['employees']
        employees = [e.strip() for e in employees_str.split(',') if e.strip()]
        if not employees:
            return render_template('index.html', error="Please provide a list of employees.")

        schedule, stats = generate_schedule(employees)
        return render_template('index.html', schedule=schedule, stats=stats, employees=employees_str)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
