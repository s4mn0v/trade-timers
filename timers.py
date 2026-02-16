import tkinter as tk
import time
from datetime import datetime, timezone, timedelta

class TimeframeSyncWidget:
    def __init__(self, root):
        self.root = root
        
        # Base dimensions to calculate scale factors
        self.base_width = 780
        self.base_height = 160
        
        # Initialize variables for move/resize
        self.start_x = 0
        self.start_y = 0
        self.start_w = 0
        self.start_h = 0

        # Window setup
        self.root.title("Timeframe Sync")
        self.root.geometry("780x160")
        self.root.configure(bg='#1a1a1a')

        # STRONG ALWAYS ON TOP
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(1000, self.keep_on_top)

        # Slight transparency
        self.root.attributes('-alpha', 0.95)

        # Bindings: Left Click to Move, Right Click to Resize
        self.root.bind('<Button-1>', self.init_move)
        self.root.bind('<B1-Motion>', self.move_window)
        self.root.bind('<Button-3>', self.init_resize)
        self.root.bind('<B3-Motion>', self.resize_window)
        
        # Listen for window size changes to trigger scaling
        self.root.bind('<Configure>', self.on_window_resize)
        
        self.TIMEFRAMES = [
            {"label": "1M", "s": 60, "color": "#e6f0fa"},
            {"label": "5M", "s": 300, "color": "#cce1f5"},
            {"label": "15M", "s": 900, "color": "#b3d2f0"},
            {"label": "30M", "s": 1800, "color": "#99c3eb"},
            {"label": "1H", "s": 3600, "color": "#80b4e6"},
            {"label": "2H", "s": 7200, "color": "#66a5e1"},
            {"label": "4H", "s": 14400, "color": "#a3d9a5"},
            {"label": "6H", "s": 21600, "color": "#a3d9a5"},
            {"label": "1D", "s": 86400, "color": "#a3d9a5"},
        ]
        
        self.SESSIONS = [
            {"name": "Asia", "start": "20:00", "end": "03:00", "color": "#3b82f6", "bg": "#1e3a8a"},
            {"name": "London", "start": "03:00", "end": "08:30", "color": "#f59e0b", "bg": "#78350f"},
            {"name": "New York", "start": "08:30", "end": "16:00", "color": "#10b981", "bg": "#064e3b"},
        ]
        
        # Lists to hold widget references for scaling
        self.tf_labels = []
        self.tf_timers = []
        self.tf_seconds = []
        self.progress_bars = [] # Stores {bg: frame, fg: frame, base_w: 60}
        
        self.create_widgets()
        self.update_clock()
    
    def keep_on_top(self):
        self.root.attributes('-topmost', True)
        self.root.lift()
        self.root.after(1000, self.keep_on_top)

    def create_widgets(self):
        # Main wrapper
        self.outer_frame = tk.Frame(self.root, bg='#1a1a1a')
        self.outer_frame.pack(fill=tk.BOTH, expand=True)

        # Close Button
        self.btn_close = tk.Label(self.root, text="×", bg='#1a1a1a', fg='#555555', font=('Arial', 14))
        self.btn_close.place(relx=1.0, x=-10, y=5, anchor='ne')
        self.btn_close.bind("<Button-1>", lambda e: self.root.quit())
        
        # Centered Container
        self.center_content = tk.Frame(self.outer_frame, bg='#1a1a1a')
        self.center_content.place(relx=0.5, rely=0.5, anchor='center')

        # 1. Timeframes Row
        self.tf_row = tk.Frame(self.center_content, bg='#1a1a1a')
        self.tf_row.pack(pady=5)
        
        for tf in self.TIMEFRAMES:
            f = tk.Frame(self.tf_row, bg='#1a1a1a')
            f.pack(side=tk.LEFT, padx=6)
            
            # Label
            lbl = tk.Label(f, text=tf["label"], bg='#1a1a1a', fg=tf["color"], font=('Arial', 9, 'bold'))
            lbl.pack()
            self.tf_labels.append(lbl)
            
            # TIMER FRAME
            t_frame = tk.Frame(f, bg='#1a1a1a')
            t_frame.pack()
            
            t = tk.Label(t_frame, text="00:00", bg='#1a1a1a', fg='#ffffff', font=('Courier New', 16, 'bold'))
            t.pack(side=tk.LEFT)
            self.tf_timers.append(t)
            
            sec = tk.Label(t_frame, text="", bg='#1a1a1a', fg='#666666', font=('Courier New', 10))
            sec.pack(side=tk.LEFT, pady=(4, 0))
            self.tf_seconds.append(sec)
            
            # Progress Bar
            pb_bg = tk.Frame(f, bg='#333333', width=60, height=3)
            pb_bg.pack(pady=(2, 0))
            pb_bg.pack_propagate(False)
            pb_fg = tk.Frame(pb_bg, bg=tf["color"], width=0, height=3)
            pb_fg.place(x=0, y=0)
            self.progress_bars.append({'bg': pb_bg, 'fg': pb_fg, 'base_w': 60})

        # Divider
        self.divider = tk.Frame(self.center_content, bg='#333333', height=1)
        self.divider.pack(fill=tk.X, pady=12, padx=20)

        # 2. Session Row
        self.session_row = tk.Frame(self.center_content, bg='#1a1a1a')
        self.session_row.pack()
        
        self.badge = tk.Label(self.session_row, text="---", bg='#333333', fg='#ffffff',
                            font=('Arial', 9, 'bold'), padx=12, pady=3)
        self.badge.pack(side=tk.LEFT, padx=15)
        
        self.session_timer = tk.Label(self.session_row, text="--h --m --s", 
                                     bg='#1a1a1a', fg='#ffffff', font=('Courier New', 12, 'bold'))
        self.session_timer.pack(side=tk.LEFT)

        # Resize Hint (Bottom Right)
        self.grip = tk.Label(self.root, text="◢", bg='#1a1a1a', fg='#333333', font=('Arial', 8))
        self.grip.place(relx=1.0, rely=1.0, x=-2, y=-2, anchor='se')

    def on_window_resize(self, event):
        """Calculates scale factor and updates all UI elements."""
        # Only trigger if the actual root window resized
        if event.widget != self.root:
            return

        # Calculate scale factor based on width/height change
        scale_w = self.root.winfo_width() / self.base_width
        scale_h = self.root.winfo_height() / self.base_height
        scale = min(scale_w, scale_h) # Maintain aspect ratio for fonts

        # Update Timeframe Fonts
        for lbl in self.tf_labels:
            lbl.config(font=('Arial', int(9 * scale), 'bold'))
        for t in self.tf_timers:
            t.config(font=('Courier New', int(16 * scale), 'bold'))
        for sec in self.tf_seconds:
            sec.config(font=('Courier New', int(10 * scale)))

        # Update Progress Bar Widths
        for pb in self.progress_bars:
            new_width = int(pb['base_w'] * scale)
            pb['bg'].config(width=new_width, height=max(2, int(3 * scale)))

        # Update Session Fonts
        self.badge.config(font=('Arial', int(9 * scale), 'bold'))
        self.session_timer.config(font=('Courier New', int(12 * scale), 'bold'))
        
        # Update Close Button size
        self.btn_close.config(font=('Arial', int(14 * scale)))

    def update_clock(self):
        curr_unix = time.time()
        
        # Timeframe Updates
        for i, tf in enumerate(self.TIMEFRAMES):
            rem = tf["s"] - (int(curr_unix) % tf["s"])
            h, m, s = rem // 3600, (rem % 3600) // 60, rem % 60
            
            if h > 0:
                self.tf_timers[i].config(text=f"{h:02d}:{m:02d}")
                self.tf_seconds[i].config(text=f":{s:02d}")
            else:
                self.tf_timers[i].config(text=f"{m:02d}:{s:02d}")
                self.tf_seconds[i].config(text="")
            
            # Progress update based on CURRENT scaled width
            prog = (tf["s"] - rem) / tf["s"]
            current_max_w = self.progress_bars[i]['bg'].winfo_width()
            self.progress_bars[i]['fg'].config(width=int(prog * current_max_w))

        # Session Logic (Unchanged)
        now = datetime.now(timezone.utc)
        ny = now - timedelta(hours=4) 
        cur_m, cur_s = ny.hour * 60 + ny.minute, ny.second
        
        active = None
        for s in self.SESSIONS:
            sh, sm = map(int, s["start"].split(":"))
            eh, em = map(int, s["end"].split(":"))
            s_mins, e_mins = sh * 60 + sm, eh * 60 + em
            if s_mins < e_mins:
                if s_mins <= cur_m < e_mins: active = s
            else: 
                if cur_m >= s_mins or cur_m < e_mins: active = s
        
        if active:
            eh, em = map(int, active["end"].split(":"))
            rem_m = (eh * 60 + em - cur_m + 1440) % 1440
            tot_s = (rem_m * 60) - cur_s
            self.badge.config(text=active["name"].upper(), bg=active["bg"], fg='#ffffff')
            self.session_timer.config(text=f"Ends in: {tot_s//3600}h {(tot_s%3600)//60:02d}m {tot_s%60:02d}s")
        else:
            next_s = None
            min_wait = 9999
            for s in self.SESSIONS:
                sh, sm = map(int, s["start"].split(":"))
                wait = (sh * 60 + sm - cur_m + 1440) % 1440
                if wait < min_wait:
                    min_wait = wait
                    next_s = s
            tot_s = (min_wait * 60) - cur_s
            h, m, s = tot_s // 3600, (tot_s % 3600) // 60, tot_s % 60
            self.badge.config(text=f"NEXT: {next_s['name'].upper()}", bg='#2a2a2a', fg='#888888')
            self.session_timer.config(text=f"Starts in: {h}h {m:02d}m {s:02d}s")

        self.root.after(1000, self.update_clock)

    def init_move(self, event):
        self.start_x = event.x
        self.start_y = event.y

    def move_window(self, event):
        x = self.root.winfo_x() + (event.x - self.start_x)
        y = self.root.winfo_y() + (event.y - self.start_y)
        self.root.geometry(f"+{x}+{y}")

    def init_resize(self, event):
        self.start_w = self.root.winfo_width()
        self.start_h = self.root.winfo_height()
        self.start_rx = event.x_root
        self.start_ry = event.y_root

    def resize_window(self, event):
        diff_x = event.x_root - self.start_rx
        diff_y = event.y_root - self.start_ry
        # Enforce minimum sizes to prevent UI crashing
        new_w = max(400, self.start_w + diff_x)
        new_h = max(100, self.start_h + diff_y)
        self.root.geometry(f"{new_w}x{new_h}")

if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("780x160")
    app = TimeframeSyncWidget(root)
    root.mainloop()

