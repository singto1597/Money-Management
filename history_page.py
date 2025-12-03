import customtkinter as ctk
import db
import db_function as db_func
from datetime import datetime, timedelta

class allHistoryTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.week_offset = 0 
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        self.accounts_map = { row["account_name"]: row["account_id"] for row in db.getDB("Accounts") }
        self.cache_widgets = [] 

        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_prev = ctk.CTkButton(self.ctrl_frame, text="< สัปดาห์ก่อน", width=100, command=self.prev_week)
        self.btn_prev.pack(side="left")

        self.lbl_date_range = ctk.CTkLabel(self.ctrl_frame, text="...", font=("Arial", 16, "bold"))
        self.lbl_date_range.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.ctrl_frame, text="สัปดาห์ถัดไป >", width=100, command=self.next_week)
        self.btn_next.pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        
        self.table_frame.grid_columnconfigure(0, weight=1) # วันที่
        self.table_frame.grid_columnconfigure(1, weight=3) # รายการ (กว้างสุด)
        self.table_frame.grid_columnconfigure(2, weight=1) # หมวด
        self.table_frame.grid_columnconfigure(3, weight=1) # จำนวนเงิน
        self.table_frame.grid_columnconfigure(4, weight=0) # ปุ่ม Edit
        self.table_frame.grid_columnconfigure(5, weight=0) # ปุ่ม Delete

        headers = ["วันที่/เวลา", "รายการ", "หมวดหมู่", "จำนวนเงิน", "", ""]
        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=("Arial", 14, "bold"))
            lbl.grid(row=0, column=idx, sticky="w", padx=5, pady=5)

        self.refresh_table()
        

    def get_week_range(self):
        today = datetime.now()
        target_date = today + timedelta(weeks=self.week_offset)
        
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return start_of_week, end_of_week

    def prev_week(self):
        self.week_offset -= 1
        self.refresh_table()

    def next_week(self):
        self.week_offset += 1
        self.refresh_table()

    def refresh_table(self):

        start_date, end_date = self.get_week_range()
        s_str = start_date.strftime("%Y-%m-%d")
        e_str = end_date.strftime("%Y-%m-%d")
        
        self.lbl_date_range.configure(text=f"{s_str} ถึง {e_str}")

        transactions = db_func.getTransactionsByDateRange(s_str, e_str)


        for i, row in enumerate(transactions):
            current_row_idx = i + 1

 
            amount_color = "yellow" 
            if row['category_type'] == 'income': amount_color = "green"
            elif row['category_type'] == 'expense': amount_color = "red"
            elif row.get('category_id') == 100: amount_color = "yellow"
            
            amount_text = f"{row['amount']:,.2f}"

            t_id = row['transaction_id']
            acc_name = row['account_name']
            amo = row['amount']
            t_type = row['category_type']
            cmd_edit = lambda x=t_id, d=row['description'], a=row['amount']: self.open_edit_popup(x, d, a)
            cmd_delete = lambda x=t_id, acc = acc_name, a = amo, t = t_type: self.delete_item(x, acc, a, t)

            if i < len(self.cache_widgets):
                widgets = self.cache_widgets[i]
                
                widgets[0].configure(text=row['transaction_date'][0:16])
                widgets[1].configure(text=row['description'])
                widgets[2].configure(text=row['category_name'])
                widgets[3].configure(text=amount_text, text_color=amount_color)
                widgets[4].configure(command=cmd_edit)
                widgets[5].configure(command=cmd_delete)
                
                for w in widgets: w.grid()
                
            else:
                l1 = ctk.CTkLabel(self.table_frame, text=row['transaction_date'][0:16])
                l2 = ctk.CTkLabel(self.table_frame, text=row['description'])
                l3 = ctk.CTkLabel(self.table_frame, text=row['category_name'])
                l4 = ctk.CTkLabel(self.table_frame, text=amount_text, text_color=amount_color)
          
                btn_edit = ctk.CTkButton(self.table_frame, text="✏️", width=30, fg_color="orange", command=cmd_edit)
                
          
                btn_delete = ctk.CTkButton(self.table_frame, text="🗑️", width=30, fg_color="red", command=cmd_delete)



                l1.grid(row=current_row_idx, column=0, sticky="w", padx=5)
                l2.grid(row=current_row_idx, column=1, sticky="w", padx=5)
                l3.grid(row=current_row_idx, column=2, sticky="w", padx=5)
                l4.grid(row=current_row_idx, column=3, sticky="e", padx=5)
                btn_edit.grid(row=current_row_idx, column=4, padx=2)
                btn_delete.grid(row=current_row_idx, column=5, padx=2)

                self.cache_widgets.append([l1, l2, l3, l4, btn_edit, btn_delete])

        for i in range(len(transactions), len(self.cache_widgets)):
            for widget in self.cache_widgets[i]:
                widget.grid_remove()
    def delete_item(self, t_id, account_name, amount, type):
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        print(f"Deleting transaction {t_id}")
        db_func.deleteTransaction(t_id)
        acc_id = self.accounts_map.get(account_name, 0)
        acc_balance = self.accounts_map_balance.get(account_name, 0)

        diff = 0
        if type == "income" or type == "transfrom_to": 
            diff = -amount 

            print("in")
            
        elif type == "expense" or type == "transfrom_from":
            diff = amount
            print("ex")
            
        else:
            print(f"Unknown Type: {type} - No balance change")
            diff = 0
        print(diff)
        db_func.changeBalanceInAccount(balance = acc_balance + diff, 
                                       id = acc_id)
        self.refresh_table()

    def open_edit_popup(self, t_id, desc, amount):
        EditPopup(self, t_id, desc, amount, self.refresh_table)


