import sys
from chemistry.flask import Flask
from chemistry.chemical import Chemical
from chemistry.reaction import Reaction

HELPDOCS = """
==== COMMAND USAGE ====

add <name> <moles>
    Add a chemical to the flask.
    Example: 'add HCl 0.1' or 'add C6H12O6 0.05'
    
    Note: 
    - If the name is recognized (HCl, NaOH, H2O), it uses specific data.
    - If unrecognized, the engine will try to parse the formula and 
      assign a default gray color and 0.0 enthalpy.

react [seconds] [step]
    Run the simulation for a set duration.
    Example: 'react 15 0.5' (Runs for 15s with a 0.5s calculation step).

status
    Displays current Flask stats: Temperature, pH, and chemical concentrations.

list
    Shows all chemicals currently in your "known" library.

settemp <Kelvin>
    Force the flask to a specific temperature.

quit / exit
    Close the program.
========================
"""

def make_chemicals():
    """Initializes the starting library of chemicals with known properties."""
    # Default to aqueous state for these common solutes
    water = Chemical('H2O', [('H',2), ('O',1)], 0.0, '#00AEEF', 0.0, state='aqueous')
    hcl = Chemical('HCl', [('H',1), ('Cl',1)], 0.0, '#FF0000', -92.3, state='aqueous')
    naoh = Chemical('NaOH', [('Na',1), ('O',1), ('H',1)], 0.0, '#0000FF', -470.0, state='aqueous')
    return {'H2O': water, 'HCl': hcl, 'NaOH': naoh}

def main():
    chems = make_chemicals()
    flask = Flask(volume=1.0)

    # Setup the initial neutralization reaction
    if 'HCl' in chems and 'NaOH' in chems and 'H2O' in chems:
        reactants = {chems['HCl']: 1.0, chems['NaOH']: 1.0}
        products = {chems['H2O']: 1.0}
        reaction = Reaction('HCl+NaOH', reactants, products, kc=1e6, rate_constant=1.0, delta_h=-57.0, activation_energy=10.0)
        flask.chemical_state.add_reaction(reaction)

    print('Chem CLI. Type "help" for detailed usage.')
    while True:
        try:
            line = input('> ').strip()
        except EOFError:
            break
        if not line:
            continue
            
        parts = line.split()
        cmd = parts[0].lower()
        
        if cmd in ('quit', 'exit'):
            break
            
        if cmd == 'help':
            print(HELPDOCS)
            continue
            
        if cmd == 'list':
            print("Known/Registered Chemicals:")
            for k in chems.keys():
                print(f" - {k}")
            continue
            
        if cmd == 'add':
            if len(parts) < 3:
                print('Usage: add <name> <moles>')
                continue
                
            name = parts[1]
            try:
                moles = float(parts[2])
            except ValueError:
                print('Error: Moles must be a number.')
                continue
            
            # --- DYNAMIC CHEMICAL CREATION ---
            if name not in chems:
                print(f"Chemical '{name}' not in library. Creating dynamic entry...")
                try:
                    # We pass components=None to let the Chemical class's 
                    # internal parser handle the formula.
                    new_chem = Chemical(
                        name=name,
                        components=None,
                        moles=0.0,
                        color_hex='#808080',
                        enthalpy=0.0,
                        state='aqueous'
                    )
                    chems[name] = new_chem
                except Exception as e:
                    print(f"Error: Could not parse chemical '{name}': {e}")
                    continue
            # ---------------------------------

            flask.add_reactant(chems[name], moles)
            print(f'Added {moles} mol {name}')
            continue
            
        if cmd == 'react':
            # Usage: react <duration> [step] [status_interval]
            seconds = 15.0
            step = 0.5
            status_interval = None
            if len(parts) >= 2:
                try:
                    seconds = float(parts[1])
                except ValueError:
                    print('Invalid seconds, using 15')
            if len(parts) >= 3:
                try:
                    step = float(parts[2])
                except ValueError:
                    print('Invalid step, using 0.5')
            if len(parts) >= 4:
                try:
                    status_interval = float(parts[3])
                except ValueError:
                    print('Invalid status interval; ignoring')

            # If a status_interval is provided, run in chunks and show live updates
            if status_interval and status_interval > 0:
                elapsed = 0.0
                while elapsed < seconds:
                    chunk = min(status_interval, seconds - elapsed)
                    res = flask.react(duration=chunk, step=step)
                    elapsed += chunk
                    # Print live status
                    print(f"\n[t={elapsed:.1f}s] {res['reactions_fired']} Heat={res['total_heat_change_kj']:.4f}kJ T={res['temperature']:.2f}K")
                    # Show equilibrium summary for each reaction
                    for r in flask.chemical_state.reactions:
                        try:
                            eq = r.describe_equilibrium()
                            print(f"  - {r.name}: Q={eq['Q']:.3g}, Kc={eq['Kc']:.3g}, dir={eq['direction']}")
                        except Exception:
                            pass
                print('Reaction complete (live).')
            else:
                res = flask.react(duration=seconds, step=step)
                print(f'Reaction complete: {res}')
            continue
            
        if cmd == 'status':
            vd = flask.get_visual_data()
            print(f"\n--- FLASK STATUS ---")
            print(f"Temp: {vd['temperature']:.2f} K | Boiling: {vd['is_boiling']}")
            print(f"pH:   {flask.get_ph():.2f}")
            print(f"Chemicals:")
            for chem, moles in flask.chemical_state.chemicals.items():
                print(f'  {chem.name:8}: {moles:10.4f} mol ({chem.molarity:8.4f} M)')
            print("--------------------\n")
            continue
            
        if cmd == 'settemp':
            if len(parts) < 2:
                print('Usage: settemp <Kelvin>')
                continue
            try:
                k = float(parts[1])
                flask.set_temperature(k)
                print(f'Temperature set to {k} K')
            except ValueError:
                print('Error: Invalid temperature value.')
            continue
            
        print(f"Unknown command: {cmd}")

if __name__ == '__main__':
    main()