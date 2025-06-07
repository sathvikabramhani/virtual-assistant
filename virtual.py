import tkinter as tk
from tkinter import ttk, messagebox
import requests
import wikipedia
import sqlite3
from datetime import datetime

class VirtualAssistant:
    def __init__(self):
        self.api_key = None
        self.init_db()

    def init_db(self):
        self.conn = sqlite3.connect("history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS operations (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                operation TEXT,
                                result TEXT,
                                timestamp TEXT)''')
        self.conn.commit()

    def set_api_key(self, key):
        self.api_key = key

    def get_weather(self, city):
        if not self.api_key:
            return "API key not set."
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.api_key}&units=metric"
            res = requests.get(url).json()
            if res.get("main"):
                desc = res["weather"][0]["description"]
                temp = res["main"]["temp"]
                return f"Weather in {city.title()}: {desc}, {temp}°C"
            return "City not found."
        except:
            return "Error fetching weather."

    def answer_question(self, q):
        predefined = {
            "what is your name": "I'm your virtual assistant!",
            "how are you": "I'm functioning optimally!",
            "what can you do": "I can do math, set reminders, tell weather, and answer questions.",
            "who created you": "I was created using Python.",
            "what is the time": datetime.now().strftime("Current time: %H:%M:%S"),
            "what is the date": datetime.now().strftime("Today is: %Y-%m-%d")
        }
        q = q.lower().strip()
        if q in predefined:
            return predefined[q]
        try:
            return wikipedia.summary(q, sentences=2)
        except wikipedia.exceptions.DisambiguationError as e:
            return f"Too broad. Suggestions: {', '.join(e.options[:3])}"
        except wikipedia.exceptions.PageError:
            return "No results found."
        except:
            return "Error processing the query."

    def calculate(self, expression):
        try:
            result = eval(expression)
            self.log_operation(expression, result)
            return result
        except ZeroDivisionError:
            return "Error: Division by zero"
        except:
            return "Invalid expression"

    def log_operation(self, operation, result):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute("INSERT INTO operations (operation, result, timestamp) VALUES (?, ?, ?)",
                            (operation, str(result), timestamp))
        self.conn.commit()

    def get_history(self):
        self.cursor.execute("SELECT * FROM operations ORDER BY id DESC LIMIT 10")
        return self.cursor.fetchall()

class AssistantApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Virtual Assistant")
        self.root.attributes('-fullscreen', True)  # Start in fullscreen mode
        self.root.configure(bg="#ECF0F1")  # Light background
        self.assistant = VirtualAssistant()
        self.build_ui()

        # Bind Escape key to exit fullscreen
        self.root.bind("<Escape>", self.exit_fullscreen)

    def exit_fullscreen(self, event=None):
        self.root.attributes('-fullscreen', False)
        self.root.geometry("800x600")  # Optionally set window size back to normal

    def build_ui(self):
        # Title
        title = tk.Label(self.root, text="🌟 Virtual Assistant", font=("Segoe UI", 36, "bold"),
                         bg="#ECF0F1", fg="#2C3E50")
        title.pack(pady=20)

        # Welcome message
        welcome_msg = tk.Label(self.root, text="What would you like to do?", font=("Segoe UI", 24),
                                bg="#ECF0F1", fg="#34495E")
        welcome_msg.pack(pady=(0, 20))

        # Buttons for different functionalities
        button_frame = tk.Frame(self.root, bg="#ECF0F1")
        button_frame.pack(pady=20)

        ttk.Button(button_frame, text="Get Weather", command=self.select_weather, width=30, padding=10).pack(pady=10)
        ttk.Button(button_frame, text="Calculator", command=self.select_calculator, width=30, padding=10).pack(pady=10)
        ttk.Button(button_frame, text="Set Reminder", command=self.select_reminder, width=30, padding=10).pack(pady=10)
        ttk.Button(button_frame, text="Ask a Question", command=self.select_qa, width=30, padding=10).pack(pady=10)

        # Frame for content forms
        self.content_frame = tk.Frame(self.root, bg="#F9FAFB", bd=0)
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def select_weather(self):
        self.clear_content_frame()

        title = tk.Label(self.content_frame, text="🌤️ Get Weather Information",
                         font=("Segoe UI", 28, "bold"), fg="#2C3E50", bg="#F9FAFB")
        title.pack(anchor='w', pady=(0, 20))

        api_label = tk.Label(self.content_frame, text="OpenWeatherMap API Key:", font=("Segoe UI", 18),
                             bg="#F9FAFB", fg="#34495E")
        api_label.pack(anchor='w')

        self.api_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.api_entry.pack(fill='x', pady=(0, 10))

        city_label = tk.Label(self.content_frame, text="City Name:", font=("Segoe UI", 18),
                              bg="#F9FAFB", fg="#34495E")
        city_label.pack(anchor='w')

        self.city_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.city_entry.pack(fill='x', pady=(0, 10))

        ttk.Button(self.content_frame, text="Get Weather", command=self.show_weather, padding=10).pack(pady=10)

        self.weather_label = tk.Label(self.content_frame, text="", font=("Segoe UI", 18), fg="#2980B9", bg="#F9FAFB")
        self.weather_label.pack(pady=(10, 0))

    def show_weather(self):
        api_key = self.api_entry.get().strip()
        city = self.city_entry.get().strip()
        if not api_key:
            messagebox.showerror("API Key Missing", "Please enter your OpenWeatherMap API key.")
            return
        if not city:
            messagebox.showerror("City Missing", "Please enter a city name.")
            return
        self.assistant.set_api_key(api_key)
        result = self.assistant.get_weather(city)
        self.weather_label.config(text=result)

    def select_calculator(self):
        self.clear_content_frame()

        title = tk.Label(self.content_frame, text="➗ Arithmetic Calculator",
                         font=("Segoe UI", 28, "bold"), fg="#2C3E50", bg="#F9FAFB")
        title.pack(anchor='w', pady=(0, 20))

        expr_label = tk.Label(self.content_frame, text="Enter an expression (e.g., 3 + 4 * 2):",
                              font=("Segoe UI", 18), bg="#F9FAFB", fg="#34495E")
        expr_label.pack(anchor='w')

        self.expr_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.expr_entry.pack(fill='x', pady=(0, 10))

        ttk.Button(self.content_frame, text="Calculate", command=self.calculate, padding=10).pack(pady=10)

        self.result_label = tk.Label(self.content_frame, text="", font=("Segoe UI", 18), fg="#27AE60", bg="#F9FAFB")
        self.result_label.pack(pady=(10, 0))

    def calculate(self):
        expr = self.expr_entry.get().strip()
        if not expr:
            messagebox.showerror("Input Missing", "Please enter a valid expression.")
            return
        result = self.assistant.calculate(expr)
        self.result_label.config(text=f"Result: {result}")

    def select_reminder(self):
        self.clear_content_frame()

        title = tk.Label(self.content_frame, text="⏰ Set a Reminder",
                         font=("Segoe UI", 28, "bold"), fg="#2C3E50", bg="#F9FAFB")
        title.pack(anchor='w', pady=(0, 20))

        reminder_label = tk.Label(self.content_frame, text="Reminder Text:", font=("Segoe UI", 18),
                                  bg="#F9FAFB", fg="#34495E")
        reminder_label.pack(anchor='w')

        self.reminder_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.reminder_entry.pack(fill='x', pady=(0, 10))

        time_label = tk.Label(self.content_frame, text="Set Time (24h format HH:MM):", font=("Segoe UI", 18),
                              bg="#F9FAFB", fg="#34495E")
        time_label.pack(anchor='w')

        self.reminder_time_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.reminder_time_entry.pack(fill='x', pady=(0, 10))

        ttk.Button(self.content_frame, text="Set Reminder", command=self.set_reminder, padding=10).pack(pady=10)

    def set_reminder(self):
        text = self.reminder_entry.get().strip()
        time_str = self.reminder_time_entry.get().strip()
        if not text:
            messagebox.showerror("Input Error", "Please enter reminder text.")
            return
        if not time_str:
            messagebox.showerror("Input Error", "Please enter a time (HH:MM).")
            return

        try:
            reminder_time = datetime.strptime(time_str, "%H:%M").time()
            now = datetime.now()
            reminder_datetime = datetime.combine(now.date(), reminder_time)
            if reminder_datetime < now:
                # If time already passed today, schedule for next day
                reminder_datetime = reminder_datetime.replace(day=now.day + 1)
        except Exception:
            messagebox.showerror("Input Error", "Time must be in HH:MM 24h format.")
            return

        # Save reminder
        messagebox.showinfo("Reminder Set", f"Reminder set for {reminder_datetime.strftime('%Y-%m-%d %H:%M')}")
        self.reminder_entry.delete(0, tk.END)
        self.reminder_time_entry.delete(0, tk.END)

    def select_qa(self):
        self.clear_content_frame()

        title = tk.Label(self.content_frame, text="💬 Ask a Question",
                         font=("Segoe UI", 28, "bold"), fg="#2C3E50", bg="#F9FAFB")
        title.pack(anchor='w', pady=(0, 20))

        question_label = tk.Label(self.content_frame, text="Enter your question:", font=("Segoe UI", 18),
                                  bg="#F9FAFB", fg="#34495E")
        question_label.pack(anchor='w')

        self.qa_entry = tk.Entry(self.content_frame, font=("Segoe UI", 18), bd=1, relief="solid", width=30)
        self.qa_entry.pack(fill='x', pady=(0, 10))

        ttk.Button(self.content_frame, text="Ask", command=self.ask, padding=10).pack(pady=10)

        self.qa_label = tk.Label(self.content_frame, text="", wraplength=500, foreground="#34495E", bg="#F9FAFB")
        self.qa_label.pack(pady=(10, 0))

    def ask(self):
        query = self.qa_entry.get().strip()
        if not query:
            messagebox.showerror("Input Error", "Please enter a question.")
            return
        response = self.assistant.answer_question(query)
        self.qa_label.config(text=response)

if __name__ == "__main__":
    root = tk.Tk()
    app = AssistantApp(root)
    root.mainloop()