class accountHistoryTable(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.week_offset = 0 
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        self.accounts_map = { row["account_name"]: row["account_id"] for row in db.getDB("Accounts") }
        self.cache_widgets = [] 
        
        self.ctrl_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.ctrl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)
        
        self.btn_prev = ctk.CTkButton(self.ctrl_frame, text="< สัปดาห์ก่อน", width=100, command=self.prev_week)
        self.btn_prev.pack(side="left")

        self.lbl_date_range = ctk.CTkLabel(self.ctrl_frame, text="...", font=("Arial", 16, "bold"))
        self.lbl_date_range.pack(side="left", expand=True)

        self.btn_next = ctk.CTkButton(self.ctrl_frame, text="สัปดาห์ถัดไป >", width=100, command=self.next_week)
        self.btn_next.pack(side="right")

        self.table_frame = ctk.CTkScrollableFrame(self)
        self.table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        self.acc_label = ctk.CTkLabel(self, text="กระเป๋า/บัญชี:")
        self.acc_combo = ctk.CTkComboBox(self, values=list(self.accounts_map.keys()), command = self.update_account_balance)
        if self.accounts_map:
            first_acc = list(self.accounts_map.keys())[0]
            self.acc_combo.set(first_acc)

        self.acc_label.grid(row=2, column=0, padx=20, pady=10, sticky="e")
        self.acc_combo.grid(row=2, column=1, padx=20, pady=10, sticky="e")
        self.table_frame.grid_columnconfigure(0, weight=1) # วันที่
        self.table_frame.grid_columnconfigure(1, weight=3) # รายการ (กว้างสุด)
        self.table_frame.grid_columnconfigure(2, weight=1) # หมวด
        self.table_frame.grid_columnconfigure(3, weight=1) # จำนวนเงิน
        self.table_frame.grid_columnconfigure(4, weight=0) # ปุ่ม Edit
        self.table_frame.grid_columnconfigure(5, weight=0) # ปุ่ม Delete

        headers = ["วันที่/เวลา", "รายการ", "หมวดหมู่", "จำนวนเงิน", "", ""]
        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=("Arial", 14, "bold"))
            lbl.grid(row=0, column=idx, sticky="w", padx=5, pady=5)

        self.refresh_table()
        

    def get_week_range(self):
        today = datetime.now()
        target_date = today + timedelta(weeks=self.week_offset)
        
        start_of_week = target_date - timedelta(days=target_date.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        return start_of_week, end_of_week

    def prev_week(self):
        self.week_offset -= 1
        self.refresh_table()

    def next_week(self):
        self.week_offset += 1
        self.refresh_table()

    def refresh_table(self):

        start_date, end_date = self.get_week_range()
        s_str = start_date.strftime("%Y-%m-%d")
        e_str = end_date.strftime("%Y-%m-%d")
        
        self.lbl_date_range.configure(text=f"{s_str} ถึง {e_str}")
        
        account_name = self.acc_combo.get()
        account_id = self.accounts_map.get(account_name)

        transactions = db_func.getTransactionsByDateRange(s_str, e_str, account_id)


        for i, row in enumerate(transactions):
            current_row_idx = i + 1

 
            amount_color = "yellow" 
            if row['category_type'] == 'income': amount_color = "green"
            elif row['category_type'] == 'expense': amount_color = "red"
            elif row.get('category_id') == 100: amount_color = "yellow"
            
            amount_text = f"{row['amount']:,.2f}"

            t_id = row['transaction_id']
            acc_name = row['account_name']
            amo = row['amount']
            t_type = row['category_type']
            cmd_edit = lambda x=t_id, d=row['description'], a=row['amount']: self.open_edit_popup(x, d, a)
            cmd_delete = lambda x=t_id, acc = acc_name, a = amo, t = t_type: self.delete_item(x, acc, a, t)

            if i < len(self.cache_widgets):
                widgets = self.cache_widgets[i]
                
                widgets[0].configure(text=row['transaction_date'][0:16])
                widgets[1].configure(text=row['description'])
                widgets[2].configure(text=row['category_name'])
                widgets[3].configure(text=amount_text, text_color=amount_color)
                widgets[4].configure(command=cmd_edit)
                widgets[5].configure(command=cmd_delete)
                
                for w in widgets: w.grid()
                
            else:
                l1 = ctk.CTkLabel(self.table_frame, text=row['transaction_date'][0:16])
                l2 = ctk.CTkLabel(self.table_frame, text=row['description'])
                l3 = ctk.CTkLabel(self.table_frame, text=row['category_name'])
                l4 = ctk.CTkLabel(self.table_frame, text=amount_text, text_color=amount_color)
          
                btn_edit = ctk.CTkButton(self.table_frame, text="✏️", width=30, fg_color="orange", command=cmd_edit)
                
          
                btn_delete = ctk.CTkButton(self.table_frame, text="🗑️", width=30, fg_color="red", command=cmd_delete)



                l1.grid(row=current_row_idx, column=0, sticky="w", padx=5)
                l2.grid(row=current_row_idx, column=1, sticky="w", padx=5)
                l3.grid(row=current_row_idx, column=2, sticky="w", padx=5)
                l4.grid(row=current_row_idx, column=3, sticky="e", padx=5)
                btn_edit.grid(row=current_row_idx, column=4, padx=2)
                btn_delete.grid(row=current_row_idx, column=5, padx=2)

                self.cache_widgets.append([l1, l2, l3, l4, btn_edit, btn_delete])

        for i in range(len(transactions), len(self.cache_widgets)):
            for widget in self.cache_widgets[i]:
                widget.grid_remove()
    def delete_item(self, t_id, account_name, amount, type):
        self.accounts_map_balance = { row["account_name"]: row["account_balance"] for row in db.getDB("Accounts") }
        print(f"Deleting transaction {t_id}")
        db_func.deleteTransaction(t_id)
        acc_id = self.accounts_map.get(account_name, 0)
        acc_balance = self.accounts_map_balance.get(account_name, 0)

        diff = 0
        if type == "income" or type == "transfrom_to": 
            diff = -amount 

            print("in")
            
        elif type == "expense" or type == "transfrom_from":
            diff = amount
            print("ex")
            
        else:
            print(f"Unknown Type: {type} - No balance change")
            diff = 0
        print(diff)
        db_func.changeBalanceInAccount(balance = acc_balance + diff, 
                                       id = acc_id)
        self.refresh_table()

    def open_edit_popup(self, t_id, desc, amount):
        EditPopup(self, t_id, desc, amount, self.refresh_table)
    def update_account_balance(self, choice):
        self.refresh_table()


class HistoryPage(ctk.CTkTabview): 
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ประวัติทั้งหมด")
        self.add("ประวัติรายบัญชี")

        self.general_frame = allHistoryTable(master=self.tab("ประวัติทั้งหมด"))
        self.general_frame.pack(fill="both", expand=True)

        self.account_history_frame = accountHistoryTable(master=self.tab("ประวัติรายบัญชี"))
        self.account_history_frame.pack(fill="both", expand=True)
        self.configure(command=self._on_tab_change)

    def refresh_data(self):
        """สั่งให้ทุกเฟรมย่อยใน HistoryPage ไปโหลดข้อมูลใหม่"""
        self.general_frame.refresh_table()
        


    def _on_tab_change(self):
        """เมื่อมีการกดเปลี่ยน Tab ให้รีเฟรชข้อมูลใน Tab นั้นๆ"""
    
        self.general_frame.refresh_table()
        self.account_history_frame.refresh_table()
        # print ("test")


class EditPopup(ctk.CTkToplevel):
    def __init__(self, master, t_id, old_desc, old_amount, callback_refresh):
        super().__init__(master)
        self.title("แก้ไขรายการ")
        self.geometry("300x200")
        
        self.t_id = t_id
        self.callback_refresh = callback_refresh # ฟังก์ชันที่จะเรียกเมื่อบันทึกเสร็จ

        # UI แก้ไขง่ายๆ
        ctk.CTkLabel(self, text="รายการ:").pack(pady=5)
        self.entry_desc = ctk.CTkEntry(self)
        self.entry_desc.insert(0, old_desc) # ใส่ค่าเดิม
        self.entry_desc.pack(pady=5)

        ctk.CTkLabel(self, text="จำนวนเงิน:").pack(pady=5)
        self.entry_amount = ctk.CTkEntry(self)
        self.entry_amount.insert(0, str(old_amount)) # ใส่ค่าเดิม
        self.entry_amount.pack(pady=5)

        ctk.CTkButton(self, text="บันทึก", command=self.save_edit, fg_color="green").pack(pady=20)
        
        # ทำให้หน้าต่างนี้อยู่บนสุดเสมอ
        self.attributes("-topmost", True)

    def save_edit(self):
        new_desc = self.entry_desc.get()
        new_amt = float(self.entry_amount.get())
        
        # ส่งไปแก้ใน DB
        db_func.updateTransaction(self.t_id, new_desc, new_amt)
        
        # สั่งให้หน้าตารางรีเฟรช
        self.callback_refresh()
        self.destroy() # ปิดหน้าต่าง