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
    columnWillInsert = "(account_name, account_type, account_balance)"
    valueWillInsert = (nameOfAccount, typeOfAccount, initial_balance)
    db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)
    if initial_balance > 0:
        conn = db.connectToDatabase()
        cursor = conn.cursor()
        cursor.execute("SELECT account_id FROM Accounts WHERE account_name = ?", (nameOfAccount,))
        acc_id = cursor.fetchone()['account_id']
        conn.close()

        addTransaction(
            description="ยอดยกมา (Initial Balance)", 
            category_id=13,
            amount=initial_balance, 
            account_id=acc_id
        )
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
def transferMoney(amount, from_acc_id, to_acc_id, desc="โอนเงิน", date_input=None):
    conn = db.connectToDatabase()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT account_name FROM Accounts WHERE account_id = ?", (from_acc_id,))
        from_acc_name = cursor.fetchone()['account_name']
        
        cursor.execute("SELECT account_name FROM Accounts WHERE account_id = ?", (to_acc_id,))
        to_acc_name = cursor.fetchone()['account_name']

        cursor.execute("SELECT category_id FROM Categories WHERE category_type='transfer_from'") # หรือ transfrom_from ตาม DB คุณ
        cat_out_data = cursor.fetchone()
        cat_out = cat_out_data['category_id'] if cat_out_data else None
        
        cursor.execute("SELECT category_id FROM Categories WHERE category_type='transfer_to'") # หรือ transfrom_to ตาม DB คุณ
        cat_in_data = cursor.fetchone()
        cat_in = cat_in_data['category_id'] if cat_in_data else None

        record_time = date_input if date_input else datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        cursor.execute("SELECT MAX(transfer_group_id) FROM Transactions")
        row = cursor.fetchone()
        # ถ้าไม่มีข้อมูล (None) ให้เริ่มที่ 0, ถ้ามีให้เอาค่าเดิมมา
        last_group_id = row[0] if row[0] is not None else 0
        new_group_id = last_group_id + 1

        cursor.execute("""
            INSERT INTO Transactions (transaction_date, description, category_id, amount, account_id, transfer_group_id) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (record_time, f"โอนไป {to_acc_name} ({desc})", cat_out, -amount, from_acc_id, new_group_id))
        
        cursor.execute("UPDATE Accounts SET account_balance = account_balance - ? WHERE account_id = ?", (amount, from_acc_id))

        # [ขาเข้า]
        cursor.execute("""
            INSERT INTO Transactions (transaction_date, description, category_id, amount, account_id, transfer_group_id) 
            VALUES (?, ?, ?, ?, ?, ?)""",
            (record_time, f"ได้รับจาก {from_acc_name} ({desc})", cat_in, amount, to_acc_id, new_group_id))
        
        cursor.execute("UPDATE Accounts SET account_balance = account_balance + ? WHERE account_id = ?", (amount, to_acc_id))
        conn.commit()
        print(f"Transfer Success: {from_acc_name} -> {to_acc_name} ({amount})")
        
    except Exception as e:
        conn.rollback()
        print(f"Transfer Failed: {e}")
    finally:
        conn.close()
def getTransactionsByDateRange(start_date_str, end_date_str, account_id = None):
    # start_date_str: "2023-11-20"
    # end_date_str: "2023-11-26"
    
    start_full = f"{start_date_str} 00:00:00"
    end_full = f"{end_date_str} 23:59:59"
    

    conn = db.connectToDatabase()
    cursor = conn.cursor()
    if not account_id:
        sql = """
            SELECT T.transaction_id, T.transaction_date, T.description, T.amount, 
                C.category_name, C.category_type, A.account_name
            FROM Transactions T
            LEFT JOIN Categories C ON T.category_id = C.category_id
            JOIN Accounts A ON T.account_id = A.account_id
            WHERE T.transaction_date BETWEEN ? AND ? 
            ORDER BY T.transaction_date DESC
        """
        
        cursor.execute(sql, (start_full, end_full))
    else:
        sql = """
            SELECT T.transaction_id, T.transaction_date, T.description, T.amount, 
                C.category_name, C.category_type, A.account_name
            FROM Transactions T
            LEFT JOIN Categories C ON T.category_id = C.category_id
            JOIN Accounts A ON T.account_id = A.account_id
            WHERE T.account_id = ? AND T.transaction_date BETWEEN ? AND ? 
            ORDER BY T.transaction_date DESC
        """
        
        cursor.execute(sql, (account_id, start_full, end_full))
    result = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return result
def deleteTransaction(transaction_id):
    conn = db.connectToDatabase()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM Transactions WHERE transaction_id = ?", (transaction_id,))
        conn.commit()
    except Exception as e:
        print(f"Error deleting: {e}")
    finally:
        conn.close()
def updateTransaction(transaction_id, description, amount):

    conn = db.connectToDatabase()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Transactions 
            SET description = ?, amount = ? 
            WHERE transaction_id = ?
        """, (description, amount, transaction_id))
        conn.commit()
    except Exception as e:
        print(f"Error updating: {e}")
    finally:
        conn.close()
