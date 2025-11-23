import customtkinter as ctk
import db
class transaction(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # self.grid_columnconfigure(0, weight=0) 
        # self.grid_columnconfigure(1, weight=1)

        accounts = db.getDB(tableName = "Accounts", column = "account_name")
        income_categories = db.getDB(tableName = "Categories", column = "category_name", condition = "category_type = ?", conditionValues = ("income",))
        expense_categories = db.getDB(tableName = "Categories", column = "category_name", condition = "category_type = ?", conditionValues = ("expense",))

        list_accounts = []     
        list_income_categories = ["-"]
        list_expense_categories = ["-"]
        for account in accounts:
            list_accounts.append(account["account_name"])


        for category in income_categories:
            list_income_categories.append(category["category_name"])
        for category in expense_categories:
            list_expense_categories.append(category["category_name"])

        
        
        self.type_select_income = ctk.CTkComboBox(master = self, values=list_income_categories, command = self.on_select_type)
        self.type_select_expense = ctk.CTkComboBox(master = self, values=list_expense_categories, command = self.on_select_type)
        
        self.desc_text = ctk.CTkLabel(master = self, text = "รายการ")
        self.desc_entry = ctk.CTkEntry(master = self, placeholder_text="ซื้ออะไรมา??")

        self.type_text = ctk.CTkLabel(master = self, text = "ประเภท")
        self.income_type = ctk.CTkLabel(master = self, text = "รายรับ")
        self.expense_type = ctk.CTkLabel(master = self, text = "รายจ่าย")

        self.amount_text = ctk.CTkLabel(master = self, text = "จำนวน")
        self.amount_entry = ctk.CTkEntry(master = self, placeholder_text="ซื้อมาเท่าไหร่??")

        self.account_text = ctk.CTkLabel(master = self, text = "จาก")
        self.account_select = ctk.CTkComboBox(master = self, values=list_accounts, command = self.on_select_account)
        self.remaining_text = ctk.CTkLabel(master = self, text = "ตอนนี้คงเหลืออยู่ 100 บาท")

        self.submit_button = ctk.CTkButton(master = self, text="Submit")


        self.desc_text.grid(row=0, column=0, padx=20, pady=10, sticky="w")
        self.desc_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        self.type_text.grid(row=1, column=0, padx=20, pady=10, sticky="w")
        self.type_select_income.grid(row=1, column=1, padx=20, pady=10, sticky="w")
        self.type_select_expense.grid(row=2, column=1, padx=20, pady=10, sticky="w")
        self.income_type.grid(row=1, column=2, padx=20, pady=10, sticky="w")
        self.expense_type.grid(row=2, column=2, padx=20, pady=10, sticky="w")

        self.amount_text.grid(row=3, column=0, padx=20, pady=10, sticky="w")
        self.amount_entry.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.account_text.grid(row=4, column=0, padx=20, pady=10, sticky="w")
        self.account_select.grid(row=4, column=1, padx=20, pady=10, sticky="w")
        self.remaining_text.grid(row=4, column=2, padx=20, pady=10, sticky="w")

        self.submit_button.grid(row=0, column=0, padx=20, pady=10, sticky="se")


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
        self.title("Money Management")
        self.balance = 0
        self.trans = transaction(master = self)
        self.trans.grid(row=0, column=0, sticky="nsew", padx=40, pady=40)


if __name__ == "__main__":
    app = moneyApp()
    app.mainloop()
