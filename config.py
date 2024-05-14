from dotenv import load_dotenv
import os

load_dotenv()

# 视频文件所在目录,如 /Users/demo/video
# VIDEO_DIR = '/Volumes/2T/makingmoney/创业/The Virtual assistant (VA) Start up Masterclass 2023-6/'

# whisper.cpp 模型,支持以下选项:
# tiny.en, tiny, base.en, base, small.en, small, medium.en, medium
# large-v1, large-v2, large-v3
# WHISPER_MODEL = 'medium.en'

# 翻译配置,视频原语言与翻译后的目标语言
VIDEO_DIR = os.getenv('VIDEO_DIR')
VIDEO_SUFFIX = os.getenv('VIDEO_SUFFIX')
WHISPER_MODEL = os.getenv('WHISPER_MODEL')
TRANSLATE_CONFIG = {
    'source_language': os.getenv('SOURCE_LANGUAGE'),
    'target_language': os.getenv('TARGET_LANGUAGE')
}

class SupportedService:
    BAIDU = 'baidu'
    VOLC = 'volc'
    DEEPLX = 'deeplx'

TRANSLATE_SERVICE_PROVIDER = SupportedService.__dict__.get(os.getenv('TRANSLATE_SERVICE_PROVIDER'))