import tkinter as tk
import math
import os
import sys
import json
import re
import subprocess

DEFAULT_INTERVAL_MIN = 30  
SHOW_SEC = 10               
W, H = 220, 210

BASE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.abspath(__file__))



def config_path():
    if sys.platform.startswith("win"):
        d = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "shrimp")
    elif sys.platform == "darwin":
        d = os.path.expanduser("~/Library/Application Support/shrimp")
    else:
        d = os.path.join(os.environ.get("XDG_CONFIG_HOME",
                         os.path.expanduser("~/.config")), "shrimp")
    return os.path.join(d, "config.json")

def load_config():
    try:
        with open(config_path()) as f:
            return json.load(f)
    except Exception:
        return {}

def save_config(cfg):
    try:
        os.makedirs(os.path.dirname(config_path()), exist_ok=True)
        with open(config_path(), "w") as f:
            json.dump(cfg, f)
    except Exception as e:
        print("could not save config:", e)

def list_monitors():
    """List of (x, y, width, height, name), sorted left to right."""
    mons = []
    try:
        from screeninfo import get_monitors
        mons = [(m.x, m.y, m.width, m.height, m.name or "") for m in get_monitors()]
    except Exception:
        pass
    if not mons:
        try:
            out = subprocess.check_output(["xrandr", "--listmonitors"],
                                          text=True, stderr=subprocess.DEVNULL)
            for w, h, x, y, name in re.findall(
                    r"^\s*\d+:\s+\S+\s+(\d+)/\d+x(\d+)/\d+\+(\d+)\+(\d+)\s+(\S+)",
                    out, re.M):
                mons.append((int(x), int(y), int(w), int(h), name))
        except Exception:
            pass
    if not mons:
        probe = tk.Tk()
        probe.withdraw()
        mons = [(0, 0, probe.winfo_screenwidth(), probe.winfo_screenheight(), "")]
        probe.destroy()
    return sorted(mons, key=lambda m: (m[0], m[1]))


def settings_window(mons, cur_idx, cur_interval):
    win = tk.Tk()
    win.title("Shrimp - settings")
    result = {"ok": False}
    mon_var = tk.IntVar(value=cur_idx)
    interval_var = tk.StringVar(value=str(cur_interval))

    if len(mons) > 1:
        tk.Label(win, text="Where should the shrimp appear?",
                 font=("Arial", 12, "bold")).pack(padx=20, pady=(15, 6), anchor="w")
        for i, (x, y, w, h, name) in enumerate(mons):
            label = f"Monitor {i + 1}: {w}x{h}" + (f"  ({name})" if name else "")
            tk.Radiobutton(win, text=label, variable=mon_var, value=i).pack(
                padx=30, anchor="w")

    tk.Label(win, text="How often?",
             font=("Arial", 12, "bold")).pack(padx=20, pady=(15, 6), anchor="w")
    row = tk.Frame(win)
    row.pack(padx=30, anchor="w")
    tk.Label(row, text="Every").pack(side="left")
    tk.Spinbox(row, from_=1, to=240, width=5,
               textvariable=interval_var).pack(side="left", padx=6)
    tk.Label(row, text="minutes").pack(side="left")

    def start():
        try:
            minutes = int(interval_var.get())
        except ValueError:
            minutes = cur_interval
        minutes = max(1, min(1440, minutes))
        result.update(ok=True, monitor=mon_var.get(), interval=minutes)
        win.destroy()

    tk.Button(win, text="Start", command=start).pack(
        fill="x", padx=20, pady=(18, 6))
    tk.Label(win, text="To change later, run with --choose",
             fg="#666").pack(padx=20, pady=(0, 12))
    win.mainloop()
    return result


mons = list_monitors()
cfg = load_config()

idx = cfg.get("monitor")
idx_valid = isinstance(idx, int) and 0 <= idx < len(mons)
interval = cfg.get("interval")
interval_valid = isinstance(interval, int) and interval >= 1
if not idx_valid:
    idx = 0
if not interval_valid:
    interval = DEFAULT_INTERVAL_MIN

if "--choose" in sys.argv or not idx_valid or not interval_valid:
    res = settings_window(mons, idx, interval)
    if res["ok"]:
        idx, interval = res["monitor"], res["interval"]
        cfg.update(monitor=idx, interval=interval)
        save_config(cfg)



root = tk.Tk()
root.overrideredirect(True)
root.attributes("-topmost", True)

c = tk.Canvas(root, width=W, height=H, bg="#fff4e6",
              highlightthickness=2, highlightbackground="#d9573f")
c.pack()

def draw_shrimp():
    cx, cy, r = 110, 90, 50
    pts = []
    for i in range(8):
        a = math.radians(20 + i * 30)
        x, y = cx + r * math.cos(a), cy - r * math.sin(a)
        pts.append((x, y))
        s = 20 - i * 1.6
        c.create_oval(x - s, y - s * 0.8, x + s, y + s * 0.8,
                      fill="#ff7f66", outline="#d9573f", width=2)
    tx, ty = pts[-1]
    c.create_polygon(tx, ty, tx - 22, ty + 6, tx - 14, ty + 22,
                     tx + 4, ty + 18, fill="#ff9a85", outline="#d9573f")
    hx, hy = pts[0]
    c.create_oval(hx + 2, hy - 8, hx + 9, hy - 1, fill="black")
    c.create_line(hx + 10, hy - 10, hx + 45, hy - 35, fill="#d9573f", width=2)
    c.create_line(hx + 12, hy - 4, hx + 50, hy - 15, fill="#d9573f", width=2)

img_path = os.path.join(BASE, "shrimp.png")
if os.path.exists(img_path):
    root.img = tk.PhotoImage(file=img_path)
    c.create_image(W // 2, 85, image=root.img)
else:
    draw_shrimp()

c.create_text(W // 2, H - 22, text="this you", fill="#333",
              font=("Arial", 16, "bold"))

def show():
    mx, my, mw, mh, _ = mons[idx]
    root.geometry(f"{W}x{H}+{mx + mw - W - 20}+{my + mh - H - 60}")
    root.deiconify()
    root.lift()
    root.after(SHOW_SEC * 1000, root.withdraw)
    root.after(interval * 60 * 1000, show)

root.withdraw()
root.after(1000, show)
root.mainloop()