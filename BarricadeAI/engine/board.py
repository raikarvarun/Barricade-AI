import numpy as np

from engine.barricade import Barricade, BarricadeType
from collections import deque
import random

from dataclasses import dataclass

from dataclasses import field


@dataclass
class Player:

    id: int

    row: int
    col: int

    goal_row: int

    value: int
    walls_remaining: int = 10

    recent_positions: deque = field(default_factory=lambda: deque(maxlen=10))


# Movement actions
UP = 0
DOWN = 1
LEFT = 2
RIGHT = 3
PLACE_WALL = 4


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
        self.wall_action_map = []

        self.build_wall_action_map()

        self.reset()

    #########################################################
    def is_legal_wall_action(self, wall_action):

        wall = self.get_wall_from_action(wall_action)

        if wall is None:
            return False

        row, col, wall_type = wall

        if self.place_barricade(row, col):

            wall = self.barricades[-1]

            self.remove_barricade(wall)

            return True

        return False

    def get_legal_wall_mask(self):
        legal = []

        for index, (row, col, wall_type) in enumerate(self.wall_action_map):

            if self.place_barricade(row, col):

                wall = self.barricades[-1]

                self.remove_barricade(wall)

                legal.append(index)

        return legal

    def get_wall_from_action(self, wall_action):

        if wall_action < 0:
            return None

        if wall_action >= len(self.wall_action_map):
            return None

        return self.wall_action_map[wall_action]

    def build_wall_action_map(self):
        self.wall_action_map.clear()
        # -------------------------
        # Horizontal walls
        # -------------------------
        for row in range(1, self.size, 2):

            for col in range(0, self.size - 2, 2):

                self.wall_action_map.append((row, col, BarricadeType.HORIZONTAL))

        # -------------------------
        # Vertical walls
        # -------------------------
        for row in range(0, self.size - 2, 2):

            for col in range(1, self.size, 2):

                self.wall_action_map.append((row, col, BarricadeType.VERTICAL))

        print("Wall Actions:", len(self.wall_action_map))

    def path_exists(self, start_row, start_col, goal_row):

        visited = set()

        queue = deque()

        queue.append((start_row, start_col))

        visited.add((start_row, start_col))

        while queue:

            row, col = queue.popleft()

            # Goal reached (top row)
            if row == goal_row:
                return True

            for nr, nc in self.neighbors(row, col):

                if (nr, nc) not in visited:

                    visited.add((nr, nc))

                    queue.append((nr, nc))

        return False

    #########################################################
    def shortest_path_length(self, start_row, start_col, goal_row):

        visited = set()

        queue = deque()

        queue.append((start_row, start_col, 0))

        visited.add((start_row, start_col))

        while queue:

            row, col, distance = queue.popleft()

            if row == goal_row:

                return distance

            for nr, nc in self.neighbors(row, col):

                if (nr, nc) not in visited:

                    visited.add((nr, nc))

                    queue.append((nr, nc, distance + 1))

        return 9999

    def neighbors(self, row, col):
        result = []

        directions = [(UP, -2, 0), (DOWN, 2, 0), (LEFT, 0, -2), (RIGHT, 0, 2)]

        for action, dr, dc in directions:

            if not self.can_move_from(row, col, action):
                continue

            target_row = row + dr
            target_col = col + dc

            other = self.get_player_at(target_row, target_col)

            # Normal move
            if other is None:

                result.append((target_row, target_col))

                continue

            # Jump move
            jump_row = target_row + dr
            jump_col = target_col + dc

            if not self.in_bounds(jump_row, jump_col):
                continue

            if not self.can_move_from(target_row, target_col, action):
                continue

            result.append((jump_row, jump_col))

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

    def get_opponent(self, player_id):

        if player_id == 0:
            return self.players[1]
        return self.players[0]

    def place_best_wall(self, player_id):
        player = self.players[player_id]

        if player.walls_remaining <= 0:
            return False

        opponent = self.get_opponent(player_id)

        best_wall = None

        best_score = -1
        for dr in (-2, 0, 2):
            for dc in (-2, 0, 2):

                base_row = opponent.row + dr
                base_col = opponent.col + dc

                # =====================================
                # Horizontal wall
                # =====================================

                h_row = base_row - 1
                h_col = base_col

                if self.place_barricade(h_row, h_col):

                    score = self.shortest_path_length(
                        opponent.row, opponent.col, opponent.goal_row
                    )

                    wall = self.barricades[-1]

                    self.remove_barricade(wall)

                    if score > best_score:

                        best_score = score

                        best_wall = (h_row, h_col)

                # =====================================
                # Vertical wall
                # =====================================

                v_row = base_row
                v_col = base_col - 1

                if self.place_barricade(v_row, v_col):

                    score = self.shortest_path_length(
                        opponent.row, opponent.col, opponent.goal_row
                    )

                    wall = self.barricades[-1]

                    self.remove_barricade(wall)

                    if score > best_score:

                        best_score = score

                        best_wall = (v_row, v_col)
        if best_wall is None:
            return False

        if self.place_barricade(best_wall[0], best_wall[1]):

            player.walls_remaining -= 1

            return True

        return False

    def reset(self):
        self.grid.fill(Board.EMPTY)

        self.barricades.clear()

        self.winner = None

        self.players = [
            Player(
                id=0, row=16, col=8, goal_row=0, value=Board.PLAYER1, walls_remaining=10
            ),
            Player(
                id=1, row=0, col=8, goal_row=16, value=Board.PLAYER2, walls_remaining=10
            ),
        ]

        for player in self.players:
            player.recent_positions.clear()
            self.grid[player.row][player.col] = player.value

        # self.generate_random_maze(20)

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

        return 0 <= row < self.size and 0 <= col < self.size

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

    def place_barricade(self, row, col, owner=-1):

        if self.is_horizontal_slot(row, col):

            if col + 2 >= self.size:
                return False

            wall = Barricade(row, col, BarricadeType.HORIZONTAL, owner)

        elif self.is_vertical_slot(row, col):

            if row + 2 >= self.size:
                return False

            wall = Barricade(row, col, BarricadeType.VERTICAL, owner)

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
        if not self.all_players_have_path():
            self.remove_barricade(wall)

            return False
        if not self.path_exists(
            self.players[0].row, self.players[0].col, self.players[0].goal_row
        ):
            self.remove_barricade(wall)
            return False

        if not self.path_exists(
            self.players[1].row, self.players[1].col, self.players[1].goal_row
        ):
            self.remove_barricade(wall)
            return False
        return True

    def all_players_have_path(self):

        for player in self.players:

            if (
                self.shortest_path_length(player.row, player.col, player.goal_row)
                == 9999
            ):

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

            if not self.can_move_from(player.row, player.col, UP):
                return False

            target_row = player.row - 2

            # Opponent directly ahead?
            other = self.get_player_at(target_row, player.col)

            if other is not None:

                jump_row = player.row - 4

                if jump_row >= 0 and self.can_move_from(target_row, player.col, UP):

                    new_row = jump_row

                else:

                    return False

            else:

                new_row -= 2

        elif action == DOWN:
            if not self.can_move_from(player.row, player.col, DOWN):
                return False
            target_row = player.row + 2

            other = self.get_player_at(target_row, player.col)

            if other is not None:

                jump_row = player.row + 4

                if jump_row < self.size and self.can_move_from(
                    target_row, player.col, DOWN
                ):

                    new_row = jump_row

                else:

                    return False

            else:

                new_row += 2

        elif action == LEFT:
            if not self.can_move_from(player.row, player.col, LEFT):
                return False
            target_col = player.col - 2

            other = self.get_player_at(player.row, target_col)

            if other is not None:

                jump_col = player.col - 4

                if jump_col >= 0 and self.can_move_from(player.row, target_col, LEFT):

                    new_col = jump_col

                else:

                    return False

            else:

                new_col -= 2

        elif action == RIGHT:
            if not self.can_move_from(player.row, player.col, RIGHT):
                return False
            target_col = player.col + 2

            other = self.get_player_at(player.row, target_col)

            if other is not None:

                jump_col = player.col + 4

                if jump_col < self.size and self.can_move_from(
                    player.row, target_col, RIGHT
                ):

                    new_col = jump_col

                else:

                    return False

            else:

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

            if self.can_move_player(player_id, action):
                actions.append(action)

        player = self.players[player_id]

        if player.walls_remaining > 0:
            actions.append(PLACE_WALL)
        return actions

    def get_player_at(self, row, col):

        for player in self.players:

            if player.row == row and player.col == col:

                return player

        return None

    def can_move_player(self, player_id, action):
        player = self.players[player_id]

        row = player.row
        col = player.col

        target_row = row
        target_col = col

        if action == UP:
            target_row -= 2

        elif action == DOWN:
            target_row += 2

        elif action == LEFT:
            target_col -= 2

        elif action == RIGHT:
            target_col += 2

        # Board bounds
        if not self.in_bounds(target_row, target_col):
            return False

        # Wall between cells
        mid_row = (row + target_row) // 2

        mid_col = (col + target_col) // 2

        if self.grid[mid_row][mid_col] == Board.BARRICADE:
            return False

        # Opponent check
        other = self.get_player_at(target_row, target_col)

        if other is None:
            return True

        # Jump logic
        jump_row = target_row
        jump_col = target_col

        if action == UP:
            jump_row -= 2

        elif action == DOWN:
            jump_row += 2

        elif action == LEFT:
            jump_col -= 2

        elif action == RIGHT:
            jump_col += 2

        if not self.in_bounds(jump_row, jump_col):
            return False

        jump_mid_row = (target_row + jump_row) // 2

        jump_mid_col = (target_col + jump_col) // 2

        if self.grid[jump_mid_row][jump_mid_col] == Board.BARRICADE:
            return False

        return True

    def step(self, player_id, move_action, wall_action):
        reward = 0.1
        
        PLACE_WALL = 4
        if move_action == PLACE_WALL:

            player = self.players[player_id]

            if player.walls_remaining <= 0:

                return (self.get_state(), 0, False, None)

            wall = self.get_wall_from_action(wall_action)

            if wall is None:

                return (self.get_state(), -1, False, None)
            row, col, wall_type = wall

            
            

            success = self.place_barricade(row, col, player_id)

            
            
            if not success:

                return (self.get_state(), -3, False, None)
            player.walls_remaining -= 1

            
            reward += 1
            return (self.get_state(), reward, False, None)

        reward = -0.1
        done = False

        player = self.players[player_id]

        # -----------------------------
        # Try to move
        # -----------------------------

        moved = self.move_player(player_id, move_action)

        

        reward -= 0.1
        if not moved:

            reward = -10

            return (self.get_state(), reward, done, None)
        
            
                
            
        # -----------------------------
        # Goal reached?
        # -----------------------------
        if player.row == player.goal_row:

            reward = 100

            done = True

            self.winner = player_id

            return (self.get_state(), reward, done, player_id)

        return (self.get_state(), reward, done, None)

    def get_all_legal_walls(self):
        walls = []

        # -----------------------------
        # Horizontal walls
        # -----------------------------
        for row in range(1, self.size, 2):

            for col in range(0, self.size - 2, 2):

                if self.place_barricade(row, col):

                    wall = self.barricades[-1]

                    self.remove_barricade(wall)

                    walls.append((row, col, BarricadeType.HORIZONTAL))

        # -----------------------------
        # Vertical walls
        # -----------------------------
        for row in range(0, self.size - 2, 2):

            for col in range(1, self.size, 2):

                if self.place_barricade(row, col):

                    wall = self.barricades[-1]

                    self.remove_barricade(wall)

                    walls.append((row, col, BarricadeType.VERTICAL))

        return walls
