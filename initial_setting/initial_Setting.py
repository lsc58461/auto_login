# pyinstaller -w --onefile --icon=.\NIX.ico --add-data "..\assets\loading\loading.gif;." main.py
import os
import sys
import shutil
import threading
import configparser
import tkinter as tk
from PIL import Image, ImageTk


config = configparser.ConfigParser()


class LoadingWindow:
    def __init__(self, gif_path):

        # 파일을 다른 경로로 설치하기
        self.window = tk.Tk()
        self.window.title("검색 중...")

        # 창 크기 설정
        window_width, window_height = 250, 250
        self.window.geometry(f"{window_width}x{window_height}")

        # 화면 중앙에 창 위치 설정
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"+{x}+{y}")

        self.window.config(bg="white")
        self.window.overrideredirect(True)  # 타이틀 바 제거

        self.frames = []
        self.load_gif(gif_path)

        self.label = tk.Label(self.window, bg="white")
        self.label.pack()

        self.current_frame = 0
        self.update_image()

    def load_gif(self, gif_path):
        gif = Image.open(gif_path)
        for i in range(gif.n_frames):
            gif.seek(i)
            frame = ImageTk.PhotoImage(gif)
            self.frames.append(frame)

    def update_image(self):
        self.label.config(image=self.frames[self.current_frame])
        self.current_frame = (self.current_frame + 1) % len(self.frames)
        self.window.after(30, self.update_image)  # Update every 100ms

    def show(self):
        self.window.protocol("WM_DELETE_WINDOW", self.close)  # 창 닫기 버튼 이벤트 처리
        self.window.mainloop()

    def close(self):
        self.window.destroy()


# 롤과 크롬의 실행 파일 이름
LOL_EXE = "LeagueClient.exe"
CHROME_EXE = "chrome.exe"

# 검색할 폴더 리스트
SEARCH_FOLDERS = [
    "C:\Riot Games",
    "D:\Riot Games",
    "E:\Riot Games",
    "C:\Program Files\Google\Chrome\Application",
    "C:\Program Files (x86)\Google\Chrome\Application",
    "D:\Program Files\Google\Chrome\Application",
    "D:\Program Files (x86)\Google\Chrome\Application",
    "E:\Program Files\Google\Chrome\Application",
    "E:\Program Files (x86)\Google\Chrome\Application",
    "C:\Program Files",
    "C:\Program Files (x86)",
    "D:\Program Files",
    "D:\Program Files (x86)",
    "E:\Program Files",
    "E:\Program Files (x86)"
]


def search_file(file_name):
    for folder in SEARCH_FOLDERS:
        print(folder)
        for root, dirs, files in os.walk(folder):
            print(root, dirs, files)
            if file_name in files:
                return os.path.join(root + '\\' + file_name)

    for drive in range(ord('A'), ord('Z')+1):
        drive = chr(drive) + ":\\"
        print(drive)
        for root, dirs, files in os.walk(drive):
            print(root, dirs, files)
            if file_name in files:
                return os.path.join(root + '\\' + file_name)
    return None


def get_current_directory():
    if getattr(sys, 'frozen', False):  # pyinstaller로 생성된 실행 파일인 경우
        current_dir = os.path.dirname(sys.executable)
    else:  # 스크립트로 실행한 경우
        current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir


def save_to_file(file_name, content):
    with open(file_name, 'w') as file:
        file.write(content)


def save_path(type, path):
    # 실행 파일이 있는 디렉토리를 기준으로 절대 경로를 얻습니다.
    current_dir = get_current_directory()

    if type == 'LOL':
        file_name = 'Local_LOL.nix'
        content = f'[LOL]\nPath={path}'
    elif type == 'Chrome':
        file_name = 'Local_Chrome.nix'
        content = f'[Chrome]\nPath={path}'

    save_to_file(os.path.join(current_dir, file_name), content)


def search_and_display_path_lol():
    lol_result = search_file(LOL_EXE)

    if lol_result:
        print('롤 경로 검색 완료')
        save_path('LOL', lol_result)
    else:
        print('롤 경로를 찾을 수 없습니다.')


def search_and_display_path_chrome():
    chrome_result = search_file(CHROME_EXE)

    if chrome_result:
        print('크롬 경로 검색 완료')
        save_path('Chrome', chrome_result)
    else:
        print('크롬 경로를 찾을 수 없습니다.')


def main():
    current_dir = get_current_directory()

    ini_file_path = os.path.join(get_current_directory(), 'Local_Setting.nix')

    try:
        # 'init' 값이 1이면 프로그램 종료
        config.read(ini_file_path)
        initial = config['Initial']['init']
        if initial == '1':
            return
    except:
        pass

    # 현재 디렉토리에 'Local_Setting.nix' 파일 생성
    config['Initial'] = {}
    config['Initial']['init'] = '1'
    with open(ini_file_path, 'w') as configfile:
        config.write(configfile)

    def get_file_path(filename):
        if hasattr(sys, '_MEIPASS'):
            # 실행 파일 내부에서 실행 중인 경우
            print(os.path.join(sys._MEIPASS, filename))
            return os.path.join(sys._MEIPASS, filename)
        else:
            # 일반적인 파이썬 스크립트로 실행 중인 경우
            print(os.path.dirname(os.path.abspath(__file__)) + "\\" + filename)
            return os.path.dirname(os.path.abspath(__file__)) + "\\" + filename

    # 파일 경로 설정 예시
    gif_path = get_file_path("loading.gif")

    # 로딩 창을 표시합니다.
    loading_window = LoadingWindow(gif_path)

    def check_threads_completion():
        if lol_thread.is_alive() or chrome_thread.is_alive():
            # 스레드들이 여전히 실행 중이면 100ms 후에 다시 확인합니다.
            loading_window.window.after(100, check_threads_completion)
        else:
            # 스레드들이 완료되면 로딩 창을 닫습니다.
            loading_window.close()

    try:
        print('롤 경로 검색 대기 중 입니다.')

        # 스레드 생성
        lol_thread = threading.Thread(target=search_and_display_path_lol)
        chrome_thread = threading.Thread(target=search_and_display_path_chrome)

        # 스레드 시작
        lol_thread.start()
        chrome_thread.start()

        # 스레드들의 완료 여부를 주기적으로 확인합니다.
        check_threads_completion()

        # 로딩 창을 메인 스레드에서 실행
        loading_window.show()

    except Exception as e:
        # 예외가 발생하면 로그 파일에 에러 메시지를 기록합니다.
        current_dir = get_current_directory()
        log_file = os.path.join(current_dir, 'error.log')

        with open(log_file, 'w') as f:
            f.write(f"Error: {str(e)}")


if __name__ == "__main__":
    main()
