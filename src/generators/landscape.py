# src/generators/landscape.py
import math


class LandscapeGenerator:
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height

    def _draw_cloud_blob(self, buffer, x: int, y: int, width: int, height: int, palette):
        for dy in range(height):
            taper = abs(dy - height // 2)
            row_width = width - taper * 2
            if row_width <= 0:
                continue
            start_x = x + taper
            for dx in range(row_width):
                cx = start_x + dx
                cy = y + dy
                if 1 <= cx < self.width - 1 and 5 <= cy < self.height - 1:
                    buffer.set_cell(cx, cy, "#", lambda char: palette.sky_bg(palette.cloud_color(char)))

    def _draw_clouds(self, buffer, palette, scroll_offset: int):
        if not palette.is_cloudy:
            return
        cloud_offset = (scroll_offset // 5) % self.width
        cloud_definitions = [
            (15, 5, 8, 3),
            (42, 6, 14, 4),
            (70, 4, 6, 2)
        ]
        for base_x, y, w, h in cloud_definitions:
            x = (base_x - cloud_offset) % (self.width - 15) + 2
            self._draw_cloud_blob(buffer, x, y, w, h, palette)

    def generate_terrain(self, buffer, palette, weather_code: int, elevation: float, scroll_offset: int):
        self._draw_clouds(buffer, palette, scroll_offset)
        if elevation < 150:
            far_base, far_amp = 19, 0.5
            near_base, near_amp = 20, 0.2
        elif elevation < 500:
            far_base, far_amp = 16, 1.5
            near_base, near_amp = 18, 0.8
        elif elevation < 1500:
            far_base, far_amp = 13, 3.5
            near_base, near_amp = 16, 2.0
        else:
            far_base, far_amp = 10, 6.0
            near_base, near_amp = 14, 3.5
        far_mountain_heights = []
        for x in range(1, self.width - 1):
            world_x = x + scroll_offset
            y_curve = far_base + int(far_amp * math.sin(world_x * 0.1) + (far_amp / 2) * math.cos(world_x * 0.25))
            far_mountain_heights.append(y_curve)
            for y in range(y_curve, self.height - 1):
                buffer.set_cell(x, y, "^", palette.mountain_far)
        near_hill_heights = []
        for x in range(1, self.width - 1):
            world_x = x + scroll_offset
            y_curve = near_base + int(
                near_amp * math.sin(world_x * 0.15 + 2.0) + (near_amp / 2) * math.sin(world_x * 0.3)
            )
            near_hill_heights.append(y_curve)
            for y in range(y_curve, self.height - 1):
                buffer.set_cell(x, y, "#", palette.mountain_near)

        for x in range(2, self.width - 2):
            world_x = x + scroll_offset
            val = math.sin(world_x * 0.732 + weather_code * 3.14) * 43758.5453
            hash_val = val - math.floor(val)
            if hash_val < 0.15:
                y_ridge = near_hill_heights[x - 1]
                buffer.set_cell(x, y_ridge - 1, "▲", palette.tree)
