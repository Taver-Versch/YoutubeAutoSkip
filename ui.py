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
        self.start_callback = start_callback
        self.stop_callback = stop_callback
        self.region = (0, 0, 100, 100)
        self.monitors = self.get_monitors()
        self.current_monitor = 0

        # Monitor selection
        monitor_frame = ttk.LabelFrame(root, text="Monitor Selection", padding=10)
        monitor_frame.pack(padx=10, pady=10, fill="x")

        self.monitor_var = tk.StringVar()
        monitor_options = []
        for i, m in enumerate(self.monitors):
            primary_tag = " [PRIMARY]" if m.get('is_primary', False) else ""
            name = m.get('name', f'Monitor {i + 1}')
            monitor_options.append(
                f"{name}{primary_tag}: {m['width']}x{m['height']} at ({m['left']}, {m['top']})"
            )

        self.monitor_combo = ttk.Combobox(monitor_frame, textvariable=self.monitor_var,
                                          values=monitor_options, state="readonly", width=60)
        self.monitor_combo.current(0)
        self.monitor_combo.pack(fill="x")
        self.monitor_combo.bind("<<ComboboxSelected>>", self.on_monitor_change)

        # Region selection
        region_frame = ttk.LabelFrame(root, text="Screen Region Coordinates", padding=10)
        region_frame.pack(padx=10, pady=10, fill="x")

        # Create coordinate input fields
        coords_grid = ttk.Frame(region_frame)
        coords_grid.pack(fill="x")

        ttk.Label(coords_grid, text="X:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.x_entry = ttk.Entry(coords_grid, width=10)
        self.x_entry.insert(0, "0")
        self.x_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(coords_grid, text="Y:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
        self.y_entry = ttk.Entry(coords_grid, width=10)
        self.y_entry.insert(0, "0")
        self.y_entry.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(coords_grid, text="Width:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.width_entry = ttk.Entry(coords_grid, width=10)
        self.width_entry.insert(0, "800")
        self.width_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(coords_grid, text="Height:").grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.height_entry = ttk.Entry(coords_grid, width=10)
        self.height_entry.insert(0, "600")
        self.height_entry.grid(row=1, column=3, padx=5, pady=5)

        # Preview and apply button
        preview_btn = ttk.Button(region_frame, text="Preview Region", command=self.preview_region)
        preview_btn.pack(pady=5)

        # Status display
        self.status_label = ttk.Label(region_frame, text="Region: (0, 0, 800, 600)",
                                      foreground="blue")
        self.status_label.pack(pady=5)

        # Control buttons
        button_frame = ttk.Frame(root)
        button_frame.pack(padx=10, pady=10)

        self.start_button = ttk.Button(button_frame, text="Start Monitoring",
                                       command=self.on_start)
        self.start_button.pack(side="left", padx=5)

        self.stop_button = ttk.Button(button_frame, text="Stop",
                                      command=self.handle_stop, state="disabled")
        self.stop_button.pack(side="left", padx=5)

        # Bind entry changes
        for entry in [self.x_entry, self.y_entry, self.width_entry, self.height_entry]:
            entry.bind("<KeyRelease>", self.update_region)

        self.update_region()

    def get_monitors(self):
        """Get all available monitors"""
        monitors = []

        if SCREENINFO_AVAILABLE:
            try:
                # Use screeninfo to get all monitors
                for i, monitor in enumerate(get_monitors()):
                    monitors.append({
                        'left': monitor.x,
                        'top': monitor.y,
                        'width': monitor.width,
                        'height': monitor.height,
                        'name': monitor.name if hasattr(monitor, 'name') else f"Monitor {i + 1}",
                        'is_primary': monitor.is_primary if hasattr(monitor, 'is_primary') else (i == 0)
                    })

                # Sort so primary monitor is first
                monitors.sort(key=lambda m: not m.get('is_primary', False))

                if monitors:
                    return monitors
            except Exception as e:
                print(f"Error detecting monitors with screeninfo: {e}")

        # Fallback: use pyautogui for single monitor
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
            # Last resort fallback
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
        # Reset region to monitor bounds
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
        """Update the region based on entry values"""
        try:
            x = int(self.x_entry.get())
            y = int(self.y_entry.get())
            width = int(self.width_entry.get())
            height = int(self.height_entry.get())

            self.region = (x, y, width, height)
            self.status_label.config(text=f"Region: ({x}, {y}, {width}, {height})")
        except ValueError:
            self.status_label.config(text="Invalid coordinates - please enter numbers")

    def preview_region(self):
        """Show a visual preview of the selected region"""
        try:
            x, y, width, height = self.region

            # Create a transparent overlay window
            preview_window = tk.Toplevel(self.root)
            preview_window.title("Region Preview")
            preview_window.attributes('-alpha', 0.3)
            preview_window.attributes('-topmost', True)
            preview_window.configure(bg='red')

            # Position and size the window
            preview_window.geometry(f"{width}x{height}+{x}+{y}")

            # Add label
            label = tk.Label(preview_window, text="Selected Region\n(Window will close in 3 seconds)",
                             font=("Arial", 16, "bold"), bg='red', fg='white')
            label.pack(expand=True)

            # Auto-close after 3 seconds
            preview_window.after(3000, preview_window.destroy)

        except Exception as e:
            self.status_label.config(text=f"Preview error: {str(e)}")

    def on_start(self):
        """Handle start button click"""
        self.update_region()  # Make sure region is up to date
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        self.start_callback()

    def on_stop(self):
        """Handle stop button click"""
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")

    def handle_stop(self):
        """Handle the stop button being clicked"""
        self.on_stop()
        self.stop_callback()

    def get_region(self):
        return self.region
