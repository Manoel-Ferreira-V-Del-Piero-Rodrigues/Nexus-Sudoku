import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import copy
import random
import time
import json
import os

# --- DARK MODE COLORS ---
DARK_BG = "#181a20"
PANEL_BG = "#232630"
FG = "#f5ecd7"
ACCENT = "#d0b36a"
BTN_BG = "#232630"
BTN_FG = "#f5ecd7"
BTN_HIGHLIGHT = "#3b3f4a"
DESC_FG = "#c6b6a1"
ENTRY_BG = "#232630"
ENTRY_FG = "#f5ecd7"
ENTRY_DISABLED_BG = "#3b3f4a"
ENTRY_DISABLED_FG = "#ad9f8b"
ENTRY_CORRECT_BG = "#a5e6a3"
ENTRY_WRONG_BG = "#fdcbcb"
ENTRY_HIGHLIGHT_BG = "#ffeaa7"
ENTRY_HINT_BG = "#ffeaa7"
BTN_ACCENT_FG = "#262626"

DIFFICULTY_CLUES = {
    "easy": 36,
    "medium": 32,
    "hard": 28
}
DIFFICULTY_BONUS = {
    "easy": 0,
    "medium": 300,
    "hard": 600
}
HIGHSCORE_FILE = "highscores.json"
USER_FILE = "user.json"
USER_LIST_FILE = "users.json"
LOGO_FILENAME = os.path.join(os.path.dirname(__file__), "logo.png")  # Always resolve relative to script location

