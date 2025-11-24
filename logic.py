

import math
import random
from copy import deepcopy

ROWS = 6
COLS = 7
PLAYER_X = 1  # bot
PLAYER_O = -1  # opponent / human
EMPTY = 0


class ConnectN:
    def __init__(self, n=4, search_depth=5, bot_player=PLAYER_X):
        assert 3 <= n <= 6
        self.n = n
        self.rows = ROWS
        self.cols = COLS
        self.depth = search_depth
        self.bot = bot_player
        self.board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

    # ---------- board helpers ----------
    def copy_board(self):
        return deepcopy(self.board)

    def valid_moves(self):
        """Return all columns where a move can be played."""
        return [c for c in range(self.cols) if self.board[0][c] == EMPTY]

    def drop_piece(self, board, col, player):
        """Place a piece in the chosen column."""
        for r in range(self.rows - 1, -1, -1):
            if board[r][col] == EMPTY:
                board[r][col] = player
                return True
        return False

    def undo_piece(self, board, col):
        """Remove the top piece from the chosen column."""
        for r in range(self.rows):
            if board[r][col] != EMPTY:
                board[r][col] = EMPTY
                return

    # ---------- win / draw checks ----------
    def check_win(self, board, player):
        """Check if 'player' has won."""
        n = self.n
        R, C = self.rows, self.cols

        # horizontal
        for r in range(R):
            for c in range(C - n + 1):
                if all(board[r][c + i] == player for i in range(n)):
                    return True
        # vertical
        for c in range(C):
            for r in range(R - n + 1):
                if all(board[r + i][c] == player for i in range(n)):
                    return True
        # diagonal down-right
        for r in range(R - n + 1):
            for c in range(C - n + 1):
                if all(board[r + i][c + i] == player for i in range(n)):
                    return True
        # diagonal up-right
        for r in range(n - 1, R):
            for c in range(C - n + 1):
                if all(board[r - i][c + i] == player for i in range(n)):
                    return True
        return False

    def is_draw(self, board):
        return all(board[0][c] != EMPTY for c in range(self.cols))

    # ---------- evaluation ----------
    def evaluate_window(self, window, player):
        """Score a single list of cells (length n)"""
        opp = PLAYER_X if player == PLAYER_O else PLAYER_O
        score = 0
        count_self = window.count(player)
        count_opp = window.count(opp)
        count_empty = window.count(EMPTY)

        if count_self == self.n:
            score += 100000
        elif count_self == self.n - 1 and count_empty == 1:
            score += 100
        elif count_self == self.n - 2 and count_empty == 2:
            score += 10

        if count_opp == self.n - 1 and count_empty == 1:
            score -= 80  # block opponent

        return score

    def evaluate_board(self, board, player):
        """Heuristic evaluation of current board from 'player' POV."""
        score = 0
        R, C = self.rows, self.cols
        n = self.n

        # center preference
        center_col = C // 2
        center_array = [board[r][center_col] for r in range(R)]
        center_count = center_array.count(player)
        score += center_count * 3

        # horizontal
        for r in range(R):
            row_array = board[r]
            for c in range(C - n + 1):
                window = row_array[c:c + n]
                score += self.evaluate_window(window, player)

        # vertical
        for c in range(C):
            col_array = [board[r][c] for r in range(R)]
            for r in range(R - n + 1):
                window = col_array[r:r + n]
                score += self.evaluate_window(window, player)

        # diagonal down-right
        for r in range(R - n + 1):
            for c in range(C - n + 1):
                window = [board[r + i][c + i] for i in range(n)]
                score += self.evaluate_window(window, player)

        # diagonal up-right
        for r in range(n - 1, R):
            for c in range(C - n + 1):
                window = [board[r - i][c + i] for i in range(n)]
                score += self.evaluate_window(window, player)

        return score

    # ---------- minimax with alpha-beta ----------
    def minimax(self, board, depth, alpha, beta, maximizingPlayer):
        valid_moves = self.valid_moves()
        is_terminal = (
            self.check_win(board, PLAYER_X) or
            self.check_win(board, PLAYER_O) or
            self.is_draw(board)
        )
        if depth == 0 or is_terminal:
            if is_terminal:
                if self.check_win(board, self.bot):
                    return (None, math.inf)
                elif self.check_win(board, -self.bot):
                    return (None, -math.inf)
                else:
                    return (None, 0)
            else:
                return (None, self.evaluate_board(board, self.bot))

        if maximizingPlayer:
            value = -math.inf
            best_col = random.choice(valid_moves)
            for col in valid_moves:
                self.drop_piece(board, col, self.bot)
                new_score = self.minimax(board, depth - 1, alpha, beta, False)[1]
                self.undo_piece(board, col)
                if new_score > value:
                    value = new_score
                    best_col = col
                alpha = max(alpha, value)
                if alpha >= beta:
                    break  # pruning
            return best_col, value
        else:
            value = math.inf
            best_col = random.choice(valid_moves)
            for col in valid_moves:
                self.drop_piece(board, col, -self.bot)
                new_score = self.minimax(board, depth - 1, alpha, beta, True)[1]
                self.undo_piece(board, col)
                if new_score < value:
                    value = new_score
                    best_col = col
                beta = min(beta, value)
                if alpha >= beta:
                    break
            return best_col, value

    # ---------- API ----------
    def find_best_move(self):
        """Return best move (column index 0..6)."""
        valid_moves = self.valid_moves()
        if not valid_moves:
            return None
        best_col, _ = self.minimax(self.board, self.depth, -math.inf, math.inf, True)
        return best_col

    def play(self, col, player=None):
        """Make a move on internal board."""
        if player is None:
            player = self.bot
        return self.drop_piece(self.board, col, player)

    def display(self):
        print()
        for r in range(self.rows):
            print("|", end="")
            for c in range(self.cols):
                cell = self.board[r][c]
                ch = " "
                if cell == PLAYER_X:
                    ch = "X"
                elif cell == PLAYER_O:
                    ch = "O"
                print(ch, end="|")
            print()
        print(" " + " ".join(map(str, range(self.cols))))
        print()

    def game_over(self):
        return self.check_win(self.board, PLAYER_X) or \
               self.check_win(self.board, PLAYER_O) or \
               self.is_draw(self.board)



