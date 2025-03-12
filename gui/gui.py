import customtkinter as ctk
from recognition.screenshot import ScreenshotTool
from generative_ai import gemini_client
import re
import time
import threading
import queue
from recognition import tesseract_ocr as mod
import sys
from system_integration import (
    setup_hotkey, setup_tray, run_tray_icon,
    stop_tray_icon, is_in_startup
)

# Global variables
root = None
text_box = None
large_text_box = None
is_running = True
# Queue for thread-safe communication
command_queue = queue.Queue()


def process_command_queue():
    """Process commands from the queue to ensure they run on the main thread"""
    try:
        while not command_queue.empty():
            command = command_queue.get_nowait()
            if isinstance(command, tuple) and command[0] == "gemini_response":
                # Handle Gemini response
                text, response = command[1], command[2]
                large_text_box.insert("end",
                                      f"YOU: \n{text}\n\nGEMINI: \n{response}\n-  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  -  \n\n")
            elif command == "screenshot":
                execute_screenshot()
            elif command == "ocr":
                execute_ocr()
    except Exception as e:
        print(f"Error processing command queue: {e}")

    # Schedule the next check if the application is still running
    if is_running and root and root.winfo_exists():
        root.after(100, process_command_queue)


def execute_screenshot():
    """Execute screenshot capture on the main thread"""
    if root:
        root.withdraw()
    time.sleep(0.5)
    screenshot_tool = ScreenshotTool(root)
    screenshot_tool.run()
    time.sleep(0.2)
    if root and root.winfo_exists():
        root.deiconify()
        command_queue.put("ocr")


def execute_ocr():
    """Execute OCR on the main thread"""
    text = mod.oer_out()
    text_box.insert("end", text)


def takeScreenshot():
    """Queue the screenshot command to be executed on the main thread"""
    command_queue.put("screenshot")


def ocrToTextbox():
    """Queue the OCR command to be executed on the main thread"""
    command_queue.put("ocr")


def send_to_gemini():
    """Send text to Gemini API and handle the response through the command queue"""
    text = text_box.get("1.0", "end-1c")

    # Use a thread for the API call to avoid blocking the UI
    def gemini_thread():
        try:
            response = gemini_client.generate_content(text)
            processed_response = re.sub(r'\*\*(.*?)\*\*', r'\1', response)
            # Put the response in the command queue instead of directly updating the UI
            command_queue.put(("gemini_response", text, processed_response))
        except Exception as e:
            print(f"Error in Gemini thread: {e}")
            command_queue.put(("gemini_response", text, f"Error: {str(e)}"))

    # Start the thread
    thread = threading.Thread(target=gemini_thread, daemon=True)
    thread.start()


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
    message_label.place(x=30, y=400)
    root.after(800, message_label.destroy)


def exit_application():
    """Properly exit the application"""
    global is_running, root
    is_running = False
    stop_tray_icon()
    if root and root.winfo_exists():
        root.quit()
    sys.exit(0)


def show_window():
    """Show the main application window"""
    global root
    if root is None or not root.winfo_exists():
        start_gui(show_immediately=True)
    else:
        root.deiconify()


def minimize_to_tray():
    """Minimize the application to the system tray"""
    clear()
    if root:
        root.withdraw()


def start_gui(show_immediately=True, start_minimized=False):
    global root, text_box, large_text_box

    # Only initialize GUI if not already initialized
    if root is None or not root.winfo_exists():
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        root = ctk.CTk()
        root.title("OCR-GPT")

        # Override close button to minimize to tray
        root.protocol("WM_DELETE_WINDOW", minimize_to_tray)

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

        button = ctk.CTkButton(left_frame, text="Copy", command=copy_to_clipboard)
        button.grid(row=2, column=1, padx=5, pady=5)

        right_frame = ctk.CTkFrame(root)
        right_frame.pack(side="right", padx=10, pady=10)

        large_text_box = ctk.CTkTextbox(right_frame, height=450, width=350, wrap="word")
        large_text_box.pack()

        # Start command queue processing
        root.after(100, process_command_queue)

        # If we should start minimized
        if start_minimized:
            root.withdraw()

    # If root exists but we need to show it
    elif show_immediately:
        root.deiconify()

    # Start the mainloop if this is the first initialization
    if show_immediately and not start_minimized:
        root.mainloop()


def initialize_background_services():
    """Initialize all background services needed before GUI starts"""
    # Set up the hotkey
    setup_hotkey(takeScreenshot)

    # Set up the system tray
    tray_icon = setup_tray(show_window, takeScreenshot, exit_application)

    # Run the tray icon in a separate thread
    tray_thread = threading.Thread(target=run_tray_icon, args=(tray_icon,))
    tray_thread.daemon = True
    tray_thread.start()

    return tray_thread