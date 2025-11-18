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
    sqlCommand = f"UPDATE {tableName} SET "
    for i in range(num_columns):
        column = tupleOfColumn_WillChange[i]
        info = tupleOfInfo_WillChange_Values[i]
        sqlCommand += f"{column} = {info} "
        if i < num_columns - 1:
            sqlCommand += ", "
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

def deleteInfoIntoTable(tableName,conditionOfColumn = None):
    # tableName = "Categories"
    # columnWillChange = ("category_name", "category_type")
    # valueWillChange = ('"testChange"', '"type"')
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

