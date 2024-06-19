import sqlite3
import matplotlib.pyplot as plt
from collections import defaultdict
import mplcursors


def connect():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    # Drop the existing table if it exists
    c.execute('DROP TABLE IF EXISTS expenses')

    # Create the table
    c.execute('''
        CREATE TABLE expenses (
            Day TEXT,
            Month TEXT,
            Year TEXT,
            Description TEXT,
            Amount TEXT,
            Category TEXT CHECK(Category IN ('Food', 'Work_Study', 'Transportation', 'Monthly_Payment', 'Enjoyable', 'Others'))
        )
    ''')
    conn.commit()
    return conn


def read_all_data(conn):
    c = conn.cursor()
    c.execute("SELECT * FROM expenses")
    rows = c.fetchall()
    for row in rows:
        print(row)
    return rows


def add_expense(conn, data):
    c = conn.cursor()
    c.executemany('''
        INSERT INTO expenses (Day, Month, Year, Description, Amount, Category) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', data)
    conn.commit()


def edit_expense(conn, key, new_data):
    c = conn.cursor()
    c.execute('''
        UPDATE expenses 
        SET Day = ?, Month = ?, Year = ?, Description = ?, Amount = ?, Category = ?
        WHERE rowid = ?
    ''', (*new_data, key))
    conn.commit()


def remove_expense(conn, key):
    c = conn.cursor()
    c.execute('DELETE FROM expenses WHERE rowid = ?', (key,))
    conn.commit()


def parse_amount(amount_str):
    # Convert "385.000,00 đ" to 385000.00
    amount_str = amount_str.replace(' đ', '').replace('.', '').replace(',', '.')
    return float(amount_str)


def summarize_expenses_by_category(conn):
    c = conn.cursor()
    c.execute("SELECT Category, Amount FROM expenses")
    rows = c.fetchall()

    summary = defaultdict(float)
    for row in rows:
        category, amount = row
        parsed_amount = parse_amount(amount)
        summary[category] += parsed_amount

    return summary


def create_bar_chart(summary):
    categories = list(summary.keys())
    expenses = list(summary.values())

    plt.bar(categories, expenses)
    plt.xlabel('Category')
    plt.ylabel('Total Expense (VND)')
    plt.title('Expenses by Category')
    plt.xticks(rotation=45)

    # Format y-axis to display amounts in a human-readable format
    formatter = plt.FuncFormatter(lambda x, _: f'{x:,.0f}')
    plt.gca().yaxis.set_major_formatter(formatter)

    # Add mplcursors to show the exact amount on hover
    cursor = mplcursors.cursor(hover=True)
    cursor.connect("add", lambda sel: sel.annotation.set_text(f'{categories[sel.index]}: {expenses[sel.index]:,.0f} VND'))

    plt.tight_layout()
    plt.show()


def print_total_for_category(conn, category):
    summary = summarize_expenses_by_category(conn)
    total = summary.get(category, 0)
    print(f'Total expense for {category}: {total:,.0f} VND')


# Data to be inserted
data = [
    ("06", "06", "2024", "tiền ăn trưa tháng 5", "385.000,00 đ", "Monthly_Payment"),
    ("16", "06", "2024", "tiền nhà", "1.000.000,00 đ", "Monthly_Payment"),
    ("16", "06", "2024", "tiền sinh hoạt phòng", "617.000,00 đ", "Monthly_Payment"),
    ("09", "06", "2024", "đổ xăng", "60.000,00 đ", "Transportation"),
    ("15", "06", "2024", "thay dầu xe máy", "100.000,00 đ", "Transportation"),
    ("05", "06", "2024", "sửa màn hình điện thoại", "450.000,00 đ", "Others"),
    ("05", "06", "2024", "tiền nhà", "1.000.000,00 đ", "Monthly_Payment"),
    ("16", "06", "2024", "tiền học tiếng anh", "4.400.000,00 đ", "Work_Study"),
    ("11", "06", "2024", "học cầu lông tháng 6", "600.000,00 đ", "Work_Study"),
    ("07", "06", "2024", "chatgpt plus", "410.000,00 đ", "Food"),
    ("05", "06", "2024", "bánh mì", "25.000,00 đ", "Food"),
    ("06", "06", "2024", "ăn sáng", "27.000,00 đ", "Food"),
    ("05", "06", "2024", "ăn trưa", "60.000,00 đ", "Food"),
    ("07", "06", "2024", "ăn sáng + 5 highlands", "73.000,00 đ", "Food"),
    ("09", "06", "2024", "chơi cầu lông", "60.000,00 đ", "Enjoyable"),
    ("10", "06", "2024", "bida", "116.000,00 đ", "Enjoyable")
]

# Usage example
conn = connect()
add_expense(conn, data)
read_all_data(conn)

# Summarize expenses by category
summary = summarize_expenses_by_category(conn)

# Create the bar chart
create_bar_chart(summary)

# Print the total expense for a specific category
print_total_for_category(conn, 'Work_Study')

conn.close()
