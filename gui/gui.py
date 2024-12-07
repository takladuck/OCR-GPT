import tkinter as tk
from screenshot import ScreenshotTool
from tkinter import messagebox



def takeScreenshot():
    screenshot_tool = ScreenshotTool()
    screenshot_tool.run()

root = tk.Tk()
root.title("OCR-GPT")

left_frame = tk.Frame(root)
left_frame.pack(side="left", padx=10, pady=10)

text_box = tk.Text(left_frame, height=5, width=30)
text_box.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

button = tk.Button(left_frame, text=f"New Screenshot",command=takeScreenshot)
button.grid(row=1, column=0, padx=5, pady=5)

button = tk.Button(left_frame, text=f"Send to GPT")
button.grid(row=1, column=1, padx=5, pady=5)

button = tk.Button(left_frame, text=f"+ Add Text")
button.grid(row=2, column=0, padx=5, pady=5)

button = tk.Button(left_frame, text=f"Copy")
button.grid(row=2, column=1, padx=5, pady=5)

right_frame = tk.Frame(root)
right_frame.pack(side="right", padx=10, pady=10)

large_text_box = tk.Text(right_frame, height=15, width=40)
large_text_box.pack()

root.mainloop()
