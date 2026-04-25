"""
test_chemistry.py - Basic tests and demonstration of chemistry objects.
"""

from chemistry.chemical import Chemical
from chemistry.reaction import Reaction
from chemistry.chemical_state import ChemicalState
from chemistry.flask import Flask


def test_chemical():
    """Test Chemical class."""
    print("\n=== Testing Chemical ===")
    h2o = Chemical("H2O", [("H", 2), ("O", 1)], 1.0, "#87CEEB", -285.8)  # Light blue, exothermic
    print(f"Created: {h2o}")
    
    h2o.add_moles(0.5)
    print(f"After adding 0.5 mol: {h2o}")
    
    h2o.update_concentration(1.0)  # 1 liter
    print(f"Concentration in 1L: {h2o.concentration:.3f} M")


def test_reaction():
    """Test Reaction class."""
    print("\n=== Testing Reaction ===")
    
    # Simple reaction: 2H2 + O2 -> 2H2O
    h2 = Chemical("H2", [("H", 2)], 1.0, "#FFFF00", 0)      # Yellow
    o2 = Chemical("O2", [("O", 2)], 0.5, "#87CEEB", 0)      # Light blue
    h2o = Chemical("H2O", [("H", 2), ("O", 1)], 0.0, "#FFFFFF", -285.8)  # Water, exothermic
    
    # Concentrations matter for Q calculation
    h2.concentration = 1.0
    o2.concentration = 0.5
    h2o.concentration = 0.0
    
    reaction = Reaction(
        name="Hydrogen Combustion",
        reactants={h2: 2, o2: 1},
        products={h2o: 2},
        kc=1e30,  # Very large K_c favors products
        rate_constant=0.1,
        delta_h=-286,  # kJ/mol (exothermic)
        activation_energy=50
    )
    
    print(f"Created: {reaction}")
    print(f"Q (initial): {reaction.calculate_q():.2e}")
    print(f"Direction: {reaction.calculate_shift()}")
    print(f"Rate at 300K: {reaction.calculate_rate(300):.4f}")
    print(f"Rate at 500K: {reaction.calculate_rate(500):.4f}")
    print(f"Heat change (1.0 extent): {reaction.get_heat_change(1.0):.1f} kJ")


def test_chemical_state():
    """Test ChemicalState class."""
    print("\n=== Testing ChemicalState ===")
    
    state = ChemicalState(volume=2.0, temperature=293.15)
    print(f"Initial state: {state}")
    
    # Add some chemicals
    h2 = Chemical("H2", [("H", 2)], 2.0, "#FFFF00", 0)
    o2 = Chemical("O2", [("O", 2)], 1.0, "#87CEEB", 0)
    h2o = Chemical("H2O", [("H", 2), ("O", 1)], 0.0, "#FFFFFF", -285.8)
    
    state.add_chemical(h2, 2.0)
    state.add_chemical(o2, 1.0)
    state.add_chemical(h2o, 0.0)
    
    print(f"After adding chemicals: {state}")
    print(f"Net color: {state.get_net_color()}")
    
    # Add a reaction
    reaction = Reaction(
        name="Combustion",
        reactants={h2: 2, o2: 1},
        products={h2o: 2},
        kc=1e30,
        rate_constant=0.1,
        delta_h=-286,
        activation_energy=50
    )
    state.add_reaction(reaction)
    
    # Update state
    print("\nUpdating state for 0.1 seconds...")
    result = state.update(delta_time=0.1)
    print(f"Update result: {result}")
    print(f"H2 remaining: {h2.moles:.3f} mol")
    print(f"H2O produced: {h2o.moles:.3f} mol")
    print(f"Net color after reaction: {state.get_net_color()}")


def test_flask():
    """Test Flask class."""
    print("\n=== Testing Flask ===")
    
    flask = Flask(volume=1.0, max_temperature=373.15)
    print(f"Initial: {flask}")
    print(f"Visual data: {flask.get_visual_data()}")
    
    # Add chemicals
    h2 = Chemical("H2", [("H", 2)], 2.0, "#FFFF00", 0)
    o2 = Chemical("O2", [("O", 2)], 1.0, "#87CEEB", 0)
    h2o = Chemical("H2O", [("H", 2), ("O", 1)], 0.0, "#FFFFFF", -285.8)
    
    flask.add_reactant(h2, 2.0)
    flask.add_reactant(o2, 1.0)
    flask.add_reactant(h2o, 0.0)
    
    # Add reaction
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
    
    # Simulate
    print("\nSimulating combustion reaction...")
    for i in range(5):
        result = flask.update(delta_time=0.1)
        visual = flask.get_visual_data()
        print(f"Step {i+1}: T={visual['temperature']:.1f}K, Color={visual['color_hex']}, "
              f"H2O={flask.get_chemical_amount('H2O'):.3f} mol")


if __name__ == "__main__":
    test_chemical()
    test_reaction()
    test_chemical_state()
    test_flask()
    print("\n✓ All tests completed!")
