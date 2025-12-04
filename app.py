import sys
import customtkinter as ctk
import webbrowser
# import db
# import db_function as db_func
import add_page
import history_page
import edit_page
import summary_page
import debt_page
import initial_db

class MoneyApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Money Management")
        self.geometry("1000x600")

        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.sidebar_frame = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(6, weight=1)


        self.logo_label = ctk.CTkLabel(self.sidebar_frame, text="Money Manager", font=ctk.CTkFont(size=20, weight="bold"))
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.btn_add = self.create_sidebar_button("เพิ่มรายการ", self.show_add_page, row=1)
        self.btn_history = self.create_sidebar_button("ประวัติ", self.show_history_page, row=2)
        self.btn_summary = self.create_sidebar_button("สรุป/สถิติ", self.show_summary_page, row=3)
        self.btn_debt = self.create_sidebar_button("หนี้สิน/ลูกหนี้", self.show_debt_page, row=4)
        self.btn_edit = self.create_sidebar_button("แก้ไขข้อมูล", self.show_edit_page, row=5)
        self.credit_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Created by Phatthanaphon Sutham", 
            font=ctk.CTkFont(size=10),       # ตัวเล็กๆ
            text_color=("gray50", "gray70"), # สีจางๆ (เทาเข้ม/เทาอ่อน)
            cursor="hand2"                   # เปลี่ยนเมาส์เป็นรูปมือเมื่อชี้
        )
        self.credit_label.grid(row=6, column=0, padx=20, pady=10, sticky="s")

        self.credit_label.bind("<Button-1>", lambda event: self.open_github())
        
        self.credit_label.bind("<Enter>", lambda event: self.credit_label.configure(text_color="white")) 
        self.credit_label.bind("<Leave>", lambda event: self.credit_label.configure(text_color=("gray50", "gray70")))
        
        self.add_page = add_page.AddPage(master=self)
        self.history_page = history_page.HistoryPage(master=self)
        self.summary_page = summary_page.SummaryPage(master=self)
        self.debt_page = debt_page.DebtPage(master=self, on_settle_callback=self.settle_debt_action)
        self.edit_page = edit_page.EditPage(master=self)

        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.show_add_page()

    def create_sidebar_button(self, text, command, row):
        btn = ctk.CTkButton(self.sidebar_frame, text=text, command=command,
                            fg_color="transparent", text_color=("gray10", "gray90"), hover_color=("gray70", "gray30"),
                            anchor="w")
        btn.grid(row=row, column=0, padx=20, pady=10, sticky="ew")
        return btn

    def select_button(self, btn):
        """ เปลี่ยนสีปุ่มที่ถูกเลือก """
        self.btn_add.configure(fg_color="transparent")
        self.btn_history.configure(fg_color="transparent")
        self.btn_summary.configure(fg_color="transparent")
        self.btn_edit.configure(fg_color="transparent")
        self.btn_debt.configure(fg_color="transparent")
        
        btn.configure(fg_color=("gray75", "gray25"))

    def show_add_page(self):
        self.select_button(self.btn_add)
        self.hide_all_pages()
        self.add_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.add_page.refresh_data() 

    def show_history_page(self):
        self.select_button(self.btn_history)
        self.hide_all_pages()
        self.history_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.history_page.refresh_data()
    
    def show_summary_page(self):
        self.select_button(self.btn_summary)
        self.hide_all_pages()
        self.summary_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.summary_page.refresh_data()

    def show_edit_page(self):
        self.select_button(self.btn_edit)
        self.hide_all_pages()
        self.edit_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.edit_page.refresh_data() 

    def hide_all_pages(self):
        self.add_page.grid_forget()
        self.history_page.grid_forget()
        self.edit_page.grid_forget()
        self.summary_page.grid_forget()
        self.debt_page.grid_forget()

    def show_debt_page(self):
        self.select_button(self.btn_debt)
        self.hide_all_pages()
        self.debt_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        self.debt_page.refresh_data()



    def on_closing(self):
        print("Closing App...")
        
        try:
            if hasattr(self, 'summary_page'):
                import matplotlib.pyplot as plt
                plt.close('all')
        except Exception as e:
            print(f"Error closing plot: {e}")

        self.destroy()

        sys.exit(0)
    def open_github(self):
        """เปิดลิงค์ GitHub ใน Browser"""
        webbrowser.open("https://github.com/singto1597/Money-Management")
    def settle_debt_action(self, from_acc, to_acc, amount):
        """ฟังก์ชันนี้จะถูกเรียกเมื่อกดปุ่ม Settle ในหน้าหนี้สิน"""
        self.select_button(self.btn_add)
        self.hide_all_pages()

        self.add_page.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.add_page.switch_to_transfer_and_fill(from_acc, to_acc, amount)

if __name__ == "__main__":
    print("Checking Database...")
    try:
        initial_db.initializeApp() 
        print("Database initialized successfully.")
    except Exception as e:
        print(f"Database init error: {e}")

    app = MoneyApp()
    app.mainloop()