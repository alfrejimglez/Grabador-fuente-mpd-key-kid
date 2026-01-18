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

        self.title("Grabador Multifuente 2026 - Preview Edition")
        self.geometry("800x650")
        self.process = None
        self.preview_process = None # Para controlar la ventana de video

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
        ctk.CTkLabel(self, text="Grabador con Vista Previa en Tiempo Real", font=("Roboto", 24, "bold")).pack(pady=20)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        self.add_field(0, "URL del Stream:", self.url_var)
        self.add_field(1, "Nombre del Archivo:", self.nombre_var)
        self.add_field(2, "KID (DRM):", self.kid_var)
        self.add_field(3, "KEY (DRM):", self.key_var)

        ctk.CTkButton(self.form_frame, text="📁 Carpeta de Destino", command=self.select_folder).grid(row=4, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.form_frame, textvariable=self.save_path, font=("Arial", 10), wraplength=400).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # --- Frame de Botones de Control ---
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10)

        self.btn_start = ctk.CTkButton(self.btn_frame, text="🔴 INICIAR GRABACIÓN", fg_color="#28a745", command=self.start_recording)
        self.btn_start.grid(row=0, column=0, padx=5)

        self.btn_preview = ctk.CTkButton(self.btn_frame, text="📺 VER PREVIA", fg_color="#17a2b8", command=self.open_preview)
        self.btn_preview.grid(row=0, column=1, padx=5)

        self.btn_stop = ctk.CTkButton(self.btn_frame, text="⬛ PARAR", fg_color="#dc3545", command=self.stop_recording, state="disabled")
        self.btn_stop.grid(row=0, column=2, padx=5)

        self.btn_save_cfg = ctk.CTkButton(self.btn_frame, text="💾 GUARDAR PRESET", command=self.save_presets)
        self.btn_save_cfg.grid(row=0, column=3, padx=5)

        # --- Sección Presets ---
        self.preset_frame = ctk.CTkFrame(self)
        self.preset_frame.pack(pady=10, padx=20, fill="x")
        
        self.preset_combo = ctk.CTkComboBox(self.preset_frame, variable=self.selected_preset_var, values=[], width=300)
        self.preset_combo.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(self.preset_frame, text="Cargar", width=80, command=self.load_selected_preset).grid(row=0, column=1, padx=5)
        ctk.CTkButton(self.preset_frame, text="Eliminar", width=80, fg_color="#bd2130", command=self.delete_selected_preset).grid(row=0, column=2, padx=5)

        self.textbox = ctk.CTkTextbox(self, height=200, font=("Consolas", 12))
        self.textbox.pack(pady=10, padx=20, fill="both", expand=True)

    def add_field(self, row, label, var):
        ctk.CTkLabel(self.form_frame, text=label).grid(row=row, column=0, padx=10, pady=5, sticky="w")
        ctk.CTkEntry(self.form_frame, textvariable=var, width=500).grid(row=row, column=1, padx=10, pady=5)

    def select_folder(self):
        path = filedialog.askdirectory()
        if path: self.save_path.set(path)

    def open_preview(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Carga una URL primero")
            return
        
        # ffplay es ideal para ver streams en tiempo real
        # -alwaysontop: mantiene la ventana visible
        # -window_title: pone nombre a la ventana
        # -noborder: visualización más moderna
        preview_cmd = [
            "ffplay", "-i", url,
            "-window_title", "VISTA PREVIA EN VIVO",
            "-alwaysontop", "-noborder",
            "-x", "640", "-y", "360", # Tamaño de ventana inicial
            "-loglevel", "quiet"
        ]

        def launch_ffplay():
            try:
                self.preview_process = subprocess.Popen(preview_cmd)
                self.textbox.insert("end", ">>> Ventana de visualización abierta.\n")
            except FileNotFoundError:
                messagebox.showerror("Error", "No se encontró 'ffplay'. Asegúrate de tener FFmpeg instalado y en el PATH.")

        threading.Thread(target=launch_ffplay, daemon=True).start()

    def start_recording(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "La URL es obligatoria")
            return

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        custom_name = self.nombre_var.get().strip().replace(" ", "_")
        final_name = f"{custom_name}_{timestamp}" if custom_name else f"Grabacion_{timestamp}"
        self.current_name = final_name
        
        command = [
            "N_m3u8DL-RE.exe",
            f"{url}",
            "--save-name", f"{final_name}",
            "--save-dir", f"{self.save_path.get()}",
            "--auto-select",
            "--live-pipe-mux"
        ]
        
        kid = self.kid_var.get().strip()
        key = self.key_var.get().strip()
        if kid and key:
            command.extend(["--key", f"{kid}:{key}"])

        self.btn_start.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.textbox.insert("end", f">>> Grabando: {final_name}\n")

        self.thread = threading.Thread(target=self.run_process, args=(command,), daemon=True)
        self.thread.start()

    def run_process(self, command):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        for line in self.process.stdout:
            self.textbox.insert("end", line)
            self.textbox.see("end")
        self.process.wait()
        self.after(0, self._on_process_end)

    def _on_process_end(self):
        self.btn_start.configure(state="normal")
        self.btn_stop.configure(state="disabled")
        self.process = None
        self.textbox.insert("end", "\n[GRABACIÓN FINALIZADA]\n")

    def stop_recording(self):
        # Detener grabación
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True): child.kill()
                parent.kill()
            except: pass
        
        # Detener previa si sigue abierta
        if self.preview_process:
            try: self.preview_process.terminate()
            except: pass

        self.textbox.insert("end", "\nDeteniendo todo...\n")
        self.after(2000, self.cleanup_folders)

    def cleanup_folders(self):
        temp_folder = os.path.join(self.save_path.get(), self.current_name)
        if os.path.exists(temp_folder):
            try: shutil.rmtree(temp_folder)
            except: pass

    def save_presets(self):
        nombre = self.nombre_var.get().strip()
        if not nombre:
            messagebox.showerror("Error", "Usa el campo 'Nombre del Archivo' para nombrar el preset.")
            return
        new_preset = {
            "nombre": nombre, "url": self.url_var.get().strip(),
            "kid": self.kid_var.get().strip(), "key": self.key_var.get().strip(),
            "path": self.save_path.get()
        }
        self.presets = [p for p in self.presets if p['nombre'] != nombre]
        self.presets.append(new_preset)
        with open("presets.json", "w") as f: json.dump(self.presets, f, indent=4)
        self.update_combo()
        messagebox.showinfo("Guardado", f"Preset '{nombre}' guardado.")

    def load_selected_preset(self):
        nombre = self.selected_preset_var.get()
        p = next((x for x in self.presets if x['nombre'] == nombre), None)
        if p:
            self.url_var.set(p['url']); self.nombre_var.set(p['nombre'])
            self.kid_var.set(p['kid']); self.key_var.set(p['key'])
            self.save_path.set(p['path'])

    def delete_selected_preset(self):
        nombre = self.selected_preset_var.get()
        if not nombre: return
        self.presets = [p for p in self.presets if p['nombre'] != nombre]
        with open("presets.json", "w") as f: json.dump(self.presets, f, indent=4)
        self.update_combo(); self.selected_preset_var.set("")

    def load_presets(self):
        if os.path.exists("presets.json"):
            try:
                with open("presets.json", "r") as f:
                    self.presets = json.load(f)
                    self.update_combo()
            except: self.presets = []

    def update_combo(self):
        nombres = [p['nombre'] for p in self.presets]
        self.preset_combo.configure(values=nombres)

if __name__ == "__main__":
    app = RecorderApp()
    app.mainloop()