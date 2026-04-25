import sys, pathlib
p = pathlib.Path(__file__).resolve().parents[1]
if str(p) not in sys.path:
    sys.path.insert(0,str(p))

    
from game.game_mode import GameMode
from game.dropper import Dropper
from chemistry.chemical import Chemical
from chemistry.flask import Flask

flask = Flask(1.0)
water = Chemical('H2O',[('H',2),('O',1)],0.1,'#87CEEB',-285.8)

gm = GameMode()
# create a dropper
dropper = Dropper(0,0, water, 0.2)
# assign flask to gm and initialize
gm.initialize_sandbox(flask, droppers=[dropper])

print('Before add: reactions count=', len(flask.chemical_state.reactions))
# simulate drag drop
try:
    gm.dragging_dropper = dropper
    gm.on_mouse_up(flask.bounds['x'] + 10, flask.bounds['y'] + 10)
    print('After drop: scheduled?', getattr(flask.chemical_state,'_needs_reaction_discovery', None))
    # simulate a few update frames to reproduce lag and observe diagnostics
    for i in range(6):
        print(f'--- frame {i} ---')
        out = gm.update(0.016)
        print('update returned status:', out.get('status'))
    print('Done frames; reactions count=', len(flask.chemical_state.reactions))
except Exception as e:
    print('Exception during simulation:', e)
