# RidgeHacks
The winners ofc 🤪

Project Overview: The Big Alchemy
1. Project Objective (What It Is)
The Big Alchemy is an interactive, 2D physics-based chemistry simulator built in Python. Unlike static calculators, it is a living system that models the complex, real-time interplay between chemical equilibrium, reaction kinetics, and thermodynamics. The application visualizes abstract chemical concepts—like Le Chatelier's principle and activation energy—through highly responsive fluid-particle systems, dynamic color shifts, and real-time thermal data.

2. The Science (The Chemistry Logic)
The simulation’s backend continuously calculates the state of the virtual flask based on three interconnected scientific pillars:

Equilibrium (Le Chatelier’s Principle): The system tracks reversible reactions using the equilibrium constant (K 
c
​
 ). When the user alters concentrations (e.g., adding an acid/base) or temperature, the backend calculates the shift to restore equilibrium. Visually, this is represented by smooth, dynamic color transitions in the liquid (e.g., transitioning from yellow chromate to orange dichromate as pH drops).

Kinetics (Reaction Rates): The speed at which reactions occur is governed by rate laws. By introducing a catalyst or increasing the concentration of reactants (like H 
2
​
 O 
2
​
 ), the reaction rate multiplier spikes. This dictates the visual spawn rate and velocity of the particle emitter, controlling how violently a gas or foam expands.

Thermodynamics (Enthalpy & Heat Transfer): The engine tracks the enthalpy (ΔH) of the current reactions. Exothermic reactions (like rapid decomposition or strong acid-base neutralizations) release thermal energy, dynamically driving up a virtual thermometer. Because temperature is fundamentally linked to the other two pillars, this heat release can subsequently shift the equilibrium or exponentially increase the kinetic rate, creating a feedback loop.

3. Interactive Modes
The application features two distinct ways to interact with the engine:

Mode 1: Free Play (Sandbox)

The user is given an empty flask and a full dashboard of stressors: reactant droppers, catalysts, acids, bases, and a hotplate.

This is an open-ended exploration mode where the user can mix any combination of chemicals to observe the physical results, trigger massive kinetic explosions (like elephant toothpaste), or attempt to balance complex thermodynamic systems manually.

Mode 2: Goal-Oriented (Challenges)

This mode presents the user with specific puzzle scenarios that require an understanding of the underlying science to solve.

Example Challenge 1 (Equilibrium): "The flask is currently yellow. Shift the equilibrium to achieve a deep orange state, but you cannot exceed 40°C."

Example Challenge 2 (Kinetics/Thermodynamics): "Produce 500 units of O 
2
​
  gas in under 10 seconds without boiling the water in the flask."

The backend validates the win state by continuously monitoring the color hex codes, particle count, and temperature variables.

4. System Architecture (How It's Built)
To handle complex scientific math and render massive particle physics without frame-rate drops, the project uses a highly optimized, hybrid architecture written in Python.

Core Framework: pygame drives the main application loop, rendering graphics, and handling user inputs.

Rigid Body Physics Engine: pymunk (a 2D physics library) handles the collision mechanics of solid objects. When a user drops a solid catalyst or chemical pellet into the flask, Pymunk calculates the gravity, mass, and precise collision with the static boundaries of the beaker.

Custom Kinematic Particle Engine: To simulate expanding gases, foam, and liquid states without crashing the CPU, the app bypasses rigid body physics for fluids. Instead, it utilizes a custom kinematic algorithm. It generates hundreds of overlapping circles per frame, dictating their velocity (v 
x
​
 ,v 
y
​
 ) and spawn rate directly from the kinetic math. By applying simulated gravity but ignoring particle-to-particle collisions, the application can render massive, screen-filling reactions smoothly.

State Management Matrix: The core logic runs on a dictionary/matrix of chemical states. Every frame, the engine reads the current volume, temperature, and moles of each substance, runs the mathematical formulas for the three scientific pillars, and passes the resulting outputs to the Pygame rendering layer to update the colors, UI, and particle emitters.
