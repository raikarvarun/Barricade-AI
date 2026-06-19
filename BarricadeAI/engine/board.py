import numpy as np

from engine.barricade import Barricade, BarricadeType
from collections import deque
import random

from dataclasses import dataclass

@dataclass
class Player:

    id: int

    row: int
    col: int

    goal_row: int

    value: int
# Movement actions
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3


class Board:

    EMPTY = 0

    PLAYER1 = 1

    PLAYER2 = 2

    BARRICADE = 3

    def __init__(self):

        # Logical board
        self.size = 17

        # Grid stores occupancy only
        self.grid = np.zeros((self.size, self.size), dtype=np.int8)

        self.barricades = []
        self.players = []

        self.current_player = 0

        self.winner = None

        self.reset()

    
    #########################################################

    def path_exists(self, start_row, start_col):

        visited = set()

        queue = deque()

        queue.append((start_row, start_col))

        visited.add((start_row, start_col))

        while queue:

            row, col = queue.popleft()

            # Goal reached (top row)
            if row == 0:
                return True

            for nr, nc in self.neighbors(row, col):

                if (nr, nc) not in visited:

                    visited.add((nr, nc))

                    queue.append((nr, nc))

        return False
    #########################################################

    def neighbors(self, row, col):

        result = []

        if self.can_move_from(row, col, UP):
            result.append((row - 2, col))

        if self.can_move_from(row, col, DOWN):
            result.append((row + 2, col))

        if self.can_move_from(row, col, LEFT):
            result.append((row, col - 2))

        if self.can_move_from(row, col, RIGHT):
            result.append((row, col + 2))

        return result

    #########################################################

    def can_move_from(self, row, col, action):

        if action == UP:

            if row == 0:
                return False

            if self.grid[row - 1][col] == Board.BARRICADE:
                return False

            return True

        elif action == DOWN:

            if row == self.size - 1:
                return False

            if self.grid[row + 1][col] == Board.BARRICADE:
                return False

            return True

        elif action == LEFT:

            if col == 0:
                return False

            if self.grid[row][col - 1] == Board.BARRICADE:
                return False

            return True

        elif action == RIGHT:

            if col == self.size - 1:
                return False

            if self.grid[row][col + 1] == Board.BARRICADE:
                return False

            return True

        return False
    
    #########################################################
    def load_test_board(self):
        # -----------------------------
        # Manual barricades
        # -----------------------------
        self.place_barricade(13, 4)
        self.place_barricade(13, 0)
        self.place_barricade(13, 8)
        
        
    #########################################################

    def generate_random_maze(self, wall_count=15):

        attempts = 0
        placed = 0
        max_attempts = wall_count * 20

        while placed < wall_count and attempts < max_attempts:

            attempts += 1

            if random.choice([True, False]):
                # Horizontal wall
                row = random.randrange(1, self.size - 1, 2)
                col = random.randrange(0, self.size - 2, 2)
            else:
                # Vertical wall
                row = random.randrange(0, self.size - 2, 2)
                col = random.randrange(1, self.size - 1, 2)

            if self.place_barricade(row, col):
                placed += 1
        
    def reset(self):
        self.grid.fill(Board.EMPTY)

        self.barricades.clear()

        self.winner = None

        self.players = [

            Player(
                id=0,
                row=16,
                col=8,
                goal_row=0,
                value=Board.PLAYER1
            ),

            Player(
                id=1,
                row=0,
                col=8,
                goal_row=16,
                value=Board.PLAYER2
            )

        ]

        for player in self.players:

            self.grid[player.row][player.col] = player.value

        self.generate_random_maze(20)

        return self.get_state()

    #########################################################
    def get_player(self, player_id):

        return self.players[player_id]
    
    def get_state(self):

        return self.grid.copy()

    #########################################################

    # def get_player_position(self):

    #     return self.player_row, self.player_col

    #########################################################

    def in_bounds(self, row, col):

        return (
            0 <= row < self.size and
            0 <= col < self.size
        )
    #########################################################

    def is_empty(self, row, col):

        return self.grid[row][col] == Board.EMPTY

    #########################################################

    def barricade_exists(self, row, col):

        if not self.in_bounds(row, col):
            return False

        return self.grid[row][col] == Board.BARRICADE
    
    #########################################################

    def can_place_cells(self, cells):

        for r, c in cells:

            if not self.in_bounds(r, c):
                return False

            if not self.is_empty(r, c):
                return False

        return True
    
    #########################################################


    def crosses_existing_wall(self, row, col, wall_type):

        if wall_type == BarricadeType.HORIZONTAL:

            center = (row, col + 1)

        else:

            center = (row + 1, col)

        for wall in self.barricades:

            if wall.type == wall_type:
                continue

            if center in wall.intersections():
                return True

        return False
    
    #########################################################
    
    def is_player_cell(self, row, col):

        return row % 2 == 0 and col % 2 == 0

    #########################################################

    def is_vertical_slot(self, row, col):

        return row % 2 == 0 and col % 2 == 1

    #########################################################

    def is_horizontal_slot(self, row, col):

        return row % 2 == 1 and col % 2 == 0

    #########################################################
    def remove_barricade(self, wall):

        for r, c in wall.cells:

            self.grid[r][c] = Board.EMPTY

        if wall in self.barricades:
            self.barricades.remove(wall)
    
    
    def place_barricade(self, row, col):

        if self.is_horizontal_slot(row, col):

            if col + 2 >= self.size:
                return False

            wall = Barricade(
                row,
                col,
                BarricadeType.HORIZONTAL,
            )

        elif self.is_vertical_slot(row, col):

            if row + 2 >= self.size:
                return False

            wall = Barricade(
                row,
                col,
                BarricadeType.VERTICAL,
            )

        else:
            return False

        if not self.can_place_cells(wall.cells):
            return False

        if self.crosses_existing_wall(
            row,
            col,
            wall.type,
        ):
            return False

        for r, c in wall.cells:

            self.grid[r][c] = Board.BARRICADE

        self.barricades.append(wall)
        # Ensure a path still exists
        if not self.path_exists(self.players[0].row,self.players[0].col):
            self.remove_barricade(wall)
            return False

        if not self.path_exists(self.players[1].row,self.players[1].col):
            self.remove_barricade(wall)
            return False
        return True

    #########################################################
    def move_player(self, player_id, action):
        player = self.players[player_id]

        row, col = player.row, player.col

        new_row, new_col = row, col

        # -----------------------------
        # Compute target position
        # -----------------------------
        if action == UP:
            new_row -= 2

        elif action == DOWN:
            new_row += 2

        elif action == LEFT:
            new_col -= 2

        elif action == RIGHT:
            new_col += 2

        # -----------------------------
        # Bounds check
        # -----------------------------
        if not self.in_bounds(new_row, new_col):
            return False

        # -----------------------------
        # Wall check (barricade in between)
        # -----------------------------
        mid_row = (row + new_row) // 2
        mid_col = (col + new_col) // 2

        if self.grid[mid_row][mid_col] == Board.BARRICADE:
            return False

        # -----------------------------
        # Collision check (other player)
        # -----------------------------
        for p in self.players:

            if p.id != player_id:

                if p.row == new_row and p.col == new_col:
                    return False

        # -----------------------------
        # Move update
        # -----------------------------
        self.grid[row][col] = Board.EMPTY

        player.row = new_row
        player.col = new_col

        self.grid[new_row][new_col] = player.value

        return True
    
    
    def get_valid_actions(self, player_id):

        player = self.players[player_id]

        actions = []

        for action in (UP, DOWN, LEFT, RIGHT):

            row = player.row
            col = player.col

            new_row = row
            new_col = col

            if action == UP:
                new_row -= 2

            elif action == DOWN:
                new_row += 2

            elif action == LEFT:
                new_col -= 2

            elif action == RIGHT:
                new_col += 2

            # -----------------------------
            # Bounds
            # -----------------------------
            if not self.in_bounds(new_row, new_col):
                continue

            # -----------------------------
            # Wall
            # -----------------------------
            mid_row = (row + new_row) // 2
            mid_col = (col + new_col) // 2

            if self.grid[mid_row][mid_col] == Board.BARRICADE:
                continue

            # -----------------------------
            # Other player
            # -----------------------------
            blocked = False

            for p in self.players:

                if p.id != player_id:

                    if p.row == new_row and p.col == new_col:

                        blocked = True
                        break

            if blocked:
                continue

            actions.append(action)

        return actions
    # def can_move(self, action):

    #     row = self.player_row
    #     col = self.player_col

    #     if action == UP:

    #         if row == 0:
    #             return False

    #         if self.grid[row - 1][col] == Board.BARRICADE:
    #             return False

    #         return True

    #     elif action == DOWN:

    #         if row == 16:
    #             return False

    #         if self.grid[row + 1][col] == Board.BARRICADE:
    #             return False

    #         return True

    #     elif action == LEFT:

    #         if col == 0:
    #             return False

    #         if self.grid[row][col - 1] == Board.BARRICADE:
    #             return False

    #         return True

    #     elif action == RIGHT:

    #         if col == 16:
    #             return False

    #         if self.grid[row][col + 1] == Board.BARRICADE:
    #             return False

    #         return True

    #     return False

    #########################################################

    # def move(self, action):

    #     if not self.can_move(action):
    #         return False

    #     self.grid[self.player_row][self.player_col] = Board.EMPTY

    #     if action == UP:
    #         self.player_row -= 2

    #     elif action == DOWN:
    #         self.player_row += 2

    #     elif action == LEFT:
    #         self.player_col -= 2

    #     elif action == RIGHT:
    #         self.player_col += 2

    #     self.grid[self.player_row][self.player_col] = Board.PLAYER

    #     return True

    #########################################################

    # def reached_goal(self):

    #     return self.player_row == 0

    #########################################################

    # def step(self, action):

    #     reward = -1
    #     done = False

    #     moved = self.move(action)

    #     if not moved:
    #         reward = -5

    #     if self.reached_goal():
            
    #         reward = 100
    #         done = True

    #     return self.get_state(), reward, done
    
    def step(self, player_id, action):

        reward = -1
        done = False

        player = self.players[player_id]

        # -----------------------------
        # Try to move
        # -----------------------------
        moved = self.move_player(
            player_id,
            action
        )

        if not moved:

            reward = -5

            return (
                self.get_state(),
                reward,
                done,
                None
            )

        # -----------------------------
        # Goal reached?
        # -----------------------------
        if player.row == player.goal_row:

            reward = 100

            done = True

            self.winner = player_id

            return (
                self.get_state(),
                reward,
                done,
                player_id
            )

        return (
            self.get_state(),
            reward,
            done,
            None
        )