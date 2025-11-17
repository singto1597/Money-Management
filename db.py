import sqlite3

def connectToDatabase():
    conn = sqlite3.connect("db/database.db")

    return conn

def initDB():
    conn = connectToDatabase()
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS Accounts(
                account_id INTEGER PRIMARY KEY,
                account_name TEXT,
                account_type TEXT,
                initial_balance REAL
                );
                ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Categories(
                category_id INTEGER PRIMARY KEY,
                category_name TEXT,
                category_type TEXT
                );
                ''')

    cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions(
                transaction_id INTEGER PRIMARY KEY,
                transaction_date DATETIME,
                description TEXT,
                category_id INTEGER,
                amount REAL,
                account_id INTEGER,
                transfer_group_id INTEGER
                );
                ''')

def insertInfoIntoTable(tableName, tupleOfColumn_WillInsert, tupleOfInfo_WillInsert_Values):
    conn = connectToDatabase()
    cursor = conn.cursor()
    num_columns = len(tupleOfInfo_WillInsert_Values)
    placeholders = "(" + ", ".join(["?"] * num_columns) + ")"

    sql_command = f"INSERT INTO {tableName} {tupleOfColumn_WillInsert} VALUES {placeholders};"

    cursor.execute(sql_command, tupleOfInfo_WillInsert_Values)

    conn.commit()

    cursor.close()
    conn.close()

