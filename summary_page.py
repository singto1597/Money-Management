import customtkinter as ctk
import db_function as db_func

# --- Import ส่วนของ Matplotlib ---
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import platform
import matplotlib.font_manager as fm
from datetime import datetime, timedelta

def get_thai_font():
    """ค้นหาฟอนต์ภาษาไทยที่ใช้ได้ในเครื่อง"""
    system_os = platform.system()
    
    target_fonts = []
    if system_os == "Linux":
        target_fonts = ['Waree', 'Loma', 'Garuda', 'Umpush', 'Noto Sans Thai']
    elif system_os == "Windows":
        target_fonts = ['Tahoma', 'Microsoft Sans Serif', 'Angsana New', 'Leelawadee']
    elif system_os == "Darwin": # MacOS
        target_fonts = ['Ayuthaya', 'Thonburi']
    available_fonts = set(f.name for f in fm.fontManager.ttflist)
    
    for font in target_fonts:
        if font in available_fonts:
            return font 
            
    return 'sans-serif'

thai_font_name = get_thai_font()
plt.rcParams['font.family'] = thai_font_name
print(f"Graph using font: {thai_font_name}")

class StatsGraphFrame(ctk.CTkFrame):
    """หน้าแสดงกราฟสถิติรายจ่าย (Pie Chart)"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        ctk.CTkLabel(self, text="สถิติการใช้จ่าย (ทั้งหมด)", font=("Arial", 18, "bold")).pack(pady=10)

        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.reload_chart()

    def reload_chart(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        data = db_func.getExpenseBreakdown()

        if not data:
             ctk.CTkLabel(self.chart_container, text="ยังไม่มีข้อมูลรายจ่าย", font=("Arial", 16)).pack(pady=50)
             return

        # --- 🛠️ ส่วนที่แก้: กรองข้อมูล (Filter) ---
        # สร้าง list ใหม่ ที่ "ไม่เอา" ชื่อหมวดหมู่ที่เกี่ยวกับการโอน
        # หมายเหตุ: ต้องใช้ "ชื่อไทย" ที่โชว์ในกราฟนะครับ ไม่ใช่ type
        ignore_names = ["โอนเงินไป", "ได้รับเงินโอน", "ปรับปรุงยอด"] 
        
        filtered_data = [row for row in data if row['category_name'] not in ignore_names]

        # ถ้ากรองแล้วไม่เหลืออะไรเลย
        if not filtered_data:
             ctk.CTkLabel(self.chart_container, text="ไม่มีข้อมูลรายจ่าย (ไม่รวมโอน)", font=("Arial", 16)).pack(pady=50)
             return

        # แยกข้อมูลจากตัวที่กรองแล้ว
        labels = [row['category_name'] for row in filtered_data]
        sizes = [row['total_amount'] for row in filtered_data]
        
        colors = ['#ff9999','#66b3ff','#99ff99','#ffcc99', '#c2c2f0','#ffb3e6']

        fig, ax = plt.subplots(figsize=(6, 5)) 
        
        wedges, texts, autotexts = ax.pie(
            sizes, 
            labels=labels, 
            colors=colors,
            autopct='%1.1f%%',
            startangle=90,
            textprops=dict(color="black") 
        )
        
        ax.axis('equal')  
        plt.setp(autotexts, size=10, weight="bold")
        plt.setp(texts, size=12)

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


class AccountsSummaryFrame(ctk.CTkFrame):
    """หน้าแสดงสรุปยอดเงินคงเหลือในแต่ละกระเป๋า"""
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        ctk.CTkLabel(self, text="ยอดเงินคงเหลือในกระเป๋า", font=("Arial", 18, "bold")).pack(pady=10)

        self.scroll_frame = ctk.CTkScrollableFrame(self)
        self.scroll_frame.pack(fill="both", expand=True, padx=15, pady=10)

        self.lbl_total_wealth = ctk.CTkLabel(self, text="กำลังคำนวณ...", font=("Arial", 16, "bold"))
        self.lbl_total_wealth.pack(pady=15)

        self.reload_data()

    def reload_data(self):
        for widget in self.scroll_frame.winfo_children():
            widget.destroy()

        accounts = db_func.getAllAccountBalances()
        total_wealth = 0

        for acc in accounts:
            balance = acc['account_balance']
            total_wealth += balance
            
            card = ctk.CTkFrame(self.scroll_frame)
            card.pack(fill="x", pady=5)

            icon = "💰" if acc['account_type'] == 'cash' else "🏦"
            
            ctk.CTkLabel(card, text=f"{icon} {acc['account_name']}", font=("Arial", 14, "bold"), anchor="w").pack(side="left", padx=15, pady=10)

            bal_color = "#2ecc71" if balance >= 0 else "#e74c3c"
            ctk.CTkLabel(card, text=f"{balance:,.2f} บาท", font=("Arial", 16, "bold"), text_color=bal_color).pack(side="right", padx=15, pady=10)

        self.lbl_total_wealth.configure(text=f"รวมทรัพย์สินทั้งหมด: {total_wealth:,.2f} บาท")

class MonthlyBarGraphFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        
        # แสดงเดือนปัจจุบันในหัวข้อ
        current_month = datetime.now().strftime("%B %Y")
        ctk.CTkLabel(self, text=f"สรุปรายจ่ายรายเดือน ({current_month})", font=("Arial", 18, "bold")).pack(pady=10)

        self.chart_container = ctk.CTkFrame(self, fg_color="transparent")
        self.chart_container.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.reload_chart()

    def reload_chart(self):
        for widget in self.chart_container.winfo_children():
            widget.destroy()

        # 1. คำนวณวันแรกและวันสุดท้ายของเดือนปัจจุบัน
        now = datetime.now()
        start_date = now.replace(day=1) # วันที่ 1 ของเดือน
        # หาวันสุดท้ายของเดือน (วิธี: ไปเดือนหน้า แล้วลบ 1 วัน)
        next_month = (start_date + timedelta(days=32)).replace(day=1)
        end_date = next_month - timedelta(days=1)

        s_str = start_date.strftime("%Y-%m-%d")
        e_str = end_date.strftime("%Y-%m-%d")

        # 2. ดึงข้อมูล Transaction ตามช่วงเวลา (ใช้ฟังก์ชันที่มีอยู่แล้ว!)
        transactions = db_func.getTransactionsByDateRange(s_str, e_str)

        # 3. รวมยอดเงินแยกตามหมวดหมู่ (Aggregation in Python)
        expense_data = {}
        for t in transactions:
            # เอาเฉพาะรายจ่าย (expense) และการโอนออก (transfrom_from)
            if t['category_type'] == 'expense':
                cat_name = t['category_name']
                amount = t['amount']
                
                # บวกสะสมยอดเงิน
                if cat_name in expense_data:
                    expense_data[cat_name] += amount
                else:
                    expense_data[cat_name] = amount

        if not expense_data:
             ctk.CTkLabel(self.chart_container, text=f"เดือนนี้ยังไม่มีรายจ่าย", font=("Arial", 16)).pack(pady=50)
             return

        # เตรียมข้อมูลกราฟ
        # เรียงลำดับจากมากไปน้อย เพื่อความสวยงาม
        sorted_data = sorted(expense_data.items(), key=lambda item: item[1], reverse=True)
        categories = [item[0] for item in sorted_data]
        amounts = [item[1] for item in sorted_data]

        # 4. วาดกราฟแท่ง
        fig, ax = plt.subplots(figsize=(6, 5))
        
        # วาดแท่ง
        bars = ax.bar(categories, amounts, color='#4caf50', zorder=3)
        
        # ตกแต่งกราฟ
        ax.set_ylabel('จำนวนเงิน (บาท)')
        ax.grid(axis='y', linestyle='--', alpha=0.7, zorder=0)
        
        # หมุนชื่อหมวดหมู่ถ้ามันยาวเกินไป
        plt.xticks(rotation=45, ha='right')
        
        # ใส่ตัวเลขบนหัวแท่ง
        ax.bar_label(bars, fmt='%.0f', padding=3)
        
        # ปรับขอบล่างให้มีที่เหลือสำหรับชื่อแกน X
        plt.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=self.chart_container)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

class SummaryPage(ctk.CTkTabview):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        self.add("ยอดเงินกระเป๋า")
        self.add("ภาพรวม (Pie)")
        self.add("รายเดือน (Bar)")

        self.pie_frame = StatsGraphFrame(self.tab("ภาพรวม (Pie)"))
        self.pie_frame.pack(fill="both", expand=True)

        self.bar_frame = MonthlyBarGraphFrame(self.tab("รายเดือน (Bar)"))
        self.bar_frame.pack(fill="both", expand=True)

        self.balance_frame = AccountsSummaryFrame(self.tab("ยอดเงินกระเป๋า"))
        self.balance_frame.pack(fill="both", expand=True)
        
        self.configure(command=self.on_tab_change)

    def refresh_data(self):
        """รีโหลดข้อมูลทุกหน้า"""
        self.pie_frame.reload_chart()
        self.bar_frame.reload_chart()
        self.balance_frame.reload_data()

    def on_tab_change(self):
        tab = self.get()
        if tab == "ภาพรวม (Pie)":
            self.pie_frame.reload_chart()
        elif tab == "รายเดือน (Bar)":
            self.bar_frame.reload_chart()
        else:
            self.balance_frame.reload_data()