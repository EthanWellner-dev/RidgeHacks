"""
test_ui_and_game.py - Tests for UI elements and GameMode integration.
"""

from chemistry.chemical import Chemical
from chemistry.flask import Flask
from chemistry.particle_emitter import ParticleEmitter
from game.dropper import Dropper
from game.thermometer import Thermometer
from game.hotplate import HotPlate
from game.challenge import Challenge, ChallengeLibrary
from game.game_mode import GameMode
from game.rigid_body import RigidBody


def test_dropper():
    """Test Dropper UI element."""
    print("\n=== Testing Dropper ===")
    
    h2so4 = Chemical("H2SO4", [("H", 2), ("S", 1), ("O", 4)], 0.0, "#FF0000", -813)
    dropper = Dropper(100, 100, h2so4, 0.1, label="Acid")
    
    print(f"Created: {dropper}")
    
    # Test click detection
    print(f"Is clicked at (100, 100)? {dropper.is_clicked(100, 100)}")
    print(f"Is clicked at (500, 500)? {dropper.is_clicked(500, 500)}")
    
    # Test mouse down
    print(f"Mouse down at (100, 100)? {dropper.on_mouse_down(100, 100)}")
    print(f"Cooldown active? {dropper.click_cooldown > 0}")
    
    # Dispense
    dispense = dropper.dispense()
    print(f"Dispensed: {dispense['moles']:.3f} mol of {dispense['chemical'].name}")
    
    # Render data
    render = dropper.get_render_data()
    print(f"Render color: {render['color']}, Label: {render['label']}")


def test_thermometer():
    """Test Thermometer UI element."""
    print("\n=== Testing Thermometer ===")
    
    thermo = Thermometer(300, 100, 0, 100, label="°C")
    print(f"Created: {thermo}")
    
    # Set temperatures
    for temp in [20, 50, 100]:
        thermo.set_temperature(temp)
        print(f"Temp {temp}°C: Fill={thermo.get_fill_percentage():.0%}, Color={thermo.get_color()}")
    
    # Test Kelvin conversion
    thermo.set_temperature_kelvin(373.15)
    print(f"373.15K (100°C): {thermo.current_temp_c:.1f}°C, Color={thermo.get_color()}")
    
    render = thermo.get_render_data()
    print(f"Render data keys: {list(render.keys())}")


def test_hotplate():
    """Test HotPlate UI element."""
    print("\n=== Testing HotPlate ===")
    
    hotplate = HotPlate(150, 150, max_heat_output=100)
    print(f"Created: {hotplate}")
    
    # Toggle on/off
    print(f"Initial heat output: {hotplate.get_heat_output():.1f} K/s")
    hotplate.toggle()
    print(f"After toggle: {hotplate.get_heat_output():.1f} K/s")
    
    # Adjust heat level
    hotplate.set_heat_level(0.75)
    print(f"Heat level 0.75: {hotplate.get_heat_output():.1f} K/s")
    
    # Render data
    render = hotplate.get_render_data()
    print(f"Render state: on={render['is_on']}, level={render['heat_level']:.0%}")


def test_challenge():
    """Test Challenge class."""
    print("\n=== Testing Challenge ===")
    
    # Create a simple challenge
    chem1 = Chemical("Acid", [("H", 1), ("Cl", 1)], 1.0, "#FF0000", -100)
    chem2 = Chemical("Base", [("Na", 1), ("O", 1), ("H", 1)], 1.0, "#0000FF", 100)
    
    challenge = Challenge(
        name="Neutralization",
        description="Create a neutral solution (purple color).",
        initial_chemicals={chem1: 1.0, chem2: 0.5},
        initial_temperature=293.15,
        win_conditions={'target_color': '#800080', 'max_temp': 350},
        time_limit=60.0
    )
    
    print(f"Created: {challenge}")
    
    # Initialize flask
    flask = challenge.initialize_flask()
    print(f"Flask initialized: {flask}")
    print(f"Flask color: {flask.color_hex}")
    
    # Simulate and check state
    for i in range(3):
        result = challenge.update(5.0)
        print(f"Step {i+1}: Status={result['status']}, Message={result['message']}")


def test_challenge_library():
    """Test predefined challenges."""
    print("\n=== Testing Challenge Library ===")
    
    challenges = [
        ChallengeLibrary.create_color_shift_challenge(),
        ChallengeLibrary.create_gas_production_challenge(),
        ChallengeLibrary.create_equilibrium_balance_challenge()
    ]
    
    for challenge in challenges:
        print(f"\nChallenge: {challenge.name}")
        print(f"  Description: {challenge.description}")
        print(f"  Win conditions: {challenge.win_conditions}")
        print(f"  Time limit: {challenge.time_limit}s")


