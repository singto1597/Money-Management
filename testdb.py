# test_system.py
import db_function
import db
import initial_db as initDB

# 1. ลองสร้าง DB และข้อมูลเริ่มต้น
print("--- Init DB ---")
initDB.initializeApp()

# 2. ลองเพิ่มข้อมูลที่มีอักขระพิเศษ (ทดสอบความแข็งแกร่ง)
# print("--- Test Special Character ---")
# db_function.addAccount("M's Wallet", "Asset", 500) # ถ้าไม่พัง แสดงว่าผ่าน

# 3. ลองดึงข้อมูลมาดู
# print("--- Test Fetch ---")
# accounts = db.getDB("Accounts")
# print(accounts) 
# ดูว่ามันออกมาเป็น [{'account_name': "M's Wallet", ...}] หรือไม่
# choise = "กระเป๋าตังค์"
# id = db.getDB(tableName = "Accounts", column = "account_id", condition = "account_name = ?", conditionValues = (choise,))
# print ("id = ", id[0]["account_id"])
# # 4. ลองลบ
# db_function.deleteAccount("M's Wallet")