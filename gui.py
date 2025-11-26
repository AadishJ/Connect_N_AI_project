import threading
import tkinter as tk
from tkinter import ttk, messagebox
from logic import ConnectN, PLAYER_X, PLAYER_O, EMPTY

CELL_SIZE = 85
BOARD_COLOR = "#1565C0"
EMPTY_COLOR = "#FFFFFF"
BOT_COLOR = "#E53935"    
HUMAN_COLOR = "#FFB300"
PIECE_PADDING = 12
BOARD_SHADOW = "#0D47A1"


class CustomDropdown(tk.Frame):
    """Custom styled dropdown that looks much better than ttk.Combobox"""
    def __init__(self, parent, variable, values, width=120, **kwargs):
        super().__init__(parent, bg="#F5F5F5", **kwargs)
        self.variable = variable
        self.values = values
        self.dropdown_open = False
        
        # Main button
        self.button = tk.Button(self, 
                               textvariable=variable,
                               command=self.toggle_dropdown,
                               font=("Arial", 11),
                               bg="white",
                               fg="#333",
                               relief="solid",
                               borderwidth=2,
                               width=width//10,
                               height=1,
                               anchor="w",
                               padx=15,
                               pady=10,
                               cursor="hand2")
        self.button.pack()
        
        # Arrow indicator
        arrow = tk.Label(self.button, text="▼", font=("Arial", 8), bg="white", fg="#666")
        arrow.place(relx=0.9, rely=0.5, anchor="center")
        
        self.dropdown_menu = None
        
    def toggle_dropdown(self):
        if self.dropdown_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self):
        self.dropdown_open = True
        
        # Create dropdown window
        self.dropdown_menu = tk.Toplevel(self)
        self.dropdown_menu.overrideredirect(True)
        self.dropdown_menu.configure(bg="white", relief="solid", borderwidth=2)
        
        # Position below button
        x = self.button.winfo_rootx()
        y = self.button.winfo_rooty() + self.button.winfo_height()
        self.dropdown_menu.geometry(f"+{x}+{y}")
        
        # Add options
        for value in self.values:
            btn = tk.Button(self.dropdown_menu,
                          text=str(value),
                          command=lambda v=value: self.select_value(v),
                          font=("Arial", 11),
                          bg="white",
                          fg="#333",
                          relief="flat",
                          anchor="w",
                          padx=15,
                          pady=8,
                          width=self.button.cget("width"),
                          cursor="hand2")
            btn.pack(fill="x")
            
            # Hover effect
            btn.bind("<Enter>", lambda e, b=btn: b.configure(bg="#E3F2FD"))
            btn.bind("<Leave>", lambda e, b=btn: b.configure(bg="white"))
        
        # Close on click outside
        self.dropdown_menu.bind("<FocusOut>", lambda e: self.close_dropdown())
        self.dropdown_menu.focus_set()
    
    def close_dropdown(self):
        if self.dropdown_menu:
            self.dropdown_menu.destroy()
            self.dropdown_menu = None
        self.dropdown_open = False
    
    def select_value(self, value):
        self.variable.set(value)
        self.close_dropdown()


class ConnectNGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Connect-N AI Game")
        self.resizable(False, False)
        self.configure(bg="#F5F5F5")

        # --- Title ---
        title_frame = tk.Frame(self, bg="#1565C0", height=60)
        title_frame.grid(row=0, column=0, sticky="ew")
        title_frame.grid_propagate(False)
        
        title_label = tk.Label(title_frame, 
                              text="🎮 Connect-N AI Game 🎮", 
                              font=("Arial", 18, "bold"),
                              bg="#1565C0", 
                              fg="white")
        title_label.pack(expand=True)

        # --- Options panel ---
        options_container = tk.Frame(self, bg="#F5F5F5")
        options_container.grid(row=1, column=0, sticky="ew", padx=20, pady=20)
        
        # Game settings frame
        settings_frame = tk.LabelFrame(options_container, 
                                      text=" Game Settings ",
                                      font=("Arial", 11, "bold"),
                                      bg="#F5F5F5",
                                      fg="#1565C0",
                                      padx=20,
                                      pady=15)
        settings_frame.pack(fill="x", pady=(0, 10))

        # Connect N setting
        n_frame = tk.Frame(settings_frame, bg="#F5F5F5")
        n_frame.grid(row=0, column=0, padx=15, pady=8, sticky="w")
        tk.Label(n_frame, text="Connect N:", font=("Arial", 11, "bold"), 
                bg="#F5F5F5", fg="#333").pack(side="top", anchor="w", pady=(0, 5))
        self.n_var = tk.StringVar(value="4")
        n_dropdown = CustomDropdown(n_frame, self.n_var, [3, 4, 5, 6], width=120)
        n_dropdown.pack(side="top", anchor="w")

        # AI Depth setting
        depth_frame = tk.Frame(settings_frame, bg="#F5F5F5")
        depth_frame.grid(row=0, column=1, padx=15, pady=8, sticky="w")
        tk.Label(depth_frame, text="AI Depth:", font=("Arial", 11, "bold"), 
                bg="#F5F5F5", fg="#333").pack(side="top", anchor="w", pady=(0, 5))
        self.depth_var = tk.StringVar(value="5")
        depth_dropdown = CustomDropdown(depth_frame, self.depth_var, [2, 3, 4, 5, 6, 7, 8, 9, 10], width=120)
        depth_dropdown.pack(side="top", anchor="w")

        # First player setting
        first_frame = tk.Frame(settings_frame, bg="#F5F5F5")
        first_frame.grid(row=0, column=2, padx=15, pady=8, sticky="w")
        tk.Label(first_frame, text="First Player:", font=("Arial", 11, "bold"), 
                bg="#F5F5F5", fg="#333").pack(side="top", anchor="w", pady=(0, 5))
        self.first_var = tk.StringVar(value="human")
        first_dropdown = CustomDropdown(first_frame, self.first_var, ["human", "AI"], width=120)
        first_dropdown.pack(side="top", anchor="w")

        # Control buttons frame
        controls_frame = tk.Frame(options_container, bg="#F5F5F5")
        controls_frame.pack(fill="x")
        
        start_btn = tk.Button(controls_frame, text="▶ START GAME", 
                             command=self.start_game,
                             font=("Arial", 12, "bold"),
                             bg="#4CAF50", fg="white",
                             padx=40, pady=15,
                             relief="flat",
                             cursor="hand2",
                             activebackground="#45a049",
                             activeforeground="white")
        start_btn.pack(side="left", padx=(0, 10))
        
        reset_btn = tk.Button(controls_frame, text="🔄 RESET", 
                             command=self.reset_game,
                             font=("Arial", 12, "bold"),
                             bg="#FF5722", fg="white",
                             padx=40, pady=15,
                             relief="flat",
                             cursor="hand2",
                             activebackground="#E64A19",
                             activeforeground="white")
        reset_btn.pack(side="left")

        # --- Board container with shadow effect ---
        board_container = tk.Frame(self, bg="#F5F5F5")
        board_container.grid(row=2, column=0, padx=20, pady=(0, 20))
        
        # Shadow frame
        shadow_frame = tk.Frame(board_container, bg="#BDBDBD")
        shadow_frame.pack(padx=4, pady=4)
        
        # Canvas for board
        self.canvas = tk.Canvas(shadow_frame, 
                               width=CELL_SIZE * 7, 
                               height=CELL_SIZE * 6, 
                               bg=BOARD_COLOR, 
                               highlightthickness=3,
                               highlightbackground=BOARD_SHADOW)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<Motion>", self.on_hover)

        # --- Status bar ---
        status_frame = tk.Frame(self, bg="#E3F2FD", relief="flat", height=50)
        status_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        status_frame.grid_propagate(False)
        
        self.status = tk.StringVar(value="Click 'START GAME' to begin playing!")
        status_label = tk.Label(status_frame, 
                               textvariable=self.status,
                               font=("Arial", 11, "bold"),
                               bg="#E3F2FD",
                               fg="#1565C0")
        status_label.pack(expand=True)

        # --- Player info ---
        info_frame = tk.Frame(self, bg="#F5F5F5")
        info_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        human_info = tk.Frame(info_frame, bg="#FFF3E0", relief="solid", borderwidth=2)
        human_info.pack(side="left", fill="x", expand=True, padx=(0, 5))
        tk.Label(human_info, text="🟡 YOU (Yellow)", font=("Arial", 11, "bold"),
                bg="#FFF3E0", fg="#F57F17", pady=10).pack()
        
        ai_info = tk.Frame(info_frame, bg="#FFEBEE", relief="solid", borderwidth=2)
        ai_info.pack(side="left", fill="x", expand=True, padx=(5, 0))
        tk.Label(ai_info, text="🔴 AI (Red)", font=("Arial", 11, "bold"),
                bg="#FFEBEE", fg="#C62828", pady=10).pack()

        self.game = None
        self.current_player = None
        self.human_player = None
        self.bot_player = None
        self.running_ai = False
        self.hover_col = None

    # ---------- Game setup ----------
    def start_game(self):
        n = int(self.n_var.get())
        depth = int(self.depth_var.get())
        human_first = (self.first_var.get() == "human")

        bot_player = PLAYER_O if human_first else PLAYER_X
        self.human_player = -bot_player
        self.bot_player = bot_player

        self.game = ConnectN(n=n, search_depth=depth, bot_player=self.bot_player)
        self.current_player = PLAYER_X

        player_name = "You start" if human_first else "AI starts"
        self.status.set(f"🎮 Game started! {player_name} first!")
        self.draw_board()

        if not human_first:
            self.after(500, self.ai_move)

    def reset_game(self):
        self.game = None
        self.hover_col = None
        self.canvas.delete("all")
        self.status.set("Game reset. Click 'START GAME' to begin playing!")

    # ---------- Drawing ----------
    def draw_board(self):
        self.canvas.delete("all")

        # Draw background grid
        for r in range(6):
            for c in range(7):
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                # Draw cell background
                self.canvas.create_rectangle(x1, y1, x2, y2, 
                                            fill=BOARD_COLOR, 
                                            outline=BOARD_SHADOW,
                                            width=2)
                
                # Draw empty slot with 3D effect
                padding = 10
                self.canvas.create_oval(x1 + padding, y1 + padding, 
                                       x2 - padding, y2 - padding, 
                                       fill=EMPTY_COLOR, 
                                       outline="#90CAF9",
                                       width=3)

        # Draw pieces
        if not self.game:
            return

        for r in range(6):
            for c in range(7):
                val = self.game.board[r][c]
                if val == EMPTY:
                    continue
                    
                if val == PLAYER_X:
                    color = BOT_COLOR if self.bot_player == PLAYER_X else HUMAN_COLOR
                elif val == PLAYER_O:
                    color = BOT_COLOR if self.bot_player == PLAYER_O else HUMAN_COLOR
                
                x1, y1 = c * CELL_SIZE, r * CELL_SIZE
                x2, y2 = x1 + CELL_SIZE, y1 + CELL_SIZE
                
                # Draw piece with shadow
                shadow_offset = 3
                self.canvas.create_oval(x1 + PIECE_PADDING + shadow_offset, 
                                       y1 + PIECE_PADDING + shadow_offset, 
                                       x2 - PIECE_PADDING + shadow_offset, 
                                       y2 - PIECE_PADDING + shadow_offset, 
                                       fill="#424242", outline="")
                
                # Draw main piece
                self.canvas.create_oval(x1 + PIECE_PADDING, y1 + PIECE_PADDING, 
                                       x2 - PIECE_PADDING, y2 - PIECE_PADDING, 
                                       fill=color, outline="#212121", width=3)
                
                # Add highlight for 3D effect
                highlight_size = 8
                self.canvas.create_oval(x1 + PIECE_PADDING + highlight_size, 
                                       y1 + PIECE_PADDING + highlight_size,
                                       x1 + PIECE_PADDING + highlight_size * 3,
                                       y1 + PIECE_PADDING + highlight_size * 3,
                                       fill="white", outline="")

    # ---------- Hover effect ----------
    def on_hover(self, event):
        if not self.game or self.running_ai:
            return
        
        col = event.x // CELL_SIZE
        if col < 0 or col >= 7:
            return
        
        if self.hover_col != col:
            self.hover_col = col
            self.draw_board()
            
            # Draw hover indicator
            x1 = col * CELL_SIZE
            x2 = x1 + CELL_SIZE
            self.canvas.create_rectangle(x1, 0, x2, CELL_SIZE * 6,
                                        fill="white", stipple="gray50",
                                        outline="")

    # ---------- Input ----------
    def on_click(self, event):
        if not self.game or self.running_ai:
            return
        col = event.x // CELL_SIZE
        if col < 0 or col >= 7:
            return

        if not self.game.play(col, self.human_player):
            self.status.set("❌ Column full! Choose another column.")
            return

        self.draw_board()
        if self.check_game_end():
            return

        self.current_player *= -1
        self.status.set("🤔 AI is thinking...")
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
        self.status.set("🎯 Your turn! Click a column to play.")

    # ---------- End game ----------
    def check_game_end(self):
        if self.game.check_win(self.game.board, PLAYER_X):
            winner = PLAYER_X
        elif self.game.check_win(self.game.board, PLAYER_O):
            winner = PLAYER_O
        elif self.game.is_draw(self.game.board):
            self.status.set("🤝 It's a draw!")
            messagebox.showinfo("Draw", "The game ended in a draw!")
            return True
        else:
            return False

        if winner == self.human_player:
            msg = "🎉 Congratulations! You win!"
            self.status.set("🏆 YOU WIN! 🏆")
        else:
            msg = "🤖 AI wins this round!"
            self.status.set("💻 AI WINS!")
        
        messagebox.showinfo("Game Over", msg)
        return True


if __name__ == "__main__":
    app = ConnectNGUI()
    app.mainloop()