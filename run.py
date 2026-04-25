"""
run.py - Launcher script for Dynamic ChemEngine.
Handles pygame installation and starts the game.
"""

import sys
import subprocess


"""Simplified launcher and mainloop for UI prototyping.

This run.py replaces the earlier launcher with a standalone pygame mainloop
that draws the UI layout from the provided mockups. It is intentionally a
lightweight prototype: the real game logic remains in other modules.
"""

import pygame
import math
import time
import random
from typing import List

from pygame_renderer import PygameRenderer
from chemistry.chemical import Chemical
from game.dropper import Dropper, TitrationDropper


def make_sample_chemicals():
    return [
        Chemical('Water', 1.0, '#4D5966', 0.0),
        Chemical('Acid', 0.2, '#D32F2F', -50.0),
        Chemical('Base', 0.2, '#2E6BD1', -20.0),
        Chemical('O2', 0.0, '#3A4B4C', 0.0)
    ]
def check_pygame():
    """Check if pygame is installed, install if needed."""
    try:
        import pygame
        import mendeleev
        print(f"✓ pygame {pygame.version.vernum} is installed")
        print(f"✓ mendeleev {mendeleev.__version__} is installed")
        return True
    except ImportError as e:
        print(f"pygame or mendeleev is not installed. Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "mendeleev"])
            print("✓ pygame installed successfully")
            print("✓ mendeleev installed successfully")
            return True
        except subprocess.CalledProcessError:
            print("✗ Failed to install pygame or mendeleev")
            print("Please install manually: pip install pygame mendeleev")
            return False


def main():
    renderer = PygameRenderer(width=1200, height=800)
    renderer.initialize()

    clock = pygame.time.Clock()
    running = True

    # Layout regions
    flask_bounds = {'x': 40, 'y': 40, 'width': 360, 'height': 720}
    thermometer_bounds = {'x': 980, 'y': 120, 'width': 60, 'height': 420}

    # Sample chemicals + droppers
    chems = make_sample_chemicals()
    droppers: List[Dropper] = []
    top_y = 60
    start_x = 460
    spacing = 90
    for i, chem in enumerate(chems):
        d = Dropper(start_x + i * spacing, top_y, chem, moles_per_drop=0.05, width=64, height=80)
        droppers.append(d)

    # Example titration dropper (not used visually here but ready)
    titration = TitrationDropper(start_x + len(chems) * spacing, top_y, chems[0], moles_per_drop=0.01, sip_rate=0.01)
    droppers.append(titration)

    # Hotplate state
    hotplate = {'x': 1040, 'y': 190, 'width': 60, 'height': 60, 'is_on': False, 'heat_level': 0.0, 'label': 'Heat'}

    # Magnifier icons (right column)
    magnifiers = []
    mag_x = 1120
    mag_y = 100
    for i in range(4):
        rect = pygame.Rect(mag_x, mag_y + i * 90, 40, 40)
        magnifiers.append(rect)

    # Particle preview state (for magnifier hover)
    preview_particles = []
    last_time = time.time()

    temp = 293.15  # Kelvin

    while running:
        dt = clock.tick(60) / 1000.0
        now = time.time()
        elapsed = now - last_time
        last_time = now

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Droppers
                for d in droppers:
                    if d.on_mouse_down(mx, my):
                        # immediate dispense for normal droppers
                        if not isinstance(d, TitrationDropper):
                            info = d.dispense()
                            info['chemical'].add_moles(info['moles'])
                            d.on_mouse_up()
                # Hotplate
                hx, hy, hw, hh = hotplate['x'], hotplate['y'], hotplate['width'], hotplate['height']
                if hx <= mx <= hx + hw and hy <= my <= hy + hh:
                    hotplate['is_on'] = not hotplate['is_on']
            elif event.type == pygame.MOUSEBUTTONUP:
                mx, my = pygame.mouse.get_pos()
                for d in droppers:
                    d.on_mouse_up()

            elif event.type == pygame.MOUSEWHEEL:
                # Placeholder: scroll support could be wired to panels
                pass

        # Update droppers (cooldowns) and handle titration hold dispensing
        mx, my = pygame.mouse.get_pos()
        for d in droppers:
            d.on_mouse_move(mx, my)
            d.update(dt)
            if isinstance(d, TitrationDropper) and d.holding:
                dispense = d.get_hold_dispense(dt)
                if dispense:
                    # apply to chemical object (visual only)
                    dispense['chemical'].add_moles(dispense['moles'])

        # Update hotplate heat level
        if hotplate['is_on']:
            hotplate['heat_level'] = min(1.0, hotplate['heat_level'] + dt * 0.2)
            temp += dt * 5.0 * hotplate['heat_level']
        else:
            hotplate['heat_level'] = max(0.0, hotplate['heat_level'] - dt * 0.05)
            temp = max(273.15, temp - dt * 1.0)

        # Update preview particles when hovering a magnifier
        hovering_preview = any(rect.collidepoint((mx, my)) for rect in magnifiers)
        if hovering_preview:
            # spawn a few preview particles inside flask bounds
            for _ in range(3):
                px = flask_bounds['x'] + 20 + (flask_bounds['width'] - 40) * random.random()
                py = flask_bounds['y'] + 20 + (flask_bounds['height'] - 40) * random.random()
                preview_particles.append({'x': px, 'y': py, 'vx': (random.random() - 0.5) * 40,
                                          'vy': -abs(random.random() * 30), 'radius': 4, 'color_hex': '#DDDDFF', 'alpha': 1.0, 'age': 0.0})

        # step preview particles
        for p in list(preview_particles):
            p['x'] += p['vx'] * dt
            p['y'] += p['vy'] * dt
            p['vy'] += 40 * dt  # gravity-like
            p['age'] += dt
            p['alpha'] = max(0.0, 1.0 - p['age'] / 1.5)
            if p['age'] > 1.5:
                preview_particles.remove(p)

        # Build render data
        renderer.clear()

        # Flask visual (large left rectangle)
        flask_color = '#FFFFFF'
        is_boiling = temp > 373.15
        renderer.render_flask({'color_hex': flask_color, 'temperature': temp, 'bounds': flask_bounds, 'is_boiling': is_boiling})

        # Draw preview particles into flask (as if magnifier shows them)
        renderer.render_particles(preview_particles)

        # Render droppers
        ui_elements = []
        for d in droppers:
            ui_elements.append({'type': 'dropper', 'data': d.get_render_data()})
        # Render thermometer and hotplate
        fill_percent = (temp - 273.15) / (373.15 - 273.15)
        fill_percent = max(0.0, min(1.0, fill_percent))
        fill_height = int(thermometer_bounds['height'] * fill_percent)
        fill_y = thermometer_bounds['y'] + thermometer_bounds['height'] - fill_height
        thermo_data = {
            'x': thermometer_bounds['x'], 'y': thermometer_bounds['y'], 'width': thermometer_bounds['width'], 'height': thermometer_bounds['height'],
            'background_color': '#E8E8E8', 'fill_height': fill_height, 'fill_y': fill_y, 'fill_color': '#6D6D7A', 'border_color': '#333333',
            'bulb_x': thermometer_bounds['x'] + thermometer_bounds['width'] // 2, 'bulb_y': thermometer_bounds['y'] + thermometer_bounds['height'] + 20,
            'bulb_radius': 24, 'bulb_color': '#6D6D7A', 'temperature_text': f"{temp - 273.15:.1f}°C"
        }

        ui_elements.append({'type': 'thermometer', 'data': thermo_data})

        hotplate_data = {'x': hotplate['x'], 'y': hotplate['y'], 'width': hotplate['width'], 'height': hotplate['height'], 'color': '#9E9E9E', 'border_color': '#333333', 'label': hotplate['label'], 'is_on': hotplate['is_on'], 'heat_level': hotplate['heat_level']}
        ui_elements.append({'type': 'hotplate', 'data': hotplate_data})

        renderer.render_ui_elements(ui_elements)

        # Draw magnifier icons
        for rect in magnifiers:
            pygame.draw.rect(renderer.screen, (220, 220, 220), rect)
            pygame.draw.rect(renderer.screen, (120, 120, 120), rect, 2)

        renderer.render_fps(clock.get_fps())
        renderer.flip()

    renderer.quit()


if __name__ == '__main__':
    main()
