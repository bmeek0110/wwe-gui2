import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import sqlite3
import random

# Database setup
def init_db():
    conn = sqlite3.connect('wwe_predictions.db')
    cursor = conn.cursor()

    # Create users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            wins INTEGER DEFAULT 0,
            losses INTEGER DEFAULT 0
        )
    ''')

    # Create events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            date TEXT NOT NULL
        )
    ''')

    # Create matches table linked to events
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id INTEGER,
            match TEXT NOT NULL,
            winner TEXT,
            FOREIGN KEY(event_id) REFERENCES events(id)
        )
    ''')

    # Create match history table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS match_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            match_id INTEGER,
            user_prediction TEXT,
            result TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(match_id) REFERENCES matches(id)
        )
    ''')

    conn.commit()
    return conn

# Sample events and matches
events = [
    {"name": "Crown Jewel", "date": "2024-11-02"},
    {"name": "Main Event", "date": "TBD"},
    {"name": "Survivor Series", "date": "TBD"},
]

matches = [
    {"event": "Crown Jewel", "match": "The American Nightmare vs. The Ring General", "predictions": ["The American Nightmare", "The Ring General"], "winner": None},
    {"event": "Crown Jewel", "match": "Seth Freakin Rollins vs. Big Bronson Reed", "predictions": ["Seth Freakin Rollins", "Big Bronson Reed"], "winner": None},
    {"event": "Crown Jewel", "match": "The Legend Killer vs. KO", "predictions": ["The Legend Killer", "KO"], "winner": None},
    {"event": "Crown Jewel", "match": "Nia Jax vs. Liv Morgan", "predictions": ["Nia Jax", "Liv Morgan"], "winner": None},
    {"event": "Crown Jewel", "match": "LA Knight vs. Andrade vs. Carmello Hayes", "predictions": ["LA Knight", "Andrade", "Carmello Hayes"], "winner": None},
    {"event": "Crown Jewel", "match": "Jade and Bianca vs. Dmg Ctrl vs. Meta Four vs. Chelsea Green and Piper", "predictions": ["Jade and Bianca", "Dmg Ctrl", "Meta Four", "Chelsea Green and Piper"], "winner": None},
]

