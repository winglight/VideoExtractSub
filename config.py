# 视频文件所在目录,如 /Users/demo/video
VIDEO_DIR = '/Volumes/2T/makingmoney/创业/build-micro-saas-makes-money/'

# whisper.cpp 模型,支持以下选项:
# tiny.en, tiny, base.en, base, small.en, small, medium.en, medium
# large-v1, large-v2, large-v3
WHISPER_MODEL = 'medium.en'

# 翻译配置,视频原语言与翻译后的目标语言
TRANSLATE_CONFIG = {
    'source_language': 'en',
    'target_language': 'zh'
}

# 支持的翻译服务商
class SupportedService:
    BAIDU = 'baidu'
    VOLC = 'volc'
    DEEPLX = 'deeplx'

# 当前使用的翻译服务商,如果不配置,则不执行翻译流程
TRANSLATE_SERVICE_PROVIDER = SupportedService.VOLC

# 翻译结果字幕文件内容配置
class ContentTemplateRule:
    ONLY_TRANSLATE = 'only_translate'  # 只输出翻译内容
    SOURCE_AND_TRANSLATE = 'source_and_translate'  # 输出原始字幕和翻译字幕,原始字幕在上面
    TRANSLATE_AND_SOURCE = 'translate_and_source'  # 输出翻译后的字幕和原始字幕,翻译字幕在上面

# 字幕文件内容模板,支持 ${source_content} 和 ${target_content} 变量
CONTENT_TEMPLATE = {
    ContentTemplateRule.ONLY_TRANSLATE: '${target_content}\n\n',
    ContentTemplateRule.SOURCE_AND_TRANSLATE: '${source_content}\n${target_content}\n\n',
    ContentTemplateRule.TRANSLATE_AND_SOURCE: '${target_content}\n${source_content}\n\n'
}

# 翻译内容输出模板规则,默认只输出翻译内容,支持 ContentTemplateRule 内的规则
CONTENT_TEMPLATE_RULE = ContentTemplateRule.ONLY_TRANSLATE

# 原始字幕文件保存命名规则,支持 file_name, source_language, target_language 变量
# 如果为空,将不保存原始字幕文件
# 例如: '${file_name}.${source_language}' -> 对于视频名为 text.mp4 的英文视频原始字幕文件名为 text.en.srt
SOURCE_SRT_SAVE_NAME = '${file_name}.${source_language}'

# 翻译后的字幕文件保存命名规则,支持 file_name, source_language, target_language 变量
TARGET_SRT_SAVE_NAME = '${file_name}.${target_language}'