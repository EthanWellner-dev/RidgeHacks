"""
Reaction - Represents a reversible chemical reaction with equilibrium and kinetics.
"""

import math
from chemistry.chemical import Chemical
import mendeleev # elements

class Reaction:
    """
    A reversible reaction with equilibrium constant, rate constant, and enthalpy change.
    Implements Le Chatelier's principle and Arrhenius equation for rate calculations.
    """
    
    def __init__(self, 
        name: str,
        reactants: dict,
        products: dict,
        kc: float = -1.0,
        rate_constant: float = -1.0,
        delta_h: float = -1.0,
        activation_energy: float = 50.0):
        """
        Initialize a reaction.
        
        Args:
            name: Reaction identifier
            reactants: {Chemical: stoichiometric_coefficient}
            products: {Chemical: stoichiometric_coefficient}
            kc: Equilibrium constant (dimensionless)
            rate_constant: Rate constant for Arrhenius equation
            delta_h: Enthalpy change (kJ/mol)
            activation_energy: Activation energy (kJ/mol) for Arrhenius
        """
        self.name = name
        self.reactants = reactants  # {Chemical: coeff}
        self.products = products    # {Chemical: coeff}
        self.kc = kc
        self.rate_constant = rate_constant
        self.delta_h = delta_h
        self.activation_energy = activation_energy
        self.direction = "equilibrium"  # 'forward', 'reverse', or 'equilibrium'
        # products may be None meaning unspecified/unknown products
        self.products = products or {}
    
    def calculate_q(self) -> float:
        """
        Calculate reaction quotient Q from current concentrations.
        Q = [products] / [reactants] (using stoichiometric coefficients)
        
        Returns:
            Reaction quotient Q
        """
        numerator = 1.0
        denominator = 1.0
        
        # Calculate product concentrations term (if products unknown, numerator stays 1)
        for chemical, coeff in (self.products or {}).items():
            numerator *= (chemical.concentration ** coeff)
        
        # Calculate reactant concentrations term
        for chemical, coeff in self.reactants.items():
            denominator *= (chemical.concentration ** coeff)
        
        if denominator == 0:
            return float('inf') if numerator > 0 else 0
        
        return numerator / denominator
    
    def calculate_shift(self) -> str:
        """
        Determine equilibrium direction by comparing Q to Kc.
        
        Returns:
            'forward' if Q < Kc, 'reverse' if Q > Kc, 'equilibrium' if Q ≈ Kc
        """
        q = self.calculate_q()
        
        # Use small tolerance for floating point comparison
        tolerance = self.kc * 0.01 if self.kc > 0 else 0.01
        
        if abs(q - self.kc) < tolerance:
            self.direction = "equilibrium"
        elif q < self.kc:
            self.direction = "forward"
        else:
            self.direction = "reverse"
        
        return self.direction
    
    def calculate_rate(self, temperature: float, catalyst_factor: float = 1.0) -> float:
        """Calculate reaction rate using Arrhenius equation.

        Interprets the returned value as a rough molar rate (mol/s) for the system.
        Args:
            temperature: Temperature in Kelvin
            catalyst_factor: Multiplier for catalyst (1.0 = no catalyst)
        Returns:
            Reaction rate in mol/s (approximate)
        """
        if temperature <= 0:
            return 0.0
        
        # Gas constant (kJ/mol·K)
        R = 0.00831
        
        # Arrhenius exponential term
        exponent = -self.activation_energy / (R * temperature)
        
        # Clamp exponent to prevent overflow
        exponent = max(exponent, -100)
        
        rate = self.rate_constant * math.exp(exponent) * catalyst_factor
        return max(0, rate)
    
    def get_heat_change(self, reaction_extent: float) -> float:
        """
        Calculate total heat change for given reaction extent.
        
        Args:
            reaction_extent: Amount reacted in moles
        Returns:
            Heat change in kJ (positive = heat released to surroundings).
            Note: `delta_h` is interpreted as reaction enthalpy ΔH in kJ/mol (negative = exothermic).
        """
        # Convention: negative ΔH = exothermic. Heat released to surroundings = -ΔH * extent
        try:
            return -float(self.delta_h) * float(reaction_extent)
        except Exception:
            return 0.0

    def describe_equilibrium(self) -> dict:
        """Return a human-friendly description of the equilibrium state for this reaction."""
        q = self.calculate_q()
        direction = self.calculate_shift()
        return {
            'reaction': repr(self),
            'Q': q,
            'Kc': self.kc,
            'direction': direction,
            'rule': 'At equilibrium Q == Kc. If Q < Kc reaction proceeds forward; if Q > Kc proceeds reverse.'
        }
    
    def __repr__(self) -> str:
        reactant_str = " + ".join([f"{coeff}{chem.name}" for chem, coeff in self.reactants.items()])
        product_str = " + ".join([f"{coeff}{chem.name}" for chem, coeff in self.products.items()])
        return f"{self.name}: {reactant_str} ⇌ {product_str} (Kc={self.kc}, ΔH={self.delta_h})"
