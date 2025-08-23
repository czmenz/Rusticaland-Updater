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

- 📑 **Manifest** – JSON file containing versions, files, and hashes.  
- 📦 **Update packages** – compressed archives with updated game files.  

All communication is done via **HTTPS** for safe and secure transfer. 🔐  

---

## 📥 Installation & Usage

1. Download the latest release from [Releases](https://github.com/your_repo/releases).  
2. Place `Rusticaland_Updater.exe` into any folder.  
3. Run the program – if Rust folder is not found, you will be asked to select it.  
4. The updater will check your version, download required files, extract, and install automatically.  

---

## ⚡ Example Log

```bash
[!] Please Select your Rust Folder
[*] Established connection with the server.
[*] Downloaded update data

[*] Current Version: 2593 (Hardcore Refresh V2)
[*] New Version: 2594 (Hardcore Refresh V3)

[*] Do you wish to download and install the new version(s)? (Y/N) Y
[*] Downloading Version: 2594...
[*] Extracting update...
[*] Applying update...
[*] Version applied successfully
[*] Cleanup completed
[*] Successfully updated
Press Enter to exit...
