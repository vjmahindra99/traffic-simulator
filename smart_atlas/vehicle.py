# Contains all the core vehicle logic (movement, spawning & turning)
import os
import time
import pygame
from . import settings

# Initialize PyGame sprite
class Vehicle(pygame.sprite.Sprite):
    
    current_image = pygame.Surface((1, 1))

    # Basic vehicle attributes
    def __init__(self, lane, vehicle_class, direction_number, direction, will_turn):
        pygame.sprite.Sprite.__init__(self)
        self.lane = lane
        self.vehicle_class = vehicle_class
        self.speed = settings.speeds[vehicle_class]
        self.direction_number = direction_number
        self.direction = direction
        self.x = settings.x[direction][lane]
        self.y = settings.y[direction][lane]
        self.crossed = 0
        self.will_turn = will_turn
        self.turned = 0
        self.rotate_angle = 0

        # Wait-time calculation
        self.spawn_time = time.time()
        settings.vehicles[direction][lane].append(self)
        self.index = len(settings.vehicles[direction][lane]) - 1

        # Load images
        path = os.path.join(settings.base_path, "assets", "vehicles", direction, vehicle_class + ".png")
        self.original_image = pygame.image.load(path)
        self.current_image = self.original_image

        # Make ambulances glow red
        if self.vehicle_class == "ambulance":
            debug_surface = self.current_image.copy()
            debug_surface.fill((255, 0, 0, 120), special_flags=pygame.BLEND_RGBA_ADD)
            self.current_image = debug_surface
            self.original_image = debug_surface

        # Sprite API fields
        self.image = self.current_image
        self.rect = self.current_image.get_rect()
        self.rect.topleft = (self.x, self.y)

        # Vehicle gap
        gap = settings.gap

        # Set stop line depending on vehicle in front
        if direction == "right":
            if (
                len(settings.vehicles[direction][lane]) > 1
                and settings.vehicles[direction][lane][self.index - 1].crossed == 0
            ):
                self.stop = (
                    settings.vehicles[direction][lane][self.index - 1].stop
                    - settings.vehicles[direction][lane][self.index - 1]
                    .current_image.get_rect()
                    .width
                    - gap
                )
            else:
                self.stop = settings.default_stop[direction]
            
            temp = self.current_image.get_rect().width + gap
            settings.x[direction][lane] -= temp
            settings.stops[direction][lane] -= temp

        elif direction == "left":
            if (
                len(settings.vehicles[direction][lane]) > 1
                and settings.vehicles[direction][lane][self.index - 1].crossed == 0
            ):
                self.stop = (
                    settings.vehicles[direction][lane][self.index - 1].stop
                    + settings.vehicles[direction][lane][self.index - 1]
                    .current_image.get_rect()
                    .width
                    + gap
                )
            else:
                self.stop = settings.default_stop[direction]
            
            temp = self.current_image.get_rect().width + gap
            settings.x[direction][lane] += temp
            settings.stops[direction][lane] += temp

        elif direction == "down":
            if (
                len(settings.vehicles[direction][lane]) > 1
                and settings.vehicles[direction][lane][self.index - 1].crossed == 0
            ):
                self.stop = (
                    settings.vehicles[direction][lane][self.index - 1].stop
                    - settings.vehicles[direction][lane][self.index - 1]
                    .current_image.get_rect()
                    .height
                    - gap
                )
            else:
                self.stop = settings.default_stop[direction]
            
            temp = self.current_image.get_rect().height + gap
            settings.y[direction][lane] -= temp
            settings.stops[direction][lane] -= temp

        elif direction == "up":
            if (
                len(settings.vehicles[direction][lane]) > 1
                and settings.vehicles[direction][lane][self.index - 1].crossed == 0
            ):
                self.stop = (
                    settings.vehicles[direction][lane][self.index - 1].stop
                    + settings.vehicles[direction][lane][self.index - 1]
                    .current_image.get_rect()
                    .height
                    + gap
                )
            else:
                self.stop = settings.default_stop[direction]
            
            temp = self.current_image.get_rect().height + gap
            settings.y[direction][lane] += temp
            settings.stops[direction][lane] += temp

        settings.simulation.add(self)

    # Record wait time when vehicles cross stop line
    def record_wait_time(self):
        if self.crossed == 0:
            idx = settings.direction_index[self.direction]
            wait = time.time() - self.spawn_time
            settings.lane_wait_sum[idx] += wait
            settings.lane_wait_count[idx] += 1
    
    # Movement logic
    # Right (East) 
    def move(self):
        if self.direction == "right":
            if (
                self.crossed == 0
                and self.x + self.current_image.get_rect().width > settings.stop_lines[self.direction]
            ):
                self.record_wait_time()
                self.crossed = 1
                settings.vehicles[self.direction]["crossed"] += 1

            if self.will_turn:
                if (
                    self.crossed == 0
                    or self.x + self.current_image.get_rect().width < settings.mid[self.direction]["x"]
                ):
                    if (
                        (self.x + self.current_image.get_rect().width <= self.stop
                         or settings.current_green == 0
                         or self.crossed == 1)
                        and (
                            self.index == 0
                            or self.x + self.current_image.get_rect().width
                            < (settings.vehicles[self.direction][self.lane][self.index - 1].x - settings.gap2)
                            or settings.vehicles[self.direction][self.lane][self.index - 1].turned == 1
                        )
                    ):
                        self.x += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += settings.rotation_angle
                        self.current_image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle
                        )
                        # Keep sprite image/rect in sync
                        self.image = self.current_image
                        self.rect = self.current_image.get_rect(center=self.rect.center)

                        self.x += 2
                        self.y += 1.8
                        if self.rotate_angle == 90:
                            self.turned = 1
                    else:
                        if (
                            self.index == 0
                            or self.y + self.current_image.get_rect().height
                            < (settings.vehicles[self.direction][self.lane][self.index - 1].y - settings.gap2)
                            or self.x + self.current_image.get_rect().width
                            < (settings.vehicles[self.direction][self.lane][self.index - 1].x - settings.gap2)
                        ):
                            self.y += self.speed
            else:
                if (
                    (
                        self.x + self.current_image.get_rect().width <= self.stop
                        or self.crossed == 1
                        or settings.current_green == 0
                    )
                    and (
                        self.index == 0
                        or self.x + self.current_image.get_rect().width
                        < (
                            settings.vehicles[self.direction][self.lane][self.index - 1].x
                            - settings.gap2
                        )
                        or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                        == 1
                    )
                ):
                    self.x += self.speed

        # Down (South)
        elif self.direction == "down":
            if (
                self.crossed == 0
                and self.y + self.current_image.get_rect().height > settings.stop_lines[self.direction]
            ):
                self.record_wait_time()
                self.crossed = 1
                settings.vehicles[self.direction]["crossed"] += 1

            if self.will_turn:
                if (
                    self.crossed == 0
                    or self.y + self.current_image.get_rect().height < settings.mid[self.direction]["y"]
                ):
                    if (
                        (self.y + self.current_image.get_rect().height <= self.stop
                         or settings.current_green == 1
                         or self.crossed == 1)
                        and (
                            self.index == 0
                            or self.y + self.current_image.get_rect().height
                            < (
                                settings.vehicles[self.direction][self.lane][self.index - 1].y
                                - settings.gap2
                            )
                            or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                            == 1
                        )
                    ):
                        self.y += self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += settings.rotation_angle
                        self.current_image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle
                        )
                        self.image = self.current_image
                        self.rect = self.current_image.get_rect(center=self.rect.center)

                        self.x -= 2.5
                        self.y += 2
                        if self.rotate_angle == 90:
                            self.turned = 1
                    else:
                        if (
                            self.index == 0
                            or self.x
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].x
                                + settings.vehicles[self.direction][self.lane][self.index - 1]
                                .current_image.get_rect()
                                .width
                                + settings.gap2
                            )
                            or self.y
                            < (
                                settings.vehicles[self.direction][self.lane][self.index - 1].y
                                - settings.gap2
                            )
                        ):
                            self.x -= self.speed
            else:
                if (
                    (
                        self.y + self.current_image.get_rect().height <= self.stop
                        or self.crossed == 1
                        or settings.current_green == 1
                    )
                    and (
                        self.index == 0
                        or self.y + self.current_image.get_rect().height
                        < (
                            settings.vehicles[self.direction][self.lane][self.index - 1].y
                            - settings.gap2
                        )
                        or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                        == 1
                    )
                ):
                    self.y += self.speed

        # Left (West)
        elif self.direction == "left":
            if self.crossed == 0 and self.x < settings.stop_lines[self.direction]:
                self.record_wait_time()
                self.crossed = 1
                settings.vehicles[self.direction]["crossed"] += 1

            if self.will_turn:
                if self.crossed == 0 or self.x > settings.mid[self.direction]["x"]:
                    if (
                        (self.x >= self.stop
                         or settings.current_green == 2
                         or self.crossed == 1)
                        and (
                            self.index == 0
                            or self.x
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].x
                                + settings.vehicles[self.direction][self.lane][self.index - 1]
                                .current_image.get_rect()
                                .width
                                + settings.gap2
                            )
                            or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                            == 1
                        )
                    ):
                        self.x -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += settings.rotation_angle
                        self.current_image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle
                        )
                        self.image = self.current_image
                        self.rect = self.current_image.get_rect(center=self.rect.center)

                        self.x -= 1.8
                        self.y -= 2.5
                        if self.rotate_angle == 90:
                            self.turned = 1
                    else:
                        if (
                            self.index == 0
                            or self.y
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].y
                                + settings.vehicles[self.direction][self.lane][self.index - 1]
                                .current_image.get_rect()
                                .height
                                + settings.gap2
                            )
                            or self.x
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].x
                                + settings.gap2
                            )
                        ):
                            self.y -= self.speed
            else:
                if (
                    (
                        self.x >= self.stop
                        or self.crossed == 1
                        or settings.current_green == 2
                    )
                    and (
                        self.index == 0
                        or self.x
                        > (
                            settings.vehicles[self.direction][self.lane][self.index - 1].x
                            + settings.vehicles[self.direction][self.lane][self.index - 1]
                            .current_image.get_rect()
                            .width
                            + settings.gap2
                        )
                        or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                        == 1
                    )
                ):
                    self.x -= self.speed

        # Up (North)
        elif self.direction == "up":
            if self.crossed == 0 and self.y < settings.stop_lines[self.direction]:
                self.record_wait_time()
                self.crossed = 1
                settings.vehicles[self.direction]["crossed"] += 1

            if self.will_turn:
                if self.crossed == 0 or self.y > settings.mid[self.direction]["y"]:
                    if (
                        (self.y >= self.stop
                         or settings.current_green == 3
                         or self.crossed == 1)
                        and (
                            self.index == 0
                            or self.y
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].y
                                + settings.vehicles[self.direction][self.lane][self.index - 1]
                                .current_image.get_rect()
                                .height
                                + settings.gap2
                            )
                            or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                            == 1
                        )
                    ):
                        self.y -= self.speed
                else:
                    if self.turned == 0:
                        self.rotate_angle += settings.rotation_angle
                        self.current_image = pygame.transform.rotate(
                            self.original_image, -self.rotate_angle
                        )
                        self.image = self.current_image
                        self.rect = self.current_image.get_rect(center=self.rect.center)

                        self.x += 1
                        self.y -= 1
                        if self.rotate_angle == 90:
                            self.turned = 1
                    else:
                        if (
                            self.index == 0
                            or self.x
                            < (
                                settings.vehicles[self.direction][self.lane][self.index - 1].x
                                - settings.vehicles[self.direction][self.lane][self.index - 1]
                                .current_image.get_rect()
                                .width
                                - settings.gap2
                            )
                            or self.y
                            > (
                                settings.vehicles[self.direction][self.lane][self.index - 1].y
                                + settings.gap2
                            )
                        ):
                            self.x += self.speed
            else:
                if (
                    (
                        self.y >= self.stop
                        or self.crossed == 1
                        or settings.current_green == 3
                    )
                    and (
                        self.index == 0
                        or self.y
                        > (
                            settings.vehicles[self.direction][self.lane][self.index - 1].y
                            + settings.vehicles[self.direction][self.lane][self.index - 1]
                            .current_image.get_rect()
                            .height
                            + settings.gap2
                        )
                        or settings.vehicles[self.direction][self.lane][self.index - 1].turned
                        == 1
                    )
                ):
                    self.y -= self.speed