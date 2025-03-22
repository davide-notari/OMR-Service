import os
import time
import zipfile
import shutil
import subprocess
import psutil
import stat
import ctypes
import sys


APP_NAME = "OMRService.exe"
UPDATE_FILE = "OMRService.zip"
UPDATE_FOLDER = "temp_update"

def close_app():
    print(f"Chiudendo {APP_NAME}...")
    os.system(f"taskkill /f /im {APP_NAME} >nul 2>&1")

    for _ in range(10):
        if not any(proc.name() == APP_NAME for proc in psutil.process_iter()):
            print(f"{APP_NAME} chiuso con successo.")
            return
        time.sleep(1)



def force_delete_readonly(path):
    os.chmod(path, stat.S_IWRITE)
    try:
        os.remove(path)
    except IsADirectoryError:
        shutil.rmtree(path, onexc=force_delete_readonly)
    

def extract_update():
    print("Estrazione dei file...")
    with zipfile.ZipFile(UPDATE_FILE, "r") as zip_ref:
        zip_ref.extractall(UPDATE_FOLDER)
    print("File estratti")


def replace_files():
    for file_name in os.listdir(UPDATE_FOLDER):
        src = os.path.join(UPDATE_FOLDER, file_name)
        dest = os.path.join(os.getcwd(), file_name)

        if os.path.exists(dest):
            try:
                os.remove(dest)
            except PermissionError:
                print(f"Permessi negati per {dest}")
                os.chmod(dest, stat.S_IWRITE)
                os.remove(dest)

        shutil.move(src, dest)

    print("Aggiornamento completato!")


def launch_app():
    print("Avvio dell'applicazione aggiornata...")
    subprocess.Popen([APP_NAME], creationflags=subprocess.CREATE_NO_WINDOW)


def run_as_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Richiesta di permessi di amministratore...")
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()


def main():
    run_as_admin()
    close_app()
    time.sleep(2)

    extract_update()
    replace_files()

    os.remove(UPDATE_FILE)
    shutil.rmtree(UPDATE_FOLDER, onexc=force_delete_readonly)

    launch_app()

if __name__ == "__main__":
    main()