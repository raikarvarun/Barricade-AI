import torch
import torch.nn as nn


class DQN(nn.Module):

    def __init__(self, state_size=297, move_actions=5, wall_actions=144):

        super().__init__()

        self.backbone = nn.Sequential(
            nn.Linear(state_size, 256),
            nn.ReLU(),
            nn.Linear(256, 256),
            nn.ReLU(),
            nn.Linear(256, 128),
            nn.ReLU(),
        )

        self.move_head = nn.Linear(128, move_actions)

        self.wall_head = nn.Linear(128, wall_actions)

    #########################################################

    def forward(self, x):

        features = self.backbone(x)

        move_q = self.move_head(features)

        wall_q = self.wall_head(features)

        return move_q, wall_q
