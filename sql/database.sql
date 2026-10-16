CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE expenses (
    expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TEXT NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    category_id INTEGER NOT NULL,
    description TEXT,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE TABLE budgets (
    budget_id INTEGER PRIMARY KEY AUTOINCREMENT,
    year INTEGER NOT NULL,
    month INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL CHECK (amount > 0),
    UNIQUE (year, month, category_id),
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);

CREATE INDEX idx_expenses_category ON expenses(category_id);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_budgets_category ON budgets(category_id);

INSERT INTO categories (name) VALUES
('Food'),
('Transport'),
('Entertainment'),
('Utilities');

INSERT INTO expenses (expense_date, amount, category_id, description) VALUES
('2025-01-15', 25.00, 1, 'Lunch'),
('2025-01-16', 12.50, 2, 'Bus ticket'),
('2025-01-17', 45.00, 3, 'Cinema'),
('2025-01-18', 80.00, 1, 'Groceries'),
('2025-02-01', 30.00, 1, 'Dinner'),
('2025-02-02', 15.00, 2, 'Taxi');

INSERT INTO budgets (year, month, category_id, amount) VALUES
(2025, 1, 1, 300.00),
(2025, 1, 2, 100.00),
(2025, 1, 3, 50.00),
(2025, 2, 1, 250.00),
(2025, 2, 2, 120.00);