import customtkinter as ctk
from tkinter import messagebox
import db
import db_function as db_func

# --- Frame ย่อยสำหรับจัดการ "บัญชี" (Accounts) ---
class ManageAccountsFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # หัวข้อ
        ctk.CTkLabel(self, text="จัดการบัญชี / กระเป๋าเงิน", font=("Arial", 18, "bold")).pack(pady=10)

        # --- ส่วนกรอกข้อมูลเพิ่มบัญชี ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=5)

        self.entry_name = ctk.CTkEntry(self.input_frame, placeholder_text="ชื่อบัญชี (เช่น กสิกร, กระปุกหมู)")
        self.entry_name.pack(side="top", fill="x", pady=2)
        self.combo_type = ctk.CTkComboBox(self.input_frame, values=["cash", "bank", "saving", "receivable", "payable"])
        self.combo_type.set("cash")
        self.combo_type.pack(side="top", fill="x", pady=2)

        self.entry_balance = ctk.CTkEntry(self.input_frame, placeholder_text="ยอดเงินเริ่มต้น (เช่น 0)")
        self.entry_balance.pack(side="top", fill="x", pady=2)

        ctk.CTkButton(self.input_frame, text="+ เพิ่มบัญชี", fg_color="green", command=self.add_account).pack(side="top", fill="x", pady=5)

        # --- ส่วนแสดงรายชื่อบัญชี (List) ---
        ctk.CTkLabel(self, text="รายชื่อบัญชีที่มีอยู่:", font=("Arial", 14)).pack(pady=(15, 5))
        
        self.scroll_frame = ctk.CTkScrollableFrame(self, height=300)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.reload_data()

    def reload_data(self):
        # ล้างข้อมูลเก่าใน UI
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        # ดึงข้อมูลจาก DB
        accounts = db.getDB("Accounts") 
        
        for acc in accounts:
            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            # แสดงชื่อและประเภท
            info_text = f"{acc['account_name']} ({acc['account_type']})\nเริ่ม: {acc.get('initial_balance', 0):,.2f}"
            ctk.CTkLabel(row, text=info_text, anchor="w").pack(side="left", padx=5)

            # ปุ่มลบ
            ctk.CTkButton(row, text="ลบ", width=50, fg_color="red", 
                          command=lambda n=acc['account_name']: self.delete_account(n)).pack(side="right", padx=5)

    def add_account(self):
        name = self.entry_name.get()
        acc_type = self.combo_type.get()
        balance = self.entry_balance.get()

        if not name:
            messagebox.showwarning("แจ้งเตือน", "กรุณาใส่ชื่อบัญชี")
            return
        
        try:
            balance = float(balance) if balance else 0.0
        except ValueError:
            messagebox.showerror("Error", "ยอดเงินเริ่มต้นต้องเป็นตัวเลข")
            return

        db_func.addAccount(name, acc_type, balance)
        
        # เคลียร์ช่องและโหลดใหม่
        self.entry_name.delete(0, "end")
        self.entry_balance.delete(0, "end")
        self.reload_data()

    def delete_account(self, name):
        if messagebox.askyesno("ยืนยัน", f"ต้องการลบบัญชี '{name}' ใช่หรือไม่? \n(ประวัติธุรกรรมที่เกี่ยวข้องอาจหายไปหรือผิดพลาด)"):
            db_func.deleteAccount(name)
            self.reload_data()


# --- Frame ย่อยสำหรับจัดการ "หมวดหมู่" (Categories) ---
class ManageCategoriesFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        ctk.CTkLabel(self, text="จัดการหมวดหมู่", font=("Arial", 18, "bold")).pack(pady=10)

        # --- ส่วนกรอกข้อมูลเพิ่มหมวดหมู่ ---
        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(fill="x", padx=10, pady=5)

        self.entry_name = ctk.CTkEntry(self.input_frame, placeholder_text="ชื่อหมวดหมู่ (เช่น ค่าหอ, โบนัส)")
        self.entry_name.pack(side="top", fill="x", pady=2)

        self.seg_type = ctk.CTkSegmentedButton(self.input_frame, values=["expense", "income"])
        self.seg_type.set("expense")
        self.seg_type.pack(side="top", fill="x", pady=2)

        ctk.CTkButton(self.input_frame, text="+ เพิ่มหมวดหมู่", fg_color="green", command=self.add_category).pack(side="top", fill="x", pady=5)

        # --- ส่วนแสดงรายชื่อหมวดหมู่ ---
        ctk.CTkLabel(self, text="รายชื่อหมวดหมู่ที่มีอยู่:", font=("Arial", 14)).pack(pady=(15, 5))

        self.scroll_frame = ctk.CTkScrollableFrame(self, height=300)
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.reload_data()

    def reload_data(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        categories = db.getDB("Categories")
        
        # เรียงลำดับ income ขึ้นก่อน หรือจะแยกสีก็ได้
        for cat in categories:
            # ไม่แสดงหมวดระบบ (โอนเงิน) เพื่อป้องกันการลบผิด
            if cat['category_type'] in ['transfer_from', 'transfer_to']:
                continue

            row = ctk.CTkFrame(self.scroll_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)

            color = "green" if cat['category_type'] == "income" else "#D32F2F"
            ctk.CTkLabel(row, text=f"{cat['category_name']}", text_color=color, anchor="w").pack(side="left", padx=5)

            ctk.CTkButton(row, text="ลบ", width=50, fg_color="gray", hover_color="red",
                          command=lambda n=cat['category_name']: self.delete_category(n)).pack(side="right", padx=5)

    def add_category(self):
        name = self.entry_name.get()
        cat_type = self.seg_type.get()

        if not name: return

        db_func.addCategory(name, cat_type)
        self.entry_name.delete(0, "end")
        self.reload_data()

    def delete_category(self, name):
        if messagebox.askyesno("ยืนยัน", f"ต้องการลบหมวดหมู่ '{name}' ใช่หรือไม่?"):
            db_func.deleteCategory(name)
            self.reload_data()


# --- หน้าหลัก EditPage ---
class EditPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # แบ่งหน้าจอซ้าย-ขวา
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ใส่ Frame ย่อยลงไป
        self.acc_frame = ManageAccountsFrame(self)
        self.acc_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.cat_frame = ManageCategoriesFrame(self)
        self.cat_frame.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

    def refresh_data(self):
        """ฟังก์ชันนี้เอาไว้ให้ Main App เรียกเวลาสลับหน้ามาที่นี่ เพื่อโหลดข้อมูลใหม่"""
        self.acc_frame.reload_data()
        self.cat_frame.reload_data()