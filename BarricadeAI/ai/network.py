import torch
import torch.nn as nn


class DQN(nn.Module):

    def __init__(self, state_size=290, action_size=5):

        super().__init__()

        self.model = nn.Sequential(

            nn.Linear(state_size, 256),
            nn.ReLU(),

            nn.Linear(256, 256),
            nn.ReLU(),

            nn.Linear(256, 128),
            nn.ReLU(),

            nn.Linear(128, action_size)

        )

    #########################################################

    def forward(self, x):

        return self.model(x)