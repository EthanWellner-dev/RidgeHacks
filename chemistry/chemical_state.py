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
            temperature: Initial temperature for all chemicals in Kelvin (default 293.15K = 20°C)
        """
        self.volume = volume
        self.pressure = 1.0  # atm (will be calculated from ideal gas law)
        
        self.chemicals = {}      # {Chemical: moles}
        self.reactions = []      # [Reaction, ...]
        self.catalyst_factor = 1.0
        
        # Cache for chemical objects created from database
        self._chemical_cache = {}  # {name: Chemical}
        
        # Set initial temperature for all chemicals
        self._initial_temperature = temperature
    
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
        
        # Generate additional reactions using chemical principles
        self.generate_reactions()
        

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
                    # Use name-based matching since chemicals might be manually created vs database-created
                    reactant_names = [chem.name for chem in reaction.reactants.keys()]
                    available_chemical_names = [chem.name for chem in self.chemicals.keys()]
                    reactants_available = all(
                        reactant_name in available_chemical_names
                        for reactant_name in reactant_names
                    )
                    
                    if reactants_available:
                        self.add_reaction(reaction)
                        
            except (KeyError, TypeError) as e:
                print(f"Warning: Invalid reaction data for '{reaction_name}': {e}")
                continue
    
    def generate_reactions(self) -> None:
        """
        Generate reactions that aren't in the database using chemical principles and heuristics.
        This includes acid-base, redox, precipitation, and other common reaction types.
        """
        # Generate different types of reactions
        self._generate_acid_base_reactions()
        self._generate_redox_reactions()
        self._generate_precipitation_reactions()
        self._generate_gas_dissolution_reactions()
        
        # Future: Add external database lookup
        # self._lookup_external_reactions()
    
    def save_reaction_to_database(self, reaction: Reaction, db_path: str = None) -> bool:
        """
        Save a reaction to the database JSON file if it doesn't already exist.
        Also saves any new chemical molecules to the database.
        
        Args:
            reaction: Reaction object to save
            db_path: Path to the database JSON file. If None, uses default 'db.json'
        
        Returns:
            True if saved successfully, False otherwise
        """
        if db_path is None:
            # Find db.json in the project root
            current_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.dirname(current_dir)  # Go up one level from chemistry/
            db_path = os.path.join(project_root, 'db.json')
        
        try:
            # Load existing database
            with open(db_path, 'r') as f:
                db = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            # Create basic database structure if it doesn't exist
            db = {
                "atoms": {},
                "molecules": {},
                "reactions": {}
            }
        
        # Check if reaction already exists
        reactions_data = db.get('reactions', {})
        if reaction.name in reactions_data:
            return False  # Reaction already exists
        
        # Convert reaction to database format
        reaction_data = {
            'reactants': {chem.name: coeff for chem, coeff in reaction.reactants.items()},
            'products': {chem.name: coeff for chem, coeff in reaction.products.items()},
            'kc': reaction.kc,
            'rate_constant': reaction.rate_constant,
            'delta_h': reaction.delta_h,
            'activation_energy': reaction.activation_energy
        }
        
        # Add reaction to database
        reactions_data[reaction.name] = reaction_data
        db['reactions'] = reactions_data
        
        # Save any new molecules to database
        molecules_data = db.get('molecules', {})
        for chem in list(reaction.reactants.keys()) + list(reaction.products.keys()):
            if chem.name not in molecules_data:
                # Add chemical to molecules database
                molecule_data = {
                    'components': chem.components,
                    'state': chem.state,
                    'color_hex': chem.color_hex,
                    'enthalpy': chem.enthalpy
                }
                molecules_data[chem.name] = molecule_data
        
        db['molecules'] = molecules_data
        
        # Save updated database
        with open(db_path, 'w') as f:
            json.dump(db, f, indent=4)
        
        print(f"Saved reaction '{reaction.name}' to database")
        return True
        """
        Look up reactions from external databases for chemicals currently in the system.
        This is a framework for future implementation.
        
        Args:
            use_nist: Whether to query NIST Chemistry WebBook
            use_pubchem: Whether to query PubChem
        """
        if not (use_nist or use_pubchem):
            return
        
        print("External reaction lookup not yet implemented.")
        print("Future implementation would:")
        print("- Query NIST Chemistry WebBook API for reaction data")
        print("- Query PubChem for reaction information")
        print("- Filter for thermodynamically feasible reactions")
        print("- Convert external data to internal Reaction format")
        print("- Estimate missing kinetic parameters")
        
        # Placeholder for implementation
        # 
        # For NIST Chemistry WebBook:
        # - API: https://webbook.nist.gov/chemistry/
        # - Would need to search for reactions involving current chemicals
        # - Parse reaction data and thermodynamic parameters
        #
        # For PubChem:
        # - API: https://pubchem.ncbi.nlm.nih.gov/rest/pug
        # - Could query for reactions by compound names
        # - Extract reaction stoichiometry and conditions
        #
        # Common challenges:
        # - API rate limits and authentication
        # - Converting external reaction formats to internal format
        # - Estimating missing parameters (rate constants, activation energies)
        # - Filtering negligible reactions based on thermodynamics
        # - Handling different units and conditions
    
    def _generate_acid_base_reactions(self) -> None:
        """Generate acid-base neutralization reactions."""
        acids = []
        bases = []
        
        for chemical in self.chemicals.keys():
            if chemical.state == 'aqueous':
                # Identify acids (contain H+ that can be donated)
                if self._is_acid(chemical):
                    acids.append(chemical)
                
                # Identify bases (contain OH- or can accept H+)
                if self._is_base(chemical):
                    bases.append(chemical)
        
        # Generate neutralization reactions
        for acid in acids:
            for base in bases:
                reaction = self._create_neutralization_reaction(acid, base)
                if reaction and not self._reaction_exists(reaction):
                    self.add_reaction(reaction)
                    # Save new reaction to database
                    self.save_reaction_to_database(reaction)
    
    def _generate_redox_reactions(self) -> None:
        """Generate redox reactions between oxidizing and reducing agents."""
        oxidizers = []
        reducers = []
        
        for chemical in self.chemicals.keys():
            # Simple heuristics for common redox pairs
            if self._is_oxidizer(chemical):
                oxidizers.append(chemical)
            if self._is_reducer(chemical):
                reducers.append(chemical)
        
        # Generate redox reactions (simplified stoichiometry)
        for oxidizer in oxidizers:
            for reducer in reducers:
                reaction = self._create_redox_reaction(oxidizer, reducer)
                if reaction and not self._reaction_exists(reaction):
                    self.add_reaction(reaction)
                    # Save new reaction to database
                    self.save_reaction_to_database(reaction)
    
    def _generate_precipitation_reactions(self) -> None:
        """Generate precipitation reactions based on solubility rules."""
        cations = []
        anions = []
        
        for chemical in self.chemicals.keys():
            if chemical.state == 'aqueous':
                # Extract ions from dissolved salts
                if self._is_soluble_salt(chemical):
                    cat, an = self._get_ions_from_salt(chemical)
                    if cat:
                        cations.append((chemical, cat))
                    if an:
                        anions.append((chemical, an))
        
        # Check for insoluble combinations
        for cation_chem, cation in cations:
            for anion_chem, anion in anions:
                if cation_chem != anion_chem:  # Don't react with itself
                    if self._forms_insoluble_salt(cation, anion):
                        reaction = self._create_precipitation_reaction(cation_chem, anion_chem, cation, anion)
                        if reaction and not self._reaction_exists(reaction):
                            self.add_reaction(reaction)
                            # Save new reaction to database
                            self.save_reaction_to_database(reaction)
    
    def _generate_gas_dissolution_reactions(self) -> None:
        """Generate gas dissolution reactions using Henry's law approximations."""
        gases = []
        solvents = []
        
        for chemical in self.chemicals.keys():
            if chemical.state == 'gas':
                gases.append(chemical)
            elif chemical.state in ['liquid', 'aqueous'] and chemical.name in ['H2O(l)', 'H2O(aq)']:
                solvents.append(chemical)
        
        # Generate dissolution reactions
        for gas in gases:
            for solvent in solvents:
                if self._can_dissolve(gas, solvent):
                    reaction = self._create_dissolution_reaction(gas, solvent)
                    if reaction and not self._reaction_exists(reaction):
                        self.add_reaction(reaction)
                        # Save new reaction to database
                        self.save_reaction_to_database(reaction)
    
    def _is_acid(self, chemical: Chemical) -> bool:
        """Check if a chemical can act as an acid."""
        # Simple heuristics
        acid_indicators = ['HCl', 'H2SO4', 'HNO3', 'CH3COOH', 'H+']
        return any(indicator in chemical.name for indicator in acid_indicators)
    
    def _is_base(self, chemical: Chemical) -> bool:
        """Check if a chemical can act as a base."""
        base_indicators = ['OH-', 'NaOH', 'KOH', 'Ca(OH)2', 'NH3']
        return any(indicator in chemical.name for indicator in base_indicators)
    
    def _is_oxidizer(self, chemical: Chemical) -> bool:
        """Check if a chemical can act as an oxidizing agent."""
        oxidizers = ['O2', 'H2O2', 'KMnO4', 'K2Cr2O7', 'Cl2', 'Br2', 'I2']
        return any(ox in chemical.name for ox in oxidizers)
    
    def _is_reducer(self, chemical: Chemical) -> bool:
        """Check if a chemical can act as a reducing agent."""
        reducers = ['H2', 'CO', 'SO2', 'H2S', 'Fe', 'Zn', 'Mg']
        return any(red in chemical.name for red in reducers)
    
    def _is_soluble_salt(self, chemical: Chemical) -> bool:
        """Check if a chemical is a soluble ionic compound."""
        # Simplified: assume most aqueous compounds are ionic
        return chemical.state == 'aqueous' and len(chemical.components) > 1
    
    def _get_ions_from_salt(self, chemical: Chemical) -> tuple:
        """Extract cation and anion from a salt formula."""
        # Very simplified parsing
        name = chemical.name.replace('(aq)', '')
        if '+' in name or '-' in name:
            # Try to split into cation and anion
            parts = name.replace('+', ' ').replace('-', ' ').split()
            if len(parts) >= 2:
                return parts[0], parts[1]
        return None, None
    
    def _forms_insoluble_salt(self, cation: str, anion: str) -> bool:
        """Check if cation + anion forms an insoluble salt."""
        # Simplified solubility rules
        insoluble_pairs = [
            ('Ag', 'Cl'), ('Ag', 'Br'), ('Ag', 'I'),
            ('Pb', 'Cl'), ('Pb', 'Br'), ('Pb', 'I'), ('Pb', 'SO4'),
            ('Hg', 'Cl'), ('Hg', 'Br'), ('Hg', 'I'),
            ('Ba', 'SO4'), ('Ba', 'CO3'),
            ('Ca', 'CO3'), ('Ca', 'PO4'),
            ('Mg', 'CO3'), ('Mg', 'PO4'),
            ('Fe', 'OH'), ('Al', 'OH')
        ]
        return (cation, anion) in insoluble_pairs
    
    def _can_dissolve(self, gas: Chemical, solvent: Chemical) -> bool:
        """Check if a gas can dissolve in a solvent."""
        # Simplified Henry's law - most gases dissolve in water
        soluble_gases = ['CO2', 'O2', 'N2', 'H2', 'NH3', 'SO2', 'HCl']
        return solvent.name in ['H2O(l)', 'H2O(aq)'] and any(g in gas.name for g in soluble_gases)
    
    def _create_neutralization_reaction(self, acid: Chemical, base: Chemical) -> Reaction:
        """Create an acid-base neutralization reaction."""
        try:
            # Create water product
            water = self._get_or_create_chemical('H2O(l)', self._get_basic_molecule_data())
            if not water:
                return None
            
            # Create salt product (simplified)
            salt_name = self._create_salt_name(acid, base)
            salt = self._get_or_create_chemical(salt_name, self._get_basic_molecule_data())
            
            reaction_name = f"{acid.name} + {base.name} → {water.name} + {salt.name}"
            
            reactants = {acid: 1, base: 1}
            products = {water: 1, salt: 1}
            
            return Reaction(
                name=reaction_name,
                reactants=reactants,
                products=products,
                kc=1e14,  # Very favorable
                rate_constant=1e6,  # Fast
                delta_h=-50.0,  # Exothermic
                activation_energy=20.0
            )
        except Exception as e:
            print(f"Warning: Failed to create neutralization reaction: {e}")
            return None
    
    def _create_redox_reaction(self, oxidizer: Chemical, reducer: Chemical) -> Reaction:
        """Create a redox reaction (simplified)."""
        try:
            # Simplified: assume 1:1 stoichiometry for demo
            reaction_name = f"{reducer.name} + {oxidizer.name} → Redox Reaction"
            
            # Create products (simplified - would need proper stoichiometry)
            reactants = {reducer: 1, oxidizer: 1}
            products = {}  # Would need to determine actual products
            
            if not products:
                return None  # Skip if we can't determine products
            
            return Reaction(
                name=reaction_name,
                reactants=reactants,
                products=products,
                kc=1e8,  # Favorable
                rate_constant=1e3,  # Moderate speed
                delta_h=-100.0,  # Often exothermic
                activation_energy=50.0
            )
        except Exception:
            return None
    
    def _create_precipitation_reaction(self, cation_chem: Chemical, anion_chem: Chemical, cation: str, anion: str) -> Reaction:
        """Create a precipitation reaction."""
        try:
            precipitate_name = f"{cation}{anion}(s)"
            precipitate = self._get_or_create_chemical(precipitate_name, self._get_basic_molecule_data())
            
            reaction_name = f"{cation_chem.name} + {anion_chem.name} → {precipitate.name}"
            
            reactants = {cation_chem: 1, anion_chem: 1}
            products = {precipitate: 1}
            
            return Reaction(
                name=reaction_name,
                reactants=reactants,
                products=products,
                kc=1e10,  # Very favorable for precipitation
                rate_constant=1e4,  # Moderate speed
                delta_h=-10.0,  # Slightly exothermic
                activation_energy=30.0
            )
        except Exception:
            return None
    
    def _create_dissolution_reaction(self, gas: Chemical, solvent: Chemical) -> Reaction:
        """Create a gas dissolution reaction."""
        try:
            dissolved_name = gas.name.replace('(g)', '(aq)')
            dissolved = self._get_or_create_chemical(dissolved_name, self._get_basic_molecule_data())
            
            reaction_name = f"{gas.name} ⇌ {dissolved.name}"
            
            reactants = {gas: 1, solvent: 1}
            products = {dissolved: 1}
            
            return Reaction(
                name=reaction_name,
                reactants=reactants,
                products=products,
                kc=0.1,  # Henry's constant approximation
                rate_constant=1e2,  # Moderate dissolution rate
                delta_h=-5.0,  # Slightly exothermic
                activation_energy=15.0
            )
        except Exception:
            return None
    
    def _create_salt_name(self, acid: Chemical, base: Chemical) -> str:
        """Create a salt name from acid and base (simplified)."""
        # Extract cation from base and anion from acid
        base_name = base.name.replace('(aq)', '').replace('OH', '')
        acid_name = acid.name.replace('(aq)', '').replace('H', '')
        
        if base_name and acid_name:
            return f"{base_name}{acid_name}(aq)"
        return "Salt(aq)"
    
    def _reaction_exists(self, reaction: Reaction) -> bool:
        """Check if a reaction already exists in the system."""
        return any(existing.name == reaction.name for existing in self.reactions)
    
    def _get_basic_molecule_data(self) -> dict:
        """Get basic molecule data for creating new chemicals."""
        return {
            'H2O(l)': {
                'components': [('H', 2), ('O', 1)],
                'color_hex': '#87CEEB',
                'enthalpy': -285.8,
                'state': 'liquid'
            },
            'H2O(aq)': {
                'components': [('H', 2), ('O', 1)],
                'color_hex': '#B0E0E6',
                'enthalpy': -285.8,
                'state': 'aqueous'
            }
        }
    
    # Future method for external database integration
    def _lookup_external_reactions(self) -> None:
        """
        Look up reactions from external databases like NIST, PubChem, etc.
        This is a placeholder for future implementation.
        """
        # TODO: Implement API calls to:
        # - NIST Chemistry WebBook
        # - PubChem
        # - Open Reaction Database
        # - IBM RXN
        # 
        # Would need to:
        # 1. Query for reactions involving current chemicals
        # 2. Filter for thermodynamically feasible reactions
        # 3. Convert to internal Reaction format
        # 4. Estimate missing parameters (rate constants, etc.)
        pass
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
                    # Use name-based matching since chemicals might be manually created vs database-created
                    reactant_names = [chem.name for chem in reaction.reactants.keys()]
                    available_chemical_names = [chem.name for chem in self.chemicals.keys()]
                    reactants_available = all(
                        reactant_name in available_chemical_names
                        for reactant_name in reactant_names
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
            # Set initial temperature for new chemicals
            chemical.set_temperature(self._initial_temperature)
        
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
        """
        Apply heating/cooling to all chemicals to reach target temperature.
        This simulates external heating (like a hotplate).
        
        Args:
            temperature: Target temperature in Kelvin
        """
        for chemical in self.chemicals.keys():
            # Calculate temperature difference and apply it
            temp_diff = temperature - chemical.temperature
            chemical.adjust_temperature(temp_diff)
    
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
    
    def update(self, delta_time: float, ambient_temp: float = 293.15) -> dict:
        """
        Update all reactions and recalculate equilibrium.
        Also update temperatures using Newton's law of cooling/heating.
        Shifts chemicals based on reaction directions.
        
        Args:
            delta_time: Time step in seconds
            ambient_temp: Ambient temperature for cooling calculations
        
        Returns:
            dict with 'total_heat_change' (kJ) and 'reactions_fired'
        """
        self.update_concentrations()
        
        # Update temperatures using Newton's law
        for chemical in self.chemicals.keys():
            chemical.update_temperature(delta_time, ambient_temp)
        
        total_heat_change = 0.0
        reactions_fired = []
        
        for reaction in self.reactions:
            # Determine reaction direction
            direction = reaction.calculate_shift()
            
            if direction == "equilibrium":
                continue
            
            # Calculate average temperature of reactants for reaction rate
            reactant_temps = [chem.temperature for chem in reaction.reactants.keys() if chem in self.chemicals]
            avg_temp = sum(reactant_temps) / len(reactant_temps) if reactant_temps else ambient_temp
            
            # Calculate reaction rate
            rate = reaction.calculate_rate(avg_temp, self.catalyst_factor)
            
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
    
    def get_average_temperature(self) -> float:
        """
        Calculate the average temperature of all chemicals weighted by moles.
        
        Returns:
            Average temperature in Kelvin
        """
        if not self.chemicals:
            return 293.15  # Room temperature default
        
        total_moles = sum(self.chemicals.values())
        if total_moles == 0:
            return 293.15
        
        weighted_temp = sum(chem.temperature * moles for chem, moles in self.chemicals.items())
        return weighted_temp / total_moles
    
    def get_net_temperature_change(self) -> float:
        """
        Calculate cumulative temperature change from recent reactions.
        This is now handled by individual chemical temperatures.
        
        Returns:
            Average temperature change (placeholder for compatibility)
        """
        # Individual chemicals now handle their own temperature changes
        # This method is kept for compatibility but returns average temp change
        return 0.0
    
    def __repr__(self) -> str:
        avg_temp = self.get_average_temperature()
        chem_str = ", ".join([f"{c.name}: {m:.2f} mol" for c, m in self.chemicals.items()])
        return f"ChemicalState(T_avg={avg_temp:.1f}K, V={self.volume}L, Chemicals: {chem_str})"
