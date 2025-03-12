import sys
from gui import gui
from system_integration import is_in_startup

if __name__ == '__main__':
    # Initialize background services first (hotkey listener, system tray)
    tray_thread = gui.initialize_background_services()

    # Check if launched at startup and should start minimized
    start_minimized = is_in_startup() and "--minimized" in sys.argv

    # Start the GUI (minimized or normal based on the condition)
    gui.start_gui(start_minimized=start_minimized)