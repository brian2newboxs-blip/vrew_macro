import tkinter as tk
from tkinter import scrolledtext, messagebox
import json
import platform
import pyautogui
import pyperclip
import time
import threading

class VrewMacroApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Vrew 대본 자동 입력기")
        self.root.geometry("600x550")

        # 설명 라벨 (일반 텍스트)
        self.info_label = tk.Label(root, text="아래 영역에 JSON 데이터를 붙여넣고 [실행] 버튼을 누르세요.", pady=5)
        self.info_label.pack(pady=(10, 0))

        # 설명 라벨 (빨간색 경고)
        self.warn_label = tk.Label(root, text="(실행 후 3초 내에 Vrew의 첫 번째 칸을 클릭하세요)", fg="red", pady=5)
        self.warn_label.pack(pady=(0, 10))

        # JSON 입력 텍스트 영역 (스크롤 가능)
        self.text_area = scrolledtext.ScrolledText(root, width=70, height=20)
        self.text_area.pack(padx=10, pady=5)

        # 설정 프레임 (컨테이너)
        self.setting_container = tk.Frame(root)
        self.setting_container.pack(pady=5)

        # 설정 1행: 다음 칸 키
        self.row1_frame = tk.Frame(self.setting_container)
        self.row1_frame.pack(side=tk.TOP, fill=tk.X, pady=2)
        
        tk.Label(self.row1_frame, text="다음 칸 키:").pack(side=tk.LEFT)
        self.next_key_var = tk.StringVar(value="tab")
        self.key_entry = tk.Entry(self.row1_frame, textvariable=self.next_key_var, width=10)
        self.key_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(self.row1_frame, text="(tab, enter, down, right 등)").pack(side=tk.LEFT)

        # 설정 2행: 딜레이 시간
        self.row2_frame = tk.Frame(self.setting_container)
        self.row2_frame.pack(side=tk.TOP, fill=tk.X, pady=2)

        tk.Label(self.row2_frame, text="입력 딜레이(초):").pack(side=tk.LEFT)
        self.delay_var = tk.StringVar(value="0.1")
        self.delay_entry = tk.Entry(self.row2_frame, textvariable=self.delay_var, width=10)
        self.delay_entry.pack(side=tk.LEFT, padx=5)
        tk.Label(self.row2_frame, text="(기본 0.1, 컴퓨터가 느리면 늘리세요)").pack(side=tk.LEFT)

        # 하단 버튼 프레임
        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack(pady=10)

        self.start_btn = tk.Button(self.btn_frame, text="매크로 실행 (Start)", command=self.on_start_click, bg="lightblue", height=2, width=20)
        self.start_btn.pack()

        # 상태 표시줄
        self.status_label = tk.Label(root, text="대기 중...", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def on_start_click(self):
        # 입력된 JSON 가져오기
        json_input = self.text_area.get("1.0", tk.END).strip()
        
        if not json_input:
            messagebox.showwarning("경고", "JSON 데이터를 입력해주세요.")
            return

        try:
            # JSON 파싱 테스트
            data = json.loads(json_input)
        except json.JSONDecodeError as e:
            messagebox.showerror("JSON 형식이 잘못되었습니다", f"에러 내용:\n{e}")
            return
            
        # 딜레이 값 확인
        try:
            delay_val = float(self.delay_var.get())
            if delay_val < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("경고", "딜레이는 0 이상의 숫자여야 합니다.")
            return

        # 매크로 실행 스레드 시작
        next_key = self.next_key_var.get()
        threading.Thread(target=self.run_macro, args=(data, next_key, delay_val), daemon=True).start()

    def run_macro(self, data, next_key, delay):
        self.update_status("3초 후에 시작됩니다. Vrew 창을 클릭하세요!")
        self.start_btn.config(state=tk.DISABLED)
        
        # 3초 카운트다운
        for i in range(3, 0, -1):
            self.update_status(f"{i}초 전... Vrew 입력칸을 클릭해두세요.")
            time.sleep(1)

        self.update_status("입력 시작!")
        
        try:
            total_items = len(data)
            current_idx = 0
            
            for key, text in data.items():
                if not text:
                    continue
                
                # 1. 클립보드 복사
                pyperclip.copy(text)
                
                # 2. 붙여넣기
                # Mac 사용 시 'command', Windows는 'ctrl'
                if platform.system() == 'Darwin':
                    pyautogui.hotkey('command', 'v')
                else:
                    pyautogui.hotkey('ctrl', 'v')
                time.sleep(delay) # 사용자가 설정한 딜레이 적용
                
                # 3. 다음 칸 이동
                pyautogui.press(next_key)
                time.sleep(delay) # 사용자가 설정한 딜레이 적용
                
                current_idx += 1
                progress_percent = int((current_idx / total_items) * 100)
                self.update_status(f"진행 중... ({progress_percent}%) - {key}")

            messagebox.showinfo("완료", "모든 입력이 완료되었습니다.")
            self.update_status("완료됨")
            
        except Exception as e:
            messagebox.showerror("에러 발생", str(e))
            self.update_status("에러 발생")
            
        finally:
            self.start_btn.config(state=tk.NORMAL)

    def update_status(self, text):
        self.status_label.config(text=text)

if __name__ == "__main__":
    # pyautogui 안전장치
    pyautogui.FAILSAFE = True
    
    root = tk.Tk()
    app = VrewMacroApp(root)
    root.mainloop()
