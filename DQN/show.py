def draw_board(screen, env):

    for row in range(9):
        for col in range(9):

            rect = pygame.Rect(
                col * 70 + 20,
                row * 70 + 20,
                60,
                60
            )

            pygame.draw.rect(screen, (60,60,60), rect, 2)

            if [row,col] == env.blue:
                pygame.draw.circle(
                    screen,
                    (50,150,255),
                    rect.center,
                    20
                )

            elif [row,col] == env.red:
                pygame.draw.circle(
                    screen,
                    (255,80,80),
                    rect.center,
                    20
                )
                
def draw_q_values(screen, q):

    font = pygame.font.SysFont(None, 30)

    labels = [
        f"UP    : {q[0]:.2f}",
        f"DOWN  : {q[1]:.2f}",
        f"LEFT  : {q[2]:.2f}",
        f"RIGHT : {q[3]:.2f}"
    ]

    for i, txt in enumerate(labels):

        img = font.render(
            txt,
            True,
            (255,255,255)
        )

        screen.blit(
            img,
            (700,150 + i*40)
        )
        
font = pygame.font.SysFont(None, 30)

screen.blit(
    font.render(
        f"Episode: {episode}",
        True,
        (255,255,255)
    ),
    (700,20)
)

screen.blit(
    font.render(
        f"Epsilon: {epsilon:.3f}",
        True,
        (255,255,255)
    ),
    (700,60)
)

screen.blit(
    font.render(
        f"Win Rate: {win_rate:.1f}%",
        True,
        (255,255,255)
    ),
    (700,100)
)

pygame.time.delay(100)