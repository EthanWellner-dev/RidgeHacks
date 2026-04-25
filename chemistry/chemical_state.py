"""
ChemicalState - Central state management for all chemicals and reactions.
"""

import json
import os
from chemistry.chemical import Chemical
from chemistry.reaction import Reaction


class ChemicalState:
    """
    Tracks all chemicals, reactions, and thermodynamic conditions.
    Acts as the hub for chemistry calculations each frame.
    """
    
    def __init__(self, volume: float, temperature: float = 293.15):
        """
        Initialize the chemical state.
        
        Args:
            volume: Container volume in liters
            temperature: Initial temperature in Kelvin (default 293.15K = 20°C)
        """
        self.volume = volume
        self.temperature = temperature
        self.pressure = 1.0  # atm (will be calculated from ideal gas law)
        
        self.chemicals = {}      # {Chemical: moles}
        self.reactions = []      # [Reaction, ...]
        self.catalyst_factor = 1.0
        
        # Cache for chemical objects created from database
        self._chemical_cache = {}  # {name: Chemical}
    
    def react(self) -> None:
        """With the addition of a new component, update all reactions and shift chemicals accordingly."""
        
        # Get all current chemical objects
        current_chemicals = set(self.chemicals.keys())
        
        # Check existing reactions - keep only those that can still occur
        applicable_reactions = []
        for reaction in self.reactions:
            # A reaction is applicable if all its reactants are present
            reactants_available = all(
                chemical in current_chemicals 
                for chemical in reaction.reactants.keys()
            )
            
            if reactants_available:
                applicable_reactions.append(reaction)
        
        # Update reactions list to only include applicable ones
        self.reactions = applicable_reactions
        
        # Load new applicable reactions from database based on current chemicals
        self.load_reactions_from_database()
        

    def load_reactions_from_database(self, db_path: str = None) -> None:
        """
        Load reactions from the database JSON file and add applicable ones to the system.
        
        Args:
            db_path: Path to the database JSON file. If None, uses default 'db.json'
        """
        if db_path is None:
            # Find db.json in the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # Go up one level from chemistry/
            db_path = os.path.join(project_root, 'db.json')
        
        try:
            with open(db_path, 'r') as f:
                db = json.load(f)
        except FileNotFoundError:
            print(f"Warning: Database file not found at {db_path}")
            return
        except json.JSONDecodeError:
            print(f"Warning: Invalid JSON in database file {db_path}")
            return
        
        # Load reactions from database
        reactions_data = db.get('reactions', {})
        molecules_data = db.get('molecules', {})
        
        for reaction_name, reaction_data in reactions_data.items():
            try:
                # Create reactant Chemical objects
                reactants = {}
                for chem_name, coeff in reaction_data['reactants'].items():
                    chem_obj = self._get_or_create_chemical(chem_name, molecules_data)
                    if chem_obj:
                        reactants[chem_obj] = coeff
                
                # Create product Chemical objects
                products = {}
                for chem_name, coeff in reaction_data['products'].items():
                    chem_obj = self._get_or_create_chemical(chem_name, molecules_data)
                    if chem_obj:
                        products[chem_obj] = coeff
                
                # Only create reaction if we have valid reactants and products
                if reactants and products:
                    reaction = Reaction(
                        name=reaction_name,
                        reactants=reactants,
                        products=products,
                        kc=reaction_data.get('kc', 1.0),
                        rate_constant=reaction_data.get('rate_constant', 1.0),
                        delta_h=reaction_data.get('delta_h', 0.0),
                        activation_energy=reaction_data.get('activation_energy', 50.0)
                    )
                    
                    # Check if this reaction is applicable (all reactants exist in current state)
                    reactants_available = all(
                        chemical in self.chemicals 
                        for chemical in reaction.reactants.keys()
                    )
                    
                    if reactants_available:
                        self.add_reaction(reaction)
                        
            except (KeyError, TypeError) as e:
                print(f"Warning: Invalid reaction data for '{reaction_name}': {e}")
                continue
    
    def _get_or_create_chemical(self, name: str, molecules_data: dict) -> Chemical:
        """
        Get a Chemical object from cache or create it from database data.
        
        Args:
            name: Chemical name (may include state like "H2(g)")
            molecules_data: Molecules section from database
            
        Returns:
            Chemical object or None if creation fails
        """
        # Check cache first
        if name in self._chemical_cache:
            return self._chemical_cache[name]
        
        # Try to create from database
        if name in molecules_data:
            mol_data = molecules_data[name]
            try:
                chemical = Chemical(
                    name=name,
                    components=mol_data['components'],
                    moles=0.0,  # Will be set when added to state
                    color_hex=mol_data['color_hex'],
                    enthalpy=mol_data['enthalpy'],
                    state=mol_data.get('state', 'gas')  # Default to gas if not specified
                )
                self._chemical_cache[name] = chemical
                return chemical
            except (KeyError, TypeError) as e:
                print(f"Warning: Invalid molecule data for '{name}': {e}")
                return None
        
        # If not in database, try to create a basic chemical (for generic names)
        print(f"Warning: Chemical '{name}' not found in database, creating basic entry")
        try:
            # Create a basic chemical with empty components (will need manual definition)
            chemical = Chemical(
                name=name,
                components=[],  # Empty components - needs to be defined manually
                moles=0.0,
                color_hex="#808080",  # Gray for unknown
                enthalpy=0.0,
                state="gas"  # Default state
            )
            self._chemical_cache[name] = chemical
            return chemical
        except Exception as e:
            print(f"Error creating basic chemical '{name}': {e}")
            return None
        # 1. Querying a reaction database or registry for possible reactions
        # 2. Checking if each possible reaction is already in self.reactions
        # 3. Adding new applicable reactions via add_reaction()
        

    def add_chemical(self, chemical: Chemical, moles: float) -> None:
        """
        Add or update a chemical in the state.
        
        Args:
            chemical: Chemical object to add
            moles: Moles to add (or total if new)
        """
        if chemical not in self.chemicals:
            self.chemicals[chemical] = 0.0
        
        self.chemicals[chemical] += moles
        self.chemicals[chemical] = max(0, self.chemicals[chemical])
        
        # Update concentration immediately
        chemical.update_concentration(self.volume)
        self.react()  # Check for reaction updates after adding chemical
    
    def add_reaction(self, reaction: Reaction) -> None:
        """Add a reaction to the system."""
        if reaction not in self.reactions:
            self.reactions.append(reaction)
    
    def set_temperature(self, temperature: float) -> None:
        """Set system temperature in Kelvin."""
        self.temperature = max(0, temperature)
    
    def set_catalyst_factor(self, factor: float) -> None:
        """
        Set global catalyst multiplier (affects all reactions).
        
        Args:
            factor: Multiplier (1.0 = no catalyst, >1 = accelerates)
        """
        self.catalyst_factor = max(0, factor)
    
    def update_concentrations(self) -> None:
        """Recalculate all chemical concentrations based on moles and volume."""
        for chemical in self.chemicals.keys():
            chemical.update_concentration(self.volume)
    
    def update(self, delta_time: float) -> dict:
        """
        Update all reactions and recalculate equilibrium.
        Shifts chemicals based on reaction directions.
        
        Args:
            delta_time: Time step in seconds
        
        Returns:
            dict with 'total_heat_change' (kJ) and 'reactions_fired'
        """
        self.update_concentrations()
        
        total_heat_change = 0.0
        reactions_fired = []
        
        for reaction in self.reactions:
            # Determine reaction direction
            direction = reaction.calculate_shift()
            
            if direction == "equilibrium":
                continue
            
            # Calculate reaction rate
            rate = reaction.calculate_rate(self.temperature, self.catalyst_factor)
            
            # Calculate extent of reaction for this time step
            reaction_extent = rate * delta_time
            
            # Clamp extent to physically reasonable value
            reaction_extent = min(reaction_extent, 0.1)
            
            if reaction_extent > 0:
                reactions_fired.append(reaction.name)
                
                # Apply reaction shift
                if direction == "forward":
                    # Consume reactants, produce products
                    for chemical, coeff in reaction.reactants.items():
                        self.add_chemical(chemical, -coeff * reaction_extent)
                    for chemical, coeff in reaction.products.items():
                        self.add_chemical(chemical, coeff * reaction_extent)
                    
                    heat_change = reaction.get_heat_change(reaction_extent)
                
                elif direction == "reverse":
                    # Consume products, produce reactants
                    for chemical, coeff in reaction.products.items():
                        self.add_chemical(chemical, -coeff * reaction_extent)
                    for chemical, coeff in reaction.reactants.items():
                        self.add_chemical(chemical, coeff * reaction_extent)
                    
                    heat_change = -reaction.get_heat_change(reaction_extent)
                
                total_heat_change += heat_change
        
        # Update concentrations after reactions
        self.update_concentrations()
        
        return {
            'total_heat_change': total_heat_change,
            'reactions_fired': reactions_fired
        }
    
    def get_net_color(self) -> str:
        """
        Blend colors based on all chemicals present.
        Weighted by concentration of each chemical.
        
        Returns:
            Hex color string (e.g., "#FF00FF")
        """
        if not self.chemicals:
            return "#FFFFFF"  # Default white
        
        total_concentration = sum(c.concentration for c in self.chemicals.keys())
        
        if total_concentration == 0:
            return "#FFFFFF"
        
        # Convert hex to RGB, weight by concentration, average
        r_sum = 0.0
        g_sum = 0.0
        b_sum = 0.0
        
        for chemical, _ in self.chemicals.items():
            weight = chemical.concentration / total_concentration
            
            # Parse hex color
            hex_color = chemical.color_hex.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r_sum += r * weight
            g_sum += g * weight
            b_sum += b * weight
        
        # Convert back to hex
        r = int(round(r_sum))
        g = int(round(g_sum))
        b = int(round(b_sum))
        
        return f"#{r:02X}{g:02X}{b:02X}"
    
    def get_net_temperature_change(self) -> float:
        """
        Calculate cumulative temperature change from recent reactions.
        (To be called each update and used to modify system temperature)
        
        Returns:
            Temperature change in Kelvin
        """
        # This is simplified; in reality you'd track heat capacity
        # For now, return placeholder
        return 0.0
    
    def __repr__(self) -> str:
        chem_str = ", ".join([f"{c.name}: {m:.2f} mol" for c, m in self.chemicals.items()])
        return f"ChemicalState(T={self.temperature}K, V={self.volume}L, Chemicals: {chem_str})"
