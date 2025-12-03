import sqlite3
import os
import sys

def get_base_path():
    """
    หา path สำหรับเก็บไฟล์ Database
    """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))

def connectToDatabase():
    base_dir = get_base_path() 
    
    db_path = os.path.join(base_dir, "db", "database.db")
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row 
    return conn
def insertInfoIntoTable(tableName, tupleOfColumn_WillInsert, tupleOfInfo_WillInsert_Values):
    # tableName = "Transactions"
    # columnWillInsert = "(amount, description, account_id, category_id)"
    # valueWillInsert = (100, "กินข้าว", 1, 3)
    
    conn = connectToDatabase()
    cursor = conn.cursor()
    num_columns = len(tupleOfInfo_WillInsert_Values)
    placeholders = "(" + ", ".join(["?"] * num_columns) + ")"

    sql_command = f"INSERT OR IGNORE INTO {tableName} {tupleOfColumn_WillInsert} VALUES {placeholders};"

    cursor.execute(sql_command, tupleOfInfo_WillInsert_Values)

    conn.commit()

    cursor.close()
    conn.close()
def changeInfoIntoTable(tableName, tupleOfColumn_WillChange, tupleOfInfo_WillChange_Values, conditionOfColumn = None):
    # tableName = "Categories"
    # columnWillChange = ("category_name", "category_type")
    # valueWillChange = ('"testChange"', '"type"')
    conn = connectToDatabase()
    cursor = conn.cursor()
    num_columns = len(tupleOfInfo_WillChange_Values)
    
    # UPDATE Table SET name = "ddd", type = "sss" WHERE 
    set_clause = ", ".join([f"{col} = ?" for col in tupleOfColumn_WillChange])

    sqlCommand = f"UPDATE {tableName} SET {set_clause}"

    if conditionOfColumn:
        sqlCommand += f" WHERE {conditionOfColumn}"
    else:
        print("Please input the condition!!")
        return
    # print(sqlCommand)
    cursor.execute(sqlCommand, tupleOfInfo_WillChange_Values)
    
    conn.commit()

    cursor.close()
    conn.close()
def deleteInfoIntoTable(tableName, conditionOfColumn=None, conditionValues=None):
    """
    conditionOfColumn: เช่น "account_name = ?"
    conditionValues: tuple ของค่าที่จะใส่ใน ? เช่น ("John's Wallet",)
    """
    conn = connectToDatabase()
    cursor = conn.cursor()
    
    sqlCommand = f"DELETE FROM {tableName} "
    
    if conditionOfColumn and conditionValues:
        sqlCommand += f" WHERE {conditionOfColumn}"
        cursor.execute(sqlCommand, conditionValues) 
    else: 
        print("Error: Condition is required for delete!")
        return
    
    conn.commit()
    cursor.close()
    conn.close()
def getDB(tableName, column="*", condition=None, conditionValues=None):

    # id = ?
    # conditionValues = 1
    conn = connectToDatabase()
    cursor = conn.cursor()

    sqlCommand = f"SELECT {column} FROM {tableName} "

    if condition and conditionValues:
        sqlCommand += f" WHERE {condition}"
        cursor.execute(sqlCommand, conditionValues)
    elif condition:
        sqlCommand += f" WHERE {condition}"
        cursor.execute(sqlCommand)
    else:
        cursor.execute(sqlCommand)

    result = [dict(row) for row in cursor.fetchall()]

    cursor.close()
    conn.close()
    return result