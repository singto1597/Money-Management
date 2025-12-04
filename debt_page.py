import customtkinter as ctk
import db
import db_function as db_func

class DebtPage(ctk.CTkFrame):
    def __init__(self, master, on_settle_callback=None, **kwargs):
        super().__init__(master, **kwargs)
        
        # Grid Layout
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1) # ให้พื้นที่แสดงรายการยืดขยายได้

        # --- หัวข้อ ---
        ctk.CTkLabel(self, text="จัดการหนี้สิน (Debts Management)", font=("Arial", 20, "bold")).grid(row=0, column=0, columnspan=2, pady=20)

        # --- ฝั่งซ้าย: ลูกหนี้ (คนอื่นติดเงินเรา) ---
        self.receivable_frame = ctk.CTkFrame(self)
        self.receivable_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.receivable_frame, text="ลูกหนี้ (คนอื่นค้างเงินเรา)", font=("Arial", 16, "bold"), text_color="#4caf50").pack(pady=10)
        self.receivable_list = ctk.CTkScrollableFrame(self.receivable_frame, fg_color="transparent")
        self.receivable_list.pack(fill="both", expand=True)
        
        # ยอดรวมลูกหนี้
        self.total_rec_label = ctk.CTkLabel(self.receivable_frame, text="รวม: 0.00 บาท", font=("Arial", 14, "bold"))
        self.total_rec_label.pack(pady=10)


        # --- ฝั่งขวา: เจ้าหนี้ (เราติดเงินเขา) ---
        self.payable_frame = ctk.CTkFrame(self)
        self.payable_frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(self.payable_frame, text="เจ้าหนี้ (เราค้างเงินเขา)", font=("Arial", 16, "bold"), text_color="#f44336").pack(pady=10)
        self.payable_list = ctk.CTkScrollableFrame(self.payable_frame, fg_color="transparent")
        self.payable_list.pack(fill="both", expand=True)

        # ยอดรวมเจ้าหนี้
        self.total_pay_label = ctk.CTkLabel(self.payable_frame, text="รวม: 0.00 บาท", font=("Arial", 14, "bold"))
        self.total_pay_label.pack(pady=10)

        self.on_settle_callback = on_settle_callback

        # ปุ่ม Refresh (หรือจะเรียกจากนอก class ก็ได้)
        # self.refresh_data() # เรียกตอน init หรือให้ app.py เรียก

    def refresh_data(self):
        # 1. ล้างข้อมูลเก่า
        for widget in self.receivable_list.winfo_children(): widget.destroy()
        for widget in self.payable_list.winfo_children(): widget.destroy()

        accounts = db.getDB("Accounts")
        
        total_rec = 0
        total_pay = 0

        for acc in accounts:
            acc_type = acc['account_type']
            name = acc['account_name']
            balance = acc['account_balance']

            if acc_type == 'receivable':
                # --- สร้างการ์ดลูกหนี้ ---
                total_rec += balance
                self.create_card(self.receivable_list, name, balance, "receivable")

            elif acc_type == 'payable':
                # --- สร้างการ์ดเจ้าหนี้ ---
                # เจ้าหนี้ ปกติยอดจะติดลบ (แปลว่าเราเป็นหนี้) แต่เพื่อความสวยงาม เราอาจจะโชว์เป็นตัวเลขบวกในวงเล็บ หรือสีแดง
                total_pay += balance
                self.create_card(self.payable_list, name, balance, "payable")

        self.total_rec_label.configure(text=f"รวมยอดที่ต้องได้คืน: {total_rec:,.2f} บาท")
        self.total_pay_label.configure(text=f"รวมยอดหนี้สินคงค้าง: {total_pay:,.2f} บาท")

    def create_card(self, parent, name, balance, type):
        card = ctk.CTkFrame(parent)
        card.pack(fill="x", pady=5, padx=5)
        
        # ชื่อและยอดเงิน
        ctk.CTkLabel(card, text=name, font=("Arial", 14)).pack(side="left", padx=10, pady=10)
        
        display_bal = f"{balance:,.2f}"
        text_color = "black" # Default
        
        settle_from = ""
        settle_to = ""
        settle_amount = abs(balance) # ยอดที่จะโอนต้องเป็นบวกเสมอ

        if type == 'receivable':
            text_color = "green" if balance > 0 else "gray"
            display_bal = f"+{balance:,.2f}"
            settle_from = name 
            settle_to = ""  
            
        else: # payable
            text_color = "red" if balance < 0 else "gray"
            # ยอดเจ้าหนี้มักติดลบ
            settle_from = ""   # (ให้ User เลือกเองว่าจะเอาเงินไหนจ่าย)
            settle_to = name   # จ่ายไปให้เขา

        ctk.CTkLabel(card, text=display_bal, font=("Arial", 14, "bold"), text_color=text_color).pack(side="right", padx=10)

        # ปุ่ม Settle (แสดงเฉพาะตอนมียอดค้าง)
        if abs(balance) > 0.01:
            btn_settle = ctk.CTkButton(card, text="ชำระ/เคลียร์", width=80, height=25, 
                                       fg_color="orange", hover_color="darkorange",
                                       command=lambda: self.on_click_settle(settle_from, settle_to, settle_amount))
            btn_settle.pack(side="right", padx=5)

    def on_click_settle(self, f, t, a):
        if self.on_settle_callback:
            self.on_settle_callback(f, t, a)