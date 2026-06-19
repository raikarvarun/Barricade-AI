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

        state = self.build_state(board.get_state())

        valid_actions = board.get_valid_actions(
            self.player_id
        )

        if len(valid_actions) == 0:
            return None

        # -----------------------------
        # Exploration
        # -----------------------------
        if random.random() < self.epsilon:

            return random.choice(valid_actions)

        # -----------------------------
        # Exploitation
        # -----------------------------
        q_values = self.shared_agent.predict(state)

        q_values = q_values.clone()

        for action in range(4):

            if action not in valid_actions:

                q_values[action] = -1e9

        return int(q_values.argmax().item())

    #########################################################

    def remember(

        self,

        state,

        action,

        reward,

        next_state,

        done

    ):

        state = self.build_state(state)

        next_state = self.build_state(next_state)

        self.memory.push(

            state,

            action,

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