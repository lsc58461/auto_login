'''
pyinstaller -w --uac-admin --onefile --icon=.\\assets\\icons\\NIX.ico `
--add-data ".\\qss\\styles.qss;.\\qss" `
--add-data ".\\assets\\icons\\NIX.ico;.\\assets\\icons" `
--add-data ".\\initial_setting\\Initial_Setting.exe;.\\initial_setting" `
--add-data ".\\update\\update.exe;.\\update" `
--add-data ".\\images\\login_success_form.png;.\\images" `
--add-data ".\\images\\login_page.png;.\\images" `
--add-data ".\\images\\login_result_1.png;.\\images" `
--add-data ".\\images\\login_result_2.png;.\\images" `
--add-data ".\\images\\LOL_button.png;.\\images" `
--add-data ".\\images\\play_button.png;.\\images" `
--add-data ".\\images\\refresh.png;.\\images" `
--add-data ".\\images\\add.png;.\\images" `
--add-data ".\\images\\delete.png;.\\images" `
--add-data ".\\images\\edit.png;.\\images" `
--add-data ".\\images\\alert.png;.\\images" `
--add-data ".\\images\\unranked.png;.\\images" `
--add-data ".\\assets\\fonts\\NanumSquareL.ttf;.\\assets\\fonts" `
--add-data ".\\assets\\fonts\\SB 어그로 L.ttf;.\\assets\\fonts" `
--add-data ".\\assets\\fonts\\SB 어그로 M.ttf;.\\assets\\fonts" `
--add-data ".\\assets\\fonts\\EF_watermelonSalad.ttf;.\\assets\\fonts" `
--add-data ".\\sounds\\alert.wav;.\\sounds" `
--name=Auto_Login main.py
'''

from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QPushButton, QGraphicsDropShadowEffect, QSizePolicy, QLineEdit, QLabel, QVBoxLayout, QWidget, QMessageBox, QListView, QDialog, QAbstractItemView
from PyQt5.QtGui import QStandardItemModel, QStandardItem, QFont, QIcon, QPixmap, QCursor, QColor, QFontDatabase
from PyQt5.QtCore import Qt, QModelIndex, pyqtSignal, pyqtSlot, QSize
from PyQt5 import QtCore
from PyQt5.QtMultimedia import QSound

import os
import sys
import time
import hashlib
import ctypes
import shutil
import win32gui
import requests
import subprocess
from urllib.parse import quote
import configparser
import pyautogui
import pyperclip
import threading
import logging
import cv2
import numpy as np
import pygetwindow as gw
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


ver = '4.1.1'


