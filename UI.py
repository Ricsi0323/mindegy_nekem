from PySide6.QtWidgets import (
    QApplication, QWidget, QGridLayout, QPushButton, QLineEdit,
    QVBoxLayout, QLabel, QTabWidget
)
from PySide6.QtCore import QThread, Signal
import sys
import cmath
import re
import serial
import time


# =====================================================================
# QTHREAD – biztonságos serial port olvasás Qt-ban
# =====================================================================
class SerialReader(QThread):
    key_signal = Signal(str)

    def __init__(self, port="COM3", baud=9600):
        super().__init__()
        self.running = True
        self.port = port
        self.baud = baud
        self.ser = None

    def run(self):
        try:
            self.ser = serial.Serial(self.port, self.baud, timeout=0.1)
        except:
            print("Nem sikerült megnyitni a serial portot!")
            return

        mapping = {
            1: "7", 2: "8", 3: "9", 4: "/",
            5: "4", 6: "5", 7: "6", 8: "*",
            9: "1", 10: "2", 11: "3", 12: "-"
        }

        while self.running:
            try:
                line = self.ser.readline().decode().strip()
                if not line:
                    continue

                try:
                    key = int(line)
                except:
                    continue

                if key in mapping:
                    self.key_signal.emit(mapping[key])

            except:
                pass

            time.sleep(0.02)

    def stop(self):
        self.running = False
        time.sleep(0.05)
        try:
            if self.ser:
                self.ser.close()
        except:
            pass