if __name__ == "__main__":
    print("=== Connect-N (6x7) AI ===")
    try:
        n = int(input("Enter N (3–6): "))
        if not (3 <= n <= 6):
            n = 4
    except ValueError:
        n = 4

    try:
        depth = int(input("Enter AI search depth (default 5, higher = smarter but slower): "))
        if depth < 1:
            depth = 5
    except ValueError:
        depth = 5

    try:
        first = input("Do you want to play first? (y/n): ").strip().lower()
        human_first = (first == "y")
    except:
        human_first = True

    bot_player = PLAYER_O if human_first else PLAYER_X
    game = ConnectN(n=n, search_depth=depth, bot_player=bot_player)

    print(f"\nGame started! Connect {n} on a 6x7 board.")
    print(f"You are {'O' if human_first else 'X'}; AI is {'X' if human_first else 'O'}.\n")

    current_player = PLAYER_X  # X always starts
    while not game.game_over():
        game.display()

        if current_player == game.bot:
            print("AI is thinking...")
            move = game.find_best_move()
            if move is None:
                print("No moves available. Draw!")
                break
            game.play(move, game.bot)
            print(f"AI plays column {move}.")
        else:
            # Human move
            valid = False
            while not valid:
                try:
                    move = int(input("Enter column (0–6): "))
                    if move not in range(7):
                        raise ValueError
                    if not game.play(move, -game.bot):
                        print("Column full. Try again.")
                        continue
                    valid = True
                except ValueError:
                    print("Invalid input. Please enter 0–6.")
        # Switch turns
        current_player *= -1

    game.display()
    # Determine winner
    if game.check_win(game.board, PLAYER_X):
        print("Player X wins!")
    elif game.check_win(game.board, PLAYER_O):
        print("Player O wins!")
    else:
        print("It's a draw!")

