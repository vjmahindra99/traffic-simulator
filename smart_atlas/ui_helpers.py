# UI utilities
import pygame

# Button functions
def draw_small_button(screen, rect, text, font, base_color, hover_color, mouse_pos):

    if rect.collidepoint(mouse_pos):
        color = hover_color
    else:
        color = base_color

    pygame.draw.rect(screen, color, rect, border_radius=8)
    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)