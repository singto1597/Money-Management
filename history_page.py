import customtkinter as ctk
import db
import db_function as db_func

class HistoryPage(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        ctk.CTkLabel(self, text="หน้าประวัติการเงิน", font=("Arial", 24)).pack(pady=50)