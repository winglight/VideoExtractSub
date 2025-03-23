import os
import subprocess
from config import (
    VIDEO_DIRS, VIDEO_SUFFIXES, WHISPER_MODEL, TRANSLATE_CONFIG, SOURCE_LANGUAGE
)
from utils import extract_audio, install_whisper
import time
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import multiprocessing
from translator import translate_srt_file_process

install_whisper()

# def count_files():
#     file_count = 0
#     for dir_path in VIDEO_DIRS:
#         for root, _, files in os.walk(dir_path):
#             for file in files:
#                 _, file_ext = os.path.splitext(file)
#                 if file_ext in VIDEO_SUFFIXES and not file.startswith("."):
#                     file_count += 1
#     return file_count

# total_files = count_files()
# start_time = time.time()
# processed_count = 0

# def process_file(file_path, base_dir):
#     file_name = os.path.basename(file_path)
#     _, file_ext = os.path.splitext(file_name)
#     if file_ext in VIDEO_SUFFIXES and not file_name.startswith("."):
#         print(f'Start processing file: {file_path}')
#         try:
#             base_name = os.path.splitext(file_name)[0]
#             wav_file = os.path.join(base_dir, f'{base_name}.wav')
#             src_lang = TRANSLATE_CONFIG['source_language']
#             srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}.srt')

#             if not os.path.exists(srt_file):
#                 srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}')
#                 if not os.path.exists(wav_file):
#                     extract_audio(file_path, wav_file)
#                     print('Audio file extraction complete. Preparing to generate subtitle file.')

#                 cmd = f'./whisper.cpp/main -m ./whisper.cpp/models/ggml-{WHISPER_MODEL}.bin -f "{wav_file}" -osrt -of "{srt_file}"'
#                 subprocess.run(cmd, shell=True, check=True)

#                 global processed_count
#                 processed_count = processed_count + 1

#             if os.path.exists(wav_file):
#                 os.remove(wav_file)
#                 print(f'Removed wav file {wav_file}')

#         except Exception as e:
#             print(f'An error occurred: {e}')

# def traverse_dirs(dir_paths, level=1):
#     if level > 4:
#         return

#     for dir_path in dir_paths:
#         for entry in os.listdir(dir_path):
#             entry_path = os.path.join(dir_path, entry)
#             if os.path.isdir(entry_path):
#                 traverse_dirs([entry_path], level + 1)
#             else:
#                 process_file(entry_path, dir_path)
#                 # Timer and progress refresh
#                 if processed_count > 0:
#                     elapsed_time = time.time() - start_time
#                     remaining_time = (elapsed_time / processed_count) * (total_files - processed_count)
#                     progress = processed_count / total_files * 100
#                     print(f"\rProgress: {progress:.2f}% Estimated remaining time: {time.strftime('%H:%M:%S', time.gmtime(remaining_time))}", end="")

# traverse_dirs(VIDEO_DIRS)         

