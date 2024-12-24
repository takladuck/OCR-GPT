import customtkinter as ctk
from recognition.screenshot import ScreenshotTool
from generative_ai import gemini_client
import re
import time
from recognition import tesseract_ocr as mod


def takeScreenshot():
    root.withdraw()
    time.sleep(0.5)
    screenshot_tool = ScreenshotTool(root)
    screenshot_tool.run()
    time.sleep(0.2)
    root.deiconify()
    ocrToTextbox()


def ocrToTextbox():
    text = mod.oer_out()
    text_box.insert("end", text)

def send_to_gemini():
    text = text_box.get("1.0", "end-1c")
    response = gemini_client.generate_content(text)
    processed_response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
    large_text_box.insert("end", f"YOU: \n{text}\n\nGEMINI: \n{processed_response}\n-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  \n\n")



def clear():
    text_box.delete("1.0", "end")
    large_text_box.delete("1.0", "end")
    show_message("Cleared")

def copy_to_clipboard():
    root.clipboard_clear()
    root.clipboard_append(text_box.get("1.0", "end-1c"))
    show_message("Copied to clipboard")


def show_message(message):
    message_label = ctk.CTkLabel(root, text=message, fg_color="grey", corner_radius=8, text_color="black")
    message_label.place(x=30,y=400)
    root.after(800, message_label.destroy)


def start_gui():
    global root, text_box, large_text_box
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    root = ctk.CTk()
    root.title("OCR-GPT")

    left_frame = ctk.CTkFrame(root)
    left_frame.pack(side="left", padx=10, pady=10)

    text_box = ctk.CTkTextbox(left_frame, height=200, width=350, wrap="word")
    text_box.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    button = ctk.CTkButton(left_frame, text="New Screenshot", command=takeScreenshot)
    button.grid(row=1, column=0, padx=5, pady=5)

    button = ctk.CTkButton(left_frame, text="Send to Gemini", command=send_to_gemini)
    button.grid(row=1, column=1, padx=5, pady=5)

    button = ctk.CTkButton(left_frame, text="Clear", command=clear)
    button.grid(row=2, column=0, padx=5, pady=5)

    button = ctk.CTkButton(left_frame, text="Copy", command = copy_to_clipboard)
    button.grid(row=2, column=1, padx=5, pady=5)

    right_frame = ctk.CTkFrame(root)
    right_frame.pack(side="right", padx=10, pady=10)

    large_text_box = ctk.CTkTextbox(right_frame, height=450, width=350, wrap="word")
    large_text_box.pack()

    root.mainloop()