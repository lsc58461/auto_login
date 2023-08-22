# -*- mode: python ; coding: utf-8 -*-


block_cipher = None


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[('.\\\\qss\\\\styles.qss', '.\\\\qss'), ('.\\\\assets\\\\icons\\\\NIX.ico', '.\\\\assets\\\\icons'), ('.\\\\initial_setting\\\\Initial_Setting.exe', '.\\\\initial_setting'), ('.\\\\update\\\\update.exe', '.\\\\update'), ('.\\\\images\\\\login_success_form.png', '.\\\\images'), ('.\\\\images\\\\login_page.png', '.\\\\images'), ('.\\\\images\\\\login_result_1.png', '.\\\\images'), ('.\\\\images\\\\login_result_2.png', '.\\\\images'), ('.\\\\images\\\\LOL_button.png', '.\\\\images'), ('.\\\\images\\\\play_button.png', '.\\\\images'), ('.\\\\images\\\\refresh.png', '.\\\\images'), ('.\\\\images\\\\add.png', '.\\\\images'), ('.\\\\images\\\\delete.png', '.\\\\images'), ('.\\\\images\\\\edit.png', '.\\\\images'), ('.\\\\images\\\\alert.png', '.\\\\images'), ('.\\\\assets\\\\fonts\\\\NanumSquareL.ttf', '.\\\\assets\\\\fonts'), ('.\\\\assets\\\\fonts\\\\SB 어그로 L.ttf', '.\\\\assets\\\\fonts'), ('.\\\\assets\\\\fonts\\\\SB 어그로 M.ttf', '.\\\\assets\\\\fonts'), ('.\\\\assets\\\\fonts\\\\EF_watermelonSalad.ttf', '.\\\\assets\\\\fonts'), ('.\\\\sounds\\\\alert.wav', '.\\\\sounds')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Auto_Login',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    uac_admin=True,
    icon=['assets\\icons\\NIX.ico'],
)
