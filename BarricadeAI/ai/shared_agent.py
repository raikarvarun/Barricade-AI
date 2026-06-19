import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from ai.network import DQN


class SharedAgent:

    #########################################################

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        print(f"Using device: {self.device}")

        self.model = DQN().to(self.device)

        self.target_model = DQN().to(self.device)

        self.target_model.load_state_dict(
            self.model.state_dict()
        )

        self.target_model.eval()

        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=0.001
        )

        self.criterion = nn.MSELoss()

        self.gamma = 0.99

        self.batch_size = 64

        self.target_update = 1000

        self.train_steps = 0

    #########################################################

    def predict(self, state):

        state = torch.FloatTensor(
            state
        ).unsqueeze(0).to(self.device)

        with torch.no_grad():

            q_values = self.model(state)

        return q_values.squeeze(0)

    #########################################################

    def train(self, replay_memory):

        if len(replay_memory) < self.batch_size:
            return

        batch = replay_memory.sample(
            self.batch_size
        )

        states = np.array(
            [b[0] for b in batch],
            dtype=np.float32
        )

        actions = np.array(
            [b[1] for b in batch]
        )

        rewards = np.array(
            [b[2] for b in batch],
            dtype=np.float32
        )

        next_states = np.array(
            [b[3] for b in batch],
            dtype=np.float32
        )

        dones = np.array(
            [b[4] for b in batch],
            dtype=np.float32
        )

        states = torch.FloatTensor(
            states
        ).to(self.device)

        actions = torch.LongTensor(
            actions
        ).to(self.device)

        rewards = torch.FloatTensor(
            rewards
        ).to(self.device)

        next_states = torch.FloatTensor(
            next_states
        ).to(self.device)

        dones = torch.FloatTensor(
            dones
        ).to(self.device)

        current_q = self.model(states).gather(
            1,
            actions.unsqueeze(1)
        ).squeeze()

        with torch.no_grad():

            next_q = self.target_model(
                next_states
            ).max(1)[0]

        target_q = rewards + (
            1 - dones
        ) * self.gamma * next_q

        loss = self.criterion(
            current_q,
            target_q
        )

        self.optimizer.zero_grad()

        loss.backward()

        self.optimizer.step()

        self.train_steps += 1

        if self.train_steps % self.target_update == 0:

            self.target_model.load_state_dict(
                self.model.state_dict()
            )

    #########################################################

    def save(self, path):

        torch.save(
            self.model.state_dict(),
            path
        )

    #########################################################

    def load(self, path):

        self.model.load_state_dict(
            torch.load(
                path,
                map_location=self.device
            )
        )

        self.target_model.load_state_dict(
            self.model.state_dict()
        )