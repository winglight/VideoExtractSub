# VideoExtractSub

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](https://github.com/winglight/VideoExtractSub/blob/master/LICENSE)

## 项目简介

**VideoExtractSub** 是一个用于从视频文件中提取字幕的开源工具。该项目旨在帮助用户轻松地从各种格式的视频文件中提取出内嵌的字幕，支持字幕格式:SRT。

## 特别说明

本代码有90%来自AI（Claude3.5）的协助生成，另有文档说明整个过程：[AI助我写代码（1）：批量生成视频字幕——宇哥自习室](https://www.broyustudio.com/2024/08/28/AI-Help-Video-Subtract-Srt.html)

## 项目特点

- **多格式支持**：支持多种视频格式，如 MP4、MKV、AVI 等。
- **高效提取**：利用 FFmpeg 提供高效的视频处理和字幕提取。
- **简单易用**：通过GUI即可轻松操作，适合各类用户使用。
- **跨平台**：支持 Windows、macOS 和 Linux 系统。

## 适用场景

- 从电影、电视剧等视频文件中提取字幕用于学习或翻译。
- 提取字幕以便进行字幕校对和编辑。
- 从视频中提取字幕以生成字幕文件，方便播放时加载外部字幕。

## 安装指南

### 前提条件

- **FFmpeg**：需要预先安装 FFmpeg，具体安装方法请参考 [FFmpeg 官方文档](https://ffmpeg.org/download.html)。
- **Python 3.6+**：请确保已安装 Python 3.6 或更高版本。
- **Git** 需要本地有安装git，并且命令行中可以运行git

### 安装步骤

1. 克隆本仓库到本地：
    ```bash
    git clone https://github.com/winglight/VideoExtractSub.git
    ```

2. 进入项目目录：
    ```bash
    cd VideoExtractSub
    ```

3. 安装依赖：
    ```bash
    pip install -r requirements.txt
    ```

4. 设置.env环境变量：
    ```bash
    cp .env.example .env
    ```
    然后修改.env中的设置，也可以在启动GUI后，在界面中修改

## 使用指南

### 基本用法

使用以下命令启动GUI界面：
```bash
python main.py
```

**注意：如果文件夹路径中包括英文逗号，需要删除后再生成字幕，否则解析时会报错**
