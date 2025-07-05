import os
import random
from datetime import datetime, date
from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
from io import BytesIO

# Explicitly set template and static folder paths
app = Flask(
    __name__,
    template_folder=os.path.join(os.path.dirname(__file__), '../templates'),
    static_folder=os.path.join(os.path.dirname(__file__), '../static')
)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////tmp/todos.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = os.environ.get('SECRET_KEY', 'dev')

db = SQLAlchemy(app)

class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_reset = db.Column(db.String(10), default="")  # YYYY-MM-DD

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    note = db.Column(db.String(500), nullable=True)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.String(10), nullable=True)  # YYYY-MM-DD

with app.app_context():
    db.create_all()
    # Ensure Meta row exists
    if not Meta.query.first():
        db.session.add(Meta(last_reset=""))
        db.session.commit()
    # Add columns if missing
    if not hasattr(ToDo, 'note'):
        with db.engine.connect() as con:
            con.execute('ALTER TABLE todo ADD COLUMN note VARCHAR(500)')
    if not hasattr(ToDo, 'due_date'):
        with db.engine.connect() as con:
            con.execute('ALTER TABLE todo ADD COLUMN due_date VARCHAR(10)')

MOTIVATIONAL_QUOTES = [
    "The secret of getting ahead is getting started.",
    "Don't watch the clock; do what it does. Keep going.",
    "It always seems impossible until it's done.",
    "Success is the sum of small efforts, repeated day in and day out.",
    "You don't have to be great to start, but you have to start to be great.",
    "The future depends on what you do today.",
    "Dream big. Start small. Act now.",
    "Push yourself, because no one else is going to do it for you.",
    "Great things never come from comfort zones.",
    "Don't stop when you're tired. Stop when you're done."
]

def reset_todos_if_new_day():
    today = datetime.now().strftime('%Y-%m-%d')
    meta = Meta.query.first()
    if meta.last_reset != today:
        # Reset all todos to uncompleted
        ToDo.query.update({ToDo.completed: False})
        meta.last_reset = today
        db.session.commit()

def get_filtered_todos(search, filter_status):
    q = ToDo.query
    if search:
        q = q.filter((ToDo.title.ilike(f'%{search}%')) | (ToDo.note.ilike(f'%{search}%')))
    if filter_status == 'completed':
        q = q.filter_by(completed=True)
    elif filter_status == 'incomplete':
        q = q.filter_by(completed=False)
    return q.all()

@app.route('/', methods=['GET'])
def index():
    reset_todos_if_new_day()
    search = request.args.get('search', '')
    filter_status = request.args.get('filter', 'all')
    todos = get_filtered_todos(search, filter_status)
    quote = random.choice(MOTIVATIONAL_QUOTES)
    completed_count = sum(1 for t in todos if t.completed)
    overdue_ids = [t.id for t in todos if t.due_date and not t.completed and t.due_date < date.today().strftime('%Y-%m-%d')]
    return render_template('index.html', todos=todos, quote=quote, search=search, filter_status=filter_status, completed_count=completed_count, total_count=len(todos), overdue_ids=overdue_ids)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    note = request.form.get('note')
    due_date = request.form.get('due_date')
    if title:
        new_todo = ToDo(title=title, note=note, due_date=due_date)
        db.session.add(new_todo)
        db.session.commit()
        flash('Task added!', 'success')
    return redirect(url_for('index'))

@app.route('/edit/<int:todo_id>', methods=['GET', 'POST'])
def edit(todo_id):
    todo = ToDo.query.get_or_404(todo_id)
    if request.method == 'POST':
        todo.title = request.form.get('title')
        todo.note = request.form.get('note')
        todo.due_date = request.form.get('due_date')
        db.session.commit()
        flash('Task updated!', 'info')
        return redirect(url_for('index'))
    return render_template('edit.html', todo=todo)

@app.route('/complete/<int:todo_id>')
def complete(todo_id):
    todo = ToDo.query.get_or_404(todo_id)
    todo.completed = True
    db.session.commit()
    flash('Task completed!', 'success')
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = ToDo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
    flash('Task deleted!', 'danger')
    return redirect(url_for('index'))

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/export')
def export():
    todos = ToDo.query.all()
    data = [{
        'Title': t.title,
        'Note': t.note or '',
        'Completed': 'Yes' if t.completed else 'No',
        'Due Date': t.due_date or ''
    } for t in todos]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='ToDos')
    output.seek(0)
    flash('Tasks exported to Excel!', 'info')
    return send_file(output, download_name='todos.xlsx', as_attachment=True)

app = app  # For Vercel 