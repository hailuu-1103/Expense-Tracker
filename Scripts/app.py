from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.Integer, nullable=False)
    month = db.Column(db.Integer, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(20), nullable=False)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    categories = ['Food', 'Work_Study', 'Transportation', 'Monthly_Payment', 'Enjoyable', 'Others']
    categorized_expenses = {category: Expense.query.filter_by(category=category).all() for category in categories}

    # Pre-process the data
    for expenses in categorized_expenses.values():
        for expense in expenses:
            expense.day = int(expense.day)
            expense.month = int(expense.month)

    return render_template('index.html', categorized_expenses=categorized_expenses)

@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            day = date_obj.day
            month = date_obj.month
            year = date_obj.year
            description = request.form['description']
            amount = float(request.form['amount'])
            category = request.form['category']
            new_expense = Expense(day=day, month=month, year=year, description=description, amount=amount, category=category)
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('add_expense'))
    return render_template('add_expense.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%Y-%m-%d')
            expense.day = date_obj.day
            expense.month = date_obj.month
            expense.year = date_obj.year
            expense.description = request.form['description']
            expense.amount = float(request.form['amount'])
            expense.category = request.form['category']
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('edit_expense', id=id))
    return render_template('edit_expense.html', expense=expense)

@app.route('/delete/<int:id>')
def delete_expense(id):
    try:
        expense = Expense.query.get_or_404(id)
        db.session.delete(expense)
        db.session.commit()
        flash('Expense deleted successfully!', 'success')
    except Exception as e:
        flash(f'Error: {e}', 'error')
    return redirect(url_for('index'))

@app.route('/summary')
def summary():
    expenses = Expense.query.all()
    summary = {}
    for expense in expenses:
        if expense.category in summary:
            summary[expense.category] += expense.amount
        else:
            summary[expense.category] = expense.amount

    categories = list(summary.keys())
    amounts = list(summary.values())

    return render_template('summary.html', categories=categories, amounts=amounts)

if __name__ == '__main__':
    app.run(debug=True)
