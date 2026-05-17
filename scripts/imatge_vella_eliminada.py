import os
import time

CARPETA = "/home/safefall/safefall/flask/static/imatges/"
INTERVAL = 90 #segons

def eliminar_imatge():
        try:
                files = [os.path.join(CARPETA, f) for f in os.listdir(CARPETA)]
                if not files:
                        print("No hi ha imatges")
                        return

                files.sort(key=os.path.getctime)
                oldest = files[0]

                os.remove(oldest)
                print(f"Imatge més vella eliminada {oldest}")
        except Exception as e:
                print(f"Error al eliminar el fitxer {e}")

def main():
        print("Script de nateja iniciat")
        while True:
                eliminar_imatge()
                time.sleep(INTERVAL)

if __name__ == "__main__":
        main()
