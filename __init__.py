"""
Dynamic ChemEngine - Core modules

This package contains the fundamental chemistry simulation objects:
- Chemical: Individual chemical substances
- Reaction: Reversible reactions with equilibrium and kinetics
- ChemicalState: Central state management for all chemicals
- Flask: Main simulation container
- Particle: Individual particle for visual effects
- ParticleEmitter: Manages groups of particles
"""

from chemical import Chemical
from reaction import Reaction
from chemical_state import ChemicalState
from flask import Flask
from particle import Particle
from particle_emitter import ParticleEmitter

__all__ = [
    'Chemical',
    'Reaction',
    'ChemicalState',
    'Flask',
    'Particle',
    'ParticleEmitter'
]

__version__ = '0.1.0'
