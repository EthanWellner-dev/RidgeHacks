"""
Dropper - UI element for dispensing chemicals into the flask.
"""


class Dropper:
    """
    A clickable dropper/pipette UI button that dispenses a specific chemical.
    """
    
    def __init__(self, x: float, y: float, chemical, moles_per_drop: float,
                 width: float = 50, height: float = 80, label: str = None):
        """
        Initialize a dropper.
        
        Args:
            x: Screen position x (pixels)
            y: Screen position y (pixels)
            chemical: Chemical object to dispense
            moles_per_drop: Moles dispensed per click
            width: Button width in pixels
            height: Button height in pixels
            label: Optional label (defaults to chemical name)
        """
        self.x = float(x)
        self.y = float(y)
        self.chemical = chemical
        self.moles_per_drop = max(0.001, moles_per_drop)
        self.width = float(width)
        self.height = float(height)
        self.label = label or (chemical.name if chemical else "Dropper")
        
        # Visual state
        self.is_hovered = False
        self.is_pressed = False
        self.click_cooldown = 0.0  # seconds
        self.click_delay = 0.2  # Prevent rapid clicks
        
        # Bounds (for collision detection)
        self.bounds = {
            'x': self.x - self.width / 2,
            'y': self.y - self.height / 2,
            'width': self.width,
            'height': self.height
        }
        # Whether this dropper is currently placed in a sidebar (inactive)
        self.in_sidebar = False
        self.active = True
    
    def update(self, delta_time: float) -> None:
        """Update cooldown timer."""
        if self.click_cooldown > 0:
            self.click_cooldown -= delta_time
    
    def is_clicked(self, mouse_x: float, mouse_y: float) -> bool:
        """
        Check if dropper was clicked (mouse is over it).
        
        Args:
            mouse_x: Mouse x position
            mouse_y: Mouse y position
        
        Returns:
            True if mouse is over dropper bounds
        """
        bounds = self.bounds
        return (bounds['x'] <= mouse_x <= bounds['x'] + bounds['width'] and
                bounds['y'] <= mouse_y <= bounds['y'] + bounds['height'])
    
    def on_mouse_down(self, mouse_x: float, mouse_y: float) -> bool:
        """
        Handle mouse down event.
        
        Returns:
            True if dropper was activated (clicked and not on cooldown)
        """
        if self.is_clicked(mouse_x, mouse_y) and self.click_cooldown <= 0:
            self.is_pressed = True
            self.click_cooldown = self.click_delay
            return True
        return False
    
    def on_mouse_up(self) -> None:
        """Handle mouse up event."""
        self.is_pressed = False
    
    def on_mouse_move(self, mouse_x: float, mouse_y: float) -> None:
        """Update hover state."""
        self.is_hovered = self.is_clicked(mouse_x, mouse_y)
    
    def dispense(self) -> dict:
        """
        Dispense the chemical.
        
        Returns:
            dict with 'chemical' and 'moles' to add to flask
        """
        return {
            'chemical': self.chemical,
            'moles': self.moles_per_drop
        }
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering.
        
        Returns:
            dict with position, size, color, label
        """
        # Color changes based on state
        if self.is_pressed:
            color = "#404040"  # Dark gray when pressed
        elif self.is_hovered:
            color = "#606060"  # Medium gray when hovered
        else:
            color = "#808080"  # Light gray normally
        
        return {
            'x': self.bounds['x'],
            'y': self.bounds['y'],
            'width': self.width,
            'height': self.height,
            'color': color,
            'border_color': self.chemical.color_hex if self.chemical else "#FFFFFF",
            'border_width': 3,
            'label': self.label,
            'label_color': self.chemical.color_hex if self.chemical else "#FFFFFF",
            'cooldown': self.click_cooldown,
            'cooldown_max': self.click_delay
            , 'in_sidebar': getattr(self, 'in_sidebar', False), 'active': getattr(self, 'active', True)
        }
    
    def __repr__(self) -> str:
        return f"Dropper({self.label}, {self.moles_per_drop:.3f} mol/drop)"


class TitrationDropper(Dropper):
    """
    A Dropper variant for titration-style interactions. Holding the mouse delivers
    a small continuous amount (mol/sec) instead of a single discrete drop.
    This class is intentionally minimal — the game loop or UI layer should
    call `get_hold_dispense(dt)` each frame while the dropper is being held
    and apply the returned moles to the flask.
    """

    def __init__(self, x: float, y: float, chemical, moles_per_drop: float,
                 sip_rate: float = 0.005, width: float = 50, height: float = 80,
                 label: str = None):
        super().__init__(x, y, chemical, moles_per_drop, width, height, label)
        # sip_rate: mol per second while holding
        self.sip_rate = max(1e-6, float(sip_rate))
        self.holding = False

    def on_mouse_down(self, mouse_x: float, mouse_y: float) -> bool:
        if self.is_clicked(mouse_x, mouse_y):
            self.holding = True
            # also keep normal click behavior for immediate drop
            self.click_cooldown = self.click_delay
            return True
        return False

    def on_mouse_up(self) -> None:
        self.holding = False
        super().on_mouse_up()

    def update(self, delta_time: float) -> None:
        super().update(delta_time)

    def get_hold_dispense(self, delta_time: float) -> dict | None:
        """
        If the dropper is being held, return a small dispense dict for the
        current frame. Returns None when not dispensing.
        """
        if self.holding:
            moles = self.sip_rate * float(delta_time)
            return {'chemical': self.chemical, 'moles': moles}
        return None
