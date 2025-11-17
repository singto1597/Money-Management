import db
# cursor = db.connectToDatabase()

tableName = "Transactions"
columnWillInsert = "(amount, description, account_id, category_id)"
valueWillInsert = (100, "กินข้าว", 1, 3)

db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)


# cursor.close()

