import customtkinter as ctk
import db

class TransactionFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.accounts_map = { row["account_name"]: row["account_id"] for row in db.getDB("Accounts") }
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }

        raw_income = db.getDB("Categories", condition="category_type = ?", conditionValues=("income",))
        self.income_map = { row["category_name"]: row["category_id"] for row in raw_income }
        
        raw_expense = db.getDB("Categories", condition="category_type = ?", conditionValues=("expense",))
        self.expense_map = { row["category_name"]: row["category_id"] for row in raw_expense }

        
        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 

        
        # Row 0: เลือกประเภท 
        self.type_label = ctk.CTkLabel(self, text="ประเภทธุรกรรม:")
        self.type_seg_btn = ctk.CTkSegmentedButton(self, 
                                                   values=["รายจ่าย", "รายรับ"], 
                                                   command=self.update_category_list)
        self.type_seg_btn.set("รายจ่าย") # defalse

        # Row 1: รายการ
        self.desc_label = ctk.CTkLabel(self, text="รายการ:")
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="ซื้ออะไรมา??")

        # Row 2: หมวดหมู่
        self.cat_label = ctk.CTkLabel(self, text="หมวดหมู่:")
        self.cat_combo = ctk.CTkComboBox(self, values=list(self.expense_map.keys()))

        # Row 3: จำนวนเงิน
        self.amount_label = ctk.CTkLabel(self, text="จำนวนเงิน:")
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="0.00")

        # Row 4: กระเป๋าเงิน
        self.acc_label = ctk.CTkLabel(self, text="กระเป๋า/บัญชี:")
        self.acc_combo = ctk.CTkComboBox(self, values=list(self.accounts_map.keys()), command = self.update_account_balance)
        self.acc_balance = list(self.accounts_map_balance.values())[0]
        # print (self.acc_balance)
        self.acc_balance_label = ctk.CTkLabel(master = self, text = f"มีจำนวนเงิน {self.acc_balance}")

        # Row 5: ปุ่มบันทึก
        self.submit_btn = ctk.CTkButton(self, text="บันทึกรายการ", command=self.submit_data)

        
        self.type_label.grid(row=0, column=0, padx=20, pady=10, sticky="e")
        self.type_seg_btn.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        self.desc_label.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.desc_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        self.cat_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.cat_combo.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        self.amount_label.grid(row=3, column=0, padx=20, pady=10, sticky="e")
        self.amount_entry.grid(row=3, column=1, padx=20, pady=10, sticky="ew")

        self.acc_label.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.acc_combo.grid(row=4, column=1, padx=20, pady=10, sticky="ew")
        self.acc_balance_label.grid(row=5, column=1, padx=20, pady=10, sticky="w")

        self.submit_btn.grid(row=6, column=0, columnspan=2, padx=20, pady=30, sticky="ew")

    def update_category_list(self, value):
        if value == "รายรับ":
            new_values = list(self.income_map.keys())
            self.submit_btn.configure(fg_color="green", hover_color="darkgreen") # เปลี่ยนสีปุ่มให้รู้ว่าเป็นรายรับ
        else:
            new_values = list(self.expense_map.keys())
            self.submit_btn.configure(fg_color="#3B8ED0", hover_color="#36719F") # สีเดิม (ฟ้า)

        self.cat_combo.configure(values=new_values)
        self.cat_combo.set(new_values[0] if new_values else "-")

    def submit_data(self):
        account_name = self.acc_combo.get()
        category_name = self.cat_combo.get()
        transaction_type = self.type_seg_btn.get()
        desc = self.desc_entry.get()
        amount = self.amount_entry.get()

        if not amount:
            amount = 0
        if not desc:
            desc = transaction_type

        
        account_id = self.accounts_map.get(account_name)
        
        if transaction_type == "รายรับ":
            category_id = self.income_map.get(category_name)
        else:
            category_id = self.expense_map.get(category_name)
            
        print(f"Saving: Type={transaction_type}, AccID={account_id}, CatID={category_id}, Amt={amount}, desc={desc}")
    def update_account_balance(self, choise):
        acc_balance = self.accounts_map_balance.get(choise, 0)
        # test = self.acc_combo.get()
        self.acc_balance_label.configure(text=f"มีจำนวนเงิน {acc_balance}")
class MoneyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.geometry("600x500") 
        self.title("Money Management")
        
        
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        
        self.trans_frame = TransactionFrame(master=self)
        self.trans_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nsew")

if __name__ == "__main__":
    app = MoneyApp()
    app.mainloop()