"""
Dynamic ChemEngine - Interactive 2D Physics-Based Chemistry Simulator

Core Chemistry Modules:
- Chemical: Individual chemical substances
- Reaction: Reversible reactions with equilibrium and kinetics
- ChemicalState: Central state management for all chemicals
- Flask: Main simulation container

Particle System:
- Particle: Individual particle for visual effects
- ParticleEmitter: Manages groups of particles

UI Elements:
- Dropper: Chemical dispenser button
- Thermometer: Temperature display
- HotPlate: Temperature control

Game Logic:
- Challenge: Goal-oriented puzzle scenarios
- GameMode: Orchestrates game flow and modes
- RigidBody: Physics wrapper for solid objects
"""

from chemistry.chemical import Chemical
from chemistry.reaction import Reaction
from chemistry.chemical_state import ChemicalState
from chemistry.flask import Flask
from chemistry.particle import Particle
from chemistry.particle_emitter import ParticleEmitter
from game.dropper import Dropper
from game.thermometer import Thermometer
from game.hotplate import HotPlate
from game.challenge import Challenge, ChallengeLibrary
from game.game_mode import GameMode
from game.rigid_body import RigidBody

__all__ = [
    # Chemistry
    'Chemical',
    'Reaction',
    'ChemicalState',
    'Flask',
    # Particles
    'Particle',
    'ParticleEmitter',
    # UI
    'Dropper',
    'Thermometer',
    'HotPlate',
    # Game
    'Challenge',
    'ChallengeLibrary',
    'GameMode',
    'RigidBody'
]

__version__ = '0.2.0'
