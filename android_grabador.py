import subprocess
import threading
import os
import json
import shutil
from datetime import datetime
import psutil

class RecorderApp:
    def __init__(self):
        self.process = None
        self.presets = []
        self.load_presets()

    def run(self):
        while True:
            print("\n=== Grabador Fuente MPD - KEY:KID ===")
            print("1. Iniciar Grabación")
            print("2. Parar Grabación")
            print("3. Guardar Preset")
            print("4. Cargar Preset")
            print("5. Eliminar Preset")
            print("6. Salir")
            choice = input("Elige una opción: ").strip()

            if choice == '1':
                self.start_recording()
            elif choice == '2':
                self.stop_recording()
            elif choice == '3':
                self.save_presets()
            elif choice == '4':
                self.load_selected_preset()
            elif choice == '5':
                self.delete_selected_preset()
            elif choice == '6':
                break
            else:
                print("Opción inválida.")

    def start_recording(self):
        url = input("URL del MPD: ").strip()
        if not url:
            print("Falta la URL")
            return

        kid = input("KID (opcional): ").strip()
        key = input("KEY (opcional): ").strip()
        save_path = input("Carpeta de guardado (default current): ").strip() or os.getcwd()

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name = f"Grabacion_{timestamp}"
        self.current_name = name

        command = ["N_m3u8DL-RE", url, "--save-name", name, "--save-dir", save_path, "--auto-select", "--live-pipe-mux"]
        if kid and key:
            command.extend(["--key", f"{kid}:{key}"])

        print(f"Iniciando grabación: {name}")
        self.thread = threading.Thread(target=self.run_process, args=(command,), daemon=True)
        self.thread.start()

    def run_process(self, command):
        self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in self.process.stdout:
            print(line, end='')
        self.process.wait()
        print("\n--- GRABACIÓN FINALIZADA ---")

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
            if hasattr(self, 'current_name'):
                folder_path = os.path.join(os.getcwd(), self.current_name)  # Ajustar path
                if os.path.exists(folder_path):
                    shutil.rmtree(folder_path)
            print("Grabación parada y carpeta borrada.")
        else:
            print("No hay grabación en curso.")

    def save_presets(self):
        nombre = input("Nombre del preset: ").strip()
        if not nombre:
            print("Ingresa un nombre.")
            return
        url = input("URL: ").strip()
        kid = input("KID: ").strip()
        key = input("KEY: ").strip()
        path = input("Path: ").strip() or os.getcwd()

        existing = next((p for p in self.presets if p.get('nombre') == nombre), None)
        if existing:
            existing.update({"url": url, "kid": kid, "key": key, "path": path})
        else:
            self.presets.append({"nombre": nombre, "url": url, "kid": kid, "key": key, "path": path})
        with open("presets.json", "w") as f:
            json.dump(self.presets, f)
        print("Preset guardado.")

    def load_selected_preset(self):
        if not self.presets:
            print("No hay presets.")
            return
        print("Presets disponibles:")
        for i, p in enumerate(self.presets):
            print(f"{i+1}. {p.get('nombre')}")
        try:
            idx = int(input("Elige número: ")) - 1
            preset = self.presets[idx]
            print(f"Cargado: {preset}")
        except:
            print("Inválido.")

    def delete_selected_preset(self):
        if not self.presets:
            print("No hay presets.")
            return
        print("Presets disponibles:")
        for i, p in enumerate(self.presets):
            print(f"{i+1}. {p.get('nombre')}")
        try:
            idx = int(input("Elige número para eliminar: ")) - 1
            nombre = self.presets[idx]['nombre']
            del self.presets[idx]
            with open("presets.json", "w") as f:
                json.dump(self.presets, f)
            print(f"Preset '{nombre}' eliminado.")
        except:
            print("Inválido.")

    def load_presets(self):
        if os.path.exists("presets.json"):
            with open("presets.json", "r") as f:
                data = json.load(f)
                if isinstance(data, list):
                    self.presets = data
                elif isinstance(data, dict):
                    self.presets = [data]
                else:
                    self.presets = []
        else:
            self.presets = []

if __name__ == "__main__":
    app = RecorderApp()
    app.run()