class App:
    def __init__(self, root):
        self.root = root
        self.root.title('Batch Video Subtitle Export Tool')
        self.create_widgets()
        self.translation_processes = []  # 添加翻译进程列表

    def create_widgets(self):
        # Configuration section
        self.config_frame = tk.LabelFrame(self.root, text='Configuration')
        self.config_frame.pack(fill='x', padx=10, pady=10)

        tk.Label(self.config_frame, text='Video Directories:').grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.video_dirs_var = tk.StringVar(value=','.join(VIDEO_DIRS))
        self.video_dirs_entry = tk.Entry(self.config_frame, textvariable=self.video_dirs_var, width=50)
        self.video_dirs_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.config_frame, text='Video Suffixes:').grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.video_suffixes_var = tk.StringVar(value=','.join(VIDEO_SUFFIXES))
        self.video_suffixes_entry = tk.Entry(self.config_frame, textvariable=self.video_suffixes_var, width=50)
        self.video_suffixes_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(self.config_frame, text='Whisper Model:').grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.whisper_model_var = tk.StringVar(value=WHISPER_MODEL)
        self.whisper_model_entry = tk.Entry(self.config_frame, textvariable=self.whisper_model_var, width=50)
        self.whisper_model_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Label(self.config_frame, text='Source Language:').grid(row=3, column=0, padx=5, pady=5, sticky='e')
        self.source_language_var = tk.StringVar(value=TRANSLATE_CONFIG['source_language'])
        self.source_language_entry = tk.Entry(self.config_frame, textvariable=self.source_language_var, width=50)
        self.source_language_entry.grid(row=3, column=1, padx=5, pady=5)

        tk.Label(self.config_frame, text='Target Language:').grid(row=4, column=0, padx=5, pady=5, sticky='e')
        self.target_language_var = tk.StringVar(value=TRANSLATE_CONFIG['target_language'])
        self.target_language_entry = tk.Entry(self.config_frame, textvariable=self.target_language_var, width=50)
        self.target_language_entry.grid(row=4, column=1, padx=5, pady=5)

        # Progress section
        self.progress_frame = tk.LabelFrame(self.root, text='Progress')
        self.progress_frame.pack(fill='x', padx=10, pady=10)

        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(self.progress_frame, variable=self.progress_var, maximum=100)
        self.progress_bar.pack(fill='x', padx=5, pady=5)

        self.progress_label = tk.Label(self.progress_frame, text='Progress: 0.00% Remaining Time: 00:00:00')
        self.progress_label.pack(padx=5, pady=5)

        # Buttons section
        self.button_frame = tk.Frame(self.root)
        self.button_frame.pack(fill='x', padx=10, pady=10)

        self.start_button = tk.Button(self.button_frame, text='Start Export', command=self.start_processing)
        self.start_button.pack(side='left', padx=5, pady=5)

        self.stop_button = tk.Button(self.button_frame, text='Stop', command=self.stop_processing)
        self.stop_button.pack(side='left', padx=5, pady=5)
        
        # 添加翻译按钮
        self.translate_button = tk.Button(self.button_frame, text='Translate SRT Files', command=self.start_translation)
        self.translate_button.pack(side='left', padx=5, pady=5)

        self.check_button = tk.Button(self.button_frame, text='Check Dependencies', command=self.check_dependencies)
        self.check_button.pack(side='left', padx=5, pady=5)

        self.install_git_button = tk.Button(self.button_frame, text='Install Git', command=self.install_git)
        self.install_git_button.pack(side='left', padx=5, pady=5)

        self.install_ffmpeg_button = tk.Button(self.button_frame, text='Install FFmpeg', command=self.install_ffmpeg)
        self.install_ffmpeg_button.pack(side='left', padx=5, pady=5)

        self.stop_flag = False

    def start_processing(self):
        self.stop_flag = False
        self.start_button.config(state='disabled')
        self.processing_thread = threading.Thread(target=self.process_files)
        self.processing_thread.start()

    def stop_processing(self):
        self.stop_flag = True
        self.start_button.config(state='normal')

    def process_files(self):
        video_dirs = self.video_dirs_var.get().split(',')
        video_suffixes = self.video_suffixes_var.get().split(',')
        whisper_model = self.whisper_model_var.get()
        source_language = self.source_language_var.get()
        target_language = self.target_language_var.get()

        # Assuming we have a function `get_video_files` to fetch all video files
        video_files = self.get_video_files(video_dirs, video_suffixes)
        total_files = len(video_files)
        
        if total_files == 0:
            messagebox.showwarning("Warning", "No video files found.")
            self.start_button.config(state='normal')
            return

        start_time = time.time()
        processed_count = 0
        for index, video_file in enumerate(video_files):
            if self.stop_flag:
                break
            try:
                base_dir, file_name = os.path.split(video_file)
                base_name = os.path.splitext(file_name)[0]
                wav_file = os.path.join(base_dir, f'{base_name}.wav')
                
                # 修改判断字幕文件是否存在的逻辑
                # 检查是否存在以视频文件名为前缀的任意字幕文件
                subtitle_exists = False
                from config import SUBTITLE_FORMATS
                
                for root, _, files in os.walk(base_dir):
                    for file in files:
                        # 检查文件是否以视频文件名为前缀
                        if file.startswith(base_name):
                            # 检查文件扩展名是否在配置的字幕格式中
                            file_ext = os.path.splitext(file)[1].lower()
                            if file_ext in SUBTITLE_FORMATS:
                                subtitle_exists = True
                                print(f"找到匹配的字幕文件: {os.path.join(root, file)}")
                                break
                    if subtitle_exists:
                        break
                
                if not subtitle_exists:
                    srt_file = os.path.join(base_dir, f'{base_name}.{SOURCE_LANGUAGE}.srt')
                    if not os.path.exists(wav_file):
                        extract_audio(video_file, wav_file)
                        print('Audio extraction completed, preparing to generate subtitle file.')
                
                    cmd = f'./whisper.cpp/main -m ./whisper.cpp/models/ggml-{whisper_model}.bin -f "{wav_file}" -osrt -of "{srt_file}"'
                    subprocess.run(cmd, shell=True, check=True)
                
                    processed_count = processed_count + 1
                else:
                    print(f"跳过处理视频 {video_file}，已存在匹配的字幕文件")
                
                if os.path.exists(wav_file):
                    os.remove(wav_file)
                    print(f'Removed wav file {wav_file}')

            except Exception as e:
                print(f'Error occurred: {e}')

            progress = (index + 1) / total_files * 100
            elapsed_time = time.time() - start_time
            estimated_total_time = elapsed_time / (index + 1) * total_files
            remaining_time = estimated_total_time - elapsed_time

            self.progress_var.set(progress)
            self.progress_label.config(text=f'{index}/{total_files} Progress: {progress:.2f}% Remaining Time: {time.strftime("%H:%M:%S", time.gmtime(remaining_time))} \n{video_file}')
            self.root.update_idletasks()

        self.start_button.config(state='normal')
        messagebox.showinfo("Completed", "All video files have been processed.")

    def check_dependencies(self):
        git_installed = self.check_git_installed()
        ffmpeg_installed = self.check_ffmpeg_installed()

        message = "Dependency Check Results:\n"
        message += f"git: {'Installed' if git_installed else 'Not Installed'}\n"
        message += f"ffmpeg: {'Installed' if ffmpeg_installed else 'Not Installed'}"
        messagebox.showinfo("Check Dependencies", message)

    def check_git_installed(self):
        try:
            subprocess.check_call(['git', '--version'])
            return True
        except subprocess.CalledProcessError:
            return False

    def check_ffmpeg_installed(self):
        try:
            subprocess.check_call(['ffmpeg', '-version'])
            return True
        except subprocess.CalledProcessError:
            return False

    def install_git(self):
        if self.check_git_installed():
            messagebox.showinfo("Install Git", "Git is already installed.")
            return

        if os.name == 'nt':  # Windows
            subprocess.run(['powershell', 'Start-Process', 'powershell', '-ArgumentList', '"winget install --id Git.Git -e --source winget"', '-Verb', 'RunAs'])
        else:
            subprocess.run(['sudo', 'apt-get', 'install', 'git'])

    def install_ffmpeg(self):
        if self.check_ffmpeg_installed():
            messagebox.showinfo("Install FFmpeg", "FFmpeg is already installed.")
            return

        if os.name == 'nt':  # Windows
            subprocess.run(['powershell', 'Start-Process', 'powershell', '-ArgumentList', '"winget install --id Gyan.FFmpeg -e --source winget"', '-Verb', 'RunAs'])
        else:
            subprocess.run(['sudo', 'apt-get', 'install', 'ffmpeg'])

    def get_video_files(self, dirs, suffixes):
        video_files = []
        for directory in dirs:
            for root, _, files in os.walk(directory):
                for file in files:
                    if any(file.endswith(suffix) for suffix in suffixes):
                        video_files.append(os.path.join(root, file))
        return video_files


    def start_translation(self):
        """开始翻译SRT文件的处理"""
        self.translate_button.config(state='disabled')
        self.translation_thread = threading.Thread(target=self.translate_files)
        self.translation_thread.start()

    def translate_files(self):
        """翻译所有SRT文件的处理函数"""
        video_dirs = self.video_dirs_var.get().split(',')
        source_language = self.source_language_var.get()
        target_language = self.target_language_var.get()
        
        # 获取所有SRT文件
        srt_files = get_srt_files(video_dirs, source_language)
        total_files = len(srt_files)
        
        if total_files == 0:
            # 使用after方法确保在主线程中显示消息框
            self.root.after(0, lambda: messagebox.showwarning("警告", f"未找到{', '.join(SUBTITLE_FORMATS)}格式的字幕文件。"))
            self.root.after(0, lambda: self.translate_button.config(state='normal'))
            return
        
        # 清理之前的翻译进程
        for p in self.translation_processes:
            if p.is_alive():
                p.terminate()
        self.translation_processes = []
        
        # 创建进程池
        pool = multiprocessing.Pool(processes=min(multiprocessing.cpu_count(), 4))
        results = []
        
        # 提交翻译任务
        for srt_file in srt_files:
            result = pool.apply_async(
                translate_srt_file_process, 
                (srt_file, source_language, target_language),
                callback=self.update_translation_progress
            )
            results.append(result)
        
        # 关闭进程池
        pool.close()
        
        # 更新进度条
        start_time = time.time()
        completed = 0
        self.progress_var.set(0)
        
        while completed < total_files:
            completed = sum(1 for r in results if r.ready())
            progress = completed / total_files * 100
            
            elapsed_time = time.time() - start_time
            if completed > 0:
                estimated_total_time = elapsed_time / completed * total_files
                remaining_time = estimated_total_time - elapsed_time
            else:
                remaining_time = 0
            
            self.progress_var.set(progress)
            self.progress_label.config(
                text=f'翻译进度: {completed}/{total_files} ({progress:.2f}%) 剩余时间: {time.strftime("%H:%M:%S", time.gmtime(remaining_time))}'
            )
            self.root.update_idletasks()
            time.sleep(0.5)
            
            # 检查是否所有任务都已完成
            if all(r.ready() for r in results):
                break
        
        # 等待所有进程完成
        pool.join()
        
        # 使用after方法确保在主线程中更新UI
        self.root.after(0, lambda: self.translate_button.config(state='normal'))
        self.root.after(0, lambda: messagebox.showinfo("完成", f"所有字幕文件翻译完成，共处理 {completed} 个文件。"))

    def update_translation_progress(self, result):
        """翻译进程回调函数"""
        if result:
            print(f"翻译完成: {result}")

def get_srt_files(dirs, source_language):
    """获取所有字幕文件"""
    from config import SUBTITLE_FORMATS
    
    subtitle_files = []
    for directory in dirs:
        if not directory.strip():  # 跳过空目录
            continue
            
        for root, _, files in os.walk(directory):
            for file in files:
                # 检查文件是否是支持的字幕格式
                file_ext = os.path.splitext(file)[1].lower()
                if file_ext in SUBTITLE_FORMATS:
                    # 检查是否包含源语言标记
                    # if f'.{source_language}{file_ext}' in file or f'.{source_language}.' in file:
                    subtitle_files.append(os.path.join(root, file))
    
    print(f"找到 {len(subtitle_files)} 个字幕文件")
    return subtitle_files

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()