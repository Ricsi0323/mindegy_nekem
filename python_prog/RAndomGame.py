import serial
import time
import random
import sys
import os
try:
    import msvcrt
except Exception:
    msvcrt = None
import select

# ------- Beállítások ---------
PORT = "COM3"      # <- állítsd be a te portodra!
BAUD = 9600
MAX_LIVES = 3
# ------------------------------

try:
    ser = serial.Serial(PORT, BAUD, timeout=0.1)
except Exception:
    ser = None
    print(f"[info] Nem sikerült megnyitni a soros portot ({PORT}). Mock módban futok (billentyűzet).")

score = 0
lives = MAX_LIVES

def clear():
    os.system("cls" if os.name == "nt" else "clear")

clear()
print("=== REFLEX SHOOTER ===")
print("Várakozunk az Arduino-ra...")

time.sleep(2)

while lives > 0:
    clear()
    print(f"Pontok: {score}   Életek: {lives}")

    # Véletlen várakozás
    time.sleep(random.uniform(1.5, 4))

    # Jelzés
    print("\nELLENSÉG MEGJELENT! LŐJ!\n")
    start = time.time()
    hit = False

    # Időkeret a lövéshez
    def wait_for_hit(timeout_seconds: float) -> bool:
        t0 = time.time()
        # Ha van soros eszköz, ellenőrizzük azt
        if ser:
            while time.time() - t0 < timeout_seconds:
                if ser.in_waiting:
                    data = ser.readline().decode(errors="ignore").strip()
                    if data:
                        return True
                time.sleep(0.01)
            return False
        # Ha nincs soros eszköz, használjuk a billentyűzetet (Windows: msvcrt, egyéb: select)
        else:
            if msvcrt:
                while time.time() - t0 < timeout_seconds:
                    if msvcrt.kbhit():
                        _ = msvcrt.getwch()
                        return True
                    time.sleep(0.01)
                return False
            else:
                # POSIX megoldás: select a stdin-re
                rlist, _, _ = select.select([sys.stdin], [], [], timeout_seconds)
                if rlist:
                    _ = sys.stdin.readline()
                    return True
                return False

    if wait_for_hit(2):
        hit = True

    if hit:
        reaction = time.time() - start
        print(f"Találat! Reakcióidő: {reaction:.3f} mp")
        score += 1
        time.sleep(1.2)
        if reaction < 0.5:
            print("Gyors reakció! +1 élet")
            lives += 1
            time.sleep(1.5)
        else:
            time.sleep(1.5)
            print("Lassu vagy bazeg!")
    else:
        print("Lekésted! -1 élet")
        lives -= 1
        time.sleep(1.5)

clear()
print("=== GAME OVER ===")
print(f"Végső pontszám: {score}")

