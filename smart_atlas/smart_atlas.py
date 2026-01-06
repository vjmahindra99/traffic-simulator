# PyGame mainframe, UI & Summary Pop-up for smart traffic simulation
import os
import sys
import pygame
import threading
from . import settings
from .ui_helpers import draw_small_button
from .export_stats import export_stats_to_xlsx, sec_to_min_sec
from .controller import init_signals, signal_controller, generate_vehicles
from .stats_window import start_stats_window, pump_stats_window, close_stats_window
from .run_summary import append_run_summary

# Simulation main function
def main():

    # Reset settings for every new simulation
    settings.reset_for_new_run()
    
    # Initialize PyGame library
    pygame.init()

    # Asset directory
    asset_dir = os.path.join(os.path.dirname(__file__), "assets")

    # Background music
    music_path = os.path.join(asset_dir, "bg_music.mp3")

    # Initialize mixer
    pygame.mixer.init()
    
    # Load background music
    pygame.mixer.music.load(music_path)
    pygame.mixer.music.set_volume(0.05)
    pygame.mixer.music.play(-1)

    # Initialize traffic signal objects & settings
    init_signals()

    # Background thread for traffic light controller
    t_ctrl = threading.Thread(target=signal_controller, daemon=True)
    t_ctrl.start()

    # Background thread for spawning vehicles
    t_generate = threading.Thread(target=generate_vehicles, daemon=True)
    t_generate.start()

    # RGB colour definitions
    black = (0, 0, 0)
    white = (255, 255, 255)
    
    # PyGame window size
    screen_width = 1400
    screen_height = 800
    screen_size = (screen_width, screen_height)

    # Street layout image
    background_path = os.path.join(asset_dir, "street_background.png")
    background = pygame.image.load(background_path)
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption("[SMART] Density-based Traffic Simulation")

    # Start side stats window
    start_stats_window()

    # Cursor icon
    pygame.mouse.set_visible(False)
    cursor_path = os.path.join(asset_dir, "cursor.png")
    cursor_img = pygame.image.load(cursor_path).convert_alpha()
    cursor_img = pygame.transform.scale(cursor_img, (45, 45))
    
    # Signal light images
    red_signal = pygame.image.load(os.path.join(settings.base_path, "assets", "signals", "red.png"))
    yellow_signal = pygame.image.load(os.path.join(settings.base_path, "assets", "signals", "yellow.png"))
    green_signal = pygame.image.load(os.path.join(settings.base_path, "assets", "signals", "green.png"))
    
    # UI text font sizes
    font_dir = os.path.join(os.path.dirname(__file__), "assets", "fonts")
    font_bold = os.path.join(font_dir, "LuckiestGuy-Regular.ttf")
    timer_font_path = os.path.join(font_dir, "Anton-Regular.ttf")

    font = pygame.font.Font(None, 30)
    big_font = pygame.font.Font(None, 40)
    title_font = pygame.font.Font(font_bold, 33)
    timer_font = pygame.font.Font(timer_font_path, 25)

    # FPS counter font style
    fps_font = pygame.font.Font(None, 20)
    fps_value = 0.0

    # Back button UI
    back_button_width = 110
    back_button_height = 36
    back_button = pygame.Rect(0, 0, back_button_width, back_button_height)
    back_button.bottomright = (screen_width - 20, screen_height - 20)
    back_base = (60, 60, 60)
    back_hover = (110, 110, 110)
    back_font = pygame.font.Font(None, 26)

    # Simulation clock
    clock = pygame.time.Clock()

    # Mute button assets
    sound_on_path = os.path.join(asset_dir, "sound_on.png")
    sound_off_path = os.path.join(asset_dir, "sound_off.png")
    sound_on_img = pygame.transform.scale(pygame.image.load(sound_on_path).convert_alpha(), (26, 26))
    sound_off_img = pygame.transform.scale(pygame.image.load(sound_off_path).convert_alpha(), (26, 26))
    music_hitbox = pygame.Rect(0, 0, 0, 0)

    # Label font for top-right UI
    music_font = pygame.font.Font(timer_font_path, 18)
    music_ui_padding = 12
    music_ui_gap = 8

    # Simulation state
    simulation_over = False
    exported_stats = False
    fading_out = False
    fade_alpha = 0
    music_muted = False

    # Game loop
    while True:

        fps_value = clock.get_fps() # FPS value
        mouse_pos = pygame.mouse.get_pos() # Get mouse position

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                settings.simulation_running = False
                close_stats_window()
                pygame.mixer.music.stop()
                pygame.quit()
                sys.exit()

            # Toggle music
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if music_hitbox.collidepoint(event.pos):
                    music_muted = not music_muted
                    pygame.mixer.music.set_volume(0.0 if music_muted else 0.05)
                    continue

            # Back button function
            if (
            (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and back_button.collidepoint(event.pos))
            or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE)
            ):
                settings.simulation_running = False
                close_stats_window()
                pygame.mixer.music.stop()
                pygame.quit()
                return # back to main_menu

            # After simulation ends, exit ONLY when SPACEBAR is pressed
            if simulation_over and event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    fading_out = True
                    fade_alpha = 0

        screen.blit(background, (0, 0))

        # Back button style
        draw_small_button(
            screen,
            back_button,
            "Back",
            back_font,
            back_base,
            back_hover,
            mouse_pos,
        )

        # Draw music UI
        label_text = "Music: OFF" if music_muted else "Music: ON"
        label_surf = music_font.render(label_text, True, white)
        icon_img = sound_off_img if music_muted else sound_on_img

        icon_rect = icon_img.get_rect()
        icon_rect.top = music_ui_padding
        icon_rect.right = screen_width - music_ui_padding

        label_rect = label_surf.get_rect()
        label_rect.centery = icon_rect.centery
        label_rect.right = icon_rect.left - music_ui_gap

        music_hitbox = label_rect.union(icon_rect).inflate(5, 5)

        # Hover outline
        if music_hitbox.collidepoint(mouse_pos):
            pygame.draw.rect(screen, (255, 255, 255), music_hitbox, 2, border_radius=5)

        screen.blit(label_surf, label_rect)
        screen.blit(icon_img, icon_rect)

        # Simulation title
        title_surface = title_font.render("Smart Traffic Simulator", True, white)
        screen.blit(title_surface, (90, 30))
    
        if not simulation_over:

            # Draw traffic signals
            for i in range(settings.no_of_signals):
                if i == settings.current_green:
                    if settings.current_yellow == 1:
                        screen.blit(yellow_signal, settings.signal_coords[i])
                    else:
                        screen.blit(green_signal, settings.signal_coords[i])
                else:
                    screen.blit(red_signal, settings.signal_coords[i])

            # Timers & vehicles counter
            for i in range(settings.no_of_signals):
            
                # Traffic light timer text
                txt = str(settings.signals[i].signal_text)
                timer_surface = font.render(txt, True, white, black)
                screen.blit(timer_surface, settings.signal_timer_coords[i])

                # Vehicles passed counter text
                count = settings.vehicles[settings.direction_numbers[i]]["crossed"]
                count_surface = font.render(str(count), True, black, white)
                screen.blit(count_surface, settings.vehicle_count_coords[i])

            # Overall simulation timer
            elapsed_str = sec_to_min_sec(settings.time_elapsed)
            time_text = timer_font.render("Time elapsed: " + elapsed_str, True, black, white)
            screen.blit(time_text, (1100, 50))

        # Total vehicles passed lane
        total_passed = (
            settings.vehicles["right"]["crossed"]
            + settings.vehicles["down"]["crossed"]
            + settings.vehicles["left"]["crossed"]
            + settings.vehicles["up"]["crossed"]
        )

        if not simulation_over:
            # Move vehicles while running
            for v in settings.simulation:
                screen.blit(v.current_image, (v.x, v.y))
                v.move()

            # Check end condition
            if total_passed > settings.vehicle_limit:
                print("[simulation end] total vehicles passed = {}".format(total_passed))
                simulation_over = True
                
                # Stop background threads and freeze timers
                settings.simulation_running = False
        else:
            # Freeze vehicles in final positions
            for v in settings.simulation:
                screen.blit(v.current_image, (v.x, v.y))
            
            # Export stats once
            if not exported_stats:
                export_stats_to_xlsx() # detailed lane stats
                append_run_summary() # per-run summary stats
                exported_stats = True

            # Semi-transparent dark overlay
            overlay = pygame.Surface((screen_width, screen_height))
            overlay.set_alpha(200)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))

            # Compute average waiting time per lane
            avg_wait = []
            for i in range(4):
                if settings.lane_wait_count[i] > 0:
                    avg = settings.lane_wait_sum[i] / settings.lane_wait_count[i]
                else:
                    avg = 0.0
                avg_wait.append(avg)
            
            # Average lane waiting time before green
            avg_wait_before_green = []
            for i in range(4):
                if settings.lane_wait_before_green_count[i] > 0:
                    avg_bg = (
                        settings.lane_wait_before_green_sum[i]
                        / settings.lane_wait_before_green_count[i]
                    )
                else:
                    avg_bg = 0.0
                avg_wait_before_green.append(avg_bg)

            # Average queue size at the moment lane turns green
            avg_queue_at_green = []
            for i in range(4):
                if settings.queue_at_green_count[i] > 0:
                    avg_qg = (
                        settings.queue_at_green_sum[i]
                        / settings.queue_at_green_count[i]
                    )
                else:
                    avg_qg = 0.0
                avg_queue_at_green.append(avg_qg)

            # Bold text for pop-up end window
            font.set_bold(True)
            big_font.set_bold(True)

            # Summary text to display in UI
            title_text = "Simulation Ended"
            title_surf = big_font.render(title_text, True, white)
            title_rect = title_surf.get_rect(center=(screen_width // 2, 140))
            screen.blit(title_surf, title_rect)

            total_text = "Total vehicles passed: " + str(total_passed)
            total_surf = font.render(total_text, True, white)
            total_rect = total_surf.get_rect(center=(screen_width // 2, 185))
            screen.blit(total_surf, total_rect)

            # Titles
            left_title  = "Average vehicle wait time per lane (seconds):"
            right_title = "Average lane waiting time before green (seconds):"
            queue_title = "Average no. of vehicles waiting in lane when light turns green:"

            # Left column lines
            left_lines = [
                "North (dir 4): %.2fs" % avg_wait[3],
                "South (dir 2): %.2fs" % avg_wait[1],
                "East  (dir 1): %.2fs" % avg_wait[0],
                "West  (dir 3): %.2fs" % avg_wait[2],
            ]

            # Right column lines
            right_lines = [
                "North (dir 4): %.2fs" % avg_wait_before_green[3],
                "South (dir 2): %.2fs" % avg_wait_before_green[1],
                "East  (dir 1): %.2fs" % avg_wait_before_green[0],
                "West  (dir 3): %.2fs" % avg_wait_before_green[2],
            ]

            # Center column lines
            queue_lines = [
                "North (dir 4): %.2f vehicles" % avg_queue_at_green[3],
                "South (dir 2): %.2f vehicles" % avg_queue_at_green[1],
                "East  (dir 1): %.2f vehicles" % avg_queue_at_green[0],
                "West  (dir 3): %.2f vehicles" % avg_queue_at_green[2],
            ]

            # Column positions
            left_center  = screen_width // 2 - 300
            right_center = screen_width // 2 + 300

            start_y = 280
            line_gap = 35

            # Left column
            left_title_surf = font.render(left_title, True, white)
            left_title_rect = left_title_surf.get_rect(center=(left_center, start_y))
            screen.blit(left_title_surf, left_title_rect)

            for i, text in enumerate(left_lines):
                surf = font.render(text, True, white)
                text_rect = surf.get_rect(center=(left_center, start_y + (i + 1) * line_gap))
                screen.blit(surf, text_rect)

            # Right column
            right_title_surf = font.render(right_title, True, white)
            right_title_rect = right_title_surf.get_rect(center=(right_center, start_y))
            screen.blit(right_title_surf, right_title_rect)

            for i, text in enumerate(right_lines):
                surf = font.render(text, True, white)
                text_rect = surf.get_rect(center=(right_center, start_y + (i + 1) * line_gap))
                screen.blit(surf, text_rect)

            # Average queue size when light turns green
            queue_title_surf = font.render(queue_title, True, white)
            queue_title_rect = queue_title_surf.get_rect(center=(screen_width // 2, start_y + 5 * line_gap))
            screen.blit(queue_title_surf, queue_title_rect)

            for i, text in enumerate(queue_lines):
                surf = font.render(text, True, white)
                text_rect = surf.get_rect(center=(screen_width // 2, start_y + (6 + i) * line_gap))
                screen.blit(surf, text_rect)

            # Footer text
            exit_text = "Press SPACEBAR to exit"
            exit_surf = font.render(exit_text, True, white)
            exit_rect = exit_surf.get_rect(center=(screen_width // 2, screen_height - 80))
            screen.blit(exit_surf, exit_rect)

        # Exit fade-out function
        if fading_out:
            fade_alpha += 15 # fade speed
            
            if fade_alpha > 255:
                fade_alpha = 255

            fade_surface = pygame.Surface((screen_width, screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(fade_alpha)
            screen.blit(fade_surface, (0, 0))

            if fade_alpha >= 255:
                settings.simulation_running = False
                close_stats_window()
                pygame.mixer.music.stop()
                pygame.quit()
                return # back to main_menu

        # FPS counter text
        fps_text = fps_font.render("{:.0f} FPS".format(fps_value), True, (255, 255, 0))
        fps_rect = fps_text.get_rect()
        fps_rect.bottomleft = (10, screen_height - 10)
        screen.blit(fps_text, fps_rect)

        # Draw custom cursor
        mouse_x, mouse_y = pygame.mouse.get_pos()
        screen.blit(cursor_img, (mouse_x, mouse_y))

        pump_stats_window()
        pygame.display.update()
        clock.tick(60)

if __name__ == "__main__":
    main()