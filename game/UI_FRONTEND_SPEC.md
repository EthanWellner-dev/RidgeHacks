UI Frontend Specification
=========================

Overview
--------
This document describes the intended frontend behavior for the Big Alchemy UI elements referenced in the mockup/sketch. It is intentionally implementation-agnostic and provides concrete entry points for the renderer (`pygame_renderer.py`) and game loop (`main.py` / `game_mode.py`).

Assets (placeholders)
- `assets/beaker.png` — beaker graphic (optional)
- `assets/volumetric_flask.png` — volumetric flask graphic (optional)
- `assets/magnifier.png` — magnifier icon for right toolbar
- `assets/dropper_icon.png` — generic dropper icon

Key UI Features
---------------
- Right-side magnifiers: small icon buttons aligned vertically on the right edge.
  - Hovering a magnifier over a vessel area triggers a read-only particle preview.
  - Preview should use a zoomed view and play the particle emitter animation without mutating chemical state.

- Scrollable tool panels:
  - Left column (droppers/tools) is vertically scrollable when content overflows.
  - Right column (magnifiers/tools/indicators) is independently scrollable.

- TitrationDropper (UI behavior):
  - On mouse-down over the dropper, start continuous micro-dosing.
  - While held, call `get_hold_dispense(dt)` on the `TitrationDropper` each frame and apply the returned moles to the flask.
  - On mouse-up, stop dosing.
  - Show a small progress/dosing indicator (e.g., thin horizontal bar under the dropper) while dosing.

- Tools Indicator:
  - Small badges in the tools column show state for helpers like pH strip or reaction measurer.
  - Badges are clickable for toggling or show a tooltip with current measured value on hover.

Renderer integration notes
-------------------------
- The renderer should expose a `render_preview(vessel_id, surface, rect)` API that accepts a vessel identifier and a target surface/rect to draw a read-only particle snapshot.
- The preview system should sample particle emitter state (positions, colors, alpha) and draw them without advancing the actual simulation state.

Design considerations
---------------------
- Previews must not mutate chemical amounts, temperature, or reaction rates.
- Previews can simulate a short local particle animation timeline (0.5–1.5s) using a frozen copy of the particle emitter state.
- Keep UI controls accessible with keyboard focus and ensure scroll areas are reachable with mouse-wheel and touchpad gestures.

Notes for assets
----------------
The document references placeholder images — the UI will work without these assets, but having beaker/flask/magnifier icons will make the interface clearer. The code should fall back gracefully to simple vector/rectangle placeholders when images are missing.

Interaction Examples
--------------------
- Hover magnifier → preview appears over flask (no state change)
- Click and hold `TitrationDropper` → small moles added continuously until release
- Scroll left tools column to access more droppers

End of spec