def generate_full_board():
    board = [[0] * 9 for _ in range(9)]
    def is_valid(board, row, col, num):
        for i in range(9):
            if board[row][i] == num or board[i][col] == num:
                return False
        start_row, start_col = 3*(row//3), 3*(col//3)
        for i in range(3):
            for j in range(3):
                if board[start_row+i][start_col+j] == num:
                    return False
        return True
    def fill(board):
        for i in range(9):
            for j in range(9):
                if board[i][j] == 0:
                    nums = list(range(1, 10))
                    random.shuffle(nums)
                    for num in nums:
                        if is_valid(board, i, j, num):
                            board[i][j] = num
                            if fill(board):
                                return True
                            board[i][j] = 0
                    return False
        return True
    fill(board)
    return board

def make_puzzle(full_board, clues):
    puzzle = copy.deepcopy(full_board)
    cells = [(i, j) for i in range(9) for j in range(9)]
    random.shuffle(cells)
    for (i, j) in cells:
        if sum(1 for row in puzzle for v in row if v != 0) <= clues:
            break
        puzzle[i][j] = 0
    return puzzle

def get_user_list():
    if os.path.exists(USER_LIST_FILE):
        try:
            with open(USER_LIST_FILE, "r") as f:
                users = json.load(f)
                if isinstance(users, list):
                    return users
        except Exception:
            pass
    return []

def save_user_list(users):
    with open(USER_LIST_FILE, "w") as f:
        json.dump(users, f)

def save_active_user(username):
    with open(USER_FILE, "w") as f:
        json.dump({"username": username}, f)

def load_username():
    if os.path.exists(USER_FILE):
        try:
            with open(USER_FILE, "r") as f:
                data = json.load(f)
                return data.get("username", None)
        except Exception:
            return None
    return None

class Sudoku:
    def __init__(self, starting_board):
        self.starting_board = copy.deepcopy(starting_board)
        self.board = copy.deepcopy(self.starting_board)
    def is_valid(self, row, col, num):
        for i in range(9):
            if self.board[row][i] == num or self.board[i][col] == num:
                return False
        start_row, start_col = 3*(row//3), 3*(col//3)
        for i in range(3):
            for j in range(3):
                if self.board[start_row+i][start_col+j] == num:
                    return False
        return True
    def solve(self):
        for row in range(9):
            for col in range(9):
                if self.board[row][col] == 0:
                    for num in range(1, 10):
                        if self.is_valid(row, col, num):
                            self.board[row][col] = num
                            if self.solve():
                                return True
                            self.board[row][col] = 0
                    return False
        return True

class UsernameMenu:
    def __init__(self, root, on_submit, allow_cancel=False):
        self.root = root
        self.on_submit = on_submit
        self.allow_cancel = allow_cancel
        self.top = tk.Toplevel(root)
        self.top.title("Create a Nexus Sudoku account")
        self.top.configure(bg=DARK_BG)
        self.top.resizable(False, False)
        w, h = 420, 210
        ws = self.top.winfo_screenwidth()
        hs = self.top.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.top.geometry(f"{w}x{h}+{x}+{y}")

        # Logo
        logo_frame = tk.Frame(self.top, bg=DARK_BG)
        logo_frame.pack(pady=(15, 0))
        try:
            img = Image.open(LOGO_FILENAME)
            img = img.resize((80, 60), Image.ANTIALIAS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(logo_frame, image=self.logo_img, bg=DARK_BG, bd=0)
            logo_label.pack()
        except Exception:
            logo_label = tk.Label(logo_frame, text="🧩", font=("Arial", 30), bg=DARK_BG, fg=FG)
            logo_label.pack()

        title = tk.Label(self.top, text="Create a username", font=("Arial", 20, "bold"), bg=DARK_BG, fg=ACCENT)
        title.pack(pady=(0, 10))
        self.entry = tk.Entry(self.top, font=("Arial", 18), bg=ENTRY_BG, fg=ENTRY_FG, insertbackground=ENTRY_FG, width=20)
        self.entry.pack(pady=(0, 12))
        self.entry.focus_set()
        self.top.bind("<Return>", self.submit)
        submit_btn = tk.Button(self.top, text="Create", font=("Arial", 14, "bold"), bg=BTN_BG, fg=ACCENT,
                               activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                               relief="flat", bd=0, cursor="hand2", command=self.submit)
        submit_btn.pack()
        if self.allow_cancel:
            cancel_btn = tk.Button(self.top, text="Cancel", font=("Arial", 12), bg=BTN_BG, fg=DESC_FG,
                                   relief="flat", bd=0, cursor="hand2", command=self.cancel)
            cancel_btn.pack(pady=(7, 0))
        self.msg = tk.Label(self.top, text="", font=("Arial", 12), bg=DARK_BG, fg="#ff8c8c")
        self.msg.pack(pady=(6, 0))

    def submit(self, event=None):
        username = self.entry.get().strip()
        if not username:
            self.msg.config(text="Username cannot be empty.")
            return
        if len(username) > 20:
            self.msg.config(text="Username too long (max 20 chars).")
            return
        users = get_user_list()
        if username in users:
            self.msg.config(text="That username already exists. Choose another.")
            return
        users.append(username)
        save_user_list(users)
        save_active_user(username)
        self.top.destroy()
        self.on_submit(username)

    def cancel(self):
        self.top.destroy()
        self.on_submit(None)

class AccountSwitchMenu:
    def __init__(self, root, on_select):
        self.root = root
        self.on_select = on_select
        self.top = tk.Toplevel(root)
        self.top.title("Switch account")
        self.top.configure(bg=DARK_BG)
        self.top.resizable(False, False)
        w, h = 400, 350
        ws = self.top.winfo_screenwidth()
        hs = self.top.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.top.geometry(f"{w}x{h}+{x}+{y}")

        title = tk.Label(self.top, text="Choose an account", font=("Arial", 18, "bold"), bg=DARK_BG, fg=ACCENT)
        title.pack(pady=(20, 10))

        self.users = get_user_list()
        self.selected_idx = 0
        self.listbox = tk.Listbox(self.top, font=("Arial", 16), bg=ENTRY_BG, fg=ENTRY_FG, width=22, height=8, activestyle='dotbox', selectbackground=ACCENT, selectforeground=DARK_BG)
        for u in self.users:
            self.listbox.insert(tk.END, u)
        self.listbox.pack(pady=(0,10))
        if self.users:
            self.listbox.select_set(0)
        self.listbox.bind("<Double-1>", self.select_user)
        self.listbox.bind("<Return>", self.select_user)
        self.listbox.bind("<Up>", self.move_up)
        self.listbox.bind("<Down>", self.move_down)

        btn_frame = tk.Frame(self.top, bg=DARK_BG)
        btn_frame.pack(pady=(0, 10))
        select_btn = tk.Button(btn_frame, text="Select", font=("Arial", 13, "bold"), bg=BTN_BG, fg=ACCENT,
                               activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                               relief="flat", bd=0, cursor="hand2", command=self.select_user)
        select_btn.grid(row=0, column=0, padx=6)
        new_btn = tk.Button(btn_frame, text="Create new account", font=("Arial", 13), bg=BTN_BG, fg=DESC_FG,
                            activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                            relief="flat", bd=0, cursor="hand2", command=self.create_new)
        new_btn.grid(row=0, column=1, padx=6)
        cancel_btn = tk.Button(btn_frame, text="Cancel", font=("Arial", 13), bg=BTN_BG, fg=DESC_FG,
                               relief="flat", bd=0, cursor="hand2", command=self.cancel)
        cancel_btn.grid(row=0, column=2, padx=6)
        self.msg = tk.Label(self.top, text="", font=("Arial", 12), bg=DARK_BG, fg="#ff8c8c")
        self.msg.pack(pady=(6, 0))

    def select_user(self, event=None):
        users = self.users
        idxs = self.listbox.curselection()
        if not users or not idxs:
            self.msg.config(text="Select an account or create a new one.")
            return
        username = users[idxs[0]]
        save_active_user(username)
        self.top.destroy()
        self.on_select(username)

    def create_new(self):
        self.top.withdraw()
        UsernameMenu(self.root, self.finish_new_account, allow_cancel=True)

    def finish_new_account(self, username):
        if username:
            self.top.destroy()
            self.on_select(username)
        else:
            self.top.deiconify()

    def cancel(self):
        self.top.destroy()
        self.on_select(None)

    def move_up(self, event):
        idxs = self.listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        if idx > 0:
            self.listbox.selection_clear(idx)
            self.listbox.selection_set(idx-1)
            self.listbox.activate(idx-1)

    def move_down(self, event):
        idxs = self.listbox.curselection()
        if not idxs:
            return
        idx = idxs[0]
        if idx < len(self.users)-1:
            self.listbox.selection_clear(idx)
            self.listbox.selection_set(idx+1)
            self.listbox.activate(idx+1)

class SudokuMenu:
    def __init__(self, root, start_callback, username, account_switch_callback):
        self.root = root
        self.start_callback = start_callback
        self.account_switch_callback = account_switch_callback
        self.username = username
        self.menu_win = tk.Toplevel(self.root)
        self.menu_win.title("Welcome to Nexus Sudoku!")
        self.menu_win.resizable(True, True)
        self.menu_win.configure(bg=DARK_BG)
        self.menu_win.update_idletasks()
        w, h = 900, 650  # Increased window size
        ws = self.menu_win.winfo_screenwidth()
        hs = self.menu_win.winfo_screenheight()
        x = (ws // 2) - (w // 2)
        y = (hs // 2) - (h // 2)
        self.menu_win.geometry(f"{w}x{h}+{x}+{y}")

        # --- Logo ---
        logo_frame = tk.Frame(self.menu_win, bg=DARK_BG)
        logo_frame.pack(pady=(30, 0))
        try:
            img = Image.open(LOGO_FILENAME)
            img = img.resize((180, 130), Image.ANTIALIAS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(logo_frame, image=self.logo_img, bg=DARK_BG, bd=0)
            logo_label.pack()
        except Exception:
            logo_label = tk.Label(logo_frame, text="🧩", font=("Arial", 60), bg=DARK_BG, fg=FG)
            logo_label.pack()

        title = tk.Label(self.menu_win, text="NEXUS SUDOKU", font=("Arial", 38, "bold"), bg=DARK_BG, fg=ACCENT)
        title.pack(pady=(0, 10))
        subtitle = tk.Label(self.menu_win, text=f"Welcome, {self.username}! Choose your challenge:", font=("Arial", 17), bg=DARK_BG, fg=DESC_FG)
        subtitle.pack(pady=(0, 18))

        self.difficulties = [
            {
                "key": "easy",
                "emoji": "🟢",
                "name": "Easy",
                "desc": "Beginner-friendly, lots of clues."
            },
            {
                "key": "medium",
                "emoji": "🟡",
                "name": "Medium",
                "desc": "A fair challenge for most players."
            },
            {
                "key": "hard",
                "emoji": "🔴",
                "name": "Hard",
                "desc": "Fewer clues, only for experts!"
            }
        ]
        self.selected_idx = 0
        self.buttons = []
        self.btn_frame = tk.Frame(self.menu_win, bg=DARK_BG)
        self.btn_frame.pack(pady=20)
        self.make_menu_buttons()

        # --- Change account button must be packed to self.menu_win ---
        switch_btn = tk.Button(
            self.menu_win,
            text="Change account",
            font=("Arial", 15, "bold"),
            bg=BTN_BG, fg=ACCENT,
            activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
            relief="flat", bd=0, cursor="hand2",
            command=self.switch_account
        )
        switch_btn.pack(pady=(7, 0))

        credits = tk.Label(self.menu_win, text="Developed By Manoel Del Piero, 2025", font=("Arial", 11, "italic"),
                           bg=DARK_BG, fg="#808080", anchor="e")
        credits.place(relx=1.0, rely=1.0, anchor="se", x=-14, y=-10)

        self.menu_win.bind("<Up>", self.on_up)
        self.menu_win.bind("<Down>", self.on_down)
        self.menu_win.bind("<Return>", self.on_enter)
        self.highlight_selected()
        self.menu_win.protocol("WM_DELETE_WINDOW", self.root.destroy)

    def make_menu_buttons(self):
        for child in self.btn_frame.winfo_children():
            child.destroy()
        self.buttons.clear()
        for i, diff in enumerate(self.difficulties):
            frm = tk.Frame(self.btn_frame, bg=DARK_BG)
            frm.pack(fill="x", pady=13, padx=20)
            btn = tk.Button(
                frm,
                text=f"{diff['emoji']}  {diff['name']}",
                font=("Arial", 28, "bold"), # increased font size
                width=15,
                bg=BTN_BG,
                fg=BTN_FG,
                activebackground=BTN_HIGHLIGHT,
                activeforeground=ACCENT,
                cursor="hand2",
                relief="flat", bd=0, highlightthickness=0,
                command=lambda d=diff['key']: self.start(d)
            )
            btn.pack(side="left", padx=12)
            btn.bind("<Enter>", lambda e, idx=i: self.set_selected(idx))
            desc = tk.Label(frm, text=diff["desc"], font=("Arial", 16), bg=DARK_BG, fg=DESC_FG)
            desc.pack(side="left", padx=12)
            self.buttons.append((btn, desc, frm))

    def set_selected(self, idx):
        self.selected_idx = idx
        self.highlight_selected()

    def highlight_selected(self):
        for i, (btn, desc, frm) in enumerate(self.buttons):
            if i == self.selected_idx:
                btn.config(
                    bg=ACCENT,
                    fg=DARK_BG,
                    activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT
                )
            else:
                btn.config(
                    bg=BTN_BG,
                    fg=BTN_FG,
                    activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT
                )

    def on_up(self, event):
        self.selected_idx = (self.selected_idx - 1) % len(self.difficulties)
        self.highlight_selected()

    def on_down(self, event):
        self.selected_idx = (self.selected_idx + 1) % len(self.difficulties)
        self.highlight_selected()

    def on_enter(self, event):
        self.start(self.difficulties[self.selected_idx]["key"])

    def start(self, difficulty):
        self.menu_win.destroy()
        self.start_callback(difficulty)

    def switch_account(self):
        self.menu_win.destroy()
        self.account_switch_callback()

class SudokuApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sudoku Nexus")
        self.entries = [[None for _ in range(9)] for _ in range(9)]
        self.solved_board = None
        self.difficulty = None
        self.sudoku = None
        self.score_label = None
        self.highscore_label = None
        self.hints_used = 0
        self.mistakes_made = 0
        self.start_time = None
        self.username = None
        self.highscores = {}
        self.bg = DARK_BG
        self.panel = PANEL_BG
        self.fg = FG
        self.paused = False
        self.pause_time = 0
        self.pause_btn = None
        self.pause_overlay = None

        self.root.configure(bg=self.bg)
        self.root.geometry("680x720")
        self.root.resizable(False, False)
        self.create_title()
        self.username = load_username()
        if not self.username:
            UsernameMenu(self.root, self.set_username)
        else:
            self.load_highscores()
            SudokuMenu(self.root, self.start_game, self.username, self.account_switch_menu)

    def set_username(self, username):
        if username:
            self.username = username
            self.load_highscores()
            SudokuMenu(self.root, self.start_game, self.username, self.account_switch_menu)

    def account_switch_menu(self):
        def after_switch(username):
            if username:
                self.username = username
                self.load_highscores()
                SudokuMenu(self.root, self.start_game, self.username, self.account_switch_menu)
            else:
                SudokuMenu(self.root, self.start_game, self.username, self.account_switch_menu)
        AccountSwitchMenu(self.root, after_switch)

    def create_title(self):
        if getattr(self, "title_label", None):
            self.title_label.destroy()
        if getattr(self, "logo_frame", None):
            self.logo_frame.destroy()
        self.logo_frame = tk.Frame(self.root, bg=self.bg)
        self.logo_frame.pack(pady=10)
        # Try to display the logo. If not, show "NEXUS SUDOKU" as title.
        try:
            img = Image.open(LOGO_FILENAME)
            img = img.resize((180, 130), Image.ANTIALIAS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self.logo_frame, image=self.logo_img, bg=self.bg, bd=0)
            logo_label.pack()
            self.title_label = self.logo_frame
        except Exception as e:
            print("Logo not loaded, showing title instead:", e)
            title_label = tk.Label(self.logo_frame, text="NEXUS SUDOKU", font=("Arial", 32, "bold"), bg=self.bg, fg=ACCENT)
            title_label.pack()
            self.title_label = title_label

    def start_game(self, difficulty):
        self.root.deiconify()
        self.difficulty = difficulty
        self.hints_used = 0
        self.mistakes_made = 0
        self.start_time = time.time()
        self.paused = False
        self.init_board()
        self.create_board()
        self.create_controls()
        self.create_score_label()
        self.create_highscore_label()

    def init_board(self):
        full_board = generate_full_board()
        clues = DIFFICULTY_CLUES[self.difficulty]
        puzzle = make_puzzle(full_board, clues)
        self.sudoku = Sudoku(puzzle)
        self.solved_board = None
        self.full_solution = full_board

    def create_board(self):
        if getattr(self, "board_frame", None):
            self.board_frame.destroy()
        self.board_frame = tk.Frame(self.root, bg=self.panel)
        self.board_frame.pack(padx=30, pady=30)
        for i in range(9):
            for j in range(9):
                frame = tk.Frame(
                    self.board_frame,
                    highlightbackground=ACCENT if (i % 3 == 0 and i != 0 or j % 3 == 0 and j != 0) else self.panel,
                    highlightcolor=ACCENT if (i % 3 == 0 and i != 0 or j % 3 == 0 and j != 0) else self.panel,
                    highlightthickness=2 if (i % 3 == 0 and i != 0 or j % 3 == 0 and j != 0) else 1,
                    bd=0,
                    bg=self.panel
                )
                frame.grid(row=i, column=j, padx=(1, 1), pady=(1, 1))
                e = tk.Entry(
                    frame,
                    width=2,
                    font=('Arial', 22, 'bold'),
                    justify='center',
                    relief='ridge',
                    bg=ENTRY_BG,
                    fg=ENTRY_FG,
                    insertbackground=ENTRY_FG,
                    highlightthickness=0,
                    disabledbackground=ENTRY_DISABLED_BG,
                    disabledforeground=ENTRY_DISABLED_FG,
                )
                if self.sudoku.starting_board[i][j] != 0:
                    e.insert(0, str(self.sudoku.starting_board[i][j]))
                    e.config(state='disabled')
                else:
                    e.bind("<FocusIn>", lambda event, x=i, y=j: self.highlight_cell(x, y))
                    e.bind("<FocusOut>", lambda event, x=i, y=j: self.unhighlight_cell(x, y))
                    e.bind("<KeyRelease>", lambda event, x=i, y=j: self.check_user_entry(x, y))
                e.grid(row=0, column=0)
                self.entries[i][j] = e

    def highlight_cell(self, row, col):
        self.entries[row][col].config(bg=ENTRY_HIGHLIGHT_BG)

    def unhighlight_cell(self, row, col):
        self.entries[row][col].config(bg=ENTRY_BG)

    def create_controls(self):
        if getattr(self, "controls", None):
            self.controls.destroy()
        self.controls = tk.Frame(self.root, bg=self.bg)
        self.controls.pack(pady=10)
        solve_btn = tk.Button(self.controls, text="Solve", font=("Arial", 14), command=self.solve_board, width=10,
                              bg=BTN_BG, fg=ACCENT, activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                              relief="flat", bd=0, cursor="hand2")
        solve_btn.grid(row=0, column=0, padx=5)
        hint_btn = tk.Button(self.controls, text="Hint", font=("Arial", 14), command=self.give_hint, width=10,
                             bg=BTN_BG, fg=ACCENT, activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                             relief="flat", bd=0, cursor="hand2")
        hint_btn.grid(row=0, column=1, padx=5)
        reset_btn = tk.Button(self.controls, text="Reset", font=("Arial", 14), command=self.reset_board, width=10,
                              bg=BTN_BG, fg=ACCENT, activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                              relief="flat", bd=0, cursor="hand2")
        reset_btn.grid(row=0, column=2, padx=5)
        new_btn = tk.Button(self.controls, text="New Puzzle", font=("Arial", 14), command=self.new_puzzle, width=10,
                            bg=BTN_BG, fg=ACCENT, activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                            relief="flat", bd=0, cursor="hand2")
        new_btn.grid(row=0, column=3, padx=5)
        self.pause_btn = tk.Button(self.controls, text="Pause", font=("Arial", 14), command=self.toggle_pause, width=10,
                                   bg=BTN_BG, fg=ACCENT, activebackground=BTN_HIGHLIGHT, activeforeground=ACCENT,
                                   relief="flat", bd=0, cursor="hand2")
        self.pause_btn.grid(row=0, column=4, padx=5)

    def show_pause_overlay(self):
        if self.pause_overlay is not None:
            self.pause_overlay.lift()
            self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
            return
        self.pause_overlay = tk.Frame(self.board_frame, bg="#181a20")
        self.pause_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        pause_label = tk.Label(
            self.pause_overlay,
            text="Game Paused",
            font=("Arial", 32, "bold"),
            bg="#181a20",
            fg=ACCENT
        )
        pause_label.place(relx=0.5, rely=0.5, anchor="center")

    def hide_pause_overlay(self):
        if self.pause_overlay is not None:
            self.pause_overlay.destroy()
            self.pause_overlay = None

    def toggle_pause(self):
        if not self.paused:
            self.paused = True
            self.pause_btn.config(text="Resume")
            self.pause_time = time.time()
            for i in range(9):
                for j in range(9):
                    self.entries[i][j].config(state="disabled")
            self.show_pause_overlay()
        else:
            self.paused = False
            self.pause_btn.config(text="Pause")
            self.start_time += time.time() - self.pause_time
            for i in range(9):
                for j in range(9):
                    if self.sudoku.starting_board[i][j] == 0:
                        self.entries[i][j].config(state="normal")
            self.hide_pause_overlay()

    def check_user_entry(self, row, col):
        if self.paused:
            return
        val = self.entries[row][col].get()
        if not val.isdigit() or not (1 <= int(val) <= 9):
            self.entries[row][col].config(bg=ENTRY_WRONG_BG)
            return
        correct = str(self.full_solution[row][col])
        if val == correct:
            self.entries[row][col].config(bg=ENTRY_CORRECT_BG)
            self.entries[row][col].after(400, lambda e=self.entries[row][col]: e.config(bg=ENTRY_BG))
            if self.is_puzzle_complete():
                self.show_score(final=True)
        else:
            self.entries[row][col].config(bg=ENTRY_WRONG_BG)
            self.entries[row][col].after(800, lambda e=self.entries[row][col]: e.config(bg=ENTRY_BG))
            self.entries[row][col].delete(0, tk.END)
            self.mistakes_made += 1
            self.show_score()

    def is_puzzle_complete(self):
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if str(val) != str(self.full_solution[i][j]):
                    return False
        return True

    def solve_board(self):
        if self.paused:
            return
        for i in range(9):
            for j in range(9):
                self.entries[i][j].config(state='normal')
                self.entries[i][j].delete(0, tk.END)
                self.entries[i][j].insert(0, str(self.full_solution[i][j]))
                self.entries[i][j].config(disabledforeground=ACCENT, fg=ACCENT)
        self.show_score(final=True)

    def get_solved_board(self):
        if self.solved_board:
            return self.solved_board
        temp = Sudoku(self.sudoku.starting_board)
        if temp.solve():
            self.solved_board = temp.board
            return self.solved_board
        return None

    def give_hint(self):
        if self.paused:
            return
        solved = self.get_solved_board()
        if not solved:
            messagebox.showinfo("Sudoku", "No solution available for hints!")
            return
        for i in range(9):
            for j in range(9):
                entry_val = self.entries[i][j].get()
                if entry_val == "" or entry_val == "0":
                    self.entries[i][j].config(state='normal')
                    self.entries[i][j].delete(0, tk.END)
                    self.entries[i][j].insert(0, str(solved[i][j]))
                    self.entries[i][j].config(disabledforeground="#0984e3", fg="#0984e3", bg=ENTRY_HINT_BG)
                    self.entries[i][j].after(800, lambda e=self.entries[i][j]: e.config(bg=ENTRY_BG))
                    self.hints_used += 1
                    self.show_score()
                    return
        messagebox.showinfo("Sudoku", "No empty cells left for hints!")

    def show_score(self, final=False):
        if self.start_time is None:
            score = 0
        else:
            elapsed = int(time.time() - self.start_time) if not self.paused else int(self.pause_time - self.start_time)
            base = 1000
            bonus = DIFFICULTY_BONUS[self.difficulty]
            time_penalty = elapsed
            hint_penalty = 100 * self.hints_used
            mistake_penalty = 50 * self.mistakes_made
            score = max(0, base + bonus - time_penalty - hint_penalty - mistake_penalty)
        if getattr(self, "score_label", None):
            try: self.score_label.config(text=f"Score: {score}")
            except tk.TclError: pass
        if final:
            old_high = self.get_highscore()
            if score > old_high:
                self.save_highscore(score)
                hs_msg = f"New High Score for {self.difficulty.title()}!"
            else:
                hs_msg = f"High Score for {self.difficulty.title()}: {old_high}"
            elapsed = int(time.time() - self.start_time) if not self.paused else int(self.pause_time - self.start_time)
            msg = (
                f"Congratulations! Puzzle complete.\n\n"
                f"Difficulty: {self.difficulty.title()}\n"
                f"Your Score: {score}\n"
                f"Time: {elapsed} seconds\n"
                f"Hints Used: {self.hints_used}\n"
                f"Mistakes: {self.mistakes_made}\n"
                f"{hs_msg}"
            )
            messagebox.showinfo("Score Summary", msg)
            self.create_highscore_label()

    def create_score_label(self):
        if getattr(self, "score_label", None):
            self.score_label.destroy()
        self.score_label = tk.Label(self.root, text="Score: 0", font=("Arial", 16),
                                    bg=self.bg, fg=ACCENT)
        self.score_label.pack(pady=2)

    def create_highscore_label(self):
        if getattr(self, "highscore_label", None):
            self.highscore_label.destroy()
        hs = self.get_highscore()
        self.highscore_label = tk.Label(self.root,
            text=f"High Score ({self.difficulty.title()}): {hs}", font=("Arial", 12),
            bg=self.bg, fg=DESC_FG)
        self.highscore_label.pack(pady=1)

    def reset_board(self):
        self.sudoku = Sudoku(self.sudoku.starting_board)
        self.solved_board = None
        self.hints_used = 0
        self.mistakes_made = 0
        self.start_time = time.time()
        self.paused = False
        if getattr(self, "score_label", None):
            try: self.score_label.config(text="Score: 0")
            except tk.TclError: pass
        if getattr(self, "pause_btn", None):
            try: self.pause_btn.config(text="Pause")
            except tk.TclError: pass
        for i in range(9):
            for j in range(9):
                self.entries[i][j].config(state='normal', fg=ENTRY_FG, bg=ENTRY_BG)
                self.entries[i][j].delete(0, tk.END)
                val = self.sudoku.starting_board[i][j]
                if val != 0:
                    self.entries[i][j].insert(0, str(val))
                    self.entries[i][j].config(state='disabled', disabledbackground=ENTRY_DISABLED_BG, disabledforeground=ENTRY_DISABLED_FG)

    def new_puzzle(self):
        self.root.withdraw()
        if getattr(self, "board_frame", None):
            self.board_frame.destroy()
        if getattr(self, "controls", None):
            self.controls.destroy()
        if getattr(self, "score_label", None):
            self.score_label.destroy()
        if getattr(self, "highscore_label", None):
            self.highscore_label.destroy()
        SudokuMenu(self.root, self.start_game, self.username, self.account_switch_menu)

    def update_board_from_entries(self):
        for i in range(9):
            for j in range(9):
                val = self.entries[i][j].get()
                if val.isdigit():
                    self.sudoku.board[i][j] = int(val)
                else:
                    self.sudoku.board[i][j] = 0

    def load_highscores(self):
        if not os.path.exists(HIGHSCORE_FILE):
            self.highscores = {}
        else:
            try:
                with open(HIGHSCORE_FILE, "r") as f:
                    self.highscores = json.load(f)
            except Exception:
                self.highscores = {}
        if self.username not in self.highscores:
            self.highscores[self.username] = {"easy": 0, "medium": 0, "hard": 0}

    def save_highscore(self, score):
        if self.username not in self.highscores:
            self.highscores[self.username] = {"easy": 0, "medium": 0, "hard": 0}
        self.highscores[self.username][self.difficulty] = score
        with open(HIGHSCORE_FILE, "w") as f:
            json.dump(self.highscores, f)

    def get_highscore(self):
        if self.username not in self.highscores:
            return 0
        return self.highscores[self.username].get(self.difficulty, 0)

if __name__ == "__main__":
    root = tk.Tk()
    root.configure(bg=DARK_BG)
    root.geometry("900x850")
    root.resizable(False, False)
    root.withdraw()  # Hide until menu is ready
    app = SudokuApp(root)
    root.mainloop()