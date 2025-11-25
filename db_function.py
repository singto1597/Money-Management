import db
from datetime import datetime, timedelta

def addCategory(nameOfCategory, typeOfCategory):
    tableName = "Categories"
    columnWillInsert = "(category_name, category_type)"
    valueWillInsert = (nameOfCategory, typeOfCategory)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

def deleteCategory(nameOfCategory):
    tableName = "Categories"
    db.deleteInfoIntoTable(tableName, "category_name = ?", (nameOfCategory,))


def addAccount(nameOfAccount, typeOfAccount, initial_balance = 0):
    tableName = "Accounts"
    columnWillInsert = "(account_name, account_type, initial_balance)"
    valueWillInsert = (nameOfAccount, typeOfAccount, initial_balance)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

def deleteAccount(nameOfAccount):
    tableName = "Accounts"
    db.deleteInfoIntoTable(tableName, "account_name = ?", (nameOfAccount,))

def changeValueInAccount(columnWillChange, valueWillChange, conditionOfColumn = None):
    db.changeInfoIntoTable(tableName = "Accounts", tupleOfColumn_WillChange = (columnWillChange,), tupleOfInfo_WillChange_Values = (valueWillChange,), conditionOfColumn = conditionOfColumn)

def changeBalanceInAccount(balance, id):
    changeValueInAccount(columnWillChange = "account_balance", valueWillChange = balance, conditionOfColumn = f"account_id = {id}")

def addTransaction(description, category_id = None, amount = 0, account_id = None, transfer_group_id = None, date_input = None):
    tableName = "Transactions"

    columnWillInsert = "(transaction_date, description, category_id, amount, account_id, transfer_group_id)"
    
    if date_input is None:
        record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        record_time = date_input

    valueWillInsert = (record_time, description, category_id, amount, account_id, transfer_group_id)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

def transferMoney(amount, from_acc_id, to_acc_id, desc="โอนเงิน"):
    accounts_map_balance = { row["account_id"]: row["account_balance"] for row in db.getDB("Accounts") }
    from_acc_balance = accounts_map_balance[from_acc_id]
    to_acc_balance = accounts_map_balance[to_acc_id]
    addTransaction(description = f"โอนไป {to_acc_id} ({desc})", 
                   amount = amount, 
                   account_id = from_acc_id, 
                   transfer_group_id = 0)
    changeBalanceInAccount(balance = from_acc_balance - amount, 
                           id = from_acc_id)
    
    addTransaction(description = f"ได้รับจาก {from_acc_id} ({desc})", 
                   amount = amount, 
                   account_id = to_acc_id, 
                   transfer_group_id = 0)
    changeBalanceInAccount(balance = to_acc_balance + amount, 
                           id = to_acc_id)
    
def getTransactionsByDateRange(start_date_str, end_date_str):
    # start_date_str: "2023-11-20"
    # end_date_str: "2023-11-26"
    
    start_full = f"{start_date_str} 00:00:00"
    end_full = f"{end_date_str} 23:59:59"
    

    conn = db.connectToDatabase()
    cursor = conn.cursor()
    
    sql = """
        SELECT T.transaction_id, T.transaction_date, T.description, T.amount, 
               C.category_name, C.category_type, A.account_name
        FROM Transactions T
        JOIN Categories C ON T.category_id = C.category_id
        JOIN Accounts A ON T.account_id = A.account_id
        WHERE T.transaction_date BETWEEN ? AND ?
        ORDER BY T.transaction_date DESC
    """
    
    cursor.execute(sql, (start_full, end_full))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return result