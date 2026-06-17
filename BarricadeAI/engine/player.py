class Player:
    def __init__(self, board_size):
        self.board_size = board_size
        self.reset()

    def reset(self):
        self.row = self.board_size - 1
        self.col = self.board_size // 2

    def position(self):
        return (self.row, self.col)
    
import numpy as np

UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


class Board:

    def __init__(self, size=9):

        self.size = size

        self.reset()

    #################################################

    def reset(self):

        self.player_row = self.size - 1
        self.player_col = self.size // 2

        return self.get_state()

    #################################################

    def get_state(self):

        return np.array(
            [
                self.player_row / (self.size - 1),
                self.player_col / (self.size - 1),
            ],
            dtype=np.float32,
        )

    #################################################

    def step(self, action):

        reward = -1
        done = False

        old_row = self.player_row
        old_col = self.player_col

        if action == UP:
            self.player_row -= 1

        elif action == DOWN:
            self.player_row += 1

        elif action == LEFT:
            self.player_col -= 1

        elif action == RIGHT:
            self.player_col += 1

        # Wall collision
        if (
            self.player_row < 0
            or self.player_row >= self.size
            or self.player_col < 0
            or self.player_col >= self.size
        ):

            self.player_row = old_row
            self.player_col = old_col

            reward = -5

        # Goal reached
        if self.player_row == 0:

            reward = 100
            done = True

        return self.get_state(), reward, done

    #################################################

    def get_player_position(self):

        return self.player_row, self.player_col