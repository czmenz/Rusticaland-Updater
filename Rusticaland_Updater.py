import os
import sys
import json
import shutil
import requests
import tempfile
import zstandard as zstd
import tkinter as tk
from tkinter import filedialog, messagebox, Tk
from colorama import init, Fore, Style
from tqdm import tqdm
import ctypes
import zstandard as zstd
import time
import subprocess
import stat

init(autoreset=True)

SERVER_URL = "http://89.203.249.22:3232"
CONFIG_FILE = "config.json"

CURRENT_VERSION = "1.0.3"
CURRENT_TYPE = "Alpha"



ctypes.windll.kernel32.SetConsoleTitleW("Rusticaland Updater - Alpha 1.0.3")

try:
    r = requests.get(SERVER_URL + "/version.manifest", timeout=5)
    r.raise_for_status()
    remote_manifest = r.json()
except Exception as e:
    root = Tk()
    root.withdraw()
    messagebox.showerror("Error", f"Failed to download version manifest")
    sys.exit(1)

remote_version = remote_manifest.get("verze")
remote_type = remote_manifest.get("typ")

# --- Porovnání verze ---
if remote_version != CURRENT_VERSION or remote_type != CURRENT_TYPE:
    root = Tk()
    root.withdraw()
    messagebox.showerror(
        "Version Mismatch",
        f"Please Redownload the latest Updater from website or Discord"
    )
    sys.exit(1)


def log_success(msg):
    print(Fore.GREEN + "[*] " + msg)

def log_error(msg):
    print(Fore.RED + "[-] " + msg)

def log_warn(msg):
    print(Fore.YELLOW + "[!] " + msg)

def get_app_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_config_path():
    return os.path.join(get_app_path(), CONFIG_FILE)

def get_real_user():
    """Get the real user who launched the program, even if running as admin"""
    try:
        # Try to get the original user from environment
        original_user = os.environ.get('USERNAME')
        if original_user and original_user != 'SYSTEM':
            return original_user
    except:
        pass
    
    # Fallback to current user
    try:
        import getpass
        return getpass.getuser()
    except:
        return None

def preserve_ownership_copy(src_file, dst_file):
    """Copy file while preserving original ownership and permissions"""
    try:
        # First, copy the file normally
        shutil.copy2(src_file, dst_file)
        
        # If we're running as admin, we need to fix ownership
        if ctypes.windll.shell32.IsUserAnAdmin():
            real_user = get_real_user()
            if real_user:
                try:
                    # Use icacls to set proper ownership and permissions
                    # Grant full control to the real user
                    subprocess.run([
                        'icacls', dst_file, 
                        '/grant', f'{real_user}:F',
                        '/T', '/Q'
                    ], check=False, capture_output=True)
                    
                    # Remove any inherited permissions that might cause issues
                    subprocess.run([
                        'icacls', dst_file,
                        '/inheritance:e',
                        '/Q'
                    ], check=False, capture_output=True)
                    
                except Exception as e:
                    log_warn(f"Could not fix ownership for {dst_file}: {e}")
        
        return True
    except Exception as e:
        log_error(f"Failed to copy and fix ownership for {os.path.basename(dst_file)}: {e}")
        return False

def preserve_ownership_mkdir(directory):
    """Create directory with proper ownership"""
    try:
        os.makedirs(directory, exist_ok=True)
        
        # Fix ownership if running as admin
        if ctypes.windll.shell32.IsUserAnAdmin():
            real_user = get_real_user()
            if real_user:
                try:
                    subprocess.run([
                        'icacls', directory,
                        '/grant', f'{real_user}:F',
                        '/T', '/Q'
                    ], check=False, capture_output=True)
                    
                    subprocess.run([
                        'icacls', directory,
                        '/inheritance:e',
                        '/Q'
                    ], check=False, capture_output=True)
                    
                except Exception as e:
                    log_warn(f"Could not fix directory ownership for {directory}: {e}")
        
        return True
    except Exception as e:
        log_error(f"Failed to create directory {directory}: {e}")
        return False

