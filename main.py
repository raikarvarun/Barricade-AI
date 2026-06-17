import pygame
import sys

# ------------------------
# CONFIG
# ------------------------
BOARD_SIZE = 9
CELL_SIZE = 70
MARGIN = 20

BOARD_W = BOARD_SIZE * CELL_SIZE
BOARD_H = BOARD_SIZE * CELL_SIZE

SIDE_PANEL = 250

WIDTH = BOARD_W + SIDE_PANEL + MARGIN * 3
HEIGHT = BOARD_H + MARGIN * 2

BG = (20, 20, 20)
GRID = (70, 70, 70)
WHITE = (240, 240, 240)

BLUE = (40, 120, 255)
RED = (255, 70, 70)


game_over = False
winner = None

pygame.init()

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Barricade GG Prototype")

font = pygame.font.SysFont(None, 28)

# ------------------------
# GAME STATE
# ------------------------
blue_pos = [4, 8]
red_pos = [4, 0]

current_player = "BLUE"

barrier_mode = "H"

horizontal_barriers = []
vertical_barriers = []


# ------------------------
# DRAW BOARD
# ------------------------
def draw_board():

    start_x = MARGIN
    start_y = MARGIN

    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):

            rect = pygame.Rect(
                start_x + col * CELL_SIZE,
                start_y + row * CELL_SIZE,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )

            pygame.draw.rect(screen, (45, 45, 45), rect, border_radius=8)
            pygame.draw.rect(screen, GRID, rect, 2, border_radius=8)

    # Horizontal barriers
    for r, c in horizontal_barriers:

        x = start_x + c * CELL_SIZE
        y = start_y + (r + 1) * CELL_SIZE - 6

        pygame.draw.rect(screen, BARRIER, (x, y, CELL_SIZE * 2, 10))

    # Vertical barriers
    for r, c in vertical_barriers:

        x = start_x + (c + 1) * CELL_SIZE - 6
        y = start_y + r * CELL_SIZE

        pygame.draw.rect(screen, BARRIER, (x, y, 10, CELL_SIZE * 2))


def draw_players():

    start_x = MARGIN
    start_y = MARGIN

    bx = start_x + blue_pos[0] * CELL_SIZE + CELL_SIZE // 2
    by = start_y + blue_pos[1] * CELL_SIZE + CELL_SIZE // 2

    rx = start_x + red_pos[0] * CELL_SIZE + CELL_SIZE // 2
    ry = start_y + red_pos[1] * CELL_SIZE + CELL_SIZE // 2

    pygame.draw.circle(screen, BLUE, (bx, by), 18)
    pygame.draw.circle(screen, RED, (rx, ry), 18)


def draw_possible_moves():

    if current_player == "BLUE":
        row, col = blue_pos
    else:
        row, col = red_pos

    moves = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]
    
    for r, c in moves:

        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:

            rect = pygame.Rect(
                MARGIN + r * CELL_SIZE,
                MARGIN + c * CELL_SIZE,
                CELL_SIZE - 4,
                CELL_SIZE - 4,
            )

            pygame.draw.rect(screen, WHITE, rect, 3, border_radius=8)


def draw_ui():

    panel_x = BOARD_W + MARGIN * 2

    title = font.render("Barricade GG", True, WHITE)
    screen.blit(title, (panel_x, 40))

    turn = font.render(f"Turn: {current_player}", True, WHITE)
    screen.blit(turn, (panel_x, 100))

    mode = font.render(
        f"Barrier: {'Horizontal' if barrier_mode=='H' else 'Vertical'}",
        True,
        WHITE,
    )
    screen.blit(mode, (panel_x, 150))

    help1 = font.render("M = Move", True, WHITE)
    help2 = font.render("H = Horizontal", True, WHITE)
    help3 = font.render("V = Vertical", True, WHITE)

    screen.blit(help1, (panel_x, 240))
    screen.blit(help2, (panel_x, 280))
    screen.blit(help3, (panel_x, 320))

def draw_winner():

    if not game_over:
        return

    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(180)
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))

    text = font.render(f"{winner} WINS!", True, (255, 255, 255))
    rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))

    screen.blit(text, rect)
    
    
# ------------------------
# GAME LOGIC
# ------------------------
def check_winner():
    global game_over, winner

    # blue wins if reaches top row
    if blue_pos[1] == 0:
        game_over = True
        winner = "BLUE"

    # red wins if reaches bottom row
    elif red_pos[1] == BOARD_SIZE - 1:
        game_over = True
        winner = "RED"
        
def switch_turn():
    global current_player

    if current_player == "BLUE":
        current_player = "RED"
    else:
        current_player = "BLUE"


def move_player(r, c):

    global blue_pos, red_pos

    if game_over:
        return
    
    if current_player == "BLUE":
        row, col = blue_pos
    else:
        row, col = red_pos

    legal = [
        (row - 1, col),
        (row + 1, col),
        (row, col - 1),
        (row, col + 1),
    ]

    if (r, c) in legal:

        if current_player == "BLUE":
            blue_pos = [r, c]
        else:
            red_pos = [r, c]

        check_winner()

        if not game_over:
            switch_turn()


# ------------------------
# MAIN LOOP
# ------------------------
running = True

while running:

    screen.fill(BG)

    draw_board()
    draw_possible_moves()
    draw_players()
    draw_ui()
    draw_winner()

    pygame.display.flip()

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_h:
                barrier_mode = "H"

            elif event.key == pygame.K_v:
                barrier_mode = "V"

        elif event.type == pygame.MOUSEBUTTONDOWN:

            mx, my = pygame.mouse.get_pos()

            row = (mx - MARGIN) // CELL_SIZE
            col = (my - MARGIN) // CELL_SIZE

            if 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE:

                move_player(row, col)

pygame.quit()
sys.exit()