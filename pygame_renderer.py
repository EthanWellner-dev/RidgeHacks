"""
pygame_renderer.py - Rendering layer for all game visuals.
Converts backend data into pygame graphics.
"""

import pygame
import math
from typing import Dict, List, Tuple


class PygameRenderer:
    """
    Handles all rendering of game elements to pygame surface.
    """
    
    def __init__(self, width: int = 1200, height: int = 800):
        """
        Initialize renderer.
        
        Args:
            width: Screen width in pixels
            height: Screen height in pixels
        """
        self.width = width
        self.height = height
        self.screen = None
        
        # Color palette
        self.colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0),
            'gray': (128, 128, 128),
            'dark_gray': (64, 64, 64),
            'light_gray': (200, 200, 200),
            'background': (240, 245, 250)
        }
        
        # Fonts (loaded on first use)
        self.fonts = {}
        self.font_sizes = {
            'small': 12,
            'medium': 16,
            'large': 24,
            'title': 36
        }
    
    def initialize(self) -> None:
        """Initialize pygame display."""
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Dynamic ChemEngine")
        self._load_fonts()
    
    def _load_fonts(self) -> None:
        """Load all fonts."""
        for name, size in self.font_sizes.items():
            self.fonts[name] = pygame.font.Font(None, size)
    
    def _hex_to_rgb(self, hex_color: str) -> Tuple[int, int, int]:
        """
        Convert hex color to RGB tuple.
        
        Args:
            hex_color: Color in hex format (e.g., "#FF0000")
        
        Returns:
            (R, G, B) tuple
        """
        hex_color = hex_color.lstrip('#')
        try:
            return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        except:
            return self.colors['gray']
    
    def _clamp_color(self, rgb: Tuple[int, int, int]) -> Tuple[int, int, int]:
        """Clamp RGB values to 0-255 range."""
        return tuple(max(0, min(255, c)) for c in rgb)
    
    def clear(self) -> None:
        """Clear screen with background color."""
        self.screen.fill(self.colors['background'])
    
    def render_flask(self, flask_data: Dict) -> None:
        """
        Render the flask container.
        
        Args:
            flask_data: dict with 'color_hex', 'temperature', 'bounds', 'is_boiling'
        """
        bounds = flask_data['bounds']
        x = bounds['x']
        y = bounds['y']
        width = bounds['width']
        height = bounds['height']
        
        # Flask background (main color)
        color_rgb = self._hex_to_rgb(flask_data['color_hex'])
        color_rgb = self._clamp_color(color_rgb)
        pygame.draw.rect(self.screen, color_rgb, (x, y, width, height))
        
        # Flask border
        border_color = (0, 0, 0) if not flask_data['is_boiling'] else (255, 0, 0)
        border_width = 4 if flask_data['is_boiling'] else 3
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), border_width)
        
        # Boiling effect (animated shimmer)
        if flask_data['is_boiling']:
            self._render_boiling_effect(x, y, width, height)
    
    def _render_boiling_effect(self, x: float, y: float, width: float, height: float) -> None:
        """Render boiling water visual effect."""
        num_bubbles = 5
        for i in range(num_bubbles):
            bubble_x = x + (i + 1) * width / (num_bubbles + 1)
            bubble_y = y + height - 20
            pygame.draw.circle(self.screen, (200, 200, 200), (int(bubble_x), int(bubble_y)), 3, 1)
    
    def render_particles(self, particles: List[Dict]) -> None:
        """
        Render all particles.
        
        Args:
            particles: List of dicts with 'x', 'y', 'radius', 'color_hex', 'alpha'
        """
        for particle in particles:
            x = int(particle['x'])
            y = int(particle['y'])
            radius = int(particle['radius'])
            color_rgb = self._hex_to_rgb(particle['color_hex'])
            alpha = particle.get('alpha', 1.0)
            
            # Create a temporary surface for transparency
            if 0 < alpha < 1:
                particle_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                alpha_int = int(255 * alpha)
                color_with_alpha = (*color_rgb, alpha_int)
                pygame.draw.circle(particle_surface, color_with_alpha, (radius, radius), radius)
                self.screen.blit(particle_surface, (x - radius, y - radius))
            else:
                pygame.draw.circle(self.screen, color_rgb, (x, y), radius)
    
    def render_dropper(self, dropper_data: Dict) -> None:
        """
        Render a dropper UI button.
        
        Args:
            dropper_data: dict with position, size, color, label, cooldown
        """
        x = int(dropper_data['x'])
        y = int(dropper_data['y'])
        width = int(dropper_data['width'])
        height = int(dropper_data['height'])
        color = self._hex_to_rgb(dropper_data['color'])
        border_color = self._hex_to_rgb(dropper_data['border_color'])
        
        # Draw button
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 
                        int(dropper_data['border_width']))
        
        # Draw label
        label = dropper_data['label']
        label_surface = self.fonts['medium'].render(label, True, border_color)
        label_rect = label_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(label_surface, label_rect)
        
        # Draw cooldown indicator
        cooldown = dropper_data['cooldown']
        if cooldown > 0:
            cooldown_max = dropper_data['cooldown_max']
            cooldown_percent = cooldown / cooldown_max
            bar_height = int(height * cooldown_percent)
            pygame.draw.rect(self.screen, (100, 100, 100), (x, y + height - bar_height, width, bar_height))
    
    def render_thermometer(self, thermo_data: Dict) -> None:
        """
        Render a thermometer UI element.
        
        Args:
            thermo_data: dict with position, size, fill info, colors
        """
        x = int(thermo_data['x'])
        y = int(thermo_data['y'])
        width = int(thermo_data['width'])
        height = int(thermo_data['height'])
        
        # Background
        pygame.draw.rect(self.screen, self._hex_to_rgb(thermo_data['background_color']), 
                        (x, y, width, height))
        
        # Fill (colored part)
        fill_height = int(thermo_data['fill_height'])
        fill_y = int(thermo_data['fill_y'])
        fill_color = self._hex_to_rgb(thermo_data['fill_color'])
        pygame.draw.rect(self.screen, fill_color, (x, fill_y, width, fill_height))
        
        # Border
        border_color = self._hex_to_rgb(thermo_data['border_color'])
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)
        
        # Bulb at bottom
        bulb_x = int(thermo_data['bulb_x'])
        bulb_y = int(thermo_data['bulb_y'])
        bulb_radius = int(thermo_data['bulb_radius'])
        bulb_color = self._hex_to_rgb(thermo_data['bulb_color'])
        pygame.draw.circle(self.screen, bulb_color, (bulb_x, bulb_y), bulb_radius)
        pygame.draw.circle(self.screen, border_color, (bulb_x, bulb_y), bulb_radius, 2)
        
        # Temperature text
        temp_text = thermo_data['temperature_text']
        temp_surface = self.fonts['small'].render(temp_text, True, (0, 0, 0))
        self.screen.blit(temp_surface, (x - 30, bulb_y - 5))
    
    def render_hotplate(self, hotplate_data: Dict) -> None:
        """
        Render a hotplate UI control.
        
        Args:
            hotplate_data: dict with position, size, state, heat level
        """
        x = int(hotplate_data['x'])
        y = int(hotplate_data['y'])
        width = int(hotplate_data['width'])
        height = int(hotplate_data['height'])
        color = self._hex_to_rgb(hotplate_data['color'])
        border_color = self._hex_to_rgb(hotplate_data['border_color'])
        
        # Draw button
        pygame.draw.rect(self.screen, color, (x, y, width, height))
        pygame.draw.rect(self.screen, border_color, (x, y, width, height), 2)
        
        # Draw label
        label = hotplate_data['label']
        state = "ON" if hotplate_data['is_on'] else "OFF"
        label_text = f"{label}\n{state}"
        label_surface = self.fonts['small'].render(label_text, True, (0, 0, 0))
        label_rect = label_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(label_surface, label_rect)
        
        # Heat level indicator
        if hotplate_data['is_on']:
            level = hotplate_data['heat_level']
            indicator_height = int(height * level)
            pygame.draw.rect(self.screen, (255, 100, 0), (x + 2, y + height - indicator_height - 2, 
                                                          width - 4, indicator_height))
    
    def render_ui_elements(self, ui_elements: List[Dict]) -> None:
        """
        Render all UI elements.
        
        Args:
            ui_elements: List of dicts with 'type' and 'data'
        """
        for element in ui_elements:
            element_type = element['type']
            data = element['data']
            
            if element_type == 'dropper':
                self.render_dropper(data)
            elif element_type == 'thermometer':
                self.render_thermometer(data)
            elif element_type == 'hotplate':
                self.render_hotplate(data)
    
    def render_challenge_info(self, challenge_data: Dict) -> None:
        """
        Render challenge information overlay.
        
        Args:
            challenge_data: dict with name, description, status, time, conditions
        """
        # Left area: title and status
        left_x = 20
        left_y = 20

        title_text = f"Challenge: {challenge_data['name']}"
        title_surface = self.fonts['large'].render(title_text, True, (0, 0, 0))
        self.screen.blit(title_surface, (left_x, left_y))
        left_y += 35

        desc_text = challenge_data.get('description', '')
        desc_surface = self.fonts['small'].render(desc_text, True, (64, 64, 64))
        self.screen.blit(desc_surface, (left_x, left_y))
        left_y += 24

        # Time (if present)
        if challenge_data.get('time_limit'):
            time_text = f"Time: {challenge_data['time_elapsed']:.1f}s / {challenge_data['time_limit']:.0f}s"
            time_surface = self.fonts['medium'].render(time_text, True, (0, 0, 0))
            self.screen.blit(time_surface, (left_x, left_y))
            left_y += 25

            # Time progress bar
            bar_width = 200
            bar_height = 12
            pygame.draw.rect(self.screen, (220, 220, 220), (left_x, left_y, bar_width, bar_height))
            progress_width = int(bar_width * challenge_data.get('time_progress', 0.0))
            pygame.draw.rect(self.screen, (0, 150, 0), (left_x, left_y, progress_width, bar_height))
            pygame.draw.rect(self.screen, (0, 0, 0), (left_x, left_y, bar_width, bar_height), 1)

        # Right area: Objectives panel (scrollable)
        panel_w = 260
        panel_h = 380
        panel_x = self.width - panel_w - 20
        panel_y = 20

        # Panel background
        pygame.draw.rect(self.screen, (245, 245, 250), (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(self.screen, (0, 0, 0), (panel_x, panel_y, panel_w, panel_h), 2)

        # Panel title
        title_s = self.fonts['medium'].render('Objectives', True, (0, 0, 0))
        self.screen.blit(title_s, (panel_x + 12, panel_y + 8))

        # Prepare objective lines from win_conditions
        win = challenge_data.get('win_conditions', {})
        lines = []
        if 'target_color' in win:
            lines.append(f"Target color: {win['target_color']}")
        if 'min_gas' in win:
            lines.append(f"Produce ≥ {win['min_gas']} mol gas")
        if 'max_temp' in win:
            lines.append(f"Keep temp ≤ {win['max_temp']:.0f} K")
        if 'min_temp' in win:
            lines.append(f"Reach temp ≥ {win['min_temp']:.0f} K")

        # If no explicit lines, show description as objective
        if not lines:
            lines.append(challenge_data.get('description', ''))

        # Scroll offset (provided by GameMode)
        scroll = int(challenge_data.get('scroll_offset', 0))

        # Draw objective text with simple scrolling
        y_cursor = panel_y + 40 + scroll
        text_color = (30, 30, 30)
        for line in lines:
            text_surf = self.fonts['small'].render('• ' + line, True, text_color)
            # Only blit if inside panel area
            if y_cursor + text_surf.get_height() > panel_y and y_cursor < panel_y + panel_h:
                self.screen.blit(text_surf, (panel_x + 12, y_cursor))
            y_cursor += text_surf.get_height() + 8

        # Footer hint
        hint = self.fonts['small'].render('Scroll to view more', True, (100, 100, 100))
        self.screen.blit(hint, (panel_x + 12, panel_y + panel_h - 24))
    
    def render_status_message(self, message: str, x: float = None, y: float = None) -> None:
        """
        Render status/message text.
        
        Args:
            message: Message text
            x: X position (center if None)
            y: Y position (center if None)
        """
        if not message:
            return
        
        text_surface = self.fonts['large'].render(message, True, (0, 0, 0))
        
        if x is None:
            x = (self.width - text_surface.get_width()) // 2
        if y is None:
            y = (self.height - text_surface.get_height()) // 2
        
        # Draw background box
        padding = 10
        box_rect = text_surface.get_rect(topleft=(x - padding, y - padding))
        box_rect.width += padding * 2
        box_rect.height += padding * 2
        pygame.draw.rect(self.screen, (255, 255, 200), box_rect)
        pygame.draw.rect(self.screen, (0, 0, 0), box_rect, 2)
        
        self.screen.blit(text_surface, (x, y))
    
    def render_fps(self, fps: float) -> None:
        """
        Render FPS counter.
        
        Args:
            fps: Current frames per second
        """
        fps_text = f"FPS: {fps:.0f}"
        fps_surface = self.fonts['small'].render(fps_text, True, (0, 0, 0))
        self.screen.blit(fps_surface, (self.width - 100, 10))
    
    def render_main_menu(self, selected: int = 0) -> None:
        """
        Render main menu.
        
        Args:
            selected: Index of selected option (0=Sandbox, 1=Challenge, 2=Quit)
        """
        self.clear()
        
        # Title
        title = self.fonts['title'].render("Dynamic ChemEngine", True, (0, 0, 0))
        title_rect = title.get_rect(center=(self.width // 2, 100))
        self.screen.blit(title, title_rect)
        
        # Subtitle
        subtitle = self.fonts['medium'].render("Interactive Chemistry Simulator", True, (100, 100, 100))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 150))
        self.screen.blit(subtitle, subtitle_rect)
        
        # Menu options
        options = ["Sandbox Mode", "Challenge Mode", "Quit"]
        y_pos = 300
        
        for i, option in enumerate(options):
            color = (255, 0, 0) if i == selected else (0, 0, 0)
            option_surface = self.fonts['large'].render(option, True, color)
            option_rect = option_surface.get_rect(center=(self.width // 2, y_pos))
            self.screen.blit(option_surface, option_rect)
            y_pos += 80
        
        # Instructions
        instructions = self.fonts['small'].render("Use UP/DOWN arrows to select, ENTER to confirm", 
                                                 True, (100, 100, 100))
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height - 50))
        self.screen.blit(instructions, instructions_rect)
    
    def render_pause_overlay(self) -> None:
        """Render pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        pause_text = self.fonts['title'].render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(pause_text, pause_rect)
        
        # Instructions
        instructions = self.fonts['medium'].render("Press SPACE to resume", True, (200, 200, 200))
        instructions_rect = instructions.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instructions, instructions_rect)
    
    def flip(self) -> None:
        """Update display."""
        pygame.display.flip()
    
    def quit(self) -> None:
        """Shutdown pygame."""
        pygame.quit()
