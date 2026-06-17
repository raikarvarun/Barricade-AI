import numpy as np

class BarricadeEnv:

    def __init__(self):
        self.size = 9
        self.reset()

    def reset(self):

        self.board = np.zeros((9,9), dtype=np.float32)

        self.blue = [8,4]
        self.red = [0,4]

        self.board[8,4] = 1
        self.board[0,4] = -1

        self.done = False

        return self.get_state()

    def get_state(self):
        return self.board.flatten()

    def legal_moves(self,pos):

        r,c = pos

        moves = []

        dirs = [
            (-1,0),
            (1,0),
            (0,-1),
            (0,1)
        ]

        for dr,dc in dirs:

            nr = r + dr
            nc = c + dc

            if 0 <= nr < 9 and 0 <= nc < 9:
                moves.append((nr,nc))

        return moves

    def step(self,action):

        reward = -0.1

        old_dist = self.blue[0]

        r,c = self.blue

        actions = [
            (-1,0),
            (1,0),
            (0,-1),
            (0,1)
        ]

        dr,dc = actions[action]

        nr = r + dr
        nc = c + dc

        if not (0 <= nr < 9 and 0 <= nc < 9):

            return self.get_state(), -5, False

        self.board[r,c] = 0

        self.blue = [nr,nc]

        self.board[nr,nc] = 1

        new_dist = nr

        reward += old_dist - new_dist

        if nr == 0:
            reward = 100
            self.done = True

        return self.get_state(), reward, self.done