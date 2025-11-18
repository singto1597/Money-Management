import sqlite3

def connectToDatabase():
    conn = sqlite3.connect("db/database.db")
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

def deleteInfoIntoTable(tableName,conditionOfColumn = None):
    conn = connectToDatabase()
    cursor = conn.cursor()
    
    sqlCommand = f"DELETE FROM {tableName} "
    if conditionOfColumn:
        sqlCommand += f" WHERE {conditionOfColumn}"
    else:
        print("Please input the condition!!")
        return
    # print(sqlCommand)
    cursor.execute(sqlCommand)
    
    conn.commit()

    cursor.close()
    conn.close()

def getDB(tableName, column = "*", condition = None):
    conn = connectToDatabase()
    cursor = conn.cursor()

    sqlCommand = f"SELECT {column} FROM {tableName} "

    if condition:
        sqlCommand += f"WHERE {condition};"
    else:
        sqlCommand += ";"

    cursor.execute(sqlCommand)
    result = cursor.fetchall()


    cursor.close()
    conn.close()
    return result