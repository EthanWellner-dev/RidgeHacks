"""
Flask - The main vessel containing all chemicals, reactions, and particles.
"""

from chemical import Chemical
from chemical_state import ChemicalState


class Flask:
    """
    The primary simulation container. Manages chemical state, particle emitters,
    temperature, and provides visual data for rendering.
    """
    
    def __init__(self, volume: float, max_temperature: float = 373.15):
        """
        Initialize a flask.
        
        Args:
            volume: Container volume in liters
            max_temperature: Maximum temperature before boiling (Kelvin, default 373.15K = 100°C)
        """
        self.volume = volume
        self.max_temperature = max_temperature
        
        # Chemistry system
        self.chemical_state = ChemicalState(volume, temperature=293.15)  # Start at room temp
        
        # Particle effects (will manage ParticleEmitter objects)
        self.particle_emitters = []
        
        # Visual properties
        self.is_boiling = False
        self.color_hex = "#FFFFFF"  # Current blended color
        
        # Bounds for rendering (pixels)
        self.bounds = {
            'x': 0,
            'y': 0,
            'width': 400,
            'height': 500
        }
        
        # Metadata
        self.name = "Flask"
    
    def add_reactant(self, chemical: Chemical, moles: float) -> None:
        """
        Add a reactant to the flask.
        
        Args:
            chemical: Chemical object to add
            moles: Amount in moles
        """
        self.chemical_state.add_chemical(chemical, moles)
    
    def add_catalyst(self, catalyst_factor: float) -> None:
        """
        Apply catalyst multiplier to all reactions.
        
        Args:
            catalyst_factor: Reaction rate multiplier (1.0 = no effect)
        """
        self.chemical_state.set_catalyst_factor(catalyst_factor)
    
    def set_temperature(self, temp: float) -> None:
        """
        Manually set temperature (e.g., via hotplate).
        
        Args:
            temp: Temperature in Kelvin
        """
        temp = max(0, min(temp, self.max_temperature))
        self.chemical_state.set_temperature(temp)
        self.is_boiling = (temp >= self.max_temperature)
    
    def adjust_temperature(self, delta_temp: float) -> None:
        """
        Adjust temperature by delta (can be from exothermic reactions).
        
        Args:
            delta_temp: Temperature change in Kelvin
        """
        new_temp = self.chemical_state.temperature + delta_temp
        self.set_temperature(new_temp)
    
    def update(self, delta_time: float) -> dict:
        """
        Tick the chemistry and particle systems.
        
        Args:
            delta_time: Time step in seconds
        
        Returns:
            dict with update metadata
        """
        # Update chemistry
        chem_update = self.chemical_state.update(delta_time)
        
        # Apply heat from reactions to temperature
        heat_change_kj = chem_update.get('total_heat_change', 0.0)
        # Simplified: 1 kJ raises temperature by 1 K (assuming water, 1L ≈ 1 kg)
        delta_temp = heat_change_kj * 0.001  # Dampening factor
        self.adjust_temperature(delta_temp)
        
        # Update color
        self.color_hex = self.chemical_state.get_net_color()
        
        # Update particle emitters (placeholder for future)
        for emitter in self.particle_emitters:
            if hasattr(emitter, 'update'):
                emitter.update(delta_time)
        
        return {
            'temperature': self.chemical_state.temperature,
            'is_boiling': self.is_boiling,
            'color_hex': self.color_hex,
            'reactions_fired': chem_update.get('reactions_fired', [])
        }
    
    def get_visual_data(self) -> dict:
        """
        Return all visual data for rendering.
        
        Returns:
            dict with 'color_hex', 'temperature', 'particle_count', 'is_boiling'
        """
        particle_count = sum(
            len(emitter.particles) if hasattr(emitter, 'particles') else 0
            for emitter in self.particle_emitters
        )
        
        return {
            'color_hex': self.color_hex,
            'temperature': self.chemical_state.temperature,
            'temperature_max': self.max_temperature,
            'particle_count': particle_count,
            'is_boiling': self.is_boiling,
            'volume': self.volume,
            'bounds': self.bounds.copy()
        }
    
    def get_chemical_by_name(self, name: str) -> Chemical:
        """Find a chemical by name."""
        for chemical in self.chemical_state.chemicals.keys():
            if chemical.name == name:
                return chemical
        return None
    
    def get_chemical_amount(self, chemical_name: str) -> float:
        """Get moles of a specific chemical."""
        for chemical, moles in self.chemical_state.chemicals.items():
            if chemical.name == chemical_name:
                return moles
        return 0.0
    
    def add_particle_emitter(self, emitter) -> None:
        """Register a particle emitter with this flask."""
        self.particle_emitters.append(emitter)
    
    def remove_particle_emitter(self, emitter) -> None:
        """Unregister a particle emitter."""
        if emitter in self.particle_emitters:
            self.particle_emitters.remove(emitter)
    
    def reset(self) -> None:
        """Clear all chemicals and reset to initial state."""
        self.chemical_state.chemicals.clear()
        self.chemical_state.set_temperature(293.15)
        self.particle_emitters.clear()
        self.is_boiling = False
        self.color_hex = "#FFFFFF"
    
    def __repr__(self) -> str:
        return f"Flask({self.volume}L, T={self.chemical_state.temperature:.1f}K, {len(self.chemical_state.chemicals)} chemicals)"
