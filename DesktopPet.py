import math
import tkinter as tk

from PIL import Image, ImageOps, ImageTk

from config import (
    BOB_AMOUNT,
    CHASE_SPEED,
    GROUND_MARGIN,
    JUMP_HEIGHT,
    JUMP_TICKS,
    KEY_RELEASE_GRACE_MS,
    PET_PATH,
    TARGET_H,
    TICK_MS,
    TRANSPARENT_KEY,
    TRICK_DURATIONS,
    WALK_SPEED,
    WAVE_HEIGHT,
)


class DesktopPet:
    def __init__(self, root):
        self.root = root
        self.screen_w = root.winfo_screenwidth()
        self.screen_h = root.winfo_screenheight()

        base = Image.open(PET_PATH).convert("RGBA")
        w, h = base.size
        scale = TARGET_H / h
        self.img_w, self.img_h = int(w * scale), int(h * scale)
        base = base.resize((self.img_w, self.img_h), Image.LANCZOS)
        self.base_right = base
        self.base_left = ImageOps.mirror(base)

        # borderless, always-on-top, transparent window (no regular GUI chrome)
        root.overrideredirect(True)
        root.wm_attributes("-topmost", True)
        try:
            root.wm_attributes("-transparentcolor", TRANSPARENT_KEY)
        except tk.TclError:
            # Not Windows / not supported here — fall back to a translucent
            # whole window so the app is still usable.
            try:
                root.wm_attributes("-alpha", 0.95)
            except tk.TclError:
                pass

        # extra padding so jump/spin/duck effects never clip against the window edge
        self.canvas_w = self.img_w + 80
        self.canvas_h = self.img_h + 80
        self.canvas = tk.Canvas(
            root, width=self.canvas_w, height=self.canvas_h,
            bg=TRANSPARENT_KEY, highlightthickness=0,
        )
        self.canvas.pack()

        self.x = (self.screen_w - self.canvas_w) // 2
        self.base_y = self.screen_h - self.canvas_h - GROUND_MARGIN
        self.y = self.base_y
        root.geometry(f"{self.canvas_w}x{self.canvas_h}+{self.x}+{self.y}")

        self.facing = 1          # 1 = right, -1 = left
        self.walk_phase = 0.0
        self.pressed = set()
        self._release_timers = {}

        self.jump_t = None       # None, or ticks progressed through the jump
        self.duck = False
        self.trick = None        # None, or name of the trick currently playing
        self.trick_t = 0         # ticks progressed through the current trick
        self.chase = False       # autonomously walk toward the mouse cursor

        self.tk_image = None
        self.image_id = self.canvas.create_image(
            self.canvas_w // 2, self.canvas_h // 2, image=None
        )

        self._bind_keys()
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.do_drag)
        self.canvas.bind("<ButtonRelease-3>", lambda e: self.root.destroy())

        self.root.focus_force()
        self.render()
        self.tick()

    # ------------------------------------------------------------ #
    # Input
    # ------------------------------------------------------------ #
    def _bind_keys(self):
        for k in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<KeyPress-{k}>", self.on_key_press)
            self.root.bind(f"<KeyRelease-{k}>", self.on_key_release)
        for key, trick in (
            ("d", "dance"), ("w", "wave"), ("g", "grow"), ("f", "flip"), ("s", "spin"),
        ):
            self.root.bind(f"<KeyPress-{key}>", lambda e, t=trick: self.start_trick(t))
        self.root.bind("c", self.toggle_chase)
        self.root.bind("C", self.toggle_chase)
        self.root.bind("q", lambda e: self.root.destroy())
        self.root.bind("Q", lambda e: self.root.destroy())
        self.root.bind("<Escape>", lambda e: self.root.destroy())

    def on_key_press(self, event):
        k = event.keysym
        # OS key-repeat sends KeyPress without a real KeyRelease in between;
        # cancel any pending "treat as released" timer so holding stays held.
        timer = self._release_timers.pop(k, None)
        if timer is not None:
            self.root.after_cancel(timer)
        self.pressed.add(k)

        if k in ("Left", "Right"):
            self.chase = False
        if k == "Up" and self.jump_t is None:
            self.jump_t = 0
        if k == "Down":
            self.duck = True

    def on_key_release(self, event):
        k = event.keysym

        def release():
            self.pressed.discard(k)
            self._release_timers.pop(k, None)
            if k == "Down":
                self.duck = False

        self._release_timers[k] = self.root.after(KEY_RELEASE_GRACE_MS, release)

    def start_trick(self, name):
        self.chase = False
        self.trick = name
        self.trick_t = 0

    def toggle_chase(self, event):
        self.chase = not self.chase

    def start_drag(self, event):
        self.root.focus_force()
        self._drag_offset = (event.x, event.y)
        self.chase = False
        self.jump_t = None

    def do_drag(self, event):
        ox, oy = self._drag_offset
        new_x = self.root.winfo_pointerx() - ox
        new_y = self.root.winfo_pointery() - oy
        new_x = max(-40, min(new_x, self.screen_w - self.canvas_w + 40))
        new_y = max(-40, min(new_y, self.screen_h - self.canvas_h + 40))
        self.x, self.y = new_x, new_y
        self.base_y = new_y
        self.root.geometry(f"+{self.x}+{self.y}")

    # ------------------------------------------------------------ #
    # Movement / animation loop
    # ------------------------------------------------------------ #
    def tick(self):
        moving = False
        if "Left" in self.pressed:
            self.x -= WALK_SPEED
            self.facing = -1
            moving = True
        if "Right" in self.pressed:
            self.x += WALK_SPEED
            self.facing = 1
            moving = True

        if self.chase:
            target_x = self.root.winfo_pointerx() - self.canvas_w // 2
            dist = target_x - self.x
            if abs(dist) > 10:
                step = CHASE_SPEED if dist > 0 else -CHASE_SPEED
                self.x += step
                self.facing = 1 if step > 0 else -1
                moving = True

        self.x = max(-40, min(self.x, self.screen_w - self.canvas_w + 40))
        self.walk_phase = self.walk_phase + 0.35 if moving else 0.0

        jump_offset = 0
        if self.jump_t is not None:
            self.jump_t += 1
            progress = self.jump_t / JUMP_TICKS
            if progress >= 1:
                self.jump_t = None
            else:
                jump_offset = -JUMP_HEIGHT * math.sin(progress * math.pi)

        wave_offset = 0
        if self.trick == "wave":
            wave_offset = -WAVE_HEIGHT * math.sin(
                (self.trick_t / TRICK_DURATIONS["wave"]) * math.pi
            )

        self.y = self.base_y + jump_offset + wave_offset
        self.root.geometry(f"+{int(self.x)}+{int(self.y)}")

        if self.trick is not None:
            self.trick_t += 1
            if self.trick_t >= TRICK_DURATIONS[self.trick]:
                self.trick = None

        self.render()
        self.root.after(TICK_MS, self.tick)

    # ------------------------------------------------------------ #
    # Drawing
    # ------------------------------------------------------------ #
    def render(self):
        frame = self.base_right if self.facing >= 0 else self.base_left
        bob = int(abs(math.sin(self.walk_phase)) * BOB_AMOUNT) if self.walk_phase else 0

        if self.duck:
            nh = max(1, int(self.img_h * 0.75))
            frame = frame.resize((self.img_w, nh), Image.LANCZOS)

        if self.trick == "spin":
            progress = self.trick_t / TRICK_DURATIONS["spin"]
            angle = progress * 360
            frame = frame.rotate(
                angle if self.facing >= 0 else -angle,
                expand=True, resample=Image.BICUBIC,
            )
        elif self.trick == "dance":
            progress = self.trick_t / TRICK_DURATIONS["dance"]
            angle = 18 * math.sin(progress * math.pi * 6)
            frame = frame.rotate(angle, expand=True, resample=Image.BICUBIC)
        elif self.trick == "grow":
            progress = self.trick_t / TRICK_DURATIONS["grow"]
            factor = 1 + 0.45 * math.sin(progress * math.pi)
            nw = max(1, int(frame.width * factor))
            nh = max(1, int(frame.height * factor))
            frame = frame.resize((nw, nh), Image.LANCZOS)
        elif self.trick == "flip":
            progress = self.trick_t / TRICK_DURATIONS["flip"]
            squash = max(0.02, abs(math.cos(progress * math.pi)))
            src = ImageOps.flip(frame) if progress > 0.5 else frame
            nh = max(1, int(src.height * squash))
            frame = src.resize((self.img_w, nh), Image.LANCZOS)

        self.tk_image = ImageTk.PhotoImage(frame)
        self.canvas.coords(self.image_id, self.canvas_w // 2, self.canvas_h // 2 - bob)
        self.canvas.itemconfig(self.image_id, image=self.tk_image)
