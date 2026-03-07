import tkinter as tk
import threading
import sys
import ctypes

class RecordingOverlay:
    """
    Creates a transparent window that only draws a red border around the screen edges.
    Runs in its own thread to avoid blocking the main application.
    """
    def __init__(self, thickness=3, color="red"):
        self.thickness = thickness
        self.color = color
        self.root = None
        self.thread = None
        self.is_running = False

    def _run_overlay(self):
        self.root = tk.Tk()
        
        # Make the window borderless and cover the entire screen
        self.root.overrideredirect(True)
        self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
        
        # Set a transparent color key (e.g. gray is fully transparent)
        transparent_color = "gray12"
        self.root.wm_attributes("-transparentcolor", transparent_color)
        self.root.wm_attributes("-topmost", True)
        self.root.config(bg=transparent_color)

        # Draw the frame using a canvas
        canvas = tk.Canvas(self.root, width=self.root.winfo_screenwidth(), height=self.root.winfo_screenheight(), 
                           bg=transparent_color, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        w = self.root.winfo_screenwidth()
        h = self.root.winfo_screenheight()
        t = self.thickness
        o = t / 2  # Offset to draw line inside canvas bounds

        # Draw 4 dashed lines for the border to leave the center completely transparent to clicks
        # dash=(10, 5) means 10 pixels drawn, 5 pixels blank ("cortecitos")
        canvas.create_line(0, o, w, o, fill=self.color, width=t, dash=(15, 10)) # Top
        canvas.create_line(0, h-o, w, h-o, fill=self.color, width=t, dash=(15, 10)) # Bottom
        canvas.create_line(o, 0, o, h, fill=self.color, width=t, dash=(15, 10)) # Left
        canvas.create_line(w-o, 0, w-o, h, fill=self.color, width=t, dash=(15, 10)) # Right

        # Ensure the window is click-through on Windows
        if sys.platform == "win32":
            try:
                hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())
                # WS_EX_LAYERED = 0x00080000, WS_EX_TRANSPARENT = 0x00000020
                exStyle = ctypes.windll.user32.GetWindowLongW(hwnd, -20)
                ctypes.windll.user32.SetWindowLongW(hwnd, -20, exStyle | 0x00080000 | 0x00000020)
            except Exception:
                pass

        self.root.mainloop()

    def start(self):
        if not self.is_running:
            self.is_running = True
            self.thread = threading.Thread(target=self._run_overlay, daemon=True)
            self.thread.start()

    def stop(self):
        self.is_running = False
        if self.root:
            try:
                self.root.quit()
                self.root.destroy()
            except Exception:
                pass
        self.root = None

# Testing directly
if __name__ == "__main__":
    import time
    print("Muestra overlay por 3 segs...")
    ov = RecordingOverlay()
    ov.start()
    time.sleep(3)
    ov.stop()
    print("Done")
