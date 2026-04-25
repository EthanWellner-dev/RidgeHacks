from chemistry.flask import Flask
from chemistry.chemical import Chemical
class Wrapper:
    def __init__(self, chemical):
        self.chemical = chemical

if __name__ == '__main__':
    f = Flask(1.0)
    water = Chemical('H2O',[('H',2),('O',1)], 0.1, '#87CEEB', -285.8)
    # Normal add
    f.add_reactant(water, 0.1)
    print('Added water ok, moles:', f.chemical_state.chemicals.get(water))
    # Add via wrapper
    w = Wrapper(water)
    f.add_reactant(w, 0.05)
    print('Added via wrapper ok, moles:', f.chemical_state.chemicals.get(water))
    # Add via dict
    f.add_reactant({'name':'NaCl'}, 0.01)
    print('Added via dict ok; chemicals:', [c.name for c in f.chemical_state.chemicals.keys()])
