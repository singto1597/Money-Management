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

        headers = ["วันที่/เวลา", "รายการ", "หมวดหมู่", "จำนวนเงิน"]
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

 
            amount_color = "red" 
            if row['category_type'] == 'income': amount_color = "green"
            elif row.get('category_id') == 100: amount_color = "blue"
            
            amount_text = f"{row['amount']:,.2f}"

            if i < len(self.cache_widgets):
                widgets = self.cache_widgets[i]
                
                widgets[0].configure(text=row['transaction_date'][0:16])
                widgets[1].configure(text=row['description'])
                widgets[2].configure(text=row['category_name'])
                widgets[3].configure(text=amount_text, text_color=amount_color)
                
                for w in widgets: w.grid()
                
            else:
                l1 = ctk.CTkLabel(self.table_frame, text=row['transaction_date'][0:16])
                l2 = ctk.CTkLabel(self.table_frame, text=row['description'])
                l3 = ctk.CTkLabel(self.table_frame, text=row['category_name'])
                l4 = ctk.CTkLabel(self.table_frame, text=amount_text, text_color=amount_color)

                l1.grid(row=current_row_idx, column=0, sticky="w", padx=5)
                l2.grid(row=current_row_idx, column=1, sticky="w", padx=5)
                l3.grid(row=current_row_idx, column=2, sticky="w", padx=5)
                l4.grid(row=current_row_idx, column=3, sticky="e", padx=5)

                self.cache_widgets.append([l1, l2, l3, l4])

        # 4. ซ่อน Widget ส่วนเกิน
        for i in range(len(transactions), len(self.cache_widgets)):
            for widget in self.cache_widgets[i]:
                widget.grid_remove()


class HistoryPage(ctk.CTkTabview): 
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ประวัติทั้งหมด")
        self.add("ประวัติรายบัญชี")

        self.general_frame = allHistoryTable(master=self.tab("ประวัติทั้งหมด"))
        self.general_frame.pack(fill="both", expand=True)

        self.transfer_frame = allHistoryTable(master=self.tab("ประวัติรายบัญชี"))
        self.transfer_frame.pack(fill="both", expand=True)
        # self.configure(command=self._on_tab_change)

    def refresh_data(self):
        """สั่งให้ทุกเฟรมย่อยใน HistoryPage ไปโหลดข้อมูลใหม่"""
        self.general_frame.refresh_table()
        


    # def _on_tab_change(self, tab_name):
    #     """เมื่อมีการกดเปลี่ยน Tab ให้รีเฟรชข้อมูลใน Tab นั้นๆ"""
    #     if tab_name == "ประวัติทั้งหมด":
    #         self.general_frame.refresh_table()
    #     elif tab_name == "ประวัติรายบัญชี":
    #         #     self.account_history_frame.refresh_table()
    #         print ("test")


