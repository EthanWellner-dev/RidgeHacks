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
    
    def get_component_amounts(self) -> dict:
        amounts = {}
        for val in self.components:
            amounts[val][0] = val[1] * self.moles
        return amounts
    
    def __repr__(self) -> str:
        return f"Chemical({self.name}({self.state}), {self.moles:.3f} mol, {self.color_hex})"
