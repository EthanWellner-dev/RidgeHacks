"""
RigidBody - Wrapper around pymunk physics bodies for solid objects.
"""


class RigidBody:
    """
    Represents a rigid solid object with physics.
    Wraps pymunk bodies for gravity, collisions, and forces.
    """
    
    def __init__(self, x: float, y: float, mass: float, shape: str, 
                 size: float, name: str = "RigidBody"):
        """
        Initialize a rigid body.
        
        Args:
            x: Initial x position (pixels)
            y: Initial y position (pixels)
            mass: Mass in arbitrary units
            shape: Shape type ('circle' or 'rect')
            size: For circle: radius; for rect: side length
            name: Object identifier
        """
        self.x = float(x)
        self.y = float(y)
        self.mass = max(0.01, mass)  # Clamp to prevent division by zero
        self.shape = shape.lower()
        self.size = float(size)
        self.name = name
        
        # Velocity
        self.vx = 0.0
        self.vy = 0.0
        
        # Acceleration (updated from forces)
        self.ax = 0.0
        self.ay = 0.0
        
        # Forces and torque
        self.force_x = 0.0
        self.force_y = 0.0
        
        # Rotation (for future use)
        self.angle = 0.0  # radians
        self.angular_velocity = 0.0
        
        # Physics properties
        self.gravity = 0.0  # m/s^2 (0 = use default)
        self.friction = 0.3  # Friction coefficient
        self.restitution = 0.6  # Bounce factor (0-1)
        
        # Pymunk integration (optional)
        self.pymunk_body = None
        self.pymunk_shape = None
        
        # Visual properties
        self.color_hex = "#808080"
        self.is_active = True
    
    def apply_force(self, fx: float, fy: float) -> None:
        """
        Apply force in Newtons.
        
        Args:
            fx: Force in x direction
            fy: Force in y direction
        """
        self.force_x += float(fx)
        self.force_y += float(fy)
    
    def clear_forces(self) -> None:
        """Reset accumulated forces."""
        self.force_x = 0.0
        self.force_y = 0.0
    
    def set_velocity(self, vx: float, vy: float) -> None:
        """
        Set velocity directly.
        
        Args:
            vx: Velocity in x direction
            vy: Velocity in y direction
        """
        self.vx = float(vx)
        self.vy = float(vy)
    
    def get_velocity(self) -> tuple:
        """Get current velocity."""
        return (self.vx, self.vy)
    
    def get_speed(self) -> float:
        """Get magnitude of velocity."""
        return (self.vx ** 2 + self.vy ** 2) ** 0.5
    
    def update(self, delta_time: float, gravity: float = 100.0,
               damping: float = 0.98, bounds: dict = None) -> None:
        """
        Update position and velocity using Euler integration.
        
        Args:
            delta_time: Time step in seconds
            gravity: Gravity acceleration (pixels/s^2)
            damping: Velocity dampening per step
            bounds: Container bounds for collision detection
        """
        if not self.is_active or self.mass <= 0:
            return
        
        # Calculate acceleration from forces
        self.ax = self.force_x / self.mass
        self.ay = (self.force_y + gravity * self.mass) / self.mass
        
        # Update velocity
        self.vx += self.ax * delta_time
        self.vy += self.ay * delta_time
        
        # Apply damping
        self.vx *= damping
        self.vy *= damping
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Handle boundary collisions
        if bounds:
            self._handle_collision(bounds)
        
        # Clear forces for next frame
        self.clear_forces()
    
    def _handle_collision(self, bounds: dict) -> None:
        """
        Simple boundary collision detection and response.
        
        Args:
            bounds: dict with 'x', 'y', 'width', 'height'
        """
        left = bounds.get('x', 0)
        top = bounds.get('y', 0)
        right = left + bounds.get('width', 800)
        bottom = top + bounds.get('height', 600)
        
        radius = self.size / 2 if self.shape == 'circle' else self.size / 2
        
        # Left wall
        if self.x - radius < left:
            self.x = left + radius
            self.vx *= -self.restitution
        
        # Right wall
        if self.x + radius > right:
            self.x = right - radius
            self.vx *= -self.restitution
        
        # Top wall
        if self.y - radius < top:
            self.y = top + radius
            self.vy *= -self.restitution
        
        # Bottom wall
        if self.y + radius > bottom:
            self.y = bottom - radius
            self.vy *= -self.restitution
    
    def get_position(self) -> tuple:
        """
        Get current position.
        
        Returns:
            (x, y) tuple
        """
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """Set position directly."""
        self.x = float(x)
        self.y = float(y)
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering.
        
        Returns:
            dict with shape, position, and visual properties
        """
        return {
            'shape': self.shape,
            'x': self.x,
            'y': self.y,
            'size': self.size,
            'color': self.color_hex,
            'velocity': (self.vx, self.vy),
            'angle': self.angle,
            'is_active': self.is_active,
            'name': self.name
        }
    
    def __repr__(self) -> str:
        speed = self.get_speed()
        return f"RigidBody({self.name}, {self.shape}, pos=({self.x:.0f}, {self.y:.0f}), " \
               f"v={speed:.1f} px/s, mass={self.mass:.2f})"
