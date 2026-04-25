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

from chemical import Chemical
from reaction import Reaction
from chemical_state import ChemicalState
from flask import Flask
from particle import Particle
from particle_emitter import ParticleEmitter
from dropper import Dropper
from thermometer import Thermometer
from hotplate import HotPlate
from challenge import Challenge, ChallengeLibrary
from game_mode import GameMode
from rigid_body import RigidBody

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
