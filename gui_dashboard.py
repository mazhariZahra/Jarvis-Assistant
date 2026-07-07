import sys
import threading
import customtkinter as ctk
import os
import time
import datetime

# import فایل اصلی جارویس
import jarvis
import psutil

# ==================== تنظیمات ظاهری ====================
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

# رنگ‌های سفارشی
BG_DARK = "#0f1117"
BG_CARD = "#1a1d27"
BG_CARD_HOVER = "#222533"
ACCENT_BLUE = "#3b82f6"
ACCENT_GREEN = "#10b981"
ACCENT_RED = "#ef4444"
ACCENT_YELLOW = "#f59e0b"
ACCENT_PURPLE = "#8b5cf6"
TEXT_PRIMARY = "#e2e8f0"
TEXT_SECONDARY = "#94a3b8"
BORDER = "#2d3340"

# ==================== Redirect خروجی ====================
class OutputRedirector:
    def __init__(self, callback):
        self.callback = callback
    def write(self, text):
        if text.strip():
            self.callback(text.strip())
    def flush(self):
        pass

# ==================== رشته جارویس ====================
class JarvisThread(threading.Thread):
    def __init__(self, output_callback):
        super().__init__()
        self.output_callback = output_callback
        self.daemon = True
        self._stop_event = threading.Event()
    
    def stop(self):
        """توقف امن رشته"""
        self._stop_event.set()
    
    def run(self):
        import sys
        sys.stdout = OutputRedirector(self.output_callback)
        jarvis.run_jarvis()

# ==================== کارت وضعیت سیستم ====================
class SystemCard(ctk.CTkFrame):
    def __init__(self, master, title, icon, color):
        super().__init__(master, fg_color=BG_CARD, corner_radius=15, border_width=1, border_color=BORDER)
        self.color = color
        
        # هدر کارت
        self.header = ctk.CTkFrame(self, fg_color="transparent")
        self.header.pack(fill="x", padx=15, pady=(15, 5))
        
        self.icon_label = ctk.CTkLabel(self.header, text=icon, font=ctk.CTkFont(size=20))
        self.icon_label.pack(side="left")
        
        self.title_label = ctk.CTkLabel(
            self.header, text=title,
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=TEXT_SECONDARY
        )
        self.title_label.pack(side="left", padx=8)
        
        # مقدار
        self.value_label = ctk.CTkLabel(
            self, text="--",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=color
        )
        self.value_label.pack(pady=(5, 5))
        
        # نوار پیشرفت
        self.progress = ctk.CTkProgressBar(self, height=6, corner_radius=3, fg_color="#2d3340", progress_color=color)
        self.progress.pack(fill="x", padx=15, pady=(0, 15))
        self.progress.set(0)
    
    def update_value(self, value, unit="%"):
        self.value_label.configure(text=f"{value}{unit}")
        self.progress.set(value / 100)

