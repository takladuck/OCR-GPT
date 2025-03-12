import tkinter as tk
from PIL import ImageGrab, Image, ImageTk
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception as e:
    print(f"Could not set DPI awareness: {e}")

class ScreenshotTool:
    def __init__(self, root):
        self.root = root
        self.top = tk.Toplevel(self.root)
        self.top.attributes("-fullscreen", True)
        self.top.attributes("-alpha", 1)
        self.top.attributes("-topmost", True)

        self.screen_image = ImageGrab.grab()
        self.dimmed_image = self.create_dimmed_image(self.screen_image)
        self.photo_image = ImageTk.PhotoImage(self.dimmed_image)

        self.canvas = tk.Canvas(self.top, cursor="cross")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo_image)

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.highlight_rect = None

        self.canvas.bind("<ButtonPress-1>", self.on_button_press)
        self.canvas.bind("<B1-Motion>", self.on_mouse_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_button_release)

    def create_dimmed_image(self, image):
        dimmed = image.convert("RGBA")
        overlay = Image.new("RGBA", dimmed.size, (0, 0, 0, 150))
        return Image.alpha_composite(dimmed, overlay)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='red', width=2)

    def on_mouse_drag(self, event):
        current_x = event.x
        current_y = event.y
        self.canvas.coords(self.rect, self.start_x, self.start_y, current_x, current_y)
        self.highlight_selected_area(self.start_x, self.start_y, current_x, current_y)

    def highlight_selected_area(self, x1, y1, x2, y2):
        self.canvas.delete(self.highlight_rect)
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        cropped_image = self.screen_image.crop((left, top, right, bottom))
        self.highlight_photo = ImageTk.PhotoImage(cropped_image)
        self.highlight_rect = self.canvas.create_image(left, top, anchor=tk.NW, image=self.highlight_photo)

    def on_button_release(self, event):
        end_x = event.x
        end_y = event.y
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        right = max(self.start_x, end_x)
        bottom = max(self.start_y, end_y)
        screenshot = ImageGrab.grab(bbox=(left, top, right, bottom))
        screenshot.save("screenshot.png")
        print("Screenshot saved as screenshot.png")
        self.top.quit()
        self.top.destroy()

    def cancel_screenshot(self, event=None):
        self.top.quit()
        self.top.destroy()

    def run(self):
        self.top.mainloop()