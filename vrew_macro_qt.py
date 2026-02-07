import sys
import json
import time
import threading
import pyautogui
import pyperclip
import platform
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QTextEdit, QPushButton, QLineEdit, QMessageBox, QFrame)
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont

class WorkerSignals(QObject):
    update_status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)

class VrewMacroApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('Vrew 대본 자동 입력기')
        self.setGeometry(100, 100, 600, 550) 
        
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 10, 10, 10)

        # 1. Info Label
        self.info_label = QLabel("아래 영역에 JSON 데이터를 붙여넣고 [실행] 버튼을 누르세요.")
        self.info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.info_label)

        # 2. Warning Label
        self.warn_label = QLabel("(실행 후 3초 내에 Vrew의 첫 번째 칸을 클릭하세요)")
        self.warn_label.setStyleSheet("color: red;")
        self.warn_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.warn_label)

        # 3. Text Area
        self.text_area = QTextEdit()
        self.text_area.setMinimumHeight(300) 
        layout.addWidget(self.text_area)

        # 4. Settings
        row1 = QHBoxLayout()
        row1.addStretch()
        row1.addWidget(QLabel("다음 칸 키:"))
        
        self.key_input = QLineEdit("tab")
        self.key_input.setFixedWidth(80) 
        self.key_input.setAlignment(Qt.AlignCenter)
        row1.addWidget(self.key_input)
        
        row1.addWidget(QLabel("(tab, enter, down, right 등)"))
        row1.addStretch()
        layout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addStretch()
        row2.addWidget(QLabel("입력 딜레이(초):"))
        
        self.delay_input = QLineEdit("0.2")
        self.delay_input.setFixedWidth(80) 
        self.delay_input.setAlignment(Qt.AlignCenter)
        row2.addWidget(self.delay_input)
        
        row2.addWidget(QLabel("(기본 0.2, 컴퓨터가 느리면 늘리세요)"))
        row2.addStretch()
        layout.addLayout(row2)

        # 5. Start Button
        self.btn = QPushButton('매크로 실행 (Start)')
        self.btn.clicked.connect(self.start_macro)
        self.btn.setFixedHeight(50) 
        self.btn.setStyleSheet("""
            QPushButton {
                background-color: lightblue; 
                border: 1px solid gray;
                border-radius: 5px;
                color: black;
                font-weight: bold;
            }
            QPushButton:pressed { background-color: #add8e6; }
        """)
        layout.addWidget(self.btn)

        # 6. Status Label
        self.status_label = QLabel("대기 중...")
        self.status_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.status_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.show()

    def start_macro(self):
        json_text = self.text_area.toPlainText().strip()
        if not json_text:
            QMessageBox.warning(self, "경고", "JSON 데이터를 입력해주세요.")
            return

        try:
            data = json.loads(json_text)
            delay = float(self.delay_input.text())
            key = self.key_input.text()
        except Exception as e:
            QMessageBox.critical(self, "JSON 형식이 잘못되었습니다", f"에러 내용:\n{e}")
            return

        self.btn.setEnabled(False)
        self.signals = WorkerSignals()
        self.signals.update_status.connect(self.update_status_label)
        self.signals.finished.connect(self.on_finished)
        self.signals.error.connect(self.on_error)

        threading.Thread(target=self.run_logic, args=(data, key, delay, self.signals), daemon=True).start()

    def update_status_label(self, text):
        self.status_label.setText(text)

    def on_finished(self):
        self.btn.setEnabled(True)
        QMessageBox.information(self, "완료", "모든 입력이 완료되었습니다.")
        self.status_label.setText("완료됨")

    def on_error(self, err_msg):
        self.btn.setEnabled(True)
        QMessageBox.critical(self, "에러 발생", err_msg)
        self.status_label.setText("에러 발생")

    def run_logic(self, data, next_key, delay, signals):
        try:
            signals.update_status.emit("3초 후에 시작됩니다. Vrew 창을 클릭하세요!")
            time.sleep(3)

            total = len(data)
            count = 0
            mod_key = 'command' if platform.system() == 'Darwin' else 'ctrl'

            for k, text in data.items():
                if not text: continue
                pyperclip.copy(text)
                pyautogui.hotkey(mod_key, 'v')
                time.sleep(delay)
                pyautogui.press(next_key)
                time.sleep(delay)
                
                count += 1
                progress = int((count / total) * 100)
                signals.update_status.emit(f"진행 중... ({progress}%) - {k}")

            signals.finished.emit()

        except Exception as e:
            signals.error.emit(str(e))

if __name__ == '__main__':
    pyautogui.FAILSAFE = True
    app = QApplication(sys.argv)
    ex = VrewMacroApp()
    sys.exit(app.exec_())