def load_or_select_rust_folder():
    config_path = get_config_path()

    # Zkus načíst existující config
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                cfg = json.load(f)
                rust_folder = cfg.get("rust_folder")
                if rust_folder and os.path.exists(rust_folder):
                    return rust_folder
        except Exception as e:
            log_warn(f"Failed to load config: {e}")

    # Pokud neexistuje nebo selhal, požádat uživatele o složku
    log_warn("Please Select your Rust Folder")
    try:
        root = tk.Tk()
        root.withdraw()
        rust_folder = filedialog.askdirectory(title="Select Rust Folder")
        root.destroy()
        if not rust_folder:
            log_error("No folder selected. Exiting quietly.")
            sys.exit(0)  # Tiše ukončit exe
    except Exception as e:
        log_error(f"Folder selection failed: {e}")
        sys.exit(0)

    # Kontrola základních souborů
    if not os.path.exists(os.path.join(rust_folder, "RustClient.exe")) or \
       not os.path.exists(os.path.join(rust_folder, "Bundles")):
        log_error("Invalid Rust folder (RustClient.exe or Bundles missing). Exiting.")
        sys.exit(0)

    # Uložit config
    try:
        with open(config_path, "w") as f:
            json.dump({"rust_folder": rust_folder}, f, indent=4)
    except Exception as e:
        log_warn(f"Failed to save config: {e}")

    return rust_folder

def ping_server():
    try:
        r = requests.get(SERVER_URL, timeout=5)
        if r.status_code == 200:
            log_success("Established connection with the server.")
            return True
    except Exception:
        pass
    log_error("Failed to reach the server.")
    return False

def download_manifest(temp_dir):
    try:
        r = requests.get(f"{SERVER_URL}/manifest.json")
        if r.status_code == 200:
            manifest_path = os.path.join(temp_dir, "manifest.json")
            with open(manifest_path, "wb") as f:
                f.write(r.content)
            log_success("Downloaded update data")
            return r.json()
    except Exception:
        pass
    log_error("Failed to download update data")
    input("Press Enter to exit...")
    sys.exit(1)


def get_free_space_bytes(path):
    """Vrátí volné místo na disku v bajtech."""
    total, used, free = shutil.disk_usage(path)
    return free

def check_space_for_update(rust_folder, compressed_size, uncompressed_size):
    """Kontroluje volné místo na disku pro kompresovaný a dekompresovaný update"""
    stat = shutil.disk_usage(rust_folder)
    free_bytes = stat.free

    if free_bytes < uncompressed_size:
        print("")
        log_error(f"Not enough disk space for uncompressed update. Required: {uncompressed_size / (1024**3):.2f} GB, Free: {free_bytes / (1024**3):.2f} GB")
        print("")
        return False

    if free_bytes < compressed_size:
        print("")
        log_warn(f"Warning: not enough disk space for compressed file. Required: {compressed_size / (1024**3):.2f} GB, Free: {free_bytes / (1024**3):.2f} GB")
        print("")
    
    # Pokud je místa dost, vypíše info
    print("")
    log_success(f"Download Size: {compressed_size / (1024**2):.2f} MB")
    log_success(f"Installing: {uncompressed_size / (1024**3):.2f} GB")
    print("")
    
    return True













def hash_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(8192):
            h.update(chunk)
    return h.hexdigest()

def get_current_version(rust_folder, manifest):
    for version in reversed(manifest.get("versions", [])):
        match_all = True
        for file_info in version["files"]:
            path = os.path.join(rust_folder, file_info["name"])
            if not os.path.exists(path) or hash_file(path) != file_info["hash"]:
                match_all = False
                break
        if match_all:
            return version
    return None




