import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
from face_matcher import compare_faces

class FaceMatchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Face Matching Mini Tool")

        self.image_paths = {"face1": None, "face2": None}

        self._build_ui()

    def _build_ui(self):
        frame = tk.Frame(self.root, padx=20, pady=20)
        frame.pack()
        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)
        frame.pack(fill="both", expand=True)
        frame.grid_rowconfigure(0, weight=1)   # the row with previews/buttons — let it grow
        frame.grid_rowconfigure(1, weight=0)   # compare button row — stays fixed height
        frame.grid_rowconfigure(2, weight=0)   # result label row — stays fixed height

        self.preview_labels = {}
        for i, key in enumerate(["face1", "face2"]):
            col_frame = tk.Frame(frame)
            col_frame.grid(row=0, column=i, padx=10)
            col_frame.grid(row=0, column=i, padx=10, sticky="nsew")


            label = tk.Label(col_frame, text=f"Face {i + 1}", width=35, height=15, bg="#eee")

            label.pack(fill="both", expand=True)
            self.preview_labels[key] = label

            button = tk.Button(
                col_frame,
                text=f"Select Face {i + 1}",
                command=lambda k=key: self._select_image(k),
            )
            button.pack(pady=5)

        self.compare_button = tk.Button(frame, text="Compare", state="disabled", command=self._compare)
        self.compare_button.grid(row=1, column=0, columnspan=2, pady=15, sticky="ew")

        self.result_label = tk.Label(frame, text="", font=("Arial", 14, "bold"))
        self.result_label.grid(row=2, column=0, columnspan=2, sticky="ew")
    def _select_image(self, key):
        path = filedialog.askopenfilename(
            filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        )
        if not path:
            return

        self.image_paths[key] = path
        self._show_preview(key, path)
        self._update_compare_button_state()

    def _show_preview(self, key, path):
        try:
            img = Image.open(path)
            img.thumbnail((350, 350))
            photo = ImageTk.PhotoImage(img)

            self.preview_labels[key].configure(image=photo, text="", width=0, height=0)
            self.preview_labels[key].image = photo
        except Exception:
            messagebox.showerror("Invalid image", "Could not open that image file.")
            self.image_paths[key] = None
            
    def _update_compare_button_state(self):
        ready = all(self.image_paths.values())
        self.compare_button.configure(state="normal" if ready else "disabled")
        
    def _compare(self):
        self.result_label.configure(text="Comparing...", fg="black")
        self.root.update_idletasks()

        result = compare_faces(self.image_paths["face1"], self.image_paths["face2"])

        if result.error:
            self.result_label.configure(text=result.error, fg="orange")
            return

        if result.is_match:
            self.result_label.configure(text="MATCH", fg="green")
        else:
            self.result_label.configure(text="NO MATCH", fg="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = FaceMatchApp(root)
    root.mainloop()
