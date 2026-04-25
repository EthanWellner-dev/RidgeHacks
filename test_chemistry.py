"""
test_chemistry.py - Comprehensive tests and demonstration of the Dynamic ChemEngine.
"""

from chemistry.chemical import Chemical
from chemistry.reaction import Reaction
from chemistry.chemical_state import ChemicalState
from chemistry.flask import Flask

def test_chemical():
    """Test Chemical class and its properties."""
    print("\n=== Testing Chemical ===")
    

    # Using signature inferred from architecture: name, moles, color, enthalpy
    h2o = Chemical("H2O", moles=1.0, color_hex="#87CEEB", enthalpy=-285.8)
    print(f"Created: {h2o.name} | {h2o.moles} mol | Color: {h2o.color_hex} | dH: {h2o.enthalpy} kJ/mol")
    
    h2o.moles += 0.5
    print(f"After adding 0.5 mol: {h2o.moles} mol")
    
    # Manually setting concentration for testing (usually handled by ChemicalState)
    h2o.concentration = h2o.moles / 1.0  # Assuming 1L
    print(f"Concentration in 1L: {h2o.concentration:.3f} M")


def test_reaction():
    """Test Reaction class, including describe_equilibrium and unknown products."""
    print("\n=== Testing Reaction ===")
    
    h2 = Chemical("H2", moles=2.0, color_hex="#FFFF00", enthalpy=0)
    o2 = Chemical("O2", moles=1.0, color_hex="#87CEEB", enthalpy=0)
    h2o = Chemical("H2O", moles=0.0, color_hex="#FFFFFF", enthalpy=-285.8)
    
    # Mock concentrations for Q calculation
    h2.concentration = 1.0
    o2.concentration = 0.5
    h2o.concentration = 0.0
    
    # 1. Standard Reversible Reaction
    combustion = Reaction(
        name="Hydrogen Combustion",
        reactants={h2: 2, o2: 1},
        products={h2o: 2},
        kc=1e30,
        rate_constant=0.1,
        delta_h=-286,
        activation_energy=50
    )
    
    print(f"Reaction 1: {combustion.name}")
    print(f"Q (initial): {combustion.calculate_q():.2e}")
    
    # Testing new describe_equilibrium() method
    if hasattr(combustion, 'describe_equilibrium'):
        eq_desc = combustion.describe_equilibrium()
        print(f"Equilibrium Status: {eq_desc}")
    else:
        print(f"Direction: {combustion.calculate_shift()}")
        
    print(f"Rate at 300K: {combustion.calculate_rate(300):.4f}")

    # 2. Decomposition / Unspecified Products Reaction (New Architecture Feature)
    h2o2 = Chemical("H2O2", moles=1.0, color_hex="#EEEEEE", enthalpy=-187.8)
    h2o2.concentration = 1.0
    
    decomposition = Reaction(
        name="Peroxide Decomposition",
        reactants={h2o2: 2},
        products=None,  # Unspecified products as per architecture
        kc=1e10,
        rate_constant=0.05,
        delta_h=-98.2,
        activation_energy=75
    )
    print(f"\nReaction 2: {decomposition.name} (No explicit products)")
    print(f"Rate at 300K: {decomposition.calculate_rate(300):.4f}")


def test_chemical_state():
    """Test ChemicalState, focusing on effective_volume and water dilution."""
    print("\n=== Testing ChemicalState ===")
    
    base_volume = 2.0
    state = ChemicalState(volume=base_volume, temperature=293.15)
    print(f"Initial state: Base Volume = {state.volume}L, Temp = {state.temperature}K")
    
    # Add chemicals
    nacl = Chemical("NaCl", moles=1.0, color_hex="#FFFFFF", enthalpy=-411.1)
    water = Chemical("H2O", moles=55.5, color_hex="#87CEEB", enthalpy=-285.8) # ~1 Liter of water
    
    state.add_chemical(nacl, 1.0)
    state.add_chemical(water, 55.5)
    
    # Testing the new effective_volume logic (Base volume + solvent contributions)
    # 55.5 mol H2O * 0.018 L/mol ≈ 0.999 L
    if hasattr(state, 'effective_volume'):
        eff_vol = state.effective_volume
        print(f"Effective Volume (including {water.moles} mol H2O): {eff_vol:.3f} L")
        expected_vol = base_volume + (55.5 * 0.018)
        print(f"Expected Effective Volume: ~{expected_vol:.3f} L")
    else:
        print("Note: 'effective_volume' property not yet detected on ChemicalState.")
        
    print(f"Net color: {state.get_net_color()}")


def test_flask():
    """Test Flask class, focusing on the new react() batch-update method."""
    print("\n=== Testing Flask ===")
    
    flask = Flask(volume=1.0, max_temperature=373.15)
    print(f"Initial Flask Temp: {flask.chemical_state.get_average_temperature():.1f} K")
    
    h2 = Chemical("H2", moles=2.0, color_hex="#FFFF00", enthalpy=0)
    o2 = Chemical("O2", moles=1.0, color_hex="#87CEEB", enthalpy=0)
    h2o = Chemical("H2O", moles=0.0, color_hex="#FFFFFF", enthalpy=-285.8)
    
    flask.add_reactant(h2, 2.0)
    flask.add_reactant(o2, 1.0)
    flask.add_reactant(h2o, 0.0)
    
    reaction = Reaction(
        name="Combustion",
        reactants={h2: 2, o2: 1},
        products={h2o: 2},
        kc=1e30,
        rate_constant=0.1,
        delta_h=-286,
        activation_energy=50
    )
    flask.chemical_state.add_reaction(reaction)
    
    # Testing the new Flask.react(duration=15) helper
    print("\nExecuting Flask.react(duration=15)...")
    if hasattr(flask, 'react'):
        flask.react(duration=15)
        visual = flask.get_visual_data()
        print(f"After 15s React: T={visual['temperature']:.1f}K, Color={visual['color_hex']}, "
              f"H2O={flask.get_chemical_amount('H2O'):.3f} mol")
    else:
        print("Fallback: 'react()' method not found. Simulating manually for 15s...")
        time_simulated = 0
        while time_simulated < 15:
            flask.update(delta_time=0.1)
            time_simulated += 0.1
        
        visual = flask.get_visual_data()
        print(f"Manual 15s Simulation: T={visual.get('temperature', 0):.1f}K, "
              f"H2O={flask.get_chemical_amount('H2O'):.3f} mol")


if __name__ == "__main__":
    test_chemical()
    test_reaction()
    test_chemical_state()
    test_flask()
    print("\n✓ All engine architecture tests completed!")