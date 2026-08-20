import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PET_PATH = os.path.join(SCRIPT_DIR, "pet.png")

TARGET_H = 140               # on-screen height of the pet, px
WALK_SPEED = 6                # px per tick while holding left/right
TICK_MS = 30                   # animation/movement tick interval
BOB_AMOUNT = 6                 # walk-bounce height, px
JUMP_HEIGHT = 60               # px
JUMP_TICKS = 20
WAVE_HEIGHT = 22               # px, smaller than a real jump
CHASE_SPEED = 5
GROUND_MARGIN = 80             # gap kept above the bottom of the screen
KEY_RELEASE_GRACE_MS = 60      # bridges the gap between OS key-repeat events

TRANSPARENT_KEY = "magenta"    # not present anywhere in pet.png; punched
                                # out via Tk's "-transparentcolor" (Windows-only)

TRICK_DURATIONS = {            # ticks each named trick runs for
    "spin": 18,
    "dance": 40,
    "wave": 14,
    "grow": 24,
    "flip": 22,
}
