import os
import subprocess
from config import (
    VIDEO_DIRS, VIDEO_SUFFIXES, WHISPER_MODEL, TRANSLATE_CONFIG
)
from utils import extract_audio, install_whisper
import time
import threading
import tkinter as tk
from tkinter import filedialog, ttk, messagebox

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
        video_files = get_video_files(video_dirs, video_suffixes)
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
                src_lang = TRANSLATE_CONFIG['source_language']
                srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}.srt')

                if not os.path.exists(srt_file):
                    srt_file = os.path.join(base_dir, f'{base_name}.{src_lang}')
                    if not os.path.exists(wav_file):
                        extract_audio(video_file, wav_file)
                        print('Audio extraction completed, preparing to generate subtitle file.')

                    cmd = f'./whisper.cpp/main -m ./whisper.cpp/models/ggml-{whisper_model}.bin -f "{wav_file}" -osrt -of "{srt_file}"'
                    subprocess.run(cmd, shell=True, check=True)

                    processed_count = processed_count + 1

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

def get_video_files(dirs, suffixes):
    video_files = []
    for directory in dirs:
        for root, _, files in os.walk(directory):
            for file in files:
                if any(file.endswith(suffix) for suffix in suffixes):
                    video_files.append(os.path.join(root, file))
    return video_files

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()