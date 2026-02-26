import tkinter as tk
import utils
# Use modern UI
from ui.main_window_modern import MainWindow

def main():
    # Setup hidden logging (brainstormed feature)
    utils.setup_hidden_logging()
    
    root = tk.Tk()
    app = MainWindow(root)
    root.mainloop()

if __name__ == "__main__":
    main()
