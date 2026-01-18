import customtkinter as ctk
import subprocess
import threading
import os
import json
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox
import psutil

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Grabador Fuente MPD - KEY:KID")
        self.geometry("700 x 550")
        self.process = None

        #variables
        self.url_var = ctk.StringVar()
        self.nombre_var = ctk.StringVar()
        self.kid_var = ctk.StringVar()
        self.key_var = ctk.StringVar()
        self.save_path = ctk.StringVar(value=os.getcwd())
        self.selected_preset_var = ctk.StringVar()
        self.presets = []

        self.create_widgets()
        self.load_presets()

    def create_widgets(self):
        ctk.CTkLabel(self, text="Grabador Fuente MPD - KEY:KID", font=("Roboto", 24, "bold")).pack(pady=20)

        #form
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.form_frame, text="URL del MPD:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.url_var, width=400).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.form_frame, text="Nombre:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.nombre_var, width=400).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.form_frame, text="KID:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.kid_var, width=400).grid(row=2, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.form_frame, text="KEY:").grid(row=3, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.key_var, width=400).grid(row=3, column=1, padx=10, pady=5)

        ctk.CTkButton(self.form_frame, text="Seleccionar Carpeta", command=self.select_folder).grid(row=4, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.form_frame, textvariable=self.save_path, font=("Arial", 10)).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=20)

        self.btn_start = ctk.CTkButton(self.btn_frame, text="🔴 INICIAR GRABACIÓN", fg_color="green", hover_color="darkgreen", command=self.start_recording)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="⬛ PARAR", fg_color="red", hover_color="darkred", command=self.stop_recording, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_save_cfg = ctk.CTkButton(self.btn_frame, text="💾 GUARDAR DATOS", command=self.save_presets)
        self.btn_save_cfg.grid(row=0, column=2, padx=10)

        self.preset_frame = ctk.CTkFrame(self)
        self.preset_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.preset_frame, text="Preset:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.preset_combo = ctk.CTkComboBox(self.preset_frame, variable=self.selected_preset_var, values=[])
        self.preset_combo.grid(row=0, column=1, padx=10, pady=5)
        ctk.CTkButton(self.preset_frame, text="Cargar", command=self.load_selected_preset).grid(row=0, column=2, padx=10)

        self.textbox = ctk.CTkTextbox(self, height=150)
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path:
            self.save_path.set(path)

    def start_recording(self):
        if not self.url_var.get() or not self.kid_var.get() or not self.key_var.get():
            messagebox.showerror("Error", "Faltan datos (URL, KID o KEY)")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"Grabacion_{timestamp}"
        self.current_name = name
        key_full = f"{self.kid_var.get()}:{self.key_var.get()}"
        
        command = [
            "N_m3u8DL-RE.exe",
            self.url_var.get(),
            "--key", key_full,
            "--save-name", name,
            "--save-dir", self.save_path.get(),
            "--auto-select",
            "--live-pipe-mux"
        ]

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.textbox.insert("end", f"Iniciando grabación: {name}\n")

        # de momento hilo separado para evitar el freezeoo
        self.thread = threading.Thread(target=self.run_process, args=(command,), daemon=True)
        self.thread.start()

    def run_process(self, command):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        for line in self.process.stdout:
            self.textbox.insert("end", line)
            self.textbox.see("end")
        self.process.wait()
        self.after(0, self._on_process_end)

    def _on_process_end(self):
        self.process = None
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.textbox.insert("end", "\n--- GRABACIÓN FINALIZADA ---\n")

    def stop_recording(self):
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True):
                    child.kill()
                parent.kill()
            except psutil.NoSuchProcess:
                pass  
            self.process = None
            # Borrar la carpeta  de los datos m4s y demas encriptados
            if hasattr(self, 'current_name'):
                folder_path = os.path.join(self.save_path.get(), self.current_name)
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            self.textbox.insert("end", "\n--- GRABACIÓN FINALIZADA ---\n")
        
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
#queguarde los datos en un archivo json para la proxima vez que se abra la aplicacion
    def save_presets(self):
        nombre = self.nombre_var.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Ingresa un nombre para el preset.")
            return
        # Buscar si existe
        existing = next((p for p in self.presets if p.get("nombre") == nombre), None)
        if existing:
            existing.update({
                "url": self.url_var.get(),
                "kid": self.kid_var.get(),
                "key": self.key_var.get(),
                "path": self.save_path.get()
            })
        else:
            self.presets.append({
                "nombre": nombre,
                "url": self.url_var.get(),
                "kid": self.kid_var.get(),
                "key": self.key_var.get(),
                "path": self.save_path.get()
            })
        with open("presets.json", "w") as f:
            json.dump(self.presets, f)
        self.preset_combo.configure(values=[p.get("nombre", "") for p in self.presets])
        messagebox.showinfo("Guardado", "Preset guardado.")

    def load_selected_preset(self):
        nombre = self.selected_preset_var.get()
        preset = next((p for p in self.presets if p.get("nombre") == nombre), None)
        if preset:
            self.url_var.set(preset.get("url", ""))
            self.nombre_var.set(preset.get("nombre", ""))
            self.kid_var.set(preset.get("kid", ""))
            self.key_var.set(preset.get("key", ""))
            self.save_path.set(preset.get("path", os.getcwd()))
        else:
            messagebox.showerror("Error", "Preset no encontrado.")

    def load_presets(self):
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.presets = data
                elif isinstance(data, dict):
                    # presets del json personal ( de momento para guardar varias fuentes)
                    self.presets = [data]
                else:
                    self.presets = []
        else:
            self.presets = []
        self.preset_combo.configure(values=[p.get("nombre", "") for p in self.presets])

if __name__ == "__main__":
    app = RecorderApp()
    app.mainloop()