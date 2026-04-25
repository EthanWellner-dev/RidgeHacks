"""
Flask - The main vessel containing all chemicals, reactions, and particles.
"""

from chemistry.chemical import Chemical
from chemistry.chemical_state import ChemicalState


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
    
    def add_reactant(self, chemical: Chemical, moles: float, trigger_react: bool = True) -> None:
        """
        Add a reactant to the flask.
        
        Args:
            chemical: Chemical object to add
            moles: Amount in moles
        """
        # Defensive: ensure we don't crash if UI passes a wrapper or wrong object
        try:
            self.chemical_state.add_chemical(chemical, moles, trigger_react=trigger_react)
        except Exception as e:
            # Try to coerce common wrapper types
            if hasattr(chemical, 'chemical') and isinstance(getattr(chemical, 'chemical'), Chemical):
                self.chemical_state.add_chemical(getattr(chemical, 'chemical'), moles, trigger_react=trigger_react)
                return
            # If given a name or dict, let ChemicalState handle coercion (it will warn if unsupported)
            try:
                self.chemical_state.add_chemical(chemical, moles, trigger_react=trigger_react)
            except Exception:
                print(f"Warning: Failed to add reactant: {e}")
    
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
        Applies the temperature change to all chemicals.
        
        Args:
            delta_temp: Temperature change in Kelvin
        """
        current_avg_temp = self.chemical_state.get_average_temperature()
        new_temp = current_avg_temp + delta_temp
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
        chem_update = self.chemical_state.update(delta_time, ambient_temp=293.15)
        
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
            'temperature': self.chemical_state.get_average_temperature(),
            'is_boiling': self.is_boiling,
            'color_hex': self.color_hex,
            'reactions_fired': chem_update.get('reactions_fired', [])
        }

    def react(self, duration: float = 15.0, step: float = 1.0) -> dict:
        """
        Simulate reactions over a defined duration (default 15 seconds).

        Args:
            duration: total time to simulate in seconds (default 15s)
            step: timestep to use for internal updates (seconds)

        Returns:
            Aggregated metadata from the simulation period
        """
        print("reacting")
        elapsed = 0.0
        total_reactions = []
        total_heat = 0.0

        # Clamp step
        step = max(0.01, float(step))

        while elapsed < duration:
            dt = min(step, duration - elapsed)
            result = self.chemical_state.update(dt)
            heat_change_kj = result.get('total_heat_change', 0.0)
            total_heat += heat_change_kj

            # Apply heat to temperature (kept same dampening as update())
            delta_temp = heat_change_kj * 0.001
            self.adjust_temperature(delta_temp)

            # Accumulate reactions
            total_reactions.extend(result.get('reactions_fired', []))

            elapsed += dt

            # Early exit if no reactions fired in this step
            if not result.get('reactions_fired') and elapsed >= duration:
                break

        # Refresh visual properties
        self.color_hex = self.chemical_state.get_net_color()
        self.is_boiling = (self.chemical_state.temperature >= self.max_temperature)

        return {
            'duration': duration,
            'steps': int(max(1, duration / step)),
            'total_heat_change_kj': total_heat,
            'reactions_fired': total_reactions,
            'temperature': self.chemical_state.temperature,
            'is_boiling': self.is_boiling,
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
            'temperature': self.chemical_state.get_average_temperature(),
            'temperature_max': self.max_temperature,
            'particle_count': particle_count,
            'is_boiling': self.is_boiling,
            'volume': self.volume,
            'bounds': self.bounds.copy(),
            'chemicals': [
                {'name': chemical.name, 'moles': moles, 'color_hex': getattr(chemical, 'color_hex', '#FFFFFF')}
                for chemical, moles in self.chemical_state.chemicals.items()
            ]
        }

    def get_ph(self) -> float | None:
        """Estimate pH of the current mixture using simple heuristics.

        Returns approximate pH in range [0,14] or None if undefined.
        Uses known strong acids/bases and simple fractions for weak species.
        """
        # Map molecule names to acid/base behavior (strength factor, positive for H+ donors, negative for OH- donors)
        strength = {
            'HCl': ('acid', 1.0),
            'H+': ('acid', 1.0),
            'H2SO4': ('acid', 2.0),
            'NaOH': ('base', 1.0),
            'OH-': ('base', 1.0),
            'NH3': ('base', 0.1)  # weak base fraction
        }

        total_H = 0.0
        total_OH = 0.0
        for chemical, moles in self.chemical_state.chemicals.items():
            name = chemical.name if hasattr(chemical, 'name') else str(chemical)
            if name in strength:
                typ, factor = strength[name]
                if typ == 'acid':
                    total_H += moles * factor
                else:
                    total_OH += moles * factor
            else:
                # Heuristic: if name contains 'H' at start and is not H2O, treat as acid small
                if name.startswith('H') and name != 'H2O':
                    total_H += moles * 0.5

        # Convert to concentrations (mol/L) using chemical_state's volume
        vol = max(1e-6, float(self.chemical_state.volume))
        H_conc = total_H / vol
        OH_conc = total_OH / vol

        # Net result
        if H_conc <= 0 and OH_conc <= 0:
            return None

        import math
        # If concentrations are very close, treat as neutral (pH ~7)
        eps = 1e-12
        if abs(H_conc - OH_conc) <= eps:
            return 7.0

        if H_conc > OH_conc:
            net_H = H_conc - OH_conc
            # avoid zero/negative
            net_H = max(net_H, 1e-14)
            ph = -math.log10(net_H)
        else:
            net_OH = OH_conc - H_conc
            net_OH = max(net_OH, 1e-14)
            poh = -math.log10(net_OH)
            ph = 14.0 - poh

        # Clamp
        ph = max(0.0, min(14.0, ph))
        return ph
    
    
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
        return f"Flask({self.volume}L, T={self.chemical_state.get_average_temperature():.1f}K, {len(self.chemical_state.chemicals)} chemicals)"
