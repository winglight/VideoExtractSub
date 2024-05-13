import os
import subprocess
import shutil
from string import Template

# 配置
VIDEO_DIR = './videos'
TRANSLATE_CONFIG = {
    'source_language': 'en',
    'target_language': 'zh'
}
WHISPER_MODEL = 'base'

# 渲染模板字符串
def render_template(template, data):
    return Template(template).substitute(data)

# 渲染文件路径
def render_file_path(template, file_name):
    data = {
        'fileName': file_name,
        'sourceLanguage': TRANSLATE_CONFIG['source_language'],
        'targetLanguage': TRANSLATE_CONFIG['target_language']
    }
    final_path = template or f'temp-{file_name}'
    file_path = render_template(final_path, data)
    return os.path.join(VIDEO_DIR, file_path)

# 提取音频
def extract_audio(video_path, audio_path):
    cmd = f'ffmpeg -i {video_path} -ar 16000 -ac 1 -c:a pcm_s16le -y {audio_path}'
    subprocess.run(cmd, shell=True, check=True)

# 运行命令
def run_command(cmd, args):
    process = subprocess.Popen([cmd, *args], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        print(f'Error: {stderr.decode()}')
    else:
        print(stdout.decode())

# 安装 whisper.cpp 及模型
def install_whisper():
    repo_url = 'https://github.com/ggerganov/whisper.cpp'
    local_path = './whisper.cpp'
    model_path = f'./whisper.cpp/models/ggml-{WHISPER_MODEL}.bin'
    main_path = './whisper.cpp/main'

    if not os.path.exists(local_path):
        print('Cloning whisper.cpp repository')
        run_command('git', ['clone', repo_url])

    if not os.path.exists(model_path):
        print('Installing whisper.cpp model')
        run_command('bash', ['./whisper.cpp/models/download-ggml-model.sh', WHISPER_MODEL])

    if not os.path.exists(main_path):
        print('Compiling whisper.cpp')
        run_command('make', ['-C', './whisper.cpp'])