import os
import subprocess
from dotenv import load_dotenv
from config import (
    VIDEO_DIR, WHISPER_MODEL, SOURCE_SRT_SAVE_NAME, TRANSLATE_SERVICE_PROVIDER
)
from utils import extract_audio, render_file_path, install_whisper

load_dotenv()

def log(*args):
    print(*args)

def error(*args):
    print(*args)

install_whisper()

for file_name in os.listdir(VIDEO_DIR):
    if file_name.endswith('.mp4'):
        log(f'开始处理文件：{file_name}')
        try:
            base_name = os.path.splitext(file_name)[0]
            wav_file = os.path.join(VIDEO_DIR, f'{base_name}.wav')
            srt_file = render_file_path(SOURCE_SRT_SAVE_NAME, base_name)

            extract_audio(os.path.join(VIDEO_DIR, file_name), wav_file)
            log('完成音频文件提取，准备生成字幕文件')

            subprocess.run([
                './whisper.cpp/main',
                '-m', f'./whisper.cpp/models/ggml-{WHISPER_MODEL}.bin',
                '-f', wav_file,
                '-osrt', '-of', f'{srt_file}.srt'
            ], check=True)

            log('完成字幕文件生成，准备开始翻译')
            if TRANSLATE_SERVICE_PROVIDER:
                translate.app(VIDEO_DIR, base_name, f'{srt_file}.srt')

            log('翻译完成')
            os.remove(wav_file)
            log(f'删除wav文件 {wav_file}')

            if not SOURCE_SRT_SAVE_NAME:
                os.remove(f'{srt_file}.srt')

        except Exception as e:
            log(f'执行出错 {e}')