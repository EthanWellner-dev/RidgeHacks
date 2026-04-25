# Dynamic ChemEngine - Object Architecture

## Core Chemical Classes

### `Chemical`
Represents a single chemical substance in the system. Stores the name, current molar amount, color representation (as hex), enthalpy value, and calculated concentration. This is the fundamental building block for all reactions in the system.

**Properties:**
- Name identifier
- Moles (quantity)
- Color hex code (for visual rendering)
- Enthalpy (kJ/mol)
- Concentration (derived from moles/volume)

**Planned Methods:**
- `get_component_details()` - Returns display information about the chemical (name, concentration, color, properties). **Not yet implemented.**

---

### `Reaction`
Represents a single reversible chemical reaction with reactants and products. Stores the equilibrium constant (Kc), rate constant for Arrhenius equation, and enthalpy change (ΔH). Provides methods to calculate the reaction quotient Q, determine equilibrium shift direction, and compute reaction rate based on temperature and catalysts.

**Key Methods:**
- Calculate reaction quotient (Q) from current concentrations
- Determine if reaction shifts forward, reverse, or is at equilibrium (Q vs Kc)
- Calculate reaction rate using Arrhenius equation with temperature and catalyst factors

---

### `ChemicalState`
Central state management matrix that tracks all chemicals present, all active reactions, current temperature, volume, and derived pressure. Acts as the hub for all chemistry calculations and updates each frame.

**Key Properties:**
- Dictionary of chemicals with their molar amounts
- List of all active reactions
- Current temperature (Kelvin)
- Container volume (Liters)
- Pressure (derived)

**Key Methods:**
- Add or update chemical quantities
- Update all reaction states and recalculate equilibrium each frame
- Calculate net color by blending all chemical colors
- Sum temperature changes from all reactions (ΔH calculations)

---

## Particle Physics Classes

### `Particle`
Represents a single particle in the kinematic particle engine. Stores position, velocity components, color, lifetime, and age. Used to simulate expanding gases, foam, and visual effects without using rigid body physics (for performance).

**Key Methods:**
- Update position and apply gravity
- Track remaining lifetime
- Check if particle is still alive

---

### `ParticleEmitter`
Manager for spawning and updating groups of particles. Controls spawn rate, velocity magnitude, and particle lifetime. Continuously generates new particles and removes expired ones. Intensity adjusts dynamically based on reaction kinetics to create explosive or calm visual effects.

**Key Methods:**
- Spawn particles with random angle variance
- Update all living particles and remove dead ones
- Adjust spawn rate and velocity intensity (driven by reaction rates)

---

## Container Classes

### `Flask`
The main vessel containing all chemicals and reactions. Holds a ChemicalState instance, multiple ParticleEmitters, spatial bounds, max temperature threshold, and current temperature. This is the primary object the player interacts with indirectly through UI controls.

**Key Methods:**
- Add reactants (chemicals) to the flask
- Apply catalyst multipliers to reaction rates
- Update all chemistry and particle systems each frame
- Set/adjust temperature (via hotplate)
- Return visual data (color, temperature, particle count, boiling state)

---

## Interaction & UI Classes

### `Dropper`
UI element representing a dropper/pipette button. Stores its screen position, the chemical it dispenses, amount per drop, and clickable bounds. Player clicks to add specific chemicals to the flask.

**Key Methods:**
- Detect if dropper was clicked (collision with mouse)
- Dispense the chemical and return quantity to add

---

### `Thermometer`
Visual temperature gauge displayed on screen. Stores position, min/max temperature range, current displayed temperature, and screen bounds. Shows real-time feedback on flask temperature.

**Key Methods:**
- Update displayed temperature
- Render thermometer graphic to screen

---

## Challenge & Game Mode Classes

### `Challenge`
Represents a single goal-oriented puzzle scenario. Stores the challenge name, description, initial flask setup (chemicals and temperature), win conditions (target color, gas volume, temperature bounds, etc.), and optional time limit.

**Key Methods:**
- Initialize a Flask with the scenario's starting conditions
- Check if all win conditions are met
- Check if loss conditions triggered (boiling, constraint violation)

---

### `GameMode`
Encapsulates either Sandbox or Challenge game mode. Manages the Flask instance, all UI elements (Droppers, Thermometer, etc.), the current Challenge (if any), and game flow.

**Key Methods:**
- Initialize the mode (setup UI and Flask)
- Handle player input (mouse clicks, keyboard)
- Update game state each frame
- Check game status (in progress, won, lost) and return appropriate message

---

## Physics Classes (via Pymunk)

### `RigidBody`
Wrapper around pymunk physics objects for solid items like catalyst pellets. Stores position, mass, shape type (circle/rect), and size. Interfaces with pymunk for realistic gravity and collision physics.

**Key Methods:**
- Apply force (in Newtons) to the object
- Set velocity directly
- Update position from pymunk calculations
- Get current position

---

## System Overview

The Flask is the core engine—it updates ChemicalState (chemistry math), manages ParticleEmitters (visuals), and syncs data with UI elements. GameMode orchestrates everything, handling player input (Droppers, hotplate) and monitoring Challenge win/loss conditions. Physics objects (RigidBody) interact with the Flask for solid object drops. All calculations are designed to run efficiently O(R + P) where R = reactions and P = particles per frame.

---

## Summary: Class Dependency Graph

```
GameMode
├── Flask
│   ├── ChemicalState
│   │   ├── Chemical
│   │   └── Reaction
│   └── ParticleEmitter
│       └── Particle
├── Challenge
├── UI (Dropper, Thermometer, etc.)
└── RigidBody
```

**Estimated Efficiency:**
- **ChemicalState**: O(R) per update where R = number of reactions
- **ParticleEmitter**: O(P) where P = particle count (can batch updates)
- **Flask**: O(R + P) per frame
- **Particle**: O(1) per particle update
- **Minimal overhead**: All core classes use primitives + references, no heavy copying.
