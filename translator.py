import os
import re
from transformers import MarianMTModel, MarianTokenizer
from config import TRANSLATE_CONFIG

def get_translation_model_name(source_lang, target_lang):
    """根据源语言和目标语言获取MarianMT模型名称"""
    # 语言代码映射（ISO代码到MarianMT使用的代码）
    lang_map = {
        'en': 'en',
        'zh': 'zh',
        'fr': 'fr',
        'de': 'de',
        'es': 'es',
        'it': 'it',
        'ja': 'jap',
        'ko': 'kor',
        'pt': 'pt',
        'ru': 'ru',
        # 可根据需要添加更多语言
    }
    
    src = lang_map.get(source_lang.lower(), source_lang.lower())
    tgt = lang_map.get(target_lang.lower(), target_lang.lower())
    
    return f"Helsinki-NLP/opus-mt-{src}-{tgt}"

class SRTTranslator:
    # 添加类变量用于缓存模型
    _model_cache = {}
    _tokenizer_cache = {}
    
    def __init__(self, source_lang=None, target_lang=None):
        """初始化翻译器"""
        self.source_lang = source_lang or TRANSLATE_CONFIG['source_language']
        self.target_lang = target_lang or TRANSLATE_CONFIG['target_language']
        self.model_name = get_translation_model_name(self.source_lang, self.target_lang)
        self.tokenizer = None
        self.model = None
        
    def load_model(self):
        """加载MarianMT模型和分词器，使用缓存避免重复加载"""
        if self.model_name in SRTTranslator._model_cache and self.model_name in SRTTranslator._tokenizer_cache:
            print(f"使用缓存的翻译模型: {self.model_name}")
            self.model = SRTTranslator._model_cache[self.model_name]
            self.tokenizer = SRTTranslator._tokenizer_cache[self.model_name]
            return True
            
        print(f"正在加载翻译模型: {self.model_name}")
        try:
            self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
            self.model = MarianMTModel.from_pretrained(self.model_name)
            
            # 缓存模型和分词器
            SRTTranslator._model_cache[self.model_name] = self.model
            SRTTranslator._tokenizer_cache[self.model_name] = self.tokenizer
            
            print("翻译模型加载成功")
            return True
        except Exception as e:
            print(f"加载翻译模型失败: {e}")
            return False
    
    def translate_text(self, text):
        """翻译单个文本"""
        if not self.model or not self.tokenizer:
            if not self.load_model():
                return text
        
        try:
            # 对于过长的文本，分段翻译
            if len(text) > 500:
                parts = [text[i:i+500] for i in range(0, len(text), 500)]
                translated_parts = []
                for part in parts:
                    inputs = self.tokenizer(part, return_tensors="pt", padding=True)
                    translated_ids = self.model.generate(**inputs)
                    translated_part = self.tokenizer.batch_decode(translated_ids, skip_special_tokens=True)[0]
                    translated_parts.append(translated_part)
                return " ".join(translated_parts)
            else:
                inputs = self.tokenizer(text, return_tensors="pt", padding=True)
                translated_ids = self.model.generate(**inputs)
                return self.tokenizer.batch_decode(translated_ids, skip_special_tokens=True)[0]
        except Exception as e:
            print(f"翻译文本时出错: {e}")
            return text
    
    def translate_srt_file(self, srt_file_path):
        """翻译字幕文件内容并保存到新文件"""
        if not os.path.exists(srt_file_path):
            print(f"字幕文件不存在: {srt_file_path}")
            return None
        
        # 确定输出文件路径
        base_dir = os.path.dirname(srt_file_path)
        base_name = os.path.basename(srt_file_path)
        file_ext = os.path.splitext(base_name)[1]  # 获取文件扩展名
        
        # 移除可能的语言后缀
        if file_ext.lower() == '.srt':
            base_name = re.sub(r'\.[a-z]{2,3}\.srt$', '.srt', base_name)
            output_file = os.path.join(base_dir, base_name.replace('.srt', f'.{self.target_lang}.srt'))
        elif file_ext.lower() == '.vtt':
            base_name = re.sub(r'\.[a-z]{2,3}\.vtt$', '.vtt', base_name)
            output_file = os.path.join(base_dir, base_name.replace('.vtt', f'.{self.target_lang}.vtt'))
        else:
            # 默认使用srt格式
            output_file = os.path.join(base_dir, f"{os.path.splitext(base_name)[0]}.{self.target_lang}.srt")
        
        # 检查目标文件是否已存在，如果存在则跳过翻译
        if os.path.exists(output_file):
            print(f"目标文件已存在，跳过翻译: {output_file}")
            return output_file
            
        try:
            # 读取字幕文件
            with open(srt_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 根据文件类型选择不同的解析方式
            if file_ext.lower() == '.srt':
                # 解析SRT文件
                pattern = r'(\d+)\n(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})\n((?:.+\n)+?)(?:\n|$)'
                matches = re.findall(pattern, content)
                
                translated_content = ""
                for index, timestamp, text in matches:
                    # 翻译字幕文本
                    translated_text = self.translate_text(text.strip())
                    # 重新组装SRT格式
                    translated_content += f"{index}\n{timestamp}\n{translated_text}\n\n"
            
            elif file_ext.lower() == '.vtt':
                # 解析VTT文件
                # 跳过WEBVTT头部
                if content.startswith('WEBVTT'):
                    header_end = content.find('\n\n')
                    header = content[:header_end+2]
                    content = content[header_end+2:]
                else:
                    header = 'WEBVTT\n\n'
                
                # VTT格式解析
                pattern = r'((?:\d{2}:)?\d{2}:\d{2}\.\d{3} --> (?:\d{2}:)?\d{2}:\d{2}\.\d{3}[^\n]*)\n((?:.+\n)+?)(?:\n|$)'
                matches = re.findall(pattern, content)
                
                translated_content = header
                for timestamp, text in matches:
                    # 翻译字幕文本
                    translated_text = self.translate_text(text.strip())
                    # 重新组装VTT格式
                    translated_content += f"{timestamp}\n{translated_text}\n\n"
            
            else:
                print(f"不支持的字幕格式: {file_ext}")
                return None
            
            # 保存翻译后的内容
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(translated_content)
            
            print(f"翻译完成，已保存到: {output_file}")
            return output_file
        except Exception as e:
            print(f"翻译字幕文件时出错: {e}")
            return None

def translate_srt_file_process(srt_file_path, source_lang=None, target_lang=None):
    """用于多进程调用的翻译函数"""
    translator = SRTTranslator(source_lang, target_lang)
    return translator.translate_srt_file(srt_file_path)