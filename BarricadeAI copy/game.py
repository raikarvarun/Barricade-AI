import pygame
import random

from settings import *
from engine.board import Board
from engine.board import UP, DOWN, LEFT, RIGHT

from ai.agent import Agent

from ui import Button

panel_x = 850



class Game:

    def __init__(self):

        self.btn_start = Button(panel_x, 80, 280, 55, "START")

        self.btn_pause = Button(panel_x, 150, 280, 55, "PAUSE")

        self.btn_reset = Button(panel_x, 220, 280, 55, "RESET")

        self.btn_save = Button(panel_x, 290, 280, 55, "SAVE MODEL")

        self.btn_load = Button(panel_x, 360, 280, 55, "LOAD MODEL")

        self.btn_speed_up = Button(panel_x, 430, 135, 55, "SPEED +")

        self.btn_speed_down = Button(panel_x + 145, 430, 135, 55, "SPEED -")
        
        
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Barricade AI Trainer")

        self.clock = pygame.time.Clock()

        self.running = True

        # Training
        self.training = True

        # Player
        

        self.board = Board(BOARD_SIZE)

        self.episode = 1
        self.steps = 0
        self.reward = 0
        
        self.agent = Agent()

        self.state = self.board.reset()

    ######################################################

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

        # Temporary movement
        # Later DQN will choose actions.

        self.steps += 1

        self.player_row -= 1

        self.reward -= 1

        if self.player_row < 0:

            self.reward += 100

            self.episode += 1

            self.reset_episode()

    ######################################################

    def reset_episode(self):
        self.board.reset()

        self.steps = 0
        self.reward = 0
        
        self.state = self.board.reset()

        self.steps = 0
        self.reward = 0


    ######################################################

    def draw(self):

        self.screen.fill(BACKGROUND)

        self.draw_header()

        self.draw_board()
        
        self.draw_panel()

        pygame.display.flip()

    ######################################################

    def draw_header(self):

        font = pygame.font.SysFont("Arial", 26)

        texts = [

            f"Training : {'ON' if self.training else 'PAUSED'}"

        ]

        y = 20

        for txt in texts:

            surface = font.render(txt, True, WHITE)

            self.screen.blit(surface, (30, y))

            y += 35

    ######################################################
    def draw_panel(self):

        pygame.draw.rect(

            self.screen,

            (35, 35, 35),

            (800, 0, 400, 900)

        )

        self.btn_start.draw(self.screen)

        self.btn_pause.draw(self.screen)

        self.btn_reset.draw(self.screen)

        self.btn_save.draw(self.screen)

        self.btn_load.draw(self.screen)


        font = pygame.font.SysFont("Arial", 24)

        labels = [

            f"Episode : {self.episode}",

            f"Reward : {self.reward}",

            f"Steps : {self.steps}",

            f"Epsilon : {self.agent.epsilon:.3f}"

            

        ]

        y = 520

        for txt in labels:

            surface = font.render(txt, True, (255,255,255))

            self.screen.blit(surface, (840, y))

            y += 35
    def draw_board(self):

        start_x = BOARD_MARGIN
        start_y = 180

        for row in range(BOARD_SIZE):

            for col in range(BOARD_SIZE):

                x = start_x + col * CELL_SIZE
                y = start_y + row * CELL_SIZE

                rect = pygame.Rect(
                    x,
                    y,
                    CELL_SIZE,
                    CELL_SIZE
                )

                pygame.draw.rect(
                    self.screen,
                    GRID_COLOR,
                    rect,
                    2
                )

        # Goal row

        pygame.draw.rect(

            self.screen,

            GOAL_COLOR,

            (
                start_x,
                start_y,
                BOARD_SIZE * CELL_SIZE,
                CELL_SIZE
            ),

            4

        )

        # Player

        row, col = self.board.get_player_position()

        center_x = start_x + col * CELL_SIZE + CELL_SIZE // 2
        center_y = start_y + row * CELL_SIZE + CELL_SIZE // 2

        pygame.draw.circle(

            self.screen,

            PLAYER_COLOR,

            (center_x, center_y),

            CELL_SIZE // 3

        )