def editTransactionSafe(t_id, new_desc, new_amount, new_account_id=None, new_category_id=None):
    conn = db.connectToDatabase()
    cursor = conn.cursor()
    try:
        sql_get_old = """
            SELECT T.amount, T.account_id, T.category_id, C.category_type 
            FROM Transactions T
            JOIN Categories C ON T.category_id = C.category_id
            WHERE T.transaction_id = ?
        """
        cursor.execute(sql_get_old, (t_id,))
        old_data = cursor.fetchone()
        
        if not old_data:
            print("Error: Transaction not found")
            return

        old_amount = old_data['amount']
        old_acc_id = old_data['account_id']
        old_type = old_data['category_type'].strip().lower()
        
        final_acc_id = new_account_id if new_account_id else old_acc_id
        final_cat_id = new_category_id if new_category_id else old_data['category_id']

        if old_type == 'expense' or old_type == 'transfer_from':
            cursor.execute("UPDATE Accounts SET account_balance = account_balance + ? WHERE account_id = ?", (old_amount, old_acc_id))
        elif old_type == 'income' or old_type == 'transfer_to':
            cursor.execute("UPDATE Accounts SET account_balance = account_balance - ? WHERE account_id = ?", (old_amount, old_acc_id))

        cursor.execute("SELECT category_type FROM Categories WHERE category_id = ?", (final_cat_id,))
        new_cat_data = cursor.fetchone()
        new_type = new_cat_data['category_type'].strip().lower()

        sql_update_t = """
            UPDATE Transactions 
            SET description = ?, amount = ?, account_id = ?, category_id = ?
            WHERE transaction_id = ?
        """
        cursor.execute(sql_update_t, (new_desc, new_amount, final_acc_id, final_cat_id, t_id))

        if new_type == 'expense' or new_type == 'transfer_from':
            cursor.execute("UPDATE Accounts SET account_balance = account_balance - ? WHERE account_id = ?", (new_amount, final_acc_id))
        elif new_type == 'income' or new_type == 'transfer_to':
            cursor.execute("UPDATE Accounts SET account_balance = account_balance + ? WHERE account_id = ?", (new_amount, final_acc_id))

        conn.commit()
        print(f"Edit Success: Reverted {old_amount} ({old_type}) -> Applied {new_amount} ({new_type})")

    except Exception as e:
        conn.rollback()
        print(f"Edit Failed: {e}")
    
    finally:
        conn.close()
def getExpenseBreakdown():
    """ดึงข้อมูลสรุปรายจ่ายแยกตามหมวดหมู่ เรียงจากมากไปน้อย"""
    conn = db.connectToDatabase()
    cursor = conn.cursor()
    try:
        sql = """
            SELECT C.category_name, SUM(T.amount) as total_amount
            FROM Transactions T
            JOIN Categories C ON T.category_id = C.category_id
            WHERE C.category_type = 'expense' OR C.category_type = 'transfer_from'
            GROUP BY C.category_name
            ORDER BY total_amount DESC
        """
        cursor.execute(sql)
        result = cursor.fetchall()
        return result
    except Exception as e:
        print(f"Error getting breakdown: {e}")
        return []
    finally:
        conn.close()
def getAllAccountBalances():
    """ดึงข้อมูลบัญชีและยอดเงินล่าสุด"""
    accounts = db.getDB("Accounts")
    return accounts