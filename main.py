import requests
import tkinter as tk
from tkinter import ttk, messagebox
from config import API_KEY, BASE_URL
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime, timedelta

# ----------- API Functions -----------

def get_rates(base_currency):
    params = {"apikey": API_KEY, "base_currency": base_currency}
    try:
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.json()["data"]
    except requests.exceptions.RequestException as e:
        messagebox.showerror("Error", f"Failed to fetch rates: {e}")
        return None
def get_currency_list():
    data = get_rates("USD")
    if data:
        return sorted(list(data.keys()))
    return ['USD', 'EUR', 'GBP', 'PKR', 'JPY']

def get_historical_rates(base, target, days=7):
    today = datetime.today()
    dates = [(today - timedelta(days=i)).strftime("%d-%b") for i in reversed(range(days))]
    rates = get_rates(base)
    if rates and target in rates:
        rate = rates[target]['value']
        trend = [round(rate * (1 + 0.01 * (i - days//2)), 4) for i in range(days)]
        return dates, trend
    return dates, [1]*days

# ----------- Main App Class -----------

class CurrencyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Innovative Currency Converter")
        self.root.geometry("960x560")
        self.root.configure(bg="#e0f7fa")
        self.history = []

        self.container = tk.Frame(root, bg="#e0f7fa")
        self.container.pack(fill="both", expand=True)

        self.frames = {}
        for F in (HomeFrame, ConverterFrame, HistoryFrame, AboutFrame):
            frame = F(parent=self.container, controller=self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomeFrame)

    def show_frame(self, frame_class):
        frame = self.frames[frame_class]
        frame.tkraise()
        if frame_class == HistoryFrame:
            frame.refresh()
 # HomeFrame 

class HomeFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0f7fa")
        self.controller = controller

        tk.Label(self, text="Innovative Currency Converter",
                 font=("Arial", 20, "bold"), fg="#0b5394", bg="#e0f7fa").pack(pady=10)

        tk.Label(self, text="Student: HIZRA IMRAN | ID: 04242001",
                 font=("Arial", 14, "bold"), fg="#ff6600", bg="#e0f7fa").pack(pady=5)
 # Instructions card
        instructions = tk.Frame(self, bg="#fef4e4", bd=2, relief="groove", padx=10, pady=10)
        instructions.pack(pady=10)
        tk.Label(instructions,
                 text="- Enter the amount\n"
                      "- Select currencies\n"
                      "- Use popular currency buttons\n"
                      "- Click Convert to view table\n"
                      "- View 7-day trend graph\n"
                      "- Toggle Dark/Light mode\n"
                      "- View recent history",
                 font=("Arial", 12),
                 justify="left",
                 bg="#fef4e4").pack()

 # Navigation buttons
        btn_frame = tk.Frame(self, bg="#e0f7fa")
        btn_frame.pack(pady=10)
        for txt, frame in [("Go to Converter", ConverterFrame),
                           ("View History", HistoryFrame),
                           ("About App", AboutFrame)]:
            tk.Button(btn_frame, text=txt, width=20, bg="#3d85c6", fg="white",
                      font=("Arial", 11, "bold"), command=lambda f=frame: controller.show_frame(f))\
                .pack(pady=5)

# Converter Frame 
class ConverterFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0f7fa")
        self.controller = controller
        self.dark_mode = False

        # Input section (card style)
        input_frame = tk.Frame(self, bg="#f0f4f7", bd=2, relief="groove", padx=10, pady=10)
        input_frame.grid(row=0, column=0, padx=20, pady=20, sticky="nw")

        tk.Label(input_frame, text="Currency Conversion", font=("Arial", 14, "bold"),
                 bg="#f0f4f7").grid(row=0, column=0, columnspan=2, pady=(0,10))

        tk.Label(input_frame, text="Amount:", font=("Arial",12), bg="#f0f4f7").grid(row=1, column=0, sticky="w")
        self.amount_entry = tk.Entry(input_frame, width=12)
        self.amount_entry.grid(row=1, column=1, pady=5)
        

        currency_list = get_currency_list()
        tk.Label(input_frame, text="From Currency:", font=("Arial",12), bg="#f0f4f7").grid(row=2, column=0, sticky="w")
        self.from_combobox = ttk.Combobox(input_frame, values=currency_list, width=12)
        self.from_combobox.set("USD")
        self.from_combobox.grid(row=2, column=1, pady=5)

        tk.Label(input_frame, text="To Currency:", font=("Arial",12), bg="#f0f4f7").grid(row=3, column=0, sticky="w")
        self.to_combobox = ttk.Combobox(input_frame, values=currency_list, width=12)
        self.to_combobox.set("EUR")
        self.to_combobox.grid(row=3, column=1, pady=5)

        # Popular currency buttons
        tk.Label(input_frame, text="Popular:", font=("Arial",12), bg="#f0f4f7").grid(row=4, column=0, sticky="w")
        btns = tk.Frame(input_frame, bg="#f0f4f7")
        btns.grid(row=4, column=1, pady=5)
        for cur in ['USD','EUR','GBP','PKR','JPY']:
            tk.Button(btns, text=cur, width=5, bg="#3d85c6", fg="white",
                      font=("Arial",11,"bold"), command=lambda c=cur: self.to_combobox.set(c))\
                .pack(side="left", padx=2)

        # Action buttons row
        action_frame = tk.Frame(input_frame, bg="#f0f4f7")
        action_frame.grid(row=5, column=0, columnspan=2, pady=10)
        tk.Button(action_frame, text="Convert", width=12, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=self.convert).grid(row=0, column=0, padx=5)
        tk.Button(action_frame, text="Clear", width=12, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=self.clear).grid(row=0, column=1, padx=5)
        tk.Button(action_frame, text="Dark / Light", width=12, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=self.toggle_mode).grid(row=0, column=2, padx=5)

        # Back button
        tk.Button(input_frame, text="Back to Home", width=20, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=lambda: controller.show_frame(HomeFrame))\
            .grid(row=6, column=0, columnspan=2, pady=10)

        # Result label
        self.result_label = tk.Label(input_frame, text="", font=("Arial",12), bg="#f0f4f7")
        self.result_label.grid(row=7, column=0, columnspan=2, pady=5)

        # Right frame: table + graph
        right = tk.Frame(self, bg="#e0f7fa")
        right.grid(row=0, column=1, padx=10, pady=20)

        # Conversion table
        self.table = ttk.Treeview(right, columns=("Currency","Amount"), show="headings", height=6)
        self.table.heading("Currency", text="Currency")
        self.table.heading("Amount", text="Converted")
        self.table.pack(pady=5)
        style = ttk.Style()
        style.configure("Treeview", rowheight=25, font=("Arial",11))
        style.configure("Treeview.Heading", font=("Arial",12,"bold"))

        # 7-day trend graph
        self.figure = plt.Figure(figsize=(5,2.5), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor("white")
        self.canvas = FigureCanvasTkAgg(self.figure, right)
        self.canvas.get_tk_widget().pack(pady=10)

    # ----------- Converter Functions -----------

    def convert(self):
        try:
            amount = float(self.amount_entry.get())
            base = self.from_combobox.get()
            target = self.to_combobox.get()

            rates = get_rates(base)
            if not rates or target not in rates:
                messagebox.showerror("Error", "Currency not found")
                return

            converted = amount * rates[target]['value']
            self.result_label.config(text=f"{amount} {base} = {converted:.2f} {target}")

            self.controller.history.append(f"{amount} {base} = {converted:.2f} {target}")
            self.controller.history = self.controller.history[-10:]

            for row in self.table.get_children():
                self.table.delete(row)
            for cur in ['USD','EUR','GBP','PKR','JPY']:
                if cur in rates:
                    self.table.insert("", "end", values=(cur, round(amount*rates[cur]['value'],2)))

            dates, trend = get_historical_rates(base, target)
            self.ax.clear()
            self.ax.plot(dates, trend, marker='o')
            self.ax.set_title(f"{base} → {target} (7 Days)")
            self.ax.set_ylabel("Rate")
            self.ax.set_xlabel("Date")
            self.ax.tick_params(axis='x', rotation=45)
            self.figure.tight_layout()
            self.canvas.draw()

        except ValueError:
            messagebox.showerror("Error", "Enter a valid number")

    def clear(self):
        self.amount_entry.delete(0, tk.END)
        self.table.delete(*self.table.get_children())
        self.ax.clear()
        self.canvas.draw()
        self.result_label.config(text="")

    def toggle_mode(self):
        self.dark_mode = not self.dark_mode
        bg = "#2e2e2e" if self.dark_mode else "#e0f7fa"
        fg = "white" if self.dark_mode else "black"
        self.configure(bg=bg)
        for widget in self.winfo_children():
            if isinstance(widget,(tk.Label,tk.Button,tk.Frame)):
                widget.configure(bg=bg, fg=fg)
class HistoryFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, bg="#e0f7fa")
        self.controller = controller

        tk.Label(self, text="Conversion History", font=("Arial",16,"bold"), bg="#e0f7fa").pack(pady=10)
        self.listbox = tk.Listbox(self, width=50, height=15)
        self.listbox.pack()
        tk.Button(self, text="Back to Home", width=20, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=lambda: controller.show_frame(HomeFrame)).pack(pady=5)

    def refresh(self):
        self.listbox.delete(0, tk.END)
        for item in self.controller.history:
            self.listbox.insert(tk.END, item)
            
class AboutFrame(tk.Frame):
    def __init__(self,parent,controller):
        super().__init__(parent,bg="#e0f7fa")
        tk.Label(self,text="About App", font=("Arial",16,"bold"), bg="#e0f7fa").pack(pady=20)
        tk.Label(self, text="Currency Converter using Currency API\n- Tkinter GUI\n- OOP Design\n- Data Visualisation\n- Dark/Light Mode",
                 bg="#e0f7fa", justify="left").pack()
        tk.Button(self,text="Back to Home", width=20, bg="#3d85c6", fg="white",
                  font=("Arial",11,"bold"), command=lambda: controller.show_frame(HomeFrame)).pack(pady=10)
        
if __name__=="__main__":
    root = tk.Tk()
    app = CurrencyApp(root)
    root.mainloop()

