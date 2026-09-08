import threading
import tkinter.font as tkfont
from tkinter import filedialog, messagebox

import customtkinter as ctk
from PIL import Image
from tkinterdnd2 import DND_FILES, TkinterDnD

from face_matcher import MatchResult, compare_faces

# default appearance and theme settings for the application
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

# Color and Font Constants
COLOR_BG = "#f7f8f6"
COLOR_CARD_BG = "#ffffff"
COLOR_CARD_BORDER = "#dfe5e1"
COLOR_ACCENT = "#167d78"
COLOR_ACCENT_HOVER = "#0f625e"
COLOR_ACCENT_LIGHT = "#e7f3f1"
COLOR_ACCENT_DISABLED = "#5f8984"
COLOR_TEXT_PRIMARY = "#17211f"
COLOR_TEXT_SECONDARY = "#52605c"
COLOR_TEXT_MUTED = "#899691"
COLOR_SUCCESS = "#16805c"
COLOR_DANGER = "#c94b4b"
COLOR_WARNING = "#b7791f"

FONT_FAMILY = "Segoe UI"


class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)


class FaceMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Matching Mini Tool")
        self.root.configure(fg_color=COLOR_BG)
        self.root.geometry("760x660")
        self.root.minsize(680, 600)
        self.image_paths = {"face1": None, "face2": None}
        self._build_ui()

    def _build_ui(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=28, pady=28)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

        frame.grid_rowconfigure(0, weight=0)  # Title
        frame.grid_rowconfigure(1, weight=0)  # Subtitle
        frame.grid_rowconfigure(2, weight=1)  # Image cards
        frame.grid_rowconfigure(3, weight=0)  # Buttons
        frame.grid_rowconfigure(4, weight=0)  # Result
        frame.grid_rowconfigure(5, weight=0)  # Status

        # Title
        title = ctk.CTkLabel(
            frame,
            text="Face Matching",
            font=ctk.CTkFont(family=FONT_FAMILY, size=26, weight="bold"),
            text_color=COLOR_TEXT_PRIMARY,
        )
        title.grid(row=0, column=0, columnspan=2, pady=(0, 4))

        # Subtitle
        subtitle = ctk.CTkLabel(
            frame,
            text="Select two face images to compare",
            font=ctk.CTkFont(family=FONT_FAMILY, size=13),
            text_color=COLOR_TEXT_SECONDARY,
        )
        subtitle.grid(row=1, column=0, columnspan=2, pady=(0, 22))

        self.preview_labels = {}
        self.file_labels = {}
        self._default_file_label_width = 270

        blank = Image.new("RGBA", (1, 1), (0, 0, 0, 0))

        self._blank_image = ctk.CTkImage(
            light_image=blank,
            dark_image=blank,
            size=(1, 1),
        )

        # Image cards for face1 and face2
        for i, key in enumerate(["face1", "face2"]):
            card = ctk.CTkFrame(
                frame,
                corner_radius=10,
                border_width=1,
                border_color=COLOR_CARD_BORDER,
                fg_color=COLOR_CARD_BG,
            )
            card.grid(row=2, column=i, padx=8, pady=(0, 6), sticky="nsew")

            caption = ctk.CTkLabel(
                card,
                text=f"Face {i + 1}",
                font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
                text_color=COLOR_TEXT_SECONDARY,
            )
            caption.pack(pady=(16, 6))

            label = ctk.CTkLabel(
                card,
                text="Click or drop an image",
                width=300,
                height=270,
                corner_radius=8,
                fg_color=COLOR_ACCENT_LIGHT,
                text_color=COLOR_ACCENT,
                font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
                cursor="hand2",
            )
            label.pack(padx=16, pady=(0, 14))

            label.bind(
                "<Button-1>",
                lambda e, k=key: self._select_image(k),
            )

            label.drop_target_register(DND_FILES)

            label.dnd_bind(
                "<<Drop>>",
                lambda e, k=key: self._on_drop(e, k),
            )

            label.bind(
                "<Enter>",
                lambda e, k=key: self.preview_labels[k].configure(
                    border_width=2, border_color=COLOR_ACCENT
                ) if not self.image_paths[k] else None,
            )
            label.bind(
                "<Leave>",
                lambda e, k=key: self.preview_labels[k].configure(
                    border_width=0
                ) if not self.image_paths[k] else None,
            )

            self.preview_labels[key] = label

            file_label = ctk.CTkLabel(
                card,
                text="No file selected",
                width=self._default_file_label_width,
                font=ctk.CTkFont(family=FONT_FAMILY, size=11),
                text_color=COLOR_TEXT_MUTED,
            )
            file_label.pack(pady=(0, 16))

            self.file_labels[key] = file_label

        # Compare button
        self.compare_button = ctk.CTkButton(
            frame,
            text="Compare faces",
            state="disabled",
            corner_radius=6,
            height=44,
            font=ctk.CTkFont(family=FONT_FAMILY, size=14, weight="bold"),
            fg_color="#5f8984",
            text_color="#ffffff",
            hover_color="#0f625e",
            command=self._compare,
        )
        self.compare_button.grid(row=3, column=0, pady=(22, 0), padx=(0, 8), sticky="ew")

        # Reset button
        self.reset_button = ctk.CTkButton(
            frame,
            text="Reset",
            corner_radius=6,
            height=44,
            font=ctk.CTkFont(family=FONT_FAMILY, size=13, weight="bold"),
            fg_color="#edf3f1",
            border_width=1,
            border_color="#b8c5c1",
            text_color="#36514c",
            hover_color="#dceae6",
            command=self._reset,
        )
        self.reset_button.grid(row=3, column=1, pady=(22, 0), padx=(8, 0), sticky="ew")

        # Result banner uses color only after a comparison has completed.
        self.result_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            corner_radius=8,
            height=46,
            fg_color="transparent",
        )
        self.result_label.grid(row=4, column=0, columnspan=2, sticky="ew", pady=(16, 4))

        # Supported formats
        self.status_label = ctk.CTkLabel(
            frame,
            text="Supported formats: JPG, JPEG, PNG",
            font=ctk.CTkFont(family=FONT_FAMILY, size=10),
            text_color=COLOR_TEXT_MUTED,
        )
        self.status_label.grid(row=5, column=0, columnspan=2, pady=(4, 0))
    
    # Helper methods for image selection
    def _select_image(self, key):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not path:
            return
        self._set_image(key, path)

    # handles the logic for setting the image, showing a preview, and updating the UI accordingly
    def _set_image(self, key, path):
        if not path.lower().endswith((".jpg", ".jpeg", ".png")):
            messagebox.showerror(
                "Invalid file",
                "Please use a .jpg, .jpeg, or .png image."
            )
            return

        if not self._show_preview(key, path):
            return

        self.image_paths[key] = path
        self._update_compare_button_state()
        self.result_label.configure(text="", fg_color="transparent")

        filename = path.replace("\\", "/").split("/")[-1]
        label_width = self.file_labels[key].cget("width")
        self.file_labels[key].configure(
            text=self._truncate_filename(filename, label_width),
            text_color=COLOR_TEXT_SECONDARY
        )
    
    # handles the drag-and-drop event, extracting the file path and calling _set_image to update the UI
    def _on_drop(self, event, key):
        paths = self.root.tk.splitlist(event.data)
        if not paths:
            return
        self._set_image(key, paths[0])

    # resets the application state, clearing selected images and resetting UI elements to their default state
    def _reset(self):
        self.image_paths = {"face1": None, "face2": None}
        for key in ["face1", "face2"]:
            label = self.preview_labels[key]
            label.configure(image=self._blank_image, text="Click or drop an image")
            label.image = self._blank_image
            self.file_labels[key].configure(
                text="No file selected",
                width=self._default_file_label_width,
                text_color=COLOR_TEXT_MUTED,
            )
        self._update_compare_button_state()
        self.result_label.configure(text="", fg_color="transparent")
    
    # displays a preview of the selected image in the corresponding label
    def _show_preview(self, key, path):
        try:
            img = Image.open(path)
            img.thumbnail((270, 270))

            ctk_image = ctk.CTkImage(
                light_image=img,
                dark_image=img,
                size=img.size
            )

            self.file_labels[key].configure(width=img.width)

            self.preview_labels[key].configure(
                image=ctk_image,
                text=""
            )
            self.preview_labels[key].image = ctk_image

            return True

        except Exception:
            messagebox.showerror(
                "Invalid image",
                "The selected file could not be opened as a valid image."
            )

            return False
    

    # shortens the filename to fit within the specified width, adding an ellipsis if necessary, while ensuring that the text remains readable and does not overflow the label's boundaries
    @staticmethod
    def _truncate_filename(filename, max_width):
        font = tkfont.Font(family=FONT_FAMILY, size=11)
        if font.measure(filename) <= max_width:
            return filename

        suffix = "..."
        truncated = filename
        while truncated and font.measure(truncated + suffix) > max_width:
            truncated = truncated[:-1]

        return truncated + suffix if truncated else suffix

    # updates the state of the compare button based on whether both images have been selected, enabling it only when both images are ready for comparison
    def _update_compare_button_state(self):
        ready = all(self.image_paths.values())
        if ready:
            self.compare_button.configure(
                state="normal", fg_color=COLOR_ACCENT, text_color="#ffffff", hover_color=COLOR_ACCENT_HOVER
            )
        else:
            self.compare_button.configure(
                state="disabled",
                fg_color=COLOR_ACCENT_DISABLED,
                text_color="#ffffff",
                hover_color=COLOR_ACCENT_DISABLED,
                font=ctk.CTkFont(family=FONT_FAMILY, size=15, weight="bold"),
            )

    # threading to avoid freezing the GUI during comparison
    def _compare(self):
        self.compare_button.configure(state="disabled", text="Comparing...")
        self.reset_button.configure(state="disabled")
        self._set_result("Comparing...", bg=COLOR_CARD_BORDER, fg=COLOR_TEXT_SECONDARY)

        thread = threading.Thread(
            target=self._run_compare_in_background,
            args=(self.image_paths["face1"], self.image_paths["face2"]),
            daemon=True,
        )
        thread.start()
    
    # runs the face comparison in a separate thread to keep the GUI responsive, and schedules the result handling on the main thread
    def _run_compare_in_background(self, path1, path2):
        try:
            result = compare_faces(path1, path2)
        except Exception:
            result = MatchResult(
                is_match=False,
                distance=1.0,
                error="An unexpected error occurred during comparison.",
            )

        self.root.after(0, self._on_compare_finished, result)
    
    # updates the UI based on the result of the face comparison, displaying whether the faces match and the distance metric
    def _on_compare_finished(self, result):
        self.compare_button.configure(text="Compare faces")
        self.reset_button.configure(state="normal")
        self._update_compare_button_state()

        if result.error:
            self._set_result(f"⚠  {result.error}", bg=COLOR_WARNING, fg="white")
            return

        if result.is_match:
            self._set_result(
                f"✓  MATCH   ·   Distance: {result.distance:.3f}", bg=COLOR_SUCCESS, fg="white"
            )
        else:
            self._set_result(
                f"✕  NO MATCH   ·   Distance: {result.distance:.3f}",
                bg=COLOR_DANGER,
                fg="white",
            )

              
    # sets the result label's text and background color based on the comparison outcome
    def _set_result(self, text, bg, fg):
        self.result_label.configure(text=text, fg_color=bg, text_color=fg)