class WWEApp:
    def __init__(self, root):
        self.root = root
        self.root.title("WWE Event Prediction")
        self.root.geometry("400x600")
        self.root.configure(bg="#1C1C2B")
        self.conn = init_db()
        self.username = None
        
        self.init_ui()

    def init_ui(self):
        # Main menu frame
        self.main_frame = tk.Frame(self.root, bg="#1C1C2B")
        self.main_frame.pack(pady=20)

        self.title_label = tk.Label(self.main_frame, text="WWE Event Prediction", font=("Helvetica", 24, 'bold'), bg="#1C1C2B", fg="#EAEAEA")
        self.title_label.pack()

        self.login_button = self.create_button("Login", self.show_login_window)
        self.login_button.pack(pady=5)

        self.register_button = self.create_button("Register", self.show_register_window)
        self.register_button.pack(pady=5)

        self.quit_button = tk.Button(self.main_frame, text="Exit", command=self.root.quit, width=20, bg="#e74c3c", fg="#ffffff", 
                                      activebackground="#c0392b", activeforeground="#ffffff", highlightthickness=0, 
                                      highlightbackground="#1C1C2B", relief="flat", font=("Helvetica", 12))
        self.quit_button.pack(pady=5)

    def create_button(self, text, command):
        return tk.Button(self.main_frame, text=text, command=command, width=20, bg="#3498db", fg="#ffffff", 
                         activebackground="#2980b9", activeforeground="#ffffff", highlightthickness=0, 
                         highlightbackground="#1C1C2B", relief="flat", font=("Helvetica", 12))

    def show_login_window(self):
        self.login_window = tk.Toplevel(self.root)
        self.login_window.title("Login")
        self.login_window.geometry("300x250")
        self.login_window.configure(bg="#2E2E38")

        tk.Label(self.login_window, text="Username:", bg="#2E2E38", fg="#EAEAEA").pack(pady=10)
        self.login_username_entry = tk.Entry(self.login_window)
        self.login_username_entry.pack(pady=5)

        login_button = tk.Button(self.login_window, text="Login", command=self.login, bg="#3498db", fg="#ffffff")
        login_button.pack(pady=10)

        cancel_button = tk.Button(self.login_window, text="Cancel", command=self.login_window.destroy, bg="#e74c3c", fg="#ffffff")
        cancel_button.pack(pady=5)

    def show_register_window(self):
        self.register_window = tk.Toplevel(self.root)
        self.register_window.title("Register")
        self.register_window.geometry("300x250")
        self.register_window.configure(bg="#2E2E38")

        tk.Label(self.register_window, text="Choose a Username:", bg="#2E2E38", fg="#EAEAEA").pack(pady=10)
        self.register_username_entry = tk.Entry(self.register_window)
        self.register_username_entry.pack(pady=5)

        register_button = tk.Button(self.register_window, text="Register", command=self.register, bg="#3498db", fg="#ffffff")
        register_button.pack(pady=10)

        cancel_button = tk.Button(self.register_window, text="Cancel", command=self.register_window.destroy, bg="#e74c3c", fg="#ffffff")
        cancel_button.pack(pady=5)

    def register(self):
        username = self.register_username_entry.get()
        if username:
            self.add_user(username)
            messagebox.showinfo("Success", f"User {username} registered successfully!")
            self.register_window.destroy()
        else:
            messagebox.showerror("Error", "Username cannot be empty.")

    def login(self):
        username = self.login_username_entry.get()
        if username and self.check_user_exists(username):
            self.username = username
            self.login_window.destroy()
            self.show_dashboard()  
        else:
            messagebox.showerror("Error", "Invalid username. Please try again.")

    def show_dashboard(self):
        self.dashboard_window = tk.Toplevel(self.root)
        self.dashboard_window.title("Select Event for Predictions")
        self.dashboard_window.geometry("400x600")
        self.dashboard_window.configure(bg="#1C1C2B")

        dashboard_title = tk.Label(self.dashboard_window, text=f"Welcome, {self.username}!", font=("Helvetica", 16), bg="#1C1C2B", fg="#EAEAEA")
        dashboard_title.pack(pady=10)

        tk.Label(self.dashboard_window, text="Select an Event:", font=("Helvetica", 14), bg="#1C1C2B", fg="#EAEAEA").pack(pady=(10, 0))

        # Dropdown menu for events
        self.event_combobox = ttk.Combobox(self.dashboard_window, state="readonly")
        self.event_combobox['values'] = [event["name"] for event in events]
        self.event_combobox.pack(pady=10)

        select_button = tk.Button(self.dashboard_window, text="Select Event", command=self.display_event_matches, bg="#3498db", fg="#ffffff")
        select_button.pack(pady=5)

        self.leaderboard_button = tk.Button(self.dashboard_window, text="View Leaderboard", command=self.show_leaderboard, width=20, bg="#3498db", fg="#ffffff")
        self.leaderboard_button.pack(pady=5)

        self.set_results_button = tk.Button(self.dashboard_window, text="Set Match Results", command=self.set_match_results, width=20, bg="#3498db", fg="#ffffff")
        self.set_results_button.pack(pady=5)

        self.logout_button = tk.Button(self.dashboard_window, text="Logout", command=self.logout, width=20, bg="#e74c3c", fg="#ffffff")
        self.logout_button.pack(pady=20)

    def display_event_matches(self):
        event_name = self.event_combobox.get()
        matches_for_event = [match for match in matches if match['event'] == event_name]
        
        match_window = tk.Toplevel(self.dashboard_window)
        match_window.title(f"Matches for {event_name}")
        match_window.geometry("400x400")
        match_window.configure(bg="#2E2E38")

        tk.Label(match_window, text=f"Matches for {event_name}", font=("Helvetica", 16), bg="#2E2E38", fg="#EAEAEA").pack(pady=10)

        self.match_results = {}
        for match in matches_for_event:
            match_label = tk.Label(match_window, text=match['match'], bg="#2E2E38", fg="#EAEAEA")
            match_label.pack(pady=5)

            user_prediction = simpledialog.askstring("Prediction", f"Who do you think will win in '{match['match']}'? ({', '.join(match['predictions'])})")
            self.match_results[match["match"]] = user_prediction if user_prediction in match['predictions'] else None

            # Store prediction in database
            if self.match_results[match["match"]]:
                match_id = self.get_match_id(match["match"], event_name)
                self.store_prediction(self.username, match_id, self.match_results[match["match"]])

        # Show results button
        show_results_button = tk.Button(match_window, text="Show Results", command=lambda: self.show_match_results(match_window), bg="#3498db", fg="#ffffff")
        show_results_button.pack(pady=10)

    def show_match_results(self, match_window):
        results_text = "Your Predictions:\n\n"
        for match, prediction in self.match_results.items():
            results_text += f"{match}: {prediction}\n"

        messagebox.showinfo("Match Results", results_text)

    def get_match_id(self, match_name, event_name):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM matches WHERE match = ? AND event_id = (SELECT id FROM events WHERE name = ?)", (match_name, event_name))
        match_id = cursor.fetchone()
        return match_id[0] if match_id else None

    def store_prediction(self, username, match_id, user_prediction):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        user_id = cursor.fetchone()
        if user_id:
            cursor.execute("INSERT INTO match_history (user_id, match_id, user_prediction, result) VALUES (?, ?, ?, ?)", 
                           (user_id[0], match_id, user_prediction, "Pending"))
            self.conn.commit()

    def add_user(self, username):
        cursor = self.conn.cursor()
        try:
            cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
            self.conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username already exists. Please choose a different username.")

    def check_user_exists(self, username):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
        return cursor.fetchone() is not None

    def show_leaderboard(self):
        leaderboard_window = tk.Toplevel(self.root)
        leaderboard_window.title("Leaderboard")
        leaderboard_window.geometry("300x400")
        leaderboard_window.configure(bg="#2E2E38")

        tk.Label(leaderboard_window, text="Leaderboard:", font=("Helvetica", 16), bg="#2E2E38", fg="#EAEAEA").pack(pady=10)

        cursor = self.conn.cursor()
        cursor.execute("SELECT username, wins, losses FROM users ORDER BY wins DESC")
        users = cursor.fetchall()

        for user in users:
            username, wins, losses = user
            tk.Label(leaderboard_window, text=f"{username}: {wins} Wins, {losses} Losses", bg="#2E2E38", fg="#EAEAEA").pack(pady=5)

    def set_match_results(self):
        event_name = self.event_combobox.get()
        matches_for_event = [match for match in matches if match['event'] == event_name]

        results_window = tk.Toplevel(self.dashboard_window)
        results_window.title(f"Set Results for {event_name}")
        results_window.geometry("400x400")
        results_window.configure(bg="#2E2E38")

        tk.Label(results_window, text=f"Set Match Results for {event_name}", font=("Helvetica", 16), bg="#2E2E38", fg="#EAEAEA").pack(pady=10)

        for match in matches_for_event:
            match_label = tk.Label(results_window, text=match['match'], bg="#2E2E38", fg="#EAEAEA")
            match_label.pack(pady=5)

            winner = simpledialog.askstring("Winner", f"Who won in '{match['match']}'? ({', '.join(match['predictions'])})")
            match['winner'] = winner if winner in match['predictions'] else None
            match_id = self.get_match_id(match['match'], event_name)

            if match['winner']:
                self.update_match_result(match_id, match['winner'])
                self.update_user_predictions(match_id, match['winner'])

        messagebox.showinfo("Results Set", "Match results have been successfully set!")

    def update_match_result(self, match_id, winner):
        cursor = self.conn.cursor()
        cursor.execute("UPDATE matches SET winner = ? WHERE id = ?", (winner, match_id))
        self.conn.commit()

    def update_user_predictions(self, match_id, winner):
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, user_prediction FROM match_history WHERE match_id = ?", (match_id,))
        predictions = cursor.fetchall()

        for user_id, user_prediction in predictions:
            if user_prediction == winner:
                cursor.execute("UPDATE users SET wins = wins + 1 WHERE id = ?", (user_id,))
            else:
                cursor.execute("UPDATE users SET losses = losses + 1 WHERE id = ?", (user_id,))
        
        self.conn.commit()

    def logout(self):
        self.username = None
        self.dashboard_window.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = WWEApp(root)
    root.mainloop()
