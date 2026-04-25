"""
Thermometer - Visual temperature gauge display.
"""


class Thermometer:
    """
    A visual temperature indicator displayed on screen.
    Shows current temperature relative to min/max bounds.
    """
    
    def __init__(self, x: float, y: float, min_temp: float, max_temp: float,
                 width: float = 40, height: float = 200, label: str = "°C"):
        """
        Initialize a thermometer.
        
        Args:
            x: Screen position x (pixels)
            y: Screen position y (pixels, top of thermometer)
            min_temp: Minimum temperature (bottom, in Celsius)
            max_temp: Maximum temperature (top, in Celsius)
            width: Thermometer width in pixels
            height: Thermometer height in pixels
            label: Temperature unit label (default "°C")
        """
        self.x = float(x)
        self.y = float(y)
        self.min_temp_c = float(min_temp)  # Celsius
        self.max_temp_c = float(max_temp)
        self.width = float(width)
        self.height = float(height)
        self.label = label
        
        # Current state
        self.current_temp_c = 20.0  # Default room temperature
        
        # Visual properties
        self.bounds = {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height
        }

        # Initialize a pygame.Rect hitbox for click detection (synchronized by renderer)
        try:
            import pygame
            self.rect = pygame.Rect(int(self.x), int(self.y), int(self.width), int(self.height))
        except Exception:
            self.rect = None
        
        self.bulb_radius = self.width / 2
        # Sidebar state
        self.in_sidebar = False
        self.active = True
    
    def set_temperature(self, temp_celsius: float) -> None:
        """
        Update thermometer temperature.
        
        Args:
            temp_celsius: Temperature in Celsius
        """
        # Clamp to min/max range for display
        self.current_temp_c = max(self.min_temp_c, min(temp_celsius, self.max_temp_c))
    
    def set_temperature_kelvin(self, temp_kelvin: float) -> None:
        """
        Update thermometer temperature from Kelvin.
        
        Args:
            temp_kelvin: Temperature in Kelvin
        """
        temp_celsius = temp_kelvin - 273.15
        self.set_temperature(temp_celsius)
    
    def get_fill_percentage(self) -> float:
        """
        Get thermometer fill as percentage (0-1).
        
        Returns:
            Fill percentage from min to max
        """
        if self.max_temp_c <= self.min_temp_c:
            return 0.0
        
        fill = (self.current_temp_c - self.min_temp_c) / (self.max_temp_c - self.min_temp_c)
        return max(0.0, min(1.0, fill))
    
    def get_color(self) -> str:
        """
        Get thermometer color based on temperature.
        
        Returns:
            Hex color code
        """
        fill = self.get_fill_percentage()
        
        # Color gradient: blue (cold) → yellow → red (hot)
        if fill < 0.5:
            # Blue to yellow
            progress = fill * 2  # 0 to 1
            r = int(255 * progress)
            g = int(255 * progress)
            b = int(255 * (1 - progress))
        else:
            # Yellow to red
            progress = (fill - 0.5) * 2  # 0 to 1
            r = 255
            g = int(255 * (1 - progress))
            b = 0
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering.
        
        Returns:
            dict with thermometer visual properties
        """
        fill_height = self.height * self.get_fill_percentage()
        
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'fill_height': fill_height,
            'fill_y': self.y + self.height - fill_height,  # Fill from bottom
            'fill_color': self.get_color(),
            'background_color': "#E0E0E0",
            'border_color': "#404040",
            'border_width': 2,
            'bulb_radius': self.bulb_radius,
            'bulb_x': self.x + self.width / 2,
            'bulb_y': self.y + self.height + self.bulb_radius,
            'bulb_color': self.get_color(),
            'temperature_text': f"{self.current_temp_c:.1f}",
            'min_label': f"{self.min_temp_c:.0f}",
            'max_label': f"{self.max_temp_c:.0f}",
            'unit': self.label
            , 'in_sidebar': getattr(self, 'in_sidebar', False), 'active': getattr(self, 'active', True)
        }
    
    def __repr__(self) -> str:
        return f"Thermometer({self.current_temp_c:.1f}°C, range={self.min_temp_c:.0f}-{self.max_temp_c:.0f}°C)"
