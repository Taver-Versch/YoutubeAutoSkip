import tkinter as tk
from ui import AppUI
import logic
import threading
import time

running = False

def start_loop():
    global running
    if running:
        return
    running = True
    threading.Thread(target=main_loop, daemon=True).start()

def stop_loop():
    global running
    running = False

def main_loop():
    while running:
        try:
            region = ui.get_region()
            search_text = ui.get_search_text()
            img = logic.screenshot_region(region)
            button = logic.find_skip_button(img, search_text)
            if button:
                logic.click_button(region, button)
                time.sleep(3)
            time.sleep(2)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    root = tk.Tk()
    root.iconbitmap('app_icon.ico')
    ui = AppUI(root, start_loop, stop_loop)
    root.mainloop()
