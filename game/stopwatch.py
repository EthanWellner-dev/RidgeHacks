"""
Stopwatch - simple start/stop/reset timer UI element.
"""

from time import monotonic


class Stopwatch:
    def __init__(self, x: float, y: float, width: float = 80, height: float = 80, label: str = "Timer"):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.label = label

        self.running = False
        self.elapsed = 0.0
        self._last_start = None

        self.in_sidebar = False
        self.active = True
        self.is_hovered = False
        # Initialize pygame.Rect for click detection
        try:
            import pygame
            self.rect = pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
        except Exception:
            self.rect = None

    def start(self):
        if not self.running:
            self._last_start = monotonic()
            self.running = True

    def stop(self):
        if self.running:
            self.elapsed += monotonic() - (self._last_start or monotonic())
            self._last_start = None
            self.running = False

    def reset(self):
        self.running = False
        self.elapsed = 0.0
        self._last_start = None

    def get_time(self) -> float:
        if self.running and self._last_start is not None:
            return self.elapsed + (monotonic() - self._last_start)
        return self.elapsed

    # Button layout: left half is start/stop (green/yellow), right small area is reset (red)
    def _button_areas(self):
        bx, by = self.x, self.y
        w, h = self.width, self.height
        return {
            'start_stop': (bx, by, int(w * 0.7), h),
            'reset': (bx + int(w * 0.7), by, int(w * 0.3), h)
        }

    def on_click(self, mx: float, my: float) -> bool:
        if not getattr(self, 'active', True):
            return False
        for name, (ax, ay, aw, ah) in self._button_areas().items():
            if ax <= mx <= ax + aw and ay <= my <= ay + ah:
                if name == 'reset':
                    self.reset()
                else:
                    if self.running:
                        self.stop()
                    else:
                        self.start()
                return True
        return False

    def on_mouse_move(self, mx: float, my: float) -> None:
        self.is_hovered = any(ax <= mx <= ax + aw and ay <= my <= ay + ah
                              for (ax, ay, aw, ah) in self._button_areas().values())

    def get_render_data(self) -> dict:
        return {
            'x': int(self.x), 'y': int(self.y), 'width': int(self.width), 'height': int(self.height),
            'label': self.label, 'time': self.get_time(), 'running': self.running,
            'in_sidebar': getattr(self, 'in_sidebar', False), 'active': getattr(self, 'active', True)
        }

    def __repr__(self) -> str:
        return f"Stopwatch(time={self.get_time():.1f}s, running={self.running})"
