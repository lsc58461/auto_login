# pyinstaller -w --onefile --icon=..\assets\icons\NIX.ico update.py
from PIL import Image, ImageTk
from ftplib import FTP
import sys
import threading
import os
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.messagebox as messagebox
import subprocess
import logging


class LoadingWindow:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("업데이트")

        # 창 크기 설정
        window_width, window_height = 250, 55
        self.window.geometry(f"{window_width}x{window_height}")

        self.window.attributes('-topmost', True)  # 최상위로 설정

        # 화면 중앙에 창 위치 설정
        screen_width = self.window.winfo_screenwidth()
        screen_height = self.window.winfo_screenheight()
        x = (screen_width // 2) - (window_width // 2)
        y = (screen_height // 2) - (window_height // 2)
        self.window.geometry(f"+{x}+{y}")

        self.window.config(bg="black")
        self.window.overrideredirect(True)  # 타이틀 바 제거

        self.window.attributes("-transparentcolor", "black")  # 배경 투명 설정

        self.frame = ttk.Frame(self.window)
        self.frame.pack(pady=20)

        self.progress = ttk.Progressbar(
            self.frame, length=200, mode='determinate')
        self.progress.pack(side="left")

        self.percentage_var = tk.StringVar()
        self.percentage_label = tk.Label(
            self.frame, textvariable=self.percentage_var, bg="black")
        self.percentage_label.config(font=("Arial", 10), fg="white")
        self.percentage_label.pack(side="left")

        self.previous_progress = 0  # 이전 진행 상태를 저장하는 변수

    def set_progress(self, value):
        if value != self.previous_progress:  # 이전 진행 상태와 현재 진행 상태를 비교
            self.progress['value'] = value
            self.percentage_var.set(f"{int(value)}%")
            logging.info(f"{int(value)}%")
            self.window.update_idletasks()
            self.previous_progress = value

    def show(self):
        self.window.protocol("WM_DELETE_WINDOW", self.close)  # 창 닫기 버튼 이벤트 처리
        self.window.mainloop()

    def close(self):
        self.window.destroy()


def download_file(loading_window, progress):
    # replace with your FTP server details
    ftp = FTP('')
    ftp.login('', '')

    # 접속 성공 후 파일 목록 가져오기
    file_list = ftp.nlst()

    # 가져온 파일 목록 출력
    logging.info(f'디버그 : {file_list}')

    # Change to the desired directory
    ftp.cwd('/html/UPDATE/')

    filename = 'Auto_Login.exe'

    # Set transfer mode to binary
    ftp.voidcmd('TYPE I')

    # 현재 실행 파일의 위치에서 두 단계 위의 디렉토리를 가져옵니다.
    target_dir = os.path.dirname(os.path.dirname(get_current_directory()))

    # 다운로드 파일의 경로를 설정합니다.
    download_file_path = os.path.join(target_dir, "Auto_Login.exe")
    logging.info(f'다운로드 파일의 경로 : {download_file_path}')

    localfile = open(download_file_path, 'wb')

    # Get the file size for progress tracking
    file_size = ftp.size(filename)

    def callback(chunk):
        nonlocal progress
        localfile.write(chunk)
        progress += len(chunk)
        percentage = int(progress / file_size * 100)

        if percentage != loading_window.previous_progress:
            loading_window.set_progress(percentage)

    # Download the file from FTP server and replace the local file
    ftp.retrbinary('RETR ' + filename, callback, 1024)

    ftp.quit()
    localfile.close()


def get_current_directory():
    if getattr(sys, 'frozen', False):  # pyinstaller로 생성된 실행 파일인 경우
        current_dir = os.path.dirname(sys.executable)
        logging.info(f'pyinstaller : {current_dir}')
    else:  # 스크립트로 실행한 경우
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logging.info(f'script : {current_dir}')
    return current_dir


def main():
    # 로딩 창을 표시합니다.
    loading_window = LoadingWindow()

    def check_threads_completion():
        if download_thread.is_alive():
            logging.info('다운로드 중')
            # 스레드들이 여전히 실행 중이면 100ms 후에 다시 확인합니다.
            loading_window.window.after(100, check_threads_completion)
        else:
            # 스레드들이 완료되면 로딩 창을 닫고 메시지 박스를 생성합니다.
            messagebox.showinfo("업데이트 완료", "업데이트가 성공적으로 완료되었습니다!")
            logging.info(f'업데이트 완료')

            # 업데이트된 파일 실행
            target_dir = os.path.dirname(
                os.path.dirname(get_current_directory()))
            logging.info(f'업데이드 된 파일 위치 : {target_dir}')
            update_file_path = target_dir + "\\Auto_Login.exe"  # 실행할 파일 경로
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(update_file_path,
                             stdin=None, stdout=None, stderr=None, shell=True,
                             creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
                             )
            logging.info('update_file 실행')
            loading_window.close()
            logging.info('loading_window 종료')

    try:
        messagebox.showinfo("업데이트", "최신버전이 있습니다.\n업데이트를 시작합니다.")

        # progress 변수 초기화
        progress = 0

        # 스레드 생성
        download_thread = threading.Thread(
            target=lambda: download_file(loading_window, progress))

        # 스레드 시작
        download_thread.start()

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
    # 로그 생성
    logger = logging.getLogger()

    # 로그의 출력 기준 설정
    logger.setLevel(logging.INFO)

    # log 출력 형식
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # log 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # log를 파일에 출력
    file_handler = logging.FileHandler('update.log')
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    main()
