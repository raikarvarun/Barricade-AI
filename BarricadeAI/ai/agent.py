import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from ai.network import DQN
from ai.replay_memory import ReplayMemory


class Agent:

    def __init__(self):

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.policy_net = DQN().to(self.device)
        self.target_net = DQN().to(self.device)

        self.target_net.load_state_dict(
            self.policy_net.state_dict()
        )

        self.optimizer = optim.Adam(
            self.policy_net.parameters(),
            lr=0.001,
        )

        self.loss_fn = nn.MSELoss()

        self.memory = ReplayMemory()

        self.gamma = 0.99

        self.epsilon = 1.0
        self.epsilon_decay = 0.995
        self.epsilon_min = 0.02

        self.batch_size = 64

        self.action_size = 4

        self.update_counter = 0

    #################################################

    def choose_action(self, state):

        if random.random() < self.epsilon:
            return random.randint(0, self.action_size - 1)

        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():
            q = self.policy_net(state)

        return q.argmax().item()

    #################################################

    def remember(
        self,
        state,
        action,
        reward,
        next_state,
        done,
    ):

        self.memory.push(
            state,
            action,
            reward,
            next_state,
            done,
        )

    #################################################

    def train(self):

        if len(self.memory) < self.batch_size:
            return

        batch = self.memory.sample(self.batch_size)

        states = torch.FloatTensor(
            np.array([b[0] for b in batch])
        ).to(self.device)

        actions = torch.LongTensor(
            [b[1] for b in batch]
        ).unsqueeze(1).to(self.device)

        rewards = torch.FloatTensor(
            [b[2] for b in batch]
        ).to(self.device)

        next_states = torch.FloatTensor(
            np.array([b[3] for b in batch])
        ).to(self.device)

        dones = torch.FloatTensor(
            [b[4] for b in batch]
        ).to(self.device)

        current_q = self.policy_net(states).gather(
            1,
            actions,
        ).squeeze()

        with torch.no_grad():

            next_q = self.target_net(
                next_states
            ).max(1)[0]

        target_q = rewards + (
            1 - dones
        ) * self.gamma * next_q

        loss = self.loss_fn(
            current_q,
            target_q,
        )

        self.optimizer.zero_grad()

        loss.backward()

        self.optimizer.step()

        self.update_counter += 1

        if self.update_counter % 100 == 0:

            self.target_net.load_state_dict(
                self.policy_net.state_dict()
            )

        if self.epsilon > self.epsilon_min:

            self.epsilon *= self.epsilon_decay

    #################################################

    def save(self, filename="model.pth"):

        torch.save(
            self.policy_net.state_dict(),
            filename,
        )

    #################################################

    def load(self, filename="model.pth"):

        self.policy_net.load_state_dict(
            torch.load(
                filename,
                map_location=self.device,
            )
        )

        self.target_net.load_state_dict(
            self.policy_net.state_dict()
        )