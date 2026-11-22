import tkinter as tk
import math
import os
import sys

INTERVAL_MIN = 1  
SHOW_SEC = 10      
W, H = 220, 210


BASE = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) \
    else os.path.dirname(os.path.abspath(__file__))

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

def primary_monitor():
    """x, y, width, height of the primary monitor."""
    try:
        from screeninfo import get_monitors
        mons = get_monitors()
        m = next((m for m in mons if m.is_primary), mons[0])
        return m.x, m.y, m.width, m.height
    except Exception:
        return 0, 0, root.winfo_screenwidth(), root.winfo_screenheight()

def show():
    mx, my, mw, mh = primary_monitor()
    root.geometry(f"{W}x{H}+{mx + mw - W - 20}+{my + mh - H - 60}")
    root.deiconify()
    root.lift()
    root.after(SHOW_SEC * 1000, root.withdraw)
    root.after(INTERVAL_MIN * 60 * 1000, show)

root.withdraw()
root.after(1000, show)
root.mainloop()