# =====================================================================
# SZÁMOLÓGÉP FŐ OSZTÁLY
# =====================================================================
class SciCalculator(QWidget):
    def __init__(self):
        super().__init__()

        self.clear_on_next = False
        self.serial_mode = False

        self.setWindowTitle("Komplex Tudományos Számológép – Serial Ready")
        self.setFixedSize(430, 600)

        # i mint sqrt(-1)
        self.i = cmath.sqrt(-1)

        # --- Kijelző ---
        self.display = QLineEdit()
        self.display.setReadOnly(True)
        self.display.setStyleSheet("font-size: 26px; padding: 15px;")

        # Serial mód jelzés
        self.mode_label = QLabel("Mód: GUI")
        self.mode_button = QPushButton("Serial mód KI/BE")
        self.mode_button.clicked.connect(self.toggle_serial_mode)

        # Szög mód (deg/rad/grad)
        self.angle_mode = "deg"
        self.angle_label = QLabel("Szög mód: fok")

        # Tabs
        self.tabs = QTabWidget()
        self.tabs.addTab(self.basic_tab(), "Alap")
        self.tabs.addTab(self.science_tab(), "Tudományos")
        self.tabs.addTab(self.complex_tab(), "Komplex")

        # Fő layout
        main = QVBoxLayout()
        main.addWidget(self.display)
        main.addWidget(self.mode_label)
        main.addWidget(self.mode_button)
        main.addWidget(self.angle_label)
        main.addWidget(self.tabs)
        self.setLayout(main)

        # Serial thread
        self.serial_thread = SerialReader("COM3", 9600)
        self.serial_thread.key_signal.connect(self.process_key)

    # =====================================================================
    # SERIAL MODE KI/BE
    # =====================================================================
    def toggle_serial_mode(self):
        self.serial_mode = not self.serial_mode

        if self.serial_mode:
            self.mode_label.setText("Mód: SERIAL")
            self.tabs.hide()
            self.mode_button.setStyleSheet("background:#faa;")
            self.serial_thread.start()
        else:
            self.mode_label.setText("Mód: GUI")
            self.tabs.show()
            self.mode_button.setStyleSheet("")
            self.serial_thread.stop()

            self.serial_thread = SerialReader("COM3", 9600)
            self.serial_thread.key_signal.connect(self.process_key)

    # =====================================================================
    # Bemenet feldolgozása (GUI + SERIAL)
    # =====================================================================
    def process_key(self, text):

        if self.clear_on_next and text not in ["="]:
            self.display.setText("")
            self.clear_on_next = False

        if text == "=":
            self.calculate()
            return

        if text == "C":
            self.display.setText("")
            return

        if text == "deg/rad/grad":
            self.toggle_angle_mode()
            return

        if text == "i":
            self.display.setText(self.display.text() + " i ")
            return

        self.display.setText(self.display.text() + text)

    # -----------------------------
    # GUI-s gombok ezt hívják
    # -----------------------------
    def on_button_click(self):
        text = self.sender().text()
        self.process_key(text)

    # =====================================================================
    # Szög mód váltás
    # =====================================================================
    def toggle_angle_mode(self):
        if self.angle_mode == "deg":
            self.angle_mode = "rad"
            self.angle_label.setText("Szög mód: radián")
        elif self.angle_mode == "rad":
            self.angle_mode = "grad"
            self.angle_label.setText("Szög mód: grad")
        else:
            self.angle_mode = "deg"
            self.angle_label.setText("Szög mód: fok")

    # =====================================================================
    # KIÉRTÉKELÉS
    # =====================================================================
    def calculate(self):
        try:
            expr = self.display.text()

            # Függvények cseréje
            expr = expr.replace("sin", "self.sin_func")
            expr = expr.replace("cos", "self.cos_func")
            expr = expr.replace("tan", "self.tan_func")
            expr = expr.replace("log(", "cmath.log10(")
            expr = expr.replace("ln(", "cmath.log(")
            expr = expr.replace("sqrt", "cmath.sqrt")

            # i mint sqrt(-1)
            expr = re.sub(r'(?<![a-zA-Z0-9_])i(?![a-zA-Z0-9_])', "self.i", expr)

            result = eval(expr)
            self.display.setText(str(result))

            self.clear_on_next = True

        except:
            self.display.setText("Sintaxis hiba")
            self.clear_on_next = True

    # =====================================================================
    # SZÖG FÜGGVÉNYEK (deg/rad/grad)
    # =====================================================================
    def angle_convert(self, x):
        x = complex(eval(str(x)))
        if self.angle_mode == "deg":
            return cmath.pi * x / 180
        elif self.angle_mode == "grad":
            return cmath.pi * x / 200
        return x

    def sin_func(self, x):
        return cmath.sin(self.angle_convert(x))

    def cos_func(self, x):
        return cmath.cos(self.angle_convert(x))

    def tan_func(self, x):
        return cmath.tan(self.angle_convert(x))

    # =====================================================================
    # KOMPLEX FÜGGVÉNYEK
    # =====================================================================
    def real_func(self, x):
        return complex(eval(str(x))).real

    def imag_func(self, x):
        return complex(eval(str(x))).imag

    def conj_func(self, x):
        return complex(eval(str(x))).conjugate()

    # =====================================================================
    # TABOK
    # =====================================================================
    def basic_tab(self):
        w = QWidget()
        l = QGridLayout()
        btns = [["7","8","9","/"],
                ["4","5","6","*"],
                ["1","2","3","-"],
                ["0",".","=","+"]]
        for r,row in enumerate(btns):
            for c,t in enumerate(row):
                b = QPushButton(t)
                b.clicked.connect(self.on_button_click)
                l.addWidget(b,r,c)
        w.setLayout(l)
        return w

    def science_tab(self):
        w = QWidget()
        l = QGridLayout()
        btns = [
            ["sin","cos","tan","sqrt"],
            ["log","ln","i","C"],
            ["("," )","=","deg/rad/grad"]
        ]
        for r,row in enumerate(btns):
            for c,t in enumerate(row):
                b = QPushButton(t)
                b.clicked.connect(self.on_button_click)
                l.addWidget(b,r,c)
        w.setLayout(l)
        return w

    def complex_tab(self):
        w = QWidget()
        l = QGridLayout()
        btns = [
            ["i","real","imag","conj"],
            ["C","=","",""]
        ]
        for r,row in enumerate(btns):
            for c,t in enumerate(row):
                if t:
                    b = QPushButton(t)
                    b.clicked.connect(self.on_button_click)
                    l.addWidget(b,r,c)
        w.setLayout(l)
        return w


# =====================================================================
# MAIN
# =====================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = SciCalculator()
    win.show()
    sys.exit(app.exec())
