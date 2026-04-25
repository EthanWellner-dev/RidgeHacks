"""
Challenge - Goal-oriented puzzle scenarios.
"""

from chemistry.flask import Flask
from chemistry.chemical import Chemical


class Challenge:
    """
    Represents a single goal-oriented puzzle scenario.
    Manages initial state, win/loss conditions, and time limits.
    """
    
    def __init__(self, name: str, description: str, 
                 initial_chemicals: dict,
                 initial_temperature: float,
                 win_conditions: dict,
                 loss_conditions: dict = None,
                 time_limit: float = None,
                 flask_volume: float = 1.0):
        """
        Initialize a challenge.
        
        Args:
            name: Challenge name (e.g., "Color Shift")
            description: Challenge description/instructions
            initial_chemicals: {Chemical: moles} to start with
            initial_temperature: Starting temperature in Kelvin
            win_conditions: dict with required conditions
                - 'target_color': hex color to achieve
                - 'min_gas': minimum moles of gas
                - 'max_temp': maximum allowed temperature
                - 'min_temp': minimum required temperature
            loss_conditions: dict with failure conditions (optional)
                - 'max_temp': boiling temperature
                - 'timeout': time limit exceeded
            time_limit: Optional time limit in seconds
            flask_volume: Container volume in liters
        """
        self.name = name
        self.description = description
        self.initial_chemicals = initial_chemicals
        self.initial_temperature = float(initial_temperature)
        self.win_conditions = win_conditions or {}
        self.loss_conditions = loss_conditions or {'max_temp': 373.15}  # Default boil point
        # Challenges no longer use an enforced timer; keep value for backward compatibility but ignore it
        self.time_limit = None
        self.flask_volume = float(flask_volume)
        
        # Runtime state
        self.flask = None
        self.elapsed_time = 0.0
        self.state = "not_started"  # not_started, in_progress, won, lost
        self.loss_reason = None
    
    def initialize_flask(self) -> Flask:
        """
        Create and initialize a flask with challenge starting conditions.
        
        Returns:
            Flask object configured for this challenge
        """
        self.flask = Flask(self.flask_volume, max_temperature=self.loss_conditions.get('max_temp', 373.15))
        self.flask.set_temperature(self.initial_temperature)
        
        # Add initial chemicals
        for chemical, moles in self.initial_chemicals.items():
            self.flask.add_reactant(chemical, moles)
        
        self.state = "in_progress"
        self.elapsed_time = 0.0
        self.loss_reason = None
        
        return self.flask
    
    def update(self, delta_time: float) -> dict:
        """
        Update challenge state and check win/loss conditions.
        
        Args:
            delta_time: Time step in seconds
        
        Returns:
            dict with 'status' (in_progress/won/lost) and 'message'
        """
        if self.state in ["won", "lost"]:
            return {'status': self.state, 'message': self.get_state_message()}
        
        # Check loss conditions
        loss_status = self.check_loss_condition()
        if loss_status:
            self.state = "lost"
            # Some loss_status variants may return 'message' instead of 'reason'
            self.loss_reason = loss_status.get('message', loss_status.get('reason', None))
            return loss_status
        
        # Check win conditions
        win_status = self.check_win_condition()
        if win_status:
            self.state = "won"
            return win_status
        
        return {'status': 'in_progress', 'message': ''}
    
    def check_win_condition(self) -> dict:
        """
        Validate all win conditions.
        
        Returns:
            None if conditions not met, else dict with status and message
        """
        if not self.flask:
            return None
        
        visual_data = self.flask.get_visual_data()
        
        # Check target color
        if 'target_color' in self.win_conditions:
            target = self.win_conditions['target_color'].upper()
            current = visual_data['color_hex'].upper()
            
            # Allow some color tolerance (simple hex comparison)
            if target != current:
                return None
        
        # Check minimum gas production (sum of gaseous species moles)
        if 'min_gas' in self.win_conditions:
            try:
                gas_threshold = float(self.win_conditions['min_gas'])
                total_gas = 0.0
                for chem, moles in self.flask.chemical_state.chemicals.items():
                    if getattr(chem, 'state', 'gas') == 'gas':
                        total_gas += moles
                if total_gas < gas_threshold:
                    return None
            except Exception:
                return None

        # Check for a specific target chemical produced from given reagents
        if 'target_chemical' in self.win_conditions:
            target_name = self.win_conditions['target_chemical']
            required_moles = float(self.win_conditions.get('target_moles', 0.0))
            found = False
            for chem, moles in self.flask.chemical_state.chemicals.items():
                if Chemical._normalize_name(getattr(chem, 'name', '')) == Chemical._normalize_name(target_name):
                    if moles >= required_moles:
                        found = True
                        break
            if not found:
                return None
        
        # Check temperature constraints
        if 'max_temp' in self.win_conditions:
            if visual_data['temperature'] > self.win_conditions['max_temp']:
                return None
        
        if 'min_temp' in self.win_conditions:
            if visual_data['temperature'] < self.win_conditions['min_temp']:
                return None
        
        # All conditions met!
        return {
            'status': 'won',
            'message': f"🎉 Challenge '{self.name}' completed in {self.elapsed_time:.1f}s!",
            'time_taken': self.elapsed_time
        }
    
    def check_loss_condition(self) -> dict:
        """
        Check if failure conditions are triggered.
        
        Returns:
            None if still playing, else dict with status and message
        """
        if not self.flask:
            return None
        
        visual_data = self.flask.get_visual_data()
        
        # Check temperature limit
        if 'max_temp' in self.loss_conditions:
            if visual_data['temperature'] > self.loss_conditions['max_temp']:
                return {
                    'status': 'lost',
                    'message': f"❌ Flask boiled at {visual_data['temperature']:.1f}K! Challenge failed."
                }
        
        # No timeouts for challenges — timing removed
        
        return None
    
    def get_state_message(self) -> str:
        """Get current challenge state message."""
        if self.state == "won":
            return f"Challenge won in {self.elapsed_time:.1f}s!"
        elif self.state == "lost":
            return self.loss_reason or "Challenge failed."
        elif self.state == "in_progress":
            time_left = ""
            if self.time_limit:
                time_left = f" ({self.time_limit - self.elapsed_time:.1f}s left)"
            return f"Challenge in progress...{time_left}"
        else:
            return "Not started"
    
    def get_render_data(self) -> dict:
        """
        Get visual data for rendering challenge info.
        
        Returns:
            dict with challenge display information
        """
        return {
            'name': self.name,
            'description': self.description,
            'status': self.state,
            'message': self.get_state_message(),
            'time_elapsed': self.elapsed_time,
            'time_limit': None,
            'win_conditions': self.win_conditions,
            'current_color': self.flask.color_hex if self.flask else "#FFFFFF",
            'current_temp': self.flask.chemical_state.get_average_temperature() if self.flask else 293.15
        }
    
    def __repr__(self) -> str:
        return f"Challenge('{self.name}', status={self.state}, time={self.elapsed_time:.1f}s)"


