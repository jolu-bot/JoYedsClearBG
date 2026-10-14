# main.py
# JoYed'S ClearBG - v1.0
# © 2025 JoYed'S. Tous droits réservés.

import os, json, time
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from tkinterdnd2 import TkinterDnD, DND_FILES
from PIL import Image, ImageTk
from rembg import remove
from datetime import datetime

HISTORY_FILE = "logs.json"

class SplashScreen(tk.Toplevel):
    def __init__(self, master, logo_path):
        super().__init__(master)
        self.overrideredirect(True)
        self.configure(bg="white")
        self.logo = ImageTk.PhotoImage(Image.open(logo_path).resize((180, 180)))
        tk.Label(self, image=self.logo, bg="white").pack(pady=10)
        tk.Label(self, text="JoYed'S ClearBG", font=("Helvetica", 16, "bold"), bg="white", fg="#144aad").pack()
        self.center()
        self.after(2000, self.destroy)

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
        self.output_dir = os.getcwd()

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
        tk.Button(options, text="Supprimer BG", command=self.process_images, bg="#144aad", fg="white").grid(row=0, column=3, padx=10)

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
        link.bind("<Button-1>", lambda e: os.system("open https://joyeds.com"))

    def on_drop(self, event):
        files = self.tk.splitlist(event.data)
        self.images = [f for f in files if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        messagebox.showinfo("Importation", f"{len(self.images)} image(s) chargée(s).")

    def choose_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir = path

    def process_images(self):
        if not self.images:
            messagebox.showwarning("Aucune image", "Glissez des images à traiter.")
            return

        total = len(self.images)
        self.progress["value"] = 0
        self.progress["maximum"] = total

        for i, img_path in enumerate(self.images):
            try:
                img = Image.open(img_path)
                if self.resolution_var.get() != "original":
                    w, h = map(int, self.resolution_var.get().split("x"))
                    img = img.resize((w, h))
                output = remove(img)
                base = os.path.splitext(os.path.basename(img_path))[0]
                save_path = os.path.join(self.output_dir, f"{base}_clear.png")
                output.save(save_path)
                self.log_history(img_path, save_path)
            except Exception as e:
                print(f"Erreur: {e}")
            self.progress["value"] = i + 1
            self.percent_label.config(text=f"{int(((i+1)/total)*100)} %")
            self.update_idletasks()

        messagebox.showinfo("Terminé", "Suppression d’arrière-plan terminée !")

    def log_history(self, original, output):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {os.path.basename(original)} → {os.path.basename(output)}\n"
        self.history_box.config(state="normal")
        self.history_box.insert("end", entry)
        self.history_box.config(state="disabled")

        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
        else:
            data = []

        data.append({"timestamp": timestamp, "input": original, "output": output})
        with open(HISTORY_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def load_history(self):
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r") as f:
                data = json.load(f)
            for item in data[-5:]:
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
            except:
                pass
        self.history_box.config(bg="#2a2a2a" if self.dark_mode else "#f8f8f8", fg=colors["fg"])

if __name__ == "__main__":
    splash = SplashScreen(None, "logo.png")
    app = ClearBGApp()
    app.after(2000, app.deiconify)
    app.withdraw()
    app.mainloop()
