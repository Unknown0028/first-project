import os
import random
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, send_file
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

db = SQLAlchemy(app)

class Meta(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    last_reset = db.Column(db.String(10), default="")  # YYYY-MM-DD

class ToDo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    note = db.Column(db.String(500), nullable=True)
    completed = db.Column(db.Boolean, default=False)

with app.app_context():
    db.create_all()
    # Ensure Meta row exists
    if not Meta.query.first():
        db.session.add(Meta(last_reset=""))
        db.session.commit()
    # Add note column if missing (for upgrades)
    if not hasattr(ToDo, 'note'):
        with db.engine.connect() as con:
            con.execute('ALTER TABLE todo ADD COLUMN note VARCHAR(500)')

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

@app.route('/')
def index():
    reset_todos_if_new_day()
    todos = ToDo.query.all()
    quote = random.choice(MOTIVATIONAL_QUOTES)
    return render_template('index.html', todos=todos, quote=quote)

@app.route('/add', methods=['POST'])
def add():
    title = request.form.get('title')
    note = request.form.get('note')
    if title:
        new_todo = ToDo(title=title, note=note)
        db.session.add(new_todo)
        db.session.commit()
    return redirect(url_for('index'))

@app.route('/complete/<int:todo_id>')
def complete(todo_id):
    todo = ToDo.query.get_or_404(todo_id)
    todo.completed = True
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = ToDo.query.get_or_404(todo_id)
    db.session.delete(todo)
    db.session.commit()
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
        'Completed': 'Yes' if t.completed else 'No'
    } for t in todos]
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='ToDos')
    output.seek(0)
    return send_file(output, download_name='todos.xlsx', as_attachment=True)

app = app  # For Vercel 