import db
from datetime import datetime

def addCategory(nameOfCategory, typeOfCategory):
    tableName = "Categories"
    columnWillInsert = "(category_name, category_type)"
    valueWillInsert = (nameOfCategory, typeOfCategory)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

def deleteCategory(nameOfCategory):
    tableName = "Categories"
    db.deleteInfoIntoTable(tableName, f'category_name = "{nameOfCategory}"')


def addAccount(nameOfAccount, typeOfAccount, initial_balance = 0):
    tableName = "Accounts"
    columnWillInsert = "(account_name, account_type, initial_balance)"
    valueWillInsert = (nameOfAccount, typeOfAccount, initial_balance)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)

def deleteAccount(nameOfAccount):
    tableName = "Accounts"
    db.deleteInfoIntoTable(tableName, f'account_name = "{nameOfAccount}"')


def addTransaction(description, category, amount, account, transfer_group_id = None, date_input = None):
    tableName = "Transactions"

    columnWillInsert = "(transaction_date, description, category_id, amount, account_id, transfer_group_id)"
    
    raw_cat = db.getDB("Categories", "category_id", f'category_name = "{category}"')
    if raw_cat:
        category_id = raw_cat[0][0]
    else:
        print(f"ไม่พบหมวดหมู่: {category}")
        return 

    raw_acc = db.getDB("Accounts", "account_id", f'account_name = "{account}"')
    if raw_acc:
        account_id = raw_acc[0][0]
    else:
        print(f"ไม่พบกระเป๋า: {account}")
        return

    
    if date_input is None:
        record_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    else:
        # กรณีอยากย้อนอดีต ก็รับค่ามา (ต้อง format ให้ตรงนะ)
        record_time = date_input

    valueWillInsert = (record_time, description, category_id, amount, account_id, transfer_group_id)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)