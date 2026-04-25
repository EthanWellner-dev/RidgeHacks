"""
Particle - Single particle in the kinematic particle engine.
"""

import random
import math


class Particle:
    """
    A single particle for simulating gases, foam, and visual effects.
    Uses kinematic motion without rigid body collisions for performance.
    """
    
    def __init__(self, x: float, y: float, vx: float, vy: float, 
                 color_hex: str, lifetime: float, radius: float = 2.0):
        """
        Initialize a particle.
        
        Args:
            x: Initial x position (pixels)
            y: Initial y position (pixels)
            vx: Initial x velocity (pixels/second)
            vy: Initial y velocity (pixels/second)
            color_hex: Hex color (e.g., "#FFFF00")
            lifetime: Maximum lifetime in seconds
            radius: Visual radius in pixels
        """
        self.x = float(x)
        self.y = float(y)
        self.vx = float(vx)
        self.vy = float(vy)
        self.color_hex = color_hex
        self.lifetime = float(lifetime)
        self.age = 0.0
        self.radius = float(radius)
        self.is_alive = True
    
    def update(self, delta_time: float, gravity: float = 100.0, 
               damping: float = 0.98, bounds: dict = None) -> bool:
        """
        Update particle position and lifetime.
        
        Args:
            delta_time: Time step in seconds
            gravity: Gravity acceleration (pixels/second²)
            damping: Velocity damping per step (0.98 = 2% loss)
            bounds: Container bounds dict with 'x', 'y', 'width', 'height'
        
        Returns:
            True if particle is still alive, False if expired
        """
        if not self.is_alive:
            return False
        
        # Update age
        self.age += delta_time
        if self.age >= self.lifetime:
            self.is_alive = False
            return False
        
        # Apply gravity
        self.vy += gravity * delta_time
        
        # Apply velocity dampening
        self.vx *= damping
        self.vy *= damping
        
        # Update position
        self.x += self.vx * delta_time
        self.y += self.vy * delta_time
        
        # Boundary collision (simple bounce)
        if bounds:
            left = bounds.get('x', 0)
            top = bounds.get('y', 0)
            right = left + bounds.get('width', 800)
            bottom = top + bounds.get('height', 600)
            
            if self.x - self.radius < left:
                self.x = left + self.radius
                self.vx *= -0.8
            elif self.x + self.radius > right:
                self.x = right - self.radius
                self.vx *= -0.8
            
            if self.y - self.radius < top:
                self.y = top + self.radius
                self.vy *= -0.8
            elif self.y + self.radius > bottom:
                self.y = bottom - self.radius
                self.vy *= -0.8
        
        return self.is_alive
    
    def get_alpha(self) -> float:
        """
        Get particle opacity (0-1) based on age.
        Fades out as it approaches lifetime.
        
        Returns:
            Opacity value (1.0 = fully opaque, 0.0 = transparent)
        """
        if self.lifetime <= 0:
            return 1.0
        
        progress = self.age / self.lifetime
        
        # Fade in first 10%, stay opaque, fade out last 30%
        if progress < 0.1:
            return progress * 10.0
        elif progress < 0.7:
            return 1.0
        else:
            return (1.0 - progress) / 0.3
    
    def __repr__(self) -> str:
        return f"Particle({self.x:.0f}, {self.y:.0f}, age={self.age:.2f}s/{self.lifetime:.2f}s)"
