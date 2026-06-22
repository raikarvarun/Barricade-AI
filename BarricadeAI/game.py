import pygame
import random
import torch

from settings import *
from engine.board import Board
from engine.board import UP, DOWN, LEFT, RIGHT

from ai.agent import Agent


from ui import Button

panel_x = 850
from ai.shared_agent import SharedAgent
from ai.player_agent import PlayerAgent


from engine.renderer import Renderer


class Game:

    def __init__(self):

        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.font = pygame.font.SysFont("Arial", 24)

        self.btn_start = Button(panel_x, 80, 280, 55, "START")

        self.btn_pause = Button(panel_x, 150, 280, 55, "PAUSE")

        self.btn_reset = Button(panel_x, 220, 280, 55, "RESET")

        self.btn_save = Button(panel_x, 290, 280, 55, "SAVE MODEL")

        self.btn_load = Button(panel_x, 360, 280, 55, "LOAD MODEL")

        self.btn_speed_up = Button(panel_x, 430, 135, 55, "SPEED +")

        self.btn_speed_down = Button(panel_x + 145, 430, 135, 55, "SPEED -")

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Barricade AI Trainer")

        self.renderer = Renderer(self.screen)

        self.clock = pygame.time.Clock()

        self.running = True

        # Training
        self.training = True

        # Player
        self.player1_network = SharedAgent()

        self.player2_network = SharedAgent()

        self.player1 = PlayerAgent(self.player1_network, 0)

        self.player2 = PlayerAgent(self.player2_network, 1)
        self.current_player = 0

        self.player1_wins = 0
        self.player2_wins = 0
        self.draw_games= 0 

        self.board = Board()

        self.episode = 1
        self.steps = 0

        self.reward_player1 = 0
        self.reward_player2 = 0

        self.agent = Agent()

        self.state = self.board.reset()

        self.shared_agent = SharedAgent()

    ######################################################
    def get_current_agent(self):
        if self.current_player == 0:
            return self.player1

        return self.player2

    def run(self):

        while self.running:

            self.events()

            if self.training:
                self.environment_step()

            self.draw()

            self.clock.tick(FPS)

    ######################################################

    def events(self):

        for event in pygame.event.get():

            if self.btn_start.clicked(event):

                self.training = True

            elif self.btn_pause.clicked(event):

                self.training = False

            elif self.btn_reset.clicked(event):

                self.reset_episode()

            elif self.btn_save.clicked(event):

                self.save_stats("stats.pth")
                self.player1_network.save_players("player1.pth")
                self.player2_network.save_players("player2.pth")
                print("Model Saved")

            elif self.btn_load.clicked(event):

                self.player1_network.load_players("player1.pth")
                self.player2_network.load_players("player2.pth")

                self.load_stats("stats.pth")

                print("Model Loaded")

            elif self.btn_speed_up.clicked(event):

                self.move_delay = max(10, self.move_delay - 20)

            elif self.btn_speed_down.clicked(event):

                self.move_delay += 20

            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:
                    self.running = False

                elif event.key == pygame.K_SPACE:
                    self.training = not self.training

                elif event.key == pygame.K_r:
                    self.reset_episode()

    ######################################################

    def environment_step(self):

        self.steps += 1

        # ---------------------------------------
        # Current player
        # ---------------------------------------

        if self.current_player == 0:
            agent = self.player1
        else:
            agent = self.player2

        agent = self.get_current_agent()
        state = agent.build_state(self.board)
        # ---------------------------------------
        # Choose action
        # ---------------------------------------

        move_action, wall_action = agent.choose_action(self.board)

        # ---------------------------------------
        # Environment step
        # ---------------------------------------

        next_state, reward, done, winner = self.board.step(
            self.current_player, move_action, wall_action
        )

        next_state = agent.build_state(self.board)
        if self.steps >= 501:
            self.reward_player1 = -100
            self.reward_player2 = -100
            reward = -100
            done = True

            winner = -1
        # ---------------------------------------
        # Store transition
        # ---------------------------------------

        agent.remember(state, move_action, wall_action, reward, next_state, done)

        # ---------------------------------------
        # Train shared model
        # ---------------------------------------

        agent.train()

        self.state = next_state

        if self.current_player == 0:
            self.reward_player1 += reward
        else:

            self.reward_player2 += reward

        # ---------------------------------------
        # Episode finished
        # ---------------------------------------

        if done:
            loser_agent = None
            if winner != -1:
                if winner == 0:
                    self.player1_wins += 1
                    loser_agent = self.player2
                else:
                    self.player2_wins += 1
                    loser_agent = self.player1
            else:
                if self.current_player == 0:
                    loser_agent = self.player2
                else:
                    loser_agent = self.player1
                self.draw_games += 1

            if loser_agent is not None:
                loser_state = loser_agent.build_state(self.board)

                loser_agent.remember(
                    loser_state,
                    0,  # dummy action
                    -1,  # dummy wall action
                    -100,
                    loser_state,
                    True,
                )

            print(f"Episode {self.episode} | " f"Winner: Player {winner + 1}")

            self.player1.end_episode()
            self.player2.end_episode()

            self.episode += 1

            self.state = self.board.reset()
            self.steps = 0
            self.reward_player1 = 0
            self.reward_player2 = 0

            # Auto save every 10 episodes
            if self.episode % 10 == 0:
                self.save_stats(f"saves/{self.episode}_stats.pth")
                self.player1_network.save_players(f"saves/{self.episode}_player1.pth")
                self.player2_network.save_players(f"saves/{self.episode}_player2.pth")

            self.current_player = 0

            return

        # ---------------------------------------
        # Switch turns
        # ---------------------------------------

        self.current_player = 1 - self.current_player

    def load_stats(self, path):
        stats = torch.load("stats.pth", weights_only=False)
        self.episode = stats["episode"]

        self.player1_wins = stats["player1_wins"]

        self.player2_wins = stats["player2_wins"]

        self.player1.epsilon = stats["player1_epsilon"]

        self.player2.epsilon = stats["player2_epsilon"]

        self.player1.memory.memory = stats["player1_memory"]

        self.player2.memory.memory = stats["player2_memory"]

    def save_stats(self, path):

        torch.save(
            {
                "episode": self.episode,
                "player1_wins": self.player1_wins,
                "player2_wins": self.player2_wins,
                "player1_epsilon": self.player1.epsilon,
                "player2_epsilon": self.player2.epsilon,
                "player1_memory": self.player1.memory.memory,
                "player2_memory": self.player2.memory.memory,
            },
            path,
        )

    ######################################################

    def reset_episode(self):
        self.board.reset()

        self.steps = 0
        self.reward_player1 = 0
        self.reward_player2 = 0

        self.state = self.board.reset()

        self.reward_player1 = 0
        self.reward_player2 = 0

    ######################################################

    def draw_panel(self):

        # Background
        panel_rect = pygame.Rect(800, 0, 400, 900)

        pygame.draw.rect(self.screen, (35, 35, 35), panel_rect)

        pygame.draw.line(self.screen, (70, 70, 70), (800, 0), (800, 900), 2)

        # Title
        title = self.title_font.render("Barricade AI", True, (255, 255, 255))

        self.screen.blit(title, (900, 25))

        # Buttons
        self.btn_start.draw(self.screen)
        self.btn_pause.draw(self.screen)
        self.btn_reset.draw(self.screen)
        self.btn_save.draw(self.screen)
        self.btn_load.draw(self.screen)

        # Statistics
        pygame.draw.line(self.screen, (70, 70, 70), (830, 500), (1170, 500), 1)

        stats = [
            ("Episode", self.episode),
            ("P1 Walls", self.board.players[0].walls_remaining),
            ("P2 Walls", self.board.players[1].walls_remaining),
            ("P1 Wins", self.player1_wins),
            ("P2 Wins", self.player2_wins),
            ("Draws", self.draw_games),
            ("Reward player1", self.reward_player1),
            ("Steps", self.steps),
            ("P1 Epsilon", f"{self.player1.epsilon:.3f}"),
            ("P2 Epsilon", f"{self.player2.epsilon:.3f}"),
            ("Training", "Running" if self.training else "Paused"),
        ]

        # y = 520
        y = 30

        for label, value in stats:

            text = self.font.render(f"{label:<12}: {value}", True, (255, 255, 255))

            self.screen.blit(text, (1200, y))

            y += 35

    def draw(self):
        self.renderer.draw(self)
        self.draw_panel()
        pygame.display.flip()
