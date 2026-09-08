import customtkinter as ctk

from gui import FaceMatchApp, CTkDnD


def main(): 
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")
    
    # Create the main application window using CTkDnD, which is a custom Tkinter window with drag-and-drop support.
    root = CTkDnD()

    FaceMatchApp(root)

    window_width = 720
    window_height = 600

    root.update_idletasks()

    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)

    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(window_width, window_height)

    root.mainloop()


if __name__ == "__main__":
    main()