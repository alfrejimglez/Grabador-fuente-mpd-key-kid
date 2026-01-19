import customtkinter as ctk
import subprocess
import threading
import os
import json
import shutil
from datetime import datetime
from tkinter import filedialog, messagebox
import psutil
import glob

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class RecorderApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Grabador M3U8/MPD con Vista Previa")
        self.geometry("800x650")
        self.process = None
        self.preview_process = None 

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
        ctk.CTkLabel(self, text="Grabador MPD Y M3U8", font=("Roboto", 24, "bold")).pack(pady=20)

        self.form_frame = ctk.CTkFrame(self)
        self.form_frame.pack(pady=10, padx=20, fill="x")

        self.add_field(0, "URL del Stream:", self.url_var)
        self.add_field(1, "Nombre del Archivo:", self.nombre_var)
        self.add_field(2, "KID (DRM):", self.kid_var)
        self.add_field(3, "KEY (DRM):", self.key_var)

        ctk.CTkButton(self.form_frame, text="📁 Carpeta de Destino", command=self.select_folder).grid(row=4, column=0, padx=10, pady=10)
        ctk.CTkLabel(self.form_frame, textvariable=self.save_path, font=("Arial", 10), wraplength=400).grid(row=4, column=1, padx=10, pady=10, sticky="w")

        # --- Botones ---
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

        # --- Presets ---
        self.preset_frame = ctk.CTkFrame(self)
        self.preset_frame.pack(pady=10, padx=20, fill="x")
        
        self.preset_combo = ctk.CTkComboBox(self.preset_frame, variable=self.selected_preset_var, values=[], width=300)
        self.preset_combo.grid(row=0, column=0, padx=10, pady=10)
        ctk.CTkButton(self.preset_frame, text="Cargar", width=80, command=self.load_selected_preset).grid(row=0, column=1, padx=5)
        ctk.CTkButton(self.preset_frame, text="Eliminar", width=80, fg_color="#bd2130", command=self.delete_selected_preset).grid(row=0, column=2, padx=5)
        ctk.CTkButton(self.preset_frame, text="Limpiar Consola", width=100, command=self.clear_console).grid(row=0, column=3, padx=5)

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
        key = self.key_var.get().strip()
        kid = self.kid_var.get().strip()  # Necesitamos KID y KEY para DRM
        
        if not url:
            messagebox.showerror("Error", "Carga una URL primero")
            return

        # (sin DRM) el resto m3u8 o ts
        is_m3u8_or_ts = url.endswith('.m3u8') or url.endswith('.ts')
        
        if not key and not is_m3u8_or_ts:
            messagebox.showerror("Error", "Se requiere KEY para desencriptar, o la URL debe ser .m3u8/.ts sin DRM.")
            return

        #  DRM mpd
        use_mpv = False
        player_exe = "ffmpeg"
        
        if key:
            preview_cmd = f"{player_exe} -cenc_decryption_key {key} -i \"{url}\" -map 0:v:0 -map 0:a:0 -c copy -f mpegts - | ffplay -i - -window_title \"VISTA PREVIA\" -alwaysontop -x 640 -y 360"
        else:
            preview_cmd = f"ffplay \"{url}\" -window_title \"VISTA PREVIA\" -alwaysontop -x 640 -y 360"

        def launch_player():
            try:
                if key:
                    self.textbox.insert("end", f">>> Iniciando Previa con DRM: FFmpeg + FFplay...\n")
                else:
                    self.textbox.insert("end", f">>> Iniciando Previa sin DRM: FFplay...\n")
                
                self.textbox.insert("end", f"Comando: {preview_cmd}\n")
                
                self.preview_process = subprocess.Popen(preview_cmd, shell=True, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                
                for line in self.preview_process.stderr:
                    self.textbox.insert("end", f"[FFPLAY] {line}")
                    self.textbox.see("end")
                
            except FileNotFoundError:
                messagebox.showerror("Error", f"No se encontró ffmpeg o ffplay. Instala FFmpeg.")

        threading.Thread(target=launch_player, daemon=True).start()

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
            "--drop-audio", ".*[Dd]escripcion.*",
            "--drop-subtitle", ".*",
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
        
        # Delete SRT files
        srt_files = glob.glob(os.path.join(self.save_path.get(), "*.srt"))
        for srt in srt_files:
            try:
                os.remove(srt)
                self.textbox.insert("end", f"Eliminado: {os.path.basename(srt)}\n")
            except:
                pass

        # convierto a ts-mp4 y luego borro  ts
        ts_file = os.path.join(self.save_path.get(), f"{self.current_name}.ts")
        mp4_file = os.path.join(self.save_path.get(), f"{self.current_name}.mp4")
        if os.path.exists(ts_file):
            convert_cmd = ["ffmpeg", "-i", ts_file, "-c", "copy", mp4_file]
            try:
                subprocess.run(convert_cmd, check=True, creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
                self.textbox.insert("end", f"Convertido a MP4: {os.path.basename(mp4_file)}\n")
                try:
                    os.remove(ts_file)
                    self.textbox.insert("end", f"Eliminado TS: {os.path.basename(ts_file)}\n")
                except:
                    self.textbox.insert("end", "Error al eliminar TS\n")
            except subprocess.CalledProcessError:
                self.textbox.insert("end", "Error al convertir a MP4\n")

    def stop_recording(self):
        if self.process:
            try:
                parent = psutil.Process(self.process.pid)
                for child in parent.children(recursive=True): child.kill()
                parent.kill()
            except: pass
        
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

    def clear_console(self):
        self.textbox.delete("1.0", "end")

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