def test_gamemode_sandbox():
    """Test GameMode in sandbox mode."""
    print("\n=== Testing GameMode (Sandbox) ===")
    
    # Create flask and UI
    flask = Flask(1.0)
    
    # Create some chemicals and droppers
    h2o = Chemical("H2O", 0.0, "#87CEEB", -285.8)
    h2so4 = Chemical("H2SO4", 0.0, "#FF0000", -813)
    
    dropper1 = Dropper(100, 100, h2o, 0.1, label="Water")
    dropper2 = Dropper(200, 100, h2so4, 0.05, label="Acid")
    
    thermometer = Thermometer(350, 100, -10, 110)
    hotplate = HotPlate(350, 250)
    
    # Initialize game mode
    game_mode = GameMode()
    game_mode.initialize_sandbox(flask, [dropper1, dropper2], thermometer, hotplate)
    
    print(f"Created: {game_mode}")
    print(f"UI elements: {len(game_mode.ui_elements)}")
    
    # Simulate
    print("\nSimulating 10 frames...")
    for frame in range(10):
        result = game_mode.update(0.016)  # ~60 FPS
        print(f"Frame {frame+1}: Status={result['status']}")
    
    # Test input
    print("\nTesting mouse click...")
    game_mode.handle_input({
        'type': 'mouse_click',
        'x': 100,
        'y': 100
    })
    print(f"Water in flask: {flask.get_chemical_amount('H2O'):.3f} mol")
    
    # Test hotplate
    print("\nTesting hotplate toggle...")
    game_mode.handle_input({
        'type': 'mouse_click',
        'x': 350,
        'y': 250
    })
    print(f"Hotplate on? {hotplate.is_on}")


def test_gamemode_challenge():
    """Test GameMode in challenge mode."""
    print("\n=== Testing GameMode (Challenge) ===")
    
    challenge = ChallengeLibrary.create_color_shift_challenge()
    
    thermometer = Thermometer(350, 100, -10, 110)
    hotplate = HotPlate(350, 250)
    
    game_mode = GameMode()
    game_mode.initialize_challenge(challenge, thermometer, hotplate)
    
    print(f"Created: {game_mode}")
    print(f"Challenge: {challenge.name}")
    print(f"Description: {challenge.description}")
    
    # Simulate
    print("\nSimulating challenge...")
    for frame in range(100):
        result = game_mode.update(0.1)
        
        if result['status'] in ['won', 'lost']:
            print(f"Frame {frame+1}: {result['status'].upper()}")
            print(f"Message: {result['message']}")
            break
        
        if frame % 20 == 0:
            visual = game_mode.flask.get_visual_data()
            print(f"Frame {frame+1}: Temp={visual['temperature']:.1f}K, Color={visual['color_hex']}")


def test_rigid_body():
    """Test RigidBody physics."""
    print("\n=== Testing RigidBody ===")
    
    body = RigidBody(400, 300, mass=5.0, shape='circle', size=10, name="Pellet")
    print(f"Created: {body}")
    
    # Apply force
    body.apply_force(100, 0)  # Push right
    print(f"Force applied: ({body.force_x}, {body.force_y})")
    
    # Update physics
    bounds = {'x': 0, 'y': 0, 'width': 800, 'height': 600}
    for i in range(10):
        body.update(0.016, gravity=100, bounds=bounds)
    
    print(f"After 10 frames: Position=({body.x:.0f}, {body.y:.0f}), Velocity=({body.vx:.1f}, {body.vy:.1f})")
    print(f"Speed: {body.get_speed():.1f} px/s")
    
    # Test render data
    render = body.get_render_data()
    print(f"Render data: {render['shape']} at ({render['x']:.0f}, {render['y']:.0f})")


def test_full_integration():
    """Full integration test: Sandbox with real simulation."""
    print("\n=== Full Integration Test ===")
    
    # Setup chemistry
    from chemistry.reaction import Reaction
    
    h2 = Chemical("H2", 1.0, "#FFFF00", 0)
    o2 = Chemical("O2", 0.5, "#87CEEB", 0)
    h2o = Chemical("H2O", 0.0, "#FFFFFF", -286)
    
    reaction = Reaction(
        name="Combustion",
        reactants={h2: 2, o2: 1},
        products={h2o: 2},
        kc=1e30,
        rate_constant=0.1,
        delta_h=-286,
        activation_energy=50
    )
    
    # Setup flask
    flask = Flask(1.0)
    flask.add_reactant(h2, 1.0)
    flask.add_reactant(o2, 0.5)
    flask.add_reactant(h2o, 0.0)
    flask.chemical_state.add_reaction(reaction)
    
    # Setup particle emitter
    emitter = ParticleEmitter(200, 300, spawn_rate=50, velocity_magnitude=100, color_hex="#FF8800")
    flask.add_particle_emitter(emitter)
    
    # Setup UI
    dropper = Dropper(100, 100, h2, 0.1, label="H2")
    thermometer = Thermometer(350, 100, -10, 110)
    hotplate = HotPlate(350, 250)
    
    # Create game mode
    game_mode = GameMode()
    game_mode.initialize_sandbox(flask, [dropper], thermometer, hotplate)
    
    print("Running full simulation for 50 frames...")
    for frame in range(50):
        # Simulate a click on frame 5 to add H2
        if frame == 5:
            game_mode.handle_input({'type': 'mouse_click', 'x': 100, 'y': 100})
        
        # Enable heating on frame 20
        if frame == 20:
            game_mode.handle_input({'type': 'mouse_click', 'x': 350, 'y': 250})
            hotplate.set_heat_level(0.75)
        
        result = game_mode.update(0.016)
        
        if frame % 10 == 0:
            render = game_mode.get_render_data()
            print(f"Frame {frame}: Particles={len(render['particles'])}, "
                  f"Color={render['flask']['color_hex']}, "
                  f"Temp={render['flask']['temperature']:.1f}K")
    
    print("✓ Integration test complete!")


if __name__ == "__main__":
    test_dropper()
    test_thermometer()
    test_hotplate()
    test_challenge()
    test_challenge_library()
    test_gamemode_sandbox()
    test_gamemode_challenge()
    test_rigid_body()
    test_full_integration()
    print("\n✓ All UI and game tests completed!")
