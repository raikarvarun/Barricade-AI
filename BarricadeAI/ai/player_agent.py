import random
import numpy as np

from ai.replay_memory import ReplayMemory


class PlayerAgent:

    #########################################################

    def __init__(
        self,
        shared_agent,
        player_id
    ):

        self.shared_agent = shared_agent

        self.player_id = player_id

        self.memory = ReplayMemory()

        self.epsilon = 1.0
        self.epsilon_min = 0.05
        self.epsilon_decay = 0.9999

    #########################################################

    # def build_state(self, board_state):

    #     board_state = board_state.astype(np.float32).flatten()

    #     return np.concatenate(
    #         (
    #             board_state,
    #             np.array(
    #                 [self.player_id],
    #                 dtype=np.float32
    #             )
    #         )
    #     )
    def build_state(self, board):
        me = board.players[
            self.player_id
        ]

        opponent = board.players[
            1 - self.player_id
        ]

        board_state = board.get_state().flatten()

        extra = np.array(

            [

                me.row,
                me.col,

                opponent.row,
                opponent.col,

                me.goal_row,
                opponent.goal_row,

                me.walls_remaining,
                opponent.walls_remaining

            ],

            dtype=np.float32

        )

        return np.concatenate(

            [

                board_state,

                extra

            ]

        )
    
    #########################################################

    def choose_action(self, board):

        state = self.build_state(
            board
        )

        valid_actions = board.get_valid_actions(
            self.player_id
        )
        
        
        legal_wall_ids  = board.get_legal_wall_mask()

        # -----------------------------------
        # Exploration
        # -----------------------------------

        if random.random() < self.epsilon:
            if len(valid_actions) == 0:

                return 0, -1

            move_action = random.choice(
                valid_actions
            )

            if move_action == 4:
                legal_wall_ids = board.get_legal_wall_mask()

                if len(legal_wall_ids) == 0:

                    non_wall_actions = [

                        a for a in valid_actions

                        if a != 4

                    ]

                    if len(non_wall_actions) == 0:

                        return 0, -1

                    return random.choice(
                        non_wall_actions
                    ), -1

                wall_action = random.choice(
                    legal_wall_ids
                )

                return move_action, wall_action
            return move_action, -1

        # -----------------------------------
        # Exploitation
        # -----------------------------------

        move_q, wall_q = self.shared_agent.predict(
            state
        )
        
        move_q = move_q.clone()

        for action in range(5):

            if action not in valid_actions:

                move_q[action] = -1e9

        move_action = int(
            move_q.argmax().item()
        )
        
        if move_action != 4:
            return move_action, -1
        
        legal_wall_ids = board.get_legal_wall_mask()
        if len(legal_wall_ids) == 0:
            move_q[4] = -1e9

            move_action = int(
                move_q.argmax().item()
            )

            return move_action, -1
        
        wall_q = wall_q.clone()

        for wall_id in range(144):

            if wall_id not in legal_wall_ids:

                wall_q[wall_id] = -1e9
        
        
        
        wall_action = int( wall_q.argmax().item() ) 

        return move_action, wall_action

    #########################################################

    def remember(
        self,

        state,

        move_action,

        wall_action,

        reward,

        next_state,

        done

    ):

        self.memory.push(

            state,

            move_action,

            wall_action,

            reward,

            next_state,

            done

        )

    #########################################################

    def train(self):

        self.shared_agent.train(
            self.memory
        )

        

    #########################################################

    def end_episode(self):

        if self.epsilon > self.epsilon_min:

            self.epsilon *= self.epsilon_decay

            if self.epsilon < self.epsilon_min:

                self.epsilon = self.epsilon_min