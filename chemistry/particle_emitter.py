"""
ParticleEmitter - Manages spawning and updating groups of particles.
"""

import random
import math
from chemistry.particle import Particle


class ParticleEmitter:
    """
    Spawns and manages particles for gases, foam, and visual effects.
    Intensity adjusts dynamically based on reaction rates.
    """
    
    def __init__(self, x: float, y: float, spawn_rate: float, 
                 velocity_magnitude: float, color_hex: str, 
                 lifetime: float = 2.0, radius: float = 2.0):
        """
        Initialize a particle emitter.
        
        Args:
            x: Spawn position x (pixels)
            y: Spawn position y (pixels)
            spawn_rate: Particles per second
            velocity_magnitude: Initial velocity magnitude (pixels/second)
            color_hex: Particle color (e.g., "#FF0000")
            lifetime: Particle lifetime in seconds
            radius: Particle visual radius
        """
        self.x = float(x)
        self.y = float(y)
        self.spawn_rate = max(0, spawn_rate)
        self.velocity_magnitude = max(0, velocity_magnitude)
        self.color_hex = color_hex
        self.lifetime = max(0.1, lifetime)
        self.radius = float(radius)
        
        self.particles = []
        self.spawn_accumulator = 0.0  # For smooth spawning
        self.active = True
    
    def spawn(self, count: int, angle_variance: float = 360.0) -> None:
        """
        Spawn particles immediately.
        
        Args:
            count: Number of particles to spawn
            angle_variance: Spread angle in degrees (360 = all directions)
        """
        variance_rad = math.radians(angle_variance)
        
        for _ in range(count):
            # Random angle within variance
            angle = random.uniform(0, variance_rad)
            if angle_variance < 360:
                # Center around upward direction
                angle -= variance_rad / 2
            
            # Velocity components
            vx = self.velocity_magnitude * math.sin(angle)
            vy = self.velocity_magnitude * math.cos(angle)
            
            # Small random offset to spawn position
            spawn_x = self.x + random.uniform(-self.radius, self.radius)
            spawn_y = self.y + random.uniform(-self.radius, self.radius)
            
            particle = Particle(
                spawn_x, spawn_y,
                vx, vy,
                self.color_hex,
                self.lifetime,
                self.radius
            )
            self.particles.append(particle)
    
    def update(self, delta_time: float, gravity: float = 100.0, 
               bounds: dict = None) -> None:
        """
        Update all particles and remove dead ones.
        Also handle continuous spawning based on spawn_rate.
        
        Args:
            delta_time: Time step in seconds
            gravity: Gravity acceleration (pixels/second²)
            bounds: Container bounds for collision detection
        """
        if not self.active:
            return
        
        # Handle continuous spawning
        self.spawn_accumulator += self.spawn_rate * delta_time
        spawn_count = int(self.spawn_accumulator)
        if spawn_count > 0:
            self.spawn(spawn_count)
            self.spawn_accumulator -= spawn_count
        
        # Update all particles and remove dead ones
        self.particles = [
            p for p in self.particles
            if p.update(delta_time, gravity, bounds=bounds)
        ]
    
    def set_intensity(self, spawn_rate: float, velocity_magnitude: float) -> None:
        """
        Adjust spawn rate and velocity dynamically.
        Driven by reaction kinetics to create visual feedback.
        
        Args:
            spawn_rate: New particles per second
            velocity_magnitude: New velocity magnitude
        """
        self.spawn_rate = max(0, spawn_rate)
        self.velocity_magnitude = max(0, velocity_magnitude)
    
    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear()
    
    def stop(self) -> None:
        """Stop spawning new particles but let existing ones die naturally."""
        self.active = False
    
    def resume(self) -> None:
        """Resume spawning particles."""
        self.active = True
    
    def get_particle_count(self) -> int:
        """Get number of active particles."""
        return len(self.particles)
    
    def get_particles_to_render(self) -> list:
        """
        Get list of particles with rendering data.
        
        Returns:
            List of dicts with 'x', 'y', 'radius', 'color_hex', 'alpha'
        """
        return [
            {
                'x': p.x,
                'y': p.y,
                'radius': p.radius,
                'color_hex': p.color_hex,
                'alpha': p.get_alpha()
            }
            for p in self.particles
        ]
    
    def __repr__(self) -> str:
        return f"ParticleEmitter({self.x:.0f}, {self.y:.0f}, " \
               f"spawn_rate={self.spawn_rate:.1f}/s, {len(self.particles)} active)"
