"""
Chemical - Represents a single chemical substance in the system.
"""
import re
import mendeleev

class Chemical:
    """
    A chemical substance with molar quantity, color representation, and thermodynamic properties.
    Supports flexible construction: pass `components` list or let the class parse a formula string.
    """
    
    def __init__(self, name: str, components: list | None = None, moles: float = 0.0, color_hex: str = "#FFFFFF", enthalpy: float = 0.0, state: str = "gas", volume: float | None = None):
        """
        Initialize a chemical.

        Args:
            name: Chemical identifier (e.g., "H2O", "H2SO4")
            components: A list of tuples (element_symbol, count) representing the chemical formula
            moles: Current molar amount
            color_hex: Hex color code for visualization (e.g., "#FFD700")
            enthalpy: Molar enthalpy in kJ/mol
            state: Physical state ("gas", "liquid", "solid", "aqueous")
            volume: Optional per-chemical volume hint (L)
        """
        self.name = name
        # Allow components to be omitted — parse from name if not provided
        if components is None:
            self.components = self._parse_formula(name)
        else:
            self.components = components

        self.moles = max(0, float(moles))  # Cannot have negative moles
        self.color_hex = color_hex
        self.enthalpy = enthalpy
        self.state = state  # Physical state: gas, liquid, solid, aqueous
        self.concentration = 0.0  # M (will be calculated from moles/volume)
        self.temperature = 293.15  # Temperature in Kelvin (starts at room temperature)
        self.heat_capacity = 4.184  # J/g·K (water equivalent, can be overridden for other substances)
        self.volume = float(volume) if volume is not None else None

        # Auto-populate thermodynamic properties for single-element chemicals
        self._auto_populate_properties()
    
    def _auto_populate_properties(self) -> None:
        """
        Auto-populate thermodynamic properties using mendeleev for single-element chemicals.
        Only works for chemicals with exactly one component (pure elements).
        """
        # Only auto-populate for single-element chemicals
        if len(self.components) != 1:
            return
        
        element_symbol, count = self.components[0]
        
        try:
            element = mendeleev.element(element_symbol)
            
            # Set heat capacity (specific heat) if available
            # Use specific_heat which is in J/g·K
            if hasattr(element, 'specific_heat') and element.specific_heat is not None:
                specific_heat = element.specific_heat
                # Only override default if we get a reasonable value
                if 0.1 < specific_heat < 10.0:  # Reasonable range for specific heat capacity
                    self.heat_capacity = specific_heat
            
            # Set enthalpy of formation if not provided (enthalpy == 0)
            # Use heat_of_formation which is in kJ/mol
            if self.enthalpy == 0.0 and hasattr(element, 'heat_of_formation') and element.heat_of_formation is not None:
                enthalpy_kj_per_mol = element.heat_of_formation
                # Scale by stoichiometry (count) for molecular formulas like H2, O2
                if abs(enthalpy_kj_per_mol) < 10000:  # Reasonable range check
                    self.enthalpy = enthalpy_kj_per_mol * count
            
        except (AttributeError, TypeError, ValueError) as e:
            # Silently fail if mendeleev lookup fails - use provided/default values
            pass

    @staticmethod
    def _normalize_name(name: str) -> str:
        """Normalize chemical name for comparisons (fix common typos like 'H20' -> 'H2O')."""
        if not isinstance(name, str):
            return str(name)
        # Replace common zero-for-O typo when it looks like a formula (e.g., H20)
        if re.match(r'^[A-Za-z0-9()]+$', name) and '0' in name:
            alt = name.replace('0', 'O')
            return alt.upper()
        return name.upper()

    @staticmethod
    def _parse_formula(formula: str) -> list:
        """Very small formula parser returning list of (element, count).
        Falls back to a single-component entry if parsing fails.
        """
        if not formula or not isinstance(formula, str):
            return []

        # Try to correct a common typo: zero instead of letter-O
        if '0' in formula and 'O' not in formula:
            formula = formula.replace('0', 'O')

        # Regex to capture element symbols and optional counts, e.g. H2, Na, O
        token_re = re.compile(r'([A-Z][a-z]?)(\d*)')
        tokens = token_re.findall(formula)
        if not tokens:
            return []

        components = []
        for sym, count in tokens:
            cnt = int(count) if count else 1
            components.append((sym, cnt))
        return components
    
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
        # If this chemical has its own volume hint use that, otherwise use container volume
        effective_vol = self.volume if (hasattr(self, 'volume') and self.volume is not None and self.volume > 0) else volume
        if effective_vol > 0:
            self.concentration = self.moles / effective_vol
        else:
            self.concentration = 0.0

    @property
    def molarity(self) -> float:
        """Alias for concentration (mol/L)."""
        return self.concentration
    
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
        """Return a mapping of element symbol -> total atom count in current moles."""
        amounts: dict[str, float] = {}
        for symbol, count in self.components:
            amounts.setdefault(symbol, 0.0)
            amounts[symbol] += count * self.moles
        return amounts
    
    def __repr__(self) -> str:
        return f"Chemical({self.name}({self.state}), {self.moles:.3f} mol, {self.color_hex})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Chemical):
            return False
        return self._normalize_name(self.name) == self._normalize_name(other.name)

    def __hash__(self) -> int:
        return hash(self._normalize_name(self.name))

    @classmethod
    def from_name(cls, name: str, **kwargs):
        """Factory to construct a Chemical by name string (parses formula)."""
        # Allow creating with just a name and kwargs like moles, color_hex, enthalpy
        return cls(name=name, components=None, **kwargs)
