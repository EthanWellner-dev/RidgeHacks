"""
TemperatureChanger - UI element to set a temperature target.
"""

from typing import Optional


class TemperatureChanger:
    """
    A small controller that sets a target temperature (Kelvin).
    It exposes a simple control loop (proportional) to compute desired
    heat output when connected to a HotPlate.
    """

    def __init__(self, x: float, y: float, min_temp_k: float = 273.15,
                 max_temp_k: float = 373.15, initial_target_k: float = 293.15,
                 width: float = 80, height: float = 80, label: str = "Temp"):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.min_k = float(min_temp_k)
        self.max_k = float(max_temp_k)
        self.target_k = float(initial_target_k)
        self.label = label

        # UI state
        self.in_sidebar = False
        self.active = True
        self.is_hovered = False

    def increase(self, delta_k: float = 1.0) -> None:
        self.target_k = min(self.max_k, self.target_k + float(delta_k))

    def decrease(self, delta_k: float = 1.0) -> None:
        self.target_k = max(self.min_k, self.target_k - float(delta_k))

    def set_target_kelvin(self, k: float) -> None:
        self.target_k = min(self.max_k, max(self.min_k, float(k)))

    def get_target_kelvin(self) -> float:
        return self.target_k

    def get_heat_output(self, max_heat_output: float, current_temp_k: Optional[float]) -> float:
        """
        Compute desired heat output (K/s) based on a simple proportional controller.
        Returns heat in Kelvin-per-second (same units as HotPlate.get_heat_output expects).
        """
        if current_temp_k is None:
            return 0.0
        # proportional gain (simple): how aggressively to reach target
        error = self.target_k - float(current_temp_k)
        kp = 0.6  # tuning constant
        desired = kp * error
        # Clamp to physical heater capability
        desired = max(-max_heat_output, min(max_heat_output, desired))
        # Allow negative output (cooling) if desired by controller logic
        return desired

    # Simple rectangular button regions inside the element for +/- controls
    def _button_areas(self):
        # left half is decrease (yellow), right half is increase (red)
        bx = self.x
        by = self.y
        w = self.width
        h = self.height
        return {
            'decrease': (bx, by, w // 2, h),
            'increase': (bx + w // 2, by, w // 2, h)
        }

    def on_click(self, mouse_x: float, mouse_y: float) -> bool:
        if not getattr(self, 'active', True):
            return False
        areas = self._button_areas()
        for name, (ax, ay, aw, ah) in areas.items():
            if ax <= mouse_x <= ax + aw and ay <= mouse_y <= ay + ah:
                if name == 'increase':
                    self.increase(1.0)
                else:
                    self.decrease(1.0)
                return True
        return False

    def on_mouse_move(self, mouse_x: float, mouse_y: float) -> None:
        areas = self._button_areas()
        self.is_hovered = any(ax <= mouse_x <= ax + aw and ay <= mouse_y <= ay + ah
                              for (ax, ay, aw, ah) in areas.values())

    def get_render_data(self) -> dict:
        return {
            'x': int(self.x), 'y': int(self.y), 'width': int(self.width), 'height': int(self.height),
            'label': self.label, 'target_k': self.target_k,
            'in_sidebar': getattr(self, 'in_sidebar', False), 'active': getattr(self, 'active', True)
        }

    def __repr__(self) -> str:
        return f"TemperatureChanger(target={self.target_k:.1f}K)"
