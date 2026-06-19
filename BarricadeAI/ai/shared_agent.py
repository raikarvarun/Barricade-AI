import random

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from ai.network import DQN


class SharedAgent:

    #########################################################

    def __init__(self):

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        print(f"Using device: {self.device}")

        self.model = DQN().to(self.device)

        self.target_model = DQN().to(self.device)

        self.target_model.load_state_dict(self.model.state_dict())

        self.target_model.eval()

        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.criterion = nn.MSELoss()

        self.gamma = 0.99

        self.batch_size = 64

        self.target_update = 1000

        self.train_steps = 0

    #########################################################

    def predict(self, state):

        state = torch.FloatTensor(state).unsqueeze(0).to(self.device)

        with torch.no_grad():

            move_q, wall_q = self.model(state)

        return (move_q.squeeze(0), wall_q.squeeze(0))

    #########################################################

    def train(self, replay_memory):

        if len(replay_memory) < self.batch_size:
            return

        batch = replay_memory.sample(self.batch_size)

        states = np.array([b[0] for b in batch], dtype=np.float32)

        move_actions = np.array([b[1] for b in batch], dtype=np.int64)

        wall_actions = np.array([b[2] for b in batch], dtype=np.int64)

        rewards = np.array([b[3] for b in batch], dtype=np.float32)

        next_states = np.array([b[4] for b in batch], dtype=np.float32)

        dones = np.array([b[5] for b in batch], dtype=np.float32)

        states = torch.FloatTensor(states).to(self.device)

        move_actions = torch.LongTensor(move_actions).to(self.device)

        wall_actions = torch.LongTensor(wall_actions).to(self.device)

        rewards = torch.FloatTensor(rewards).to(self.device)

        next_states = torch.FloatTensor(next_states).to(self.device)

        dones = torch.FloatTensor(dones).to(self.device)

        move_q, wall_q = self.model(states)

        target_move_q, target_wall_q = self.target_model(next_states)

        current_move_q = move_q.gather(1, move_actions.unsqueeze(1)).squeeze()

        next_move_q = target_move_q.max(1)[0]

        move_target = rewards + (1 - dones) * self.gamma * next_move_q

        move_loss = self.criterion(current_move_q, move_target)

        PLACE_WALL = 4

        wall_mask = (move_actions == PLACE_WALL)
        if wall_mask.any():
            current_wall_q = (
                wall_q[wall_mask]
                .gather(1, wall_actions[wall_mask].unsqueeze(1))
                .squeeze()
            )

            next_wall_q = target_wall_q[wall_mask].max(1)[0]

            wall_target = (
                rewards[wall_mask] + (1 - dones[wall_mask]) * self.gamma * next_wall_q
            )
            wall_loss = self.criterion(current_wall_q, wall_target)
        else:
            wall_loss = torch.tensor(0.0, device=self.device)

        loss = move_loss + wall_loss
        self.optimizer.zero_grad()

        loss.backward()

        self.optimizer.step()

        
        
        self.train_steps += 1

        if self.train_steps % self.target_update == 0:

            self.target_model.load_state_dict(self.model.state_dict())

    #########################################################

    def save(self, path):

        torch.save(self.model.state_dict(), path)

    #########################################################

    def load(self, path):

        self.model.load_state_dict(torch.load(path, map_location=self.device))

        self.target_model.load_state_dict(self.model.state_dict())

    def save_checkpoint(self, path, game):

        torch.save(
            {
                "model": self.model.state_dict(),
                "target_model": self.target_model.state_dict(),
                "optimizer": self.optimizer.state_dict(),
                "episode": game.episode,
                "player1_wins": game.player1_wins,
                "player2_wins": game.player2_wins,
                "player1_epsilon": game.player1.epsilon,
                "player2_epsilon": game.player2.epsilon,
                "train_steps": self.train_steps,
                "player1_memory": game.player1.memory.memory,
                "player2_memory": game.player2.memory.memory,
            },
            path,
        )

    def load_checkpoint(self, path, game):
        checkpoint = torch.load(path, map_location=self.device)

        self.model.load_state_dict(checkpoint["model"])

        self.target_model.load_state_dict(checkpoint["target_model"])

        self.optimizer.load_state_dict(checkpoint["optimizer"])

        self.train_steps = checkpoint["train_steps"]

        game.episode = checkpoint["episode"]

        game.player1_wins = checkpoint["player1_wins"]

        game.player2_wins = checkpoint["player2_wins"]

        game.player1.epsilon = checkpoint["player1_epsilon"]

        game.player2.epsilon = checkpoint["player2_epsilon"]
        
        game.player1.memory.memory = checkpoint["player1_memory"]
        
        game.player2.memory.memory = checkpoint["player2_memory"]
