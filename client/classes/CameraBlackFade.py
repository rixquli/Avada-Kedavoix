import pygame


class CameraBlackFade:
    def __init__(
        self,
        vision_radius: int = 200,
        softness: int = 95,
        darkness_alpha: int = 255,
    ):
        self.vision_radius = vision_radius
        self.softness = softness
        self.darkness_alpha = darkness_alpha

        self._overlay = None
        self._overlay_size = (0, 0)
        self._light_stamp = None
        self._light_stamp_radius = -1

    def _ensure_overlay(self, surface_size: tuple[int, int]):
        if self._overlay_size == surface_size and self._overlay is not None:
            return

        self._overlay_size = surface_size
        self._overlay = pygame.Surface(surface_size, pygame.SRCALPHA)

    def _ensure_light_stamp(self):
        total_radius = self.vision_radius + self.softness
        if self._light_stamp is not None and self._light_stamp_radius == total_radius:
            return

        diameter = total_radius * 2
        stamp = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        center = (total_radius, total_radius)

        # Build a radial alpha falloff used to subtract darkness around the player.
        for radius in range(total_radius, 0, -2):
            ratio = radius / total_radius
            strength = int((1.0 - (ratio * ratio)) * self.darkness_alpha)
            pygame.draw.circle(stamp, (0, 0, 0, strength), center, radius)

        self._light_stamp = stamp
        self._light_stamp_radius = total_radius

    def draw(self, surface: pygame.Surface, focus_pos: tuple[int, int]):
        self._ensure_overlay(surface.get_size())
        self._ensure_light_stamp()

        self._overlay.fill((0, 0, 0, self.darkness_alpha))

        cx, cy = focus_pos
        stamp_x = int(cx - self._light_stamp_radius)
        stamp_y = int(cy - self._light_stamp_radius)

        self._overlay.blit(
            self._light_stamp,
            (stamp_x, stamp_y),
            special_flags=pygame.BLEND_RGBA_SUB,
        )
        surface.blit(self._overlay, (0, 0))
