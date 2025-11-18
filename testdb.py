import db
import initial_db as initDB
import db_function as appDB

initDB.initializeApp()

appDB.addTransaction("กินข้าว", "อาหาร", -100, "กระเป๋าตังค์", date_input = "2025-10-1 20:00:00")