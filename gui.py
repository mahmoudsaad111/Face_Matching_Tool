import tkinter as tk
import customtkinter as ctk
import threading
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from face_matcher import compare_faces, distance_to_confidence
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image as PILImage



class CTkDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class FaceMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Matching Mini Tool")
        self.image_paths = {"face1": None, "face2": None}
        self._build_ui()


    def _build_ui(self):
        frame = ctk.CTkFrame(self.root, fg_color="transparent")
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=0)
        

        self.preview_labels = {}
        self.file_labels = {}
        blank = PILImage.new("RGBA", (1, 1), (0, 0, 0, 0))
        self._blank_image = ctk.CTkImage(light_image=blank, dark_image=blank, size=(1, 1))
        for i, key in enumerate(["face1", "face2"]):
            card = ctk.CTkFrame(frame, corner_radius=12, border_width=2, border_color="#d1d5db")
            card.grid(row=0, column=i, padx=10, sticky="nsew")

            caption = ctk.CTkLabel(
                card,
                text=f"Face {i + 1}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#6b7280",
            )
            caption.pack(pady=(12, 4))

            label = ctk.CTkLabel(
                card,
                text="+",
                width=300,
                height=280,
                fg_color="#f3f4f6",
                corner_radius=8,
                text_color="#9ca3af",
                font=ctk.CTkFont(size=48, weight="bold"),
                cursor="hand2",
            )
            label.pack(padx=12, pady=(0, 12))
            label.bind("<Button-1>", lambda e, k=key: self._select_image(k))

            label.drop_target_register(DND_FILES)
            label.dnd_bind('<<Drop>>', lambda e, k=key: self._on_drop(e, k))

            self.preview_labels[key] = label

            file_label = ctk.CTkLabel(
                card,
                text="No file selected",
                font=ctk.CTkFont(size=11),
                text_color="#9ca3af",
            )
            file_label.pack(pady=(0, 12))
            self.file_labels[key] = file_label

        self.compare_button = ctk.CTkButton(
            frame,
            text="Compare",
            state="disabled",
            corner_radius=8,
            height=42,
            font=ctk.CTkFont(size=15, weight="bold"),
            fg_color="#9ca3af",
            hover_color="#9ca3af",
            command=self._compare,
        )
        self.compare_button.grid(row=1, column=0, pady=15, padx=(0, 5), sticky="ew")
        self.reset_button = ctk.CTkButton(
                frame,
                text="Reset",
                corner_radius=8,
                height=42,
                font=ctk.CTkFont(size=14),
                fg_color="transparent",
                border_width=1,
                border_color="#d1d5db",
                text_color="#374151",
                hover_color="#f3f4f6",
                command=self._reset,
            )
        self.reset_button.grid(row=1, column=1, pady=15, padx=(5, 0), sticky="ew")
        self.result_label = ctk.CTkLabel(
            frame,
            text="",
            font=ctk.CTkFont(size=16, weight="bold"),
            corner_radius=8,
            height=44,
            fg_color="transparent",
        )
        self.result_label.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0, 5))


    def _select_image(self, key):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not path:
            return
        self._set_image(key, path)

    def _set_image(self, key, path):
        if not path.lower().endswith((".jpg", ".jpeg", ".png")):
            messagebox.showerror("Invalid file", "Please use a .jpg, .jpeg, or .png image.")
            return
        self.image_paths[key] = path
        self._show_preview(key, path)
        self._update_compare_button_state()
        self.result_label.configure(text="", fg_color="transparent")

        filename = path.replace("\\", "/").split("/")[-1]
        self.file_labels[key].configure(text=filename, text_color="#374151")

    def _on_drop(self, event, key):
        paths = self.root.tk.splitlist(event.data)
        if not paths:
            return
        self._set_image(key, paths[0])

    def _reset(self):
        self.image_paths = {"face1": None, "face2": None}
        for key in ["face1", "face2"]:
            label = self.preview_labels[key]
            label.configure(image=self._blank_image, text="+")
            label.image = self._blank_image
            self.file_labels[key].configure(text="No file selected", text_color="#9ca3af")
        self._update_compare_button_state()
        self.result_label.configure(text="", fg_color="transparent")

    def _show_preview(self, key, path):
        try:
            img = Image.open(path)
            img.thumbnail((280, 280))

            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=img.size)

            self.preview_labels[key].configure(image=ctk_image, text="")
            self.preview_labels[
                key
            ].image = ctk_image  # keep a reference so it isn't garbage-collected
        except Exception as e:
            print("REAL ERROR:", e)
            face_label = "Face 1" if key == "face1" else "Face 2"
            messagebox.showerror(
                "Invalid image",
                f"Could not open the image for {face_label}."
            )
            self.image_paths[key] = None

    def _update_compare_button_state(self):
        ready = all(self.image_paths.values())
        if ready:
            self.compare_button.configure(
                state="normal", fg_color="#4f46e5", hover_color="#4338ca"
            )
        else:
            self.compare_button.configure(
                state="disabled", fg_color="#9ca3af", hover_color="#9ca3af"
            )


    # threading to avoid freezing the GUI during comparison
    def _compare(self):
        self.compare_button.configure(state="disabled", text="Comparing...")
        self.reset_button.configure(state="disabled")
        self._set_result("Comparing...", bg="#e5e7eb", fg="#374151")

        thread = threading.Thread(
            target=self._run_compare_in_background,
            args=(self.image_paths["face1"], self.image_paths["face2"]),
            daemon=True,
        )
        thread.start()

    def _run_compare_in_background(self, path1, path2):
        result = compare_faces(path1, path2)
        self.root.after(0, self._on_compare_finished, result)

    def _on_compare_finished(self, result):
        self.compare_button.configure(text="Compare")
        self.reset_button.configure(state="normal")
        self._update_compare_button_state()

        if result.error:
            self._set_result(f"⚠ {result.error}", bg="#f59e0b", fg="white")
            return

        confidence = distance_to_confidence(result.distance)

        if result.is_match:
            self._set_result(f"✓ MATCH  ·  {confidence}% confidence", bg="#16a34a", fg="white")
        else:
            self._set_result(f"✕ NO MATCH  ·  {confidence}% confidence", bg="#dc2626", fg="white")

    def _set_result(self, text, bg, fg):
        self.result_label.configure(text=text, fg_color=bg, text_color=fg)


if __name__ == "__main__":
    ctk.set_appearance_mode("light")
    ctk.set_default_color_theme("blue")

    root = CTkDnD()
    app = FaceMatchApp(root)

    window_width, window_height = 700, 520
    root.update_idletasks()  # forces geometry calculations before we read screen size
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    root.minsize(window_width, window_height)

    root.mainloop()
