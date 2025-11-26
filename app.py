import customtkinter as ctk
import db
import db_function as db_func
import add_page
import history_page
import edit_page

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

        
        self.add_page = add_page.AddPage(master=self)
        self.history_page = history_page.HistoryPage(master=self)
        self.edit_page = edit_page.EditPage(master=self)

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
        self.btn_edit.configure(fg_color="transparent")
        
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