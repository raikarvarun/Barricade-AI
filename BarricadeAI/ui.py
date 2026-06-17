import pygame


class Button:

    def __init__(self, x, y, w, h, text):

        self.rect = pygame.Rect(x, y, w, h)

        self.text = text

        self.font = pygame.font.SysFont("Arial", 24)

    def draw(self, screen):

        mouse = pygame.mouse.get_pos()

        color = (70, 70, 70)

        if self.rect.collidepoint(mouse):
            color = (100, 100, 100)

        pygame.draw.rect(screen, color, self.rect, border_radius=10)

        pygame.draw.rect(screen, (220, 220, 220), self.rect, 2, border_radius=10)

        txt = self.font.render(self.text, True, (255, 255, 255))

        screen.blit(
            txt,
            txt.get_rect(center=self.rect.center)
        )

    def clicked(self, event):

        if event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                return self.rect.collidepoint(event.pos)

        return False