class ChallengeLibrary:
    """
    Collection of predefined challenge scenarios.
    """
    
    @staticmethod
    def create_color_shift_challenge() -> Challenge:
        """
        Challenge 1: Shift the color from yellow to orange by adjusting pH.
        """
        # Chromate/dichromate color shift (simplified)
        chromate = Chemical("CrO4^2-(aq)", [("Cr", 1), ("O", 4)], 0.5, "#FFD700", 0, "aqueous")  # Yellow
        acid = Chemical("H+(aq)", [("H", 1)], 0.0, "#FFFFFF", 0, "aqueous")
        
        return Challenge(
            name="Color Shift",
            description="The flask contains chromate (yellow). Add acid to shift the color to orange (dichromate).",
            initial_chemicals={chromate: 0.5},
            initial_temperature=293.15,
            win_conditions={
                'target_color': '#FFA500'  # Orange
            },
        )
        
    
    @staticmethod
    def create_gas_production_challenge() -> Challenge:
        """
        Challenge 2: Produce O2 gas rapidly without overheating.
        """
        h2o2 = Chemical("H2O2", [("H", 2), ("O", 2)], 1.0, "#CCCCCC", 0)
        catalyst = Chemical("MnO2", [("Mn", 1), ("O", 2)], 0.1, "#404040", 0)
        o2 = Chemical("O2", [("O", 2)], 0.0, "#87CEEB", 0)
        
        return Challenge(
            name="Gas Burst",
            description="Produce 0.5 moles of O2 without overheating (no timer).",
            initial_chemicals={h2o2: 1.0},
            initial_temperature=293.15,
            win_conditions={
                'min_gas': 0.5,
                'max_temp': 350.0
            },
        )
        
    
    @staticmethod
    def create_equilibrium_balance_challenge() -> Challenge:
        """
        Challenge 3: Maintain equilibrium at exactly target color.
        """
        reactant_a = Chemical("Reactant A", [("A", 1)], 1.0, "#FF0000", 50)
        product_b = Chemical("Product B", [("B", 1)], 0.0, "#0000FF", -50)
        
        return Challenge(
            name="Equilibrium Balance",
            description="Adjust temperature to achieve a purple color (#800080) without boiling.",
            initial_chemicals={reactant_a: 1.0, product_b: 0.0},
            initial_temperature=293.15,
            win_conditions={
                'target_color': '#800080',
                'max_temp': 373.15
            },
            loss_conditions={'max_temp': 373.15},
        )
