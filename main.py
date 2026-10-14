# main.py
# JoYed'S ClearBG - v1.0
# © 2025 JoYed'S. Tous droits réservés.

import os, sys, json, threading, queue, webbrowser
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk, ImageOps
from rembg import remove
from datetime import datetime

EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp', '.bmp')


def resource_path(name):
    """Resolve a bundled resource (works from source and from a py2app bundle)."""
    base = os.environ.get("RESOURCEPATH") or os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, name)


def data_dir():
    """Writable per-user folder for the history file."""
    if sys.platform == "darwin":
        path = os.path.expanduser("~/Library/Application Support/JoYedsClearBG")
    else:
        path = os.path.expanduser("~/.joyeds_clearbg")
    os.makedirs(path, exist_ok=True)
    return path


HISTORY_FILE = os.path.join(data_dir(), "logs.json")

class SplashScreen(tk.Toplevel):
    def __init__(self, master, logo_path):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="white")
        self.logo = ImageTk.PhotoImage(Image.open(logo_path).resize((180, 180)))
        tk.Label(self, image=self.logo, bg="white").pack(pady=10)
        tk.Label(self, text="JoYed'S ClearBG", font=("Helvetica", 16, "bold"), bg="white", fg="#144aad").pack()
        self.center()

    def center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        x = (self.winfo_screenwidth() - w) // 2
        y = (self.winfo_screenheight() - h) // 2
        self.geometry(f"+{x}+{y}")

class ClearBGApp(TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("JoYed'S ClearBG")
        self.geometry("700x500")
        self.configure(bg="white")
        self.dark_mode = False
        self.images = []
        pictures = os.path.expanduser("~/Pictures")
        self.output_dir = pictures if os.path.isdir(pictures) else os.path.expanduser("~")
        self.results = queue.Queue()
        self.processing = False
        self.errors = []

        self.create_widgets()
        self.load_history()

    def create_widgets(self):
        top = tk.Frame(self, bg="white")
        top.pack(pady=10)
        self.drop_area = tk.Label(top, text="📁 Glissez vos images ici", relief="groove", width=60, height=6, bg="#f0f0f0")
        self.drop_area.pack()
        self.drop_area.drop_target_register(DND_FILES)
        self.drop_area.dnd_bind('<<Drop>>', self.on_drop)

        options = tk.Frame(self, bg="white")
        options.pack(pady=10)

        tk.Label(options, text="Résolution cible:", bg="white").grid(row=0, column=0, padx=5)
        self.resolution_var = tk.StringVar(value="original")
        tk.OptionMenu(options, self.resolution_var, "original", "640x480", "800x600", "1024x768").grid(row=0, column=1, padx=5)

        tk.Button(options, text="Choisir dossier sortie", command=self.choose_output).grid(row=0, column=2, padx=10)
        self.run_button = tk.Button(options, text="Supprimer BG", command=self.process_images, bg="#144aad", fg="white")
        self.run_button.grid(row=0, column=3, padx=10)

        self.progress = ttk.Progressbar(self, orient="horizontal", mode="determinate", length=400)
        self.progress.pack(pady=10)
        self.percent_label = tk.Label(self, text="0 %", bg="white")
        self.percent_label.pack()

        self.history_box = tk.Text(self, height=6, state="disabled", bg="#f8f8f8")
        self.history_box.pack(padx=10, pady=10, fill="x")

        # Theme toggle
        tk.Button(self, text="🌓", command=self.toggle_theme, width=3).pack(side="right", padx=10)

        link = tk.Label(self, text="Powered by JoYed'S", fg="#144aad", cursor="hand2", bg="white")
        link.pack(side="bottom")
        link.bind("<Button-1>", lambda e: webbrowser.open("https://joyeds.com"))

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.images = [f for f in files if f.lower().endswith(EXTENSIONS)]
        messagebox.showinfo("Importation", f"{len(self.images)} image(s) chargée(s).")

    def choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path

    def process_images(self):
        if self.processing:
            return
        if not self.images:
            messagebox.showwarning("Aucune image", "Glissez des images à traiter.")
            return

        self.processing = True
        self.run_button.config(state="disabled")
        self.progress["value"] = 0
        self.progress["maximum"] = len(self.images)
        self.percent_label.config(text="0 %")
        threading.Thread(
            target=self._worker,
            args=(list(self.images), self.resolution_var.get(), self.output_dir),
            daemon=True,
        ).start()
        self.after(100, self._poll)

    def _worker(self, images, resolution, output_dir):
        for img_path in images:
            try:
                img = Image.open(img_path)
                if resolution != "original":
                    w, h = map(int, resolution.split("x"))
                    img = ImageOps.contain(img, (w, h))
                output = remove(img)
                base = os.path.splitext(os.path.basename(img_path))[0]
                save_path = os.path.join(output_dir, f"{base}_clear.png")
                output.save(save_path)
                self.results.put((img_path, save_path, None))
            except Exception as e:
                self.results.put((img_path, None, str(e)))
        self.results.put(None)

    def _poll(self):
        done = False
        while True:
            try:
                item = self.results.get_nowait()
            except queue.Empty:
                break
            if item is None:
                done = True
                break
            img_path, save_path, error = item
            if error:
                self.errors.append(f"{os.path.basename(img_path)} : {error}")
            else:
                self.log_history(img_path, save_path)
            self.progress["value"] += 1
            pct = int(self.progress["value"] / self.progress["maximum"] * 100)
            self.percent_label.config(text=f"{pct} %")

        if not done:
            self.after(100, self._poll)
            return

        self.processing = False
        self.run_button.config(state="normal")
        if self.errors:
            messagebox.showwarning("Terminé avec erreurs", "\n".join(self.errors))
            self.errors = []
        else:
            messagebox.showinfo("Terminé", "Suppression d’arrière-plan terminée !")

    def log_history(self, original, output):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {os.path.basename(original)} → {os.path.basename(output)}\n"
        self.history_box.config(state="normal")
        self.history_box.insert("end", entry)
        self.history_box.config(state="disabled")

        data = self.read_history()
        data.append({"timestamp": timestamp, "input": original, "output": output})
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def read_history(self):
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (OSError, ValueError):
            return []

    def load_history(self):
        for item in self.read_history()[-5:]:
            entry = f"[{item['timestamp']}] {os.path.basename(item['input'])} → {os.path.basename(item['output'])}\n"
            self.history_box.config(state="normal")
            self.history_box.insert("end", entry)
            self.history_box.config(state="disabled")

    def toggle_theme(self):
        self.dark_mode = not self.dark_mode
        colors = {
            True: {"bg": "#1e1e1e", "fg": "white"},
            False: {"bg": "white", "fg": "black"}
        }[self.dark_mode]
        self.configure(bg=colors["bg"])
        for child in self.winfo_children():
            try:
                child.configure(bg=colors["bg"], fg=colors["fg"])
            except tk.TclError:
                pass
        self.history_box.config(bg="#2a2a2a" if self.dark_mode else "#f8f8f8", fg=colors["fg"])

if __name__ == "__main__":
    app = ClearBGApp()
    app.withdraw()
    splash = SplashScreen(app, resource_path("logo.png"))

    def show_main():
        if splash.winfo_exists():
            splash.destroy()
        app.deiconify()

    app.after(2000, show_main)
    app.mainloop()