class MainWindow(QMainWindow):
    login_attempt_signal = pyqtSignal(str, str)
    login_result_signal = pyqtSignal(bool)
    play_button_clicked_signal = pyqtSignal(int)
    LOL_button_clicked_signal = pyqtSignal(int)

    def __init__(self):
        super(MainWindow, self).__init__()

        style_path = os.path.join(current_dir, ".\\NIX\\Data\\styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

        # This line will hide the maximize button

        self.setWindowTitle(ver)
        self.resize(540, 730)

        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # Fix the window size.
        self.setFixedSize(self.size())

        self.setWindowIcon(QIcon(f'{current_dir}\\NIX\\Data\\ICO\\NIX.ico'))

        self.widget = QWidget()
        self.layout = QVBoxLayout(self.widget)

        # Signal을 slot에 연결
        self.login_attempt_signal.connect(self.show_login_attempt_message)
        self.login_result_signal.connect(self.update_login_result)
        self.LOL_button_clicked_signal.connect(
            self.try_click_LOL_button_until_timeout)
        self.play_button_clicked_signal.connect(
            self.try_click_play_button_until_timeout)

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setObjectName('tool-button')
        self.layout.addWidget(self.title_bar)

        self.title_label = QLabel("apple")
        self.title_label.setObjectName('title-label')
        self.title_label.setAlignment(QtCore.Qt.AlignCenter)
        self.title_label_shadow = QGraphicsDropShadowEffect(self)
        self.title_label_shadow.setBlurRadius(99)
        self.title_label_shadow.setColor(QColor(255, 255, 255))
        self.title_label_shadow.setOffset(0)
        self.title_label.setGraphicsEffect(
            self.title_label_shadow)

        # 탭 순서 설정
        self.account_list = QListView(self)
        self.account_list.verticalScrollBar()
        self.account_list.setFixedHeight(500)
        self.account_list.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.account_list_shadow = QGraphicsDropShadowEffect(self)
        self.account_list_shadow.setBlurRadius(99)
        self.account_list_shadow.setColor(QColor(255, 255, 255, 10))
        self.account_list_shadow.setOffset(0)
        self.account_list.setGraphicsEffect(
            self.account_list_shadow)

        # QStandardItemModel 인스턴스 생성
        self.model = QStandardItemModel(self.account_list)

        # 이미지 아이콘 크기 조절
        icon_size = 10
        icon_path = f'{current_dir}\\NIX\\Data\\Assets\\add.png'
        pixmap = QPixmap(icon_path).scaled(icon_size, icon_size)
        self.add_account_button = QPushButton('', self)
        self.add_account_button.setIcon(QIcon(pixmap))
        self.add_account_button.setToolTip("계정 추가")  # 툴팁 설정
        self.add_account_button.setFixedWidth(24)
        self.add_account_button.setFixedHeight(24)
        self.add_account_button.setObjectName('tool-button')
        self.add_account_button.clicked.connect(self.add_account)
        self.add_account_button_shadow = QGraphicsDropShadowEffect(self)
        self.add_account_button_shadow.setBlurRadius(15)
        self.add_account_button_shadow.setColor(QColor(0, 0, 0, 30))
        self.add_account_button_shadow.setOffset(0)
        self.add_account_button.setGraphicsEffect(
            self.add_account_button_shadow)

        icon_size = 10
        icon_path = f'{current_dir}\\NIX\\Data\\Assets\\delete.png'
        pixmap = QPixmap(icon_path).scaled(icon_size, icon_size)
        self.delete_account_button = QPushButton('', self)
        self.delete_account_button.setIcon(QIcon(pixmap))
        self.delete_account_button.setToolTip("계정 삭제")  # 툴팁 설정
        self.delete_account_button.setFixedWidth(24)
        self.delete_account_button.setFixedHeight(24)
        self.delete_account_button.setObjectName('tool-button')
        self.delete_account_button.clicked.connect(self.delete_account)
        self.delete_account_button_shadow = QGraphicsDropShadowEffect(self)
        self.delete_account_button_shadow.setBlurRadius(15)
        self.delete_account_button_shadow.setColor(QColor(0, 0, 0, 30))
        self.delete_account_button_shadow.setOffset(0)
        self.delete_account_button.setGraphicsEffect(
            self.delete_account_button_shadow)

        icon_size = 13
        icon_path = f'{current_dir}\\NIX\\Data\\Assets\\edit.png'
        pixmap = QPixmap(icon_path).scaled(icon_size, icon_size)
        self.account_setting_button = QPushButton('', self)
        self.account_setting_button.setIcon(QIcon(pixmap))
        self.account_setting_button.setToolTip("계정 수정")  # 툴팁 설정
        self.account_setting_button.setFixedWidth(24)
        self.account_setting_button.setFixedHeight(24)
        self.account_setting_button.setObjectName('tool-button')
        self.account_setting_button.clicked.connect(self.edit_account)
        self.account_setting_button_shadow = QGraphicsDropShadowEffect(self)
        self.account_setting_button_shadow.setBlurRadius(15)
        self.account_setting_button_shadow.setColor(QColor(0, 0, 0, 30))
        self.account_setting_button_shadow.setOffset(0)
        self.account_setting_button.setGraphicsEffect(
            self.account_setting_button_shadow)

        self.horizontal_tools_layout = QHBoxLayout()
        self.horizontal_tools_layout.addStretch()
        self.horizontal_tools_layout.addWidget(self.add_account_button)
        self.horizontal_tools_layout.addWidget(self.delete_account_button)
        self.horizontal_tools_layout.addWidget(self.account_setting_button)

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        spacer.setFixedWidth(24)
        spacer.setFixedHeight(20)
        self.horizontal_tools_layout.addWidget(spacer)

        self.update_image_url_button = QPushButton('', self)
        self.update_image_url_button.setIcon(
            QIcon(f'{current_dir}\\NIX\\Data\\Assets\\refresh.png'))  # 이미지 아이콘 설정
        self.update_image_url_button.setIconSize(QSize(30, 30))
        self.update_image_url_button.setFixedSize(60, 60)
        self.update_image_url_button.setToolTip('티어 갱신')
        self.update_image_url_button.setObjectName('button')
        self.update_image_url_button.clicked.connect(
            self.update_image_url_handle_click)

        self.horizontal_center_layout = QHBoxLayout()
        self.horizontal_center_layout.addStretch()
        self.horizontal_center_layout.addWidget(self.update_image_url_button)
        self.horizontal_center_layout.addStretch()

        self.layout.addWidget(self.title_label)
        self.layout.addLayout(self.horizontal_tools_layout)  # 버튼 레이아웃 추가
        self.layout.addWidget(self.account_list)
        self.layout.addLayout(self.horizontal_center_layout)

        self.setCentralWidget(self.widget)

        self.account_list.doubleClicked.connect(self.update_main_account)
        self.refresh_list_view()

        font_db = QFontDatabase()

        # 첫 번째 폰트 추가
        NanumSquare_Light_path = f'{current_dir}\\NIX\\Data\\Assets\\NanumSquareL.ttf'
        NanumSquare_Light_id = font_db.addApplicationFont(
            NanumSquare_Light_path)

        # 두 번째 폰트 추가
        SB_Aggro_Medium = f'{current_dir}\\NIX\\Data\\Assets\\SB 어그로 M.ttf'
        SB_Aggro_Medium_id = font_db.addApplicationFont(SB_Aggro_Medium)

        # 두 번째 폰트 추가
        EF_watermelonSalad = f'{current_dir}\\NIX\\Data\\Assets\\EF_watermelonSalad.ttf'
        EF_watermelonSalad_id = font_db.addApplicationFont(EF_watermelonSalad)

        if NanumSquare_Light_id != -1 and SB_Aggro_Medium_id != -1 and EF_watermelonSalad_id != -1:
            NanumSquare_Light_font_family = font_db.applicationFontFamilies(
                NanumSquare_Light_id)[0]
            SB_Aggro_Medium_font_family = font_db.applicationFontFamilies(SB_Aggro_Medium_id)[
                0]
            EF_watermelonSalad_font_family = font_db.applicationFontFamilies(EF_watermelonSalad_id)[
                0]

            print(NanumSquare_Light_font_family)
            print(SB_Aggro_Medium_font_family)
            print(EF_watermelonSalad_font_family)

            # 첫 번째 폰트를 위한 QFont 객체 생성
            NanumSquare_Light_font = QFont()
            NanumSquare_Light_font.setFamily(NanumSquare_Light_font_family)

            # 두 번째 폰트를 위한 QFont 객체 생성
            SB_Aggro_Medium_font = QFont()
            SB_Aggro_Medium_font.setFamily(SB_Aggro_Medium_font_family)

            EF_watermelonSalad_font = QFont()
            EF_watermelonSalad_font.setFamily(EF_watermelonSalad_font_family)

            # 각 위젯에 해당 폰트 적용
            self.title_label.setFont(NanumSquare_Light_font)
            self.account_list.setFont(NanumSquare_Light_font)

            # 필요한 경우 다른 위젯에도 해당 폰트 적용 가능

        else:
            logging.warning("Font loading failed.")

    def show_alert(self, title, text):
        icon_path = os.path.join(
            current_dir, 'NIX', 'Data', 'Assets', 'alert.png')
        custom_alert = CustomAlert(self, title, text, icon_path)
        custom_alert.exec_()

    def apply_font(self, font):
        self.setFont(font)
        for widget in self.findChildren(QWidget):
            widget.setFont(font)

    def check_account_info(self, ini_file_path):
        if not os.path.isfile(ini_file_path):
            self.unblock_input()
            self.login_attempt_signal.emit(
                'warning', '계정 정보가 없습니다.\n설정에서 아이디, 패스워드를 저장 후\n자동 로그인에 사용 할 계정을 더블 클릭해서 지정해주세요.')
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

        except Exception as e:
            self.unblock_input()
            self.login_attempt_signal.emit(
                'critical', f"예외가 발생했습니다.\n{str(e)}")
            logging.warning(str(e))
            self.login_result_signal.emit(False)

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
                break

    @pyqtSlot(int)
    def try_click_play_button_until_timeout(self, timeout):
        logging.info('try_click_play_button_until_timeout')
        start_time = time.time()

        while time.time() - start_time < timeout:
            if self.find_and_click_play_button():
                break

    @pyqtSlot(str, str)
    def show_login_attempt_message(self, icon, message):
        logging.info(message)
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

        self.on_login_button_click()

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
        
        tier_mapping = {
            'iron': '아이언',
            'bronze': '브론즈',
            'silver': '실버',
            'gold': '골드',
            'emerald': '에메랄드',
            'platinum': '플래티넘',
            'diamond': '다이아몬드',
            'master': '마스터',
            'grandmaster': '그랜드마스터',
            'challenger': '챌린저'
        }

        icon_size = 36

        self.model.clear()
        dir_path = os.path.join(os.getcwd(), "NIX", "Data", "Account")

        for filename in os.listdir(dir_path):
            if filename.endswith(".ini"):
                config = configparser.ConfigParser()
                config.read(os.path.join(dir_path, filename))
                nickname = config['Account']['NickName']
                item = QStandardItem(nickname)
                image_url = config['Account']['ImageURL']
                if image_url:  # 이미지 URL이 존재할 경우

                    for tier, tooltip in tier_mapping.items():
                        if tier in image_url:
                            tier_tooltip = tooltip

                    pixmap = QPixmap()
                    pixmap.loadFromData(requests.get(image_url).content)
                    item.setIcon(QIcon(pixmap))
                    item.setToolTip(f'{tier_tooltip} {nickname}')
                else:
                    unranked_image_path = f'{current_dir}\\NIX\\Data\\Assets\\unranked.png'
                    pixmap = QPixmap(unranked_image_path)
                    item.setIcon(QIcon(pixmap))
                    item.setToolTip(f'언랭 {nickname}',)

                item.setSizeHint(QSize(-1, icon_size))  # 가로 길이는 -1로 설정하여 기존 가로 길이를 유지
                self.model.appendRow(item)

        self.account_list.setIconSize(QSize(icon_size, icon_size))
        self.account_list.setModel(self.model)

    def add_account(self):
        dialog = AddAccountDialog(self)
        if dialog.exec_():
            self.refresh_list_view()

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
                    self.update_image_url(config_path)

            self.update_image_url(config_dict)
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

    def update_image_url(self, config_path):
        try:
            config = configparser.ConfigParser()
            config.read(config_path)

            for section in config.sections():
                nickname = config[section]['NickName']

                image_url = get_tier_image_url(nickname)

                # Update the image_url value in the config dictionary
                config.set(section, 'ImageURL', image_url)

                # Save the updated configuration back to the ini file
                with open(config_path, 'w') as configfile:
                    config.write(configfile)

        except Exception as e:
            self.show_alert('알림', '티어 갱신에 실패했습니다.')
            logging.error(f'update_image_url error: {e}')
            self.update_image_url_button.setEnabled(True)

    def closeEvent(self, event):
        # 프로그램 종료 시 수행할 로직 작성
        try:
            logging.info('프로그램 종료')
        except Exception as e:
            logging.warning(f'close event error: {e}')
        finally:
            # 기본 closeEvent 처리를 유지하려면 아래 라인 주석 처리
            super().closeEvent(event)


class AddAccountDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)

        style_path = os.path.join(current_dir, ".\\NIX\\Data\\styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

        self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("Add Account")
        self.resize(460, 240)
        self.setFixedSize(self.size())

        self.layout = QVBoxLayout()

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setObjectName('tool-button')
        self.layout.addWidget(self.title_bar)

        self.id_input = QLineEdit(self)
        self.id_input.setPlaceholderText("아이디")
        self.id_input.setFixedWidth(404)
        self.id_input.setFixedHeight(54)
        self.id_input.setObjectName('account-input')

        self.id_input_shadow = QGraphicsDropShadowEffect(self)
        self.id_input_shadow.setBlurRadius(10)
        self.id_input_shadow.setColor(QColor(0, 0, 0, 20))
        self.id_input_shadow.setOffset(5)
        self.id_input.setGraphicsEffect(self.id_input_shadow)

        self.id_input_layout = QVBoxLayout()
        self.id_input_layout.addWidget(self.id_input)
        self.id_input_layout.setAlignment(Qt.AlignCenter)

        self.pw_input = QLineEdit(self)
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setFixedWidth(404)
        self.pw_input.setFixedHeight(54)
        self.pw_input.setObjectName('account-input')

        self.pw_input_shadow = QGraphicsDropShadowEffect(self)
        self.pw_input_shadow.setBlurRadius(10)
        self.pw_input_shadow.setColor(QColor(0, 0, 0, 20))
        self.pw_input_shadow.setOffset(5)
        self.pw_input.setGraphicsEffect(self.pw_input_shadow)

        self.pw_input_layout = QVBoxLayout()
        self.pw_input_layout.addWidget(self.pw_input)
        self.pw_input_layout.setAlignment(Qt.AlignCenter)

        self.ok_button = QPushButton("등록", self)
        self.ok_button.setFixedWidth(90)
        self.ok_button.setFixedHeight(36)
        self.ok_button.setObjectName('save-button')
        self.ok_button.clicked.connect(self.add_account)
        self.ok_button_shadow = QGraphicsDropShadowEffect(self)
        self.ok_button_shadow.setBlurRadius(20)
        self.ok_button_shadow.setColor(QColor(0, 0, 0, 20))
        self.ok_button_shadow.setOffset(0)
        self.ok_button.setGraphicsEffect(self.ok_button_shadow)

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(self.id_input_layout)
        self.layout.addLayout(self.pw_input_layout)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.file_path = file_path
        self.parent = parent

        font_db = QFontDatabase()

        NanumSquare_Light_path = f'{current_dir}\\NIX\\Data\\Assets\\NanumSquareL.ttf'
        NanumSquare_Light_id = font_db.addApplicationFont(
            NanumSquare_Light_path)

        if NanumSquare_Light_id != -1:
            NanumSquare_Light_font_family = font_db.applicationFontFamilies(NanumSquare_Light_id)[
                0]

            print(NanumSquare_Light_font_family)

            NanumSquare_Light_font = QFont()
            NanumSquare_Light_font.setFamily(NanumSquare_Light_font_family)

            # 모든 위젯에 해당 폰트 적용
            for widget in self.findChildren(QWidget):
                widget.setFont(NanumSquare_Light_font)

        else:
            logging.warning("Font loading failed")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.add_account()

    def show_alert(self, title, text):
        icon_path = os.path.join(
            current_dir, 'NIX', 'Data', 'Assets', 'alert.png')
        custom_alert = CustomAlert(self, title, text, icon_path)
        custom_alert.exec_()

    def add_account(self):
        try:
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

                    image_url = get_tier_image_url(summoner_name)

                    config = configparser.ConfigParser()
                    config['Account'] = {
                        'NickName': nickname, 'ID': id, 'PW': pw, 'ImageURL': image_url}

                    with open(f'{current_dir}\\NIX\\Data\\Account\\{nickname}.ini', 'w') as configfile:
                        config.write(configfile)

                    self.unsetCursor()
                    self.show_alert('알림', '저장되었습니다.')
                    self.parent.refresh_list_view()
                    self.close()

                except Exception as e:
                    self.unsetCursor()
                    logging.warning(f'add_account error : {e}')
                    self.show_alert(
                        '알림', '닉네임을 불러올 수 없습니다.\n아이디와 패스워드를 확인해주세요.')
                    return

        except Exception as e:
            self.unsetCursor()
            self.show_alert('알림', '저장에 실패했습니다.')
            logging.warning('계정 저장 실패: %s', str(e))

        finally:
            self.unsetCursor()


class EditAccountDialog(QDialog):
    def __init__(self, parent, file_path):
        super().__init__(parent)

        style_path = os.path.join(current_dir, ".\\NIX\\Data\\styles.qss")
        with open(style_path, "r") as style_file:
            self.setStyleSheet(style_file.read())

        self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle("Edit Account")
        self.resize(460, 240)
        self.setFixedSize(self.size())

        config = configparser.ConfigParser()
        config.read(file_path)
        account_data = config['Account']

        self.layout = QVBoxLayout()

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setObjectName('tool-button')
        self.layout.addWidget(self.title_bar)

        self.id_input = QLineEdit(account_data.get('ID', ''), self)
        self.id_input.setPlaceholderText("아이디")
        self.id_input.setFixedWidth(404)
        self.id_input.setFixedHeight(54)
        self.id_input.setObjectName('account-input')

        self.id_input_shadow = QGraphicsDropShadowEffect(self)
        self.id_input_shadow.setBlurRadius(20)
        self.id_input_shadow.setColor(QColor(0, 0, 0, 20))
        self.id_input_shadow.setOffset(5)
        self.id_input.setGraphicsEffect(self.id_input_shadow)

        self.id_input_layout = QVBoxLayout()
        self.id_input_layout.addWidget(self.id_input)
        self.id_input_layout.setAlignment(Qt.AlignCenter)

        self.pw_input = QLineEdit(account_data.get('PW', ''), self)
        self.pw_input.setPlaceholderText("비밀번호")
        self.pw_input.setFixedWidth(404)
        self.pw_input.setFixedHeight(54)
        self.pw_input.setObjectName('account-input')

        self.pw_input_shadow = QGraphicsDropShadowEffect(self)
        self.pw_input_shadow.setBlurRadius(20)
        self.pw_input_shadow.setColor(QColor(0, 0, 0, 20))
        self.pw_input_shadow.setOffset(5)
        self.pw_input.setGraphicsEffect(self.pw_input_shadow)

        self.pw_input_layout = QVBoxLayout()
        self.pw_input_layout.addWidget(self.pw_input)
        self.pw_input_layout.setAlignment(Qt.AlignCenter)

        self.ok_button = QPushButton("수정", self)
        self.ok_button.setFixedWidth(90)
        self.ok_button.setFixedHeight(36)
        self.ok_button.setObjectName('save-button')
        self.ok_button.clicked.connect(self.save)
        self.ok_button_shadow = QGraphicsDropShadowEffect(self)
        self.ok_button_shadow.setBlurRadius(20)
        self.ok_button_shadow.setColor(QColor(0, 0, 0, 20))
        self.ok_button_shadow.setOffset(0)
        self.ok_button.setGraphicsEffect(self.ok_button_shadow)

        self.button_layout = QVBoxLayout()
        self.button_layout.addWidget(self.ok_button)
        self.button_layout.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(self.id_input_layout)
        self.layout.addLayout(self.pw_input_layout)
        self.layout.addLayout(self.button_layout)

        self.setLayout(self.layout)

        self.config = config
        self.file_path = file_path
        self.parent = parent

        font_db = QFontDatabase()

        NanumSquare_Light_path = f'{current_dir}\\NIX\\Data\\Assets\\NanumSquareL.ttf'
        NanumSquare_Light_id = font_db.addApplicationFont(
            NanumSquare_Light_path)

        if NanumSquare_Light_id != -1:
            NanumSquare_Light_font_family = font_db.applicationFontFamilies(NanumSquare_Light_id)[
                0]

            print(NanumSquare_Light_font_family)

            NanumSquare_Light_font = QFont()
            NanumSquare_Light_font.setFamily(NanumSquare_Light_font_family)

            # 모든 위젯에 해당 폰트 적용
            for widget in self.findChildren(QWidget):
                widget.setFont(NanumSquare_Light_font)

        else:
            logging.warning("Font loading failed")

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.save()

    def show_alert(self, title, text):
        icon_path = os.path.join(
            current_dir, 'NIX', 'Data', 'Assets', 'alert.png')
        custom_alert = CustomAlert(self, title, text, icon_path)
        custom_alert.exec_()

    def save(self):
        self.setCursor(QCursor(Qt.WaitCursor))
        id = self.id_input.text()
        pw = self.pw_input.text()

        account_data = self.config['Account']
        account_data_NickName = account_data.get('NickName', '')
        account_data_ID = account_data.get('ID', '')
        account_data_PW = account_data.get('PW', '')
        account_data_ImageURL = account_data.get('ImageURL', '')
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

            image_url = get_tier_image_url(summoner_name)

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

                self.unsetCursor()
                self.parent.refresh_list_view()
                self.show_alert('알림', '변경 사항이 저장되었습니다.')
                self.close()


class CustomTitleBar(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.setFixedHeight(10)

        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.close_button = QPushButton("")
        self.close_button.setFixedWidth(10)
        self.close_button.setObjectName('status-bar-button-close')
        self.close_button.clicked.connect(self.parent.close)

        self.maximized_button = QPushButton("")
        self.maximized_button.setFixedWidth(10)
        self.maximized_button.setObjectName('status-bar-button-maximized')
        self.maximized_button.clicked.connect(self.ismaximized)

        self.minimized_button = QPushButton("")
        self.minimized_button.setFixedWidth(10)
        self.minimized_button.setObjectName('status-bar-button-minimized')
        self.minimized_button.clicked.connect(self.parent.showMinimized)

        self.layout.addStretch()  # 오른쪽 정렬을 위한 스트레치 공간
        self.layout.addWidget(self.minimized_button)
        self.layout.addWidget(self.maximized_button)
        self.layout.addWidget(self.close_button)

        self.setLayout(self.layout)
        self.drag_position = None

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.close()

    def mousePressEvent(self, event):
        self.drag_position = event.globalPos() - self.parent.pos()

    def mouseMoveEvent(self, event):
        if self.drag_position:
            self.parent.move(event.globalPos() - self.drag_position)

    def ismaximized(self):
        if self.parent.isMaximized():
            self.parent.showNormal()
        else:
            self.parent.showMaximized()


class CustomAlert(QDialog):
    def __init__(self, parent, title, text, icon_path):
        super().__init__(parent)
        alert_sound_path = f'{current_dir}\\NIX\\Data\\Sounds\\alert.wav'
        QSound.play(alert_sound_path)

        self.resize(480, 200)
        self.setFixedSize(self.size())

        self.setWindowFlag(Qt.FramelessWindowHint)
        # self.setAttribute(Qt.WA_TranslucentBackground)

        self.setWindowTitle(title)

        self.layout = QVBoxLayout()

        self.title_bar = CustomTitleBar(self)
        self.title_bar.setObjectName('tool-button')
        self.layout.addWidget(self.title_bar)

        self.label_text = QLabel(text)
        self.label_text_layout = QVBoxLayout()
        self.label_text_layout.addWidget(self.label_text)
        self.label_text_layout.setAlignment(Qt.AlignCenter)

        self.icon = QIcon(icon_path)
        self.pixmap = self.icon.pixmap(48, 48)
        self.label_icon = QLabel()
        self.label_icon.setPixmap(self.pixmap)
        self.label_icon_layout = QVBoxLayout()
        self.label_icon_layout.addSpacing(10)
        self.label_icon_layout.addWidget(self.label_icon)
        self.label_icon_layout.setAlignment(Qt.AlignCenter)

        self.layout.addLayout(self.label_icon_layout)
        self.layout.addLayout(self.label_text_layout)

        self.setLayout(self.layout)

        self.title_bar.close_button.setFocus()
        font_db = QFontDatabase()

        NanumSquare_Light_path = f'{current_dir}\\NIX\\Data\\Assets\\NanumSquareL.ttf'
        NanumSquare_Light_id = font_db.addApplicationFont(
            NanumSquare_Light_path)

        if NanumSquare_Light_id != -1:
            NanumSquare_Light_font_family = font_db.applicationFontFamilies(NanumSquare_Light_id)[
                0]

            print(NanumSquare_Light_font_family)

            NanumSquare_Light_font = QFont()
            NanumSquare_Light_font.setFamily(NanumSquare_Light_font_family)

            # 모든 위젯에 해당 폰트 적용
            for widget in self.findChildren(QWidget):
                widget.setFont(NanumSquare_Light_font)

        else:
            logging.warning("Font loading failed")

def get_tier_image_url(summoner_name):
    response = get_summoner_data(summoner_name)
    try:
        rank_data = response['summoner_rank_data_response'][0]
        if rank_data == None:
            tier = '언랭'
        else:
            tier = rank_data.get('tier')
            if rank_data.get('queueType') == 'RANKED_TFT_DOUBLE_UP':
                tier = '언랭'
            elif tier is None:
                tier = '언랭'
        if tier == '언랭':
            image_url = ''
            return image_url
        else:
            image_url = f'https://opgg-static.akamaized.net/images/medals_new/{tier.lower()}.png'
            return image_url
            
    except IndexError as e:
        image_url = ''
        return image_url


def get_summoner_data(summoner_name):
    # 로그인
    try:
        login_url = 'http://jeongyun0302.pythonanywhere.com/login'
        login_data = {'username': 'admin', 'password': 'admin'}
        login_response = requests.post(login_url, json=login_data)
        token = login_response.json().get('token')

        # 보호된 엔드포인트에 접근
        protected_url = 'http://jeongyun0302.pythonanywhere.com/protected'
        headers = {
            'Authorization': f'Bearer {token}',
            'nickname': quote(summoner_name),
        }
        response = requests.get(protected_url, headers=headers)
        logging.info(f'get_summoner_data: {response.json()}\n')
        return response.json()
    except Exception as e:
        return e


def get_nickname(id, pw):
    try:
        # options = webdriver.ChromeOptions()
        # options.add_argument('--headless')  # 브라우저 창을 숨김
        driver = webdriver.Chrome()

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

            return nickname

    except Exception as e:
        logging.info(f'get_nickname error: {e}')
        return None

    finally:
        if driver is not None:
            driver.close()
            logging.info('웹 드라이버 종료')


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


def copy_file(source_path, destination_path):  # 파일을 복사하고, 복사 과정에서 발생하는 예외를 처리
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
    os.makedirs(f'{current_dir}\\NIX\\Data\\Assets', exist_ok=True)
    os.makedirs(f'{current_dir}\\NIX\\Data\\Sounds', exist_ok=True)

    # 파일 복사 작업
    file_list = [
        ('initial_setting\\Initial_Setting.exe', 'Initial_Setting.exe'),
        ('assets\\icons\\NIX.ico', 'ICO\\NIX.ico'),
        ('update\\update.exe', 'update.exe'),
        ('images\\login_page.png', 'Login\\login_page.png'),
        ('images\\login_result_1.png', 'Login\\login_result_1.png'),
        ('images\\login_result_2.png', 'Login\\login_result_2.png'),
        ('images\\LOL_button.png', 'Login\\LOL_button.png'),
        ('images\\play_button.png', 'Login\\play_button.png'),
        ('images\\login_success_form.png', 'Login\\login_success_form.png'),
        ('images\\refresh.png', 'Assets\\refresh.png'),
        ('images\\add.png', 'Assets\\add.png'),
        ('images\\delete.png', 'Assets\\delete.png'),
        ('images\\edit.png', 'Assets\\edit.png'),
        ('images\\alert.png', 'Assets\\alert.png'),
        ('images\\unranked.png', 'Assets\\unranked.png'),
        ('assets\\fonts\\NanumSquareL.ttf', 'Assets\\NanumSquareL.ttf'),
        ('assets\\fonts\\SB 어그로 L.ttf', 'Assets\\SB 어그로 L.ttf'),
        ('assets\\fonts\\SB 어그로 M.ttf', 'Assets\\SB 어그로 M.ttf'),
        ('assets\\fonts\\EF_watermelonSalad.ttf', 'Assets\\EF_watermelonSalad.ttf'),
        ('sounds\\alert.wav', 'Sounds\\alert.wav'),
        ('qss\\styles.qss', 'styles.qss'),
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

            # GUI 애플리케이션 실행 부분
            app = QApplication(sys.argv)
            main_window = MainWindow()
            main_window.show()

            end_time = time.time()  # 파일 복사 종료 시간 기록
            elapsed_time = end_time - start_time  # 파일 복사에 소요된 시간 계산
            logging.info(f'프로그램 로딩시간 : {elapsed_time}')

            sys.exit(app.exec_())
    except Exception as e:
        logging.warning(f'hash response error : {e}')
