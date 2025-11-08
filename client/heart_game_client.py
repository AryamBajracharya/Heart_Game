import tkinter as tk
from tkinter import messagebox, ttk
from PIL import Image, ImageTk
import requests, io, pygame, threading, random
from config import SERVER_URL

pygame.mixer.init()

def play_sound(sound_file):
    try:
        pygame.mixer.Sound(sound_file).play()
    except Exception:
        pass

class HeartGameClient:
    def __init__(self, root):
        self.root = root
        self.root.title("❤️ Heart Guess Game - Client")
        self.root.geometry("900x600")
        self.root.config(bg="black")

        self.username = None
        self.token = None
        self.score = 0
        self.high_score = 0

        self.show_login()

    # -------------------- LOGIN SCREEN -------------------- #
    def show_login(self):
        self.clear_screen()

        tk.Label(self.root, text="🔐 LOGIN",
                 font=("Arial Rounded MT Bold", 28),
                 fg="#ff6699", bg="black").pack(pady=40)

        tk.Label(self.root, text="Username:", fg="white", bg="black", font=("Arial", 14)).pack()
        self.username_entry = tk.Entry(self.root, font=("Arial", 14))
        self.username_entry.pack(pady=5)

        tk.Label(self.root, text="Password:", fg="white", bg="black", font=("Arial", 14)).pack()
        self.password_entry = tk.Entry(self.root, font=("Arial", 14), show="*")
        self.password_entry.pack(pady=5)

        ttk.Button(self.root, text="Login", command=self.login).pack(pady=10)
        ttk.Button(self.root, text="Register", command=self.register).pack(pady=10)

    # -------------------- REGISTER -------------------- #
    def register(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Enter all fields")
            return
        try:
            r = requests.post(f"{SERVER_URL}/register", json={"username": username, "password": password})
            data = r.json()
            messagebox.showinfo("Register", data.get("message", data.get("error", "")))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot reach server.\n{e}")

    # -------------------- LOGIN -------------------- #
    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        if not username or not password:
            messagebox.showerror("Error", "Enter both username and password")
            return
        try:
            r = requests.post(f"{SERVER_URL}/login", json={"username": username, "password": password})
            if r.status_code == 200:
                data = r.json()
                self.username = data["username"]
                self.token = data["token"]
                self.high_score = data.get("highscore", 0)
                messagebox.showinfo("Login", f"Welcome, {self.username}! 🎉")
                self.show_menu()
            else:
                messagebox.showerror("Error", "Invalid credentials")
        except Exception as e:
            messagebox.showerror("Connection Error", f"Cannot reach server.\n{e}")

    # -------------------- MENU -------------------- #
    def show_menu(self):
        self.clear_screen()

        tk.Label(self.root, text="💖 HEART GUESS GAME 💖",
                 font=("Arial Rounded MT Bold", 36),
                 fg="#ff6699", bg="black").pack(pady=30)

        tk.Label(self.root, text=f"Welcome, {self.username}!",
                 font=("Arial Rounded MT Bold", 20), fg="#00ffcc", bg="black").pack(pady=10)

        ttk.Button(self.root, text="🎮 Play", command=self.start_game).pack(pady=10)
        ttk.Button(self.root, text="🏆 Leaderboard", command=self.show_leaderboard).pack(pady=10)
        ttk.Button(self.root, text="❌ Logout", command=self.show_login).pack(pady=10)

        tk.Label(self.root, text=f"High Score: {self.high_score}",
                 font=("Arial", 16), fg="white", bg="black").pack(pady=20)

    # -------------------- START GAME -------------------- #
    def start_game(self):
        self.score = 0
        self.load_question()

    def load_question(self):
        self.clear_screen()
        ttk.Button(self.root, text="⬅️ Back", command=self.show_menu).place(x=20, y=20)
        tk.Label(self.root, text=f"Player: {self.username} | Score: {self.score}",
                 fg="white", bg="black", font=("Arial", 14)).pack(anchor="ne", padx=10, pady=5)
        tk.Label(self.root, text="💖 Guess the Heart Value 💖",
                 fg="#00ffcc", bg="black", font=("Arial", 24)).pack(pady=10)

        try:
            r = requests.get("https://marcconrad.com/uob/heart/api.php", timeout=5)
            data = r.json()
            img_data = requests.get(data['question']).content
            img = Image.open(io.BytesIO(img_data))
            self.answer = data['solution']
        except Exception:
            img = Image.open("assets/heart.jpg")
            self.answer = random.randint(1, 9)

        img = img.resize((250, 300))
        self.img_tk = ImageTk.PhotoImage(img)
        tk.Label(self.root, image=self.img_tk, bg="black").pack(pady=20)

        tk.Label(self.root, text="Enter answer (1-9):",
                 fg="white", bg="black", font=("Arial", 16)).pack()
        self.answer_entry = tk.Entry(self.root, font=("Arial", 16))
        self.answer_entry.pack(pady=10)

        ttk.Button(self.root, text="✅ Submit", command=self.check_answer).pack(pady=20)

    def check_answer(self):
        user_input = self.answer_entry.get().strip()
        if not user_input.isdigit():
            messagebox.showerror("Error", "Enter a number")
            return

        if int(user_input) == self.answer:
            play_sound("sounds/correct.mp3")
            self.score += 10
            messagebox.showinfo("Correct", "🎉 +10 Points!")
        else:
            play_sound("sounds/wrong.mp3")
            messagebox.showerror("Wrong", f"The answer was {self.answer}")

        self.update_score()
        threading.Timer(1.2, self.load_question).start()

    # -------------------- SCORE MANAGEMENT -------------------- #
    def update_score(self):
        try:
            r = requests.post(f"{SERVER_URL}/submit_score",
                              json={"token": self.token, "score": self.score})
            if r.status_code == 200:
                data = r.json()
                self.high_score = data.get("highscore", self.high_score)
        except Exception as e:
            print("Score update failed:", e)

    # -------------------- LEADERBOARD -------------------- #
    def show_leaderboard(self):
        self.clear_screen()
        tk.Label(self.root, text="🏆 Leaderboard 🏆",
                 font=("Arial Rounded MT Bold", 28),
                 fg="#ff6699", bg="black").pack(pady=30)
        try:
            r = requests.get(f"{SERVER_URL}/leaderboard")
            data = r.json().get("leaderboard", [])
        except Exception:
            data = []

        if not data:
            tk.Label(self.root, text="No scores yet!",
                     font=("Arial", 16), fg="white", bg="black").pack(pady=20)
        else:
            table = ttk.Treeview(self.root, columns=("Rank", "Player", "Score"), show="headings", height=10)
            table.heading("Rank", text="Rank")
            table.heading("Player", text="Player")
            table.heading("Score", text="Score")
            table.column("Rank", width=80, anchor="center")
            table.column("Player", width=200, anchor="center")
            table.column("Score", width=100, anchor="center")

            for i, player in enumerate(data, start=1):
                table.insert("", "end", values=(i, player["username"], player["highscore"]))

            table.pack(pady=10)

        ttk.Button(self.root, text="⬅️ Back", command=self.show_menu).pack(pady=20)

    # -------------------- UTILITY -------------------- #
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = HeartGameClient(root)
    root.mainloop()
