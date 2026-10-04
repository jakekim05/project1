import tkinter as tk
from tkinter import ttk

class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Omok++ Gui")
        self.width = 600
        self.height = 660
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)

        self.wins = 0
        self.losses = 0
        self.draws = 0

        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        ttk.Label(self.control_frame, text="Opponent:").pack(side=tk.LEFT, padx=5)
        self.opp_var = tk.StringVar(value="RandomPlayer")
        self.opp_combo = ttk.Combobox(self.control_frame, textvariable=self.opp_var, values=["HumanPlayer", "RandomPlayer", "SimplePlayer"], state="readonly", width=12)
        self.opp_combo.pack(side=tk.LEFT, padx=5)

        self.start_btn = ttk.Button(self.control_frame, text="Start Game", command=self.on_start_clicked)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.score_label = ttk.Label(self.control_frame, text="Wins: 0 | Losses: 0 | Draws: 0")
        self.score_label.pack(side=tk.RIGHT, padx=5)

        self.canvas = tk.Canvas(self, width=self.width, height=600, bg='white')
        self.canvas.pack()
        self.d = 30
        self.side = 600 - 2 * self.d
        self.box = self.side / 19
        self.canvas.create_rectangle(self.d, self.d, self.d + self.side, self.d + self.side, outline='black', width=2)
        for i in range(19):
            t = self.d + self.box / 2 + i * self.box
            self.canvas.create_line(self.d + self.box / 2, t, self.d + self.side - self.box / 2, t, fill='black', width=1)
            self.canvas.create_line(t, self.d + self.box / 2, t, self.d + self.side - self.box / 2, fill='black', width=1)

        self.game = None
        
    def draw_stone(self, row, col, color):
        x = self.d + self.box / 2 + col * self.box
        y = self.d + self.box / 2 + row * self.box
        radius = self.box / 2 * 0.9
        if color == 0:
            fill_color = 'black'
        else:
            fill_color = 'white'
        return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill_color, outline='black')

    def get_position(self):
        x, y = 0, 0
        flag = tk.BooleanVar(master=self)

        def on_click(event):
            nonlocal x, y
            x, y = event.x, event.y
            flag.set(True)

        binding = self.canvas.bind("<Button-1>", on_click)
        self.wait_variable(flag)
        self.canvas.unbind("<Button-1>", binding)

        if self.d <= x <= self.d + self.side and self.d <= y <= self.d + self.side:
            col = int((x - self.d) / self.box)
            row = int((y - self.d) / self.box)
            return row, col
        return None
    
    def update_score(self, result):
        if result == "win":
            self.wins += 1
        elif result == "loss":
            self.losses += 1
        else:
            self.draws += 1
        self.score_label.config(text=f"Wins: {self.wins} | Losses: {self.losses} | Draws: {self.draws}")
        
        self.opp_combo.pack(side=tk.LEFT, padx=5)
        self.start_btn.pack(side=tk.LEFT, padx=5)

    def on_start_clicked(self):
        from gamemanager import GameManager
        
        self.opp_combo.pack_forget()
        self.start_btn.pack_forget()

        self.canvas.delete("all")
        self.canvas.create_rectangle(self.d, self.d, self.d + self.side, self.d + self.side, outline='black', width=2)
        for i in range(19):
            t = self.d + self.box / 2 + i * self.box
            self.canvas.create_line(self.d + self.box / 2, t, self.d + self.side - self.box / 2, t, fill='black', width=1)
            self.canvas.create_line(t, self.d + self.box / 2, t, self.d + self.side - self.box / 2, fill='black', width=1)

        opp_name = self.opp_var.get()
        if opp_name == "HumanPlayer":
            opp_cls = HumanPlayer
        elif opp_name == "RandomPlayer":
            opp_cls = RandomPlayer
        else:
            opp_cls = SimplePlayer

        player1 = HumanPlayer(0)
        player2 = opp_cls(1)

        self.game = GameManager(player1, player2)
        self.run_turn()

    def run_turn(self):
        if self.game.whos_win() == -1:
            try:
                self.game.start_turn(-1)
            except Exception:
                pass
            
            if self.game.whos_win() == -1:
                self.after(10, self.run_turn)
            else:
                self.handle_game_over()
        else:
            self.handle_game_over()

    def handle_game_over(self):
        winner = self.game.whos_win()
        if winner == 0:
            result = "win"
        elif winner == 1:
            result = "loss"
        else:
            result = "draw"

        self.update_score(result)

gui = Gui()

from humanplayer import HumanPlayer
from randomplayer import RandomPlayer
from simpleplayer import SimplePlayer

if __name__ == "__main__":
    gui.mainloop()