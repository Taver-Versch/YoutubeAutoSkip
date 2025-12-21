import tkinter as tk
from tkinter import ttk
import pyautogui

try:
    from screeninfo import get_monitors

    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False
    print("screeninfo not installed. Install with: pip install screeninfo")


class AppUI:
    def __init__(self, root, start_callback, stop_callback):
        self.root = root
        self.root.title("YoutubeAutoSkip")

        rs_font = ("RuneScape", 13)

        style = ttk.Style()
        style.configure("TLabel", font=rs_font)
        style.configure("TButton", font=rs_font)
        style.configure("TLabelframe.Label", font=rs_font)
        style.configure("TCombobox", font=rs_font)
        style.configure("TEntry", font=rs_font)

        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.region = (0, 0, 100, 100)
        self.monitors = self.get_monitors()
        self.current_monitor = 0

        monitor_frame = ttk.LabelFrame(root, text="WHICH MONITOR", padding=10)
        monitor_frame.pack(padx=10, pady=10, fill="x")

        self.monitor_var = tk.StringVar()
        monitor_options = []
        for i, m in enumerate(self.monitors):
            primary_tag = " [PRIMARY]" if m.get('is_primary', False) else ""
            name = m.get('name', f'Monitor {i + 1}')
            monitor_options.append(f"{name}{primary_tag}: {m['width']}x{m['height']}")

        self.monitor_combo = ttk.Combobox(monitor_frame, textvariable=self.monitor_var,
                                          values=monitor_options, state="readonly", width=60)
        self.monitor_combo.current(0)
        self.monitor_combo.pack(fill="x")
        self.monitor_combo.bind("<<ComboboxSelected>>", self.on_monitor_change)

        region_frame = ttk.LabelFrame(root, text="SCREEN COORDS", padding=10)
        region_frame.pack(padx=10, pady=10, fill="x")

        coords_grid = ttk.Frame(region_frame)
        coords_grid.pack(fill="x", expand=True)
        coords_grid.columnconfigure(0, weight=1)
        coords_grid.columnconfigure(1, weight=1)
        coords_grid.columnconfigure(2, weight=1)
        coords_grid.columnconfigure(3, weight=1)

        ttk.Label(coords_grid, text="X:").grid(row=0, column=0, padx=5, pady=5)
        self.x_entry = ttk.Entry(coords_grid, width=10, justify="center")
        self.x_entry.insert(0, "0")
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(coords_grid, text="Y:").grid(row=0, column=2, padx=5, pady=5)
        self.y_entry = ttk.Entry(coords_grid, width=10, justify="center")
        self.y_entry.insert(0, "0")
        self.y_entry.grid(row=0, column=3, padx=5, pady=5)

        primary_monitor = self.monitors[0]

        ttk.Label(coords_grid, text="Width:").grid(row=1, column=0, padx=5, pady=5)
        self.width_entry = ttk.Entry(coords_grid, width=10, justify="center")
        self.width_entry.insert(0, str(primary_monitor['width']))
        self.width_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(coords_grid, text="Height:").grid(row=1, column=2, padx=5, pady=5)
        self.height_entry = ttk.Entry(coords_grid, width=10, justify="center")
        self.height_entry.insert(0, str(primary_monitor['height']))
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)

        preview_btn = ttk.Button(region_frame, text="Preview Region", command=self.preview_region)
        preview_btn.pack(pady=5)

        search_frame = ttk.LabelFrame(root, text="WHAT TO PRESS", padding=10)
        search_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(search_frame, text="Search for:").pack(side="left", padx=5)
        self.search_entry = ttk.Entry(search_frame, width=20, justify="center")
        self.search_entry.insert(0, "skip")
        self.search_entry.pack(side="left", padx=5)

        ttk.Label(search_frame, text="", foreground="gray").pack(side="left", padx=5)

        button_frame = ttk.Frame(root)
        button_frame.pack(padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Monitoring", command=self.on_start)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop", command=self.handle_stop, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        for entry in [self.x_entry, self.y_entry, self.width_entry, self.height_entry]:
            entry.bind("<KeyRelease>", self.update_region)

        self.update_region()

    def get_monitors(self):
        monitors = []

        if SCREENINFO_AVAILABLE:
            try:
                for i, monitor in enumerate(get_monitors()):
                    monitors.append({
                        'left': monitor.x,
                        'top': monitor.y,
                        'width': monitor.width,
                        'height': monitor.height,
                        'name': monitor.name if hasattr(monitor, 'name') else f"Monitor {i + 1}",
                        'is_primary': monitor.is_primary if hasattr(monitor, 'is_primary') else (i == 0)
                    })
                monitors.sort(key=lambda m: not m.get('is_primary', False))
                if monitors:
                    return monitors
            except Exception as e:
                print(f"Error detecting monitors with screeninfo: {e}")

        try:
            screen_width, screen_height = pyautogui.size()
            monitors = [{
                'left': 0,
                'top': 0,
                'width': screen_width,
                'height': screen_height,
                'name': 'Primary Monitor',
                'is_primary': True
            }]
        except:
            monitors = [{
                'left': 0,
                'top': 0,
                'width': 1920,
                'height': 1080,
                'name': 'Default Monitor',
                'is_primary': True
            }]

        return monitors

    def on_monitor_change(self, event):
        self.current_monitor = self.monitor_combo.current()
        monitor = self.monitors[self.current_monitor]
        self.x_entry.delete(0, tk.END)
        self.x_entry.insert(0, str(monitor['left']))
        self.y_entry.delete(0, tk.END)
        self.y_entry.insert(0, str(monitor['top']))
        self.width_entry.delete(0, tk.END)
        self.width_entry.insert(0, str(monitor['width']))
        self.height_entry.delete(0, tk.END)
        self.height_entry.insert(0, str(monitor['height']))
        self.update_region()

    def update_region(self, event=None):
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())
            self.region = (x, y, width, height)
        except ValueError:
            pass

    def preview_region(self):
        try:
            x, y, width, height = self.region

            preview_window = tk.Toplevel(self.root)
            preview_window.title("Region Preview")
            preview_window.attributes('-alpha', 0.6)
            preview_window.attributes('-topmost', True)
            preview_window.configure(bg='green')
            preview_window.geometry(f"{width}x{height}+{x}+{y}")

            label = tk.Label(preview_window, text="Selected Region\n(This popup will disappear in 3 seconds)",
                             font=("Arial", 16, "bold"), bg='black', fg='white')
            label.pack(expand=True)

            preview_window.after(3000, preview_window.destroy)
        except Exception as e:
            print(f"Preview error: {e}")

    def on_start(self):
        self.update_region()
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.start_callback()

    def on_stop(self):
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def handle_stop(self):
        self.on_stop()
        self.stop_callback()

    def get_region(self):
        return self.region

    def get_search_text(self):
        return self.search_entry.get().strip()
