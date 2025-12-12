## Dolgok ami kellenek a python enviormenthez:
- pyserial
- pyautogui vagy keyboard

## Hogyan aktiváljuk a python enviormentet:

1. Beírjuk a terminálba ezt:
   ```powershell
   python -m venv venv
   ```

2. Utána ezt :
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. Ha erre hibát dob ki akkor a powershell buziskodik
   - a megoldásához ezt kell írni:  
   ```powershell
   Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process -Force
   ```

4. Ezek után beírjuk a kettesben lévő parancsot és akkor ilyennek kell meg jelennie a terminálban:
   ```powershell
   (venv) PS C:\Users\Agero\Documents\gitcucc\mindegy_nekem-1>
   ```

5. Ha a hármas lépés sikerült akkor már csak a lib-eket kell letölteni
   - Letöltés módja pedig: 
      ```powershell
      pip install <lib_név>
      
      
      
# Szükséges importok és telepítendő csomag az UI CALCULATORHOZ

Ez a program a következő Python modulokat használja:

# 🐍 Beépített:

    import math
    import cmath
    import threading
    import time
    import sys

## 📦 Telepítendő külső csomag:

    pip install PySide6 pyserial

### Magyarázat

-   **PySide6**  -- A grafikus felhasználói felület (UI) működéséhez.
-   **pyserial** -- A soros port kezeléséhez (COM port olvasása
    gombnyomásokhoz).

## 📁 Rendszerkövetelmények

-   Python **3.9 vagy újabb**