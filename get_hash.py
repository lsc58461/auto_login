#pyinstaller --onefile --icon=.\NIX.ico get_hash.py

import hashlib
import sys
import os

def get_current_directory():
    if getattr(sys, 'frozen', False):  # pyinstaller로 생성된 실행 파일인 경우
        current_dir = os.path.dirname(sys.executable)
    else:  # 스크립트로 실행한 경우
        current_dir = os.path.dirname(os.path.abspath(__file__))
    return current_dir

# Calculate local file hash
def calculate_checksum(file_path):
    sha256_hash = hashlib.sha256()
    try:
        with open(file_path,"rb") as f:
            for byte_block in iter(lambda: f.read(4096),b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    except:
        print('파일을 찾을 수 없습니다.')

current_dir = get_current_directory()
# Local file to be checked
file_path = f'{current_dir}\\Auto_Login.exe'

# Get the local file hash
local_file_hash = calculate_checksum(file_path)

hash_file_path = f'{current_dir}\\hash.txt'

# Save the hash value to hash.txt
with open(hash_file_path, 'w') as hash_file:
    hash_file.write(local_file_hash)

print(f'해쉬 값이 {hash_file_path}에 저장되었습니다.')
os.system("pause")
