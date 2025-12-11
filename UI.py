from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit,
    QVBoxLayout, QLabel, QTabWidget
)
import sys
import cmath
import re
import serial
import threading
import time


class SciCalculator(QWidget):
    def __init__(self):
        super().__init__()

        # flag: ha True, a következő gombnyomás törli az előző eredményt
        self.clear_on_next = False

        self.setWindowTitle("Komplex Tudományos Számológép – PySide6")
        self.setFixedSize(420, 550)

        self.angle_mode = "deg"  # deg / rad / grad

        # Komplex egység i := sqrt(-1)
        self.i = cmath.sqrt(-1)

        # --- KIjelző ---
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 26px; padding: 15px;")
        self.display.setText("")

        # --- Szög mód címke ---
        self.angle_label = QLabel("Szög mód: fok")
        self.angle_label.setStyleSheet("font-size: 16px; padding: 6px;")

        # --- Tabs ---
        self.tabs = QTabWidget()
        self.tabs.addTab(self.basic_tab(), "Alap")
        self.tabs.addTab(self.science_tab(), "Tudományos")
        self.tabs.addTab(self.complex_tab(), "Komplex")

        # --- Fő layout ---
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.display)
        main_layout.addWidget(self.angle_label)
        main_layout.addWidget(self.tabs)

        self.setLayout(main_layout)

        # ============================
        # SERIAL PORT MEGNYITÁSA
        # ============================
        try:
            self.ser = serial.Serial("COM3", 9600, timeout=0.1)  # Állítsd át szükség szerint!
            self.serial_thread = threading.Thread(target=self.read_serial, daemon=True)
            self.serial_thread.start()
        except:
            print("Nem sikerült megnyitni a COM portot!")
            self.ser = None

    # ==========================================================================
    # Tiszta logika: gombnyomás GUI-ból és SERIAL-ból is ezt hívja → biztonságos
    # ==========================================================================
    
    def process_key(self, text):

        # Ha korábbi eredmény van, a következő normál gomb törölje azt
        if self.clear_on_next and text not in ["=", "deg/rad/grad"]:
            self.display.setText("")
            self.clear_on_next = False

        if text == "=":
            self.calculate()
            return

        if text == "C":
            self.display.setText("")
            self.clear_on_next = False
            return

        if text == "i":
            self.display.setText(self.display.text() + " i ")
            return
        
        # Függvénygombok: automatikus nyitó zárójel
        if text in ["sin", "cos", "tan", "log", "ln", "sqrt", "real()", "imag()", "conj()"]:
            # Ha már van zárójel, ne add hozzá újra
            if text.endswith("()"):
                self.display.setText(self.display.text() + text)
            else:
                self.display.setText(self.display.text() + text + "(")
            return

        self.display.setText(self.display.text() + text)

    # -------------------------
    # GUI-s gombok ezt hívják
    # -------------------------
    def on_button_click(self):
        text = self.sender().text()
        self.process_key(text)

    # ==========================================================================
    # SERIAL KEZELÉSE
    # ==========================================================================
    
    def read_serial(self):
        """
        Folyamatosan olvassa a soros portot.
        Ha 1–12 közötti gomb érkezik, azt leképezzük egy UI gombra.
        """
        mapping = {
            1: "7",
            2: "8",
            3: "9",
            4: "/",
            5: "4",
            6: "5",
            7: "6",
            8: "*",
            9: "1",
            10: "2",
            11: "3",
            12: "-",    # Az utolsó 3 (13–15) ignorálva
        }

        while True:
            try:
                if self.ser is None:
                    time.sleep(0.1)
                    continue

                line = self.ser.readline().decode().strip()
                if line == "":
                    continue

                try:
                    key = int(line)
                except:
                    continue

                if key in mapping:
                    text = mapping[key]
                    self.process_key(text)

            except:
                pass

            time.sleep(0.02)

    # ==========================================================================
    # KIÉRTÉKELÉS
    # ==========================================================================
    def calculate(self):
        try:
            expr = self.display.text().strip()
            
            # Automatikusan zárjuk az nyitott zárójeleket
            open_count = expr.count("(")
            close_count = expr.count(")")
            expr += ")" * (open_count - close_count)

            # függvények átírása
            expr = expr.replace("sin", "self.sin_func")

            expr = expr.replace("cos", "self.cos_func")

            expr = expr.replace("tan", "self.tan_func")

            expr = expr.replace("log(", "cmath.log10(")

            expr = expr.replace("ln(", "cmath.log(")

            expr = expr.replace("exp(", "cmath.exp(")

            expr = expr.replace("arg", "cmath.phase")

            expr = expr.replace("sqrt", "cmath.sqrt")

            expr = expr.replace("real", "self.real_func")

            expr = expr.replace("imag", "self.imag_func")

            expr = expr.replace("conj", "self.conj_func")

            expr = expr.replace("phase", "cmath.phase")


            # " i " token → self.i
            expr = expr.replace(" i ", " self.i ")

            # 2i → 2*self.i
            expr = re.sub(r'(\d)self\.i', r'\1*self.i', expr)
            expr = re.sub(r'(\d)i', r'\1*self.i', expr)

            result = eval(expr)
            self.display.setText(str(result))
            self.clear_on_next = True

        except:
            # Nem írunk "Hiba"-t — az előzőket megtartjuk
            self.clear_on_next = True

    # ==========================================================================
    # SZÖG FÜGGVÉNYEK (deg / rad / grad)
    # ==========================================================================
    
    def angle_convert(self, x):
        x = complex(eval(str(x)))

        if self.angle_mode == "deg":
            return cmath.pi * x / 180
        elif self.angle_mode == "grad":
            return cmath.pi * x / 200
        return x  # rad

    def sin_func(self, x):
        return cmath.sin(self.angle_convert(x))

    def cos_func(self, x):
        return cmath.cos(self.angle_convert(x))

    def tan_func(self, x):
        return cmath.tan(self.angle_convert(x))

    # ==========================================================================
    # KOMPLEX SPECIÁLIS FÜGGVÉNYEK
    # ==========================================================================
    
    def real_func(self, x):
        return complex(eval(str(x))).real

    def imag_func(self, x):
        return complex(eval(str(x))).imag

    def conj_func(self, x):
        return complex(eval(str(x))).conjugate()

    # ==========================================================================
    # TAB-OK: ALAP, TUDOMÁNYOS, KOMPLEX
    # ==========================================================================
    
    def basic_tab(self):
        widget = QWidget()
        layout = QGridLayout()
        buttons = [
            ["7", "8", "9", "/"],
            ["4", "5", "6", "*"],
            ["1", "2", "3", "-"],
            ["0", ".", "=", "+"]
        ]
        for row, btn_row in enumerate(buttons):
            for col, btn_text in enumerate(btn_row):
                btn = QPushButton(btn_text)
                btn.clicked.connect(self.on_button_click)
                layout.addWidget(btn, row, col)
        widget.setLayout(layout)
        return widget
    
    def science_tab(self):
        widget = QWidget()
        layout = QGridLayout()
        buttons = [
            ["sin", "cos", "tan", "√"],
            ["log", "ln", "e^x", "π"],
            ["deg/rad/grad", "C", "←", "="]
        ]
        for row, btn_row in enumerate(buttons):
            for col, btn_text in enumerate(btn_row):
                btn = QPushButton(btn_text)
                btn.clicked.connect(self.on_button_click)
                layout.addWidget(btn, row, col)
        widget.setLayout(layout)
        return widget
    
    def complex_tab(self):
        widget = QWidget()
        layout = QGridLayout()
        buttons = [
            ["i", "real()", "imag()", "conj()"],
            ["C", "="]
        ]
        for row, btn_row in enumerate(buttons):
            for col, btn_text in enumerate(btn_row):
                btn = QPushButton(btn_text)
                btn.clicked.connect(self.on_button_click)
                layout.addWidget(btn, row, col)
        widget.setLayout(layout)
        return widget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SciCalculator()
    window.show()
    sys.exit(app.exec())
