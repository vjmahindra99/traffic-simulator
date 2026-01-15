# PyGame traffic simulator launcher
import os
import sys
import math
import pygame
from fixed_atlas.fixed_atlas import main as run_fixed_sim
from smart_atlas.smart_atlas import main as run_density_sim
from atlas.atlas import main as run_atlas_sim

# Button settings for UI
def draw_button(
    screen,
    rect,
    top_text,
    bottom_text,
    top_font,
    bottom_font,
    base_color,
    hover_color,
    mouse_pos,
):
    
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(screen, color, rect, border_radius=10)

    # Render text surfaces
    top_surf = top_font.render(top_text, True, (255, 255, 255))
    bottom_surf = bottom_font.render(bottom_text, True, (240, 240, 240))

    # Button positions
    top_rect = top_surf.get_rect(center=(rect.centerx, rect.centery - 12))
    bottom_rect = bottom_surf.get_rect(center=(rect.centerx, rect.centery + 18))

    screen.blit(top_surf, top_rect)
    screen.blit(bottom_surf, bottom_rect)

def draw_button_quit(screen, rect, text, font, base_color, hover_color, mouse_pos):
    color = hover_color if rect.collidepoint(mouse_pos) else base_color
    pygame.draw.rect(screen, color, rect, border_radius=10)

    text_surf = font.render(text, True, (255, 255, 255))
    text_rect = text_surf.get_rect(center=rect.center)
    screen.blit(text_surf, text_rect)

