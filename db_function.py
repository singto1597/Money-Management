import db
from datetime import datetime

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

def addTransaction(description, category_id, amount, account_id, transfer_group_id = None, date_input = None):
    tableName = "Transactions"

    columnWillInsert = "(transaction_date, description, category_id, amount, account_id, transfer_group_id)"
    
    if date_input is None:
        record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        record_time = date_input

    valueWillInsert = (record_time, description, category_id, amount, account_id, transfer_group_id)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

# def transferMoney(amount, from_acc_id, to_acc_id, desc="โอนเงิน"):