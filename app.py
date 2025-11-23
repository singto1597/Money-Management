import customtkinter as ctk
import db
class transaction(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        accounts = db.getDB(tableName = "Accounts", column = "account_name")
        income_categories = db.getDB(tableName = "Categories", column = "category_name", condition = "category_type = ?", conditionValues = ("income",))
        expense_categories = db.getDB(tableName = "Categories", column = "category_name", condition = "category_type = ?", conditionValues = ("expense",))

        list_accounts = ["-"]     
        list_income_categories = ["-"]
        list_expense_categories = ["-"]
        for account in accounts:
            list_accounts.append(account["account_name"])


        for category in income_categories:
            list_income_categories.append(category["category_name"])
        for category in expense_categories:
            list_expense_categories.append(category["category_name"])

        self.account_select = ctk.CTkComboBox(master = self, values=list_accounts, command = self.on_select_account)
        self.account_select.grid(row=1, column=0, padx=20, pady=10, sticky="w")

        self.type_select_income = ctk.CTkComboBox(master = self, values=list_income_categories, command = self.on_select_type)
        self.type_select_income.grid(row=2, column=0, padx=20, pady=10, sticky="w")

        self.type_select_expense = ctk.CTkComboBox(master = self, values=list_expense_categories, command = self.on_select_type)
        self.type_select_expense.grid(row=3, column=0, padx=20, pady=10, sticky="w")


    def on_select_account(self, choise):
        if choise != "-":
            self.id = db.getDB(tableName = "Accounts", column = "account_id", condition = "account_name = ?", conditionValues = (choise, ))
        else:
            return
        print ("account id = ", self.id[0]["account_id"])
    def on_select_type(self, choise):
        if choise != "-":
            self.id = db.getDB(tableName = "Categories", column = "category_id", condition = "category_name = ?", conditionValues = (choise, ))
        else:
            return
        
        print ("category id = ", self.id[0]["category_id"])

class moneyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("800x600")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.balance = 0
        self.trans = transaction(master = self)
        self.trans.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)


if __name__ == "__main__":
    app = moneyApp()
    app.mainloop()
