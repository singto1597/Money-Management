import db
import read_json_data as js_file

def initDB():
    conn = db.connectToDatabase()
    cursor = conn.cursor()
    
    default_tables = js_file.openFile_as_key("tables")

    for table in default_tables:
        sqlCommand = "CREATE TABLE IF NOT EXISTS " + table["tableName"] + "("
        for i, column in enumerate(table["columns"]):
            sqlCommand += column["variableName"] + " " + column["variableType"]
            if i < len(table['columns']) - 1:
                sqlCommand += ", "
        sqlCommand += ");"
        cursor.execute(sqlCommand)

    conn.commit()
    cursor.close()
    conn.close()

def initCategories_default():
    default_categories = js_file.openFile_as_key("default_categories")
    for category in default_categories:
        tableName = "Categories"
        columnWillInsert = "(category_name, category_type)"
        valueWillInsert = (category["name"], category["type"])
        db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)


def initAccounts_default():
    default_Accounts = js_file.openFile_as_key("default_accounts")
    for account in default_Accounts:
        tableName = "Accounts"
        columnWillInsert = "(account_name, account_type, account_balance)"
        valueWillInsert = (account["name"], account["type"], account["initial_balance"])
        db.insertInfoIntoTable(tableName, columnWillInsert, valueWillInsert)


def initializeApp():
    initDB()
    initCategories_default()
    initAccounts_default()