# Main menu function
def main_menu():

    # Centered window
    os.environ["SDL_VIDEO_CENTERED"] = "1"

    while True:

        # Initialize PyGame
        pygame.init()

        # Directory for assests
        base_dir = os.path.dirname(__file__)
        font_dir = os.path.join(base_dir, "assets", "fonts")
        asset_dir = os.path.join(base_dir, "assets")

        # Window setup
        width, height = 900, 650
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Traffic Simulator")
        clock = pygame.time.Clock()

        # Pygame window icon
        icon_path = os.path.join(asset_dir, "icon.png")
        window_icon = pygame.image.load(icon_path).convert_alpha()
        pygame.display.set_icon(window_icon)

        # Hide system cursor
        pygame.mouse.set_visible(False)

        # Load cursor icon
        cursor_path = os.path.join(asset_dir, "cursor.png")
        cursor_img = pygame.image.load(cursor_path).convert_alpha()
        cursor_img = pygame.transform.scale(cursor_img, (45, 45))

        # Mute button assets
        sound_on_path = os.path.join(asset_dir, "sound_on.png")
        sound_off_path = os.path.join(asset_dir, "sound_off.png")

        sound_on_img = pygame.image.load(sound_on_path).convert_alpha()
        sound_off_img = pygame.image.load(sound_off_path).convert_alpha()

        sound_on_img = pygame.transform.scale(sound_on_img, (36, 36))
        sound_off_img = pygame.transform.scale(sound_off_img, (36, 36))

        # Mute button position
        mute_button = pygame.Rect(15, 15, 36, 36)

        # Music state
        music_muted = False

        # Initialize mixer
        pygame.mixer.init()

        # Load background music
        music_path = os.path.join(base_dir, "assets", "bg_music.mp3")
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1) # play on loop
        pygame.mixer.music.set_volume(0.05) # volume

        # Load background image
        bg_img_path = os.path.join(asset_dir, "background_image.jpg")
        background_img = pygame.image.load(bg_img_path)
        background_img = pygame.transform.scale(background_img, (width, height))
    
        # Load traffic light images
        light_img_path1 = os.path.join(asset_dir, "traffic_icon_red.png")
        light_img_path2 = os.path.join(asset_dir, "traffic_icon_green.png")
        traffic_light1 = pygame.image.load(light_img_path1)
        traffic_light2 = pygame.image.load(light_img_path2)
        traffic_light1 = pygame.transform.scale(traffic_light1, (200, 250))
        traffic_light2 = pygame.transform.scale(traffic_light2, (200, 250))

        # Button sounds
        hover_sound_path = os.path.join(base_dir, "assets", "sound_hover.mp3")
        hover_sound = pygame.mixer.Sound(hover_sound_path)
        hover_sound.set_volume(0.1) # volume

        # Colour profile for buttons
        fixed_base = (220, 80, 80) # light red
        fixed_hover = (255, 110, 110)

        density_base = (220, 170, 50) # light yellow
        density_hover = (240, 190, 80)

        atlas_base = (80, 200, 120) # light green
        atlas_hover = (100, 235, 150)

        quit_base = (90, 90, 90) # grey
        quit_hover = (110, 110, 110)

        # Text font paths
        font_button = os.path.join(font_dir, "Anton-Regular.ttf")
        font_bold = os.path.join(font_dir, "LuckiestGuy-Regular.ttf")
        font_foot = os.path.join(font_dir, "VT323-Regular.ttf")

        # Text fonts
        title_font = pygame.font.Font(font_bold, 72)
        subtitle_font = pygame.font.Font(font_foot, 32)

        button_title_font = pygame.font.Font(font_button, 36)
        button_sub_font = pygame.font.Font(font_button, 20)

        quit_font = pygame.font.Font(font_button, 26)

        music_label_font = pygame.font.Font(font_foot, 18)

        # Button rectangles & spacing
        button_width = 350
        button_height = 80
        quit_button_width = 150
        quit_button_height = 50
        spacing = 20

        # Button positions
        y_offset = 25
        center_x = width // 2
        first_y  = height // 2 - button_height - spacing + y_offset
        second_y = height // 2 + y_offset
        third_y  = height // 2 + button_height + spacing + y_offset
        quit_y = height - 115

        # Button sizes
        fixed_button = pygame.Rect(0, 0, button_width, button_height)
        fixed_button.center = (center_x, first_y)

        density_button = pygame.Rect(0, 0, button_width, button_height)
        density_button.center = (center_x, second_y)

        atlas_button = pygame.Rect(0, 0, button_width, button_height)
        atlas_button.center = (center_x, third_y)

        quit_button = pygame.Rect(0, 0, quit_button_width, quit_button_height)
        quit_button.center = (center_x, quit_y)

        # Simualtion modes state
        chosen_mode = None  # "fixed" or "density" or "atlas"

        # Button hover state
        hover_fixed = False
        hover_density = False
        hover_atlas = False
        hover_quit = False
        hover_mute = False
        running = True
    
        # Button logic
        while running:

            mouse_pos = pygame.mouse.get_pos()

            # Hover sound for MUTE button
            if mute_button.collidepoint(mouse_pos):
                if not hover_mute:
                    hover_sound.play()
                hover_mute = True
            else:
                hover_mute = False

            # Hover effect for MUTE button
            if mute_button.collidepoint(mouse_pos):
                pygame.draw.rect(screen, (0, 0, 0), mute_button, 2, border_radius=6)

            # Hover sound for FIXED button
            if fixed_button.collidepoint(mouse_pos):
                if not hover_fixed:
                    hover_sound.play()
                hover_fixed = True
            else:
                hover_fixed = False

            # Hover sound for SMART button
            if density_button.collidepoint(mouse_pos):
                if not hover_density:
                    hover_sound.play()
                hover_density = True
            else:
                hover_density = False

            # Hover sound for ATLAS button
            if atlas_button.collidepoint(mouse_pos):
                if not hover_atlas:
                    hover_sound.play()
                hover_atlas = True
            else:
                hover_atlas = False

            # Hover sound for QUIT button
            if quit_button.collidepoint(mouse_pos):
                if not hover_quit:
                    hover_sound.play()
                hover_quit = True
            else:
                hover_quit = False

            # Game exit logic
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:

                    # Mute button click
                    if mute_button.collidepoint(event.pos):
                        music_muted = not music_muted
                        pygame.mixer.music.set_volume(0.0 if music_muted else 0.05)
                        continue

                    # Choose simulation mode
                    if fixed_button.collidepoint(event.pos):
                        chosen_mode = "fixed"
                        running = False
                    elif density_button.collidepoint(event.pos):
                        chosen_mode = "density"
                        running = False
                    elif atlas_button.collidepoint(event.pos):
                        chosen_mode = "atlas"
                        running = False
                    elif quit_button.collidepoint(event.pos):
                        pygame.quit()
                        sys.exit()

            # Background image
            screen.blit(background_img, (0, 0))

            # Title text
            title_surf = title_font.render("Traffic Simulator", True, (0, 0, 0))
            title_rect = title_surf.get_rect(center=(width // 2, 95))
            screen.blit(title_surf, title_rect)

            # Subtitle text
            subtitle_text = "Choose simulation mode:"
            subtitle_surf = subtitle_font.render(subtitle_text, True, (0, 0, 0))
            subtitle_rect = subtitle_surf.get_rect(center=(width // 2, 170))
            screen.blit(subtitle_surf, subtitle_rect)

            # Draw traffic lights on both sides
            left_x  = center_x - button_width // 2 - 235
            right_x = center_x + button_width // 2 + 40
            middle_y = height // 2 - 100

            # Hover animation for traffic lights
            elapsed = pygame.time.get_ticks() / 1000.0
            hover_amplitude = 8 # max pixels up/down
            hover_speed = 2.0 # oscillations per second
            hover_offset = math.sin(elapsed * hover_speed) * hover_amplitude

            screen.blit(traffic_light1, (left_x, middle_y + hover_offset))
            screen.blit(traffic_light2, (right_x, middle_y - hover_offset))

            # Buttons text & style
            draw_button(
                screen,
                fixed_button,
                "Classic",
                "Fixed-time",
                button_title_font,
                button_sub_font,
                fixed_base,
                fixed_hover,
                mouse_pos,
            )

            draw_button(
                screen,
                density_button,
                "Smart",
                "Rule-based Density",
                button_title_font,
                button_sub_font,
                density_base,
                density_hover,
                mouse_pos,
            )

            draw_button(
                screen,
                atlas_button,
                "ATLAS",
                "YOLO-based Density",
                button_title_font,
                button_sub_font,
                atlas_base,
                atlas_hover,
                mouse_pos,
            )

            draw_button_quit(
                screen,
                quit_button,
                "Quit",
                quit_font,
                quit_base,
                quit_hover,
                mouse_pos,
            )

            # Footer background
            footer_bg_width = 550
            footer_bg_height = 45

            footer_bg = pygame.Surface((footer_bg_width, footer_bg_height), pygame.SRCALPHA)
            pygame.draw.rect(footer_bg, (255, 255, 255, 130), (0, 0, footer_bg_width, footer_bg_height), border_radius=18)
            footer_bg_rect = footer_bg.get_rect(center=(width // 2, height - 50))
            screen.blit(footer_bg, footer_bg_rect)

            # Footer text
            footer_text = "Click a button to start or quit to exit"
            footer_surf = subtitle_font.render(footer_text, True, (0, 0, 0))
            footer_rect = footer_surf.get_rect(center=(width // 2, height - 50))
            screen.blit(footer_surf, footer_rect)

            # Draw mute button
            icon = sound_off_img if music_muted else sound_on_img
            screen.blit(icon, mute_button)

            if mute_button.collidepoint(mouse_pos):
                center = mute_button.center
                radius = mute_button.width // 2 + 4
                pygame.draw.circle(screen, (255, 255, 255), center, radius, 2)

            # Music status label
            label_text = "Music: OFF" if music_muted else "Music: ON"
            label_color = (200, 0, 0) if music_muted else (0, 120, 0)

            label_surf = music_label_font.render(label_text, True, label_color)
            label_rect = label_surf.get_rect(
                midleft=(mute_button.right + 8, mute_button.centery)
            )
            screen.blit(label_surf, label_rect)

            # Draw custom cursor
            mouse_x, mouse_y = pygame.mouse.get_pos()
            screen.blit(cursor_img, (mouse_x, mouse_y))

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

        # Launch chosen simulator
        if chosen_mode == "fixed":
            run_fixed_sim()
        elif chosen_mode == "density":
            run_density_sim()
        elif chosen_mode == "atlas":
            run_atlas_sim()
            # print("ATLAS Simulator")
        else:
            break # quit simulator

if __name__ == "__main__":
    main_menu()