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
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        start_date, end_date = self.get_week_range()
        s_str = start_date.strftime("%Y-%m-%d")
        e_str = end_date.strftime("%Y-%m-%d")
        
        self.lbl_date_range.configure(text=f"{s_str} ถึง {e_str}")

        transactions = db_func.getTransactionsByDateRange(s_str, e_str)


        headers = ["วันที่/เวลา", "รายการ", "หมวดหมู่", "จำนวนเงิน"]
        for idx, h in enumerate(headers):
            lbl = ctk.CTkLabel(self.table_frame, text=h, font=("Arial", 14, "bold"))
            lbl.grid(row=0, column=idx, sticky="w", padx=5, pady=5)


        for i, row in enumerate(transactions):
            current_row = i + 1 
            
            amount_color = "green" if row['category_type'] == 'income' else "red"
            amount_text = f"{row['amount']:,.2f}"

            ctk.CTkLabel(self.table_frame, text=row['transaction_date'][0:16]).grid(row=current_row, column=0, sticky="w", padx=5)
            ctk.CTkLabel(self.table_frame, text=row['description']).grid(row=current_row, column=1, sticky="w", padx=5)
            ctk.CTkLabel(self.table_frame, text=row['category_name']).grid(row=current_row, column=2, sticky="w", padx=5)
            ctk.CTkLabel(self.table_frame, text=amount_text, text_color=amount_color).grid(row=current_row, column=3, sticky="e", padx=5)


class HistoryPage(ctk.CTkTabview): 
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ประวัติทั้งหมด")
        self.add("ประวัติรายบัญชี")

        self.general_frame = allHistoryTable(master=self.tab("ประวัติทั้งหมด"))
        self.general_frame.pack(fill="both", expand=True)

        self.transfer_frame = allHistoryTable(master=self.tab("ประวัติรายบัญชี"))
        self.transfer_frame.pack(fill="both", expand=True)
    def refresh_data(self):
        """สั่งให้ทุกเฟรมย่อยใน HistoryPage ไปโหลดข้อมูลใหม่"""
        self.general_frame.refresh_table()
        # ถ้ามี self.account_history_frame ก็สั่ง .refresh_table() ของมันด้วย
        
        # เพิ่มเติม: เพื่อให้มั่นใจว่าถ้ามีการเปลี่ยน Tab แล้วข้อมูลถูกโหลดใหม่ 
        # เราควรผูกคำสั่ง refresh เข้ากับ event การเปลี่ยน Tab ด้วย
        self.configure(command=self._on_tab_change)

    def _on_tab_change(self, tab_name):
        """เมื่อมีการกดเปลี่ยน Tab ให้รีเฟรชข้อมูลใน Tab นั้นๆ"""
        if tab_name == "ประวัติทั้งหมด":
            self.general_frame.refresh_table()
        # elif tab_name == "ประวัติรายบัญชี":
        #     self.account_history_frame.refresh_table()