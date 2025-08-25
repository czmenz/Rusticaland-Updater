# 📦 Rusticaland Updater (Alpha)
> [!WARNING]
> ⚠️ **Alpha Notice**
> This updater is currently in **Alpha version**. 
> It has **no GUI** and runs entirely in the **terminal/console**.
> For now, it is intended for **testing purposes only**.
---

## 🚀 Features

- 🔄 **Automatic version detection** – compares your current version with the latest available in the manifest.  
- ⬇️ **Update download** – fetches the required files directly from Rusticaland servers.  
- 📂 **File extraction** – unpacks updates into the correct Rust game folder.  
- 🔒 **Integrity check** – verifies file hashes to ensure update correctness.  
- 💾 **Disk space check** – calculates required space for compressed and uncompressed update files.  
- 🧹 **Auto cleanup** – removes temporary files after the update is complete.  
- 🖥️ **Stylish logging** – color-coded logs (✅ success, ⚠️ warning, ❌ error).  

---

## 🌍 Connections

The updater connects only to official **Rusticaland update servers** for:  

- 📑 **Manifest** – JSON file containing all data about the versions.
- 📦 **Update packages** – compressed archives with updated game files.  

All communication is done via **HTTPS** for safe and secure transfer. 🔐  

---

## 📥 Installation & Usage

1. Download the latest release from [Releases](https://github.com/Rusticaland-Updater/releases).  
2. Place `Rusticaland_Updater.exe` into any folder.  
3. Run the program – you will be asked to select folder of your cracked rust
4. The updater will check your version, download required files, extract, install automatically and clean up after himself.

---

## ⚡ Example Log

```bash
[!] Please Select your Rust Folder
[*] Established connection with the server.
[*] Downloaded update data

[*] Current Version: 2594.3 (Hardcore Refresh V3)
[*] New Version: 2594.4 (Hardcore Refresh V4)

[*] Do you wish to download and install the new version(s)? (Y/N) Y
[*] Downloading Version: 2594.4...
[*] Extracting update...
[*] Applying update...
[*] Version 2594.4 applied successfully
[*] Cleanup completed
[*] Successfully updated
Press Enter to exit...
