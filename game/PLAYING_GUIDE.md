# Dynamic ChemEngine - Playing Guide

## 🎮 Quick Start

### Installation & Running

**Option 1: Using the launcher (Recommended)**
```bash
python run.py
```
This will automatically check for pygame, install it if needed, and launch the game.

**Option 2: Direct execution**
```bash
# First, install dependencies
pip install pygame

# Then run the game
python main.py
```

---

## 🎯 Game Modes

### 1. Sandbox Mode - Free Experimentation
Pure chemistry exploration with no rules or time limits.

**How to play:**
- **Click droppers** on the left to add chemicals to the flask
- **Click the hotplate** to toggle heating on/off
- Watch the thermometer to see temperature changes
- Observe color changes as chemicals react
- Particle effects show reaction intensity

**Chemistry mechanics:**
- Colors blend based on chemical concentrations
- Temperature affects reaction rates (hotter = faster)
- Exothermic reactions generate heat
- Flask will boil if temperature exceeds 100°C (373K)

---

### 2. Challenge Mode - Guided Puzzles
Solve chemistry puzzles with specific win and loss conditions.

**How to play:**
- Read the objective at the top of the screen
- Use the hotplate to control temperature
- Add chemicals strategically to achieve goals
- Must complete objective before time runs out or flask boils

**Three challenges included:**

#### Challenge 1: Color Shift
**Objective:** Shift flask color from yellow to orange
- **Starting state:** Chromate solution (yellow)
- **Goal:** Achieve orange color (dichromate)
- **Time limit:** 30 seconds
- **Hint:** Try adjusting temperature or adding different chemicals

#### Challenge 2: Gas Burst
**Objective:** Produce 0.5 moles of O₂ in under 10 seconds
- **Starting state:** H₂O₂ (hydrogen peroxide)
- **Goal:** Generate enough oxygen gas without overheating
- **Time limit:** 10 seconds
- **Max temp:** 350K (77°C)
- **Hint:** Add a catalyst to speed up decomposition

#### Challenge 3: Equilibrium Balance
**Objective:** Achieve purple color without boiling
- **Starting state:** Mixture of acid and base
- **Goal:** Create neutral solution (purple) at safe temperature
- **Time limit:** 60 seconds
- **Max temp:** 100°C (373K)
- **Hint:** Use small temperature adjustments for fine control

---

## 🎮 Controls

### Main Menu
- **UP/DOWN arrows** - Navigate menu options
- **ENTER** - Select option
- **ESC** - Exit game

### In-Game
- **Click droppers** - Add chemicals to flask
- **Click hotplate** - Toggle heating on/off
- **SPACE** - Pause game
- **ESC** - Return to main menu
- **R** - Reset flask (sandbox only)

### Mouse
- **Mouse over** - Hover effects on UI elements
- **Click** - Activate buttons

---

## 🧪 Chemistry Concepts

### Three Pillars of Chemistry

#### 1. Equilibrium (Le Chatelier's Principle)
Reversible reactions shift to restore balance when conditions change.
- When you add more reactant, reaction shifts forward
- When you heat up, reaction may shift (depends on ΔH)
- System tries to counteract changes

#### 2. Kinetics (Reaction Rates)
How fast reactions occur, controlled by temperature and catalysts.
- **Higher temperature** = Faster reactions
- **Catalyst** = Speeds up reaction (multiply by factor)
- **Higher concentration** = More frequent collisions = Faster rate

#### 3. Thermodynamics (Heat)
Energy changes in reactions.
- **Exothermic** reactions release heat (negative ΔH)
- **Endothermic** reactions absorb heat (positive ΔH)
- Heat changes temperature, which affects reaction rates

### Visual Feedback

- **Flask color** - Indicates chemicals present (blended)
- **Particles spawning** - Shows reaction intensity
- **Thermometer fill** - Current temperature
- **Thermometer color** - Blue (cold) → Yellow (warm) → Red (hot)
- **Flask red border** - WARNING: Boiling! Danger!

---

## 🎨 UI Elements

### Flask
Main container showing:
- Current color (mixture of all chemicals)
- Content state
- Boiling indicator (red border = too hot!)

### Thermometer (Right side)
- Blue = Cold
- Yellow = Warm
- Red = Hot
- Bulb fills as temperature rises
- Number shows exact temperature in °C

### Hotplate (Bottom right)
- Click to toggle ON/OFF
- Heat level increases from 0-100%
- Red color indicates heating
- Increases flask temperature over time

### Droppers (Top)
- Click to add specific chemical
- Color matches chemical color
- Cooldown bar prevents spam-clicking
- Each drop adds fixed amount

### Magnifier & Titration Tools

