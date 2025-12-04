import customtkinter as ctk
import db
import db_function as db_func

import customtkinter as ctk
import db
import db_function as db_func

from tkcalendar import DateEntry
from datetime import datetime

class PaymentRow(ctk.CTkFrame):
    def __init__(self, master, account_map, default_amount="", **kwargs):
        super().__init__(master, **kwargs)
        self.account_map = account_map
        self.grid_columnconfigure(1, weight=1)

        # Dropdown เลือกบัญชี (รวมทุกบัญชี ทั้งสดและแบงก์)
        self.acc_combo = ctk.CTkComboBox(self, values=list(account_map.keys()))
        self.acc_combo.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        # ช่องกรอกเงิน
        self.amount_entry = ctk.CTkEntry(self, placeholder_text="0.00", width=100)
        if default_amount:
            self.amount_entry.insert(0, str(default_amount))
        self.amount_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # ปุ่มลบแถวนี้ (เผื่อกดผิด)
        self.btn_del = ctk.CTkButton(self, text="X", width=30, fg_color="red", command=self.destroy_row)
        self.btn_del.grid(row=0, column=2, padx=5, pady=5)
    def destroy_row(self):
        self.destroy()
    def get_data(self):
        acc_name = self.acc_combo.get()
        amount_str = self.amount_entry.get()
        
        try:
            amount = float(amount_str)
        except ValueError:
            amount = 0.0
            
        acc_id = self.account_map.get(acc_name)
        return acc_name, acc_id, amount
class TransactionFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.accounts_map = { row["account_name"]: row["account_id"] for row in db.getDB("Accounts") }
        raw_income = db.getDB("Categories", condition="category_type = ?", conditionValues=("income",))
        self.income_map = { row["category_name"]: row["category_id"] for row in raw_income }
        
        raw_expense = db.getDB("Categories", condition="category_type = ?", conditionValues=("expense",))
        self.expense_map = { row["category_name"]: row["category_id"] for row in raw_expense }
        
        self.payment_rows = []

        self.grid_columnconfigure(0, weight=0) 
        self.grid_columnconfigure(1, weight=1) 

        # --- ส่วนหัว: ประเภท, รายการ, หมวดหมู่ ---
        ctk.CTkLabel(self, text="ประเภท:").grid(row=0, column=0, padx=20, pady=10, sticky="e")
        self.type_seg_btn = ctk.CTkSegmentedButton(self, values=["รายจ่าย", "รายรับ"], command=self.update_category_list)
        self.type_seg_btn.set("รายจ่าย")
        self.type_seg_btn.grid(row=0, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="รายการ:").grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.desc_entry = ctk.CTkEntry(self, placeholder_text="ซื้ออะไร / รับจากไหน")
        self.desc_entry.grid(row=1, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="หมวดหมู่:").grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.cat_combo = ctk.CTkComboBox(self, values=list(self.expense_map.keys()))
        self.cat_combo.grid(row=2, column=1, padx=20, pady=10, sticky="ew")

        ctk.CTkLabel(self, text="ช่องทางชำระเงิน:").grid(row=3, column=0, padx=20, pady=10, sticky="ne")
        
        self.payments_container = ctk.CTkFrame(self, fg_color="transparent")
        self.payments_container.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        
        self.btn_add_split = ctk.CTkButton(self, text="+ เพิ่มช่องทางชำระ", 
                                           fg_color="gray", command=self.add_payment_row)
        self.btn_add_split.grid(row=4, column=1, padx=20, pady=0, sticky="w")

        self.submit_btn = ctk.CTkButton(self, text="บันทึกรายการ", height=40, command=self.submit_data)
        self.submit_btn.grid(row=5, column=0, columnspan=2, padx=20, pady=30, sticky="ew")
        self.add_payment_row()
    def add_payment_row(self):
        row = PaymentRow(self.payments_container, account_map=self.accounts_map)
        row.pack(fill="x", pady=2)
        self.payment_rows.append(row)
    def update_category_list(self, value):
        if value == "รายรับ":
            new_values = list(self.income_map.keys())
            self.submit_btn.configure(fg_color="green", hover_color="darkgreen")
        else:
            new_values = list(self.expense_map.keys())
            self.submit_btn.configure(fg_color="#3B8ED0", hover_color="#36719F")
        self.cat_combo.configure(values=new_values)
        self.cat_combo.set(new_values[0] if new_values else "-")
    def submit_data(self):
        category_name = self.cat_combo.get()
        transaction_type = self.type_seg_btn.get()
        desc = self.desc_entry.get()
        if not desc: desc = transaction_type

        if transaction_type == "รายรับ":
            category_id = self.income_map.get(category_name)
            multiplier = 1
        else:
            category_id = self.expense_map.get(category_name)
            multiplier = -1

        valid_rows = [r for r in self.payments_container.winfo_children() if isinstance(r, PaymentRow)]

        has_data = False
        for row in valid_rows:
            acc_name, acc_id, amount = row.get_data()
            
            if amount > 0 and acc_id is not None:
                has_data = True
                final_desc = f"{desc} ({acc_name})" 

                # บันทึก Transaction
                db_func.addTransaction(description=final_desc, 
                                       category_id=category_id, 
                                       amount=amount, 
                                       account_id=acc_id)
                
                current_acc_data = db.getDB("Accounts", condition=f"account_id={acc_id}")
                if current_acc_data:
                    current_bal = current_acc_data[0]["account_balance"]
                    new_bal = current_bal + (amount * multiplier)
                    
                    db_func.changeBalanceInAccount(balance=new_bal, id=acc_id)

        if has_data:
            print("บันทึกเสร็จสิ้น!")
            self.clear_inputs()
            self.update_view()
    def clear_inputs(self):
        self.desc_entry.delete(0, "end")
        for widget in self.payments_container.winfo_children():
            widget.destroy()
        self.payment_rows = []
        self.add_payment_row()
    def update_view(self):
        self.accounts_map = { row["account_name"]: row["account_id"] for row in db.getDB("Accounts") }
        raw_income = db.getDB("Categories", condition="category_type = ?", conditionValues=("income",))
        self.income_map = { row["category_name"]: row["category_id"] for row in raw_income }
        
        raw_expense = db.getDB("Categories", condition="category_type = ?", conditionValues=("expense",))
        self.expense_map = { row["category_name"]: row["category_id"] for row in raw_expense }
class TransferFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.accounts_map = {row["account_name"]: row["account_id"] for row in db.getDB("Accounts")}
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        acc_names = list(self.accounts_map.keys())

        self.grid_columnconfigure(1, weight=1)

        # --- แถว 0: วันที่ (Date Picker) ---
        self.lbl_date = ctk.CTkLabel(self, text="วันที่:")
        self.lbl_date.grid(row=0, column=0, padx=20, pady=10, sticky="e")
        
        # DateEntry เป็น Widget ของ tkcalendar (ไม่ใช่ ctk) แต่ใช้ร่วมกันได้
        self.date_entry = DateEntry(self, width=12, background='darkblue',
                                    foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.date_entry.grid(row=0, column=1, padx=20, pady=10, sticky="w")

        # --- แถว 1: จากกระเป๋า ---
        self.lbl_from = ctk.CTkLabel(self, text="จากกระเป๋า:")
        self.combo_from = ctk.CTkComboBox(self, values=acc_names, command=self.update_from_account_balance)
        self.lbl_from_balance = ctk.CTkLabel(master=self, text="...")
        
        self.lbl_from.grid(row=1, column=0, padx=20, pady=10, sticky="e")
        self.combo_from.grid(row=1, column=1, padx=20, pady=10, sticky="ew")
        self.lbl_from_balance.grid(row=2, column=1, padx=20, pady=0, sticky="w")

        # --- แถว 3: ไปกระเป๋า ---
        self.lbl_to = ctk.CTkLabel(self, text="ไปกระเป๋า:")
        self.combo_to = ctk.CTkComboBox(self, values=acc_names, command=self.update_to_account_balance)
        self.lbl_to_balance = ctk.CTkLabel(master=self, text="...")

        self.lbl_to.grid(row=3, column=0, padx=20, pady=10, sticky="e")
        self.combo_to.grid(row=3, column=1, padx=20, pady=10, sticky="ew")
        self.lbl_to_balance.grid(row=4, column=1, padx=20, pady=0, sticky="w")

        # --- แถว 5: จำนวนเงิน ---
        self.lbl_amt = ctk.CTkLabel(self, text="จำนวนเงิน:")
        self.entry_amt = ctk.CTkEntry(self, placeholder_text="0.00")
        
        self.lbl_amt.grid(row=5, column=0, padx=20, pady=10, sticky="e")
        self.entry_amt.grid(row=5, column=1, padx=20, pady=10, sticky="ew")

        # --- ปุ่ม ---
        self.btn_submit = ctk.CTkButton(self, text="ยืนยันการโอน", command=self.submit_transfer, fg_color="orange")
        self.btn_submit.grid(row=6, column=0, columnspan=2, padx=20, pady=20, sticky="ew")
        
        self.update_view()

    def set_transfer_data(self, from_acc, to_acc, amount):
        """ฟังก์ชันสำหรับรับค่าจากหน้า Settle มากรอกให้อัตโนมัติ"""
        self.update_view()
        
        if from_acc: self.combo_from.set(from_acc)
        if to_acc: self.combo_to.set(to_acc)
        
        self.entry_amt.delete(0, "end")
        if amount: self.entry_amt.insert(0, str(amount))
        
        self.update_from_account_balance(from_acc)
        self.update_to_account_balance(to_acc)

    def submit_transfer(self):
        acc_from_name = self.combo_from.get()
        acc_to_name = self.combo_to.get()
        amount = self.entry_amt.get()
        
        selected_date = self.date_entry.get_date() 
        full_datetime = selected_date.strftime('%Y-%m-%d') + datetime.now().strftime(' %H:%M:%S')

        if not amount: return
        try:
            amount = float(amount)
        except ValueError: return

        if amount == 0 or acc_from_name == acc_to_name: return

        # ส่ง full_datetime ไปบันทึก
        db_func.transferMoney(amount=amount, 
                              from_acc_id=self.accounts_map.get(acc_from_name), 
                              to_acc_id=self.accounts_map.get(acc_to_name),
                              date_input=full_datetime) # <--- ส่งวันที่ไป
        
        self.entry_amt.delete(0, "end")
        self.update_view()
        print("โอนสำเร็จ!")
    def update_from_account_balance(self, choise):
        self.from_balance = self.accounts_map_balance.get(choise, 0)
        self.lbl_from_balance.configure(text=f"มีจำนวนเงิน {self.from_balance}")
    def update_to_account_balance(self, choise):
        self.to_balance = self.accounts_map_balance.get(choise, 0)
        self.lbl_to_balance.configure(text=f"มีจำนวนเงิน {self.to_balance}")
    def reload_from_db(self):
        self.accounts_map = {row["account_name"]: row["account_id"] for row in db.getDB("Accounts")}
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
    def update_view(self):
        """เรียกเมื่อสลับมาหน้าโอนเงิน"""
        self.reload_from_db()
        
        acc_names = list(self.accounts_map.keys())
        self.combo_from.configure(values=acc_names)
        self.combo_to.configure(values=acc_names)
        
        self.update_from_account_balance(self.combo_from.get())
        self.update_to_account_balance(self.combo_to.get())
class AddPage(ctk.CTkTabview): 
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ทั่วไป")
        self.add("โอนเงิน")

        self.general_frame = TransactionFrame(master=self.tab("ทั่วไป"))
        self.general_frame.pack(fill="both", expand=True)

        self.transfer_frame = TransferFrame(master=self.tab("โอนเงิน"))
        self.transfer_frame.pack(fill="both", expand=True)
        self.configure(command=self.refresh_data)
    def refresh_data(self):
        self.general_frame.update_view()
        self.transfer_frame.update_view()
    def switch_to_transfer_and_fill(self, from_acc, to_acc, amount):
        """ฟังก์ชันกระโดดมาแท็บโอนเงินและกรอกข้อมูล"""
        self.set("โอนเงิน") # สลับแท็บ
        self.transfer_frame.set_transfer_data(from_acc, to_acc, amount)