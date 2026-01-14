from flask import Flask, render_template, request, redirect, jsonify

import json
import os
from datetime import datetime

app = Flask(__name__)

DATA_FILE = 'data.json'

if not os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'w') as f:
        json.dump({
            'tasks': [], 
            'classes': [],
            'subjects': {
                'Math': {'color': '#FF5733'},
                'Science': {'color': '#33FF57'},
                'English': {'color': '#3357FF'},
                'History': {'color': '#F333FF'}
            }
        }, f)

def load_data():
    """Load data from JSON file"""
    try:
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
            if isinstance(data, list):
                data = {'tasks': data, 'classes': [], 'subjects': {}}
            elif 'subjects' not in data:
                data['subjects'] = {}
            return data
    except (json.JSONDecodeError, FileNotFoundError):
        return {'tasks': [], 'classes': [], 'subjects': {}}

def save_data(data):
    """Save data to JSON file"""
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/')
def index():
    data = load_data()
    return render_template('index.html', tasks=data['tasks'], classes=data['classes'], subjects=data['subjects'])

@app.route('/add-task', methods=['POST'])
def add_task():
    title = request.form['title']
    date = request.form['date']
    subject = request.form.get('subject', '')
    
    data = load_data()
    subject_color = data['subjects'].get(subject, {}).get('color', '#ff6b6b')
    
    new_task = {
        'id': f"task_{int(datetime.now().timestamp())}",
        'title': title,
        'start': date,
        'subject': subject,
        'type': 'task',
        'allDay': True,
        'backgroundColor': subject_color,
        'borderColor': subject_color
    }
    
    data['tasks'].append(new_task)
    save_data(data)
    
    return jsonify({'success': True})

@app.route('/add-class', methods=['POST'])
def add_class():
    subject = request.form['subject']
    day = request.form['day']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    
    data = load_data()
    subject_color = data['subjects'].get(subject, {}).get('color', '#4fc3f7')
    
    new_class = {
        'id': f"class_{int(datetime.now().timestamp())}",
        'title': f"{subject}",
        'daysOfWeek': [get_day_number(day)],
        'startTime': start_time,
        'endTime': end_time,
        'subject': subject,
        'day': day,
        'type': 'class',
        'backgroundColor': subject_color,
        'borderColor': subject_color
    }
    
    data['classes'].append(new_class)
    save_data(data)
    
    return jsonify({'success': True})

def get_day_number(day_name):
    """Convert day name to FullCalendar day number"""
    days = {
        'Sunday': 0, 'Monday': 1, 'Tuesday': 2, 'Wednesday': 3,
        'Thursday': 4, 'Friday': 5, 'Saturday': 6
    }
    return days.get(day_name, 1)

@app.route('/get-events')
def get_events():
    """Get all events (tasks and classes) for FullCalendar"""
    data = load_data()
    events = []
    
    for task in data['tasks']:
        events.append(task)
    
    for class_item in data['classes']:
        events.append(class_item)
    
    return jsonify(events)

@app.route('/get-subjects')
def get_subjects():
    data = load_data()
    return jsonify(data.get('subjects', {}))

@app.route('/add-subject', methods=['POST'])
def add_subject():
    subject_name = request.form['name']
    subject_color = request.form['color']
    
    data = load_data()
    if 'subjects' not in data:
        data['subjects'] = {}
    
    data['subjects'][subject_name] = {'color': subject_color}
    save_data(data)
    
    return jsonify({'success': True})

@app.route('/delete-subject/<subject_name>', methods=['DELETE'])
def delete_subject(subject_name):
    data = load_data()
    if 'subjects' in data and subject_name in data['subjects']:
        del data['subjects'][subject_name]
        save_data(data)
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': 'Subject not found'})

@app.route('/delete-task/<task_id>', methods=['DELETE'])
def delete_task(task_id):
    data = load_data()
    data['tasks'] = [task for task in data['tasks'] if task.get('id') != task_id]
    save_data(data)
    return jsonify({'success': True})

@app.route('/delete-class/<class_id>', methods=['DELETE'])
def delete_class(class_id):
    data = load_data()
    data['classes'] = [cls for cls in data['classes'] if cls.get('id') != class_id]
    save_data(data)
    return jsonify({'success': True})

if __name__ == '__main__':
    app.run(debug=True)



tasks = [
    {"id": 1, "name": "Task 1"},
    {"id": 2, "name": "Task 2"},
]

classes = [
    {"id": 1, "name": "Class 1"},
    {"id": 2, "name": "Class 2"},
]

@app.route('/')
def index():
    return render_template('index.html', tasks=tasks, classes=classes)

@app.route('/edit_task', methods=['POST'])
def edit_task():
    data = request.json
    task_id = data.get('id')
    new_name = data.get('name')
    for task in tasks:
        if task['id'] == task_id:
            task['name'] = new_name
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

@app.route('/edit_class', methods=['POST'])
def edit_class():
    data = request.json
    class_id = data.get('id')
    new_name = data.get('name')
    for cls in classes:
        if cls['id'] == class_id:
            cls['name'] = new_name
            return jsonify({"success": True})
    return jsonify({"success": False}), 404

if __name__ == '__main__':
    app.run(debug=True)
