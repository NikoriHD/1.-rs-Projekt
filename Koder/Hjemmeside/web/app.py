from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

desktop_path = os.path.join(os.path.expanduser('~'), 'Desktop')
db_path = os.path.join(desktop_path, 'bk_sensor_data.db')

if not os.path.exists(desktop_path):
    os.makedirs(desktop_path)

if not os.path.exists(db_path):
    print(f"Database file does not exist at path: {db_path}")
else:
    print(f"Using database file at path: {db_path}")

VALID_USERNAME = "admin"
VALID_PASSWORD = "password"

def execute_sql_command(sql):
    conn = None
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(sql)
        if sql.strip().lower().startswith("select"):
            data = cursor.fetchall()
            return data
        else:
            conn.commit()
            return "Command executed successfully."
    except sqlite3.Error as e:
        return f"SQLite error: {e}"
    finally:
        if conn:
            conn.close()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error="Invalid username or password.")
    return render_template('login.html', error=None)

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

def login_required(func):
    def wrapper(*args, **kwargs):
        if not session.get('logged_in'):
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper

@app.route('/', methods=['GET', 'POST'], endpoint='index')
@login_required
def index():
    if request.method == 'POST':
        sql_command = request.form['sql_command']
        result = execute_sql_command(sql_command)
        return render_template('index.html', result=result, sql_command=sql_command)
    elif request.method == 'GET':
        sort_by = request.args.get('sort_by', 'id')
        sort_order = request.args.get('sort_order', 'ASC')
        
        column_mapping = {
            'ID': 'id',
            'Timestamp': 'timestamp',
            'Sensor_Type': 'sensor_id',
            'Temperature': 'temperature',
            'Humidity': 'humidity',
            'Analog_Value': 'analog_value',
            'Digital_Value': 'digital_value',
        }
        
        sort_column = column_mapping.get(sort_by, 'id')
        
        default_sql_command = f'SELECT * FROM bk_sensor_data ORDER BY {sort_column} {sort_order};'
        default_result = execute_sql_command(default_sql_command)
        return render_template('index.html', result=default_result, sql_command=default_sql_command, current_sort_by=sort_by)
    return render_template('index.html', result=None, sql_command=None)

@app.route('/temperature', endpoint='temperature_route')
@login_required
def temperature():
    return render_template('temperature.html')

@app.route('/humidity', endpoint='humidity_route')
@login_required
def humidity():
    return render_template('humidity.html')

@app.route('/analog_data', endpoint='analog_data')
@login_required
def analog_data():
    return render_template('analog_data.html')

@app.route('/fetch_temperature_data', endpoint='fetch_temperature')
@login_required
def fetch_temperature_data():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT temperature FROM bk_sensor_data')
        data = cursor.fetchall()
        temperatures = [entry[0] for entry in data]
        return jsonify(temperatures)
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()

@app.route('/fetch_humidity_data', endpoint='fetch_humidity')
@login_required
def fetch_humidity_data():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT humidity FROM bk_sensor_data')
        data = cursor.fetchall()
        humidities = [entry[0] for entry in data]
        return jsonify(humidities)
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()

@app.route('/fetch_analog_value_data', endpoint='fetch_analog_value')
@login_required
def fetch_analog_value_data():
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT analog_value FROM bk_sensor_data')
        data = cursor.fetchall()
        analog_values = [entry[0] for entry in data]
        return jsonify(analog_values)
    except sqlite3.Error as e:
        return str(e)
    finally:
        conn.close()

if __name__ == '__main__':
    app.run(debug=True)
