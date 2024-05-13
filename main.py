import os
import subprocess
from config import (
    VIDEO_DIR, WHISPER_MODEL, TRANSLATE_CONFIG
)
from utils import extract_audio, install_whisper


def log(*args):
    print(*args)

def error(*args):
    print(*args)

install_whisper()

def process_file(file_path, base_dir):
    file_name = os.path.basename(file_path)
    if file_name.endswith('.mp4') and not file_name.startswith("."):
        log(f'开始处理文件：{file_path}')
        try:
            base_name = os.path.splitext(file_name)[0]
            wav_file = os.path.join(base_dir, f'{base_name}.wav')
            src_lang = TRANSLATE_CONFIG['source_language']
            srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}.srt')

            if not os.path.exists(srt_file):
                srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}')
                if not os.path.exists(wav_file):
                    extract_audio(file_path, wav_file)
                    log('完成音频文件提取，准备生成字幕文件')

                cmd = f'./whisper.cpp/main -m ./whisper.cpp/models/ggml-{WHISPER_MODEL}.bin -f "{wav_file}" -osrt -of "{srt_file}"'
                subprocess.run(cmd, shell=True, check=True)

            if os.path.exists(wav_file):
                os.remove(wav_file)
                log(f'删除wav文件 {wav_file}')

        except Exception as e:
            log(f'执行出错 {e}')

def traverse_dirs(dir_path, level=1):
    if level > 3:
        return

    for entry in os.listdir(dir_path):
        entry_path = os.path.join(dir_path, entry)
        if os.path.isdir(entry_path):
            traverse_dirs(entry_path, level + 1)
        else:
            process_file(entry_path, dir_path)

traverse_dirs(VIDEO_DIR)            