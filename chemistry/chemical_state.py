"""
ChemicalState - Central state management for all chemicals and reactions.
"""

from chemistry.chemical import Chemical
from chemistry.reaction import Reaction


class ChemicalState:
    """
    Tracks all chemicals, reactions, and thermodynamic conditions.
    Acts as the hub for chemistry calculations each frame.
    """
    
    def __init__(self, volume: float, temperature: float = 293.15):
        """
        Initialize the chemical state.
        
        Args:
            volume: Container volume in liters
            temperature: Initial temperature in Kelvin (default 293.15K = 20°C)
        """
        self.volume = volume
        self.temperature = temperature
        self.pressure = 1.0  # atm (will be calculated from ideal gas law)
        
        self.chemicals = {}      # {Chemical: moles}
        self.reactions = []      # [Reaction, ...]
        self.catalyst_factor = 1.0
    
    def react(self) -> None:
        """With the addition of a new component, update all reactions and shift chemicals accordingly."""
        
        # With all current chemicals, look up all relevant reactions that would occur.
        # If they are already occuring do nothing; if not, add them to the list.
        # Any non-applicable reactions that are still listed should stop.
        

    def add_chemical(self, chemical: Chemical, moles: float) -> None:
        """
        Add or update a chemical in the state.
        
        Args:
            chemical: Chemical object to add
            moles: Moles to add (or total if new)
        """
        if chemical not in self.chemicals:
            self.chemicals[chemical] = 0.0
        
        self.chemicals[chemical] += moles
        self.chemicals[chemical] = max(0, self.chemicals[chemical])
        
        # Update concentration immediately
        chemical.update_concentration(self.volume)
    
    def add_reaction(self, reaction: Reaction) -> None:
        """Add a reaction to the system."""
        if reaction not in self.reactions:
            self.reactions.append(reaction)
    
    def set_temperature(self, temperature: float) -> None:
        """Set system temperature in Kelvin."""
        self.temperature = max(0, temperature)
    
    def set_catalyst_factor(self, factor: float) -> None:
        """
        Set global catalyst multiplier (affects all reactions).
        
        Args:
            factor: Multiplier (1.0 = no catalyst, >1 = accelerates)
        """
        self.catalyst_factor = max(0, factor)
    
    def update_concentrations(self) -> None:
        """Recalculate all chemical concentrations based on moles and volume."""
        for chemical in self.chemicals.keys():
            chemical.update_concentration(self.volume)
    
    def update(self, delta_time: float) -> dict:
        """
        Update all reactions and recalculate equilibrium.
        Shifts chemicals based on reaction directions.
        
        Args:
            delta_time: Time step in seconds
        
        Returns:
            dict with 'total_heat_change' (kJ) and 'reactions_fired'
        """
        self.update_concentrations()
        
        total_heat_change = 0.0
        reactions_fired = []
        
        for reaction in self.reactions:
            # Determine reaction direction
            direction = reaction.calculate_shift()
            
            if direction == "equilibrium":
                continue
            
            # Calculate reaction rate
            rate = reaction.calculate_rate(self.temperature, self.catalyst_factor)
            
            # Calculate extent of reaction for this time step
            reaction_extent = rate * delta_time
            
            # Clamp extent to physically reasonable value
            reaction_extent = min(reaction_extent, 0.1)
            
            if reaction_extent > 0:
                reactions_fired.append(reaction.name)
                
                # Apply reaction shift
                if direction == "forward":
                    # Consume reactants, produce products
                    for chemical, coeff in reaction.reactants.items():
                        self.add_chemical(chemical, -coeff * reaction_extent)
                    for chemical, coeff in reaction.products.items():
                        self.add_chemical(chemical, coeff * reaction_extent)
                    
                    heat_change = reaction.get_heat_change(reaction_extent)
                
                elif direction == "reverse":
                    # Consume products, produce reactants
                    for chemical, coeff in reaction.products.items():
                        self.add_chemical(chemical, -coeff * reaction_extent)
                    for chemical, coeff in reaction.reactants.items():
                        self.add_chemical(chemical, coeff * reaction_extent)
                    
                    heat_change = -reaction.get_heat_change(reaction_extent)
                
                total_heat_change += heat_change
        
        # Update concentrations after reactions
        self.update_concentrations()
        
        return {
            'total_heat_change': total_heat_change,
            'reactions_fired': reactions_fired
        }
    
    def get_net_color(self) -> str:
        """
        Blend colors based on all chemicals present.
        Weighted by concentration of each chemical.
        
        Returns:
            Hex color string (e.g., "#FF00FF")
        """
        if not self.chemicals:
            return "#FFFFFF"  # Default white
        
        total_concentration = sum(c.concentration for c in self.chemicals.keys())
        
        if total_concentration == 0:
            return "#FFFFFF"
        
        # Convert hex to RGB, weight by concentration, average
        r_sum = 0.0
        g_sum = 0.0
        b_sum = 0.0
        
        for chemical, _ in self.chemicals.items():
            weight = chemical.concentration / total_concentration
            
            # Parse hex color
            hex_color = chemical.color_hex.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r_sum += r * weight
            g_sum += g * weight
            b_sum += b * weight
        
        # Convert back to hex
        r = int(round(r_sum))
        g = int(round(g_sum))
        b = int(round(b_sum))
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def get_net_temperature_change(self) -> float:
        """
        Calculate cumulative temperature change from recent reactions.
        (To be called each update and used to modify system temperature)
        
        Returns:
            Temperature change in Kelvin
        """
        # This is simplified; in reality you'd track heat capacity
        # For now, return placeholder
        return 0.0
    
    def __repr__(self) -> str:
        chem_str = ", ".join([f"{c.name}: {m:.2f} mol" for c, m in self.chemicals.items()])
        return f"ChemicalState(T={self.temperature}K, V={self.volume}L, Chemicals: {chem_str})"
