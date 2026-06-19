import pygame

from settings import *




class Renderer:

    def __init__(self, screen):

        self.screen = screen

        self.font = pygame.font.SysFont("Arial", 24)
        
        
        # (row,col) -> (x,y,width,height)
        self.cell_positions = {}

        self.build_board_layout()

    
    ######################################################

    def build_board_layout(self):

        y = BOARD_MARGIN_Y

        for row in range(BOARD_SIZE):

            x = BOARD_MARGIN_X

            for col in range(BOARD_SIZE):

                if row % 2 == 0 and col % 2 == 0:

                    w = PLAYER_CELL
                    h = PLAYER_CELL

                elif row % 2 == 0:

                    w = BARRICADE_CELL
                    h = PLAYER_CELL

                elif col % 2 == 0:

                    w = PLAYER_CELL
                    h = BARRICADE_CELL

                else:

                    w = BARRICADE_CELL
                    h = BARRICADE_CELL

                self.cell_positions[(row, col)] = (
                    x,
                    y,
                    w,
                    h
                )

                x += w

            if row % 2 == 0:
                y += PLAYER_CELL
            else:
                y += BARRICADE_CELL
    
    ######################################################

    def draw(self, game):

        self.screen.fill(BACKGROUND)
        
        
        #self.draw_header(game)

        self.draw_board(game.board)
        self.draw_players(game.board)
        
        

    ######################################################

    def draw_header(self, game):

        texts = [

            f"Episode : {game.episode}",
            f"Reward  : {game.reward}",
            f"Steps   : {game.steps}",
            f"Epsilon : {game.agent.epsilon:.3f}",

        ]

        y = 20

        for text in texts:

            surface = self.font.render(
                text,
                True,
                WHITE
            )

            self.screen.blit(surface, (30, y))

            y += 30

    ######################################################

    

    

    def draw_board(self, board):

        for row in range(board.size):

            for col in range(board.size):

                x, y, w, h = self.cell_positions[(row, col)]

                rect = pygame.Rect(x, y, w, h)

                ################################################

                if row % 2 == 0 and col % 2 == 0:
                    # Goal row colors
                    modified_color = GRID_COLOR
                    if row == 0:
                        # Light Green
                        modified_color = (1, 26, 66)
                    elif row == 16:
                        # Light Blue
                        modified_color = (2, 66, 1)  

                        
                    pygame.draw.rect(

                        self.screen,

                        modified_color,

                        rect,
                        border_radius=5
                        

                    )

                ################################################

                elif board.grid[row][col] == board.BARRICADE:
                    modi_bari_color = BARRICADE_COLOR
                    for wall in board.barricades:
                        if (row, col) in wall.cells:
                            if wall.owner == 0:
                                modi_bari_color = (
                                    50,
                                    120,
                                    255
                                )
                                
                            elif wall.owner == 1:
                                modi_bari_color = (
                                    50,
                                    220,
                                    50
                                )
                                
                                
                            break
                        
                    pygame.draw.rect(

                        self.screen,

                        modi_bari_color,

                        rect,
                        5,
                        border_radius=8

                    )

        ########################################################

        # row, col = board.get_player_position()

        # x, y, w, h = self.cell_positions[(row, col)]

        # pygame.draw.circle(

        #     self.screen,

        #     PLAYER_COLOR,

        #     (

        #         x + w // 2,

        #         y + h // 2

        #     ),

        #     PLAYER_CELL // 3

        # )
    
    def draw_players(self, board):


        for player in board.players:
            x, y, w, h = self.cell_positions[(player.row, player.col)]

            color = (70, 150, 255) if player.id == 0 else (70, 220, 70)

            pygame.draw.circle(

                self.screen,

                color,

                (

                    x + w // 2,

                    y + h // 2

                ),

                PLAYER_CELL // 3

            )