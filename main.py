import os
import subprocess
from config import (
    VIDEO_DIRS, VIDEO_SUFFIXES, WHISPER_MODEL, TRANSLATE_CONFIG
)
from utils import extract_audio, install_whisper
import time

install_whisper()

def count_files():
    file_count = 0
    for dir_path in VIDEO_DIRS:
        for root, _, files in os.walk(dir_path):
            for file in files:
                _, file_ext = os.path.splitext(file)
                if file_ext in VIDEO_SUFFIXES and not file.startswith("."):
                    file_count += 1
    return file_count

total_files = count_files()
start_time = time.time()
processed_count = 0

def process_file(file_path, base_dir):
    file_name = os.path.basename(file_path)
    _, file_ext = os.path.splitext(file_name)
    if file_ext in VIDEO_SUFFIXES and not file_name.startswith("."):
        print(f'开始处理文件：{file_path}')
        try:
            base_name = os.path.splitext(file_name)[0]
            wav_file = os.path.join(base_dir, f'{base_name}.wav')
            src_lang = TRANSLATE_CONFIG['source_language']
            srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}.srt')

            if not os.path.exists(srt_file):
                srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}')
                if not os.path.exists(wav_file):
                    extract_audio(file_path, wav_file)
                    print('完成音频文件提取，准备生成字幕文件')

                cmd = f'./whisper.cpp/main -m ./whisper.cpp/models/ggml-{WHISPER_MODEL}.bin -f "{wav_file}" -osrt -of "{srt_file}"'
                subprocess.run(cmd, shell=True, check=True)

                global processed_count
                processed_count = processed_count + 1

            if os.path.exists(wav_file):
                os.remove(wav_file)
                print(f'删除wav文件 {wav_file}')

        except Exception as e:
            print(f'执行出错 {e}')

def traverse_dirs(dir_paths, level=1):
    if level > 4:
        return

    for dir_path in dir_paths:
        for entry in os.listdir(dir_path):
            entry_path = os.path.join(dir_path, entry)
            if os.path.isdir(entry_path):
                traverse_dirs([entry_path], level + 1)
            else:
                process_file(entry_path, dir_path)
                # 记时、刷新进度\
                if processed_count > 0:
                    elapsed_time = time.time() - start_time
                    remaining_time = (elapsed_time / processed_count) * (total_files - processed_count)
                    progress = processed_count / total_files * 100
                    print(f"\r进度: {progress:.2f}% 剩余时间: {time.strftime('%H:%M:%S', time.gmtime(remaining_time))}", end="")

traverse_dirs(VIDEO_DIRS)            