- **Magnifying Glasses (right side):** Small magnifier UI buttons sit on the right toolbar. When the player hovers a magnifier over a beaker or volumetric flask graphic, the renderer should show a live particle preview (a read-only snapshot of particle motion and intensity) for that vessel. These magnifiers are available in both Sandbox and Challenge modes.
- **Hover behavior:** Hovering the magnifier over a vessel shows the particle emitter in motion in a zoomed preview. The preview must not modify the chemistry state — it is a visualization only.
- **Scroll support:** The chemical/tool panels (left and right columns) allow vertical scrolling when content overflows; both panels scroll independently so the user can reach many droppers or magnifiers.
- **Titration Dropper:** A `TitrationDropper` UI variant enables fine, continuous micro-dosing for titration activities. Holding the mouse button (or dragging) delivers small, continuous amounts (mol/sec) for precise control. The UI shows a small dosing indicator while dispensing.
- **Tools indicator:** The right tools column contains small indicators for active tools (for example, `pH strip`, `Rxn measurer`, `Titration indicator`). Indicators show on/off or numeric value states and display a tooltip on hover.

---

## 💡 Tips & Strategies

### Sandbox Mode
1. **Start simple** - Add one chemical at a time and observe
2. **Experiment with temperature** - See how heat affects reactions
3. **Color mixing** - Combine different colored chemicals
4. **Particle effects** - High reaction rates create more particles

### Challenge Mode
1. **Read objectives carefully** - Understand exact goal
2. **Plan your approach** - Don't randomly click droppers
3. **Monitor thermometer** - Temperature control is critical
4. **Small adjustments** - Use hotplate for fine tuning
5. **Watch the time** - Plan moves before time runs out
6. **Test hypothesis** - Chemistry is about prediction

---

## 🔬 Real Chemistry Behind It

This simulator models real chemistry principles:

- **Equilibrium constant (Kc)** - Determines which direction reaction favors
- **Arrhenius equation** - Calculates how temperature affects rate
- **Le Chatelier's principle** - System shifts to oppose changes
- **Enthalpy (ΔH)** - Energy released or absorbed by reaction
- **Concentration** - Measured in Molarity (mol/L)
- **Color indicators** - Many real reactions show color changes

---

## 🐛 Troubleshooting

### Game won't start
```bash
# Make sure pygame is installed
pip install pygame

# Then try again
python run.py
```

### Window appears but is blank
- Wait a few seconds for initialization
- Try pressing ESC and starting over
- Check that your graphics drivers are up to date

### Game runs slowly
- Close other applications
- Lower screen resolution if possible
- Game uses particles for effects; many reactions slow things down

### Controls not responding
- Make sure window is in focus (click on it)
- Try clicking the flask or UI elements directly
- Check keyboard layout

---

## 📊 Game Statistics

- **13 core object classes** - All chemistry simulation
- **1800+ lines of code** - Efficient and optimized
- **No external dependencies** - Except pygame (easy install)
- **Full physics simulation** - Gravity, collisions, forces
- **Real equilibrium calculations** - Q vs Kc comparison
- **Arrhenius kinetics** - Temperature-dependent rates

---

## 🎓 Learning Outcomes

After playing Dynamic ChemEngine, you'll understand:

✓ Equilibrium and Le Chatelier's principle
✓ How temperature affects reaction rates
✓ Heat generation in chemical reactions
✓ Solute concentration and mixing
✓ Visual indicators of chemical reactions
✓ Interactive problem-solving in chemistry

---

## 🚀 Advanced Usage

### Running Tests

**Test core chemistry system:**
```bash
python test_chemistry.py
```

**Test UI and game logic:**
```bash
python test_ui_and_game.py
```

### Custom Challenges

To create your own challenge, see `challenge.py`:

```python
from challenge import Challenge
from chemical import Chemical

my_challenge = Challenge(
    name="My Challenge",
    description="Your objective here",
    initial_chemicals={chemical1: 1.0, chemical2: 0.5},
    initial_temperature=293.15,
    win_conditions={'target_color': '#FFFFFF'},
    time_limit=30.0
)
```

---

## 📝 File Structure

```
RidgeHacks/
├── main.py                    # Game application entry point
├── pygame_renderer.py         # All drawing code
├── config.py                  # Game configuration
├── run.py                     # Launcher script
├── game_mode.py              # Game mode orchestration
├── challenge.py              # Challenge system
├── flask.py                  # Main container
├── chemical_state.py         # Chemistry hub
├── reaction.py               # Reaction simulation
├── chemical.py               # Chemical substance
├── particle_emitter.py       # Particle spawning
├── particle.py               # Individual particles
├── dropper.py                # UI: Chemical dropper
├── thermometer.py            # UI: Temperature gauge
├── hotplate.py               # UI: Heating control
├── rigid_body.py             # Physics simulation
├── test_chemistry.py         # Chemistry tests
├── test_ui_and_game.py       # UI/game tests
└── README.md / This file
```

---

## 👥 Credits

**Dynamic ChemEngine**
- Interactive chemistry simulator
- Built with Python & Pygame
- Simulates equilibrium, kinetics, and thermodynamics
- Educational and entertaining

---

**Ready to explore chemistry? Launch the game and start experimenting!**

```bash
python run.py
```

Enjoy! 🧪✨
