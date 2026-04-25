"""Simple CLI for testing Flask/Chemical/Reaction interactions.

Run: python tools/chem_cli.py

Commands:
  add <name> <moles>    - Adds a chemical (H2O, HCl, NaOH supported)
  react [seconds]       - Run Flask.react for given seconds (default 15)
  status                - Show flask status (chemicals, temp, pH)
  list                  - List known chemicals
  settemp <K>           - Set flask temperature in Kelvin
  quit                  - Exit
"""
import sys
from chemistry.flask import Flask
from chemistry.chemical import Chemical
from chemistry.reaction import Reaction


def make_chemicals():
    # name, components, moles, color_hex, enthalpy (kJ/mol)
    water = Chemical('H2O', [('H',2), ('O',1)], 0.0, '#00AEEF', 0.0)
    hcl = Chemical('HCl', [('H',1), ('Cl',1)], 0.0, '#FF0000', -92.3)
    naoh = Chemical('NaOH', [('Na',1), ('O',1), ('H',1)], 0.0, '#0000FF', -470.0)
    return {'H2O': water, 'HCl': hcl, 'NaOH': naoh}


def main():
    chems = make_chemicals()
    flask = Flask(volume=1.0)

    # simple neutralization reaction: HCl + NaOH -> NaCl + H2O
    # We'll treat products partially (H2O is existing); NaCl not tracked.
    reactants = {chems['HCl']: 1.0, chems['NaOH']: 1.0}
    products = {chems['H2O']: 1.0}
    reaction = Reaction('HCl+NaOH', reactants, products, kc=1e6, rate_constant=1.0, delta_h=-57.0, activation_energy=10.0)
    flask.chemical_state.add_reaction(reaction)

    print('Chem CLI. Type "help" for commands.')
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
            print('commands: add, react, status, list, settemp, help, quit')
            continue
        if cmd == 'list':
            for k in chems.keys():
                print(k)
            continue
        if cmd == 'add':
            if len(parts) < 3:
                print('usage: add <name> <moles>')
                continue
            name = parts[1]
            try:
                moles = float(parts[2])
            except ValueError:
                print('invalid moles')
                continue
            if name not in chems:
                print('unknown chemical; known:', ','.join(chems.keys()))
                continue
            flask.add_reactant(chems[name], moles)
            print(f'Added {moles} mol {name}')
            continue
        if cmd == 'react':
            seconds = 15.0
            if len(parts) >= 2:
                try:
                    seconds = float(parts[1])
                except ValueError:
                    print('invalid seconds, using 15')
            res = flask.react(duration=seconds, step=0.5)
            print('Reacted:', res)
            continue
        if cmd == 'status':
            vd = flask.get_visual_data()
            print('Temp:', vd['temperature'], 'K', 'Boiling:', vd['is_boiling'])
            print('Chemicals:')
            for chem, moles in flask.chemical_state.chemicals.items():
                print(f'  {chem.name}: {moles:.4f} mol, {chem.molarity:.4f} M')
            ph = flask.get_ph()
            print('pH:', ph)
            continue
        if cmd == 'settemp':
            if len(parts) < 2:
                print('usage: settemp <Kelvin>')
                continue
            try:
                k = float(parts[1])
            except ValueError:
                print('invalid')
                continue
            flask.set_temperature(k)
            print('Temperature set to', k)
            continue
        print('unknown command')


if __name__ == '__main__':
    main()
