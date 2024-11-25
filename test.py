import sqlite3


class Products:

    def __init__(self):
        self.db = sqlite3.connect('test.db')
        self.cur = self.db.cursor()

    def create_tables(self):
        self.cur.executescript(
            """CREATE TABLE IF NOT EXISTS Products (
            id INTEGER PRIMARY KEY,
            name VARCHAR,
            price DECIMAL);

            CREATE TABLE IF NOT EXISTS Sales (
            id INTEGER PRIMARY KEY,
            product_id INTEGER,
            quantity INTEGER,
            sale_date DATE);

            INSERT OR IGNORE INTO Products (id, name, price) 
            VALUES (1, 'Laptop', 1200.50), (2, 'Smartphone', 800.00), (3, 'Tablet', 300.75);

            INSERT OR IGNORE INTO Sales (id, product_id, quantity, sale_date)
            VALUES (1, 1, 3, '2024-11-20'), (2, 2, 5, '2024-11-21'), 
                   (3, 3, 2, '2024-11-22'), (4, 1, 1, '2024-11-23')"""
        )
        self.db.commit()

    def select_total(self):
        self.cur.execute("""SELECT name, SUM(quantity * price) AS total 
        FROM Products p 
        JOIN Sales s ON p.id = s.product_id
        GROUP BY name""")
        for name, total in self.cur.fetchall():
            print(name, total)

    def select_sales(self):
        self.cur.execute("""SELECT p.name, s.quantity, s.sale_date 
        FROM Products p 
        JOIN Sales s ON p.id = s.product_id
        WHERE CAST(strftime('%d', sale_date) AS INTEGER) BETWEEN 21 AND 23""")
        for row in self.cur.fetchall():
            print(row)


test = Products()
test.create_tables()
test.select_total()
test.select_sales()
