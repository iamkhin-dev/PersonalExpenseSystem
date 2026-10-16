import sqlite3, os, sys

ROOT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sql")
DB, SQL_FILE = f"{ROOT}/expenses.db", f"{ROOT}/database.sql"

def conn():
    c = sqlite3.connect(DB)
    c.execute("PRAGMA foreign_keys = ON;")
    return c

def init():
    if not os.path.exists(DB):
        if not os.path.exists(SQL_FILE):
            sys.exit(f"Error: {SQL_FILE} not found.")
        with conn() as c, open(SQL_FILE) as f:
            c.executescript(f.read())

def cat_id(c, name):
    row = c.execute("SELECT category_id FROM categories WHERE name=?;", (name,)).fetchone()
    return row[0] if row else None

def input_float(prompt):
    try:
        v = float(input(prompt))
        return v if v > 0 else None
    except ValueError:
        return None

def input_date():
    d = input("Enter date (YYYY-MM-DD): ").strip()
    return d if len(d) == 10 and d[4] == '-' and d[7] == '-' else None

def input_month():
    m = input("Enter month (YYYY-MM): ").strip()
    if len(m) != 7 or m[4] != '-':
        return None
    try:
        y, mo = int(m[:4]), int(m[5:7])
        return (y, mo) if 1 <= mo <= 12 else None
    except ValueError:
        return None

def add_category():
    name = input("Enter category name: ").strip()
    if not name:
        print("Error: category name cannot be empty.")
        return
    with conn() as c:
        if cat_id(c, name):
            print("Error: category already exists.")
            return
        c.execute("INSERT INTO categories (name) VALUES (?);", (name,))
        print("Category inserted successfully.")

def insert_expense():
    date = input_date()
    if not date:
        print("Error: invalid date format.")
        return
    amount = input_float("Enter amount: ")
    if amount is None:
        print("Error: amount must be greater than zero.")
        return
    name = input("Enter category name: ").strip()
    with conn() as c:
        cid = cat_id(c, name)
        if cid is None:
            print("Error: category does not exist.")
            return
        desc = input("Enter description (optional): ").strip()
        c.execute("INSERT INTO expenses (expense_date, amount, category_id, description) VALUES (?,?,?,?);",
                  (date, amount, cid, desc))
        print("Expense inserted successfully.")

def define_budget():
    ym = input_month()
    if not ym:
        print("Error: invalid month format.")
        return
    y, m = ym
    name = input("Enter category name: ").strip()
    with conn() as c:
        cid = cat_id(c, name)
        if cid is None:
            print("Error: category does not exist.")
            return
        amount = input_float("Enter budget amount: ")
        if amount is None:
            print("Error: budget must be greater than zero.")
            return
        row = c.execute("SELECT budget_id FROM budgets WHERE year=? AND month=? AND category_id=?;", (y, m, cid)).fetchone()
        if row:
            c.execute("UPDATE budgets SET amount=? WHERE year=? AND month=? AND category_id=?;", (amount, y, m, cid))
        else:
            c.execute("INSERT INTO budgets (year, month, category_id, amount) VALUES (?,?,?,?);", (y, m, cid, amount))
        print("Monthly budget saved successfully.")

def report_total():
    with conn() as c:
        rows = c.execute("SELECT c.name, SUM(e.amount) FROM categories c "
                         "JOIN expenses e ON c.category_id = e.category_id "
                         "GROUP BY c.name ORDER BY c.name;").fetchall()
        print(f"{'Category':<20}{'Total Spent':>12}")
        print("-" * 32)
        for name, total in rows:
            print(f"{name:<20}{total:>12.2f}")

def report_budget():
    with conn() as c:
        rows = c.execute(
            "SELECT b.year, b.month, c.name, b.amount, COALESCE(SUM(e.amount),0) "
            "FROM budgets b JOIN categories c ON b.category_id = c.category_id "
            "LEFT JOIN expenses e ON c.category_id = e.category_id "
            "AND strftime('%Y', e.expense_date) = CAST(b.year AS TEXT) "
            "AND strftime('%m', e.expense_date) = printf('%02d', b.month) "
            "GROUP BY b.year, b.month, c.name, b.amount "
            "ORDER BY b.year, b.month, c.name;").fetchall()
        for y, m, name, budget, spent in rows:
            print(f"Month: {y}-{m:02d}\nCategory: {name}\nBudget: {budget:.2f}\nSpent: {spent:.2f}")
            print("Status:", "OVER BUDGET" if spent > budget else "WITHIN BUDGET")
            print("-" * 30)

def report_all():
    with conn() as c:
        rows = c.execute("SELECT e.expense_date, c.name, e.amount, e.description "
                         "FROM expenses e JOIN categories c ON e.category_id = c.category_id "
                         "ORDER BY e.expense_date;").fetchall()
        print(f"{'Date':<12}{'Category':<15}{'Amount':>10}  Description")
        print("-" * 60)
        for d, name, amt, desc in rows:
            print(f"{d:<12}{name:<15}{amt:>10.2f}  {desc or ''}")

def reports_menu():
    while True:
        print("\n--- Reports Menu ---")
        print("1. Total expenses per category")
        print("2. Monthly expenses vs budget")
        print("3. All expenses ordered by date")
        print("4. Return to main menu")
        match input("Choice: ").strip():
            case "1": report_total()
            case "2": report_budget()
            case "3": report_all()
            case "4": break
            case _: print("Invalid choice. Try again.")

def menu():
    while True:
        print("\n-------------------------")
        print("PERSONAL EXPENSE SYSTEM")
        print("-------------------------")
        print("1. Manage Categories")
        print("2. Insert Expense")
        print("3. Define Monthly Budget")
        print("4. View Reports")
        print("5. Exit")
        print("-------------------------")
        match input("Choice: ").strip():
            case "1": add_category()
            case "2": insert_expense()
            case "3": define_budget()
            case "4": reports_menu()
            case "5": 
                print("Exiting..."); 
                break
            case _: print("Invalid choice. Try again.")

if __name__ == "__main__":
    init()
    print("Welcome to the Personal Expense and Budget System!")
    menu()