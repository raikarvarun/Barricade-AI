class Player:
    def __init__(self, board_size):
        self.board_size = board_size
        self.reset()

    def reset(self):
        self.row = self.board_size - 1
        self.col = self.board_size // 2

    def position(self):
        return (self.row, self.col)
    
