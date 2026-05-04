"""
ATM Machine Simulation Project (UPGRADED VERSION)
Features:
- Modern Tkinter UI (ttk)
- User Registration + Login system
- SQLite persistent storage
- Deposit / Withdraw / Transfer
- Transaction history viewer
- CSV upload (auto-import + store in DB)
- Financial summary dashboard

Run:
python atm_app.py

Dependencies:
- pandas
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import datetime

# ---------------- DATABASE ----------------
conn = sqlite3.connect("atm.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    pin TEXT,
    balance REAL DEFAULT 0
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    type TEXT,
    amount REAL,
    target TEXT,
    date TEXT
)
""")
conn.commit()

# ---------------- APP ----------------
class ATMApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern ATM System")
        self.root.geometry("600x500")
        self.root.configure(bg="#1e1e2f")
        self.username = None

        self.style = ttk.Style()
        self.style.theme_use("clam")
        self.style.configure("TButton", font=("Arial", 11), padding=6)
        self.style.configure("TLabel", font=("Arial", 11))

        self.login_screen()

    # ---------------- UI CLEAR ----------------
    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ---------------- LOGIN SCREEN ----------------
    def login_screen(self):
        self.clear()

        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(expand=True)

        tk.Label(frame, text="ATM LOGIN", font=("Arial", 20, "bold"), fg="white", bg="#1e1e2f").pack(pady=10)

        tk.Label(frame, text="Username", fg="white", bg="#1e1e2f").pack()
        self.user_entry = tk.Entry(frame)
        self.user_entry.pack()

        tk.Label(frame, text="PIN", fg="white", bg="#1e1e2f").pack()
        self.pin_entry = tk.Entry(frame, show="*")
        self.pin_entry.pack()

        ttk.Button(frame, text="Login", command=self.login).pack(pady=5)
        ttk.Button(frame, text="Register", command=self.register_screen).pack()

    # ---------------- REGISTER ----------------
    def register_screen(self):
        self.clear()

        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(expand=True)

        tk.Label(frame, text="REGISTER ACCOUNT", font=("Arial", 18, "bold"), fg="white", bg="#1e1e2f").pack(pady=10)

        tk.Label(frame, text="Username", fg="white", bg="#1e1e2f").pack()
        user = tk.Entry(frame)
        user.pack()

        tk.Label(frame, text="PIN", fg="white", bg="#1e1e2f").pack()
        pin = tk.Entry(frame, show="*")
        pin.pack()

        def create():
            try:
                cursor.execute("INSERT INTO users (username, pin, balance) VALUES (?, ?, ?)",
                               (user.get(), pin.get(), 0))
                conn.commit()
                messagebox.showinfo("Success", "Account created")
                self.login_screen()
            except:
                messagebox.showerror("Error", "Username already exists")

        ttk.Button(frame, text="Create", command=create).pack(pady=10)
        ttk.Button(frame, text="Back", command=self.login_screen).pack()

    # ---------------- LOGIN ----------------
    def login(self):
        user = self.user_entry.get()
        pin = self.pin_entry.get()

        cursor.execute("SELECT * FROM users WHERE username=? AND pin=?", (user, pin))
        if cursor.fetchone():
            self.username = user
            self.main_menu()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    # ---------------- MAIN MENU ----------------
    def main_menu(self):
        self.clear()

        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(expand=True)

        tk.Label(frame, text=f"Welcome {self.username}", font=("Arial", 16, "bold"), fg="white", bg="#1e1e2f").pack(pady=10)

        ttk.Button(frame, text="Balance", command=self.balance).pack(pady=5)
        ttk.Button(frame, text="Deposit", command=self.deposit).pack(pady=5)
        ttk.Button(frame, text="Withdraw", command=self.withdraw).pack(pady=5)
        ttk.Button(frame, text="Transfer", command=self.transfer).pack(pady=5)
        ttk.Button(frame, text="History", command=self.history).pack(pady=5)
        ttk.Button(frame, text="Upload CSV", command=self.upload_csv).pack(pady=5)
        ttk.Button(frame, text="Summary", command=self.summary).pack(pady=5)
        ttk.Button(frame, text="Logout", command=self.login_screen).pack(pady=10)

    # ---------------- BALANCE ----------------
    def get_balance(self):
        cursor.execute("SELECT balance FROM users WHERE username=?", (self.username,))
        return cursor.fetchone()[0]

    def balance(self):
        messagebox.showinfo("Balance", f"Balance: ${self.get_balance()}")

    # ---------------- UPDATE ----------------
    def update_balance(self, amount):
        cursor.execute("UPDATE users SET balance=? WHERE username=?", (amount, self.username))
        conn.commit()

    # ---------------- TRANSACTION ----------------
    def add_transaction(self, t, a, target=None):
        cursor.execute("INSERT INTO transactions VALUES (NULL,?,?,?,?,?)",
                       (self.username, t, a, target, datetime.now().strftime("%Y-%m-%d %H:%M")))
        conn.commit()

    # ---------------- DEPOSIT ----------------
    def deposit(self):
        self.simple_input("Deposit", self.do_deposit)

    def do_deposit(self, amt):
        bal = self.get_balance() + amt
        self.update_balance(bal)
        self.add_transaction("DEPOSIT", amt)
        messagebox.showinfo("Success", "Deposited")

    # ---------------- WITHDRAW ----------------
    def withdraw(self):
        self.simple_input("Withdraw", self.do_withdraw)

    def do_withdraw(self, amt):
        bal = self.get_balance()
        if amt > bal:
            messagebox.showerror("Error", "Insufficient funds")
            return
        self.update_balance(bal - amt)
        self.add_transaction("WITHDRAW", amt)
        messagebox.showinfo("Success", "Withdrawn")

    # ---------------- TRANSFER ----------------
    def transfer(self):
        win = tk.Toplevel(self.root)
        win.title("Transfer")

        tk.Label(win, text="To User").pack()
        user = tk.Entry(win)
        user.pack()

        tk.Label(win, text="Amount").pack()
        amt = tk.Entry(win)
        amt.pack()

        def send():
            target = user.get()
            amount = float(amt.get())

            cursor.execute("SELECT balance FROM users WHERE username=?", (target,))
            r = cursor.fetchone()
            if not r:
                messagebox.showerror("Error", "User not found")
                return

            if amount > self.get_balance():
                messagebox.showerror("Error", "Insufficient funds")
                return

            self.update_balance(self.get_balance() - amount)
            cursor.execute("UPDATE users SET balance = balance + ? WHERE username=?", (amount, target))
            conn.commit()

            self.add_transaction("TRANSFER_OUT", amount, target)
            messagebox.showinfo("Success", "Transferred")
            win.destroy()

        ttk.Button(win, text="Send", command=send).pack()

    # ---------------- HISTORY ----------------
    def history(self):
        win = tk.Toplevel(self.root)
        win.title("History")

        cursor.execute("SELECT type, amount, target, date FROM transactions WHERE username=?", (self.username,))
        data = cursor.fetchall()

        text = tk.Text(win)
        text.pack(fill="both", expand=True)

        for d in data:
            text.insert(tk.END, f"{d}\n")

    # ---------------- CSV UPLOAD ----------------
    def upload_csv(self):
        file = filedialog.askopenfilename()
        if not file:
            return

        df = pd.read_csv(file)

        for _, row in df.iterrows():
            self.add_transaction(row['type'], float(row['amount']), row.get('target', None))

        messagebox.showinfo("Success", "CSV Imported & Stored")

    # ---------------- SUMMARY ----------------
    def summary(self):
        cursor.execute("SELECT type, amount FROM transactions WHERE username=?", (self.username,))
        rows = cursor.fetchall()

        income = sum(r[1] for r in rows if "DEPOSIT" in r[0])
        expense = sum(r[1] for r in rows if "WITHDRAW" in r[0])

        messagebox.showinfo("Summary", f"Income: {income}\nExpense: {expense}\nNet: {income-expense}")

    # ---------------- INPUT ----------------
    def simple_input(self, title, callback):
        win = tk.Toplevel(self.root)
        win.title(title)

        tk.Label(win, text="Amount").pack()
        e = tk.Entry(win)
        e.pack()

        def ok():
            try:
                callback(float(e.get()))
                win.destroy()
            except:
                messagebox.showerror("Error", "Invalid input")

        ttk.Button(win, text="OK", command=ok).pack()

# ---------------- RUN ----------------
root = tk.Tk()
app = ATMApp(root)
root.mainloop()
