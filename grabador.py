import customtkinter as ctk
import subprocess
import threading
import os
import json
from datetime import datetime
from tkinter import filedialog, messagebox

# Configuración de apariencia
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Grabador Fuente MPD - KEY:KID")
        self.geometry("700 x 550")
        self.process = None

        # Variables
        self.url_var = ctk.StringVar()
        self.kid_var = ctk.StringVar()
        self.key_var = ctk.StringVar()
        self.save_path = ctk.StringVar(value=os.getcwd())

        self.create_widgets()
        self.load_presets()

    def create_widgets(self):
        # Título
        ctk.CTkLabel(self, text="DASH LIVE RECORDER", font=("Roboto", 24, "bold")).pack(pady=20)

        # Formulario
        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        ctk.CTkLabel(self.form_frame, text="URL del MPD:").grid(row=0, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.url_var, width=400).grid(row=0, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.form_frame, text="KID:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.kid_var, width=400).grid(row=1, column=1, padx=10, pady=5)

        ctk.CTkLabel(self.form_frame, text="KEY:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=self.key_var, width=400).grid(row=2, column=1, padx=10, pady=5)

        # Directorio
        ctk.CTkButton(self.form_frame, text="Seleccionar Carpeta", command=self.select_folder).grid(row=3, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.form_frame, textvariable=self.save_path, font=("Arial", 10)).grid(row=3, column=1, padx=10, pady=10, sticky="w")

        # Botones de Acción
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=20)

        self.btn_start = ctk.CTkButton(self.btn_frame, text="🔴 INICIAR GRABACIÓN", fg_color="green", hover_color="darkgreen", command=self.start_recording)
        self.btn_start.grid(row=0, column=0, padx=10)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="⬛ PARAR", fg_color="red", hover_color="darkred", command=self.stop_recording, state="disabled")
        self.btn_stop.grid(row=0, column=1, padx=10)

        self.btn_save_cfg = ctk.CTkButton(self.btn_frame, text="💾 GUARDAR DATOS", command=self.save_presets)
        self.btn_save_cfg.grid(row=0, column=2, padx=10)

        # Consola de salida
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
        key_full = f"{self.kid_var.get()}:{self.key_var.get()}"
        
        # Comando corregido
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

        # Ejecutar en hilo separado para no congelar la ventana
        self.thread = threading.Thread(target=self.run_process, args=(command,), daemon=True)
        self.thread.start()

    def run_process(self, command):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, shell=True)
        for line in self.process.stdout:
            self.textbox.insert("end", line)
            self.textbox.see("end")
        self.process.wait()
        self.stop_recording()

    def stop_recording(self):
        if self.process:
            # Enviamos señal de interrupción
            self.process.terminate()
            self.process = None
            self.textbox.insert("end", "\n--- GRABACIÓN FINALIZADA ---\n")
        
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")

    def save_presets(self):
        data = {
            "url": self.url_var.get(),
            "kid": self.kid_var.get(),
            "key": self.key_var.get(),
            "path": self.save_path.get()
        }
        with open("presets.json", "w") as f:
            json.dump(data, f)
        messagebox.showinfo("Guardado", "Datos guardados para la próxima vez.")

    def load_presets(self):
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                data = json.load(f)
                self.url_var.set(data.get("url", ""))
                self.kid_var.set(data.get("kid", ""))
                self.key_var.set(data.get("key", ""))
                self.save_path.set(data.get("path", os.getcwd()))

if __name__ == "__main__":
    app = RecorderApp()
    app.mainloop()