import torch
import torch.nn as nn


class DQN(nn.Module):

    def __init__(self, state_size=2, action_size=4):
        super().__init__()

        self.model = nn.Sequential(

            nn.Linear(state_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, 64),
            nn.ReLU(),

            nn.Linear(64, action_size)

        )

    def forward(self, x):
        return self.model(x)