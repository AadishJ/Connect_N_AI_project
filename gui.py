"""
connectn_gui.py
---------------
Graphical interface for Connect-N AI
(using Tkinter, requires connectn_simple_ai.py in same directory)
"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from logic import ConnectN, PLAYER_X, PLAYER_O, EMPTY

CELL_SIZE = 70
BOARD_COLOR = "#1E88E5"
EMPTY_COLOR = "#E3F2FD"
BOT_COLOR = "#D32F2F"     # 🔴 red
HUMAN_COLOR = "#FBC02D"   # 🟡 yellow


class ConnectNGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect-N AI")
        self.resizable(False, False)

        # --- top options ---
        options = ttk.Frame(self, padding=5)
        options.grid(row=0, column=0, sticky="ew")

        ttk.Label(options, text="Connect N:").grid(row=0, column=0)
        self.n_var = tk.IntVar(value=4)
        ttk.Combobox(options, textvariable=self.n_var, values=[3, 4, 5, 6], width=3, state="readonly").grid(row=0, column=1)

        ttk.Label(options, text="AI Depth:").grid(row=0, column=2)
        self.depth_var = tk.IntVar(value=5)
        ttk.Combobox(options, textvariable=self.depth_var, values=[2, 3, 4, 5, 6], width=3, state="readonly").grid(row=0, column=3)

        ttk.Label(options, text="Who plays first:").grid(row=0, column=4)
        self.first_var = tk.StringVar(value="human")
        ttk.Combobox(options, textvariable=self.first_var, values=["human", "AI"], width=6, state="readonly").grid(row=0, column=5)

        ttk.Button(options, text="Start Game", command=self.start_game).grid(row=0, column=6, padx=10)
        ttk.Button(options, text="Reset", command=self.reset_game).grid(row=0, column=7)

        # --- canvas for board ---
        self.canvas = tk.Canvas(self, width=CELL_SIZE * 7, height=CELL_SIZE * 6, bg=BOARD_COLOR, highlightthickness=0)
        self.canvas.grid(row=1, column=0, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_click)

        # --- status bar ---
        self.status = tk.StringVar(value="Click 'Start Game' to begin.")
        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="center").grid(row=2, column=0, sticky="ew", pady=(0, 5))

        self.game = None
        self.current_player = None
        self.human_player = None
        self.bot_player = None
        self.running_ai = False

    # ---------- Game setup ----------
    def start_game(self):
        n = self.n_var.get()
        depth = self.depth_var.get()
        human_first = (self.first_var.get() == "human")

        bot_player = PLAYER_O if human_first else PLAYER_X
        self.human_player = -bot_player
        self.bot_player = bot_player

        self.game = ConnectN(n=n, search_depth=depth, bot_player=self.bot_player)
        self.current_player = PLAYER_X  # X always starts

        self.status.set(f"Game started! You are 🟡 (Yellow). AI is 🔴 (Red).")
        self.draw_board()

        if not human_first:
            self.after(500, self.ai_move)

    def reset_game(self):
        self.game = None
        self.canvas.delete("all")
        self.status.set("Game reset. Click 'Start Game' to begin.")

    # ---------- Drawing ----------
    def draw_board(self):
        self.canvas.delete("all")

        # Draw background circles
        for r in range(6):
            for c in range(7):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_oval(x1 + 5, y1 + 5, x2 - 5, y2 - 5, fill=EMPTY_COLOR, outline="#1565C0")

        # Draw pieces
        if not self.game:
            return

        for r in range(6):
            for c in range(7):
                val = self.game.board[r][c]
                if val == PLAYER_X:
                    color = BOT_COLOR if self.bot_player == PLAYER_X else HUMAN_COLOR
                elif val == PLAYER_O:
                    color = BOT_COLOR if self.bot_player == PLAYER_O else HUMAN_COLOR
                else:
                    continue
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                self.canvas.create_oval(x1 + 8, y1 + 8, x2 - 8, y2 - 8, fill=color, outline="black")

    # ---------- Input ----------
    def on_click(self, event):
        if not self.game or self.running_ai:
            return
        col = event.x // CELL_SIZE
        if col < 0 or col >= 7:
            return

        if not self.game.play(col, self.human_player):
            self.status.set("Column full! Choose another.")
            return

        self.draw_board()
        if self.check_game_end():
            return

        self.current_player *= -1
        self.status.set("AI is thinking...")
        self.after(300, self.ai_move)

    # ---------- AI Turn ----------
    def ai_move(self):
        if not self.game or self.running_ai:
            return

        def think():
            self.running_ai = True
            move = self.game.find_best_move()
            if move is not None:
                self.game.play(move, self.bot_player)
            self.running_ai = False
            self.after(0, self.finish_ai_move)

        threading.Thread(target=think, daemon=True).start()

    def finish_ai_move(self):
        self.draw_board()
        if self.check_game_end():
            return
        self.current_player *= -1
        self.status.set("Your turn.")

    # ---------- End game ----------
    def check_game_end(self):
        if self.game.check_win(self.game.board, PLAYER_X):
            winner = PLAYER_X
        elif self.game.check_win(self.game.board, PLAYER_O):
            winner = PLAYER_O
        elif self.game.is_draw(self.game.board):
            self.status.set("It's a draw!")
            messagebox.showinfo("Draw", "The game is a draw!")
            return True
        else:
            return False

        if winner == self.human_player:
            msg = "You win! 🎉"
        else:
            msg = "AI wins! 🤖"
        self.status.set(msg)
        messagebox.showinfo("Game Over", msg)
        return True


if __name__ == "__main__":
    app = ConnectNGUI()
    app.mainloop()
