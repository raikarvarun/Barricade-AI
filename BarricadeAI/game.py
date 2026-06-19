import pygame
import random

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

        self.title_font = pygame.font.SysFont(
            "Arial",
            32,
            bold=True
        )
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
        self.shared_agent = SharedAgent()

        self.player1 = PlayerAgent(
            self.shared_agent,
            player_id=0
        )

        self.player2 = PlayerAgent(
            self.shared_agent,
            player_id=1
        )
        self.current_player = 0


        self.player1_wins = 0
        self.player2_wins = 0

        self.board = Board()

        self.episode = 1
        self.steps = 0
        self.reward = 0
        
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

                self.agent.save()

                print("Model Saved")

            elif self.btn_load.clicked(event):

                self.agent.load()

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

        state = self.state

        # ---------------------------------------
        # Choose action
        # ---------------------------------------

        action = agent.choose_action(self.board)

        # ---------------------------------------
        # Environment step
        # ---------------------------------------

        next_state, reward, done, winner = self.board.step(
            self.current_player,
            action
        )

        # ---------------------------------------
        # Store transition
        # ---------------------------------------

        agent.remember(
            state,
            action,
            reward,
            next_state,
            done
        )

        # ---------------------------------------
        # Train shared model
        # ---------------------------------------

        agent.train()

        self.state = next_state
        self.reward += reward

        # ---------------------------------------
        # Episode finished
        # ---------------------------------------

        if done:

            if winner == 0:
                self.player1_wins += 1
            else:
                self.player2_wins += 1

            print(
                f"Episode {self.episode} | "
                f"Winner: Player {winner + 1}"
            )

            self.player1.end_episode()
            self.player2.end_episode()

            self.episode += 1

            self.steps = 0
            self.reward = 0

            self.state = self.board.reset()

            self.current_player = 0

            return

        # ---------------------------------------
        # Switch turns
        # ---------------------------------------

        self.current_player = 1 - self.current_player
    
    def environment_step1(self):

        self.steps += 1

        action = self.agent.choose_action(self.state)

        next_state, reward, done = self.board.step(action)

        self.agent.remember(
            self.state,
            action,
            reward,
            next_state,
            done,
        )

        self.agent.train()

        self.state = next_state

        self.reward += reward

        if done:

            print(
                f"Episode {self.episode} "
                f"Epsilon {self.agent.epsilon:.3f}"
            )

            self.episode += 1

            self.state = self.board.reset()

            self.steps = 0
            self.reward = 0
    

        
    def update(self):

        self.steps += 1

        action = self.agent.choose_action(self.state)

        next_state, reward, done = self.board.step(action)

        # End episode if it takes too long
        if self.steps >= MAX_EPISODE_STEPS:
            done = True
            reward -= 100   # Optional penalty
        
        self.agent.remember(
            self.state,
            action,
            reward,
            next_state,
            done,
        )

        self.agent.train()

        self.state = next_state

        self.reward += reward
        
        if done:
            print(
                f"Episode {self.episode} "
                f"Epsilon {self.agent.epsilon:.3f}"
            )
            self.agent.end_episode()
            self.episode += 1
            self.state = self.board.reset()
            self.steps = 0
            self.reward = 0

    ######################################################

    def reset_episode(self):
        self.board.reset()

        self.steps = 0
        self.reward = 0
        
        self.state = self.board.reset()

        self.steps = 0
        self.reward = 0


    ######################################################

    

    def draw_panel(self):

        # Background
        panel_rect = pygame.Rect(800, 0, 400, 900)

        pygame.draw.rect(
            self.screen,
            (35, 35, 35),
            panel_rect
        )

        pygame.draw.line(
            self.screen,
            (70, 70, 70),
            (800, 0),
            (800, 900),
            2
        )

        # Title
        title = self.title_font.render(
            "Barricade AI",
            True,
            (255, 255, 255)
        )

        self.screen.blit(title, (900, 25))

        # Buttons
        self.btn_start.draw(self.screen)
        self.btn_pause.draw(self.screen)
        self.btn_reset.draw(self.screen)
        self.btn_save.draw(self.screen)
        self.btn_load.draw(self.screen)

        # Statistics
        pygame.draw.line(
            self.screen,
            (70, 70, 70),
            (830, 500),
            (1170, 500),
            1
        )
        # labels = [

        #     f"Episode : {game.episode}",

        #     f"Steps : {game.steps}",

        #     f"Turn : Player {game.current_player + 1}",

        #     "",

        #     f"P1 Wins : {game.player1_wins}",

        #     f"P2 Wins : {game.player2_wins}",

        #     "",

        #     f"P1 ε : {game.player1.epsilon:.3f}",

        #     f"P2 ε : {game.player2.epsilon:.3f}",

        #     "",

        #     f"P1 Replay : {len(game.player1.memory)}",

        #     f"P2 Replay : {len(game.player2.memory)}"

        # ]
        stats = [

            ("Episode", self.episode),
            ("P1 Walls", self.board.players[0].walls_remaining),
            ("P2 Walls", self.board.players[1].walls_remaining),
            ("P1 Wins", self.player1_wins),
            ("P2 Wins", self.player2_wins),
            
            
            
            ("Reward", self.reward),
            ("Steps", self.steps),
            ("P1 Epsilon", f"{self.player1.epsilon:.3f}"),
            ("P2 Epsilon", f"{self.player2.epsilon:.3f}"),
            ("Replay Size", len(self.agent.memory)),
            ("Training", "Running" if self.training else "Paused")

        ]

        #y = 520
        y = 30

        for label, value in stats:

            text = self.font.render(
                f"{label:<12}: {value}",
                True,
                (255, 255, 255)
            )

            self.screen.blit(text, (1200, y))

            y += 35
   
    def draw(self):
        self.renderer.draw(self)
        self.draw_panel()
        pygame.display.flip()