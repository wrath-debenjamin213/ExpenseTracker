import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import csv
import os
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import hashlib

class ModernExpenseTracker:
    def __init__(self, root):
        self.root = root
        self.root.title("💰 Exchequer")
        self.root.geometry("1000x600")
        self.root.minsize(800, 500)

        # Theme colors (unchanged)
        self.dark_colors = {
            "primary": "#2a3f5f",
            "secondary": "#4a6fa5",
            "accent": "#ff6b6b",
            "background": "#1e1e2e",
            "card": "#2d2d3d",
            "text": "#e0e0e0",
            "success": "#4caf50",
            "warning": "#ff9800",
            "danger": "#f44336",
            "highlight": "#6c5ce7",
            "info": "#00bcd4",
            "button_text": "#ffffff",
            "shadow": "#1a1a2a"
        }

        self.light_colors = {
            "primary": "#4a6fa5",
            "secondary": "#2a3f5f",
            "accent": "#ff6b6b",
            "background": "#f5f5f5",
            "card": "#ffffff",
            "text": "#333333",
            "success": "#4caf50",
            "warning": "#ff9800",
            "danger": "#f44336",
            "highlight": "#6c5ce7",
            "info": "#00bcd4",
            "button_text": "#ffffff",
            "shadow": "#e0e0e0"
        }

        self.themes = {"dark": self.dark_colors, "light": self.light_colors}
        self.current_theme = "dark"
        self.colors = self.themes[self.current_theme]

        self.fonts = {
            "title": ("Segoe UI", 20, "bold"),
            "header": ("Segoe UI", 16, "bold"),
            "subheader": ("Segoe UI", 12),
            "body": ("Segoe UI", 10),
            "small": ("Segoe UI", 9),
            "button": ("Segoe UI", 11, "bold")
        }

        self.categories = ["Food", "Transport", "Shopping", "Bills", "Entertainment", "Health", "Education", "Other"]
        self.sip_categories = ["Mutual Fund", "Stocks", "ETF", "Fixed Deposit", "Other"]
        self.users_file = "users.csv"
        self.current_user = None
        self.user_data = {}
        self.next_expense_id = 1
        self.next_sip_id = 1

        self.root.configure(bg=self.colors["background"])
        self.create_login_frame()
        self.login_frame.pack(fill="both", expand=True)

    def create_button(self, parent, text, command, bg_color, small=False):
        btn_font = self.fonts["small"] if small else self.fonts["button"]
        btn = tk.Button(parent, text=text, command=command,
                        font=btn_font, bg=bg_color, fg=self.colors["button_text"],
                        bd=0, relief="flat", highlightthickness=0,
                        activebackground=self.darken_color(bg_color, 10),
                        activeforeground=self.colors["button_text"],
                        padx=12, pady=6, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.lighten_color(bg_color, 15), fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=bg_color, fg=self.colors["button_text"]))
        return btn

    def create_entry(self, parent, row=None, column=None):
        entry_frame = tk.Frame(parent, bg=self.colors["card"])
        entry_frame.pack(fill="x", padx=5, pady=5)
        entry = tk.Entry(entry_frame, font=self.fonts["body"], bd=0,
                        bg="#3a3a4a" if self.current_theme == "dark" else "#e0e0e0",
                        fg=self.colors["text"], insertbackground=self.colors["text"],
                        relief="flat")
        entry.pack(fill="x", padx=5, pady=5, ipady=6)
        return entry

    def create_login_frame(self):
        self.login_frame = tk.Frame(self.root, bg=self.colors["background"])
        
        header = tk.Frame(self.login_frame, bg=self.colors["primary"], height=120)
        header.pack(fill="x")
        
        logo_canvas = tk.Canvas(header, width=80, height=80, bg=self.colors["primary"], 
                              highlightthickness=0)
        logo_canvas.pack(pady=20)
        logo_canvas.create_oval(10, 10, 70, 70, fill=self.colors["accent"], outline="")
        logo_canvas.create_text(40, 40, text="₹", font=("Segoe UI", 30, "bold"), 
                              fill=self.colors["button_text"])

        shadow_frame = tk.Frame(self.login_frame, bg=self.colors["shadow"])
        shadow_frame.pack(pady=40, padx=40, fill="both", expand=True)
        login_container = tk.Frame(shadow_frame, bg=self.colors["card"], padx=20, pady=20)
        login_container.pack(padx=5, pady=5)

        welcome_frame = tk.Frame(login_container, bg=self.colors["card"])
        welcome_frame.pack(pady=(0, 20))
        self.welcome_label = tk.Label(welcome_frame, text="Welcome to Exchequer",
                                    font=("Segoe UI", 18, "bold"), bg=self.colors["card"],
                                    fg=self.colors["text"])
        self.welcome_label.pack()
        self.animate_welcome()

        tk.Label(login_container, text="Username", font=self.fonts["subheader"],
                bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=(10, 5))
        self.username_entry = self.create_entry(login_container)
        self.username_entry.pack(fill="x", pady=5)

        tk.Label(login_container, text="Password", font=self.fonts["subheader"],
                bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=(10, 5))
        self.password_entry = self.create_entry(login_container)
        self.password_entry.pack(fill="x", pady=5)
        self.password_entry.config(show="*")

        button_frame = tk.Frame(login_container, bg=self.colors["card"])
        button_frame.pack(pady=25)
        self.create_button(button_frame, "Login 🔑", self.login,
                         self.colors["success"]).pack(side="left", padx=10, ipadx=15, ipady=8)
        self.create_button(button_frame, "Sign Up 📝", self.signup,
                         self.colors["highlight"]).pack(side="left", padx=10, ipadx=15, ipady=8)

        footer = tk.Label(self.login_frame, text="Track your finances with style © 2025",
                         font=self.fonts["small"], bg=self.colors["background"],
                         fg=self.lighten_color(self.colors["text"], 20))
        footer.pack(side="bottom", pady=10)

    def animate_welcome(self):
        colors = [self.colors["text"], self.colors["accent"], self.colors["highlight"]]
        current_color = self.welcome_label.cget("fg")
        next_color = colors[(colors.index(current_color) + 1) % len(colors)]
        self.welcome_label.config(fg=next_color)
        self.root.after(2000, self.animate_welcome)

    def login(self):
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())
        if not username or not password:
            self.show_custom_message("ERROR", "Please enter both username and password", "error")
            return
        if not os.path.exists(self.users_file):
            self.show_custom_message("ERROR", "No users registered yet. Please sign up first.", "error")
            return
        with open(self.users_file, mode='r', newline='') as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    self.current_user = username
                    self.initialize_user_data()
                    self.login_frame.pack_forget()
                    self.initialize_main_app()
                    return
        self.show_custom_message("ERROR", "Invalid username or password", "error")

    def signup(self):
        username = self.username_entry.get()
        password = self.hash_password(self.password_entry.get())
        if not username or not password:
            self.show_custom_message("ERROR", "Please enter both username and password", "error")
            return
        if os.path.exists(self.users_file):
            with open(self.users_file, mode='r', newline='') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row['username'] == username:
                        self.show_custom_message("ERROR", "Username already exists", "error")
                        return
        user_data = [{'username': username, 'password': password}]
        fieldnames = ['username', 'password']
        mode = 'a' if os.path.exists(self.users_file) else 'w'
        with open(self.users_file, mode=mode, newline='') as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            if mode == 'w':
                writer.writeheader()
            writer.writerows(user_data)
        self.show_custom_message("SUCCESS", "Sign up successful! Please login.", "success")
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()

    def initialize_user_data(self):
        if self.current_user not in self.user_data:
            self.user_data[self.current_user] = {
                'expenses': [],
                'sips': [],
                'monthly_budget': 0.0,
                'daily_budget': 0.0,
                'monthly_goals': {},
                'csv_file': f"expenses_{self.current_user}.csv",
                'sip_csv_file': f"sips_{self.current_user}.csv",
                'goals_file': f"goals_{self.current_user}.csv"
            }
        self.load_user_data()

    def load_user_data(self):
        user = self.user_data[self.current_user]
        if os.path.exists(user['csv_file']):
            with open(user['csv_file'], mode='r', newline='') as file:
                reader = csv.DictReader(file)
                user['expenses'] = []
                for row in reader:
                    row['amount'] = float(row['amount'])
                    row['id'] = int(row['id'])
                    user['expenses'].append(row)
                self.next_expense_id = max([exp['id'] for exp in user['expenses']] + [0]) + 1
        if os.path.exists(user['sip_csv_file']):
            with open(user['sip_csv_file'], mode='r', newline='') as file:
                reader = csv.DictReader(file)
                user['sips'] = []
                for row in reader:
                    row['amount'] = float(row['amount'])
                    row['id'] = int(row['id'])
                    user['sips'].append(row)
                self.next_sip_id = max([sip['id'] for sip in user['sips']] + [0]) + 1
        if os.path.exists(user['goals_file']):
            with open(user['goals_file'], mode='r', newline='') as file:
                reader = csv.DictReader(file)
                user['monthly_goals'] = {row['category']: float(row['amount']) for row in reader}

    def save_user_data(self):
        user = self.user_data[self.current_user]
        with open(user['csv_file'], mode='w', newline='') as file:
            fieldnames = ['id', 'date', 'category', 'amount', 'description']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(user['expenses'])
        with open(user['sip_csv_file'], mode='w', newline='') as file:
            fieldnames = ['id', 'name', 'amount', 'category', 'frequency', 'start_date']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(user['sips'])
        with open(user['goals_file'], mode='w', newline='') as file:
            fieldnames = ['category', 'amount']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows([{'category': cat, 'amount': amt} for cat, amt in user['monthly_goals'].items()])

    def initialize_main_app(self):
        self.create_nav_bar()
        self.create_main_frame()
        self.create_add_expense_frame()
        self.create_view_expenses_frame()
        self.create_stats_frame()
        self.create_settings_frame()
        self.create_sip_tracker_frame()
        self.create_view_sips_frame()  # New frame for viewing SIPs
        self.create_budget_frame()
        self.show_frame(self.main_frame)
        self.load_user_data()
        self.check_budget_alerts()

    def create_nav_bar(self):
        self.nav_frame = tk.Frame(self.root, bg=self.colors["primary"], height=50)
        self.nav_frame.pack(fill="x", side="top")

        file_btn = self.create_nav_button(self.nav_frame, "📁 File", self.show_file_menu)
        file_btn.pack(side="left", padx=5, pady=5)
        view_btn = self.create_nav_button(self.nav_frame, "👁️ View", self.show_view_menu)
        view_btn.pack(side="left", padx=5, pady=5)
        settings_btn = self.create_nav_button(self.nav_frame, "⚙️ Settings",
                                             lambda: self.show_frame(self.settings_frame))
        settings_btn.pack(side="left", padx=5, pady=5)

        self.file_menu = tk.Menu(self.root, tearoff=0, bg=self.colors["card"], fg=self.colors["text"],
                                activebackground=self.colors["accent"], activeforeground="white",
                                font=self.fonts["body"])
        self.file_menu.add_command(label="📤 Export Data", command=self.export_data)
        self.file_menu.add_command(label="📥 Import Data", command=self.import_data)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="🚪 Logout", command=self.logout)

        self.view_menu = tk.Menu(self.root, tearoff=0, bg=self.colors["card"], fg=self.colors["text"],
                                activebackground=self.colors["accent"], activeforeground="white",
                                font=self.fonts["body"])
        self.view_menu.add_command(label="📊 Dashboard", command=lambda: self.show_frame(self.main_frame))
        self.view_menu.add_command(label="➕ Add Expense", command=lambda: self.show_frame(self.add_expense_frame))
        self.view_menu.add_command(label="📋 View Expenses", command=lambda: self.show_frame(self.view_expenses_frame))
        self.view_menu.add_command(label="📈 Statistics", command=lambda: self.show_frame(self.stats_frame))
        self.view_menu.add_command(label="💹 Add SIP", command=lambda: self.show_frame(self.sip_tracker_frame))
        self.view_menu.add_command(label="📜 View SIPs", command=lambda: self.show_frame(self.view_sips_frame))  # New option
        self.view_menu.add_command(label="💸 Budget", command=lambda: self.show_frame(self.budget_frame))

    def create_nav_button(self, parent, text, command):
        btn = tk.Button(parent, text=text, command=command,
                        font=self.fonts["button"], bg=self.colors["secondary"],
                        fg=self.colors["button_text"], bd=0, relief="flat",
                        activebackground=self.darken_color(self.colors["secondary"], 10),
                        activeforeground=self.colors["button_text"],
                        padx=10, pady=5, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=self.lighten_color(self.colors["secondary"], 15), fg="white"))
        btn.bind("<Leave>", lambda e: btn.config(bg=self.colors["secondary"], fg=self.colors["button_text"]))
        return btn

    def show_file_menu(self):
        self.file_menu.post(self.nav_frame.winfo_rootx() + 5,
                           self.nav_frame.winfo_rooty() + self.nav_frame.winfo_height())

    def show_view_menu(self):
        self.view_menu.post(self.nav_frame.winfo_rootx() + 60,
                           self.nav_frame.winfo_rooty() + self.nav_frame.winfo_height())

    def logout(self):
        self.save_user_data()
        self.current_user = None
        self.nav_frame.pack_forget()
        self.main_frame.pack_forget()
        self.add_expense_frame.pack_forget()
        self.view_expenses_frame.pack_forget()
        self.stats_frame.pack_forget()
        self.settings_frame.pack_forget()
        self.sip_tracker_frame.pack_forget()
        self.view_sips_frame.pack_forget()  # Added
        self.budget_frame.pack_forget()
        self.login_frame.pack(fill="both", expand=True)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def create_main_frame(self):
        self.main_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.main_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="💰 EXPENSE DASHBOARD", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        cards_frame = tk.Frame(self.main_frame, bg=self.colors["background"])
        cards_frame.pack(padx=20, pady=20, fill="both", expand=True)

        total_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        total_card.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(total_card, text="TOTAL EXPENSES", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.total_label = tk.Label(total_card, text="₹0.00", font=("Segoe UI", 16, "bold"),
                                   bg=self.colors["card"], fg=self.colors["success"])
        self.total_label.pack(anchor="w", pady=5)

        recent_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        recent_card.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(recent_card, text="RECENT EXPENSE", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.recent_label = tk.Label(recent_card, text="No recent expenses", font=("Segoe UI", 16, "bold"),
                                    bg=self.colors["card"], fg=self.colors["accent"])
        self.recent_label.pack(anchor="w", pady=5)

        budget_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        budget_card.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(budget_card, text="MONTHLY BUDGET", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.budget_label = tk.Label(budget_card, text="₹0.00 / ₹0.00", font=("Segoe UI", 16, "bold"),
                                    bg=self.colors["card"], fg=self.colors["info"])
        self.budget_label.pack(anchor="w", pady=5)

        category_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        category_card.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")
        tk.Label(category_card, text="TOP CATEGORY", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.cat_label = tk.Label(category_card, text="No data", font=("Segoe UI", 16, "bold"),
                                 bg=self.colors["card"], fg=self.colors["highlight"])
        self.cat_label.pack(anchor="w", pady=5)

        sip_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        sip_card.grid(row=1, column=1, padx=10, pady=10, sticky="nsew")
        tk.Label(sip_card, text="TOTAL SIP", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.sip_total_label = tk.Label(sip_card, text="₹0.00", font=("Segoe UI", 16, "bold"),
                                       bg=self.colors["card"], fg=self.colors["info"])
        self.sip_total_label.pack(anchor="w", pady=5)

        daily_card = tk.Frame(cards_frame, bg=self.colors["card"], padx=15, pady=15)
        daily_card.grid(row=1, column=2, padx=10, pady=10, sticky="nsew")
        tk.Label(daily_card, text="DAILY BUDGET", font=self.fonts["subheader"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w")
        self.daily_label = tk.Label(daily_card, text="₹0.00 / ₹0.00", font=("Segoe UI", 16, "bold"),
                                   bg=self.colors["card"], fg=self.colors["warning"])
        self.daily_label.pack(anchor="w", pady=5)

        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(2, weight=1)
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)

        buttons_frame = tk.Frame(self.main_frame, bg=self.colors["background"], padx=20, pady=15)
        buttons_frame.pack(fill="x")

        self.create_button(buttons_frame, "+ ADD EXPENSE",
                          lambda: self.show_frame(self.add_expense_frame),
                          self.colors["accent"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(buttons_frame, "VIEW ALL",
                          lambda: self.show_frame(self.view_expenses_frame),
                          self.colors["info"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(buttons_frame, "STATS",
                          lambda: self.show_frame(self.stats_frame),
                          self.colors["highlight"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(buttons_frame, "ADD SIP",
                          lambda: self.show_frame(self.sip_tracker_frame),
                          self.colors["success"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(buttons_frame, "BUDGET",
                          lambda: self.show_frame(self.budget_frame),
                          self.colors["warning"]).pack(side="left", padx=5, ipadx=8, ipady=4)

    def create_add_expense_frame(self):
        self.add_expense_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.add_expense_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="➕ ADD NEW EXPENSE", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        form_frame = tk.Frame(self.add_expense_frame, bg=self.colors["card"], padx=20, pady=20)
        form_frame.pack(padx=30, pady=20, fill="both", expand=True)

        tk.Label(form_frame, text="AMOUNT (₹)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.amount_entry = self.create_entry(form_frame)
        self.amount_entry.pack(fill="x", pady=5)

        tk.Label(form_frame, text="CATEGORY", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.category_var = tk.StringVar()
        self.category_dropdown = ttk.Combobox(form_frame, textvariable=self.category_var,
                                             values=self.categories, font=self.fonts["body"])
        self.category_dropdown.pack(fill="x", pady=10)
        self.category_dropdown.current(0)

        tk.Label(form_frame, text="DATE (YYYY-MM-DD)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.date_entry = self.create_entry(form_frame)
        self.date_entry.pack(fill="x", pady=5)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(form_frame, text="DESCRIPTION", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.desc_entry = self.create_entry(form_frame)
        self.desc_entry.pack(fill="x", pady=5)

        button_frame = tk.Frame(form_frame, bg=self.colors["card"])
        button_frame.pack(pady=20)
        self.create_button(button_frame, "💾 SAVE", self.save_expense,
                          self.colors["success"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(button_frame, "🗑️ CLEAR", self.clear_expense_form,
                          self.colors["warning"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(button_frame, "🔙 BACK", lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", padx=5, ipadx=8, ipady=4)

    def create_view_expenses_frame(self):
        self.view_expenses_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.view_expenses_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="📋 EXPENSE HISTORY", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        filter_frame = tk.Frame(self.view_expenses_frame, bg=self.colors["background"], padx=20, pady=15)
        filter_frame.pack(fill="x")

        tk.Label(filter_frame, text="FILTER:", font=self.fonts["subheader"],
                 bg=self.colors["background"], fg=self.colors["text"]).pack(side="left")
        self.month_var = tk.StringVar(value="All")
        months = ["All"] + [datetime(2000, m, 1).strftime("%B") for m in range(1, 13)]
        month_dropdown = ttk.Combobox(filter_frame, textvariable=self.month_var,
                                     values=months, font=self.fonts["body"], width=10)
        month_dropdown.pack(side="left", padx=5, ipady=4)
        month_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_expenses_table())

        self.year_var = tk.StringVar(value=str(datetime.now().year))
        years = ["All"] + [str(year) for year in range(datetime.now().year - 5, datetime.now().year + 1)]
        year_dropdown = ttk.Combobox(filter_frame, textvariable=self.year_var,
                                    values=years, font=self.fonts["body"], width=6)
        year_dropdown.pack(side="left", padx=5, ipady=4)
        year_dropdown.bind("<<ComboboxSelected>>", lambda e: self.update_expenses_table())

        self.search_var = tk.StringVar()
        search_entry = tk.Entry(filter_frame, textvariable=self.search_var,
                               font=self.fonts["body"], bd=0,
                               bg="#3a3a4a" if self.current_theme == "dark" else "#e0e0e0",
                               fg=self.colors["text"], insertbackground=self.colors["text"],
                               relief="flat")
        search_entry.pack(side="left", padx=5, ipady=5, ipadx=50)
        search_entry.bind("<KeyRelease>", lambda e: self.update_expenses_table())

        self.create_button(filter_frame, "🔍 SEARCH", self.update_expenses_table,
                          self.colors["accent"], small=True).pack(side="left", padx=5, ipadx=8, ipady=4)

        table_frame = tk.Frame(self.view_expenses_frame, bg=self.colors["background"], padx=20, pady=15)
        table_frame.pack(fill="both", expand=True)

        self.update_treeview_style()
        self.tree = ttk.Treeview(table_frame, columns=("ID", "Date", "Category", "Amount", "Description"),
                                show="headings", style="Treeview")
        self.tree.pack(fill="both", expand=True)
        self.tree.heading("ID", text="ID")
        self.tree.heading("Date", text="DATE")
        self.tree.heading("Category", text="CATEGORY")
        self.tree.heading("Amount", text="AMOUNT")
        self.tree.heading("Description", text="DESCRIPTION")
        self.tree.column("ID", width=50, anchor="center")
        self.tree.column("Date", width=100, anchor="center")
        self.tree.column("Category", width=120, anchor="center")
        self.tree.column("Amount", width=100, anchor="center")
        self.tree.column("Description", width=200, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.context_menu = tk.Menu(self.tree, tearoff=0, bg=self.colors["card"], fg=self.colors["text"],
                                   activebackground=self.colors["accent"], activeforeground="white",
                                   font=self.fonts["body"])
        self.context_menu.add_command(label="✏️ EDIT", command=self.edit_expense)
        self.context_menu.add_command(label="🗑️ DELETE", command=self.delete_expense)
        self.tree.bind("<Button-3>", self.show_context_menu)

        button_frame = tk.Frame(self.view_expenses_frame, bg=self.colors["background"], padx=20, pady=15)
        button_frame.pack(fill="x")
        self.create_button(button_frame, "🔙 BACK",
                          lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", ipadx=8, ipady=4)

    def create_stats_frame(self):
        self.stats_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.stats_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="📊 STATISTICS", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        chart_frame = tk.Frame(self.stats_frame, bg=self.colors["card"], padx=20, pady=20)
        chart_frame.pack(padx=30, pady=20, fill="both", expand=True)

        self.update_chart_style()
        self.fig, (self.ax1, self.ax2) = plt.subplots(1, 2, figsize=(8, 4))
        self.fig.patch.set_facecolor(self.colors["card"])
        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        button_frame = tk.Frame(self.stats_frame, bg=self.colors["background"], padx=20, pady=15)
        button_frame.pack(fill="x")
        self.create_button(button_frame, "🔙 BACK",
                          lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", ipadx=8, ipady=4)

    def create_settings_frame(self):
        self.settings_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.settings_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="⚙️ SETTINGS", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        settings_container = tk.Frame(self.settings_frame, bg=self.colors["card"], padx=20, pady=20)
        settings_container.pack(pady=50, padx=30, fill="both")

        tk.Label(settings_container, text="THEME", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.theme_var = tk.StringVar(value=self.current_theme.capitalize())
        theme_dropdown = ttk.Combobox(settings_container, textvariable=self.theme_var,
                                     values=["Dark", "Light"], font=self.fonts["body"], state="readonly")
        theme_dropdown.pack(fill="x", pady=10)
        theme_dropdown.bind("<<ComboboxSelected>>", self.change_theme)

        tk.Label(settings_container, text="ACCOUNT", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        account_frame = tk.Frame(settings_container, bg=self.colors["card"])
        account_frame.pack(pady=10)
        tk.Label(account_frame, text=f"Current: {self.current_user}", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(side="left")
        self.create_button(account_frame, "🔄 Switch", self.switch_account,
                          self.colors["accent"], small=True).pack(side="left", padx=10, ipadx=8, ipady=4)

        button_frame = tk.Frame(settings_container, bg=self.colors["card"])
        button_frame.pack(pady=20)
        self.create_button(button_frame, "🔙 BACK",
                          lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(ipadx=8, ipady=4)

    def create_sip_tracker_frame(self):
        self.sip_tracker_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.sip_tracker_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="💹 ADD SIP", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        add_frame = tk.Frame(self.sip_tracker_frame, bg=self.colors["card"], padx=20, pady=20)
        add_frame.pack(padx=30, pady=20, fill="x")

        tk.Label(add_frame, text="AMOUNT (₹)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.sip_amount_entry = self.create_entry(add_frame)
        self.sip_amount_entry.pack(fill="x", pady=5)

        tk.Label(add_frame, text="CATEGORY", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.sip_category_var = tk.StringVar()
        self.sip_category_dropdown = ttk.Combobox(add_frame, textvariable=self.sip_category_var,
                                                 values=self.sip_categories, font=self.fonts["body"])
        self.sip_category_dropdown.pack(fill="x", pady=10)
        self.sip_category_dropdown.current(0)

        tk.Label(add_frame, text="FREQUENCY", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.sip_freq_var = tk.StringVar()
        self.sip_freq_dropdown = ttk.Combobox(add_frame, textvariable=self.sip_freq_var,
                                             values=["Monthly", "Quarterly", "Yearly"], font=self.fonts["body"])
        self.sip_freq_dropdown.pack(fill="x", pady=10)
        self.sip_freq_dropdown.current(0)

        tk.Label(add_frame, text="START DATE (YYYY-MM-DD)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.sip_date_entry = self.create_entry(add_frame)
        self.sip_date_entry.pack(fill="x", pady=5)
        self.sip_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))

        tk.Label(add_frame, text="NAME", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)
        self.sip_name_entry = self.create_entry(add_frame)
        self.sip_name_entry.pack(fill="x", pady=5)

        button_frame = tk.Frame(add_frame, bg=self.colors["card"])
        button_frame.pack(pady=20)
        self.create_button(button_frame, "💾 ADD", self.save_sip,
                          self.colors["success"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(button_frame, "🗑️ CLEAR", self.clear_sip_form,
                          self.colors["warning"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(button_frame, "🔙 BACK",
                          lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", padx=5, ipadx=8, ipady=4)

    def create_view_sips_frame(self):
        self.view_sips_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.view_sips_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="📜 SIP HISTORY", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        table_frame = tk.Frame(self.view_sips_frame, bg=self.colors["background"], padx=20, pady=15)
        table_frame.pack(fill="both", expand=True)

        self.update_treeview_style()
        self.sip_tree = ttk.Treeview(table_frame, columns=("ID", "Name", "Amount", "Category", "Frequency", "Start Date"),
                                    show="headings", style="Treeview")
        self.sip_tree.pack(fill="both", expand=True)
        self.sip_tree.heading("ID", text="ID")
        self.sip_tree.heading("Name", text="NAME")
        self.sip_tree.heading("Amount", text="AMOUNT")
        self.sip_tree.heading("Category", text="CATEGORY")
        self.sip_tree.heading("Frequency", text="FREQUENCY")
        self.sip_tree.heading("Start Date", text="START DATE")
        self.sip_tree.column("ID", width=50, anchor="center")
        self.sip_tree.column("Name", width=120, anchor="center")
        self.sip_tree.column("Amount", width=100, anchor="center")
        self.sip_tree.column("Category", width=100, anchor="center")
        self.sip_tree.column("Frequency", width=100, anchor="center")
        self.sip_tree.column("Start Date", width=100, anchor="center")

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.sip_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.sip_tree.configure(yscrollcommand=scrollbar.set)

        self.sip_context_menu = tk.Menu(self.sip_tree, tearoff=0, bg=self.colors["card"], fg=self.colors["text"],
                                       activebackground=self.colors["accent"], activeforeground="white",
                                       font=self.fonts["body"])
        self.sip_context_menu.add_command(label="🗑️ DELETE", command=self.delete_sip)
        self.sip_tree.bind("<Button-3>", self.show_sip_context_menu)

        button_frame = tk.Frame(self.view_sips_frame, bg=self.colors["background"], padx=20, pady=15)
        button_frame.pack(fill="x")
        self.create_button(button_frame, "🔙 BACK",
                          lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", ipadx=8, ipady=4)

    def create_budget_frame(self):
        self.budget_frame = tk.Frame(self.root, bg=self.colors["background"])
        header = tk.Frame(self.budget_frame, bg=self.colors["primary"], height=80)
        header.pack(fill="x")
        tk.Label(header, text="💸 BUDGET MANAGER", font=self.fonts["title"],
                 bg=self.colors["primary"], fg="white", pady=10).pack()

        canvas = tk.Canvas(self.budget_frame, bg=self.colors["background"])
        scrollbar = ttk.Scrollbar(self.budget_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg=self.colors["card"])

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        monthly_section = tk.Frame(scrollable_frame, bg=self.colors["card"])
        monthly_section.pack(fill="x", pady=10, padx=20)
        tk.Label(monthly_section, text="MONTHLY BUDGET (₹)", font=self.fonts["header"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        self.monthly_budget_entry = self.create_entry(monthly_section)
        self.monthly_budget_entry.pack(fill="x", pady=10, ipady=8)
        self.monthly_budget_entry.insert(0, str(self.user_data[self.current_user]['monthly_budget']))

        daily_section = tk.Frame(scrollable_frame, bg=self.colors["card"])
        daily_section.pack(fill="x", pady=10, padx=20)
        tk.Label(daily_section, text="DAILY BUDGET (₹)", font=self.fonts["header"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        self.daily_budget_entry = self.create_entry(daily_section)
        self.daily_budget_entry.pack(fill="x", pady=10, ipady=8)
        self.daily_budget_entry.insert(0, str(self.user_data[self.current_user]['daily_budget']))

        goals_section = tk.Frame(scrollable_frame, bg=self.colors["card"])
        goals_section.pack(fill="x", pady=10, padx=20)
        tk.Label(goals_section, text="MONTHLY GOALS BY CATEGORY", font=self.fonts["header"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=10)

        self.goal_entries = {}
        for category in self.categories:
            goal_frame = tk.Frame(goals_section, bg=self.colors["card"])
            goal_frame.pack(fill="x", pady=5)
            tk.Label(goal_frame, text=f"{category}:", font=self.fonts["body"],
                     bg=self.colors["card"], fg=self.colors["text"]).pack(side="left", padx=5)
            entry = tk.Entry(goal_frame, font=self.fonts["body"], bd=0,
                            bg="#3a3a4a" if self.current_theme == "dark" else "#e0e0e0",
                            fg=self.colors["text"], insertbackground=self.colors["text"],
                            relief="flat", width=20)
            entry.pack(side="left", fill="x", expand=True, padx=5, ipady=6)
            entry.insert(0, str(self.user_data[self.current_user]['monthly_goals'].get(category, 0.0)))
            self.goal_entries[category] = entry

        canvas.pack(side="left", fill="both", expand=True, padx=20, pady=20)
        scrollbar.pack(side="right", fill="y")

        button_frame = tk.Frame(self.budget_frame, bg=self.colors["background"])
        button_frame.pack(side="bottom", fill="x", pady=10, padx=20)
        self.create_button(button_frame, "💾 SAVE", self.save_budget,
                          self.colors["success"]).pack(side="left", padx=5, ipadx=15, ipady=6)
        self.create_button(button_frame, "🗑️ CLEAR", self.clear_budget_form,
                          self.colors["warning"]).pack(side="left", padx=5, ipadx=15, ipady=6)
        self.create_button(button_frame, "🔙 BACK", lambda: self.show_frame(self.main_frame),
                          self.colors["secondary"]).pack(side="right", padx=5, ipadx=15, ipady=6)

    def save_budget(self):
        try:
            monthly_budget = float(self.monthly_budget_entry.get().strip() or 0)
            daily_budget = float(self.daily_budget_entry.get().strip() or 0)
            if monthly_budget < 0 or daily_budget < 0:
                raise ValueError("Budgets cannot be negative")

            user = self.user_data[self.current_user]
            user['monthly_budget'] = monthly_budget
            user['daily_budget'] = daily_budget

            for category, entry in self.goal_entries.items():
                value = entry.get().strip()
                if value:
                    amount = float(value)
                    if amount < 0:
                        raise ValueError(f"Goal for {category} cannot be negative")
                    user['monthly_goals'][category] = amount
                else:
                    user['monthly_goals'].pop(category, None)

            self.save_user_data()
            self.show_custom_message("SUCCESS", "Budget settings updated successfully! 🎉", "success")
            self.update_dashboard()
            self.check_budget_alerts()
        except ValueError as e:
            self.show_custom_message("ERROR", f"🚫 Invalid input: {str(e)}", "error")

    def clear_budget_form(self):
        self.monthly_budget_entry.delete(0, tk.END)
        self.monthly_budget_entry.insert(0, str(self.user_data[self.current_user]['monthly_budget']))
        self.daily_budget_entry.delete(0, tk.END)
        self.daily_budget_entry.insert(0, str(self.user_data[self.current_user]['daily_budget']))
        for category, entry in self.goal_entries.items():
            entry.delete(0, tk.END)
            entry.insert(0, str(self.user_data[self.current_user]['monthly_goals'].get(category, 0.0)))

    def check_budget_alerts(self):
        user = self.user_data[self.current_user]
        current_month = datetime.now().strftime("%Y-%m")
        current_day = datetime.now().strftime("%Y-%m-%d")
        
        monthly_total = sum(exp['amount'] for exp in user['expenses'] if exp['date'].startswith(current_month))
        if user['monthly_budget'] > 0:
            percentage = (monthly_total / user['monthly_budget']) * 100
            if percentage >= 90 and percentage < 100:
                self.show_budget_alert("Monthly Budget Warning",
                                      f"🚨 You've spent {percentage:.1f}% of your monthly budget!\n"
                                      f"Spent: ₹{monthly_total:,.2f}\nBudget: ₹{user['monthly_budget']:,.2f}",
                                      self.colors["warning"])
            elif percentage >= 100:
                self.show_budget_alert("Monthly Budget Exceeded",
                                      f"❌ You've exceeded your monthly budget!\n"
                                      f"Spent: ₹{monthly_total:,.2f}\nBudget: ₹{user['monthly_budget']:,.2f}",
                                      self.colors["danger"])

        daily_total = sum(exp['amount'] for exp in user['expenses'] if exp['date'] == current_day)
        if user['daily_budget'] > 0 and daily_total > user['daily_budget']:
            self.show_budget_alert("Daily Budget Exceeded",
                                  f"⚠️ Today's spending exceeds your daily budget!\n"
                                  f"Spent: ₹{daily_total:,.2f}\nBudget: ₹{user['daily_budget']:,.2f}",
                                  self.colors["warning"])

        monthly_totals = {}
        for exp in user['expenses']:
            if exp['date'].startswith(current_month):
                monthly_totals[exp['category']] = monthly_totals.get(exp['category'], 0) + exp['amount']
        for category, goal in user['monthly_goals'].items():
            spent = monthly_totals.get(category, 0)
            if spent > goal and goal > 0:
                self.show_budget_alert("Category Budget Alert",
                                      f"🚨 {category} spending exceeded!\n"
                                      f"Spent: ₹{spent:,.2f}\nGoal: ₹{goal:,.2f}",
                                      self.colors["warning"])

    def show_budget_alert(self, title, message, color):
        alert = tk.Toplevel(self.root)
        alert.title(title)
        alert.geometry("400x200")
        alert.resizable(False, False)
        alert.configure(bg=self.colors["background"])
        alert.grab_set()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 100
        alert.geometry(f"400x200+{x}+{y}")

        tk.Label(alert, text="💰 BUDGET ALERT", font=self.fonts["header"],
                 bg=self.colors["background"], fg=color).pack(pady=(15, 10))
        tk.Label(alert, text=message, font=self.fonts["body"],
                 bg=self.colors["background"], fg=self.colors["text"], wraplength=350).pack(pady=10)
        self.create_button(alert, "OK", alert.destroy, color).pack(pady=10, ipadx=8, ipady=4)

    def darken_color(self, color, percent):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        darkened = tuple(max(0, int(c * (100 - percent) / 100)) for c in rgb)
        return f"#{darkened[0]:02x}{darkened[1]:02x}{darkened[2]:02x}"

    def lighten_color(self, color, percent):
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        lightened = tuple(min(255, int(c + (255 - c) * percent / 100)) for c in rgb)
        return f"#{lightened[0]:02x}{lightened[1]:02x}{lightened[2]:02x}"

    def save_expense(self):
        try:
            amount = float(self.amount_entry.get().strip())
            if amount <= 0:
                raise ValueError("Amount must be positive")
            date = self.date_entry.get().strip()
            datetime.strptime(date, "%Y-%m-%d")
            expense = {
                'id': self.next_expense_id,
                'date': date,
                'category': self.category_var.get(),
                'amount': amount,
                'description': self.desc_entry.get()
            }
            self.next_expense_id += 1
            self.user_data[self.current_user]['expenses'].append(expense)
            self.save_user_data()
            self.clear_expense_form()
            self.show_custom_message("SUCCESS", "Expense created successfully! 💾", "success")
            self.update_dashboard()
            self.update_expenses_table()
            self.update_charts()
            self.check_budget_alerts()
        except ValueError as e:
            self.show_custom_message("ERROR", f"🚫 {str(e)}", "error")

    def save_sip(self):
        try:
            amount = float(self.sip_amount_entry.get().strip())
            if amount <= 0:
                raise ValueError("Amount must be positive")
            date = self.sip_date_entry.get().strip()
            datetime.strptime(date, "%Y-%m-%d")
            name = self.sip_name_entry.get().strip()
            if not name:
                raise ValueError("Name is required")
            sip = {
                'id': self.next_sip_id,
                'name': name,
                'amount': amount,
                'category': self.sip_category_var.get(),
                'frequency': self.sip_freq_var.get(),
                'start_date': date
            }
            self.next_sip_id += 1
            self.user_data[self.current_user]['sips'].append(sip)
            self.save_user_data()
            self.update_sip_table()
            self.update_dashboard()
            self.update_charts()
            self.clear_sip_form()
            self.show_custom_message("SUCCESS", "SIP created successfully! 💹", "success")
        except ValueError as e:
            self.show_custom_message("ERROR", f"🚫 {str(e)}", "error")

    def show_custom_message(self, title, message, msg_type):
        colors = {"success": self.colors["success"], "error": self.colors["danger"],
                  "info": self.colors["info"], "warning": self.colors["warning"]}
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.geometry("400x200")
        msg_window.resizable(False, False)
        msg_window.configure(bg=self.colors["background"])
        msg_window.grab_set()
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 100
        msg_window.geometry(f"400x200+{x}+{y}")

        icon_label = tk.Label(msg_window,
                             text="✓" if msg_type == "success" else "⚠️" if msg_type == "warning" else "✕",
                             font=("Segoe UI", 20), bg=self.colors["background"], fg=colors[msg_type])
        icon_label.pack(pady=(15, 10))
        tk.Label(msg_window, text=title, font=self.fonts["header"],
                 bg=self.colors["background"], fg=colors[msg_type]).pack()
        tk.Label(msg_window, text=message, font=self.fonts["body"],
                 bg=self.colors["background"], fg=self.colors["text"], wraplength=350).pack(pady=10)
        self.create_button(msg_window, "OK", msg_window.destroy, colors[msg_type]).pack(pady=10, ipadx=8, ipady=4)

    def clear_expense_form(self):
        self.amount_entry.delete(0, tk.END)
        self.category_dropdown.current(0)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.desc_entry.delete(0, tk.END)

    def clear_sip_form(self):
        self.sip_amount_entry.delete(0, tk.END)
        self.sip_category_dropdown.current(0)
        self.sip_freq_dropdown.current(0)
        self.sip_date_entry.delete(0, tk.END)
        self.sip_date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        self.sip_name_entry.delete(0, tk.END)

    def update_dashboard(self):
        user = self.user_data[self.current_user]
        expenses = user['expenses']
        sips = user['sips']
        
        total = sum(exp['amount'] for exp in expenses)
        self.total_label.config(text=f"₹{total:,.2f}")

        if expenses:
            recent_exp = max(expenses, key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"))
            self.recent_label.config(text=f"{recent_exp['category']}: ₹{recent_exp['amount']:.2f}\n{recent_exp['date']}")
        else:
            self.recent_label.config(text="No recent expenses", fg=self.colors["accent"])

        if expenses:
            cat_counts = {}
            for exp in expenses:
                cat_counts[exp['category']] = cat_counts.get(exp['category'], 0) + exp['amount']
            if cat_counts:
                top_cat = max(cat_counts.items(), key=lambda x: x[1])[0]
                self.cat_label.config(text=top_cat, fg=self.colors["highlight"])
        else:
            self.cat_label.config(text="No data", fg=self.colors["highlight"])

        sip_total = sum(sip['amount'] for sip in sips)
        self.sip_total_label.config(text=f"₹{sip_total:,.2f}", fg=self.colors["info"])

        current_month = datetime.now().strftime("%Y-%m")
        current_day = datetime.now().strftime("%Y-%m-%d")
        monthly_spent = sum(exp['amount'] for exp in expenses if exp['date'].startswith(current_month))
        daily_spent = sum(exp['amount'] for exp in expenses if exp['date'] == current_day)
        self.budget_label.config(text=f"₹{monthly_spent:,.2f} / ₹{user['monthly_budget']:,.2f}", fg=self.colors["info"])
        self.daily_label.config(text=f"₹{daily_spent:,.2f} / ₹{user['daily_budget']:,.2f}", fg=self.colors["warning"])

    def update_expenses_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        user = self.user_data[self.current_user]
        month = self.month_var.get()
        year = self.year_var.get()
        search_term = self.search_var.get().lower()
        filtered = user['expenses'][:]
        if month != "All":
            filtered = [exp for exp in filtered if datetime.strptime(exp['date'], "%Y-%m-%d").strftime("%B") == month]
        if year != "All":
            filtered = [exp for exp in filtered if str(datetime.strptime(exp['date'], "%Y-%m-%d").year) == year]
        if search_term:
            filtered = [exp for exp in filtered if (search_term in exp['description'].lower() or search_term in exp['category'].lower())]
        filtered.sort(key=lambda x: datetime.strptime(x['date'], "%Y-%m-%d"), reverse=True)
        for exp in filtered:
            self.tree.insert("", "end", values=(
                exp['id'],
                exp['date'],
                exp['category'],
                f"₹{exp['amount']:.2f}",
                exp['description']
            ))

    def update_sip_table(self):
        for item in self.sip_tree.get_children():
            self.sip_tree.delete(item)
        user = self.user_data[self.current_user]
        for sip in sorted(user['sips'], key=lambda x: x['id'], reverse=True):
            self.sip_tree.insert("", "end", values=(
                sip['id'],
                sip['name'],
                f"₹{sip['amount']:,.2f}",
                sip['category'],
                sip['frequency'],
                sip['start_date']
            ))

    def update_charts(self):
        self.ax1.clear()
        self.ax2.clear()
        user = self.user_data[self.current_user]
        if not user['expenses'] and not user['sips']:
            self.ax1.text(0.5, 0.5, "No data", ha="center", va="center",
                         fontsize=10, color=self.colors["text"])
            self.ax2.text(0.5, 0.5, "No data", ha="center", va="center",
                         fontsize=10, color=self.colors["text"])
        else:
            if user['expenses']:
                cat_totals = {}
                for exp in user['expenses']:
                    cat = exp['category']
                    cat_totals[cat] = cat_totals.get(cat, 0) + exp['amount']
                categories = list(cat_totals.keys())
                amounts = list(cat_totals.values())
                colors = plt.cm.viridis([i/float(len(categories)) for i in range(len(categories))])
                self.ax1.pie(amounts, labels=categories, autopct="%1.1f%%", startangle=90,
                            colors=colors, textprops={'color': self.colors["text"], 'fontsize': 8})
                self.ax1.set_title("Expenses by Category", color=self.colors["text"], fontsize=10)

            if user['sips']:
                sip_totals = {}
                for sip in user['sips']:
                    cat = sip['category']
                    sip_totals[cat] = sip_totals.get(cat, 0) + sip['amount']
                categories = list(sip_totals.keys())
                amounts = list(sip_totals.values())
                self.ax2.bar(categories, amounts, color=self.colors["accent"])
                self.ax2.set_title("SIP by Category", color=self.colors["text"], fontsize=10)
                self.ax2.tick_params(axis="x", rotation=45, colors=self.colors["text"])
                self.ax2.tick_params(axis="y", colors=self.colors["text"])

        self.fig.tight_layout()
        self.canvas.draw()

    def show_context_menu(self, event):
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def show_sip_context_menu(self, event):
        item = self.sip_tree.identify_row(event.y)
        if item:
            self.sip_tree.selection_set(item)
            self.sip_context_menu.post(event.x_root, event.y_root)

    def edit_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item)
        expense_id = item['values'][0]
        user = self.user_data[self.current_user]
        expense = next((exp for exp in user['expenses'] if exp['id'] == expense_id), None)
        if not expense:
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("✏️ EDIT EXPENSE")
        edit_window.geometry("400x300")
        edit_window.resizable(False, False)
        edit_window.configure(bg=self.colors["background"])
        x = (self.root.winfo_screenwidth() // 2) - 200
        y = (self.root.winfo_screenheight() // 2) - 150
        edit_window.geometry(f"400x300+{x}+{y}")

        form_frame = tk.Frame(edit_window, bg=self.colors["card"], padx=20, pady=20)
        form_frame.pack(fill="both", expand=True, padx=15, pady=15)

        tk.Label(form_frame, text="AMOUNT (₹)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        amount_entry = self.create_entry(form_frame)
        amount_entry.pack(fill="x", pady=5)
        amount_entry.insert(0, str(expense['amount']))

        tk.Label(form_frame, text="CATEGORY", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        category_var = tk.StringVar(value=expense['category'])
        category_dropdown = ttk.Combobox(form_frame, textvariable=category_var,
                                        values=self.categories, font=self.fonts["body"])
        category_dropdown.pack(fill="x", pady=5)
        category_dropdown.current(self.categories.index(expense['category']))

        tk.Label(form_frame, text="DATE (YYYY-MM-DD)", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        date_entry = self.create_entry(form_frame)
        date_entry.pack(fill="x", pady=5)
        date_entry.insert(0, expense['date'])

        tk.Label(form_frame, text="DESCRIPTION", font=self.fonts["body"],
                 bg=self.colors["card"], fg=self.colors["text"]).pack(anchor="w", pady=5)
        desc_entry = self.create_entry(form_frame)
        desc_entry.pack(fill="x", pady=5)
        desc_entry.insert(0, expense['description'] if expense['description'] else "")

        button_frame = tk.Frame(form_frame, bg=self.colors["card"])
        button_frame.pack(pady=15)
        def save_changes():
            try:
                amount = float(amount_entry.get().strip())
                if amount <= 0:
                    raise ValueError("Amount must be positive")
                new_date = date_entry.get().strip()
                datetime.strptime(new_date, "%Y-%m-%d")
                expense['amount'] = amount
                expense['category'] = category_var.get()
                expense['date'] = new_date
                expense['description'] = desc_entry.get()
                self.save_user_data()
                self.update_expenses_table()
                self.update_dashboard()
                self.update_charts()
                edit_window.destroy()
                self.show_custom_message("SUCCESS", "Expense updated successfully! ✏️", "success")
                self.check_budget_alerts()
            except ValueError as e:
                self.show_custom_message("ERROR", f"🚫 Invalid input: {e}", "error")

        self.create_button(button_frame, "💾 SAVE", save_changes,
                          self.colors["success"]).pack(side="left", padx=5, ipadx=8, ipady=4)
        self.create_button(button_frame, "❌ CANCEL", edit_window.destroy,
                          self.colors["danger"]).pack(side="right", padx=5, ipadx=8, ipady=4)

    def delete_expense(self):
        selected_item = self.tree.selection()
        if not selected_item:
            return
        item = self.tree.item(selected_item)
        expense_id = item['values'][0]
        user = self.user_data[self.current_user]
        user['expenses'] = [exp for exp in user['expenses'] if exp['id'] != expense_id]
        self.save_user_data()
        self.update_expenses_table()
        self.update_dashboard()
        self.update_charts()
        self.show_custom_message("SUCCESS", "Expense deleted successfully! 🗑️", "success")
        self.check_budget_alerts()

    def delete_sip(self):
        selected_item = self.sip_tree.selection()
        if not selected_item:
            return
        item = self.sip_tree.item(selected_item)
        sip_id = item['values'][0]
        user = self.user_data[self.current_user]
        user['sips'] = [sip for sip in user['sips'] if sip['id'] != sip_id]
        self.save_user_data()
        self.update_sip_table()
        self.update_dashboard()
        self.update_charts()
        self.show_custom_message("SUCCESS", "SIP deleted successfully! 🗑️", "success")

    def export_data(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Data As",
            initialfile=f"trackwise_export_{self.current_user}.csv"
        )
        if file_path:
            try:
                user = self.user_data[self.current_user]
                with open(file_path, mode='w', newline='') as file:
                    writer = csv.writer(file)
                    writer.writerow(["Type", "ID", "Date", "Category", "Amount", "Description", "Frequency"])
                    for exp in user['expenses']:
                        writer.writerow(["Expense", exp['id'], exp['date'], exp['category'],
                                        exp['amount'], exp['description'], ""])
                    for sip in user['sips']:
                        writer.writerow(["SIP", sip['id'], sip['start_date'], sip['category'],
                                        sip['amount'], sip['name'], sip['frequency']])
                self.show_custom_message("SUCCESS", "Data exported successfully! 📤", "success")
            except Exception as e:
                self.show_custom_message("ERROR", f"Failed to export: {str(e)}", "error")

    def import_data(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Select Data File"
        )
        if file_path:
            try:
                with open(file_path, mode='r', newline='') as file:
                    reader = csv.DictReader(file)
                    new_expenses = []
                    new_sips = []
                    for row in reader:
                        if row['Type'] == "Expense":
                            new_exp = {
                                'id': int(row['ID']),
                                'date': row['Date'],
                                'category': row['Category'],
                                'amount': float(row['Amount']),
                                'description': row['Description']
                            }
                            new_expenses.append(new_exp)
                        elif row['Type'] == "SIP":
                            new_sip = {
                                'id': int(row['ID']),
                                'name': row['Description'],
                                'amount': float(row['Amount']),
                                'category': row['Category'],
                                'frequency': row['Frequency'],
                                'start_date': row['Date']
                            }
                            new_sips.append(new_sip)

                user = self.user_data[self.current_user]
                user['expenses'] = new_expenses
                user['sips'] = new_sips
                self.next_expense_id = max([exp['id'] for exp in user['expenses']] + [0]) + 1
                self.next_sip_id = max([sip['id'] for sip in user['sips']] + [0]) + 1
                self.save_user_data()
                self.update_expenses_table()
                self.update_sip_table()
                self.update_dashboard()
                self.update_charts()
                self.show_custom_message("SUCCESS", "Data imported successfully! 📥", "success")
                self.check_budget_alerts()
            except Exception as e:
                self.show_custom_message("ERROR", f"Failed to import: {str(e)}", "error")

    def change_theme(self, event=None):
        new_theme = self.theme_var.get().lower()
        if new_theme == self.current_theme:
            return

        self.current_theme = new_theme
        self.colors = self.themes[new_theme]
        self.root.configure(bg=self.colors["background"])

        frames = [
            (self.login_frame, self.create_login_frame),
            (self.nav_frame, self.create_nav_bar),
            (self.main_frame, self.create_main_frame),
            (self.add_expense_frame, self.create_add_expense_frame),
            (self.view_expenses_frame, self.create_view_expenses_frame),
            (self.stats_frame, self.create_stats_frame),
            (self.settings_frame, self.create_settings_frame),
            (self.sip_tracker_frame, self.create_sip_tracker_frame),
            (self.view_sips_frame, self.create_view_sips_frame),  # Added
            (self.budget_frame, self.create_budget_frame)
        ]

        current_frame = None
        for frame, _ in frames:
            if frame.winfo_ismapped():
                current_frame = frame
            frame.pack_forget()
            frame.destroy()

        for _, create_func in frames:
            create_func()

        self.update_treeview_style()
        self.update_chart_style()

        if self.current_user:
            self.nav_frame.pack(fill="x", side="top")
            if current_frame == self.login_frame:
                self.show_frame(self.main_frame)
            else:
                self.show_frame(next(f for f, _ in frames if f.winfo_ismapped() == current_frame) or self.main_frame)
        else:
            self.login_frame.pack(fill="both", expand=True)

        self.update_dashboard()
        self.update_expenses_table()
        self.update_sip_table()
        self.update_charts()

    def switch_account(self):
        self.logout()
        self.show_custom_message("INFO", "Login with a different account 🔄", "info")

    def update_treeview_style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background=self.colors["card"],
                       foreground=self.colors["text"],
                       rowheight=25,
                       fieldbackground=self.colors["card"],
                       font=self.fonts["body"])
        style.configure("Treeview.Heading",
                       font=self.fonts["subheader"],
                       background=self.colors["primary"],
                       foreground="white")
        style.map("Treeview",
                 background=[("selected", self.colors["accent"])],
                 foreground=[("selected", "white")])

    def update_chart_style(self):
        plt.style.use('dark_background' if self.current_theme == "dark" else 'default')
        plt.rcParams['axes.facecolor'] = self.colors["card"]
        plt.rcParams['figure.facecolor'] = self.colors["card"]
        plt.rcParams['axes.titlecolor'] = self.colors["text"]
        plt.rcParams['axes.labelcolor'] = self.colors["text"]
        plt.rcParams['xtick.color'] = self.colors["text"]
        plt.rcParams['ytick.color'] = self.colors["text"]

    def show_frame(self, frame):
        frames = [self.main_frame, self.add_expense_frame, self.view_expenses_frame,
                  self.stats_frame, self.settings_frame, self.sip_tracker_frame,
                  self.view_sips_frame, self.budget_frame]  # Updated list
        for f in frames:
            f.pack_forget()
        frame.pack(fill="both", expand=True)
        if frame == self.view_expenses_frame:
            self.update_expenses_table()
        elif frame == self.stats_frame:
            self.update_charts()
        elif frame == self.view_sips_frame:  # Added
            self.update_sip_table()
        elif frame == self.main_frame:
            self.update_dashboard()

if __name__ == "__main__":
    root = tk.Tk()
    app = ModernExpenseTracker(root)
    root.mainloop()