def download_and_extract_update(rust_folder, version_number, temp_dir, manifest):
    zst_url = f"{SERVER_URL}/{version_number}.zst"
    local_zst = os.path.join(temp_dir, f"{version_number}.zst")

    log_success(f"Downloading Version: {version_number}...")
    r = requests.get(zst_url, stream=True)
    if r.status_code != 200:
        log_error(f"Failed to download Version: {version_number}")
        return False

    total_size = int(r.headers.get('content-length', 0))

    # najít odpovídající verzi podle čísla verze
    ver = next((v for v in manifest["versions"] if v["version"] == version_number), None)
    if ver is None:
        log_error(f"Version {version_number} not found in manifest")
        return False

    compressed_size = int(r.headers.get('content-length', 0))
    uncompressed_size = ver.get("update-size", compressed_size * 3)  # fallback

    if not check_space_for_update(rust_folder, compressed_size, uncompressed_size):
        log_error("Update aborted due to insufficient disk space.")
        return False


    chunk_size = 1024*1024
    with open(local_zst, "wb") as f, tqdm(
        total=total_size, unit='B', unit_scale=True, desc=f"{version_number}.zst", ncols=80
    ) as pbar:
        for chunk in r.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(len(chunk))

    # --- extrahovat do temp složky ---
    extract_temp = os.path.join(temp_dir, f"extract_{version_number}")
    os.makedirs(extract_temp, exist_ok=True)
    log_success("Extracting update...")

    dctx = zstd.ZstdDecompressor()
    with open(local_zst, "rb") as compressed:
        with dctx.stream_reader(compressed) as reader:
            while True:
                name_len_bytes = reader.read(4)
                if not name_len_bytes or len(name_len_bytes) < 4:
                    break
                name_len = int.from_bytes(name_len_bytes, "little")

                name_bytes = reader.read(name_len)
                file_rel_path = name_bytes.decode("utf-8")
                file_path = os.path.join(extract_temp, file_rel_path)
                os.makedirs(os.path.dirname(file_path), exist_ok=True)

                data_len_bytes = reader.read(8)
                data_len = int.from_bytes(data_len_bytes, "little")

                with open(file_path, "wb") as f:
                    remaining = data_len
                    chunk_size2 = 1024*1024
                    while remaining > 0:
                        to_read = min(remaining, chunk_size2)
                        chunk = reader.read(to_read)
                        if not chunk:
                            raise EOFError("Unexpected end of stream")
                        f.write(chunk)
                        remaining -= len(chunk)

    # --- přesunout všechny soubory do rust_folder s preservation of ownership ---
    log_success("Applying update...")
    for root_dir, dirs, files in os.walk(extract_temp):
        rel_path = os.path.relpath(root_dir, extract_temp)
        target_dir = os.path.join(rust_folder, rel_path)
        
        # Create directory with proper ownership
        if not preserve_ownership_mkdir(target_dir):
            log_error(f"Failed to create directory: {target_dir}")
            continue

        for file in files:
            src_file = os.path.join(root_dir, file)
            dst_file = os.path.join(target_dir, file)

            # pokud soubor existuje, smaž ho
            if os.path.exists(dst_file):
                try:
                    os.remove(dst_file)
                except Exception as e:
                    log_warn(f"Could not remove existing file {dst_file}: {e}")

            # Copy file with proper ownership preservation
            if not preserve_ownership_copy(src_file, dst_file):
                log_error(f"Failed to apply file: {file}")

    # nakonec můžeš smazat temp složku
    shutil.rmtree(extract_temp)
    os.remove(local_zst)

    log_success(f"Version {version_number} applied successfully")
    return True


def main():    
    rust_folder = load_or_select_rust_folder()

    if not ping_server():
        input("Press Enter to exit...")
        sys.exit(1)

    temp_dir = tempfile.mkdtemp()
    manifest = download_manifest(temp_dir)

    current_version = get_current_version(rust_folder, manifest)
    current_index = 0
    if current_version:
        for i, v in enumerate(manifest["versions"]):
            if v["version"] == current_version["version"]:
                current_index = i
                break

    latest_index = len(manifest["versions"]) - 1

    current_str = f"{current_version['version']} ({current_version['name']})" if current_version else "Unknown"
    latest_version = manifest["versions"][latest_index]
    latest_str = f"{latest_version['version']} ({latest_version['name']})" if latest_version else "Unknown"

    print("")
    print(f"[*] Current Version: {current_str}")
    log_success(f"New Version: {latest_str}")
    print("")

    if current_index == latest_index:
        print("You already have the latest version.")
        shutil.rmtree(temp_dir)
        input("Press Enter to exit...")
        sys.exit(1)
        return

    choice = input("[*] Do you wish to download and install the new version(s)? (Y/N) ").strip().lower()
    if choice != "y":
        log_warn("Update cancelled by user.")
        shutil.rmtree(temp_dir)
        return

    # postupně stahovat a aplikovat všechny verze mezi current_index+1 a latest_index
    for i in range(current_index + 1, latest_index + 1):
        version_number = manifest["versions"][i]["version"]
        success = download_and_extract_update(rust_folder, version_number, temp_dir, manifest)
        if not success:
            log_error(f"Failed to apply version {version_number}")
            break
    
    time.sleep(5)
    shutil.rmtree(temp_dir)

    log_success("Cleanup completed")
    log_success("Successfully updated")
    
    input("Press Enter to exit...")
    sys.exit(1)

if __name__ == "__main__":
    main()
