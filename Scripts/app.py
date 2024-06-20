from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from enum import Enum
import pandas as pd

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///expenses.db'
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)


class CategoryEnum(Enum):
    Food = 'Food'
    Work_Study = 'Work_Study'
    Transportation = 'Transportation'
    Monthly_Payment = 'Monthly_Payment'
    Enjoyable = 'Enjoyable'
    Others = 'Others'


class PaymentMethodEnum(Enum):
    Banking = 'Banking'
    Cash = 'Cash'


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    description = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.Enum(CategoryEnum), nullable=False)
    payment_method = db.Column(db.Enum(PaymentMethodEnum), nullable=False)


with app.app_context():
    db.create_all()


# Custom filter to format the amount
def format_vnd(value):
    return "{:,.0f} VNĐ".format(value).replace(',', '.')


app.jinja_env.filters['format_vnd'] = format_vnd


@app.route('/')
def index():
    categories = [category.value for category in CategoryEnum]
    categorized_expenses = {category: Expense.query.filter_by(category=category).all() for category in categories}

    # Calculate total expenses for each month in 2023
    monthly_expenses_2023 = [0] * 12
    expenses_2023 = Expense.query.filter(Expense.date.between('2023-01-01', '2023-12-31')).all()
    for expense in expenses_2023:
        month = expense.date.month
        amount = expense.amount
        monthly_expenses_2023[month - 1] += amount

    # Calculate total expenses for each month in 2024
    monthly_expenses_2024 = [0] * 12
    expenses_2024 = Expense.query.filter(Expense.date.between('2024-01-01', '2024-12-31')).all()
    for expense in expenses_2024:
        month = expense.date.month
        amount = expense.amount
        monthly_expenses_2024[month - 1] += amount

    return render_template('index.html', categorized_expenses=categorized_expenses, monthly_expenses_2023=monthly_expenses_2023, monthly_expenses_2024=monthly_expenses_2024)


@app.route('/add', methods=['GET', 'POST'])
def add_expense():
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')  # Change the format to match the new input format
            description = request.form['description']
            amount = float(request.form['amount'])
            category = request.form['category']
            payment_method = request.form['payment_method']
            new_expense = Expense(date=date_obj, description=description, amount=amount, category=category, payment_method=payment_method)
            db.session.add(new_expense)
            db.session.commit()
            flash('Expense added successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('add_expense'))
    categories = [category.value for category in CategoryEnum]
    payment_methods = [method.value for method in PaymentMethodEnum]
    return render_template('add_expense.html', categories=categories, payment_methods=payment_methods)


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_expense(id):
    expense = Expense.query.get_or_404(id)
    if request.method == 'POST':
        try:
            date_str = request.form['date']
            date_obj = datetime.strptime(date_str, '%d/%m/%Y')
            expense.date = date_obj
            expense.description = request.form['description']
            expense.amount = float(request.form['amount'])
            expense.category = request.form['category']
            expense.payment_method = request.form['payment_method']
            db.session.commit()
            flash('Expense updated successfully!', 'success')
            return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
            return redirect(url_for('edit_expense', id=id))
    categories = [category.value for category in CategoryEnum]
    payment_methods = [method.value for method in PaymentMethodEnum]
    return render_template('edit_expense.html', expense=expense, categories=categories, payment_methods=payment_methods)


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


@app.route('/import', methods=['GET', 'POST'])
def import_data():
    preview_data = []
    if request.method == 'POST':
        try:
            file = request.files['file']
            if file.filename.endswith('.xlsx') or file.filename.endswith('.xls'):
                df = pd.read_excel(file)
            elif file.filename.endswith('.csv'):
                df = pd.read_csv(file)
            else:
                flash('Unsupported file format. Please upload a .xlsx, .xls, or .csv file.', 'error')
                return redirect(url_for('import_data'))

            if 'preview' in request.form:
                preview_data = df.to_dict('records')
                session['preview_data'] = preview_data
            elif 'import' in request.form:
                preview_data = session.get('preview_data', [])
                for row in preview_data:
                    date = datetime.strptime(str(row['Date']), '%d/%m/%Y')
                    description = row['Description']
                    amount = float(row['Amount'])
                    category = row['Category']
                    payment_method = row['Payment Method']
                    new_expense = Expense(date=date, description=description, amount=amount, category=category, payment_method=payment_method)
                    db.session.add(new_expense)
                print(db.session)
                db.session.commit()
                flash('Data imported successfully!', 'success')
                return redirect(url_for('index'))
        except Exception as e:
            flash(f'Error: {e}', 'error')
    return render_template('import.html', preview_data=preview_data)


if __name__ == '__main__':
    app.run(debug=True)
