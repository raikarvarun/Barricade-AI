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
        self.epsilon_decay = 0.995

    #########################################################

    def build_state(self, board_state):

        board_state = board_state.astype(np.float32).flatten()

        return np.concatenate(
            (
                board_state,
                np.array(
                    [self.player_id],
                    dtype=np.float32
                )
            )
        )

    #########################################################

    def choose_action(self, board):

        state = self.build_state(
            board.get_state()
        )

        valid_actions = board.get_valid_actions(
            self.player_id
        )

        candidate_walls = board.get_candidate_walls(
            self.player_id
        )

        # -----------------------------------
        # Exploration
        # -----------------------------------

        if random.random() < self.epsilon:

            move_action = random.choice(
                valid_actions
            )

            if move_action == 4:

                if len(candidate_walls) == 0:

                    return random.choice(
                        [a for a in valid_actions if a != 4]
                    ), -1

                wall_action = random.randint(
                    0,
                    len(candidate_walls) - 1
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
        
        if len(candidate_walls) == 0:
            fallback = move_q.clone()

            fallback[4] = -1e9

            move_action = int(
                fallback.argmax().item()
            )

            return move_action, -1
        
        wall_q = wall_q.clone()

        wall_q[len(candidate_walls):] = -1e9
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

        state = self.build_state(state)

        next_state = self.build_state(next_state)

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