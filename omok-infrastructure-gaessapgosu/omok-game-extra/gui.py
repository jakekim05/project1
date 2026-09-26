import tkinter as tk
class Gui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Omok++ Gui")
        self.width = 1200
        self.height = 800
        self.geometry(f"{self.width}x{self.height}")
        self.resizable(False, False)
        self.canvas = tk.Canvas(self, width=self.width, height=self.height, bg='white')
        self.canvas.pack()
        self.d = 20
        self.side = self.height - 2 * self.d
        self.box = self.side / 19
        self.canvas.create_rectangle(self.d, self.d, self.d + self.side, self.d + self.side, outline='black', width=2)
        for i in range(19):
            t = self.d + self.box / 2 + i * self.box
            self.canvas.create_line(self.d + self.box / 2, t, self.d + self.side - self.box / 2, t, fill='black', width=1)
            self.canvas.create_line(t, self.d + self.box / 2, t, self.d + self.side - self.box / 2, fill='black', width=1)

    def draw_stone(self, row, col, color):
        x = self.d + self.box / 2 + col * self.box
        y = self.d + self.box / 2 + row * self.box
        radius = self.box / 2 * 0.9
        if color == 0:
            fill_color = 'black'
        else:
            fill_color = 'white'
        return self.canvas.create_oval(x - radius, y - radius, x + radius, y + radius, fill=fill_color, outline='black')

    def get_position(self, event):
        x, y = event.x, event.y
        if self.d <= x <= self.d + self.side and self.d <= y <= self.d + self.side:
            col = int((x - self.d) / self.box)
            row = int((y - self.d) / self.box)
            return row, col
        return None

if __name__ == "__main__":
    test_gui = Gui()
    test_gui.bind("<Button-1>", lambda event: test_gui.draw_stone(*test_gui.get_position(event), 0))
    test_gui.mainloop()