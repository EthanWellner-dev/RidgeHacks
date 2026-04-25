"""
HotPlate - Temperature control UI element.
"""


class HotPlate:
    """
    A heating control that adjusts flask temperature.
    Has on/off state and heat level control.
    """
    
    def __init__(self, x: float, y: float, max_heat_output: float = 200.0,
                 width: float = 60, height: float = 60, label: str = "Heat"):
        """
        Initialize a hotplate.
        
        Args:
            x: Screen position x (pixels)
            y: Screen position y (pixels)
            max_heat_output: Maximum temperature change per second (K/s)
            width: Button width in pixels
            height: Button height in pixels
            label: Button label
        """
        self.x = float(x)
        self.y = float(y)
        self.max_heat_output = float(max_heat_output)
        self.width = float(width)
        self.height = float(height)
        self.label = label
        
        # State
        self.is_on = False
        self.heat_level = 0.5  # 0.0 to 1.0 (fraction of max output)
        self.is_hovered = False
        
        # Bounds (for collision detection)
        self.bounds = {
            'x': self.x - self.width / 2,
            'y': self.y - self.height / 2,
            'width': self.width,
            'height': self.height
        }
    
    def on_click(self, mouse_x: float, mouse_y: float) -> bool:
        """
        Handle click event.
        
        Args:
            mouse_x: Mouse x position
            mouse_y: Mouse y position
        
        Returns:
            True if hotplate was clicked (toggled)
        """
        bounds = self.bounds
        if (bounds['x'] <= mouse_x <= bounds['x'] + bounds['width'] and
            bounds['y'] <= mouse_y <= bounds['y'] + bounds['height']):
            self.is_on = not self.is_on
            return True
        return False
    
    def on_mouse_move(self, mouse_x: float, mouse_y: float) -> None:
        """Update hover state."""
        bounds = self.bounds
        self.is_hovered = (bounds['x'] <= mouse_x <= bounds['x'] + bounds['width'] and
                          bounds['y'] <= mouse_y <= bounds['y'] + bounds['height'])
    
    def set_heat_level(self, level: float) -> None:
        """
        Set heat intensity.
        
        Args:
            level: 0.0 (no heat) to 1.0 (max heat)
        """
        self.heat_level = max(0.0, min(1.0, level))
    
    def adjust_heat_level(self, delta: float) -> None:
        """Adjust heat level by delta."""
        self.set_heat_level(self.heat_level + delta)
    
    def toggle(self) -> None:
        """Toggle on/off state."""
        self.is_on = not self.is_on
    
    def get_heat_output(self) -> float:
        """
        Get current heat output rate.
        
        Returns:
            Temperature change per second (K/s)
        """
        if self.is_on:
            return self.max_heat_output * self.heat_level
        return 0.0
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering.
        
        Returns:
            dict with hotplate visual properties
        """
        # Color based on state
        if not self.is_on:
            color = "#808080"  # Gray when off
        elif self.heat_level < 0.33:
            color = "#FFA500"  # Orange for low heat
        elif self.heat_level < 0.67:
            color = "#FF8000"  # Darker orange for medium heat
        else:
            color = "#FF0000"  # Red for high heat
        
        hover_color = "#FFAA00" if not self.is_on else color
        if self.is_hovered:
            color = hover_color
        
        return {
            'x': self.bounds['x'],
            'y': self.bounds['y'],
            'width': self.width,
            'height': self.height,
            'color': color,
            'border_color': "#404040",
            'border_width': 2,
            'label': self.label,
            'heat_level': self.heat_level,
            'is_on': self.is_on,
            'heat_output': self.get_heat_output(),
            'max_heat': self.max_heat_output
        }
    
    def __repr__(self) -> str:
        state = "ON" if self.is_on else "OFF"
        return f"HotPlate({state}, level={self.heat_level:.0%}, output={self.get_heat_output():.1f}K/s)"
