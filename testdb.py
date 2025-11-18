import db
import inital_db as initDB


initDB.initializeApp()

db.deleteInfoIntoTable("Categories", "category_id = 1")
# cursor.close()

