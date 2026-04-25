"""
Chemical - Represents a single chemical substance in the system.
"""
import mendeleev

class Chemical:
    """
    A chemical substance with molar quantity, color representation, and thermodynamic properties.
    """
    
    def __init__(self, name: str, components: list, moles: float, color_hex: str, enthalpy: float, state: str = "gas"):
        """
        Initialize a chemical.
        
        Args:
            name: Chemical identifier (e.g., "H2O", "H2SO4")
            components: A list of tuples (element_symbol, count) representing the chemical formula
            moles: Current molar amount
            color_hex: Hex color code for visualization (e.g., "#FFD700")
            enthalpy: Molar enthalpy in kJ/mol
            state: Physical state ("gas", "liquid", "solid", "aqueous")
        """
        self.name = name
        self.components = components
        self.moles = max(0, moles)  # Cannot have negative moles
        self.color_hex = color_hex
        self.enthalpy = enthalpy
        self.state = state  # Physical state: gas, liquid, solid, aqueous
        self.concentration = 0.0  # M (will be calculated from moles/volume)
        self.temperature = 293.15  # Temperature in Kelvin (starts at room temperature)
        self.heat_capacity = 4.184  # J/g·K (water equivalent, can be overridden for other substances)
    
    def set_moles(self, moles: float) -> None:
        """Set molar amount (clamped to 0)."""
        self.moles = max(0, moles)
    
    def add_moles(self, delta_moles: float) -> None:
        """Add or remove moles."""
        self.set_moles(self.moles + delta_moles)
    
    def update_concentration(self, volume: float) -> None:
        """
        Recalculate concentration from moles and volume.
        
        Args:
            volume: Container volume in liters
        """
        if volume > 0:
            self.concentration = self.moles / volume
        else:
            self.concentration = 0.0
    
    def set_temperature(self, temperature: float) -> None:
        """Set temperature in Kelvin."""
        self.temperature = max(0, temperature)
    
    def adjust_temperature(self, delta_temp: float) -> None:
        """Adjust temperature by delta amount."""
        self.set_temperature(self.temperature + delta_temp)
    
    def update_temperature(self, delta_time: float, ambient_temp: float = 293.15, cooling_constant: float = 0.1) -> None:
        """
        Update temperature using Newton's law of cooling/heating.
        
        dT/dt = -k(T - T_ambient)
        
        Args:
            delta_time: Time step in seconds
            ambient_temp: Ambient temperature in Kelvin
            cooling_constant: Cooling rate constant (higher = faster cooling)
        """
        if self.moles > 0:  # Only update if we have substance
            temp_diff = self.temperature - ambient_temp
            temp_change = -cooling_constant * temp_diff * delta_time
            self.adjust_temperature(temp_change)
    
    def get_mass(self) -> float:
        """
        Calculate approximate mass in grams.
        Uses molar masses from mendeleev for elements.
        
        Returns:
            Mass in grams
        """
        total_mass = 0.0
        for element_symbol, count in self.components:
            try:
                element = mendeleev.element(element_symbol)
                total_mass += element.mass * count
            except:
                # Fallback for unknown elements
                total_mass += 1.0 * count  # Assume 1 g/mol
        
        return total_mass * self.moles
    
    def get_component_amounts(self) -> dict:
        amounts = {}
        for val in self.components:
            amounts[val][0] = val[1] * self.moles
        return amounts
    
    def __repr__(self) -> str:
        return f"Chemical({self.name}({self.state}), {self.moles:.3f} mol, {self.color_hex})"