# ==================== پنجره اصلی ====================
class DashboardApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # تنظیمات پنجره
        self.title("J.A.R.V.I.S | داشبورد مدیریت")
        self.geometry("1100x700")
        self.minsize(1000, 650)
        self.configure(fg_color=BG_DARK)
        
        # ========== هدر ==========
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(fill="x", padx=25, pady=(20, 10))
        
        # لوگو و عنوان
        self.logo_frame = ctk.CTkFrame(self.header_frame, fg_color="transparent")
        self.logo_frame.pack(side="left")
        
        self.logo = ctk.CTkLabel(
            self.logo_frame,
            text="⚡",
            font=ctk.CTkFont(size=32)
        )
        self.logo.pack(side="left")
        
        self.title_text = ctk.CTkLabel(
            self.logo_frame,
            text="J.A.R.V.I.S",
            font=ctk.CTkFont(family="Segoe UI", size=28, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.title_text.pack(side="left", padx=10)
        
        self.version_label = ctk.CTkLabel(
            self.logo_frame,
            text="v2.0",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.version_label.pack(side="left")
        
        # ساعت
        self.clock_label = ctk.CTkLabel(
            self.header_frame,
            text="",
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.clock_label.pack(side="right")
        self.update_clock()
        
        # وضعیت
        self.status_badge = ctk.CTkFrame(self.header_frame, fg_color=BG_CARD, corner_radius=20, width=130, height=35)
        self.status_badge.pack(side="right", padx=15)
        self.status_badge.pack_propagate(False)
        
        self.status_dot = ctk.CTkLabel(self.status_badge, text="●", font=ctk.CTkFont(size=12), text_color=ACCENT_RED)
        self.status_dot.place(relx=0.15, rely=0.5, anchor="center")
        
        self.status_text = ctk.CTkLabel(self.status_badge, text="غیرفعال", font=ctk.CTkFont(size=12), text_color=TEXT_SECONDARY)
        self.status_text.place(relx=0.55, rely=0.5, anchor="center")
        
        # ========== محتوای اصلی (دو ستونه) ==========
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.pack(fill="both", expand=True, padx=25, pady=10)
        
        # ستون چپ: کارت‌های وضعیت
        self.left_column = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.left_column.pack(side="left", fill="both", expand=True, padx=(0, 8))
        
        # ردیف اول کارت‌ها
        self.cards_row1 = ctk.CTkFrame(self.left_column, fg_color="transparent")
        self.cards_row1.pack(fill="x", pady=(0, 8))
        
        self.cpu_card = SystemCard(self.cards_row1, "پردازنده", "🧠", ACCENT_BLUE)
        self.cpu_card.pack(side="left", fill="both", expand=True, padx=(0, 4))
        
        self.ram_card = SystemCard(self.cards_row1, "حافظه رم", "💾", ACCENT_PURPLE)
        self.ram_card.pack(side="left", fill="both", expand=True, padx=(4, 0))
        
        # ردیف دوم کارت‌ها
        self.cards_row2 = ctk.CTkFrame(self.left_column, fg_color="transparent")
        self.cards_row2.pack(fill="x", pady=(0, 8))
        
        self.battery_card = SystemCard(self.cards_row2, "باتری", "🔋", ACCENT_GREEN)
        self.battery_card.pack(side="left", fill="both", expand=True, padx=(0, 4))
        
        self.disk_card = SystemCard(self.cards_row2, "دیسک", "💿", ACCENT_YELLOW)
        self.disk_card.pack(side="left", fill="both", expand=True, padx=(4, 0))
        
        # کارت وضعیت کلی
        self.status_card = ctk.CTkFrame(self.left_column, fg_color=BG_CARD, corner_radius=15, border_width=1, border_color=BORDER, height=100)
        self.status_card.pack(fill="x")
        
        self.status_card_title = ctk.CTkLabel(
            self.status_card, text="📊 وضعیت کلی سیستم",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.status_card_title.pack(pady=(12, 5))
        
        self.status_card_text = ctk.CTkLabel(
            self.status_card, text="همه چیز عادی است",
            font=ctk.CTkFont(size=12),
            text_color=TEXT_SECONDARY
        )
        self.status_card_text.pack(pady=(0, 12))
        
        # ستون راست: کنسول و کنترل
        self.right_column = ctk.CTkFrame(self.main_frame, fg_color="transparent", width=420)
        self.right_column.pack(side="right", fill="both", expand=True, padx=(8, 0))
        self.right_column.pack_propagate(False)
        
        # دکمه‌های کنترل
        self.control_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        self.control_frame.pack(fill="x", pady=(0, 8))
        
        self.start_btn = ctk.CTkButton(
            self.control_frame,
            text="▶ فعال‌سازی",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=ACCENT_GREEN,
            hover_color="#059669",
            command=self.start_jarvis
        )
        self.start_btn.pack(side="left", fill="x", expand=True, padx=(0, 4))
        
        self.stop_btn = ctk.CTkButton(
            self.control_frame,
            text="⏹ توقف",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
            corner_radius=10,
            fg_color=ACCENT_RED,
            hover_color="#dc2626",
            command=self.stop_jarvis,
            state="disabled"
        )
        self.stop_btn.pack(side="left", fill="x", expand=True, padx=(4, 0))
        
        # دکمه‌های سریع
        self.quick_frame = ctk.CTkFrame(self.right_column, fg_color="transparent")
        self.quick_frame.pack(fill="x", pady=(0, 8))
        
        self.screenshot_btn = ctk.CTkButton(
            self.quick_frame, text="📸 اسکرین‌شات", width=90, height=32, corner_radius=8,
            fg_color=BG_CARD, hover_color=BG_CARD_HOVER, border_width=1, border_color=BORDER,
            command=self.quick_screenshot
        )
        self.screenshot_btn.pack(side="left", padx=(0, 4))
        
        self.music_btn = ctk.CTkButton(
            self.quick_frame, text="🎵 پخش موزیک", width=90, height=32, corner_radius=8,
            fg_color=BG_CARD, hover_color=BG_CARD_HOVER, border_width=1, border_color=BORDER,
            command=self.quick_music
        )
        self.music_btn.pack(side="left", padx=4)
        
        self.weather_btn = ctk.CTkButton(
            self.quick_frame, text="🌤️ آب و هوا", width=90, height=32, corner_radius=8,
            fg_color=BG_CARD, hover_color=BG_CARD_HOVER, border_width=1, border_color=BORDER,
            command=self.quick_weather
        )
        self.weather_btn.pack(side="left", padx=4)
        
        # کنسول
        self.console_frame = ctk.CTkFrame(self.right_column, fg_color=BG_CARD, corner_radius=15, border_width=1, border_color=BORDER)
        self.console_frame.pack(fill="both", expand=True)
        
        self.console_header = ctk.CTkFrame(self.console_frame, fg_color="transparent")
        self.console_header.pack(fill="x", padx=15, pady=(10, 0))
        
        self.console_title = ctk.CTkLabel(
            self.console_header, text="📋 کنسول خروجی",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=TEXT_PRIMARY
        )
        self.console_title.pack(side="left")
        
        self.clear_btn = ctk.CTkButton(
            self.console_header, text="پاک کردن", width=70, height=25, corner_radius=6,
            fg_color="transparent", hover_color=BG_CARD_HOVER, border_width=1, border_color=BORDER,
            font=ctk.CTkFont(size=11), command=self.clear_console
        )
        self.clear_btn.pack(side="right")
        
        self.console = ctk.CTkTextbox(
            self.console_frame,
            font=ctk.CTkFont(family="Consolas", size=11),
            fg_color="#0a0d14",
            text_color="#00e676",
            corner_radius=10,
            border_width=0
        )
        self.console.pack(pady=8, padx=8, fill="both", expand=True)
        self.console.insert("end", "╔══════════════════════════════╗\n")
        self.console.insert("end", "║   به جارویس خوش آمدید! 🌟  ║\n")
        self.console.insert("end", "║   آماده دریافت فرمان...     ║\n")
        self.console.insert("end", "╚══════════════════════════════╝\n\n")
        self.console.configure(state="disabled")
        
        # ========== متغیرها ==========
        self.jarvis_thread = None
        self.is_running = False
        
        # آپدیت دوره‌ای وضعیت سیستم
        self.update_system_info()
    
    # ========== ساعت ==========
    def update_clock(self):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.clock_label.configure(text=now)
        self.after(1000, self.update_clock)
    
    # ========== وضعیت سیستم ==========
    def update_system_info(self):
        try:
            cpu = psutil.cpu_percent()
            ram = psutil.virtual_memory().percent
            battery = psutil.sensors_battery()
            battery_percent = battery.percent if battery else 0
            disk = psutil.disk_usage('/').percent
            
            self.cpu_card.update_value(cpu)
            self.ram_card.update_value(ram)
            self.battery_card.update_value(battery_percent)
            self.disk_card.update_value(disk)
            
            # وضعیت کلی
            if cpu > 80 or ram > 80:
                self.status_card_text.configure(text="⚠️ فشار بالای سیستم", text_color=ACCENT_YELLOW)
            else:
                self.status_card_text.configure(text="✅ همه چیز عادی است", text_color=ACCENT_GREEN)
        except:
            pass
        
        self.after(2000, self.update_system_info)
    
    # ========== شروع ==========
    def start_jarvis(self):
        self.is_running = True
        self.start_btn.configure(state="disabled", text="🟢 در حال اجرا...")
        self.stop_btn.configure(state="normal")
        self.status_dot.configure(text_color=ACCENT_GREEN)
        self.status_text.configure(text="فعال")
        self.append_console("🚀 جارویس فعال شد.\n")
        
        self.jarvis_thread = JarvisThread(self.append_console)
        self.jarvis_thread.start()
    
    # ========== توقف ==========
    def stop_jarvis(self):
        self.is_running = False
        if self.jarvis_thread and self.jarvis_thread.is_alive():
            self.jarvis_thread.stop()
            self.jarvis_thread.join(timeout=2)
        
        self.start_btn.configure(state="normal", text="▶ فعال‌سازی")
        self.stop_btn.configure(state="disabled")
        self.status_dot.configure(text_color=ACCENT_RED)
        self.status_text.configure(text="غیرفعال")
        self.append_console("⏹️ جارویس متوقف شد.\n")
    
    # ========== دکمه‌های سریع ==========
    def quick_screenshot(self):
        self.append_console("📸 در حال گرفتن اسکرین‌شات...\n")
        jarvis.take_screenshot()
    
    def quick_music(self):
        self.append_console("🎵 در حال پخش موزیک...\n")
        jarvis.play_music()
    
    def quick_weather(self):
        self.append_console("🌤️ در حال دریافت آب و هوا...\n")
        # صدا می‌کنیم ولی توی کنسول نمایش داده نمیشه چون speak مستقیم کار می‌کنه
        threading.Thread(target=lambda: jarvis.get_weather("دامغان")).start()
    
    # ========== کنسول ==========
    def append_console(self, text):
        self.console.configure(state="normal")
        self.console.insert("end", text)
        self.console.see("end")
        self.console.configure(state="disabled")
    
    def clear_console(self):
        self.console.configure(state="normal")
        self.console.delete("1.0", "end")
        self.console.configure(state="disabled")

# ==================== اجرا ====================
if __name__ == "__main__":
    app = DashboardApp()
    app.mainloop()