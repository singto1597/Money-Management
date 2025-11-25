import customtkinter as ctk
import db
import db_function as db_func

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

        if not amount: return
        amount = float(amount)

        if not desc:
            desc = transaction_type

        amount_willChange_account = 0
        
        account_id = self.accounts_map.get(account_name)
        
        if transaction_type == "รายรับ":
            category_id = self.income_map.get(category_name)
            amount_willChange_account = amount
        else:
            category_id = self.expense_map.get(category_name)
            amount_willChange_account = -amount
            
        db_func.addTransaction(description = desc, 
                               category_id = category_id, 
                               amount = amount, 
                               account_id = account_id)
        db_func.changeBalanceInAccount(balance = self.acc_balance + amount_willChange_account, 
                                       id = account_id)
        
        current_balance = self.accounts_map_balance.get(account_name, 0)
        new_balance = current_balance + amount_willChange_account
        self.accounts_map_balance[account_name] = new_balance
        
        self.update_account_balance(account_name)

    def update_account_balance(self, choise):
        self.acc_balance = self.accounts_map_balance.get(choise, 0)
        self.acc_balance_label.configure(text=f"มีจำนวนเงิน {self.acc_balance}")


class TransferFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.accounts_map = {row["account_name"]: row["account_id"] for row in db.getDB("Accounts")}
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        acc_names = list(self.accounts_map.keys())

        self.grid_columnconfigure(1, weight=1)

        self.lbl_from = ctk.CTkLabel(self, text="จากกระเป๋า:")
        self.combo_from = ctk.CTkComboBox(self, values=acc_names, command = self.update_from_account_balance)

        self.from_balance = list(self.accounts_map_balance.values())[0]
        self.lbl_from_balance = ctk.CTkLabel(master = self, text = f"มีจำนวนเงิน {self.from_balance}")
        

        self.lbl_to = ctk.CTkLabel(self, text="ไปกระเป๋า:")
        self.combo_to = ctk.CTkComboBox(self, values=acc_names, command = self.update_to_account_balance)

        self.to_balance = list(self.accounts_map_balance.values())[0]
        self.lbl_to_balance = ctk.CTkLabel(master = self, text = f"มีจำนวนเงิน {self.to_balance}")



        self.lbl_amt = ctk.CTkLabel(self, text="จำนวนเงิน:")
        self.entry_amt = ctk.CTkEntry(self, placeholder_text="0.00")

        self.btn_submit = ctk.CTkButton(self, text="ยืนยันการโอน", command=self.submit_transfer, fg_color="orange", hover_color="darkorange")



        self.lbl_from.grid(row=0, column=0, padx=20, pady=10, sticky="e")
        self.combo_from.grid(row=0, column=1, padx=20, pady=10, sticky="ew")
        self.lbl_from_balance.grid(row=1, column=1, padx=20, pady=10, sticky="w")


        self.lbl_to.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.combo_to.grid(row=2, column=1, padx=20, pady=10, sticky="ew")
        self.lbl_to_balance.grid(row=3, column=1, padx=20, pady=10, sticky="w")

        self.lbl_amt.grid(row=4, column=0, padx=20, pady=10, sticky="e")
        self.entry_amt.grid(row=4, column=1, padx=20, pady=10, sticky="ew")

        self.btn_submit.grid(row=5, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
    def submit_transfer(self):
        acc_from_name = self.combo_from.get()
        acc_to_name = self.combo_to.get()
        amount = self.entry_amt.get()

        if not amount: return
        amount = float(amount)
        if amount == 0: return
        if acc_from_name == acc_to_name: return
        print(f"โอน {amount} จาก {acc_from_name} -> {acc_to_name}")
        db_func.transferMoney(amount = amount, 
                              from_acc_id = self.accounts_map.get(acc_from_name), 
                              to_acc_id = self.accounts_map.get(acc_to_name))
        
        current_balance = self.accounts_map_balance.get(acc_from_name, 0)
        new_balance = current_balance - amount
        self.accounts_map_balance[acc_from_name] = new_balance
        self.update_from_account_balance(acc_from_name)

        current_balance = self.accounts_map_balance.get(acc_to_name, 0)
        new_balance = current_balance + amount
        self.accounts_map_balance[acc_to_name] = new_balance
        self.update_to_account_balance(acc_to_name)

    def update_from_account_balance(self, choise):
        self.from_balance = self.accounts_map_balance.get(choise, 0)
        self.lbl_from_balance.configure(text=f"มีจำนวนเงิน {self.from_balance}")

    def update_to_account_balance(self, choise):
        self.to_balance = self.accounts_map_balance.get(choise, 0)
        self.lbl_to_balance.configure(text=f"มีจำนวนเงิน {self.to_balance}")

class AddPage(ctk.CTkTabview): 
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ทั่วไป")
        self.add("โอนเงิน")

        self.general_frame = TransactionFrame(master=self.tab("ทั่วไป"))
        self.general_frame.pack(fill="both", expand=True)

        self.transfer_frame = TransferFrame(master=self.tab("โอนเงิน"))
        self.transfer_frame.pack(fill="both", expand=True)

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="หน้าประวัติการเงิน", font=("Arial", 24)).pack(pady=50)

class EditPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="หน้าแก้ไข เพิ่ม เกี่ยวกับประเภทและบัญชี", font=("Arial", 24)).pack(pady=50)

class MoneyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Money Management")
        self.geometry("900x600")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)


        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Money Manager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_add = self.create_sidebar_button("เพิ่มรายการ", self.show_add_page, row=1)
        self.btn_history = self.create_sidebar_button("ประวัติ", self.show_history_page, row=2)
        self.btn_edit = self.create_sidebar_button("แก้ไขข้อมูล", self.show_edit_page, row=3)

        
        self.add_page = AddPage(master=self)
        self.history_page = HistoryPage(master=self)
        self.edit_page = EditPage(master=self)

        self.show_add_page()

    def create_sidebar_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command,
                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                            anchor="w") # anchor="w" ให้ตัวหนังสือชิดซ้าย
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        return btn

    def select_button(self, btn):
        """ เปลี่ยนสีปุ่มที่ถูกเลือก """
        self.btn_add.configure(fg_color="transparent")
        self.btn_history.configure(fg_color="transparent")
        self.btn_edit.configure(fg_color="transparent")
        
        btn.configure(fg_color=("gray75", "gray25"))

    def show_add_page(self):
        self.select_button(self.btn_add)
        self.hide_all_pages()
        self.add_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def show_history_page(self):
        self.select_button(self.btn_history)
        self.hide_all_pages()
        self.history_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        # ตรงนี้สั่ง self.history_page.refresh_data() ได้ในอนาคต

    def show_edit_page(self):
        self.select_button(self.btn_edit)
        self.hide_all_pages()
        self.edit_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

    def hide_all_pages(self):
        self.add_page.grid_forget()
        self.history_page.grid_forget()
        self.edit_page.grid_forget()

if __name__ == "__main__":
    app = MoneyApp()
    app.mainloop()